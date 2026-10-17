#!/usr/bin/env python3
"""Re-fit Yeoh with relaxed C20 bounds — check if optimum stays at boundary."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from fit_pallikaris import generate_pallikaris_csv  # noqa: E402
from run_e3_e1b import PallikarisYeohForward, fit_yeoh2  # noqa: E402


def at_bound(val: float, bound: float, tol_frac: float = 0.02) -> bool:
    return val >= bound * (1.0 - tol_frac)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ne", type=int, default=8)
    ap.add_argument("--max-nfev", type=int, default=40)
    ap.add_argument(
        "--c20-max",
        type=float,
        nargs="+",
        default=[5.0, 10.0, 15.0],
        help="Upper bounds for C20 to sweep",
    )
    ap.add_argument("--out", type=Path, default=HERE.parent / "output_exploration" / "e3_bounds_check")
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    csv_path = args.out / "pallikaris_synthetic.csv"
    exp = generate_pallikaris_csv(csv_path)

    results: list[dict] = []
    prev_x0 = None

    for c20_max in args.c20_max:
        work = args.out / f"c20max_{c20_max:g}"
        forward = PallikarisYeohForward(work / "ccx_runs", ne=args.ne)
        import numpy as np

        x0 = prev_x0 if prev_x0 is not None else None
        fit = fit_yeoh2(
            forward,
            exp,
            max_nfev=args.max_nfev,
            c10_max=max(c20_max, 5.0),
            c20_max_mpa=c20_max,
            x0=x0,
        )
        c10 = fit["params"]["C10_MPa"]
        c20 = fit["params"]["C20_MPa"]
        prev_x0 = np.array([c10, np.log10(c20)])

        row = {
            "c20_max": c20_max,
            "C10_MPa": c10,
            "C20_MPa": c20,
            "C20_at_upper_bound": at_bound(c20, c20_max),
            "C10_at_upper_bound": at_bound(c10, max(c20_max, 5.0)),
            "R2": fit["quality"]["R2"],
            "max_residual_mmHg": fit["quality"]["max_residual_mmHg"],
            "nfev": fit["optimizer"]["nfev"],
        }
        results.append(row)
        (work / "fit.json").write_text(json.dumps(fit, indent=2))
        print(
            f"c20_max={c20_max:g} -> C10={c10:.6f} C20={c20:.6f} "
            f"R2={row['R2']:.6f} at_bound={row['C20_at_upper_bound']}"
        )

    (args.out / "bounds_sweep.json").write_text(json.dumps(results, indent=2))

    lines = [
        "# E3 — C20 bound sensitivity\n",
        "",
        "| C20 max | C10 | C20 | R² | max resid | C20 at bound? |",
        "|---:|---:|---:|---:|---:|---|",
    ]
    for r in results:
        lines.append(
            f"| {r['c20_max']:.1f} | {r['C10_MPa']:.4f} | {r['C20_MPa']:.4f} | "
            f"{r['R2']:.6f} | {r['max_residual_mmHg']:.2f} | "
            f"{'**yes**' if r['C20_at_upper_bound'] else 'no'} |"
        )
    glued = all(r["C20_at_upper_bound"] for r in results)
    lines.extend(
        [
            "",
            f"**Optimizer glued to C20 upper bound across sweep?** {'YES — R² may be understated' if glued else 'NO — optimum interior'}",
        ]
    )
    (args.out / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print(f"\nWrote {args.out / 'RESULTS.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
