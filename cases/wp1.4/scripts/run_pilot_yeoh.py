#!/usr/bin/env python3
"""E6 / WP1.4 — 14-case biometry pilot with validated Yeoh-2 (octant spherical)."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WP12 = HERE.parents[1] / "wp1.2" / "scripts"
sys.path.insert(0, str(WP12))

from yeoh_forward_run import run_yeoh_forward  # noqa: E402
from yeoh_material import load_yeoh_params  # noqa: E402


def load_biometry(path: Path) -> list[dict]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", type=Path, default=HERE.parent / "data" / "biometry_14.csv")
    ap.add_argument("--ne", type=int, default=8)
    ap.add_argument("--p-final", type=float, default=50.0)
    ap.add_argument("--out", type=Path, default=HERE.parent / "output_pilot_yeoh")
    ap.add_argument(
        "--fit",
        type=Path,
        default=WP12.parent / "output_literature_p50_v2" / "friedenwald_yeoh" / "fit_results.json",
    )
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    work = args.out / "ccx_runs"
    params = load_yeoh_params(args.fit)
    cases = load_biometry(args.data)

    results: list[dict] = []
    for row in cases:
        cid = row["case_id"]
        R = float(row["R_mm"])
        t = float(row["t_mm"])
        print(f"=== {cid} R={R} t={t} ===")
        try:
            pv, meta = run_yeoh_forward(
                R, t, work, cid, ne=args.ne, p_final=args.p_final, fit_path=args.fit
            )
            v_max = max(r["dV_uL"] for r in pv)
            p_max = max(r["p_mmhg"] for r in pv)
            entry = {
                **row,
                "status": "OK",
                "V_max_uL": v_max,
                "P_max_mmHg": p_max,
                "n_pv_points": len(pv),
            }
        except Exception as exc:
            entry = {**row, "status": f"FAIL: {exc}"}
        results.append(entry)
        print(f"  -> {entry['status']}")

    n_ok = sum(1 for r in results if r["status"] == "OK")
    payload = {
        "material": {"model": "yeoh2", **params},
        "p_final_mmHg": args.p_final,
        "ne": args.ne,
        "geometry_note": "Spherical octant proxy; quarter-ellipsoid port pending.",
        "results": results,
    }
    (args.out / "pilot_results.json").write_text(json.dumps(payload, indent=2))

    lines = [
        "# WP1.4 — 14-case biometry pilot (Yeoh-2)\n",
        f"- **Material**: C10={params['C10_MPa']:.4e}, C20={params['C20_MPa']:.4e} MPa",
        f"- **Convergence**: {n_ok}/{len(results)} OK",
        f"- **Mesh**: octant spherical, ne={args.ne}",
        "",
        "| case | R | t | V_max µL | status |",
        "|---|---:|---:|---:|---|",
    ]
    for r in results:
        vm = f"{r.get('V_max_uL', 0):.1f}" if r["status"] == "OK" else "—"
        lines.append(f"| {r['case_id']} | {r['R_mm']} | {r['t_mm']} | {vm} | {r['status']} |")
    (args.out / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print(f"\nWrote {args.out / 'RESULTS.md'} ({n_ok}/{len(results)} OK)")
    return 0 if n_ok == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
