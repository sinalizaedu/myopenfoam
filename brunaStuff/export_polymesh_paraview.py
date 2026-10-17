#!/usr/bin/env python3
"""Export OpenFOAM constant/polyMesh to ParaView VTU (+ optional patch VTP).

No OpenFOAM install required — reads ASCII polyMesh only.

Example:
    python3 brunaStuff/export_polymesh_paraview.py \\
        --case cases/fsi-transient-o1-patch/solid_meshes/A1 \\
        --out cases/fsi-transient-o1-patch/solid_meshes/A1/paraview/o1_solid_A1.vtu
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "brunaStuff"))

from plot_o1_solid_mesh import (  # noqa: E402
    read_boundary,
    read_cell_zones,
    read_faces,
    read_labels,
    read_points,
)

VTK_HEXAHEDRON = 12
VTK_TRIANGLE = 5
VTK_QUAD = 9


def _cell_faces(owner: np.ndarray, neighbour: np.ndarray, n_cells: int) -> list[list[int]]:
    cell_faces: list[list[int]] = [[] for _ in range(n_cells)]
    n_int = len(neighbour)
    for fi, c in enumerate(owner):
        cell_faces[int(c)].append(fi)
        if fi < n_int:
            cell_faces[int(neighbour[fi])].append(fi)
    return cell_faces


def _order_quad_ccw(pts: np.ndarray, outward: np.ndarray) -> np.ndarray:
    c = pts.mean(axis=0)
    n = np.cross(pts[1] - pts[0], pts[2] - pts[0])
    if np.dot(n, outward) < 0:
        pts = pts[[0, 3, 2, 1]]
        n = np.cross(pts[1] - pts[0], pts[2] - pts[0])
    n = n / (np.linalg.norm(n) or 1.0)
    u = pts[0] - c
    u = u - np.dot(u, n) * n
    u = u / (np.linalg.norm(u) or 1.0)
    v = np.cross(n, u)
    ang = np.arctan2((pts - c) @ v, (pts - c) @ u)
    return pts[np.argsort(ang)]


def _order_hex_vtk(
    face_indices: list[int], faces: list[np.ndarray], points: np.ndarray
) -> np.ndarray | None:
    if len(face_indices) != 6:
        return None
    face_pts = [points[faces[fi]].astype(float) for fi in face_indices]
    uniq = sorted({int(i) for fi in face_indices for i in faces[fi]})
    if len(uniq) != 8:
        return None

    center = points[uniq].mean(axis=0)
    pairs: list[tuple[int, int]] = []
    for i, fa in enumerate(face_indices):
        sa = set(faces[fa])
        for j, fb in enumerate(face_indices):
            if j <= i:
                continue
            if sa.isdisjoint(faces[fb]):
                pairs.append((fa, fb))
    if len(pairs) != 3:
        return None

    fa, fb = pairs[0]
    pa = _order_quad_ccw(points[faces[fa]].copy(), points[faces[fa]].mean(0) - center)
    pb = _order_quad_ccw(points[faces[fb]].copy(), points[faces[fb]].mean(0) - center)
    # Match pb corners to pa via nearest neighbours.
    pb_ord = np.empty_like(pb)
    used = set()
    for i, a in enumerate(pa):
        d = np.linalg.norm(pb - a, axis=1)
        for u in used:
            d[u] = np.inf
        j = int(np.argmin(d))
        used.add(j)
        pb_ord[i] = pb[j]

    def _pid(q: np.ndarray) -> int:
        for i in uniq:
            if np.allclose(points[i], q, rtol=0, atol=1e-12):
                return int(i)
        raise KeyError(f"vertex not in cell: {q}")

    return np.array([_pid(q) for q in np.vstack([pa, pb_ord])], dtype=np.int64)


def _hex_cells(
    points: np.ndarray,
    faces: list[np.ndarray],
    owner: np.ndarray,
    neighbour: np.ndarray,
) -> tuple[list[np.ndarray], list[int]]:
    n_cells = int(owner.max()) + 1
    cell_faces = _cell_faces(owner, neighbour, n_cells)
    hexes: list[np.ndarray] = []
    skipped: list[int] = []
    for ci, cf in enumerate(cell_faces):
        ordered = _order_hex_vtk(cf, faces, points)
        if ordered is None:
            skipped.append(ci)
            continue
        hexes.append(ordered)
    return hexes, skipped


def _write_vtu(
    out: Path,
    points: np.ndarray,
    cells: list[np.ndarray],
    cell_types: list[int],
    *,
    cell_zone_id: np.ndarray | None = None,
    cell_zone_name: list[str] | None = None,
) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    npts = len(points)
    ncells = len(cells)
    with open(out, "w") as fh:
        fh.write('<?xml version="1.0"?>\n')
        fh.write(
            '<VTKFile type="UnstructuredGrid" version="0.1" byte_order="LittleEndian">\n'
        )
        fh.write("  <UnstructuredGrid>\n")
        fh.write(f'    <Piece NumberOfPoints="{npts}" NumberOfCells="{ncells}">\n')

        fh.write("      <Points>\n")
        fh.write('        <DataArray type="Float64" NumberOfComponents="3" format="ascii">\n')
        for x, y, z in points:
            fh.write(f"          {x:.12e} {y:.12e} {z:.12e}\n")
        fh.write("        </DataArray>\n      </Points>\n")

        fh.write("      <Cells>\n")
        fh.write('        <DataArray type="Int64" Name="connectivity" format="ascii">\n')
        for conn in cells:
            fh.write("          " + " ".join(str(int(i)) for i in conn) + "\n")
        fh.write("        </DataArray>\n")
        fh.write('        <DataArray type="Int64" Name="offsets" format="ascii">\n')
        off = 0
        for conn in cells:
            off += len(conn)
            fh.write(f"          {off}\n")
        fh.write("        </DataArray>\n")
        fh.write('        <DataArray type="UInt8" Name="types" format="ascii">\n')
        for t in cell_types:
            fh.write(f"          {t}\n")
        fh.write("        </DataArray>\n      </Cells>\n")

        if cell_zone_id is not None:
            fh.write('      <CellData Scalars="cellZoneId">\n')
            fh.write('        <DataArray type="Int32" Name="cellZoneId" format="ascii">\n')
            for v in cell_zone_id:
                fh.write(f"          {int(v)}\n")
            fh.write("        </DataArray>\n")
            if cell_zone_name:
                fh.write(
                    '        <DataArray type="Utf8" Name="cellZone" NumberOfComponents="1" format="ascii">\n'
                )
                for nm in cell_zone_name:
                    fh.write(f"          {nm}\n")
                fh.write("        </DataArray>\n")
            fh.write("      </CellData>\n")

        fh.write("    </Piece>\n  </UnstructuredGrid>\n</VTKFile>\n")


def _write_vtp(
    out: Path,
    points: np.ndarray,
    polys: list[np.ndarray],
    *,
    patch_name: str,
) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    npts = len(points)
    ncells = len(polys)
    with open(out, "w") as fh:
        fh.write('<?xml version="1.0"?>\n')
        fh.write('<VTKFile type="PolyData" version="0.1" byte_order="LittleEndian">\n')
        fh.write("  <PolyData>\n")
        fh.write(f'    <Piece NumberOfPoints="{npts}" NumberOfCells="{ncells}">\n')
        fh.write("      <Points>\n")
        fh.write('        <DataArray type="Float64" NumberOfComponents="3" format="ascii">\n')
        for x, y, z in points:
            fh.write(f"          {x:.12e} {y:.12e} {z:.12e}\n")
        fh.write("        </DataArray>\n      </Points>\n")
        fh.write("      <Cells>\n")
        fh.write('        <DataArray type="Int64" Name="connectivity" format="ascii">\n')
        types: list[int] = []
        for conn in polys:
            fh.write("          " + " ".join(str(int(i)) for i in conn) + "\n")
            types.append(VTK_TRIANGLE if len(conn) == 3 else VTK_QUAD)
        fh.write("        </DataArray>\n")
        fh.write('        <DataArray type="Int64" Name="offsets" format="ascii">\n')
        off = 0
        for conn in polys:
            off += len(conn)
            fh.write(f"          {off}\n")
        fh.write("        </DataArray>\n")
        fh.write('        <DataArray type="UInt8" Name="types" format="ascii">\n')
        for t in types:
            fh.write(f"          {t}\n")
        fh.write("        </DataArray>\n      </Cells>\n")
        fh.write('      <CellData Scalars="patch">\n')
        fh.write('        <DataArray type="Utf8" Name="patch" NumberOfComponents="1" format="ascii">\n')
        for _ in polys:
            fh.write(f"          {patch_name}\n")
        fh.write("        </DataArray>\n      </CellData>\n")
        fh.write("    </Piece>\n  </PolyData>\n</VTKFile>\n")


def export_case(case: Path, out_vtu: Path, *, patches: tuple[str, ...]) -> dict:
    poly = case / "constant" / "polyMesh"
    if not (poly / "points").exists():
        raise FileNotFoundError(f"missing polyMesh at {poly}")

    points = read_points(poly / "points")
    faces = read_faces(poly / "faces")
    owner = read_labels(poly / "owner")
    neighbour = read_labels(poly / "neighbour")
    n_cells = int(owner.max()) + 1
    zone_of, zone_names = read_cell_zones(poly / "cellZones", n_cells)
    bnd = read_boundary(poly / "boundary")

    hexes, skipped = _hex_cells(points, faces, owner, neighbour)
    if skipped:
        print(f"WARN: skipped {len(skipped)} non-hex cells (first: {skipped[:5]})")

    kept_cells = [ci for ci in range(n_cells) if ci not in set(skipped)]
    zone_ids = np.array([int(zone_of[ci]) for ci in kept_cells], dtype=np.int32)
    zone_labels = [zone_names[int(zone_of[ci])] if zone_of[ci] >= 0 else "unzoned" for ci in kept_cells]

    _write_vtu(
        out_vtu,
        points,
        hexes,
        [VTK_HEXAHEDRON] * len(hexes),
        cell_zone_id=zone_ids,
        cell_zone_name=zone_labels,
    )

    patch_files: dict[str, Path] = {}
    out_dir = out_vtu.parent
    stem = out_vtu.stem
    for pname in patches:
        if pname not in bnd:
            continue
        start, count = bnd[pname]
        polys = [faces[fi] for fi in range(start, start + count)]
        vtp = out_dir / f"{stem}_{pname}.vtp"
        _write_vtp(vtp, points, polys, patch_name=pname)
        patch_files[pname] = vtp

    foam = case / f"{case.name}.foam"
    if not foam.exists():
        foam.write_text("/* ParaView OpenFOAM reader stub */\n")

    return {
        "vtu": out_vtu,
        "patches": patch_files,
        "foam": foam,
        "cells": len(hexes),
        "points": len(points),
        "zones": zone_names,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--case",
        type=Path,
        default=REPO / "cases/fsi-transient-o1-patch/solid_meshes/A1",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="output .vtu (default: <case>/paraview/<case.name>_volume.vtu)",
    )
    ap.add_argument(
        "--patches",
        default="fsi_active,outer,symmetry_0,symmetry_90,fsi_iris",
        help="comma-separated boundary patches to export as .vtp",
    )
    args = ap.parse_args()
    case = args.case.resolve()
    out = args.out or (case / "paraview" / f"{case.name}_volume.vtu")
    patch_list = tuple(p.strip() for p in args.patches.split(",") if p.strip())

    info = export_case(case, out.resolve(), patches=patch_list)
    print(f"Wrote volume: {info['vtu']}  ({info['cells']} hex cells, {info['points']} points)")
    print(f"Zones: {', '.join(info['zones'])}")
    for pname, path in info["patches"].items():
        print(f"  patch {pname}: {path}")
    print(f"OpenFOAM stub: {info['foam']}  (ParaView → OpenFOAM reader, Read Zones ON)")
    print()
    print("ParaView (VTU, no OpenFOAM needed):")
    print(f"  File → Open → {info['vtu']}")
    print('  Color by cellZoneId or cellZone; Representation → Surface With Edges')


if __name__ == "__main__":
    main()
