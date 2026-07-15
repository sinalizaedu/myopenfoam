#!/usr/bin/env python3
"""Comparacao entre as 3 STLs disponiveis em ao-mestrado e o ponto P_contact:

  - artery_unscaled.stl       (artery original, sem escala, sem translacao)
  - artery_outer.stl.pre_p_contact.stl  (apos escala 1.3x, antes da translacao)
  - artery_outer.stl          (apos escala 1.3x e translacao para P_contact)

Para cada uma reporta:
  - bounds em mm
  - distancia minima ao eixo z em z in [0, 30]
  - distancia 3D minima ao ponto P_contact
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
TRI = REPO / "cases" / "ao-mestrado" / "constant" / "triSurface"

P_CONTACT_MM = np.array([0.0, 2.5, 18.5])
R_ON_MM = 1.5
R_ONS_MM = 2.5
Z0_MM, Z1_MM = 0.0, 30.0


def read_stl_vertices_unique(path: Path) -> np.ndarray:
    verts: list[tuple[float, float, float]] = []
    seen: set[tuple[float, float, float]] = set()
    with path.open() as f:
        for line in f:
            ls = line.strip()
            if ls.startswith("vertex"):
                p = ls.split()
                key = (round(float(p[1]), 9), round(float(p[2]), 9), round(float(p[3]), 9))
                if key not in seen:
                    seen.add(key)
                    verts.append(key)
    return np.array(verts, dtype=np.float64)


targets = [
    ("artery_unscaled.stl", "raw original"),
    ("artery_outer.stl.pre_p_contact.stl", "apos escala 1.3x, antes translacao"),
    ("artery_outer.stl", "apos escala 1.3x + translacao (atual)"),
    ("artery.stl.pre_p_contact.stl", "artery.stl antes translacao"),
    ("artery.stl", "artery.stl atual"),
]


for name, label in targets:
    p = TRI / name
    if not p.exists():
        print(f"[skip] {name}  -- nao existe")
        continue
    V_m = read_stl_vertices_unique(p)
    V = V_m * 1e3  # m -> mm
    n = len(V)
    bx, by, bz = V[:, 0], V[:, 1], V[:, 2]

    # banda z in [0, 30]
    mask = (V[:, 2] >= Z0_MM) & (V[:, 2] <= Z1_MM)
    Vb = V[mask]

    # distancia 3D minima ao ponto P_contact
    d3d = np.linalg.norm(V - P_CONTACT_MM, axis=1)
    i_p = int(np.argmin(d3d))

    # closest to z-axis em banda
    if len(Vb) > 0:
        rxy = np.hypot(Vb[:, 0], Vb[:, 1])
        i_a = int(np.argmin(rxy))
        rxy_min = float(rxy[i_a])
        v_a = Vb[i_a]
    else:
        rxy_min = float("nan"); v_a = np.zeros(3)

    print(f"\n=== {name}  ({label}) ===")
    print(f"  vertices unicos               : {n}")
    print(f"  bounds (mm)  x[{bx.min():+.3f}, {bx.max():+.3f}]  "
          f"y[{by.min():+.3f}, {by.max():+.3f}]  z[{bz.min():+.3f}, {bz.max():+.3f}]")
    print(f"  vertices em z in [0, 30] mm   : {len(Vb)}")
    print(f"  min |V - P_contact|           : {d3d[i_p]*1000:.1f} um   "
          f"em ({V[i_p,0]:+.3f}, {V[i_p,1]:+.3f}, {V[i_p,2]:+.3f}) mm")
    print(f"  min r_xy em z[0,30]           : {rxy_min:.4f} mm   "
          f"em ({v_a[0]:+.3f}, {v_a[1]:+.3f}, {v_a[2]:+.3f}) mm")
