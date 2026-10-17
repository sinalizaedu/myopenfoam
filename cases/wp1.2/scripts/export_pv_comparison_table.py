#!/usr/bin/env python3
"""Export P(V) table at handoff comparison volumes from forward_handoff curve."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
P0 = 16.9

# Anchor + WP1.3 slope region (handoff request)
V_QUERY = [
    0.0,
    1.0,
    2.0,
    2.86,
    5.0,
    7.5,
    10.0,
    12.5,
    15.0,
    20.0,
    25.0,
    30.0,
    35.99,
    50.0,
    72.43,
]


def main() -> int:
    src = HERE.parent / "output_octant" / "forward_handoff" / "pv_curve.csv"
    if not src.is_file():
        print(f"Missing {src}; run forward_handoff_compare.py first", file=sys.stderr)
        return 1

    rows = list(csv.DictReader(src.open()))
    v = np.array([float(r["V_uL"]) for r in rows])
    p_abs = np.array([float(r["P_mmHg"]) for r in rows])
    dp = p_abs - P0

    out = HERE.parent / "output_octant" / "forward_handoff" / "pv_comparison_table.csv"
    with out.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["V_uL", "P_abs_mmHg", "dP_mmHg", "note"])
        for vq in V_QUERY:
            if vq > v.max():
                w.writerow([f"{vq:.4f}", "", "", "beyond_FEA_range"])
                continue
            pa = float(np.interp(vq, v, p_abs))
            w.writerow([f"{vq:.4f}", f"{pa:.6f}", f"{pa - P0:.6f}", "linear_interp_17_steps"])

    print(f"Source: {src} ({len(v)} FEA load points, mu1=2.1397, alpha1=1.7709, D1=0.238446)")
    print(f"Wrote {out}\n")
    print(f"{'V_uL':>8}  {'P_abs':>10}  {'dP':>10}")
    for ln in out.read_text().strip().splitlines()[1:]:
        parts = ln.split(",")
        if parts[1]:
            print(f"{float(parts[0]):8.2f}  {float(parts[1]):10.4f}  {float(parts[2]):10.4f}")
        else:
            print(f"{float(parts[0]):8.2f}  (beyond range)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
