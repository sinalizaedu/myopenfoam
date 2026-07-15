#!/usr/bin/env python3
"""
contact_area.py
===============
Computa a area total [m^2] de um patch do polyMesh OpenFOAM (default:
contact_local, o patch focal da arteria oftalmica no on-caso-3).

Motivacao: o P_contact entra no CalculiX como *DSLOAD ... P (pressao) sobre a
superficie CONTACT_LOCAL_SURF. A FORCA arterial total e' F = P * A, e a area A
do patch muda com o refino da malha (o boxToFace seleciona mais/menos faces).
Para que o estudo de independencia de malha (e a varredura de p_c) compare a
mesma FORCA arterial, normaliza-se a pressao por malha: P = F_alvo / A.

Uso:
    python3 contact_area.py <polyMeshDir> [--patch contact_local]
    -> imprime a area em m^2 (uma linha, parse-friendly).

Tambem expoe area_of_patch() para reuso.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import numpy as np


def _strip_foam(text: str) -> str:
    """Remove comentarios C/C++ e o cabecalho FoamFile{...}."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//[^\n]*", "", text)
    # remove o bloco FoamFile { ... }
    text = re.sub(r"FoamFile\s*\{.*?\}", "", text, flags=re.DOTALL)
    return text


def read_points(polymesh: Path) -> np.ndarray:
    text = _strip_foam((polymesh / "points").read_text())
    # primeiro inteiro = contagem; depois ( ... ) com tuplas "(x y z)"
    body = text[text.index("(") + 1: text.rindex(")")]
    pts = re.findall(r"\(\s*([^\)]+?)\s*\)", body)
    arr = np.array([[float(x) for x in p.split()] for p in pts], dtype=float)
    return arr


def read_faces(polymesh: Path):
    """Retorna lista de faces (cada uma = lista de indices de pontos)."""
    text = _strip_foam((polymesh / "faces").read_text())
    body = text[text.index("(") + 1: text.rindex(")")]
    # cada face: "n(v0 v1 v2 ...)"
    faces = []
    for m in re.finditer(r"(\d+)\s*\(\s*([\d\s]+?)\s*\)", body):
        verts = [int(v) for v in m.group(2).split()]
        faces.append(verts)
    return faces


def read_boundary(polymesh: Path):
    """Retorna {patch_name: (nFaces, startFace)}."""
    text = (polymesh / "boundary").read_text()
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//[^\n]*", "", text)
    out = {}
    # casa "name { ... nFaces N; ... startFace S; ... }"
    for m in re.finditer(r"(\w+)\s*\{([^}]*)\}", text):
        name, body = m.group(1), m.group(2)
        nf = re.search(r"nFaces\s+(\d+)\s*;", body)
        sf = re.search(r"startFace\s+(\d+)\s*;", body)
        if nf and sf:
            out[name] = (int(nf.group(1)), int(sf.group(1)))
    return out


def _poly_area(verts_xyz: np.ndarray) -> float:
    """Area de um poligono 3D (fan a partir do vertice 0)."""
    if len(verts_xyz) < 3:
        return 0.0
    p0 = verts_xyz[0]
    n = np.zeros(3)
    for i in range(1, len(verts_xyz) - 1):
        n = n + np.cross(verts_xyz[i] - p0, verts_xyz[i + 1] - p0)
    return 0.5 * float(np.linalg.norm(n))


def area_of_patch(polymesh: Path, patch: str = "contact_local"):
    """(area_total_m2, n_faces) do patch."""
    bnd = read_boundary(polymesh)
    if patch not in bnd:
        raise KeyError(f"patch '{patch}' nao encontrado em {polymesh}/boundary "
                       f"(patches: {sorted(bnd)})")
    nf, sf = bnd[patch]
    pts = read_points(polymesh)
    faces = read_faces(polymesh)
    total = 0.0
    for f in range(sf, sf + nf):
        total += _poly_area(pts[faces[f]])
    return total, nf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("polymesh", help="diretorio polyMesh")
    ap.add_argument("--patch", default="contact_local")
    args = ap.parse_args()
    area, nf = area_of_patch(Path(args.polymesh), args.patch)
    # uma linha parse-friendly + um comentario humano em stderr
    import sys
    print(f"{area:.10e}")
    print(f"[contact_area] patch={args.patch} nFaces={nf} A={area*1e6:.5f} mm^2",
          file=sys.stderr)


if __name__ == "__main__":
    main()
