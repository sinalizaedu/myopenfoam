"""Inspect the original master's geometry STL.

The file at /Users/brunaenne/Documents/Doutorado/Backup/Geometria Mestrado.stl
is a binary STL exported (likely) from Ansys Workbench / SpaceClaim. STL files
are flat (no part hierarchy), but disconnected components correspond to
distinct anatomical parts. We split into connected components, measure each
(bbox, volume, surface area, centroid), and dump per-part STLs into
brunaStuff/geom_mestrado_parts/ for downstream meshing.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import trimesh

STL_PATH = Path(
    "/Users/brunaenne/Documents/Doutorado/Backup/Geometria Mestrado.stl"
)
OUT_DIR = Path(__file__).parent / "geom_mestrado_parts"
OUT_DIR.mkdir(exist_ok=True)


def main() -> None:
    print(f"[load] {STL_PATH}")
    mesh = trimesh.load_mesh(str(STL_PATH))
    if isinstance(mesh, trimesh.Scene):
        mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))

    print(f"[stats] vertices={len(mesh.vertices)}  faces={len(mesh.faces)}")
    print(f"[stats] is_watertight={mesh.is_watertight}")
    print(f"[stats] bounds (mm):\n{mesh.bounds}")
    extents = mesh.bounds[1] - mesh.bounds[0]
    print(f"[stats] extents (mm): {extents}")

    components = mesh.split(only_watertight=False)
    print(f"[split] connected components: {len(components)}")

    parts_info = []
    for i, c in enumerate(components):
        b = c.bounds
        ext = b[1] - b[0]
        centroid = c.centroid
        vol = float(c.volume) if c.is_volume else None
        area = float(c.area)
        info = {
            "index": i,
            "vertices": int(len(c.vertices)),
            "faces": int(len(c.faces)),
            "bounds_min_mm": [float(x) for x in b[0]],
            "bounds_max_mm": [float(x) for x in b[1]],
            "extents_mm": [float(x) for x in ext],
            "centroid_mm": [float(x) for x in centroid],
            "surface_area_mm2": area,
            "volume_mm3": vol,
            "watertight": bool(c.is_watertight),
        }
        parts_info.append(info)
        out = OUT_DIR / f"part_{i:02d}.stl"
        c.export(out)
        print(
            f"  part {i:02d}: V={vol if vol is None else round(vol, 3):>10}"
            f"  A={area:>10.2f}"
            f"  ext={np.round(ext, 2).tolist()}  → {out.name}"
        )

    (OUT_DIR / "_summary.json").write_text(json.dumps(parts_info, indent=2))
    print(f"[done] per-part STLs and summary in {OUT_DIR}")


if __name__ == "__main__":
    main()
