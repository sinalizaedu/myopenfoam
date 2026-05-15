"""Render the current mesh as a SOLID surface (using triangles from each
boundary patch's VTP), with the optic nerve overlaid in the same coordinate
system. Output mimics what ParaView shows when "Representation = Surface".
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

REPO = Path(__file__).resolve().parents[1]
VTK_DIR = REPO / "cases/artoph-curva-mestrado/solid/VTK/solid_0/boundary"
NERVE_STL = REPO / "cases/artoph-curva-mestrado/solid/constant/triSurface/nerve.stl"


def read_vtp(path: Path):
    tree = ET.parse(path)
    root = tree.getroot()
    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0] + "}"
    pts = np.fromstring(
        root.find(f".//{ns}Points/{ns}DataArray").text, sep=" "
    ).reshape(-1, 3)
    conn = np.fromstring(
        root.find(f".//{ns}Polys/{ns}DataArray[@Name='connectivity']").text,
        sep=" ", dtype=int,
    )
    offs = np.fromstring(
        root.find(f".//{ns}Polys/{ns}DataArray[@Name='offsets']").text,
        sep=" ", dtype=int,
    )
    polys = []
    start = 0
    for end in offs:
        polys.append(conn[start:end])
        start = end
    return pts, polys


def polys_to_triangles(pts: np.ndarray, polys):
    """Convert mixed-degree polygons (quads etc.) to triangles."""
    tris = []
    for poly in polys:
        for i in range(1, len(poly) - 1):
            tris.append([poly[0], poly[i], poly[i + 1]])
    return pts[np.array(tris)]


fig = plt.figure(figsize=(20, 7))
views = [
    ("Vista 3D", (25, -55)),
    ("Vista superior (xy)", (90, -90)),
    ("Vista lateral (xz)", (0, -90)),
]

nerve = trimesh.load_mesh(str(NERVE_STL))
nerve_tris = nerve.vertices[nerve.faces] * 1e3  # mm

patches = {
    "lumen.vtp":             ("crimson",   "lúmen (lateral curva)"),
    "artoph_end_back.vtp":   ("darkorange","artoph_end_back  (z=-30 mm)"),
    "artoph_end_front.vtp":  ("royalblue", "artoph_end_front (z=0 mm)"),
}

for i, (title, view) in enumerate(views, 1):
    ax = fig.add_subplot(1, 3, i, projection="3d")
    # Nerve as semi-transparent gray
    coll = Poly3DCollection(
        nerve_tris, alpha=0.20, facecolor="lightsteelblue", edgecolor="none"
    )
    ax.add_collection3d(coll)
    # Artery patches
    for fname, (color, _label) in patches.items():
        pts, polys = read_vtp(VTK_DIR / fname)
        tris = polys_to_triangles(pts, polys) * 1e3  # mm
        coll = Poly3DCollection(
            tris, alpha=0.85, facecolor=color, edgecolor="black", linewidth=0.03
        )
        ax.add_collection3d(coll)
    ax.set_xlim(-13, 4); ax.set_ylim(-6, 4); ax.set_zlim(-31, 2)
    ax.set_xlabel("x (mm)"); ax.set_ylabel("y (mm)"); ax.set_zlabel("z (mm)")
    ax.view_init(elev=view[0], azim=view[1])
    ax.set_title(title)

# Custom legend
handles = [
    plt.Rectangle((0,0),1,1, color="lightsteelblue", alpha=0.5),
    plt.Rectangle((0,0),1,1, color="crimson"),
    plt.Rectangle((0,0),1,1, color="darkorange"),
    plt.Rectangle((0,0),1,1, color="royalblue"),
]
labels = [
    "nervo óptico (referência, do STL original)",
    "lúmen — pressão pulsátil",
    "artoph_end_back (z=-30 mm, fixedDisplacement)",
    "artoph_end_front (z=0 mm, fixedDisplacement)",
]
fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=10, frameon=False)
fig.suptitle(
    "cases/artoph-curva-mestrado — malha atual no disco (39.490 células, snappyHexMesh)",
    fontsize=13,
)
fig.tight_layout(rect=[0, 0.05, 1, 0.97])
out = REPO / "brunaStuff/current_mesh_solid.png"
fig.savefig(out, dpi=140)
print(f"[write] {out}")
