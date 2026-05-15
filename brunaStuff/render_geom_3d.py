"""Render 3D views of both STL parts to finally understand the geometry."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

PARTS_DIR = Path(__file__).parent / "geom_mestrado_parts"


def render(meshes_with_color, view, ax):
    for mesh, color, label in meshes_with_color:
        tris = mesh.vertices[mesh.faces]
        coll = Poly3DCollection(tris, alpha=0.45, facecolor=color, edgecolor="k", linewidth=0.05)
        ax.add_collection3d(coll)
    all_v = np.vstack([m[0].vertices for m in meshes_with_color])
    mins = all_v.min(axis=0)
    maxs = all_v.max(axis=0)
    ranges = maxs - mins
    mid = (mins + maxs) / 2
    r = ranges.max() / 2
    ax.set_xlim(mid[0] - r, mid[0] + r)
    ax.set_ylim(mid[1] - r, mid[1] + r)
    ax.set_zlim(mid[2] - r, mid[2] + r)
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.set_zlabel("z (mm)")
    ax.view_init(elev=view[0], azim=view[1])
    ax.set_title(f"elev={view[0]}, azim={view[1]}")


def main() -> None:
    nerve = trimesh.load_mesh(str(PARTS_DIR / "part_00.stl"))
    artery = trimesh.load_mesh(str(PARTS_DIR / "part_01.stl"))

    meshes = [
        (nerve, "steelblue", "part_00 (nervo)"),
        (artery, "crimson", "part_01 (artéria?)"),
    ]
    fig = plt.figure(figsize=(20, 14))
    views = [(20, -60), (20, 30), (90, -90), (0, -90), (0, 0), (45, 135)]
    for i, view in enumerate(views, 1):
        ax = fig.add_subplot(2, 3, i, projection="3d")
        render(meshes, view, ax)
    fig.suptitle("Geometria Mestrado — duas componentes do STL", fontsize=14)
    fig.tight_layout()
    out = PARTS_DIR / "geom_3d_views.png"
    fig.savefig(out, dpi=110)
    print(f"[write] {out}")

    fig2 = plt.figure(figsize=(12, 8))
    ax = fig2.add_subplot(111, projection="3d")
    render(meshes, (25, -50), ax)
    fig2.tight_layout()
    out2 = PARTS_DIR / "geom_3d_hero.png"
    fig2.savefig(out2, dpi=140)
    print(f"[write] {out2}")


if __name__ == "__main__":
    main()
