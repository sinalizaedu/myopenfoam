"""Render the current snappyHexMesh state of artoph-curva-mestrado.

Reads the boundary patches exported by foamToVTK to confirm visually that
the mesh that's on disk is the curved geometry (not the straight tube the
user reports seeing in ParaView). Output: brunaStuff/current_mesh_views.png
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parents[1]
VTK_DIR = REPO / "cases/artoph-curva-mestrado/solid/VTK/solid_0/boundary"


def read_vtp_points(vtp_path: Path) -> np.ndarray:
    """Parse the <Points><DataArray> block from an ASCII VTP file."""
    tree = ET.parse(vtp_path)
    root = tree.getroot()
    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0] + "}"
    points_elem = root.find(f".//{ns}Points/{ns}DataArray")
    text = points_elem.text or ""
    nums = np.fromstring(text, sep=" ", dtype=float)
    return nums.reshape(-1, 3)


parts = {
    "lumen (superfície lateral curva)": (VTK_DIR / "lumen.vtp", "crimson"),
    "artoph_end_back (z = -30 mm)":     (VTK_DIR / "artoph_end_back.vtp", "darkorange"),
    "artoph_end_front (z = 0 mm)":      (VTK_DIR / "artoph_end_front.vtp", "royalblue"),
}

fig, axes = plt.subplots(1, 3, figsize=(20, 7))
all_pts = []
for name, (vtp, color) in parts.items():
    pts = read_vtp_points(vtp)
    pts_mm = pts * 1e3
    all_pts.append(pts_mm)
    axes[0].scatter(pts_mm[:, 0], pts_mm[:, 1], s=0.4, color=color, alpha=0.5, label=name)
    axes[1].scatter(pts_mm[:, 0], pts_mm[:, 2], s=0.4, color=color, alpha=0.5, label=name)
    axes[2].scatter(pts_mm[:, 1], pts_mm[:, 2], s=0.4, color=color, alpha=0.5, label=name)
    print(f"  {name}: {len(pts_mm)} points, "
          f"bbox x=[{pts_mm[:,0].min():.2f},{pts_mm[:,0].max():.2f}], "
          f"z=[{pts_mm[:,2].min():.2f},{pts_mm[:,2].max():.2f}]")

axes[0].set_title("Vista superior (xy)")
axes[0].set_xlabel("x (mm)"); axes[0].set_ylabel("y (mm)")
axes[1].set_title("Vista lateral (xz)")
axes[1].set_xlabel("x (mm)"); axes[1].set_ylabel("z (mm)")
axes[2].set_title("Vista lateral (yz)")
axes[2].set_xlabel("y (mm)"); axes[2].set_ylabel("z (mm)")
for ax in axes:
    ax.set_aspect("equal"); ax.grid(alpha=0.3)
    ax.axhline(0, color="gray", lw=0.4); ax.axvline(0, color="gray", lw=0.4)
axes[0].legend(loc="lower left", fontsize=9, markerscale=8)

fig.suptitle(
    "cases/artoph-curva-mestrado/solid — malha atual no disco "
    f"(39.490 células, geração via snappyHexMesh)",
    fontsize=12,
)
fig.tight_layout()
out = REPO / "brunaStuff/current_mesh_views.png"
fig.savefig(out, dpi=140)
print(f"\n[write] {out}")
