#!/usr/bin/env python3
"""Fail if ac_inlet / outlet_tm are not on the TM / CB production band (Y-axis r,y)."""

from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

CASE = Path(__file__).resolve().parent.parent
MESH = CASE / "fluid" / "constant" / "polyMesh"

# Lamminsalo TM SE / AC inlet (m), with pad for coarse N1 faces.
OUTLET = dict(r=(6.15e-3, 7.40e-3), y=(-5.20e-3, -4.15e-3))
INLET = dict(r=(6.30e-3, 7.55e-3), y=(-4.25e-3, -3.00e-3))


def _skip_header(lines: list[str]) -> int:
    i = 0
    while i < len(lines) and not lines[i].strip().isdigit():
        i += 1
    return i


def _read_label_list(path: Path) -> list[int]:
    lines = path.read_text().splitlines()
    i = _skip_header(lines)
    n = int(lines[i].strip())
    i += 1
    if lines[i].strip() != "(":
        raise SystemExit(f"ERROR: expected '(' in {path}")
    i += 1
    return [int(lines[i + k].strip()) for k in range(n)]


def _read_points(path: Path) -> list[tuple[float, float, float]]:
    raw = path.read_bytes()
    if b"format" in raw[:2048] and b"binary" in raw[:2048]:
        raise SystemExit(
            f"ERROR: {path} is binary; Allrun.sim4 must foamFormatConvert to ascii"
        )
    lines = raw.decode("utf-8").splitlines()
    i = _skip_header(lines)
    n = int(lines[i].strip())
    i += 2
    pts = []
    for k in range(n):
        s = lines[i + k].strip().strip("()")
        x, y, z = (float(v) for v in s.split())
        pts.append((x, y, z))
    return pts


def _read_faces(path: Path) -> list[list[int]]:
    lines = path.read_text().splitlines()
    i = _skip_header(lines)
    n = int(lines[i].strip())
    i += 2
    faces: list[list[int]] = []
    for k in range(n):
        line = lines[i + k].strip()
        _n, rest = line.split("(", 1)
        faces.append([int(x) for x in rest.rstrip(")").split()])
    return faces


def _patch_range(boundary: str, name: str) -> tuple[int, int] | None:
    m = re.search(
        rf"\b{name}\b\s*\{{[^}}]*?nFaces\s+(\d+);\s*startFace\s+(\d+);",
        boundary,
        re.S,
    )
    if not m:
        return None
    return int(m.group(2)), int(m.group(1))


def _face_centre(pts, faces, fi: int) -> tuple[float, float, float]:
    ids = faces[fi]
    sx = sy = sz = 0.0
    for pid in ids:
        x, y, z = pts[pid]
        sx += x
        sy += y
        sz += z
    n = float(len(ids))
    return sx / n, sy / n, sz / n


def _check_band(name: str, centres: list[tuple[float, float, float]], band: dict) -> None:
    if not centres:
        raise SystemExit(f"ERROR: {name} has 0 faces")
    rs = [math.hypot(c[0], c[2]) for c in centres]
    ys = [c[1] for c in centres]
    print(
        f"  {name}: {len(centres)} faces  "
        f"r=[{min(rs)*1e3:.3f},{max(rs)*1e3:.3f}] mm  "
        f"y=[{min(ys)*1e3:.3f},{max(ys)*1e3:.3f}] mm"
    )
    for i, (r, y) in enumerate(zip(rs, ys)):
        if r < band["r"][0] or r > band["r"][1] or y < band["y"][0] or y > band["y"][1]:
            raise SystemExit(
                f"ERROR: {name} face {i} outside TM/CB band "
                f"(r={r*1e3:.3f} mm, y={y*1e3:.3f} mm). "
                "Flow would bypass tm_zone and IOP would stick at P_TM=10 mmHg."
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--owners-in-tm-zone",
        action="store_true",
        help="Require outlet_tm owner cells to sit in tm_zone (after topoSet.g2).",
    )
    args = parser.parse_args()

    boundary = (MESH / "boundary").read_text()
    pts = _read_points(MESH / "points")
    faces = _read_faces(MESH / "faces")
    owner = _read_label_list(MESH / "owner")

    print("=== TM patch check ===")
    stored = {}
    for name, band in (("outlet_tm", OUTLET), ("ac_inlet", INLET)):
        rng = _patch_range(boundary, name)
        if rng is None:
            raise SystemExit(f"ERROR: patch {name} missing")
        start, n = rng
        cs = [_face_centre(pts, faces, start + i) for i in range(n)]
        stored[name] = (start, n)
        _check_band(name, cs, band)

    if args.owners_in_tm_zone:
        tz_path = MESH / "sets" / "tm_zone"
        if not tz_path.is_file():
            raise SystemExit("ERROR: tm_zone cellSet missing")
        tm = set(_read_label_list(tz_path))
        start, n = stored["outlet_tm"]
        owners = [owner[start + i] for i in range(n)]
        n_hit = sum(c in tm for c in owners)
        print(f"  outlet_tm owners in tm_zone: {n_hit}/{n}")
        if n_hit == 0:
            raise SystemExit(
                "ERROR: outlet_tm does not touch tm_zone — Darcy TM is bypassed."
            )
    print("  OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
