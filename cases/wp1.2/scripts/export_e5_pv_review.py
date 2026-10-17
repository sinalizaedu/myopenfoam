#!/usr/bin/env python3
"""Export full P(V) tables for E5 pretension review (target vs FEA)."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from fit_hyperelastic import dp_dv_local  # noqa: E402
from fit_pallikaris import KF_PER_UL, P0_MMHG, pallikaris_pressure  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--e5",
        type=Path,
        default=HERE.parents[1] / "wp1.3" / "output_exploration" / "pretension_study.json",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=HERE.parents[1] / "wp1.3" / "output_exploration",
    )
    args = ap.parse_args()

    data = json.loads(args.e5.read_text())
    curve = data["fea_curve_dense"]
    v = np.array([r["V_uL"] for r in curve], dtype=float)
    p_abs = np.array([r["P_abs_mmHg"] for r in curve], dtype=float)
    dp = p_abs - P0_MMHG

    # Pallikaris target ΔP(V) on same V grid
    v_fine = np.linspace(0, min(50, float(v.max())), 51)
    dp_target = np.array([pallikaris_pressure(vv, P0_MMHG, KF_PER_UL) - P0_MMHG for vv in v_fine])

    csv_path = args.out / "e5_pv_review.csv"
    with csv_path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["V_uL", "P_abs_FEA_mmHg", "dP_FEA_mmHg", "dP_Pallikaris_mmHg"])
        for vi, pa, d in zip(v, p_abs, dp):
            dp_p = pallikaris_pressure(vi, P0_MMHG, KF_PER_UL) - P0_MMHG
            w.writerow([f"{vi:.6f}", f"{pa:.6f}", f"{d:.6f}", f"{dp_p:.6f}"])

    # Local slopes along FEA curve (ΔP vs V)
    k_v0 = dp_dv_local(v, dp, 0.0)
    v_p0 = data["dense"]["V_at_P0_uL"]
    k_p0 = dp_dv_local(v, dp, v_p0)

    lines = [
        "# E5 — P(V) curve review (before accepting −19.7%)\n",
        f"- **P₀**: {P0_MMHG} mmHg | **Kf**: {KF_PER_UL} /µL",
        f"- **Material**: Yeoh E3 (C10={data['material']['C10_MPa']:.4f}, C20={data['material']['C20_MPa']:.4f})",
        "",
        "## FEA dense curve (first 15 points — early region)\n",
        "| V (µL) | P_abs | ΔP | ΔP Pallikaris |",
        "|---:|---:|---:|---:|",
    ]
    for i, (vi, pa, d) in enumerate(zip(v, p_abs, dp)):
        if i >= 15:
            break
        dp_p = pallikaris_pressure(vi, P0_MMHG, KF_PER_UL) - P0_MMHG
        lines.append(f"| {vi:.4f} | {pa:.3f} | {d:.3f} | {dp_p:.3f} |")

    lines.extend(
        [
            "",
            "## Slopes (ΔP vs V on FEA curve)",
            "",
            f"- d(ΔP)/dV @ V≈0: **{k_v0:.4f}** mmHg/µL",
            f"- d(ΔP)/dV @ V={v_p0:.4f} µL (first loaded increment): **{k_p0:.4f}** mmHg/µL",
            f"- Relative change: **{100*(k_p0-k_v0)/k_v0:+.2f}%**",
            "",
            "## Interpretation notes",
            "",
            "- First FEA increment jumps to V≈0.7 µL — 'V≈P₀' slope is **not** at V=0; it is at the first",
            "  post-baseline load point. The −19.7% compares tangent at V=0 vs tangent at V≈0.7 µL.",
            "- FEA ΔP grows **faster** than Pallikaris in 0–10 µL (stiffer than target locally), then crosses.",
            f"- Full table: `{csv_path.name}`",
        ]
    )
    review = args.out / "E5_PV_REVIEW.md"
    review.write_text("\n".join(lines) + "\n")
    print(review.read_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
