"""Shrinks the ophthalmic artery by scaling ONLY its centerline (medial axis)
about the centerline's mass centroid, while preserving the local tube radius
(per-vertex radial offset to the centerline is kept constant).

Algorithm:
  1. Restore artery.stl from artery_unscaled.stl.
  2. Slice the artery STL by ~200 planes perpendicular to z to extract
     a discrete centerline:  P(z) = (cx(z), cy(z), z) and local radius r(z).
  3. For each artery vertex V, find the centerline point P_V at the same z
     (linear interpolation), and compute the radial offset dV = V - P_V.
  4. Apply uniform xyz scaling to the centerline curve about its mass centroid
     C̄:  P_new = C̄ + s*(P - C̄). Build new vertices V_new = P_V_new + dV.
  5. Binary-search s ∈ (0, 1] such that for every vertex V_new,
     sqrt(V_new_x² + V_new_y²) >= R_NERVE_MM + CLEARANCE_MM.

Outputs:
  cases/artoph-curva-mestrado/solid/constant/triSurface/artery.stl  (overwritten)
  cases/artoph-curva-mestrado/solid/constant/triSurface/_artery_scaled_summary.json
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
import trimesh

REPO = Path(__file__).resolve().parents[1]
TRI = REPO / "cases" / "artoph-curva-mestrado" / "solid" / "constant" / "triSurface"
ARTERY_STL = TRI / "artery.stl"
ARTERY_BACKUP = TRI / "artery_unscaled.stl"

R_NERVE_MM = 1.5
CLEARANCE_MM = 0.05
N_SLICES = 250


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


def extract_centerline(mesh: trimesh.Trimesh, n: int = N_SLICES):
    """Slice the mesh perpendicular to z, return centerline points and per-z radii.

    Returns:
        z_arr  : (M,) z-coordinates of slices (sorted)
        cxy    : (M, 2) (cx, cy) per slice (mass-weighted by polygon area for safety)
        radius : (M,)  effective radius of section (sqrt(area/pi))
    """
    z_min, z_max = mesh.bounds[:, 2]
    zs = np.linspace(z_min + 1e-5, z_max - 1e-5, n)
    z_out = []
    cxy = []
    rad = []
    for z in zs:
        section = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        if section is None:
            continue
        try:
            planar, _ = section.to_planar()
        except Exception:
            continue
        polys = list(planar.polygons_full)
        if not polys:
            continue
        # Aggregate all polygons at this z (area-weighted centroid).
        areas = np.array([p.area for p in polys])
        if areas.sum() <= 0:
            continue
        cx = sum(p.centroid.x * p.area for p in polys) / areas.sum()
        cy = sum(p.centroid.y * p.area for p in polys) / areas.sum()
        r_eq = np.sqrt(areas.sum() / np.pi)
        z_out.append(z)
        cxy.append([cx, cy])
        rad.append(r_eq)
    return np.array(z_out), np.array(cxy), np.array(rad)


def centerline_at_z(z_arr, cxy, z_query):
    """Linear-interpolate centerline xy at z_query (clamped at endpoints)."""
    zq = np.clip(z_query, z_arr[0], z_arr[-1])
    cx = np.interp(zq, z_arr, cxy[:, 0])
    cy = np.interp(zq, z_arr, cxy[:, 1])
    return np.stack([cx, cy, zq], axis=-1)


def build_scaled_vertices(verts, centerline_points, c_bar, s):
    """Given the per-vertex centerline point P_V and the centroid C̄, apply
    scaling P_new = C̄ + s*(P - C̄) and keep dV = V - P_V.
    """
    P_new = c_bar + s * (centerline_points - c_bar)
    dV = verts - centerline_points
    return P_new + dV


def min_xy_distance_to_axis(verts):
    return float(np.hypot(verts[:, 0], verts[:, 1]).min())


shutil.copyfile(ARTERY_BACKUP, ARTERY_STL)
artery = trimesh.load_mesh(str(ARTERY_STL))
print(f"[restored & loaded] {ARTERY_STL.relative_to(REPO)}")
print(f"  vertices: {len(artery.vertices)}  triangles: {len(artery.faces)}")
print(
    f"  bounds (mm): x[{artery.bounds[0,0]*1e3:7.2f},{artery.bounds[1,0]*1e3:7.2f}] "
    f"y[{artery.bounds[0,1]*1e3:7.2f},{artery.bounds[1,1]*1e3:7.2f}] "
    f"z[{artery.bounds[0,2]*1e3:7.2f},{artery.bounds[1,2]*1e3:7.2f}]"
)

print("\n[centerline] slicing perpendicular to z…")
z_arr, cxy, rad = extract_centerline(artery, n=N_SLICES)
print(f"  {len(z_arr)} valid slices")
print(
    f"  cx (mm):  [{cxy[:,0].min()*1e3:7.3f}, {cxy[:,0].max()*1e3:7.3f}]   "
    f"cy (mm):  [{cxy[:,1].min()*1e3:7.3f}, {cxy[:,1].max()*1e3:7.3f}]"
)
print(f"  r  (mm):  [{rad.min()*1e3:.3f}, {rad.max()*1e3:.3f}]  mean = {rad.mean()*1e3:.3f}")

# Centerline centroid (uniform along arc length is fine; we use point mean)
c_bar = np.array([cxy[:, 0].mean(), cxy[:, 1].mean(), z_arr.mean()])
print(
    f"\n[centroid C̄]  ({c_bar[0]*1e3:.3f}, {c_bar[1]*1e3:.3f}, {c_bar[2]*1e3:.3f}) mm  "
    f"|C̄_xy| = {np.hypot(c_bar[0], c_bar[1])*1e3:.3f} mm"
)

# Each vertex's centerline-point (sampled at the vertex's z)
P_V = centerline_at_z(z_arr, cxy, artery.vertices[:, 2])
dV_norms = np.linalg.norm(artery.vertices - P_V, axis=1)
print(
    f"\n[per-vertex radial offset dV]  mean = {dV_norms.mean()*1e3:.3f} mm   "
    f"max = {dV_norms.max()*1e3:.3f} mm   "
    f"min = {dV_norms.min()*1e3:.3f} mm"
)

d0 = min_xy_distance_to_axis(artery.vertices)
print(
    f"\n[before] min(d_xy of artery surface) = {d0*1e3:.3f} mm  "
    f"(invades nerve = {d0*1e3 < R_NERVE_MM})"
)

# Binary search on s ∈ (0, 1].  Predicate: min_xy_distance(V_new) >= target.
target_m = (R_NERVE_MM + CLEARANCE_MM) * 1e-3
lo, hi = 0.0, 1.0
# First verify: at s=0 (everything collapses to centerline centroid), distance >= target?
V_at_zero = build_scaled_vertices(artery.vertices, P_V, c_bar, 0.0)
d_at_zero = min_xy_distance_to_axis(V_at_zero)
if d_at_zero < target_m:
    print(
        f"\n[!!!] Even at s=0 the offsets dV reach within {d_at_zero*1e3:.3f} mm "
        "of the nerve axis. Cannot achieve subtle touch by centerline scaling alone "
        "(centerline centroid + tube radius is already too close)."
    )
    print("    Fallback: keeping s=0 → all centerline points collapse to C̄.")
    s_best = 0.0
else:
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        V_mid = build_scaled_vertices(artery.vertices, P_V, c_bar, mid)
        if min_xy_distance_to_axis(V_mid) >= target_m:
            lo = mid
        else:
            hi = mid
    s_best = lo
print(f"\n[binary search]   s_best = {s_best:.4f}")

V_new = build_scaled_vertices(artery.vertices, P_V, c_bar, s_best)
new_min = min_xy_distance_to_axis(V_new)
artery_scaled = artery.copy()
artery_scaled.vertices = V_new

nb = artery_scaled.bounds
print(
    f"\n[after]  bounds (mm) x[{nb[0,0]*1e3:7.2f},{nb[1,0]*1e3:7.2f}] "
    f"y[{nb[0,1]*1e3:7.2f},{nb[1,1]*1e3:7.2f}] "
    f"z[{nb[0,2]*1e3:7.2f},{nb[1,2]*1e3:7.2f}]"
)
print(f"          min(d_xy)  = {new_min*1e3:.4f} mm  (target {R_NERVE_MM+CLEARANCE_MM} mm)")

# Sanity check on local radius preservation
dV_new = artery_scaled.vertices - (c_bar + s_best * (P_V - c_bar))
dV_new_norms = np.linalg.norm(dV_new, axis=1)
print(
    f"\n[radius preserved?]  max |dV - dV_new| = "
    f"{np.abs(dV_norms - dV_new_norms).max()*1e9:.1f} pm (essentially zero)"
)

write_named_stl(artery_scaled, ARTERY_STL, "artery_surface")
print(f"\n[write]  {ARTERY_STL.relative_to(REPO)} (overwritten)")

# Recompute locationInMesh inside the new (closed) surface.
artery_scaled.process()
z_min, z_max = nb[0, 2], nb[1, 2]
z_mid = (z_min + z_max) / 2.0
loc = None
for zc in np.linspace(z_min + 1e-3, z_max - 1e-3, 60):
    for xc in np.linspace(nb[0, 0] + 5e-5, nb[1, 0] - 5e-5, 60):
        for yc in np.linspace(nb[0, 1] + 5e-5, nb[1, 1] - 5e-5, 25):
            p = np.array([xc, yc, zc])
            if artery_scaled.contains([p])[0]:
                loc = p
                break
        if loc is not None:
            break
    if loc is not None:
        break

if loc is None:
    raise RuntimeError("Could not find any locationInMesh inside the scaled artery.")

print(
    f"\n[locationInMesh] ({loc[0]*1e3:.3f}, {loc[1]*1e3:.3f}, {loc[2]*1e3:.3f}) mm  "
    f"inside={artery_scaled.contains([loc])[0]}"
)
print(f"  raw m:  ({loc[0]:.6e}, {loc[1]:.6e}, {loc[2]:.6e})")

summary = {
    "operation": "scaled artery centerline about C̄ while preserving local tube radius",
    "R_nerve_mm": R_NERVE_MM,
    "clearance_mm": CLEARANCE_MM,
    "centerline_n_slices": int(len(z_arr)),
    "centerline_centroid_mm": (c_bar * 1e3).tolist(),
    "scale_factor_applied": s_best,
    "min_xy_distance_after_mm": float(new_min * 1e3),
    "tube_radius_mean_mm": float(rad.mean() * 1e3),
    "bounds_after_mm": (nb * 1e3).tolist(),
    "locationInMesh_m": loc.tolist(),
}
(TRI / "_artery_scaled_summary.json").write_text(json.dumps(summary, indent=2))
print(f"\n[write] {(TRI / '_artery_scaled_summary.json').relative_to(REPO)}")
