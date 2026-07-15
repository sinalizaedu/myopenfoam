#!/usr/bin/env python3
"""
Diagnostico visual dos dominios de FSI artoph-fsi-curva-mestrado.

Compara:
  - STL artery_outer (parede externa)
  - STL artery_inner (parede interna -- offset por h=0.2 mm)
  - Bounding box do background blockMesh
  - location_in_mesh do snappy (fluido e solido)
  - centroide REAL do lumen (estimado por amostragem)

Gera plot 3D para detectar:
  - locationInMesh do fluido cair FORA do lumen (artéria curva)
  - solid faltando artery_inner como cutting surface (manteria artéria cheia)
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

REPO = Path(__file__).resolve().parents[1]
CASE = REPO / "cases" / "artoph-fsi-curva-mestrado"


def read_stl_facets(path: Path, max_facets: int | None = None) -> tuple[np.ndarray, np.ndarray]:
    verts: list[tuple[float, float, float]] = []
    faces: list[list[int]] = []
    key_to_idx: dict[tuple[float, float, float], int] = {}
    buf: list[tuple[float, float, float]] = []

    def add(p: tuple[float, float, float]) -> int:
        k = (round(p[0], 9), round(p[1], 9), round(p[2], 9))
        if k in key_to_idx:
            return key_to_idx[k]
        i = len(verts)
        verts.append(p)
        key_to_idx[k] = i
        return i

    with path.open() as f:
        for line in f:
            ls = line.strip()
            if ls.startswith("vertex"):
                parts = ls.split()
                buf.append((float(parts[1]), float(parts[2]), float(parts[3])))
                if len(buf) == 3:
                    faces.append([add(buf[0]), add(buf[1]), add(buf[2])])
                    buf.clear()
                    if max_facets and len(faces) >= max_facets:
                        break
    V = np.array(verts)
    F = np.array(faces)
    return V, F


def read_block_bounds(path: Path) -> np.ndarray:
    """blockMeshDict vertices: extrai bounding box dos 8 cantos do hex."""
    text = path.read_text()
    nums = re.findall(r"\(\s*(-?[0-9.eE+\-]+)\s+(-?[0-9.eE+\-]+)\s+(-?[0-9.eE+\-]+)\s*\)", text)
    pts = np.array([list(map(float, t)) for t in nums[:8]])
    return np.stack([pts.min(axis=0), pts.max(axis=0)], axis=0)


def read_location_in_mesh(snappy_path: Path) -> np.ndarray | None:
    text = snappy_path.read_text()
    m = re.search(r"locationInMesh\s*\(\s*([\d.eE+\-]+)\s+([\d.eE+\-]+)\s+([\d.eE+\-]+)\s*\)", text)
    if not m:
        return None
    return np.array([float(m.group(1)), float(m.group(2)), float(m.group(3))])


def plot_triangulated_surface(ax, V: np.ndarray, F: np.ndarray, color: str, alpha: float, label: str):
    tris = V[F]
    coll = Poly3DCollection(tris, facecolor=color, edgecolor="none", alpha=alpha, label=label)
    ax.add_collection3d(coll)


def draw_box(ax, bmin: np.ndarray, bmax: np.ndarray, color: str, lw: float, label: str):
    x = [bmin[0], bmax[0]]
    y = [bmin[1], bmax[1]]
    z = [bmin[2], bmax[2]]
    pts = np.array([(xi, yi, zi) for xi in x for yi in y for zi in z])
    edges = [
        (0, 1), (0, 2), (0, 4), (3, 1), (3, 2), (3, 7),
        (5, 1), (5, 4), (5, 7), (6, 2), (6, 4), (6, 7),
    ]
    first = True
    for i, j in edges:
        ax.plot(*zip(pts[i], pts[j]), color=color, lw=lw,
                label=label if first else None)
        first = False


def main() -> None:
    print("=" * 72)
    print("DIAGNOSTICO GEOMETRICO: artoph-fsi-curva-mestrado")
    print("=" * 72)

    outer_stl = CASE / "constant" / "triSurface" / "artery_outer.stl"
    inner_stl = CASE / "constant" / "triSurface" / "artery_inner.stl"
    V_out, F_out = read_stl_facets(outer_stl)
    V_in, F_in = read_stl_facets(inner_stl)

    print(f"\nSTL outer: {len(V_out)} verts, {len(F_out)} faces")
    print(f"  bounds: {V_out.min(axis=0)*1e3} .. {V_out.max(axis=0)*1e3} mm")
    print(f"STL inner: {len(V_in)} verts, {len(F_in)} faces")
    print(f"  bounds: {V_in.min(axis=0)*1e3} .. {V_in.max(axis=0)*1e3} mm")

    # blockMeshDict pode estar em system/ ou constant/polyMesh/
    box_f_path = CASE / "fluid" / "system" / "blockMeshDict"
    if not box_f_path.exists():
        box_f_path = CASE / "fluid" / "constant" / "polyMesh" / "blockMeshDict"
    box_f = read_block_bounds(box_f_path)
    box_s = read_block_bounds(CASE / "solid" / "system" / "blockMeshDict")
    print(f"\nBlock fluid: {box_f[0]*1e3} .. {box_f[1]*1e3} mm  (size {((box_f[1]-box_f[0])*1e3)} mm)")
    print(f"Block solid: {box_s[0]*1e3} .. {box_s[1]*1e3} mm")

    loc_f = read_location_in_mesh(CASE / "fluid" / "system" / "snappyHexMeshDict")
    loc_s = read_location_in_mesh(CASE / "solid" / "system" / "snappyHexMeshDict")
    print(f"\nlocationInMesh fluid: {loc_f*1e3} mm")
    print(f"locationInMesh solid: {loc_s*1e3} mm")

    centroid_in = V_in.mean(axis=0)
    centroid_out = V_out.mean(axis=0)
    print(f"\nCentroide vertices inner: {centroid_in*1e3} mm  (usado como loc_fluid pelo script de build)")
    print(f"Centroide vertices outer: {centroid_out*1e3} mm")

    # Distancia da loc_fluid ate a superficie interna mais proxima (todos os vertices)
    d_inner = np.linalg.norm(V_in - loc_f, axis=1).min()
    d_outer = np.linalg.norm(V_out - loc_f, axis=1).min()
    print(f"\nDistancia loc_fluid -> sup. inner mais proxima: {d_inner*1e3:.3f} mm")
    print(f"Distancia loc_fluid -> sup. outer mais proxima: {d_outer*1e3:.3f} mm")
    print(f"Se loc_fluid esta DENTRO do lumen, d_inner deve ser ~raio/2 (~0.3 mm)")
    print(f"  e d_outer deve ser ~ d_inner + 0.2 mm.")

    # Plot
    fig = plt.figure(figsize=(14, 11))
    ax = fig.add_subplot(111, projection="3d")

    plot_triangulated_surface(ax, V_out, F_out, color="#cc4400", alpha=0.20, label="artery_outer (parede ext)")
    plot_triangulated_surface(ax, V_in, F_in, color="#0066cc", alpha=0.20, label="artery_inner (lumen)")

    draw_box(ax, box_f[0], box_f[1], color="green", lw=1.5, label="blockMesh background (fluid/solid)")

    ax.scatter([loc_f[0]], [loc_f[1]], [loc_f[2]], c="blue", s=140, marker="*",
               label=f"locationInMesh fluid", edgecolor="k", linewidth=1)
    ax.scatter([loc_s[0]], [loc_s[1]], [loc_s[2]], c="red", s=140, marker="*",
               label=f"locationInMesh solid", edgecolor="k", linewidth=1)
    ax.scatter([centroid_in[0]], [centroid_in[1]], [centroid_in[2]], c="cyan", s=80, marker="x",
               label="centroide inner_stl")

    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_zlabel("z [m]")
    ax.set_title("artoph-fsi: superficies artery_outer (vermelho) e artery_inner (azul)\n"
                 "caixa do blockMesh (verde) e pontos locationInMesh do snappy")
    ax.legend(loc="upper left", fontsize=9)

    # Aspect ratio
    bx, by, bz = box_f[1] - box_f[0]
    ax.set_box_aspect((bx, by, bz))

    out_png = REPO / "brunaStuff" / "inspect_artoph_fsi_domains.png"
    fig.tight_layout()
    fig.savefig(out_png, dpi=140)
    print(f"\nPlot salvo em: {out_png}")


if __name__ == "__main__":
    main()
