#!/usr/bin/env python3
"""
Find the point on the artery outer surface closest to the optic-nerve reference
cylinder (geometric only — no NO mesh).

Cylinder: axis z through origin, radius R_nerve_m, axial z in [z0, z1].

Writes cases/artoph-fsi-curva-mestrado/constant/closest_to_ON_ref.json with
coordinates for preCICE watch-point and OpenFOAM probes.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def _cases_root() -> Path:
    p = Path(__file__).resolve()
    if p.parent.name == "scripts":
        return p.parents[2]
    return p.parents[1] / "cases"


CASES = _cases_root()
_CASE_CANDIDATES = ["ao-mestrado", "artoph-fsi-curva-mestrado"]
_CASE_NAME = next((n for n in _CASE_CANDIDATES if (CASES / n).is_dir()),
                  _CASE_CANDIDATES[0])
OUTER = CASES / _CASE_NAME / "constant" / "triSurface" / "artery_outer.stl"
OUT_JSON = CASES / _CASE_NAME / "constant" / "closest_to_ON_ref.json"

# Same convention as artoph solid scripts (nerve axis = z, R = 1.5 mm ONS ref)
R_NERVE_M = 1.5e-3
Z0_M = 0.0
Z1_M = 0.03


def read_vertices_ascii_stl(path: Path) -> np.ndarray:
    verts: list[list[float]] = []
    with path.open() as f:
        for line in f:
            if line.lstrip().startswith("vertex"):
                p = line.split()
                verts.append([float(p[1]), float(p[2]), float(p[3])])
    return np.array(verts, dtype=np.float64)


def dist_to_cylinder_side(xy: np.ndarray, z: np.ndarray) -> np.ndarray:
    r = np.hypot(xy[:, 0], xy[:, 1])
    dr = np.abs(r - R_NERVE_M)
    # penalize z outside [Z0, Z1]
    lo = np.maximum(Z0_M - z, 0.0)
    hi = np.maximum(z - Z1_M, 0.0)
    dz = np.hypot(lo, hi)
    return np.hypot(dr, dz)


def main() -> None:
    if not OUTER.is_file():
        raise SystemExit(f"Run build_artoph_hollow_stls.py first. Missing {OUTER}")
    V = read_vertices_ascii_stl(OUTER)
    d = dist_to_cylinder_side(V[:, :2], V[:, 2])
    i = int(np.argmin(d))
    p = V[i].tolist()
    precice_coord = f"{p[0]};{p[1]};{p[2]}"

    doc = {
        "description": "Closest vertex on artery_outer to z-axis cylinder R (ONS ref), z clipped",
        "R_nerve_m": R_NERVE_M,
        "z_range_m": [Z0_M, Z1_M],
        "closest_vertex_index": i,
        "closest_point_m": p,
        "min_distance_m": float(d[i]),
        "precice_watchpoint_coordinate": precice_coord,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(doc, indent=2))
    print(f"[ok] wrote {OUT_JSON.relative_to(CASES)}")
    print(f"     min distance to cylinder ref = {d[i]*1e3:.4f} mm at ({p[0]*1e3:.3f}, {p[1]*1e3:.3f}, {p[2]*1e3:.3f}) mm")


if __name__ == "__main__":
    main()
