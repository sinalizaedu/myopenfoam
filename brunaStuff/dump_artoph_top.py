"""Sweep z near 0 to find where the lateral extension of part_01 lives."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import trimesh

PARTS_DIR = Path(__file__).parent / "geom_mestrado_parts"
mesh = trimesh.load_mesh(str(PARTS_DIR / "part_01.stl"))

print("Sweep along z (high resolution near z=0 and z=-30):\n")
for z in list(np.arange(-30.0, -28.0, 0.2)) + list(np.arange(-2.0, 0.6, 0.1)):
    section = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if section is None:
        print(f"  z={z:+6.2f}  (no section)")
        continue
    planar, _ = section.to_planar()
    polys = list(planar.polygons_full)
    if not polys:
        print(f"  z={z:+6.2f}  (no polygons)")
        continue
    n = len(polys)
    total_area = sum(p.area for p in polys)
    x_min = min(p.bounds[0] for p in polys)
    x_max = max(p.bounds[2] for p in polys)
    y_min = min(p.bounds[1] for p in polys)
    y_max = max(p.bounds[3] for p in polys)
    print(
        f"  z={z:+6.2f}  npoly={n}  A={total_area:6.2f}  "
        f"bbox=({x_min:+6.2f},{y_min:+6.2f})→({x_max:+6.2f},{y_max:+6.2f})"
    )
