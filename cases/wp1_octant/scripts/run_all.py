#!/usr/bin/env python3
"""Orchestrate WP1.1 octant verification, WP1.2 Pallikaris fit, WP1.3 pretension."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WP11 = ROOT / "wp1.1" / "scripts"
WP12 = ROOT / "wp1.2" / "scripts"
WP13 = ROOT / "wp1.3" / "scripts"
OUT = ROOT / "wp1_octant" / "output"


def run(cmd: list[str], label: str) -> None:
    print(f"\n{'='*60}\n{label}\n{'='*60}")
    subprocess.run(cmd, check=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skip-wp11", action="store_true")
    ap.add_argument("--skip-wp12", action="store_true")
    ap.add_argument("--skip-wp13", action="store_true")
    ap.add_argument("--wp12-ne", type=int, default=6)
    ap.add_argument("--wp12-max-nfev", type=int, default=25)
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)

    if not args.skip_wp11:
        run([sys.executable, str(WP11 / "run_verification_octant.py")], "WP1.1 octant K verification")

    wp12_out = ROOT / "wp1.2" / "output_octant"
    if not args.skip_wp12:
        run(
            [
                sys.executable,
                str(WP12 / "fit_pallikaris.py"),
                "--ne",
                str(args.wp12_ne),
                "--max-nfev",
                str(args.wp12_max_nfev),
                "--out",
                str(wp12_out),
            ],
            "WP1.2 Pallikaris Ogden fit",
        )

    if not args.skip_wp13:
        fit = wp12_out / "fit_results.json"
        if not fit.is_file():
            print(f"Missing {fit}; run WP1.2 first.")
            return 1
        run(
            [
                sys.executable,
                str(WP13 / "pretension_study.py"),
                "--fit",
                str(fit),
                "--out",
                str(ROOT / "wp1.3" / "output_octant"),
            ],
            "WP1.3 pretension study",
        )

    summary = OUT / "PIPELINE_DONE.txt"
    summary.write_text(
        "WP1 octant pipeline completed.\n"
        f"  wp1.1: {ROOT / 'wp1.1' / 'output_octant'}\n"
        f"  wp1.2: {wp12_out}\n"
        f"  wp1.3: {ROOT / 'wp1.3' / 'output_octant'}\n"
    )
    print(f"\nDone. Summary: {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
