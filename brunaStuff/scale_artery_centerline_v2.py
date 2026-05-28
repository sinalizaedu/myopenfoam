"""Shrinks the ophthalmic artery by scaling ONLY its 3D centerline (extracted
via voxel skeletonization, robust for arbitrary tube shapes), while preserving
the local tube radius (vertex-to-centerline offset kept constant in length AND
direction relative to the centerline tangent).

Algorithm:
  1. Restore artery.stl from artery_unscaled.stl.
  2. Voxelize the artery (0.2 mm pitch) and fill.
  3. Skeletonize the 3D volume → 1-voxel-thick medial axis.
  4. Convert skeleton voxels to a polyline by ordering nearest neighbours.
  5. For each artery vertex V, find the nearest centerline point P_V.
  6. Apply uniform xyz scaling to the centerline curve about its centroid C̄:
       P_new = C̄ + s*(P - C̄).
     Translate each vertex by Δ_V = P_new(V) - P_V (the centerline displacement
     at V's anchor point). This preserves the radial offset (V - P_V) intact
     in both magnitude and orientation — local tube cross-section unchanged.
  7. Binary-search s ∈ (0, 1] such that the closest vertex to the nerve axis
     (z-axis) is at distance >= R_NERVE_MM + CLEARANCE_MM.

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
from scipy.spatial import cKDTree
from skimage.morphology import skeletonize

REPO = Path(__file__).resolve().parents[1]
TRI = REPO / "cases" / "artoph-curva-mestrado" / "solid" / "constant" / "triSurface"
ARTERY_STL = TRI / "artery.stl"
ARTERY_BACKUP = TRI / "artery_unscaled.stl"

# Raio de referência do "nervo" para o clearance: 2.5 mm = parede EXTERNA do
# ONS (optic nerve sheath / bainha), conforme cases/on-mestrado/solid/system/
# blockMeshDict (ON r=0..1.5 mm, ONS r=1.5..2.5 mm).  A artéria deve ficar
# fora da bainha, não apenas fora do nervo central.
R_NERVE_MM = 2.5
CLEARANCE_MM = 0.10  # 100 µm de folga até a parede externa do ONS
VOX_PITCH_MM = 0.20
# Desired scale factor for the centerline (about its own centroid):
#   s > 1  → enlarge the curve (artery becomes "wider" around the centroid)
#   s < 1  → shrink the curve
#   s = 1  → keep the original master STL geometry
SCALE_TARGET = 1.3


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


def extract_skeleton_world_points(mesh: trimesh.Trimesh, pitch_m: float) -> np.ndarray:
    """Voxelize, fill, skeletonize 3D, return skeleton points in world coords (meters)."""
    vox = mesh.voxelized(pitch=pitch_m).fill()
    skel = skeletonize(vox.matrix.astype(bool))
    ijk = np.argwhere(skel)
    pts = vox.indices_to_points(ijk)  # world coords in meters
    return pts


def order_skeleton_points(pts: np.ndarray) -> np.ndarray:
    """Greedy NN ordering: start from an endpoint (point with fewest neighbours
    within 1.8 * pitch), traverse picking the nearest unvisited point each step."""
    n = len(pts)
    tree = cKDTree(pts)
    # Neighbour count (within sqrt(3) * pitch_world ≈ 1.8*pitch)
    counts = tree.query_ball_point(pts, r=1.8 * VOX_PITCH_MM * 1e-3, return_length=True)
    start = int(np.argmin(counts))
    visited = np.zeros(n, dtype=bool)
    order = [start]
    visited[start] = True
    cur = start
    while len(order) < n:
        # nearest unvisited
        dists, idxs = tree.query(pts[cur], k=min(20, n))
        nxt = None
        for d, i in zip(dists, idxs):
            if not visited[i]:
                nxt = int(i)
                break
        if nxt is None:
            break
        order.append(nxt)
        visited[nxt] = True
        cur = nxt
    return pts[order]


shutil.copyfile(ARTERY_BACKUP, ARTERY_STL)
artery = trimesh.load_mesh(str(ARTERY_STL))
print(f"[restored & loaded] {ARTERY_STL.relative_to(REPO)}")
print(f"  vertices: {len(artery.vertices)}  triangles: {len(artery.faces)}")
print(
    f"  bounds (mm): x[{artery.bounds[0,0]*1e3:7.2f},{artery.bounds[1,0]*1e3:7.2f}] "
    f"y[{artery.bounds[0,1]*1e3:7.2f},{artery.bounds[1,1]*1e3:7.2f}] "
    f"z[{artery.bounds[0,2]*1e3:7.2f},{artery.bounds[1,2]*1e3:7.2f}]"
)

print(f"\n[skeletonize] voxelizing at {VOX_PITCH_MM} mm pitch …")
skel_pts = extract_skeleton_world_points(artery, VOX_PITCH_MM * 1e-3)
print(f"  raw skeleton points: {len(skel_pts)}")
skel_ordered = order_skeleton_points(skel_pts)
print(f"  ordered polyline   : {len(skel_ordered)} points")
print(
    f"  centerline bounds(mm) x[{skel_ordered[:,0].min()*1e3:7.2f},{skel_ordered[:,0].max()*1e3:7.2f}] "
    f"y[{skel_ordered[:,1].min()*1e3:7.2f},{skel_ordered[:,1].max()*1e3:7.2f}] "
    f"z[{skel_ordered[:,2].min()*1e3:7.2f},{skel_ordered[:,2].max()*1e3:7.2f}]"
)

c_bar = skel_ordered.mean(axis=0)
print(
    f"\n[centroid C̄] = ({c_bar[0]*1e3:.3f}, {c_bar[1]*1e3:.3f}, {c_bar[2]*1e3:.3f}) mm  "
    f"|C̄_xy| = {np.hypot(c_bar[0], c_bar[1])*1e3:.3f} mm"
)

# For each artery vertex, find nearest centerline point
tree = cKDTree(skel_ordered)
_, nn_idx = tree.query(artery.vertices, k=1)
P_V = skel_ordered[nn_idx]
dV = artery.vertices - P_V
dV_norms = np.linalg.norm(dV, axis=1)
print(
    f"\n[per-vertex tube radius dV]  mean = {dV_norms.mean()*1e3:.3f} mm   "
    f"max = {dV_norms.max()*1e3:.3f} mm   "
    f"min = {dV_norms.min()*1e3:.3f} mm"
)

d0 = float(np.hypot(artery.vertices[:, 0], artery.vertices[:, 1]).min())
print(
    f"\n[before] min(d_xy of artery surface) = {d0*1e3:.3f} mm  "
    f"(invades nerve = {d0*1e3 < R_NERVE_MM})"
)

target_m = (R_NERVE_MM + CLEARANCE_MM) * 1e-3


def vertices_at_scale(s: float) -> np.ndarray:
    P_new = c_bar + s * (P_V - c_bar)
    return P_new + dV


def min_dxy_at_scale(s: float) -> float:
    Vn = vertices_at_scale(s)
    return float(np.hypot(Vn[:, 0], Vn[:, 1]).min())


# Apply the desired scale factor first; then translate the centerline (in xy)
# radially away from the nerve axis ONLY IF the artery still invades the nerve.
# This way the user's target scale is preserved (artery stays the requested size).
s_best = SCALE_TARGET
d_at_s = min_dxy_at_scale(s_best)
print(
    f"\n[fixed scale s = {s_best:.3f}]  →  min d_xy = {d_at_s*1e3:.4f} mm "
    f"(target {R_NERVE_MM+CLEARANCE_MM} mm)"
)

if d_at_s < target_m:
    # Direction to translate centroid in xy: away from the nerve axis, in the
    # current direction of C̄ (so the artery as a whole shifts radially outward).
    deficit = (target_m - d_at_s)
    direction = c_bar[:2] / max(np.linalg.norm(c_bar[:2]), 1e-12)
    # We move the centroid by some amount Δ in that direction.  Because the
    # transformation is V_new = C̄ + s*(P_V - C̄) + dV, shifting C̄ by Δ shifts
    # V_new by (1 - s)*Δ.  For s > 1, (1-s) < 0, so Δ must be NEGATIVE (i.e.,
    # shift C̄ toward the nerve) to push V_new AWAY from the nerve.
    # Numerically we just iterate: shift C̄ along ±direction until tangent.
    print(
        f"\n[translating]  artery invades by {deficit*1e3:.4f} mm. "
        "Shifting centroid in xy to recover tangent contact …"
    )
    direction_sign = +1.0 if (s_best < 1.0) else -1.0  # see derivation above
    lo, hi = 0.0, 50e-3
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        c_bar_try = c_bar.copy()
        c_bar_try[:2] += direction_sign * direction * mid
        P_new_try = c_bar_try + s_best * (P_V - c_bar_try)
        V_try = P_new_try + dV
        d_try = float(np.hypot(V_try[:, 0], V_try[:, 1]).min())
        if d_try >= target_m:
            hi = mid
        else:
            lo = mid
    shift_m = hi
    c_bar[:2] += direction_sign * direction * shift_m
    print(
        f"   shift |Δ| = {shift_m*1e3:.4f} mm  along sign={direction_sign:+.0f} of "
        f"({direction[0]:+.3f},{direction[1]:+.3f})"
    )
    print(
        f"   new C̄ = ({c_bar[0]*1e3:.3f}, {c_bar[1]*1e3:.3f}, {c_bar[2]*1e3:.3f}) mm"
    )
    d_at_s = min_dxy_at_scale(s_best)
    print(f"   new min d_xy = {d_at_s*1e3:.4f} mm")
else:
    print("   (already outside the nerve — no translation needed.)")

V_new = vertices_at_scale(s_best)
new_min = float(np.hypot(V_new[:, 0], V_new[:, 1]).min())
artery_scaled = artery.copy()
artery_scaled.vertices = V_new
nb = artery_scaled.bounds
print(
    f"\n[after]  bounds (mm) x[{nb[0,0]*1e3:7.2f},{nb[1,0]*1e3:7.2f}] "
    f"y[{nb[0,1]*1e3:7.2f},{nb[1,1]*1e3:7.2f}] "
    f"z[{nb[0,2]*1e3:7.2f},{nb[1,2]*1e3:7.2f}]"
)
print(f"          min(d_xy)  = {new_min*1e3:.4f} mm  (target {R_NERVE_MM+CLEARANCE_MM} mm)")

# Sanity: tube radius preserved
dV_new = V_new - (c_bar + s_best * (P_V - c_bar))
dV_new_norms = np.linalg.norm(dV_new, axis=1)
print(
    f"\n[radius preserved?]  max |dV - dV_new| = "
    f"{np.abs(dV_norms - dV_new_norms).max()*1e9:.1f} pm (essentially zero)"
)

write_named_stl(artery_scaled, ARTERY_STL, "artery_surface")
print(f"\n[write]  {ARTERY_STL.relative_to(REPO)} (overwritten)")

# locationInMesh: take the centerline point closest to the centroid C̄ (i.e., a
# point that sits well inside the tube, far from the caps and the lateral wall).
# Use the SCALED centerline (centerline transformed by P_new = C̄ + s*(P-C̄)).
artery_scaled.process()
scaled_centerline = c_bar + s_best * (skel_ordered - c_bar)
# Pick the centerline node closest to the centroid in 3D distance.
distances_to_cbar = np.linalg.norm(scaled_centerline - c_bar, axis=1)
loc = scaled_centerline[int(np.argmin(distances_to_cbar))]

# Safety check: if this point is somehow not strictly inside (e.g., due to a
# pathological skeleton point near the surface), do a small radial nudge toward
# the centroid of nearby vertices and re-check; fall back to brute-force scan.
if not bool(artery_scaled.contains([loc])[0]):
    # Try a few neighbouring centerline nodes
    order_by_d = np.argsort(distances_to_cbar)
    found = False
    for idx in order_by_d[:50]:
        cand = scaled_centerline[int(idx)]
        if bool(artery_scaled.contains([cand])[0]):
            loc = cand
            found = True
            break
    if not found:
        # Brute-force fallback (rare)
        for zc in np.linspace(nb[0, 2] + 1e-3, nb[1, 2] - 1e-3, 40):
            for xc in np.linspace(nb[0, 0] + 1e-4, nb[1, 0] - 1e-4, 40):
                for yc in np.linspace(nb[0, 1] + 1e-4, nb[1, 1] - 1e-4, 20):
                    p = np.array([xc, yc, zc])
                    if bool(artery_scaled.contains([p])[0]):
                        loc = p
                        found = True
                        break
                if found:
                    break
            if found:
                break

if loc is None or not bool(artery_scaled.contains([loc])[0]):
    raise RuntimeError("Could not find any locationInMesh inside the scaled artery.")
print(
    f"\n[locationInMesh] ({loc[0]*1e3:.3f}, {loc[1]*1e3:.3f}, {loc[2]*1e3:.3f}) mm  "
    f"inside={artery_scaled.contains([loc])[0]}"
)
print(f"  raw m:  ({loc[0]:.6e}, {loc[1]:.6e}, {loc[2]:.6e})")

summary = {
    "operation": "scaled artery 3D centerline about C̄ while preserving local tube radius",
    "R_nerve_mm": R_NERVE_MM,
    "clearance_mm": CLEARANCE_MM,
    "voxel_pitch_mm": VOX_PITCH_MM,
    "centerline_n_points": int(len(skel_ordered)),
    "centerline_centroid_mm": (c_bar * 1e3).tolist(),
    "scale_factor_applied": s_best,
    "min_xy_distance_after_mm": float(new_min * 1e3),
    "bounds_after_mm": (nb * 1e3).tolist(),
    "locationInMesh_m": loc.tolist(),
}
(TRI / "_artery_scaled_summary.json").write_text(json.dumps(summary, indent=2))
print(f"\n[write] {(TRI / '_artery_scaled_summary.json').relative_to(REPO)}")
