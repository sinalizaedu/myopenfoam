#!/usr/bin/env python3
"""WP1.2 literature matrix with corrected inverse engine (items 1–6).

Runs Friedenwald, Pallikaris (both baseline modes), Silver with Ogden/Yeoh;
objectives (a) pressure and (b) pressure + secant-K; linear baseline; CSV exports.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
WP12 = HERE.parent
sys.path.insert(0, str(HERE))

from ccx_utils import ccx_diagnostics  # noqa: E402
from fit_inverse_engine import (  # noqa: E402
    N_EVAL_PTS,
    equispaced_v_grid,
    export_curve_csvs,
    fit_material,
    linear_baseline_fit,
    save_change_log,
    write_summary_table,
    HyperelasticForward,
)
from fit_pallikaris import Geometry, P0_MMHG  # noqa: E402
from literature_targets import (  # noqa: E402
    generate_target,
    silver_v_max_at_p_cap,
    target_dp_on_grid,
)

PRIMARY_TARGETS = ("friedenwald", "pallikaris", "silver")


def run_target_bundle(
    target: str,
    out_root: Path,
    *,
    ne: int,
    p_cap: float,
    max_nfev: int,
    pallikaris_mode: str | None,
    skip_fea: bool,
) -> list[dict]:
    out = out_root / target
    if pallikaris_mode:
        out = out / pallikaris_mode
    out.mkdir(parents=True, exist_ok=True)

    p_final = p_cap
    if target == "pallikaris" and pallikaris_mode == "law_scaled":
        p_final = max(p_cap, 80.0)

    v_max = 50.0 if target == "friedenwald" else silver_v_max_at_p_cap(p_cap) if target == "silver" else 44.5
    csv_path = out / f"{target}_target.csv"
    mode = pallikaris_mode or "additive"
    if target == "pallikaris":
        generate_target(target, csv_path, v_max=v_max, p_cap=p_cap, pallikaris_mode=mode)  # type: ignore[arg-type]
    else:
        generate_target(target, csv_path, v_max=v_max, p_cap=p_cap)

    v_grid = equispaced_v_grid(v_max, N_EVAL_PTS)
    dp_target, meta = target_dp_on_grid(
        target,
        v_grid,
        p_cap=p_cap,
        pallikaris_mode=mode if target == "pallikaris" else "additive",  # type: ignore[arg-type]
    )
    linear = linear_baseline_fit(v_grid, dp_target)

    results: list[dict] = []
    if skip_fea:
        payload = {"target": target, "meta": meta, "linear_baseline": linear, "note": "skip_fea=True"}
        (out / "fit_bundle.json").write_text(json.dumps(payload, indent=2))
        return results

    geom = Geometry(R_mm=12.0, t_mm=0.5, source=f"{target}_wp12_corrected")
    for material in ("yeoh", "ogden"):
        for obj_mode in ("pressure", "pressure_and_secant_K"):
            tag = f"{material}_{obj_mode}"
            work = out / "ccx_runs" / tag
            forward = HyperelasticForward(
                work,
                geom=geom,
                ne=ne,
                p_final=p_final,
                p0=P0_MMHG,
            )
            fit = fit_material(
                forward,
                target,
                dp_target,
                v_grid,
                material,
                mode=obj_mode,  # type: ignore[arg-type]
                max_nfev=max_nfev,
            )
            fit["pallikaris_mode"] = mode if target == "pallikaris" else None
            fit["meta"] = meta
            fit["linear_baseline"] = linear
            fit["p_final_mmHg"] = p_final
            (out / f"fit_{tag}.json").write_text(json.dumps(fit, indent=2))
            results.append(fit)

    export_curve_csvs(out / "csv", target, results, linear, v_grid, dp_target)
    (out / "linear_baseline.json").write_text(json.dumps(linear, indent=2))
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--targets", default=",".join(PRIMARY_TARGETS))
    ap.add_argument("--p-cap", type=float, default=50.0, help="Absolute pressure cap for Silver / default ramp")
    ap.add_argument("--ne", type=int, default=8)
    ap.add_argument("--max-nfev", type=int, default=35)
    ap.add_argument("--out", type=Path, default=WP12 / "output_literature_corrected")
    ap.add_argument("--skip-fea", action="store_true", help="Only targets/CSVs without CalculiX")
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    try:
        ccx_info = ccx_diagnostics()
    except RuntimeError as exc:
        ccx_info = {"error": str(exc)}
    (args.out / "ccx_environment.json").write_text(json.dumps(ccx_info, indent=2))

    all_rows: list[dict] = []
    targets = [t.strip() for t in args.targets.split(",") if t.strip()]
    for target in targets:
        if target == "pallikaris":
            for mode in ("additive", "law_scaled"):
                print(f"\n=== {target} ({mode}) ===", flush=True)
                rows = run_target_bundle(
                    target,
                    args.out,
                    ne=args.ne,
                    p_cap=args.p_cap,
                    max_nfev=args.max_nfev,
                    pallikaris_mode=mode,
                    skip_fea=args.skip_fea,
                )
                all_rows.extend(rows)
        else:
            print(f"\n=== {target} ===", flush=True)
            rows = run_target_bundle(
                target,
                args.out,
                ne=args.ne,
                p_cap=args.p_cap,
                max_nfev=args.max_nfev,
                pallikaris_mode=None,
                skip_fea=args.skip_fea,
            )
            all_rows.extend(rows)

    if all_rows:
        write_summary_table(args.out / "SUMMARY.md", all_rows)
        at_bound = [r for r in all_rows if r.get("parameters_at_bound")]
        log_entries = [
            "ccx_utils.py: D1 scale 0.12 (Ogden tie + Yeoh fixed)",
            "fit_inverse_engine.py: log bounds, 15 multistart, dual objectives",
            "literature_targets.py: Silver V_max from P_cap; Pallikaris modes",
            f"Parameters still within 2% of bounds: {len(at_bound)} fits",
        ]
        if at_bound:
            for r in at_bound:
                log_entries.append(f"  {r['target']}/{r['material']}/{r['objective_mode']}: {r['parameters_at_bound']}")
        save_change_log(args.out / "CODE_CHANGE_LOG.md", log_entries, ccx_info)

    print(f"\nDone — output in {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
