#!/usr/bin/env python3
"""Print LaTeX table rows from output_literature_p50_digitized/*/fit_results.json."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WP12 = HERE.parent
sys.path.insert(0, str(HERE))

from literature_targets import V_MAX_SAFE  # noqa: E402
from yeoh_fit_bounds import YEOH_C10_HI_MPA, YEOH_C10_LO_MPA, YEOH_C20_HI_MPA, YEOH_C20_LO_MPA


def near_bound(val: float, lo: float, hi: float, frac: float = 0.02) -> bool:
    span = hi - lo
    if span <= 0:
        return False
    return val <= lo + frac * span or val >= hi - frac * span


def fmt_br(x: float, nd: int = 3) -> str:
    s = f"{x:.{nd}f}".replace(".", ",")
    return s


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=WP12 / "output_literature_p50_digitized")
    args = ap.parse_args()

    order = [
        ("friedenwald", "ogden"),
        ("friedenwald", "yeoh"),
        ("pallikaris", "ogden"),
        ("pallikaris", "yeoh"),
        ("silver", "ogden"),
        ("silver", "yeoh"),
    ]
    names = {
        "friedenwald": "Friedenwald",
        "pallikaris": "Pallikaris",
        "silver": "Silver",
    }

    for target, material in order:
        p = args.root / f"{target}_{material}" / "fit_results.json"
        if not p.is_file():
            print(f"% MISSING {p}")
            continue
        data = json.loads(p.read_text())
        sel = data["selected"]
        q = sel["quality"]
        par = sel["params"]
        vmax = V_MAX_SAFE.get(target, data.get("v_max_uL"))
        if material == "ogden":
            p1, p2 = par["mu1_MPa"], par["alpha1"]
            star1 = star2 = ""
        else:
            p1, p2 = par["C10_MPa"], par["C20_MPa"]
            star1 = "\\textsuperscript{*}" if near_bound(p1, YEOH_C10_LO_MPA, YEOH_C10_HI_MPA) else ""
            star2 = "\\textsuperscript{*}" if near_bound(p2, YEOH_C20_LO_MPA, YEOH_C20_HI_MPA) else ""
        p1s = f"{fmt_br(p1)}{star1 if material == 'yeoh' else ''}"
        p2s = f"{fmt_br(p2)}{star2 if material == 'yeoh' else ''}"
        if material == "ogden" and near_bound(p2, 0.5, 6.0):
            p2s += "\\textsuperscript{*}"
        print(
            f"{names[target]} & {material.capitalize()} & {fmt_br(float(vmax), 1).replace(',0', '')} & "
            f"{p1s if material == 'yeoh' else fmt_br(p1)} & {p2s if material == 'yeoh' else fmt_br(p2)} & "
            f"{fmt_br(q['R2'], 4)} & {fmt_br(q['max_residual_mmHg'], 2)} \\\\"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
