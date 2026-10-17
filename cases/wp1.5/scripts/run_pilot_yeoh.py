#!/usr/bin/env python3
"""E6 / WP1.5 — Yeoh-only species pilot (legacy).

Superseded by ``run_pilot_species.py`` (Ogden + Yeoh, official Friedenwald P50 fits).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WP12 = HERE.parents[1] / "wp1.2" / "scripts"
sys.path.insert(0, str(WP12))

from yeoh_forward_run import run_yeoh_forward  # noqa: E402
from yeoh_material import P0_MMHG, load_yeoh_params  # noqa: E402

SPECIES = {
    "human": {"R_mm": 12.0, "t_mm": 0.5},
    "rabbit": {"R_mm": 7.6, "t_mm": 0.33},
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ne", type=int, default=8)
    default_fit = (
        HERE.parents[1]
        / "wp1.2"
        / "output_literature_p50_v2"
        / "friedenwald_yeoh"
        / "fit_results.json"
    )
    ap.add_argument("--p-final", type=float, default=50.0)
    ap.add_argument("--out", type=Path, default=HERE.parent / "output_pilot_yeoh")
    ap.add_argument("--fit", type=Path, default=default_fit)
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    work = args.out / "ccx_runs"
    params = load_yeoh_params(args.fit)
    results: list[dict] = []

    for name, geom in SPECIES.items():
        print(f"=== WP1.5 {name} ===")
        try:
            pv, meta = run_yeoh_forward(
                geom["R_mm"],
                geom["t_mm"],
                work,
                name,
                ne=args.ne,
                p_final=args.p_final,
                fit_path=args.fit,
            )
            # Effective K at small volume from curve
            v = [r["dV_uL"] for r in pv if r["dV_uL"] > 0]
            p = [r["p_mmhg"] for r in pv if r["dV_uL"] > 0]
            if v:
                k_eff = (p[0] - P0_MMHG) / v[0] if v[0] > 1e-9 else float("nan")
            else:
                k_eff = float("nan")
            results.append(
                {
                    "species": name,
                    **geom,
                    "status": "OK",
                    "V_max_uL": max(r["dV_uL"] for r in pv),
                    "K_eff_early_mmHg_per_uL": k_eff,
                }
            )
        except Exception as exc:
            results.append({"species": name, **geom, "status": f"FAIL: {exc}"})
        print(f"  -> {results[-1]['status']}")

    n_ok = sum(1 for r in results if r["status"] == "OK")
    (args.out / "pilot_results.json").write_text(
        json.dumps(
            {
                "material": {"model": "yeoh2", **params},
                "note": "Simplified WP1.5: 2-species spherical octant. Full globe+cornea+AC pending port.",
                "results": results,
            },
            indent=2,
        )
    )
    lines = [
        "# WP1.5 — anatomical pilot (Yeoh-2, simplified)\n",
        f"- **Material**: Yeoh E3",
        f"- **Convergence**: {n_ok}/{len(results)} OK",
        "",
        "| species | R | t | V_max | K_eff early | status |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for r in results:
        ke = f"{r.get('K_eff_early_mmHg_per_uL', 0):.3f}" if r["status"] == "OK" else "—"
        vm = f"{r.get('V_max_uL', 0):.1f}" if r["status"] == "OK" else "—"
        lines.append(
            f"| {r['species']} | {r['R_mm']} | {r['t_mm']} | {vm} | {ke} | {r['status']} |"
        )
    (args.out / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print(f"\nWrote {args.out / 'RESULTS.md'}")
    return 0 if n_ok == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
