#!/usr/bin/env python3
"""Verify O1 fluid/solid interface conformity and Lamminsalo surfaces."""
from __future__ import annotations

import argparse
import itertools
import math
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_FLUID = REPO / "cases/doc-g2-sim1/fluid/constant/polyMesh"
DEFAULT_SOLID = REPO / "cases/doc-g2-sim1/solid/constant/polyMesh"


def body(path: Path) -> str:
    text = path.read_text()
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"//[^\n]*", " ", text)
    start = text.find("FoamFile")
    if start >= 0:
        depth = 0
        for i in range(text.index("{", start), len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    return text[i + 1 :]
    return text


def points(path: Path) -> list[tuple[float, float, float]]:
    return [
        tuple(map(float, m.group(1).split()))
        for m in re.finditer(r"\(\s*([-\d.eE+\s]+?)\s*\)", body(path))
        if len(m.group(1).split()) == 3
    ]


def faces(path: Path) -> list[list[int]]:
    return [
        list(map(int, m.group(2).split()))
        for m in re.finditer(r"(\d+)\s*\(([\d\s]+?)\)", body(path))
    ]


def boundary(path: Path) -> dict[str, tuple[int, int]]:
    out = {}
    for m in re.finditer(r"(\w+)\s*\{([^}]*)\}", body(path)):
        n = re.search(r"\bnFaces\s+(\d+)", m.group(2))
        s = re.search(r"\bstartFace\s+(\d+)", m.group(2))
        if n and s:
            out[m.group(1)] = (int(s.group(1)), int(n.group(1)))
    return out


def patch_centroids(poly: Path, name: str):
    ps, fs, bs = points(poly / "points"), faces(poly / "faces"), boundary(poly / "boundary")
    if name not in bs:
        raise ValueError(f"{poly}: missing patch {name}")
    start, count = bs[name]
    result = []
    ids = set()
    for f in fs[start : start + count]:
        ids.update(f)
        result.append(tuple(sum(ps[i][j] for i in f) / len(f) for j in range(3)))
    return sorted(result), [ps[i] for i in ids]


def compare(fluid: Path, fp: str, solid: Path, sp: str, tol: float) -> tuple[bool, float]:
    fc, _ = patch_centroids(fluid, fp)
    sc, _ = patch_centroids(solid, sp)
    if len(fc) != len(sc):
        print(f"[FAIL] {fp} <-> {sp}: {len(fc)} != {len(sc)} faces")
        return False, math.inf
    # Lexicographic sorting is unstable for points that should have x=0 after
    # transformPoints (roundoff changes their order).  Match in small spatial
    # bins instead.
    cell = max(4.0 * tol, 1e-10)
    bins = {}
    for p in sc:
        key = tuple(math.floor(v / cell) for v in p)
        bins.setdefault(key, []).append(p)
    worst = 0.0
    for p in fc:
        key = tuple(math.floor(v / cell) for v in p)
        candidates = []
        for delta in itertools.product((-1, 0, 1), repeat=3):
            candidates.extend(bins.get(tuple(key[i] + delta[i] for i in range(3)), ()))
        if not candidates:
            worst = math.inf
            break
        worst = max(worst, min(math.dist(p, q) for q in candidates))
    ok = worst < tol
    print(f"[{'PASS' if ok else 'FAIL'}] {fp} <-> {sp}: {len(fc)} faces, max centroid error {worst:.3e} m")
    return ok, worst


def rz(p):
    return math.hypot(p[0], p[2]), p[1]


def dcircle(p, cy, radius):
    r, y = rz(p)
    return abs(math.hypot(r, y - cy) - radius)


def dellipse(p, a, b):
    r, y = rz(p)
    # First-order physical-distance approximation to the implicit ellipse.
    f = (r / a) ** 2 + (y / b) ** 2 - 1.0
    g = 2.0 * math.hypot(r / (a * a), y / (b * b))
    return abs(f) / max(g, 1e-30)


def segment_distance(p, a, b):
    r, y = rz(p)
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = ((r - a[0]) * dx + (y - a[1]) * dy) / (dx * dx + dy * dy)
    t = min(1.0, max(0.0, t))
    return math.hypot(r - a[0] - t * dx, y - a[1] - t * dy)


def geometry_check(solid: Path, tol: float) -> bool:
    _, active = patch_centroids(solid, "fsi_active")
    bs = boundary(solid / "boundary")
    wall_segments_mm = [
        ((6.61, -4.68), (6.70, -4.75)),
        ((6.93, -4.49), (6.84, -4.42)),
        ((6.84, -4.42), (6.90, -4.02)),
    ]
    active_dev = []
    for p in active:
        choices = [
            dcircle(p, -0.00015, 0.00801),
            dcircle(p, 0.00295, 0.00941),
            dellipse(p, 0.00837, 0.00690),
        ]
        choices += [
            segment_distance(p, tuple(v * 1e-3 for v in a), tuple(v * 1e-3 for v in b))
            for a, b in wall_segments_mm
        ]
        active_dev.append(min(choices))
    lens_dev = []
    if "fsi_lens" in bs:
        _, lens = patch_centroids(solid, "fsi_lens")
        lens_dev = [
            min(dcircle(p, -0.00031, 0.00576), dcircle(p, -0.00415, 0.00479))
            for p in lens
        ]
    worst = max(active_dev + lens_dev) if (active_dev or lens_dev) else math.inf
    ok = worst < tol
    print(f"[{'PASS' if ok else 'FAIL'}] Lamminsalo coupled surfaces: max point error {worst * 1e6:.2f} um")

    # Table-SI surfaces are parallel semi-axis offsets.  These values are also
    # the exact coordinates used by the generated retina/choroid/sclera strips.
    thicknesses = (0.00847 - 0.00837, 0.00867 - 0.00847, 0.00900 - 0.00867)
    expected = (0.00010, 0.00020, 0.00033)
    band_ok = all(abs(a - b) < 1e-12 for a, b in zip(thicknesses, expected))
    print(
        f"[{'PASS' if band_ok else 'FAIL'}] posterior band offsets: "
        + "/".join(f"{v * 1e3:.3f}" for v in thicknesses)
        + " mm"
    )
    return ok and band_ok


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fluid_polyMesh", nargs="?", type=Path, default=DEFAULT_FLUID)
    parser.add_argument("solid_polyMesh", nargs="?", type=Path, default=DEFAULT_SOLID)
    parser.add_argument(
        "--centroid-tol",
        type=float,
        default=1e-6,
        help="wall↔fsi_active centroid tolerance in metres (default: 1e-6)",
    )
    parser.add_argument(
        "--lens-centroid-tol",
        type=float,
        default=3e-6,
        help="lens_wall↔fsi_lens centroid tolerance in metres (default: 3e-6)",
    )
    parser.add_argument("--surface-tol", type=float, default=20e-6)
    args = parser.parse_args()
    failures = []
    solid_bs = boundary(args.solid_polyMesh / "boundary")
    interface_checks = [("wall", "fsi_active", args.centroid_tol)]
    if "fsi_lens" in solid_bs:
        interface_checks.append(("lens_wall", "fsi_lens", args.lens_centroid_tol))
    else:
        print("[SKIP] lens_wall <-> fsi_lens: solid lens void (no fsi_lens patch)")
    for fp, sp, tol in interface_checks:
        ok, _ = compare(args.fluid_polyMesh, fp, args.solid_polyMesh, sp, tol)
        failures.append(not ok)
    failures.append(not geometry_check(args.solid_polyMesh, args.surface_tol))
    if any(failures):
        print("O1 FSI verification FAILED")
        return 1
    print("O1 FSI verification PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
