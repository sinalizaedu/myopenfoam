"""Orthogonal projections of the geometry to check for hidden concentric parts."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh

PARTS_DIR = Path(__file__).parent / "geom_mestrado_parts"

nerve = trimesh.load_mesh(str(PARTS_DIR / "part_00.stl"))
artery = trimesh.load_mesh(str(PARTS_DIR / "part_01.stl"))

fig, axes = plt.subplots(1, 3, figsize=(20, 7))

ax = axes[0]
ax.triplot(artery.vertices[:, 0], artery.vertices[:, 1], artery.faces, color="crimson", lw=0.15)
ax.triplot(nerve.vertices[:, 0], nerve.vertices[:, 1], nerve.faces, color="steelblue", lw=0.15)
ax.set_xlabel("x (mm)"); ax.set_ylabel("y (mm)"); ax.set_title("Vista superior (xy)")
ax.axhline(0, color="gray", lw=0.4); ax.axvline(0, color="gray", lw=0.4)
ax.set_aspect("equal"); ax.grid(alpha=0.3)

ax = axes[1]
ax.triplot(artery.vertices[:, 0], artery.vertices[:, 2], artery.faces, color="crimson", lw=0.15)
ax.triplot(nerve.vertices[:, 0], nerve.vertices[:, 2], nerve.faces, color="steelblue", lw=0.15)
ax.set_xlabel("x (mm)"); ax.set_ylabel("z (mm) axial"); ax.set_title("Vista lateral (xz)")
ax.axhline(0, color="gray", lw=0.4); ax.axvline(0, color="gray", lw=0.4)
ax.set_aspect("equal"); ax.grid(alpha=0.3)

ax = axes[2]
ax.triplot(artery.vertices[:, 1], artery.vertices[:, 2], artery.faces, color="crimson", lw=0.15)
ax.triplot(nerve.vertices[:, 1], nerve.vertices[:, 2], nerve.faces, color="steelblue", lw=0.15)
ax.set_xlabel("y (mm)"); ax.set_ylabel("z (mm) axial"); ax.set_title("Vista lateral (yz)")
ax.axhline(0, color="gray", lw=0.4); ax.axvline(0, color="gray", lw=0.4)
ax.set_aspect("equal"); ax.grid(alpha=0.3)

fig.suptitle("Projeções ortogonais — azul=part_00 (nervo), vermelho=part_01 (artéria)", fontsize=13)
fig.tight_layout()
out = PARTS_DIR / "geom_ortho.png"
fig.savefig(out, dpi=150)
print(f"[write] {out}")
