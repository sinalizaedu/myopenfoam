#!/usr/bin/env python3
"""
Constroi polyMesh da arteria oftalmica para o caso `cases/sugestao/`.

Reutiliza a logica de extrusao por centerline + parallel-transport de
`build_artoph_tubular_meshes.py`, com adaptacoes:

  - Le o STL de `cases/sugestao/constant/triSurface/artery.stl` (translado
    para tocar o ONS no ponto P_contact, herdado do ao-mestrado).
  - Escreve a polyMesh em `cases/sugestao/solid/staging/arteria/constant/polyMesh/`.
  - Adiciona um arquivo `cellZones` colocando TODAS as cells na zona "arteria",
    de modo que apos `mergeMeshes` com a malha do nervo, a zona arteria
    permanece identificavel para o `mechanicalProperties` multi-zona.
  - Patches: arteria_lumen (i_min), arteria_externa (i_max), inner_cap_back,
    inner_cap_front (cap_back/cap_front). Sao os patches usados pelo
    solid/0/D do caso `sugestao`.

Uso (rodar no host ou no container):
  python3 build_sugestao_solid_arteria.py

Aceita os mesmos parametros geometricos default de build_artoph
(R_LUMEN_M, H_WALL_M, NZ, NCIRC, NRAD_WALL).
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import numpy as np

# Reusa o modulo existente
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_artoph_tubular_meshes as bam  # noqa: E402


def find_sugestao_case() -> Path:
    candidates = [
        Path(__file__).resolve().parents[1] / "cases" / "sugestao",
        Path("/simulation/sugestao"),
    ]
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError("cases/sugestao nao encontrado.")


def find_src_stl(case: Path) -> Path:
    candidates = [
        case / "constant" / "triSurface" / "artery.stl",
        # Fallback: STL do ao-mestrado (mesma geometria translada)
        case.parent / "ao-mestrado" / "constant" / "triSurface" / "artery.stl",
    ]
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError(
        f"artery.stl nao encontrado em {candidates}. Coloque-o em "
        f"{case}/constant/triSurface/."
    )


def write_cellzones_all_arteria(out_dir: Path, n_cells: int) -> None:
    """Escreve o arquivo polyMesh/cellZones colocando todas as celulas
    em uma unica zona chamada `arteria`. Esse arquivo eh preservado pelo
    mergeMeshes e fica disponivel para o mechanicalProperties multi-zona.
    """
    fpath = out_dir / "cellZones"
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
        f.write("arteria\n{\n")
        f.write("    type cellZone;\n")
        f.write("    cellLabels      List<label>\n")
        f.write(f"{n_cells}\n(\n")
        for i in range(n_cells):
            f.write(f"{i}\n")
        f.write(");\n")
        f.write("}\n)\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nz", type=int, default=bam.NZ)
    ap.add_argument("--ncirc", type=int, default=bam.NCIRC)
    ap.add_argument("--nrad-wall", type=int, default=bam.NRAD_WALL)
    args = ap.parse_args()

    case = find_sugestao_case()
    src_stl = find_src_stl(case)

    print(f"[sugestao] STL fonte: {src_stl}")
    pts = bam.read_ascii_stl_vertices(src_stl)
    print(f"[sugestao]   {len(pts)} vertices STL")

    print("[sugestao] Extraindo centerline (PCA seeds + relax)...")
    cl_raw = bam.extract_centerline_marching(
        pts, r_search_m=1.5e-3, n_seeds=100, n_iter=8
    )
    arc = float(np.sum(np.linalg.norm(np.diff(cl_raw, axis=0), axis=1)))
    print(f"[sugestao]   centerline raw: {len(cl_raw)} pts, arc {arc*1e3:.2f} mm")

    cl = bam.smooth_centerline(cl_raw, nz_out=args.nz)
    print(f"[sugestao] Suavizada para {args.nz} secoes "
          f"(arc {np.sum(np.linalg.norm(np.diff(cl, axis=0), axis=1))*1e3:.2f} mm)")

    T, N, B = bam.parallel_transport_frames(cl)
    _ = T

    R_in = bam.R_LUMEN_M
    R_out = bam.R_LUMEN_M + bam.H_WALL_M
    print(f"[sugestao] Construindo annulus arterial (R_in={R_in*1e3:.2f} mm, "
          f"R_out={R_out*1e3:.2f} mm, ncirc={args.ncirc}, nrad={args.nrad_wall})")

    mesh_solid = bam.build_annulus_foam_mesh(
        cl, N, B, R_in, R_out, args.ncirc, args.nrad_wall,
        patch_names={
            "cap_back":  "inner_cap_back",
            "cap_front": "inner_cap_front",
            "r_inner":   "arteria_lumen",
            "r_outer":   "arteria_externa",
        },
    )

    pm_dir = case / "solid" / "staging" / "arteria" / "constant" / "polyMesh"
    if pm_dir.exists():
        shutil.rmtree(pm_dir)
    stats = bam.write_polymesh(
        mesh_solid, pm_dir,
        patch_types={
            "inner_cap_back":  "wall",
            "inner_cap_front": "wall",
            "arteria_lumen":   "wall",
            "arteria_externa": "wall",
        },
    )
    print(f"[sugestao]   ARTERIA solid: {stats['nPoints']} pts, "
          f"{stats['nCells']} cells, {stats['nFaces']} faces")
    for name, start, count in stats["patches"]:
        print(f"[sugestao]     patch {name}: start={start} nFaces={count}")

    # cellZones com todas as celulas na zona "arteria" (preservada pelo
    # mergeMeshes ao combinar com o nervo)
    write_cellzones_all_arteria(pm_dir, stats["nCells"])
    print(f"[sugestao]   cellZones escrito ({stats['nCells']} cells em zona 'arteria')")
    print("[sugestao] OK.")


if __name__ == "__main__":
    main()
