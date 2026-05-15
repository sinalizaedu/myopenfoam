"""Generate curved ophthalmic artery STL geometry for snappyHexMesh.

Reads /Users/brunaenne/Documents/Doutorado/Backup/Geometria Mestrado.stl,
splits it into nerve (part_00) + artery lumen (part_01), and produces:

    artery.stl  - the artery as a filled solid (= part_01 as-is). The artery
                  wall is NOT modelled as a thin shell; instead, the curved
                  tube is meshed as a solid and the pulsatile blood pressure
                  is applied as outward radial traction on the lateral
                  surface. This is a first-order approximation that
                  preserves the curved geometry (the dominant mechanism for
                  optic-nerve tortuosity) while keeping the mesh robust.

    nerve.stl   - the optic nerve, for reference and future contact coupling.

All STLs are exported in meters (OpenFOAM default), with the `solid` block
inside the STL named so that snappyHexMesh creates a matching patch.

We also compute a representative `locationInMesh` point inside the solid
artery — needed so snappyHexMesh keeps the artery region and discards
everything else.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import trimesh

REPO = Path(__file__).resolve().parents[1]
SRC_STL = Path(
    "/Users/brunaenne/Documents/Doutorado/Backup/Geometria Mestrado.stl"
)
CASE_DIR = REPO / "cases" / "artoph-curva-mestrado"
TRISURF_DIR = CASE_DIR / "solid" / "constant" / "triSurface"


def write_named_stl(mesh: trimesh.Trimesh, path: Path, solid_name: str) -> None:
    """Write ASCII STL with a chosen solid name (snappyHexMesh uses this as patch)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        f.write(f"solid {solid_name}\n")
        for tri, n in zip(mesh.triangles, mesh.face_normals):
            f.write(f"  facet normal {n[0]:.6e} {n[1]:.6e} {n[2]:.6e}\n")
            f.write("    outer loop\n")
            for v in tri:
                f.write(f"      vertex {v[0]:.6e} {v[1]:.6e} {v[2]:.6e}\n")
            f.write("    endloop\n")
            f.write("  endfacet\n")
        f.write(f"endsolid {solid_name}\n")
    print(f"  [write] {path.relative_to(REPO)}  ({len(mesh.faces)} triangles)")


def main() -> None:
    print(f"[load] {SRC_STL}")
    src = trimesh.load_mesh(str(SRC_STL))
    if isinstance(src, trimesh.Scene):
        src = trimesh.util.concatenate(tuple(src.geometry.values()))

    parts = src.split(only_watertight=False)
    parts = sorted(parts, key=lambda m: m.volume, reverse=True)
    nerve, lumen = parts[0], parts[1]
    print(
        f"[split] nerve V={nerve.volume:.2f}mm3  lumen V={lumen.volume:.2f}mm3"
    )

    # mm → m
    nerve_m = nerve.copy()
    nerve_m.vertices = nerve_m.vertices * 1e-3
    artery_m = lumen.copy()
    artery_m.vertices = artery_m.vertices * 1e-3

    print(f"\n[bounds in meters]")
    print(f"  nerve  : {nerve_m.bounds}")
    print(f"  artery : {artery_m.bounds}")

    TRISURF_DIR.mkdir(parents=True, exist_ok=True)
    write_named_stl(artery_m, TRISURF_DIR / "artery.stl", "artery_surface")
    write_named_stl(nerve_m, TRISURF_DIR / "nerve.stl", "nerve")

    # locationInMesh: a point well inside the curved artery solid. We pick the
    # leftmost vertex in the mid-z band (which sits on the artery surface at
    # the "U" leftmost reach) and shift it inward by half the local diameter
    # along the +x axis (toward the centerline of the artery at that point).
    z_min, z_max = artery_m.bounds[0, 2], artery_m.bounds[1, 2]
    z_mid = (z_min + z_max) / 2.0
    band = (artery_m.vertices[:, 2] > z_mid - 2e-3) & (
        artery_m.vertices[:, 2] < z_mid + 2e-3
    )
    cands = artery_m.vertices[band] if band.any() else artery_m.vertices
    leftmost = cands[np.argmin(cands[:, 0])]
    # Shift +x by ~ half a tube radius (0.4 mm) to land on the centerline.
    loc_in_mesh = leftmost + np.array([0.4e-3, 0.0, 0.0])

    # Sanity check: the chosen point must lie strictly inside the closed mesh.
    if not artery_m.contains([loc_in_mesh])[0]:
        # Try a denser grid of candidate points and pick the first one that
        # the watertight mesh reports as interior.
        gx = np.linspace(z_min + 2e-3, z_max - 2e-3, 30)
        for zc in gx:
            for xc in np.linspace(-10e-3, 2e-3, 25):
                for yc in np.linspace(-4e-3, 3e-3, 15):
                    p = np.array([xc, yc, zc])
                    if artery_m.contains([p])[0]:
                        loc_in_mesh = p
                        break
                else:
                    continue
                break
            else:
                continue
            break

    print(f"\n[locationInMesh]  (inside the artery solid)")
    print(f"  x = {loc_in_mesh[0]: .6e} m  ({loc_in_mesh[0]*1e3: .3f} mm)")
    print(f"  y = {loc_in_mesh[1]: .6e} m  ({loc_in_mesh[1]*1e3: .3f} mm)")
    print(f"  z = {loc_in_mesh[2]: .6e} m  ({loc_in_mesh[2]*1e3: .3f} mm)")
    print(f"  inside artery: {artery_m.contains([loc_in_mesh])[0]}")

    summary = {
        "src_stl": str(SRC_STL),
        "modelling_approach": "filled artery solid (no hollow wall)",
        "patches_after_snappy": ["artery_surface", "nerve"],
        "artery_bounds_m": artery_m.bounds.tolist(),
        "nerve_bounds_m": nerve_m.bounds.tolist(),
        "locationInMesh_m": loc_in_mesh.tolist(),
    }
    (TRISURF_DIR / "_geometry_summary.json").write_text(
        json.dumps(summary, indent=2)
    )
    print(f"\n[write] {(TRISURF_DIR / '_geometry_summary.json').relative_to(REPO)}")


if __name__ == "__main__":
    main()
