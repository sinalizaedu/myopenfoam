#!/usr/bin/env python3
"""Visualizacao 3D da nova polyMesh tubular extrudada.
Plota a centerline + secoes transversais do lumen (azul) e do annulus (vermelho).
"""
import os
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "brunaStuff"))

from build_artoph_tubular_meshes import (
    _find_src_stl, read_ascii_stl_vertices,
    extract_centerline_marching, smooth_centerline, parallel_transport_frames,
    R_LUMEN_M, H_WALL_M, NCIRC, NRAD_LUMEN, NRAD_WALL, NZ,
)

OUT_PNG = REPO / "brunaStuff" / "inspect_artoph_tubular_mesh.png"

print(f"Lendo STL e extraindo centerline ({NZ} secoes)...")
pts = read_ascii_stl_vertices(_find_src_stl())
cl_raw = extract_centerline_marching(pts, r_search_m=1.5e-3, n_seeds=100, n_iter=8)
cl = smooth_centerline(cl_raw, nz_out=NZ)
T, N, B = parallel_transport_frames(cl)

print("Gerando secoes amostradas (a cada 16 secoes)...")
thetas = np.linspace(0, 2 * np.pi, 32, endpoint=False)

fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(111, projection="3d")

ax.plot(cl[:, 0] * 1e3, cl[:, 1] * 1e3, cl[:, 2] * 1e3,
        color="black", lw=2, label="centerline")

for iz in range(0, NZ, 16):
    c = cl[iz]
    # lumen externo (R_LUMEN_M)
    lum = np.array([
        c + R_LUMEN_M * np.cos(th) * N[iz] + R_LUMEN_M * np.sin(th) * B[iz]
        for th in thetas
    ])
    lum = np.vstack([lum, lum[0:1]])
    ax.plot(lum[:, 0] * 1e3, lum[:, 1] * 1e3, lum[:, 2] * 1e3,
            color="C0", alpha=0.55, lw=0.8)
    # annulus externo (R_LUMEN_M + H_WALL_M)
    R_out = R_LUMEN_M + H_WALL_M
    ann = np.array([
        c + R_out * np.cos(th) * N[iz] + R_out * np.sin(th) * B[iz]
        for th in thetas
    ])
    ann = np.vstack([ann, ann[0:1]])
    ax.plot(ann[:, 0] * 1e3, ann[:, 1] * 1e3, ann[:, 2] * 1e3,
            color="C3", alpha=0.45, lw=0.8)

# Caps
for iz in [0, NZ - 1]:
    c = cl[iz]
    R_out = R_LUMEN_M + H_WALL_M
    ann = np.array([
        c + R_out * np.cos(th) * N[iz] + R_out * np.sin(th) * B[iz]
        for th in thetas
    ])
    ann = np.vstack([ann, ann[0:1]])
    ax.plot(ann[:, 0] * 1e3, ann[:, 1] * 1e3, ann[:, 2] * 1e3,
            color="C3", lw=2.5)

ax.set_xlabel("x [mm]")
ax.set_ylabel("y [mm]")
ax.set_zlabel("z [mm]")
ax.set_title(f"polyMesh tubular extrudada\nLumen R={R_LUMEN_M*1e3:.2f} mm (azul) | "
             f"Annulus R_in={R_LUMEN_M*1e3:.2f} → R_out={(R_LUMEN_M+H_WALL_M)*1e3:.2f} mm (vermelho) | "
             f"L_arc ≈ {np.sum(np.linalg.norm(np.diff(cl, axis=0), axis=1))*1e3:.1f} mm")
ax.legend(loc="upper left")
ax.view_init(elev=18, azim=-70)

# Equal aspect
all_coords = np.vstack([cl, cl + 1.5e-3, cl - 1.5e-3])
ranges = (all_coords.max(axis=0) - all_coords.min(axis=0)) * 1e3
max_range = ranges.max() / 2.0
mid = (all_coords.max(axis=0) + all_coords.min(axis=0)) / 2.0 * 1e3
ax.set_xlim(mid[0] - max_range, mid[0] + max_range)
ax.set_ylim(mid[1] - max_range, mid[1] + max_range)
ax.set_zlim(mid[2] - max_range, mid[2] + max_range)

plt.tight_layout()
plt.savefig(OUT_PNG, dpi=130, bbox_inches="tight")
print(f"Salvo em: {OUT_PNG}")
