#!/usr/bin/env python3
"""Plot experimental vs fitted P-V curve from wp1.2 output."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results", type=Path, required=True)
    ap.add_argument("--overlay", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    res = json.loads(args.results.read_text())
    sel = res["selected"]

    v_exp, p_exp, p_fea_pts = [], [], []
    v_dense, p_dense = [], []
    with open(args.overlay, newline="") as fh:
        reader = csv.reader(fh)
        mode = "exp"
        for row in reader:
            if not row or row[0].startswith("#"):
                if row and "dense FEA" in row[0]:
                    mode = "dense"
                continue
            if mode == "exp" and row[0] != "V_uL":
                v_exp.append(float(row[0]))
                p_exp.append(float(row[1]))
                p_fea_pts.append(float(row[2]))
            elif mode == "dense" and row[0] != "V_uL":
                v_dense.append(float(row[0]))
                p_dense.append(float(row[1]))

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(v_exp, p_exp, "o", label="Experimental (Ensaio A)", markersize=6)
    ax.plot(v_dense, p_dense, "-", label=f"FEA {sel['model']}", linewidth=2)
    ax.set_xlabel("Infused volume ΔV [µL]  (V=0 @ 15 mmHg)")
    ax.set_ylabel("IOP [mmHg]")
    q = sel["quality"]
    ax.set_title(
        f"wp1.2 inverse FEA — R²={q['R2']:.3f}, "
        f"max|resid|={q['max_residual_mmHg']:.1f} mmHg"
    )
    ax.grid(True, alpha=0.3)
    ax.legend()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(args.out, dpi=150)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
