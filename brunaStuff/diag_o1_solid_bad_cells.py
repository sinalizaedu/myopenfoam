#!/usr/bin/env python3
"""Locate inverted / zero-volume cells in the O1 solid polyMesh (diagnose-ciliary)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot_o1_solid_mesh import read_cell_zones, read_faces, read_labels, read_points

BAD = (8640, 8675, 8710, 8745, 8780, 8815, 8850, 8885, 8920, 8955, 8990, 9025)


def cell_points(faces, owner, neighbour, n_cells: int) -> list[set[int]]:
    pts: list[set[int]] = [set() for _ in range(n_cells)]
    n_int = len(neighbour)
    for fi, face in enumerate(faces):
        pts[int(owner[fi])].update(int(i) for i in face)
        if fi < n_int:
            pts[int(neighbour[fi])].update(int(i) for i in face)
    return pts


def main() -> None:
    polymesh = Path(sys.argv[1] if len(sys.argv) > 1 else
                    Path(__file__).resolve().parents[1]
                    / "cases/fsi-transient-o1-patch/solid/constant/polyMesh")
    points = read_points(polymesh / "points")
    faces = read_faces(polymesh / "faces")
    owner = read_labels(polymesh / "owner")
    neighbour = read_labels(polymesh / "neighbour")
    n_cells = int(owner.max()) + 1
    zone_of, names = read_cell_zones(polymesh / "cellZones", n_cells)
    cells = cell_points(faces, owner, neighbour, n_cells)
    print(f"mesh {polymesh}  cells={n_cells}")
    print(f"{'id':>6}  {'zone':10}  r_mm    y_mm    x_mm     z_mm")
    ids = BAD
    set_path = polymesh / "sets" / "zeroVolumeCells"
    if set_path.exists():
        body = set_path.read_text()
        ids = tuple(int(x) for x in body.split("(")[1].split(")")[0].split() if x.isdigit())
    for cid in ids:
        idx = np.fromiter(cells[cid], dtype=np.int64)
        p = points[idx]
        c = p.mean(axis=0)
        r = float(np.hypot(c[0], c[2]))
        zi = int(zone_of[cid])
        zname = names[zi] if 0 <= zi < len(names) else "?"
        print(f"{cid:6d}  {zname:10s}  {r*1e3:6.3f}  {c[1]*1e3:7.3f}  {c[0]*1e3:7.3f}  {c[2]*1e3:7.3f}")
    print()
    print("All 12 cells share one meridional column (Δid = 35 = 5×7 wine layers)")
    print("through 12 theta copies of the TM-back D-E strip — ciliary/limbus join.")


if __name__ == "__main__":
    main()
