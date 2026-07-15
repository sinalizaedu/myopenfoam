"""Shrinks the ophthalmic artery (artery.stl) proportionally (uniform xyz)
about its own mass centroid by a factor s ∈ (0, 1] chosen so that the
artery surface just touches the optic nerve cylinder (axis = z-axis,
radius R_NERVE_MM = 1.5 mm) with a small clearance CLEARANCE_MM.

Method:
  For each vertex V of the artery, look for the scale s_V such that the
  scaled vertex V' = C + s_V*(V - C) lies exactly on the cylinder
  x² + y² = (R_nerve + clearance)².  This is a quadratic in s_V:
        |C_xy + s·(V_xy - C_xy)|² = R²
  We take the smallest positive root per vertex, and the global s is the
  minimum over all vertices.  Choosing this s, the closest vertex sits
  tangent to the nerve wall and no vertex invades it.

A backup STL (artery_unscaled.stl) is written on the first run.
Outputs:
  cases/artoph-curva-mestrado/solid/constant/triSurface/artery.stl   (overwritten)
  cases/artoph-curva-mestrado/solid/constant/triSurface/_artery_scaled_summary.json
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import trimesh

REPO = Path(__file__).resolve().parents[1]
TRI = REPO / "cases" / "artoph-curva-mestrado" / "solid" / "constant" / "triSurface"
ARTERY_STL = TRI / "artery.stl"

R_NERVE_MM = 1.5
CLEARANCE_MM = 0.05
SAVE_BACKUP = True


def write_named_stl(mesh: trimesh.Trimesh, path: Path, solid_name: str) -> None:
    """Write ASCII STL with explicit solid name (snappyHexMesh requires it)."""
    with path.open("w") as f:
        f.write(f"solid {solid_name}\n")
        for face_normal, face_vertices in zip(mesh.face_normals, mesh.triangles):
            f.write(
                f"  facet normal {face_normal[0]:.6e} {face_normal[1]:.6e} {face_normal[2]:.6e}\n"
            )
            f.write("    outer loop\n")
            for v in face_vertices:
                f.write(f"      vertex {v[0]:.6e} {v[1]:.6e} {v[2]:.6e}\n")
            f.write("    endloop\n")
            f.write("  endfacet\n")
        f.write(f"endsolid {solid_name}\n")


def smallest_positive_root_per_vertex(
    verts: np.ndarray, c: np.ndarray, R: float
) -> np.ndarray:
    """For each vertex V, solve |C_xy + s(V_xy - C_xy)|² = R² for s>0."""
    Cx, Cy = c[0], c[1]
    a = verts[:, 0] - Cx
    b = verts[:, 1] - Cy

    A = a * a + b * b
    B = 2.0 * (Cx * a + Cy * b)
    K = Cx * Cx + Cy * Cy - R * R

    disc = B * B - 4.0 * A * K
    valid = (disc >= 0) & (A > 1e-30)
    sq = np.sqrt(np.maximum(disc, 0.0))

    s1 = np.where(valid, (-B - sq) / (2.0 * A), np.inf)
    s2 = np.where(valid, (-B + sq) / (2.0 * A), np.inf)

    s1p = np.where(s1 > 0, s1, np.inf)
    s2p = np.where(s2 > 0, s2, np.inf)
    return np.minimum(s1p, s2p)


artery = trimesh.load_mesh(str(ARTERY_STL))
print(f"[load] {ARTERY_STL.relative_to(REPO)}")
print(f"  vertices: {len(artery.vertices)}  triangles: {len(artery.faces)}")
print(
    f"  bounds (mm): x[{artery.bounds[0,0]*1e3:7.2f},{artery.bounds[1,0]*1e3:7.2f}] "
    f"y[{artery.bounds[0,1]*1e3:7.2f},{artery.bounds[1,1]*1e3:7.2f}] "
    f"z[{artery.bounds[0,2]*1e3:7.2f},{artery.bounds[1,2]*1e3:7.2f}]"
)

C = artery.center_mass
print(
    f"\n[centroid] ({C[0]*1e3:.3f}, {C[1]*1e3:.3f}, {C[2]*1e3:.3f}) mm  "
    f"|C_xy| = {np.hypot(C[0], C[1])*1e3:.3f} mm"
)
assert np.hypot(C[0], C[1]) > R_NERVE_MM * 1e-3, "centroid is inside the nerve"

d0 = np.hypot(artery.vertices[:, 0], artery.vertices[:, 1]).min()
print(
    f"\n[before] min(d_xy) = {d0*1e3:.3f} mm  "
    f"(invades nerve = {d0*1e3 < R_NERVE_MM})"
)

R_tangent_m = R_NERVE_MM * 1e-3
R_target_m = (R_NERVE_MM + CLEARANCE_MM) * 1e-3
s_tangent = float(smallest_positive_root_per_vertex(artery.vertices, C, R_tangent_m).min())
s_target = float(smallest_positive_root_per_vertex(artery.vertices, C, R_target_m).min())
print(f"\n[scale]   s for exact tangent (R={R_NERVE_MM} mm)  : {s_tangent:.4f}")
print(f"          s with {CLEARANCE_MM*1000:.0f} µm clearance ({R_NERVE_MM+CLEARANCE_MM} mm) : {s_target:.4f}")

artery_scaled = artery.copy()
artery_scaled.vertices = C + s_target * (artery.vertices - C)

nb = artery_scaled.bounds
new_d = np.hypot(artery_scaled.vertices[:, 0], artery_scaled.vertices[:, 1]).min()
print(
    f"\n[after]  bounds (mm) x[{nb[0,0]*1e3:7.2f},{nb[1,0]*1e3:7.2f}] "
    f"y[{nb[0,1]*1e3:7.2f},{nb[1,1]*1e3:7.2f}] "
    f"z[{nb[0,2]*1e3:7.2f},{nb[1,2]*1e3:7.2f}]"
)
print(f"          min(d_xy) = {new_d*1e3:.4f} mm  (target {R_NERVE_MM+CLEARANCE_MM} mm)")

if SAVE_BACKUP and not (TRI / "artery_unscaled.stl").exists():
    write_named_stl(artery, TRI / "artery_unscaled.stl", "artery_surface")
    print(f"\n[backup] {(TRI / 'artery_unscaled.stl').relative_to(REPO)}")

write_named_stl(artery_scaled, ARTERY_STL, "artery_surface")
print(f"[write]  {ARTERY_STL.relative_to(REPO)} (overwritten)")

# Recompute locationInMesh: pick a point in the band near the centroid in z
# but laterally to the left, then ensure it lies strictly inside the closed mesh.
z_min, z_max = nb[0, 2], nb[1, 2]
z_mid = (z_min + z_max) / 2.0
band = (artery_scaled.vertices[:, 2] > z_mid - 2e-3) & (
    artery_scaled.vertices[:, 2] < z_mid + 2e-3
)
cands = artery_scaled.vertices[band] if band.any() else artery_scaled.vertices
leftmost = cands[np.argmin(cands[:, 0])]
loc = leftmost + np.array([0.4e-3, 0.0, 0.0])

if not artery_scaled.contains([loc])[0]:
    for zc in np.linspace(z_min + 2e-3, z_max - 2e-3, 30):
        for xc in np.linspace(nb[0, 0], nb[1, 0], 25):
            for yc in np.linspace(nb[0, 1], nb[1, 1], 15):
                p = np.array([xc, yc, zc])
                if artery_scaled.contains([p])[0]:
                    loc = p
                    break
            else:
                continue
            break
        else:
            continue
        break

print(
    f"\n[locationInMesh] ({loc[0]*1e3:.3f}, {loc[1]*1e3:.3f}, {loc[2]*1e3:.3f}) mm  "
    f"inside={artery_scaled.contains([loc])[0]}"
)
print(f"  raw m:  ({loc[0]:.6e}, {loc[1]:.6e}, {loc[2]:.6e})")

summary = {
    "operation": "shrunk artery proportionally about its mass centroid",
    "R_nerve_mm": R_NERVE_MM,
    "clearance_mm": CLEARANCE_MM,
    "centroid_mm": (C * 1e3).tolist(),
    "scale_factor_tangent": s_tangent,
    "scale_factor_applied": s_target,
    "min_xy_distance_after_mm": float(new_d * 1e3),
    "bounds_after_mm": (nb * 1e3).tolist(),
    "locationInMesh_m": loc.tolist(),
}
(TRI / "_artery_scaled_summary.json").write_text(json.dumps(summary, indent=2))
print(f"\n[write] {(TRI / '_artery_scaled_summary.json').relative_to(REPO)}")
