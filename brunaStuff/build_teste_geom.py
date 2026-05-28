#!/usr/bin/env python3
"""build_teste_geom.py

Gera uma versao alternativa da polyMesh tubular extrudada da OA usando UMA das
3 estrategias de extracao de centerline, em um caso OpenFOAM standalone
(cases/teste-geom-N) pronto para inspecao visual no ParaView.

NAO roda nenhuma simulacao -- so escreve geometria.

Uso:
  python3 brunaStuff/build_teste_geom.py --strategy voxel_skeleton  --out cases/teste-geom-1
  python3 brunaStuff/build_teste_geom.py --strategy z_slicing       --out cases/teste-geom-2
  python3 brunaStuff/build_teste_geom.py --strategy tangent_marching --out cases/teste-geom-3

Estrategias:
  voxel_skeleton    -- voxeliza o STL, preenche, aplica skimage.morphology.skeletonize
                       3D e ordena por nearest-neighbour (medial axis verdadeiro).
                       Requer: scikit-image, scipy.
  z_slicing         -- slicing por planos z constantes, centroide ponderado por
                       area de cada secao (mesma logica de scale_artery_centerline.py).
                       Requer: trimesh.
  tangent_marching  -- marching iterativo: comeca num extremo do PCA, avanca por
                       passo fixo na direcao tangente local, em cada passo
                       computa o centroide dos pontos do STL numa janela esferica.
                       Sem dependencias extras.

O caso gerado contem:
  cases/teste-geom-N/fluid/constant/polyMesh/   -- lumen O-grid hex puro
  cases/teste-geom-N/solid/constant/polyMesh/   -- annulus hex puro (R_in=0.55, R_out=0.75)
  cases/teste-geom-N/constant/triSurface/       -- copia de artery.stl, artery_unscaled.stl, nerve.stl
  cases/teste-geom-N/{fluid,solid}/{system,0}/  -- stubs minimos para o ParaView abrir
  cases/teste-geom-N/teste-geom-N.foam          -- atalho para abrir no ParaView
  cases/teste-geom-N/_centerline_summary.json   -- estatisticas (estrategia, comprimento, bounds, ...)
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

# Reuso de primitivas testadas do builder original
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_artoph_tubular_meshes import (  # noqa: E402
    H_WALL_M,
    NCIRC,
    NRAD_LUMEN,
    NRAD_WALL,
    NZ,
    R_LUMEN_M,
    build_annulus_foam_mesh,
    build_lumen_foam_mesh,
    parallel_transport_frames,
    read_ascii_stl_vertices,
    smooth_centerline,
    write_polymesh,
)


REPO = Path(__file__).resolve().parents[1]
# Procura os STLs em multiplos lugares (ordem de prioridade):
#   1) cases/ao-mestrado/constant/triSurface  (caso FSI atual, autossuficiente)
#   2) cases/artoph-curva-mestrado/solid/constant/triSurface  (legado)
_TRI_CANDIDATES = [
    REPO / "cases" / "ao-mestrado" / "constant" / "triSurface",
    REPO / "cases" / "artoph-curva-mestrado" / "solid" / "constant" / "triSurface",
]
TRI_DIR_SRC = next((p for p in _TRI_CANDIDATES if (p / "artery.stl").exists()),
                   _TRI_CANDIDATES[0])
DEFAULT_SRC_STL = TRI_DIR_SRC / "artery.stl"  # a geometria atual (ja escalada)
ARTERY_UNSCALED_STL = TRI_DIR_SRC / "artery_unscaled.stl"
NERVE_STL = TRI_DIR_SRC / "nerve.stl"


# =============================================================================
# Estrategia 1: voxel skeleton 3D (skimage)
# =============================================================================
def _extend_skeleton_tip(
    skel_ordered: NDArray[np.float64],
    stl_pts: NDArray[np.float64],
    end: str,
    search_sphere_mm: float = 3.0,
    step_mm: float = 0.18,
    force_direction: NDArray[np.float64] | None = None,
    zero_axes: tuple[int, ...] = (),
) -> NDArray[np.float64]:
    """skimage.morphology.skeletonize "retrai" a centerline ~1 voxel dos topos
    rounded de tubos fechados -- a centerline termina antes do tip real do STL.

    Esta funcao estende a ponta da skeleton (end='start' ou end='end') ate o
    apex do cap real, adicionando pontos intermediarios a cada step_mm.

    Heuristica de busca do tip (mais robusta que tangente local, que pode
    apontar a direcao errada perto do cap):
      1. Considera os vertices do STL dentro de uma esfera de raio
         search_sphere_mm centrada no skel_end (= regiao do cap + parede
         proxima).
      2. Para cada candidato, calcula a distancia minima ao SKELETON INTEIRO
         (nao apenas ao endpoint).
      3. O apex do cap eh o candidato com MAIOR distancia minima ao skeleton
         (a parede lateral fica a ~R_tubo do skeleton, mas o cap apex fica
         a R_tubo + retraction_voxel).

    Se force_direction (vetor unitario) for passado, a extensao vai em LINHA
    RETA nessa direcao a partir de tip_seed, com comprimento = projecao de
    (apex - tip_seed) em force_direction. Util para forcar o "stub" final a
    ser perpendicular a um eixo de referencia (ex: [0,0,1] -> cap horizontal,
    extensao puramente vertical em +z).

    Se zero_axes for passado (e force_direction NAO for), a extensao vai na
    direcao natural (apex - tip_seed) mas com os componentes especificados
    zerados antes da normalizacao. Ex: zero_axes=(1,) zera y -> direcao fica
    "no plano xz", capturando a direcao do tubo apenas no plano vertical xz.
    """
    if end == "start":
        tip_seed = skel_ordered[0]
    elif end == "end":
        tip_seed = skel_ordered[-1]
    else:
        raise ValueError("end deve ser 'start' ou 'end'")

    try:
        from scipy.spatial import cKDTree
    except ImportError:
        return np.empty((0, 3))

    # 1) Candidatos = vertices do STL dentro da esfera
    d_end = np.linalg.norm(stl_pts - tip_seed, axis=1)
    sphere = d_end < search_sphere_mm * 1e-3
    if sphere.sum() < 6:
        return np.empty((0, 3))
    cand = stl_pts[sphere]

    # 2) Para cada candidato, distancia minima ao skeleton inteiro
    tree_skel = cKDTree(skel_ordered)
    dist_to_skel, _ = tree_skel.query(cand, k=1)

    # 3) Apex = candidato com maior dist_to_skel
    i_apex = int(np.argmax(dist_to_skel))
    real_tip = cand[i_apex]
    apex_dist_to_skel = float(dist_to_skel[i_apex])

    # 4) Define a direcao e o ponto final da extensao
    if force_direction is not None:
        d = np.asarray(force_direction, dtype=float)
        d /= np.linalg.norm(d)
        proj = float(np.dot(real_tip - tip_seed, d))
        if proj < 0.2e-3:
            return np.empty((0, 3))
        end_pt = tip_seed + proj * d
        gap = proj
        print(f"    [tip extend {end}] FORCE dir={d}  length={gap*1e3:.3f} mm "
              f"(tip_seed={tip_seed*1e3} -> straight_end={end_pt*1e3})  "
              f"[apex no STL = {real_tip*1e3}, d_apex_to_skel={apex_dist_to_skel*1e3:.3f}]")
    elif zero_axes:
        raw_dir = real_tip - tip_seed
        d = raw_dir.copy()
        for ax in zero_axes:
            d[ax] = 0.0
        norm_d = float(np.linalg.norm(d))
        if norm_d < 1e-9:
            return np.empty((0, 3))
        d /= norm_d
        proj = float(np.dot(raw_dir, d))  # = norm_d depois de zerar axes
        if proj < 0.2e-3:
            return np.empty((0, 3))
        end_pt = tip_seed + proj * d
        gap = proj
        print(f"    [tip extend {end}] AUTO dir(zero_axes={zero_axes})={d}  "
              f"length={gap*1e3:.3f} mm "
              f"(tip_seed={tip_seed*1e3} -> {end_pt*1e3})  "
              f"[apex no STL = {real_tip*1e3}]")
    else:
        gap = float(np.linalg.norm(real_tip - tip_seed))
        if gap < 0.2e-3:
            return np.empty((0, 3))
        end_pt = real_tip
        print(f"    [tip extend {end}] gap = {gap*1e3:.3f} mm "
              f"(tip_seed={tip_seed*1e3} -> apex={real_tip*1e3}, "
              f"d_apex_to_skel={apex_dist_to_skel*1e3:.3f} mm)")

    # Adiciona pontos uniformes entre tip_seed e end_pt
    n_steps = max(1, int(np.ceil(gap / (step_mm * 1e-3))))
    ts = np.linspace(0, 1, n_steps + 1)[1:]  # exclui o 0 (= tip_seed, ja existe)
    extension = tip_seed[None, :] + ts[:, None] * (end_pt - tip_seed)[None, :]
    return extension


def extract_voxel_skeleton(
    stl_path: Path, pitch_mm: float = 0.15
) -> NDArray[np.float64]:
    """Voxeliza o STL, preenche, aplica skeletonize 3D, ordena por NN greedy
    e ESTENDE ambas as pontas ate os tips reais do STL (skimage.skeletonize
    retrai a centerline ~1 voxel das calotas; sem extensao, ha um gap de
    ~1 mm em cada ponta).

    Robusto a curvaturas arbitrarias (extrai o medial axis verdadeiro). Usa
    pitch menor (0.15 mm) que o scale_artery_centerline_v2.py (0.20 mm) para
    capturar a curva em C com mais fidelidade.
    """
    try:
        import trimesh
        from scipy.spatial import cKDTree
        from skimage.morphology import skeletonize
    except ImportError as e:
        raise RuntimeError(
            "Estrategia voxel_skeleton requer scikit-image, scipy e trimesh. "
            "Instale com: python3 -m pip install scikit-image scipy trimesh"
        ) from e

    mesh = trimesh.load_mesh(str(stl_path))
    stl_pts = np.array(mesh.vertices)
    pitch_m = pitch_mm * 1e-3
    vox = mesh.voxelized(pitch=pitch_m).fill()
    skel = skeletonize(vox.matrix.astype(bool))
    ijk = np.argwhere(skel)
    pts = vox.indices_to_points(ijk)
    print(f"  [skeletonize] {len(pts)} voxels no medial axis")

    # Greedy NN ordering desde o endpoint (vertice com menos vizinhos)
    tree = cKDTree(pts)
    counts = tree.query_ball_point(pts, r=1.8 * pitch_m, return_length=True)
    start = int(np.argmin(counts))
    n = len(pts)
    visited = np.zeros(n, dtype=bool)
    order = [start]
    visited[start] = True
    cur = start
    while len(order) < n:
        _, idxs = tree.query(pts[cur], k=min(20, n))
        nxt = None
        for i in idxs:
            if not visited[i]:
                nxt = int(i)
                break
        if nxt is None:
            break
        order.append(nxt)
        visited[nxt] = True
        cur = nxt
    cl = pts[order]
    print(f"  [NN-order]    {len(cl)} pontos ordenados")

    # Estender ambas as pontas ate os tips reais do STL.
    # tip z- (end='start'): extensao reta em -z (cap horizontal apontando -z)
    # tip z+ (end='end'):   extensao na direcao do tubo PROJETADA no plano xz
    #                       (zera y), capturando a direcao natural do tubo
    #                       no plano vertical (entre -x e +z)
    ext_start = _extend_skeleton_tip(
        cl, stl_pts, end="start",
        force_direction=np.array([0.0, 0.0, -1.0]),
    )
    ext_end = _extend_skeleton_tip(
        cl, stl_pts, end="end",
        zero_axes=(1,),
    )
    if len(ext_start) > 0:
        # ext_start vai de cl[0] na direcao FORA (do skel) -> inverter ordem
        # para que a sequencia continue prepended-first-far -> ... -> cl[0]
        cl = np.vstack([ext_start[::-1], cl])
    if len(ext_end) > 0:
        cl = np.vstack([cl, ext_end])
    print(f"  [tip-extend]  total = {len(cl)} pontos "
          f"(prepended={len(ext_start)}, appended={len(ext_end)})")
    return cl


# =============================================================================
# Estrategia 2: slicing por planos z constantes (centroide ponderado por area)
# =============================================================================
def extract_z_slicing(
    stl_path: Path, n_slices: int = 250
) -> NDArray[np.float64]:
    """Slicing por planos z constantes, centroide ponderado por area por secao.

    Logica identica a brunaStuff/scale_artery_centerline.py. Boa qualidade se a
    arteria nao dobra em z (i.e., e monotonicamente crescente em z); se houver
    duplas voltas em z, as secoes com multiplos poligonos sao agregadas via
    centroide ponderado por area, o que pode achatar bifurcacoes.
    """
    try:
        import trimesh
    except ImportError as e:
        raise RuntimeError(
            "Estrategia z_slicing requer trimesh. Instale com: "
            "python3 -m pip install trimesh"
        ) from e

    mesh = trimesh.load_mesh(str(stl_path))
    z_min, z_max = mesh.bounds[:, 2]
    zs = np.linspace(z_min + 1e-5, z_max - 1e-5, n_slices)
    cl_pts: list[list[float]] = []
    n_valid = 0
    for z in zs:
        section = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        if section is None:
            continue
        try:
            planar, _ = section.to_planar()
        except Exception:
            continue
        polys = list(planar.polygons_full)
        if not polys:
            continue
        areas = np.array([p.area for p in polys])
        if areas.sum() <= 0:
            continue
        cx = sum(p.centroid.x * p.area for p in polys) / areas.sum()
        cy = sum(p.centroid.y * p.area for p in polys) / areas.sum()
        cl_pts.append([cx, cy, z])
        n_valid += 1
    print(f"  [z-slicing]   {n_valid} secoes validas (de {n_slices} tentativas)")
    return np.array(cl_pts)


# =============================================================================
# Estrategia 3: tangent marching (numpy puro)
# =============================================================================
def extract_tangent_marching(
    stl_path: Path,
    step_mm: float = 0.3,
    radial_window_mm: float = 1.5,
    slab_thickness_mm: float = 0.4,
    max_steps: int = 500,
) -> NDArray[np.float64]:
    """Marching: comeca num extremo do PCA, avanca por passo fixo na direcao
    tangente local. Em cada passo, computa o centroide dos pontos do STL que
    caem numa FATIA PERPENDICULAR (slab fino na tangente) na posicao proposta,
    e move 'new_pt' para o centro perpendicular dessa secao -- mas mantem o
    deslocamento ao longo da tangente fixo em step_mm.

    Por que slab e nao esfera: uma esfera centrada em proposed captura pontos
    'a frente' e 'atras' simetricamente, fazendo o centroide cair no proprio
    'current' (ponto fixo) -- marching trava. A slab fina captura apenas a
    cross-section local, dando o centro verdadeiro daquela secao.

    A tangente e atualizada por smoothing 60/40 entre a tangente anterior e a
    direcao do passo efetivo, permitindo capturar curvas pronunciadas sem
    achatar para o eixo principal global.

    Sem dependencias extras (so NumPy).
    """
    pts = read_ascii_stl_vertices(stl_path)
    print(f"  [STL load]    {len(pts)} vertices")

    # PCA para encontrar eixo principal e extremos
    p_mean = pts.mean(axis=0)
    C = np.cov((pts - p_mean).T)
    _, eigvecs = np.linalg.eigh(C)
    axis = eigvecs[:, -1]
    proj_all = (pts - p_mean) @ axis

    # Pontos extremos: media dos vertices dentro de 0.5 mm dos extremos do PCA
    proj_min, proj_max = proj_all.min(), proj_all.max()
    near_start = proj_all < proj_min + 0.5e-3
    near_end = proj_all > proj_max - 0.5e-3
    start_pt = pts[near_start].mean(axis=0)
    end_pt = pts[near_end].mean(axis=0)
    print(f"  [endpoints]   start={start_pt*1e3} mm")
    print(f"                end  ={end_pt*1e3} mm")
    print(f"                |end-start| = {np.linalg.norm(end_pt-start_pt)*1e3:.2f} mm")

    # Tangente inicial: na direcao do PCA, mas apontando de start para end
    tangent = end_pt - start_pt
    tangent /= np.linalg.norm(tangent)

    step_m = step_mm * 1e-3
    win_m = radial_window_mm * 1e-3
    slab_m = slab_thickness_mm * 1e-3
    cl: list[NDArray[np.float64]] = [start_pt]
    current = start_pt.copy()

    n_empty_consec = 0
    last_dist_to_end = np.linalg.norm(start_pt - end_pt)
    n_no_progress_to_end = 0
    stopped_reason = "max_steps"
    for k in range(max_steps):
        proposed = current + step_m * tangent
        # Slab perpendicular a tangent em torno de proposed
        proj_along = (pts - proposed) @ tangent
        in_slab = np.abs(proj_along) < slab_m
        # Filtra ainda por raio radial (descarta pontos longe lateralmente)
        perp = (pts - proposed) - proj_along[:, None] * tangent
        dist_perp = np.linalg.norm(perp, axis=1)
        in_window = dist_perp < win_m
        near = in_slab & in_window
        n_near = int(near.sum())

        if n_near >= 6:
            section_pts = pts[near]
            centroid = section_pts.mean(axis=0)
            # Tangente LOCAL via PCA da secao: a secao e um anel ~plano (ring),
            # entao as 2 direcoes de maior variancia estao no plano do ring, e
            # a de MENOR variancia eh a normal do ring = eixo do tubo local.
            # Bem mais estavel que estimar tangente via (new_pt - current).
            sec_centered = section_pts - centroid
            _, eigvecs_sec = np.linalg.eigh(np.cov(sec_centered.T))
            local_tan = eigvecs_sec[:, 0]  # menor eigenvalue = eixo do tubo
            # Garantir orientacao "para frente" (dot positivo com tangent atual)
            if np.dot(local_tan, tangent) < 0:
                local_tan = -local_tan
            # Smoothing 40/60 a favor do local_tan (mais responsivo a curvas)
            tangent = 0.4 * tangent + 0.6 * local_tan
            tangent /= np.linalg.norm(tangent)
            # new_pt = projecao do centroide no plano perpendicular passando por
            # proposed (garante avanco fixo de step_m na direcao da tangente)
            delta = centroid - proposed
            delta_perp = delta - np.dot(delta, tangent) * tangent
            new_pt = proposed + delta_perp
            n_empty_consec = 0
        else:
            # Slab vazio: provavelmente saimos da arteria. Marca, mas continua
            # 1-2 iteracoes pra dar chance de re-entrar (artérias com curva forte).
            new_pt = proposed
            n_empty_consec += 1
            if n_empty_consec >= 3:
                stopped_reason = f"saiu da arteria (3 slabs vazios consecutivos) em step {k}"
                break

        cl.append(new_pt)
        current = new_pt

        # Para quando chegamos perto do extremo final
        dist_to_end = np.linalg.norm(current - end_pt)
        if dist_to_end < step_m * 1.5:
            cl.append(end_pt)
            stopped_reason = f"chegou ao endpoint em {k+1} passos"
            break

        # Verifica se estamos nos AFASTANDO do end_pt (algoritmo perdeu o rumo)
        if dist_to_end > last_dist_to_end + 1e-9:
            n_no_progress_to_end += 1
            if n_no_progress_to_end >= 30:
                stopped_reason = (
                    f"se afastando do end_pt por 30 iteracoes consecutivas em step {k} "
                    f"(dist_to_end={dist_to_end*1e3:.2f}mm)"
                )
                break
        else:
            n_no_progress_to_end = 0
        last_dist_to_end = dist_to_end

    print(f"  [march]       {stopped_reason}")
    return np.array(cl)


# =============================================================================
# Estrategias registradas
# =============================================================================
STRATEGIES = {
    "voxel_skeleton": extract_voxel_skeleton,
    "z_slicing": extract_z_slicing,
    "tangent_marching": extract_tangent_marching,
}


# =============================================================================
# Stubs OpenFOAM minimos (so para o ParaView abrir o polyMesh)
# =============================================================================
def _foam_header_dict(obj_name: str) -> str:
    return (
        "FoamFile\n{\n"
        "    version     2.0;\n"
        "    format      ascii;\n"
        "    class       dictionary;\n"
        f"    object      {obj_name};\n"
        "}\n\n"
    )


_CTRLDICT = (
    _foam_header_dict("controlDict")
    + "application      pimpleFoam;\n"
    + "startFrom        startTime;\n"
    + "startTime        0;\n"
    + "stopAt           endTime;\n"
    + "endTime          0;\n"
    + "deltaT           1e-3;\n"
    + "writeControl     timeStep;\n"
    + "writeInterval    1;\n"
    + "purgeWrite       0;\n"
    + "writeFormat      ascii;\n"
    + "writePrecision   6;\n"
    + "writeCompression off;\n"
    + "runTimeModifiable yes;\n"
)

_FVSCHEMES = (
    _foam_header_dict("fvSchemes")
    + "ddtSchemes       { default steadyState; }\n"
    + "gradSchemes      { default Gauss linear; }\n"
    + "divSchemes       { default none; }\n"
    + "laplacianSchemes { default none; }\n"
    + "interpolationSchemes { default linear; }\n"
    + "snGradSchemes    { default uncorrected; }\n"
)

_FVSOLUTION = _foam_header_dict("fvSolution") + "solvers {}\n"


def write_openfoam_stubs(case_dir: Path, name: str) -> None:
    """Escreve stubs minimos de OpenFOAM (controlDict, fvSchemes, fvSolution,
    0/) para cada sub-regiao (fluid, solid), permitindo abrir no ParaView via
    case.foam ou paraFoam."""
    for sub in ("fluid", "solid"):
        sysdir = case_dir / sub / "system"
        sysdir.mkdir(parents=True, exist_ok=True)
        (case_dir / sub / "0").mkdir(parents=True, exist_ok=True)
        (sysdir / "controlDict").write_text(_CTRLDICT)
        (sysdir / "fvSchemes").write_text(_FVSCHEMES)
        (sysdir / "fvSolution").write_text(_FVSOLUTION)
        # case.foam por regiao
        (case_dir / sub / f"{sub}.foam").write_text("")
    # case.foam raiz (atalho multi-regiao)
    (case_dir / f"{name}.foam").write_text("")


def copy_reference_surfaces(case_dir: Path) -> None:
    """Copia artery.stl, artery_unscaled.stl, nerve.stl para
    constant/triSurface/ para o usuario sobrepor no ParaView."""
    dest = case_dir / "constant" / "triSurface"
    dest.mkdir(parents=True, exist_ok=True)
    for src in (DEFAULT_SRC_STL, ARTERY_UNSCALED_STL, NERVE_STL):
        if src.exists():
            shutil.copy2(src, dest / src.name)


# =============================================================================
# Main
# =============================================================================
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument(
        "--strategy",
        required=True,
        choices=list(STRATEGIES.keys()),
        help="qual estrategia de extracao de centerline",
    )
    ap.add_argument(
        "--out",
        required=True,
        type=Path,
        help="diretorio do caso de saida (ex: cases/teste-geom-1)",
    )
    ap.add_argument(
        "--src-stl",
        type=Path,
        default=DEFAULT_SRC_STL,
        help=f"STL fonte (default: {DEFAULT_SRC_STL.relative_to(REPO)})",
    )
    ap.add_argument("--nz", type=int, default=NZ, help="num. secoes ao longo da centerline")
    ap.add_argument("--ncirc", type=int, default=NCIRC, help="setores circunferenciais")
    ap.add_argument("--nrad-lumen", type=int, default=NRAD_LUMEN)
    ap.add_argument("--nrad-wall", type=int, default=NRAD_WALL)
    ap.add_argument(
        "--mesh-only",
        action="store_true",
        help="So gera fluid/constant/polyMesh e solid/constant/polyMesh. "
             "Nao sobrescreve controlDict/fvSchemes/fvSolution nem copia STLs. "
             "Usar quando ao caso de destino ja eh um caso FSI completo.",
    )
    args = ap.parse_args()

    # Resolve --out relativo ao repo
    out_case = args.out
    if not out_case.is_absolute():
        out_case = REPO / out_case
    out_case = out_case.resolve()

    src_stl = args.src_stl
    if not src_stl.is_absolute():
        src_stl = REPO / src_stl
    if not src_stl.exists():
        raise FileNotFoundError(f"STL fonte nao encontrado: {src_stl}")

    name = out_case.name  # 'teste-geom-1' etc

    print(f"=== build_teste_geom.py ===")
    print(f"  strategy: {args.strategy}")
    print(f"  src STL : {src_stl.relative_to(REPO)}")
    print(f"  out case: {out_case.relative_to(REPO)}")
    print(f"  name    : {name}")
    print()

    # 1) Extracao
    print(f"[1] Extraindo centerline via '{args.strategy}'...")
    extractor = STRATEGIES[args.strategy]
    cl_raw = extractor(src_stl)
    print(f"  centerline raw: {len(cl_raw)} pts")
    print(f"  bounds (mm): {cl_raw.min(axis=0)*1e3} .. {cl_raw.max(axis=0)*1e3}")
    arc_raw = float(np.sum(np.linalg.norm(np.diff(cl_raw, axis=0), axis=1)))
    print(f"  arc length (mm): {arc_raw*1e3:.2f}")

    # 2) Smoothing + reamostragem uniforme em arc length
    print(f"\n[2] Suavizando + reamostrando para {args.nz} secoes...")
    cl = smooth_centerline(cl_raw, nz_out=args.nz)
    arc = float(np.sum(np.linalg.norm(np.diff(cl, axis=0), axis=1)))
    print(f"  arc length apos smooth (mm): {arc*1e3:.2f}")

    # 3) Frames ortonormais (parallel transport)
    print(f"\n[3] Calculando frames (T, N, B) por parallel transport...")
    T_frames, N_frames, B_frames = parallel_transport_frames(cl)
    _ = T_frames

    # 4) Construir polyMesh do LUMEN (fluido)
    print(f"\n[4] Construindo polyMesh LUMEN "
          f"(R={R_LUMEN_M*1e3:.2f} mm, ncirc={args.ncirc}, nrad={args.nrad_lumen})...")
    mesh_fluid = build_lumen_foam_mesh(
        cl, N_frames, B_frames, R_LUMEN_M, args.ncirc, args.nrad_lumen,
        patch_names={
            "cap_back": "inlet",
            "cap_front": "outlet",
            "r_inner": "axis",
            "r_outer": "wall",
        },
    )
    pm_dir_f = out_case / "fluid" / "constant" / "polyMesh"
    if pm_dir_f.exists():
        shutil.rmtree(pm_dir_f)
    stats_f = write_polymesh(
        mesh_fluid, pm_dir_f,
        patch_types={"inlet": "patch", "outlet": "patch", "wall": "wall", "axis": "wall"},
    )
    print(f"  FLUID: {stats_f['nPoints']} pts, {stats_f['nCells']} cells, "
          f"{stats_f['nFaces']} faces ({stats_f['nInternalFaces']} internal)")

    # 5) Construir polyMesh do ANNULUS (solido)
    print(f"\n[5] Construindo polyMesh ANNULUS "
          f"(R_in={R_LUMEN_M*1e3:.2f}, R_out={(R_LUMEN_M+H_WALL_M)*1e3:.2f} mm, "
          f"ncirc={args.ncirc}, nrad={args.nrad_wall})...")
    mesh_solid = build_annulus_foam_mesh(
        cl, N_frames, B_frames, R_LUMEN_M, R_LUMEN_M + H_WALL_M,
        args.ncirc, args.nrad_wall,
        patch_names={
            "cap_back": "inner_cap_back",
            "cap_front": "inner_cap_front",
            "r_inner": "lumen",
            "r_outer": "arteria_externa",
        },
    )
    pm_dir_s = out_case / "solid" / "constant" / "polyMesh"
    if pm_dir_s.exists():
        shutil.rmtree(pm_dir_s)
    stats_s = write_polymesh(
        mesh_solid, pm_dir_s,
        patch_types={
            "inner_cap_back": "wall", "inner_cap_front": "wall",
            "lumen": "wall", "arteria_externa": "wall",
        },
    )
    print(f"  SOLID: {stats_s['nPoints']} pts, {stats_s['nCells']} cells, "
          f"{stats_s['nFaces']} faces ({stats_s['nInternalFaces']} internal)")

    if args.mesh_only:
        print(f"\n[6] --mesh-only: pulando stubs (mantendo controlDict/fvSchemes/fvSolution existentes).")
        print(f"[7] --mesh-only: pulando copia das STLs (mantendo constant/triSurface existente).")
    else:
        # 6) Stubs OpenFOAM minimos
        print(f"\n[6] Escrevendo stubs minimos (controlDict, fvSchemes, fvSolution, *.foam)...")
        write_openfoam_stubs(out_case, name)

        # 7) Copia das STLs de referencia
        print(f"\n[7] Copiando artery.stl, artery_unscaled.stl, nerve.stl para constant/triSurface/...")
        copy_reference_surfaces(out_case)

    # 8) Escreve sumario JSON
    summary = {
        "strategy": args.strategy,
        "src_stl": str(src_stl.relative_to(REPO)),
        "nz": args.nz,
        "ncirc": args.ncirc,
        "nrad_lumen": args.nrad_lumen,
        "nrad_wall": args.nrad_wall,
        "R_lumen_mm": R_LUMEN_M * 1e3,
        "R_outer_mm": (R_LUMEN_M + H_WALL_M) * 1e3,
        "wall_thickness_mm": H_WALL_M * 1e3,
        "centerline_n_raw": int(len(cl_raw)),
        "centerline_n_resampled": int(len(cl)),
        "arc_length_raw_mm": arc_raw * 1e3,
        "arc_length_resampled_mm": arc * 1e3,
        "centerline_bounds_mm": [
            (cl.min(axis=0) * 1e3).tolist(),
            (cl.max(axis=0) * 1e3).tolist(),
        ],
        "stats_fluid": {k: v for k, v in stats_f.items() if k != "patches"},
        "stats_solid": {k: v for k, v in stats_s.items() if k != "patches"},
    }
    (out_case / "_centerline_summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\n[OK] caso pronto em {out_case.relative_to(REPO)}/")
    print(f"     Abra no ParaView: {out_case.relative_to(REPO)}/{name}.foam "
          f"(ou solid/solid.foam / fluid/fluid.foam por regiao)")


if __name__ == "__main__":
    main()
