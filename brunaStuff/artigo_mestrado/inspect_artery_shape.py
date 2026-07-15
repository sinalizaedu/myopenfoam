"""Diagnostico da forma da artéria: 3D + projecoes ortogonais + slice multiplo."""
from __future__ import annotations
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

REPO = Path(__file__).resolve().parents[1]
TRI = REPO / "cases" / "artoph-curva-mestrado" / "solid" / "constant" / "triSurface"
OUT = REPO / "brunaStuff" / "inspect_artery_shape.png"

m = trimesh.load_mesh(str(TRI / "artery_unscaled.stl"))
V = m.vertices * 1e3  # mm

fig = plt.figure(figsize=(15, 10))

# 3D oblique
ax = fig.add_subplot(2, 3, 1, projection="3d")
ax.add_collection3d(
    Poly3DCollection(V[m.faces], facecolor="tab:red", edgecolor="none", alpha=0.4)
)
ax.set_xlim(-12, 5); ax.set_ylim(-6, 4); ax.set_zlim(-1, 32)
ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("z (mm)")
ax.set_title("3D oblique")
ax.view_init(elev=20, azim=-60)

# xz, yz, xy projections (scatter)
ax = fig.add_subplot(2, 3, 2)
ax.scatter(V[:, 0], V[:, 2], s=1, c="tab:red", alpha=0.4)
ax.set_aspect("equal"); ax.set_xlabel("x (mm)"); ax.set_ylabel("z (mm)"); ax.set_title("Vista xz")
ax.grid(alpha=0.3)
ax = fig.add_subplot(2, 3, 3)
ax.scatter(V[:, 1], V[:, 2], s=1, c="tab:red", alpha=0.4)
ax.set_aspect("equal"); ax.set_xlabel("y (mm)"); ax.set_ylabel("z (mm)"); ax.set_title("Vista yz")
ax.grid(alpha=0.3)
ax = fig.add_subplot(2, 3, 4)
ax.scatter(V[:, 0], V[:, 1], s=1, c="tab:red", alpha=0.4)
ax.set_aspect("equal"); ax.set_xlabel("x (mm)"); ax.set_ylabel("y (mm)"); ax.set_title("Vista xy (planta)")
# Add nerve circle
theta = np.linspace(0, 2*np.pi, 64)
ax.plot(1.5*np.cos(theta), 1.5*np.sin(theta), "b-", lw=1, label="ON r=1.5mm")
ax.legend(); ax.grid(alpha=0.3)

# Slices: how many polygons at each z?
ax = fig.add_subplot(2, 3, 5)
zs = np.linspace(m.bounds[0,2] + 1e-5, m.bounds[1,2] - 1e-5, 200)
n_polys = []
for z in zs:
    sec = m.section(plane_origin=[0,0,z], plane_normal=[0,0,1])
    if sec is None:
        n_polys.append(0); continue
    try:
        planar, _ = sec.to_planar()
        n_polys.append(len(list(planar.polygons_full)))
    except Exception:
        n_polys.append(-1)
ax.plot(zs*1e3, n_polys, "k-")
ax.set_xlabel("z (mm)"); ax.set_ylabel("# poligonos na fatia")
ax.set_title("Topologia da fatia por z")
ax.grid(alpha=0.3)

# All slice polygons projected onto xy plane
ax = fig.add_subplot(2, 3, 6)
n_z_show = 30
zs_show = np.linspace(m.bounds[0,2]+1e-4, m.bounds[1,2]-1e-4, n_z_show)
colors = plt.cm.viridis(np.linspace(0, 1, n_z_show))
for z, col in zip(zs_show, colors):
    sec = m.section(plane_origin=[0,0,z], plane_normal=[0,0,1])
    if sec is None: continue
    try:
        planar, _ = sec.to_planar()
        for poly in planar.polygons_full:
            xs, ys = poly.exterior.xy
            ax.plot(np.array(xs)*1e3, np.array(ys)*1e3, c=col, lw=0.8, alpha=0.7)
    except Exception:
        pass
ax.plot(1.5*np.cos(theta), 1.5*np.sin(theta), "b-", lw=1.5, label="ON r=1.5mm")
ax.set_aspect("equal"); ax.set_xlabel("x (mm)"); ax.set_ylabel("y (mm)")
ax.set_title("Todas as fatias z em xy (cor=z)")
ax.legend(); ax.grid(alpha=0.3)

fig.tight_layout()
fig.savefig(OUT, dpi=140)
print(f"[write] {OUT.relative_to(REPO)}")
