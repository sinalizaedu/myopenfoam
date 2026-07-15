#!/usr/bin/env python3
"""translate_artery_to_p_contact.py

Posiciona a arteria oftalmica de cases/ao-mestrado de modo que a parede da
malha FSI da arteria (extruidada em torno da centerline com R_outer =
R_LUMEN + H_WALL = 0.55 + 0.20 = 0.75 mm) seja TANGENTE ao cilindro externo
do ONS (R_ONS = 2.5 mm, z em [0, 30] mm) APENAS no ponto:

    P_contact = (0.0, 2.5, 18.5) mm

que e o mesmo ponto onde cases/on-mestrado aplica a pressao pulsatil de
contato (definido em system/topoSetDict_contact).

Logica:
  Para a parede da malha FSI (tubo de raio R_OUTER em torno da centerline)
  tocar o cilindro ONS no ponto P_contact, a centerline deve passar por:
    P_cl_target = P_contact + (P_contact / |P_contact_xy|) * R_OUTER
                = (0, 2.5, 18.5) + (0, 1, 0) * 0.75
                = (0, 3.25, 18.5) mm
  E este precisa ser o ponto de MENOR r_xy de toda a centerline em
  z em [0, 30] mm (caso contrario, outro segmento da arteria invadiria
  o ONS).

  Translacao rigida:
    delta = P_cl_target - P_centerline_closest_to_z_axis

Procedimento:
  1) Restaura artery.stl a partir de artery.stl.pre_p_contact.stl (se existir,
     senao usa artery.stl como esta).
  2) Voxeliza + skeletoniza para extrair a centerline (mesmo metodo do
     build_teste_geom --strategy voxel_skeleton).
  3) Encontra o ponto da centerline mais proximo do eixo z em z[0,30].
  4) Calcula delta e aplica a TODOS os vertices de artery.stl.
  5) Verifica: extrai a centerline novamente, confirma min_r_xy ~ 3.25 mm
     em (0, 3.25, 18.5).
  6) Reescreve artery_outer.stl como copia EXATA de artery.stl.
  7) Reescreve artery_inner.stl como artery.stl deslocado para dentro
     ao longo das normais de vertice por h = 0.2 mm.
  8) Atualiza _artery_translated_summary.json, meshHints.json e
     closest_to_ON_ref.json.

Uso:
    brunaStuff/.venv/bin/python brunaStuff/translate_artery_to_p_contact.py
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import cKDTree
from skimage.morphology import skeletonize

REPO = Path(__file__).resolve().parents[1]
TRI = REPO / "cases" / "ao-mestrado" / "constant" / "triSurface"
HINTS_JSON = REPO / "cases" / "ao-mestrado" / "constant" / "meshHints.json"
CLOSEST_JSON = REPO / "cases" / "ao-mestrado" / "constant" / "closest_to_ON_ref.json"

# Constantes geometricas
R_ONS_M = 2.5e-3            # raio externo do ONS
R_OUTER_TUBE_M = 0.75e-3    # R_LUMEN + H_WALL = 0.55e-3 + 0.20e-3
H_WALL_M = 0.20e-3

# Alvo de contato: setor angular e z. A anatomia ORIGINAL tem o ponto natural
# de contato em theta=-20 deg, z~22.8 mm (quadrante +X-Y). A escala 1.3x along
# centerline distorceu o angulo natural; entre os candidatos da centerline
# escalada, o de menor |delta| que cai em +X-Y e theta=-30 deg, z=25 mm
# (k=242 da skeleton). Confirmado por debug_artery_contact_angle.py.
P_CONTACT_THETA_DEG = -30.0
P_CONTACT_Z_MM = 25.0

# Clearance radial entre a parede externa da arteria e o cilindro ONS.
# > 0: arteria NAO toca o ONS em lugar nenhum, garantindo folga visual e
#      numerica robusta (mesh discretizada por voxel pitch ~0.15 mm).
# A pressao de contato pulsatil e aplicada ANALITICAMENTE em on-mestrado
# via system/topoSetDict_contact (caixa pequena ao redor de P_contact),
# entao nao precisamos de contato fisico real entre as malhas.
CLEARANCE_MM = 0.30

# Shift rigido adicional aplicado a TUDO (artery, outer, inner) apos a
# busca do delta. Util para microajustes finais sem mexer na logica da
# busca (ex.: encostar mais na ONS no quadrante +X-Y -> usar X< 0).
# Ordem: rigid_search_delta + EXTRA_TRANSLATION_M.
EXTRA_TRANSLATION_MM = np.array([-0.37, 0.0, 0.0])  # ~2% da extensao X da arteria

R_TARGET_CL_M = R_ONS_M + R_OUTER_TUBE_M + CLEARANCE_MM * 1e-3  # 3.55 mm

_theta_rad = np.radians(P_CONTACT_THETA_DEG)
# P_contact = ponto teorico (analitico) de aplicacao de pressao na parede
# do ONS (r=2.5mm). NAO e um ponto da malha — usado apenas como referencia
# para definir o box do topoSetDict_contact em on-mestrado.
P_CONTACT_M = np.array([
    R_ONS_M * np.cos(_theta_rad),
    R_ONS_M * np.sin(_theta_rad),
    P_CONTACT_Z_MM * 1e-3,
])
# P_centerline_target = onde colocamos o ponto da centerline mais proximo
# do eixo z. Inclui clearance, garantindo gap entre a arteria FSI e o ONS.
P_CL_TARGET_M = np.array([
    R_TARGET_CL_M * np.cos(_theta_rad),
    R_TARGET_CL_M * np.sin(_theta_rad),
    P_CONTACT_Z_MM * 1e-3,
])

Z0_M, Z1_M = 0.0, 30.0e-3
VOX_PITCH_M = 0.15e-3       # mesmo do build_teste_geom voxel_skeleton

# #region agent log
import json as _json
import time as _time
_DEBUG_LOG_PATH = Path(
    "/Users/brunaenne/Documents/repos/myopenfoam/.cursor/debug-0586c6.log"
)
_SESSION_ID = "0586c6"
_RUN_ID = f"run_{int(_time.time())}_post_fix"


def _debug_log(hypothesisId: str, location: str, message: str, data: dict) -> None:
    _DEBUG_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "sessionId": _SESSION_ID,
        "id": f"log_{int(_time.time()*1000)}_{location.replace(':', '_').replace('.', '_')}",
        "timestamp": int(_time.time() * 1000),
        "location": location,
        "message": message,
        "data": data,
        "runId": _RUN_ID,
        "hypothesisId": hypothesisId,
    }
    with _DEBUG_LOG_PATH.open("a") as f:
        f.write(_json.dumps(entry, default=float) + "\n")
# #endregion


def read_ascii_stl_facets(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Le STL ASCII preservando indices de vertices unicos e a topologia das faces."""
    verts: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int]] = []
    key_to_idx: dict[tuple[float, float, float], int] = {}
    buf: list[tuple[float, float, float]] = []

    def add_v(x: float, y: float, z: float) -> int:
        k = (round(x, 9), round(y, 9), round(z, 9))
        i = key_to_idx.get(k)
        if i is not None:
            return i
        i = len(verts)
        verts.append((x, y, z))
        key_to_idx[k] = i
        return i

    with path.open() as f:
        for line in f:
            ls = line.strip()
            if ls.startswith("vertex"):
                p = ls.split()
                buf.append((float(p[1]), float(p[2]), float(p[3])))
                if len(buf) == 3:
                    i0 = add_v(*buf[0])
                    i1 = add_v(*buf[1])
                    i2 = add_v(*buf[2])
                    faces.append((i0, i1, i2))
                    buf.clear()
    return np.array(verts, dtype=np.float64), np.array(faces, dtype=np.int64)


def write_ascii_stl(path: Path, V: np.ndarray, F: np.ndarray, name: str) -> None:
    with path.open("w") as fp:
        fp.write(f"solid {name}\n")
        for i0, i1, i2 in F:
            p0, p1, p2 = V[i0], V[i1], V[i2]
            n = np.cross(p1 - p0, p2 - p0)
            ln = np.linalg.norm(n)
            n = n / ln if ln > 1e-30 else np.array([0.0, 0.0, 1.0])
            fp.write(
                f"  facet normal {n[0]:.6e} {n[1]:.6e} {n[2]:.6e}\n"
                "    outer loop\n"
            )
            for p in (p0, p1, p2):
                fp.write(f"      vertex {p[0]:.6e} {p[1]:.6e} {p[2]:.6e}\n")
            fp.write("    endloop\n  endfacet\n")
        fp.write(f"endsolid {name}\n")


def fix_winding(V: np.ndarray, F: np.ndarray) -> tuple[np.ndarray, float]:
    vol = 0.0
    for i0, i1, i2 in F:
        vol += np.dot(V[i0], np.cross(V[i1], V[i2])) / 6.0
    if vol < 0:
        F = F.copy()
        F[:, [1, 2]] = F[:, [2, 1]]
        vol = -vol
    return F, float(vol)


def vertex_normals_outward(V: np.ndarray, F: np.ndarray) -> np.ndarray:
    fn = np.zeros((len(F), 3))
    for fi, (i0, i1, i2) in enumerate(F):
        c = np.cross(V[i1] - V[i0], V[i2] - V[i0])
        ln = np.linalg.norm(c)
        fn[fi] = c / ln if ln > 1e-30 else np.array([0.0, 0.0, 1.0])
    vn = np.zeros_like(V)
    cnt = np.zeros(len(V))
    for fi, (i0, i1, i2) in enumerate(F):
        for j in (i0, i1, i2):
            vn[j] += fn[fi]
            cnt[j] += 1.0
    nz = cnt > 0
    vn[nz] /= cnt[nz, None]
    ln = np.linalg.norm(vn, axis=1, keepdims=True)
    ln[ln < 1e-30] = 1.0
    return vn / ln


def extract_centerline(V_m: np.ndarray, F: np.ndarray) -> np.ndarray:
    """Voxeliza + skeletoniza + ordena por NN. Sem extensao das pontas
    (basta para localizar o ponto de menor r_xy)."""
    mesh = trimesh.Trimesh(vertices=V_m, faces=F, process=False)
    vox = mesh.voxelized(pitch=VOX_PITCH_M).fill()
    skel = skeletonize(vox.matrix.astype(bool))
    ijk = np.argwhere(skel)
    pts = vox.indices_to_points(ijk)
    print(f"  [skel] {len(pts)} voxels da medial axis")
    tree = cKDTree(pts)
    counts = tree.query_ball_point(pts, r=1.8 * VOX_PITCH_M, return_length=True)
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
    return pts[order]


def closest_centerline_point_to_z_axis(
    cl: np.ndarray, z_lo: float, z_hi: float
) -> tuple[np.ndarray, float, int]:
    mask = (cl[:, 2] >= z_lo) & (cl[:, 2] <= z_hi)
    if not mask.any():
        raise SystemExit(
            f"Nenhum ponto da centerline em z em [{z_lo*1e3:.2f}, {z_hi*1e3:.2f}] mm"
        )
    band = cl[mask]
    r = np.hypot(band[:, 0], band[:, 1])
    i = int(np.argmin(r))
    return band[i], float(r[i]), i


def find_best_translation(
    cl: np.ndarray, target_cl: np.ndarray, R_target: float,
    z_lo: float, z_hi: float,
) -> tuple[np.ndarray, int, float]:
    """Itera sobre todos os pontos da centerline P_k, testa delta_k =
    target_cl - P_k. Para cada delta_k, calcula min r_xy(P_j + delta_k)
    para j com (P_j + delta_k).z em [z_lo, z_hi].

    Aceita delta_k se min r_xy >= R_target - tol. Entre os aceitos,
    escolhe o que tem |delta_k| minimo (translacao mais "natural").

    Se NENHUM delta_k passa, escolhe o que maximiza min r_xy (a melhor
    aproximacao possivel) e retorna ele com flag valido=False.
    """
    n = len(cl)
    best_idx = -1
    best_delta = None
    best_norm = np.inf
    best_min_r = -np.inf
    fallback_idx = -1
    fallback_delta = None
    fallback_min_r = -np.inf
    R_target_safe = R_target - 1e-9

    for k in range(n):
        delta_k = target_cl - cl[k]
        cl_t = cl + delta_k
        mask = (cl_t[:, 2] >= z_lo) & (cl_t[:, 2] <= z_hi)
        if not mask.any():
            continue
        rxy = np.hypot(cl_t[mask, 0], cl_t[mask, 1])
        min_r = float(rxy.min())

        if min_r >= R_target_safe:
            d = float(np.linalg.norm(delta_k))
            if d < best_norm:
                best_norm = d
                best_idx = k
                best_delta = delta_k.copy()
                best_min_r = min_r
        else:
            if min_r > fallback_min_r:
                fallback_min_r = min_r
                fallback_idx = k
                fallback_delta = delta_k.copy()

    if best_delta is not None:
        return best_delta, best_idx, best_min_r
    print(f"  [warn] nenhum delta resulta em min_r >= {R_target*1e3:.3f} mm. "
          f"Usando o melhor possivel: min_r = {fallback_min_r*1e3:.4f} mm.")
    return fallback_delta, fallback_idx, fallback_min_r


def report_state(label: str, V_m: np.ndarray) -> None:
    V_mm = V_m * 1e3
    bx, by, bz = V_mm[:, 0], V_mm[:, 1], V_mm[:, 2]
    mask = (V_m[:, 2] >= Z0_M) & (V_m[:, 2] <= Z1_M)
    Vb = V_mm[mask]
    rxy = np.hypot(Vb[:, 0], Vb[:, 1]) if len(Vb) else np.array([np.nan])
    print(
        f"[{label:30s}]  bounds(mm) "
        f"x[{bx.min():+.2f},{bx.max():+.2f}] "
        f"y[{by.min():+.2f},{by.max():+.2f}] "
        f"z[{bz.min():+.2f},{bz.max():+.2f}]   "
        f"min r_xy(z[0,30]) = {rxy.min():.3f} mm  ({len(Vb)} verts)"
    )


def main() -> None:
    print(f"=== translate_artery_to_p_contact ===")
    print(f"  P_contact_alvo (parede ONS): "
          f"({P_CONTACT_M[0]*1e3:.2f}, {P_CONTACT_M[1]*1e3:.2f}, {P_CONTACT_M[2]*1e3:.2f}) mm")
    print(f"  P_centerline_alvo          : "
          f"({P_CL_TARGET_M[0]*1e3:.2f}, {P_CL_TARGET_M[1]*1e3:.2f}, {P_CL_TARGET_M[2]*1e3:.2f}) mm")
    print(f"  R_outer_tube_FSI           : {R_OUTER_TUBE_M*1e3:.3f} mm")
    print(f"  R_ONS                      : {R_ONS_M*1e3:.3f} mm\n")

    artery_path = TRI / "artery.stl"
    pre_path = TRI / "artery.stl.pre_p_contact.stl"

    # 1) Restore from pre_p_contact backup if exists (estado pos-escala, pre-translacao)
    if pre_path.exists():
        shutil.copyfile(pre_path, artery_path)
        print(f"[restored] artery.stl <- artery.stl.pre_p_contact.stl")
    else:
        print(f"[warn] sem backup pre_p_contact; usando artery.stl como esta")

    V_m, F = read_ascii_stl_facets(artery_path)
    F, vol0 = fix_winding(V_m, F)
    print(f"[load] {len(V_m)} vertices, {len(F)} faces, vol = {vol0*1e9:.3f} mm^3")
    report_state("artery.stl (pre-translate)", V_m)

    # 2) Extract centerline
    print(f"\n[centerline] voxelizando @ pitch={VOX_PITCH_M*1e3} mm + skeletonize ...")
    cl = extract_centerline(V_m, F)
    print(f"  centerline: {len(cl)} pontos, "
          f"bounds(mm) "
          f"x[{cl[:,0].min()*1e3:+.2f},{cl[:,0].max()*1e3:+.2f}] "
          f"y[{cl[:,1].min()*1e3:+.2f},{cl[:,1].max()*1e3:+.2f}] "
          f"z[{cl[:,2].min()*1e3:+.2f},{cl[:,2].max()*1e3:+.2f}]")

    # 3) Closest centerline point to z-axis in z [0, 30] (informativo)
    P_close, r_close, _ = closest_centerline_point_to_z_axis(cl, Z0_M, Z1_M)
    print(f"\n  centerline closest to z-axis (z em [0,30]): "
          f"({P_close[0]*1e3:+.3f}, {P_close[1]*1e3:+.3f}, {P_close[2]*1e3:+.3f}) mm   "
          f"r_xy = {r_close*1e3:.3f} mm")

    # 4) BUSCA o melhor delta: itera sobre cada P_k da centerline. Para cada,
    # delta_k = P_cl_target - P_k. Aceita delta_k se em z[0,30] pos-translate,
    # nenhum ponto da centerline tem r_xy < R_TARGET_CL = R_ONS + R_OUTER_TUBE
    # + CLEARANCE = 3.55 mm.
    R_target = R_TARGET_CL_M
    print(f"\n[search] iterando {len(cl)} candidatos para tangencia "
          f"r_xy_min >= {R_target*1e3:.3f} mm em z[0,30]  "
          f"(R_ONS + R_outer + clearance({CLEARANCE_MM:.2f}mm))...")
    delta, k_best, min_r_after = find_best_translation(
        cl, P_CL_TARGET_M, R_target, Z0_M, Z1_M
    )
    print(f"  [escolhido] P_k(idx={k_best}) = "
          f"({cl[k_best,0]*1e3:+.3f}, {cl[k_best,1]*1e3:+.3f}, "
          f"{cl[k_best,2]*1e3:+.3f}) mm  "
          f"|delta_busca| = {np.linalg.norm(delta)*1e3:.4f} mm   "
          f"min_r_xy_after = {min_r_after*1e3:.4f} mm")

    # Aplica shift rigido adicional (microajuste fino solicitado pelo usuario)
    extra = EXTRA_TRANSLATION_MM * 1e-3
    delta = delta + extra
    print(f"\n[delta_busca] = ({(delta-extra)[0]*1e3:+.4f}, "
          f"{(delta-extra)[1]*1e3:+.4f}, {(delta-extra)[2]*1e3:+.4f}) mm")
    print(f"[extra_shift] = ({extra[0]*1e3:+.4f}, {extra[1]*1e3:+.4f}, "
          f"{extra[2]*1e3:+.4f}) mm")
    print(f"[delta TOTAL] = ({delta[0]*1e3:+.4f}, {delta[1]*1e3:+.4f}, "
          f"{delta[2]*1e3:+.4f}) mm  (|delta| = {np.linalg.norm(delta)*1e3:.4f} mm)")

    # #region agent log
    _theta_resulting = float(np.degrees(np.arctan2(P_CL_TARGET_M[1], P_CL_TARGET_M[0])))
    _debug_log(
        "POST_FIX",
        "translate.py:target_chosen",
        "Novo alvo de contato (pos-fix)",
        {
            "P_contact_theta_deg": float(P_CONTACT_THETA_DEG),
            "P_contact_z_mm": float(P_CONTACT_Z_MM),
            "P_contact_xyz_mm": (P_CONTACT_M * 1e3).tolist(),
            "P_centerline_target_xyz_mm": (P_CL_TARGET_M * 1e3).tolist(),
            "delta_mm": (delta * 1e3).tolist(),
            "delta_norm_mm": float(np.linalg.norm(delta) * 1e3),
            "k_chosen": int(k_best),
            "P_centerline_target_theta_deg": _theta_resulting,
            "expected_quadrant": "+X-Y",
        },
    )
    # #endregion

    V_new = V_m + delta
    cl_new = cl + delta

    # 5) Verify
    P_close_new, r_close_new, _ = closest_centerline_point_to_z_axis(cl_new, Z0_M, Z1_M)
    print(f"\n[verify] centerline closest to z-axis pos-translate: "
          f"({P_close_new[0]*1e3:+.4f}, {P_close_new[1]*1e3:+.4f}, "
          f"{P_close_new[2]*1e3:+.4f}) mm   r_xy = {r_close_new*1e3:.4f} mm "
          f"(target {R_target*1e3:.3f} mm)")

    # Verifica vertices da artery.stl: ainda pode haver wall vertice mais
    # proximo do eixo do que centerline - R_outer (geometria local), mas o
    # criterio realmente importante e a centerline (porque a malha FSI usa
    # um tubo de raio constante R_OUTER em torno dela).
    rxy_wall = np.hypot(V_new[:, 0], V_new[:, 1])
    mask_wall = (V_new[:, 2] >= Z0_M) & (V_new[:, 2] <= Z1_M)
    rxy_wall_band = rxy_wall[mask_wall]
    print(f"  artery.stl wall: min r_xy(z[0,30]) = {rxy_wall_band.min()*1e3:.3f} mm  "
          f"(arteria anatomica raio local pode diferir do tubo FSI)")
    n_wall_inside_ons = int((rxy_wall_band < R_ONS_M - 1e-9).sum())

    # #region agent log
    _V_band = V_new[mask_wall] * 1e3
    if len(_V_band) > 0:
        _r_band_mm = np.hypot(_V_band[:, 0], _V_band[:, 1])
        _kmin = int(np.argmin(_r_band_mm))
        _theta_wall_deg = float(np.degrees(np.arctan2(_V_band[_kmin, 1], _V_band[_kmin, 0])))
        _debug_log(
            "POST_FIX",
            "translate.py:wall_closest",
            "Vertice da parede mais proximo do eixo z apos translacao",
            {
                "x_mm": float(_V_band[_kmin, 0]),
                "y_mm": float(_V_band[_kmin, 1]),
                "z_mm": float(_V_band[_kmin, 2]),
                "r_xy_mm": float(_r_band_mm[_kmin]),
                "theta_deg": _theta_wall_deg,
                "is_X_pos_Y_neg": bool(_V_band[_kmin, 0] > 0 and _V_band[_kmin, 1] < 0),
            },
        )

    _P_close_new_theta = float(np.degrees(np.arctan2(P_close_new[1], P_close_new[0])))
    _debug_log(
        "POST_FIX",
        "translate.py:centerline_closest",
        "Centerline closest ao eixo z apos translacao",
        {
            "x_mm": float(P_close_new[0] * 1e3),
            "y_mm": float(P_close_new[1] * 1e3),
            "z_mm": float(P_close_new[2] * 1e3),
            "r_xy_mm": float(r_close_new * 1e3),
            "theta_deg": _P_close_new_theta,
            "n_wall_vertices_inside_ons": n_wall_inside_ons,
            "is_X_pos_Y_neg": bool(P_close_new[0] > 0 and P_close_new[1] < 0),
        },
    )
    # #endregion
    if n_wall_inside_ons > 0:
        print(f"  AVISO: {n_wall_inside_ons} vertices da parede anatomica "
              f"ainda dentro do cilindro ONS - mas o tubo FSI extrudado "
              f"sera tangente em P_contact (centerline correta).")

    # 6) Save translated artery.stl (mesma forma, so transladada)
    write_ascii_stl(artery_path, V_new, F, "artery_surface")
    print(f"\n[write] {artery_path.relative_to(REPO)}  (mesma forma + delta)")

    # 7) artery_outer.stl e artery_inner.stl: regenera a partir de artery.stl
    # (transladada). Os backups .pre_p_contact tinham um SHIFT espurio de
    # ~(-3.99, +0.24, 0) mm relativo a artery.stl, herdado de pipeline antigo,
    # que causava sobreposicao anomala com o ONS. Confirmado por
    # debug_overlap_diagnostic: 844 vertices de artery_outer dentro do ONS,
    # min r_xy = 0.18 mm.
    #
    # Filosofia: artery_outer = parede externa anatomica = artery.stl
    # (a forma anatomica completa, com detalhe de ponta preservado pela
    # translacao rigida). artery_inner = artery.stl deslocado para dentro
    # por H_WALL ao longo das normais de vertice (parede de espessura
    # constante 0.2 mm).
    outer_path = TRI / "artery_outer.stl"
    inner_path = TRI / "artery_inner.stl"

    write_ascii_stl(outer_path, V_new, F, "artery_outer_surface")
    bo = np.stack([V_new.min(axis=0), V_new.max(axis=0)])
    print(f"[write] {outer_path.relative_to(REPO)}  (= artery.stl, mesma forma)  "
          f"bounds(mm) x[{bo[0,0]*1e3:+.2f},{bo[1,0]*1e3:+.2f}] "
          f"y[{bo[0,1]*1e3:+.2f},{bo[1,1]*1e3:+.2f}] "
          f"z[{bo[0,2]*1e3:+.2f},{bo[1,2]*1e3:+.2f}]")

    vn = vertex_normals_outward(V_new, F)
    V_inner_new = V_new - H_WALL_M * vn
    F_inner = F.copy()
    F_inner, _ = fix_winding(V_inner_new, F_inner)
    write_ascii_stl(inner_path, V_inner_new, F_inner, "artery_inner_surface")
    bi = np.stack([V_inner_new.min(axis=0), V_inner_new.max(axis=0)])
    print(f"[write] {inner_path.relative_to(REPO)}  (artery.stl - H_WALL*normal)  "
          f"bounds(mm) x[{bi[0,0]*1e3:+.2f},{bi[1,0]*1e3:+.2f}] "
          f"y[{bi[0,1]*1e3:+.2f},{bi[1,1]*1e3:+.2f}] "
          f"z[{bi[0,2]*1e3:+.2f},{bi[1,2]*1e3:+.2f}]")

    # bo, bi ja preenchidos durante a regeneracao acima.

    # locationInMesh: ponto da centerline (apos translacao) mais proximo do
    # centroide. Como a centerline atravessa o lumen, esse ponto e seguramente
    # interno ao tubo gerado em torno dela.
    cl_centroid = cl_new.mean(axis=0)
    loc_idx = int(np.argmin(np.linalg.norm(cl_new - cl_centroid, axis=1)))
    loc_fluid = cl_new[loc_idx].copy()
    # locationInMesh do annulus (solido): ponto deslocado da centerline por
    # 0.5 * (R_lumen + R_outer) ~ 0.65 mm na direcao normal a tangente.
    if loc_idx == 0:
        tangent = cl_new[1] - cl_new[0]
    elif loc_idx == len(cl_new) - 1:
        tangent = cl_new[-1] - cl_new[-2]
    else:
        tangent = cl_new[loc_idx + 1] - cl_new[loc_idx - 1]
    tangent /= max(np.linalg.norm(tangent), 1e-30)
    # vetor perpendicular a tangente, no plano que melhor evita o eixo z
    z_axis = np.array([0.0, 0.0, 1.0])
    normal = np.cross(tangent, z_axis)
    if np.linalg.norm(normal) < 1e-6:
        normal = np.cross(tangent, np.array([1.0, 0.0, 0.0]))
    normal /= np.linalg.norm(normal)
    R_LUMEN_M = 0.55e-3
    r_solid_offset = 0.5 * (R_LUMEN_M + (R_LUMEN_M + H_WALL_M))  # = 0.65 mm
    loc_solid = loc_fluid + r_solid_offset * normal

    hints = {
        "wall_thickness_mm": H_WALL_M * 1e3,
        "solid_locationInMesh": loc_solid.tolist(),
        "fluid_locationInMesh": loc_fluid.tolist(),
        "z_end_back_m": float(bo[0, 2] - 0.0003),
        "z_end_front_m": float(bo[1, 2] + 0.0003),
        "bounds_outer_m": bo.tolist(),
        "bounds_inner_m": bi.tolist(),
        "signed_volume_outer_m3": vol0,
        "locationInMesh_validation": "centerline-based: loc_fluid em ponto da skel; loc_solid offset perpendicular",
        "last_rigid_translation_m": delta.tolist(),
    }
    HINTS_JSON.write_text(json.dumps(hints, indent=2))
    print(f"[write] {HINTS_JSON.relative_to(REPO)}")

    # 10) Update _artery_translated_summary.json
    summary = {
        "operation": "rigid translation: centerline tangent to (R_ONS + R_outer_tube) cylinder at P_contact",
        "P_contact_target_m": P_CONTACT_M.tolist(),
        "P_centerline_target_m": P_CL_TARGET_M.tolist(),
        "R_ONS_m": R_ONS_M,
        "R_outer_tube_m": R_OUTER_TUBE_M,
        "centerline_pre_translation_closest_m": P_close.tolist(),
        "centerline_pre_translation_min_r_xy_mm": float(r_close * 1e3),
        "delta_translation_m": delta.tolist(),
        "delta_translation_mm": (delta * 1e3).tolist(),
        "after_translation": {
            "centerline_closest_m": P_close_new.tolist(),
            "centerline_min_r_xy_mm": float(r_close_new * 1e3),
            "wall_min_r_xy_mm_in_z_band": float(rxy_wall_band.min() * 1e3),
            "n_wall_vertices_inside_ons_cylinder": int(n_wall_inside_ons),
            "outer_bounds_mm": (bo * 1e3).tolist(),
        },
    }
    (TRI / "_artery_translated_summary.json").write_text(json.dumps(summary, indent=2))
    print(f"[write] cases/ao-mestrado/constant/triSurface/_artery_translated_summary.json")

    # 11) Update closest_to_ON_ref.json (preCICE watchpoint)
    # Idealmente o watchpoint deveria ser o ponto da PAREDE da malha FSI
    # mais proximo do nervo. Como a parede FSI e gerada em runtime, escolhemos
    # P_contact analitico, que sera o ponto real de contato pos-extrusao.
    closest_doc = {
        "description": "Watchpoint preCICE = ponto teorico de contato arteria-ONS apos translacao rigida.",
        "R_ons_m": R_ONS_M,
        "z_range_m": [Z0_M, Z1_M],
        "closest_point_m": P_CONTACT_M.tolist(),
        "min_distance_m": 0.0,
        "precice_watchpoint_coordinate": (
            f"{P_CONTACT_M[0]:.6f};{P_CONTACT_M[1]:.6f};{P_CONTACT_M[2]:.6f}"
        ),
        "centerline_target_m": P_CL_TARGET_M.tolist(),
        "delta_translation_applied_m": delta.tolist(),
    }
    CLOSEST_JSON.write_text(json.dumps(closest_doc, indent=2))
    print(f"[write] {CLOSEST_JSON.relative_to(REPO)}")

    # Mirror para fluid/ e solid/ se existirem
    for sub in ("fluid", "solid"):
        sub_dir = REPO / "cases" / "ao-mestrado" / sub / "constant"
        if sub_dir.is_dir():
            (sub_dir / "closest_to_ON_ref.json").write_text(json.dumps(closest_doc, indent=2))
            print(f"[write] cases/ao-mestrado/{sub}/constant/closest_to_ON_ref.json")

    print(f"\n[ok] arteria posicionada. Exec build_teste_geom em runtime "
          f"produzira parede FSI tangente ao ONS APENAS em P_contact.")
    print(f"     Verifique apos rodar Allrun: as celulas da parede em "
          f"z=18.5 mm devem estar em contato com o ONS, e nenhuma celula "
          f"em z em [0,30] mm deve invadir o cilindro r_xy < 2.5 mm.")


if __name__ == "__main__":
    main()
