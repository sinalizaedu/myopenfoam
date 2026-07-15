#!/usr/bin/env python3
"""Copia a polyMesh sólida da artéria do caso `cases/ao-mestrado/solid/`
para `cases/sugestao/solid/staging/arteria/constant/polyMesh/` e a adapta
para uso no caso unificado:

  1) Copia points/faces/owner/neighbour/boundary/pointZones/faceZones/cellZones
     (tudo que existir).
  2) Renomeia o patch `lumen` -> `arteria_lumen` no arquivo `boundary`
     (manter o nome usado pelos preciceDict, 0/D, e function objects do
     caso `sugestao`).
  3) Garante que existe um arquivo `cellZones` com todas as cells
     na zona "arteria" (preservada por mergeMeshes).

Nada de extrair centerline / extrudar tubo: usa a malha JÁ validada do
ao-mestrado, que cobre a artéria oftálmica anatômica inteira.

Uso:
  python3 copy_arteria_mesh_from_ao_mestrado.py [--ao-mestrado-case PATH]
                                                 [--target-staging PATH]
"""
from __future__ import annotations
import argparse
import re
import shutil
import sys
from pathlib import Path


def find_default_paths() -> tuple[Path, Path]:
    here = Path(__file__).resolve()
    repo_candidates = [
        here.parents[3],                  # repo/cases/sugestao/scripts/
        Path("/simulation").parent,       # /simulation/sugestao/scripts/ in container
    ]
    for repo in repo_candidates:
        ao = repo / "cases" / "ao-mestrado"
        sug = repo / "cases" / "sugestao"
        if ao.exists() and sug.exists():
            return (
                ao / "solid" / "constant" / "polyMesh",
                sug / "solid" / "staging" / "arteria" / "constant" / "polyMesh",
            )
    # Fallback dentro do container
    return (
        Path("/simulation/ao-mestrado/solid/constant/polyMesh"),
        Path("/simulation/sugestao/solid/staging/arteria/constant/polyMesh"),
    )


def count_cells_from_owner(owner_path: Path) -> int:
    """nCells = max(owner) + 1. Lê o arquivo owner do polyMesh."""
    n_owner = 0
    max_label = -1
    with owner_path.open() as f:
        in_list = False
        n_decl = None
        for ln in f:
            ls = ln.strip()
            if not in_list:
                if re.match(r"^\d+$", ls) and n_decl is None:
                    n_decl = int(ls)
                    continue
                if ls.startswith("(") and n_decl is not None:
                    in_list = True
                    continue
                continue
            if ls.startswith(")"):
                break
            if re.match(r"^-?\d+$", ls):
                v = int(ls)
                if v > max_label:
                    max_label = v
                n_owner += 1
    return max_label + 1


def rename_patch_in_boundary(boundary_path: Path,
                             old_name: str, new_name: str) -> bool:
    """Renomeia patch <old_name> -> <new_name> no arquivo boundary do polyMesh.
    Retorna True se renomeou; False se nao encontrou."""
    txt = boundary_path.read_text()
    pat = re.compile(
        rf"^(\s*){re.escape(old_name)}(\s*\{{)", re.MULTILINE
    )
    if not pat.search(txt):
        return False
    new_txt = pat.sub(rf"\1{new_name}\2", txt)
    boundary_path.write_text(new_txt)
    return True


def translate_points_radially(pm_dir: Path,
                              R_ons_m: float = 2.5e-3,
                              overlap_um: float = 30.0,
                              ) -> dict:
    """Aplica translacao radial (no plano XY) para colocar a face mais
    proxima de arteria_externa em INTERPENETRACAO `overlap_um` micrometros
    com o cilindro do ONS (raio R_ons_m em torno do eixo z).

    Estrategia:
      1) Le points + faces + boundary do polyMesh.
      2) Identifica patch arteria_externa.
      3) Calcula o centroide de cada face desse patch e a distancia radial
         r_xy ao eixo z.
      4) Pega a face com r_xy minimo: ela esta a (r_min - R_ons) micrometros
         de FORA do cilindro do ONS (ou DENTRO se r_min < R_ons).
      5) Calcula vetor de translacao no plano XY tal que a face mais
         proxima fique a R_ons - overlap_um (interior do cilindro do ONS).
      6) Aplica essa translacao a TODOS os pontos do polyMesh.

    Retorna dict com diagnostico (delta, r_min antes/depois).
    """
    txt_pts = (pm_dir / "points").read_text()
    txt_faces = (pm_dir / "faces").read_text()
    txt_bnd = (pm_dir / "boundary").read_text()

    # Parse points
    pts = []
    in_list = False
    for ln in txt_pts.splitlines():
        s = ln.strip()
        if not in_list:
            if s.startswith("("):
                in_list = True
            continue
        if s.startswith(")"):
            break
        m = re.match(r"\(([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\)", s)
        if m:
            pts.append([float(m.group(1)), float(m.group(2)),
                        float(m.group(3))])

    # Parse faces
    faces = []
    in_list = False
    for ln in txt_faces.splitlines():
        s = ln.strip()
        if not in_list:
            if s.startswith("("):
                in_list = True
            continue
        if s.startswith(")"):
            break
        m = re.match(r"\d+\(([\d ]+)\)", s)
        if m:
            faces.append([int(x) for x in m.group(1).split()])

    # Parse boundary -> startFace, nFaces de arteria_externa
    m_bnd = re.search(
        r"\barteria_externa\s*\{[^{}]*?nFaces\s+(\d+)[^{}]*?startFace\s+(\d+)",
        txt_bnd, re.DOTALL,
    )
    if not m_bnd:
        return {"error": "patch arteria_externa nao encontrado"}
    nF = int(m_bnd.group(1))
    sF = int(m_bnd.group(2))

    # Centroides do patch + r_xy
    r_min = float("inf")
    cent_min_xy = (0.0, 0.0)
    for i in range(nF):
        face = faces[sF + i]
        cx = sum(pts[j][0] for j in face) / len(face)
        cy = sum(pts[j][1] for j in face) / len(face)
        r = (cx * cx + cy * cy) ** 0.5
        if r < r_min:
            r_min = r
            cent_min_xy = (cx, cy)

    # Vetor de translacao radial: levar r_min para R_ons - overlap
    target_r = R_ons_m - overlap_um * 1e-6
    delta_r = r_min - target_r       # Quanto reduzir r
    if r_min <= 0:
        return {"error": "r_min <= 0 (artery centroid no eixo Z)"}
    # direcao radial (de r_min em direcao ao eixo z)
    ux = -cent_min_xy[0] / r_min
    uy = -cent_min_xy[1] / r_min
    dx = ux * delta_r
    dy = uy * delta_r

    # Aplica translacao a TODOS os pontos (so XY)
    new_pts = []
    for p in pts:
        new_pts.append([p[0] + dx, p[1] + dy, p[2]])

    # Reescreve points
    header_end = txt_pts.find("(")
    head = txt_pts[: header_end + 1]
    body = "\n" + "\n".join(
        f"({p[0]:.10g} {p[1]:.10g} {p[2]:.10g})" for p in new_pts
    ) + "\n"
    # acha o ")" do fim da lista (apos os pontos), preserva o resto
    after = txt_pts[header_end + 1 :]
    # encontra o primeiro ")" depois do header
    rest_start = after.find(")")
    rest = after[rest_start:]
    (pm_dir / "points").write_text(head + body + rest)

    # Sanity check: re-parsa novamente para reportar r_min novo
    new_r_min = float("inf")
    for i in range(nF):
        face = faces[sF + i]
        cx = sum(new_pts[j][0] for j in face) / len(face)
        cy = sum(new_pts[j][1] for j in face) / len(face)
        r = (cx * cx + cy * cy) ** 0.5
        if r < new_r_min:
            new_r_min = r

    return {
        "delta_xy_m": (dx, dy),
        "delta_xy_um": (dx * 1e6, dy * 1e6),
        "r_min_before_mm": r_min * 1e3,
        "r_min_after_mm": new_r_min * 1e3,
        "R_ons_mm": R_ons_m * 1e3,
        "overlap_um_target": overlap_um,
        "overlap_um_achieved": (R_ons_m - new_r_min) * 1e6,
    }


def write_cellzones_all_arteria(pm_dir: Path, n_cells: int,
                                zone_name: str = "arteria") -> None:
    fpath = pm_dir / "cellZones"
    with fpath.open("w") as f:
        f.write(
            "FoamFile\n{\n"
            "    version     2.0;\n"
            "    format      ascii;\n"
            "    class       regIOobject;\n"
            "    location    \"constant/polyMesh\";\n"
            "    object      cellZones;\n"
            "}\n\n"
        )
        f.write("1\n(\n")
        f.write(f"{zone_name}\n{{\n")
        f.write("    type cellZone;\n")
        f.write("    cellLabels      List<label>\n")
        f.write(f"{n_cells}\n(\n")
        for i in range(n_cells):
            f.write(f"{i}\n")
        f.write(");\n}\n)\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ao-mestrado-mesh", default=None,
                    help="caminho da polyMesh sólida ao-mestrado")
    ap.add_argument("--target-staging", default=None,
                    help="caminho do polyMesh staging em sugestao")
    ap.add_argument("--zone-name", default="arteria")
    ap.add_argument("--R-ons-m", type=float, default=2.5e-3,
                    help="raio externo do ONS no caso sugestao (m)")
    ap.add_argument("--overlap-um", type=float, default=30.0,
                    help="overlap inicial desejado entre arteria_externa e "
                         "ons_outer (microns). Para criar uma "
                         "interpenetracao inicial leve que o solidContact "
                         "vai resolver no t=0. Use 0 para tangenciar.")
    ap.add_argument("--no-translate", action="store_true",
                    help="pula a translacao radial (debug)")
    args = ap.parse_args()

    src_def, dst_def = find_default_paths()
    src = Path(args.ao_mestrado_mesh) if args.ao_mestrado_mesh else src_def
    dst = Path(args.target_staging) if args.target_staging else dst_def

    print(f"[copy-arteria] origem (ao-mestrado): {src}")
    print(f"[copy-arteria] destino (sugestao staging): {dst}")

    if not (src / "points").exists():
        print(f"ERROR: polyMesh ao-mestrado nao encontrada em {src}.\n"
              f"Rode antes: cd cases/ao-mestrado && ./Allrun (ate o passo 1).",
              file=sys.stderr)
        sys.exit(1)

    if dst.exists():
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)

    files_to_copy = [
        "points", "faces", "owner", "neighbour", "boundary",
        "pointZones", "faceZones", "cellZones",  # opcionais
    ]
    dst.mkdir()
    copied = []
    for fn in files_to_copy:
        s = src / fn
        if s.exists():
            shutil.copy2(s, dst / fn)
            copied.append(fn)
    print(f"[copy-arteria] copiados: {copied}")

    n_cells = count_cells_from_owner(dst / "owner")
    print(f"[copy-arteria] nCells (do owner) = {n_cells}")

    bnd = dst / "boundary"
    if rename_patch_in_boundary(bnd, "lumen", "arteria_lumen"):
        print("[copy-arteria] patch 'lumen' renomeado para 'arteria_lumen'.")
    else:
        print("[copy-arteria] (patch 'lumen' nao presente — talvez ja "
              "renomeado ou usa outro nome). OK.")

    write_cellzones_all_arteria(dst, n_cells, zone_name=args.zone_name)
    print(f"[copy-arteria] cellZones escrito ({n_cells} cells em zona "
          f"'{args.zone_name}').")

    if not args.no_translate:
        print(f"[copy-arteria] aplicando translacao radial para criar "
              f"overlap inicial de {args.overlap_um} um com R_ons="
              f"{args.R_ons_m*1e3:.2f} mm...")
        info = translate_points_radially(dst,
                                         R_ons_m=args.R_ons_m,
                                         overlap_um=args.overlap_um)
        if "error" in info:
            print(f"[copy-arteria] WARNING: {info['error']}")
        else:
            print(f"[copy-arteria]   r_min ANTES:  {info['r_min_before_mm']:.4f} mm")
            print(f"[copy-arteria]   r_min DEPOIS: {info['r_min_after_mm']:.4f} mm")
            print(f"[copy-arteria]   R_ons:        {info['R_ons_mm']:.4f} mm")
            print(f"[copy-arteria]   delta_xy:     ({info['delta_xy_um'][0]:+.2f}, "
                  f"{info['delta_xy_um'][1]:+.2f}) um")
            print(f"[copy-arteria]   overlap alvo: {info['overlap_um_target']:.1f} um")
            print(f"[copy-arteria]   overlap real: {info['overlap_um_achieved']:.1f} um "
                  f"(positivo = interpenetracao)")
    print("[copy-arteria] OK.")


if __name__ == "__main__":
    main()
