#!/usr/bin/env python3
"""One-at-a-time sensitivity: each of 8 parameters at low/high vs nominal."""
from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
SWEEP = HERE.parent
sys.path.insert(0, str(HERE))

from case_model import nominal_row  # noqa: E402
from run_sweep import run_one_case  # noqa: E402

BOUNDS = {
    "comprimento_axial_mm": (20.0, 30.0),
    "t_equatorial_mm": (0.3, 0.8),
    "t_posterior_mm": (0.6, 1.2),
    "mu1_factor": (0.5, 1.5),
    "alpha1_factor": (0.5, 1.5),
    "ACD_mm": (2.0, 4.5),
}

CAT_BOUNDS = {
    "lens_status": ["phakic", "pseudophakic", "aphakic"],
    "vitrectomy": [False, True],
}


def _build_cases() -> list[dict]:
    base = nominal_row()
    cases = [{"case_id": "SENS_NOM", **base}]
    for key, (lo, hi) in BOUNDS.items():
        for tag, val in (("LO", lo), ("HI", hi)):
            row = deepcopy(base)
            row["case_id"] = f"SENS_{key}_{tag}"
            row[key] = val
            if key.endswith("_factor"):
                from case_model import ALPHA1_NOMINAL, MU1_NOMINAL

                if key == "mu1_factor":
                    row["mu1_MPa"] = MU1_NOMINAL * val
                else:
                    row["alpha1"] = ALPHA1_NOMINAL * val
            cases.append(row)
    for key, opts in CAT_BOUNDS.items():
        for opt in opts:
            row = deepcopy(base)
            lab = str(opt).upper() if isinstance(opt, bool) else str(opt)
            row["case_id"] = f"SENS_{key}_{lab}"
            row[key] = opt
            cases.append(row)
    return cases


def main() -> int:
    out = SWEEP / "output_sensitivity"
    work = out / "ccx_runs"
    work.mkdir(parents=True, exist_ok=True)
    cases = _build_cases()
    results = []
    v_nom = None
    for row in cases:
        print(f"=== {row['case_id']} ===")
        r = run_one_case(row, work, ne=8, p_final=50.0)
        results.append({k: v for k, v in r.items() if k != "pv_curve"})
        if row["case_id"] == "NOMINAL" and r.get("status") == "OK":
            v_nom = r["V_max_uL"]
    report = []
    for r in results:
        if r.get("status") != "OK":
            report.append({**r, "delta_pct": None})
            continue
        ref = v_nom or r["V_max_uL"]
        delta_pct = 100.0 * (r["V_max_uL"] - ref) / ref if ref else 0.0
        report.append({**r, "delta_pct_vs_nominal": round(delta_pct, 2)})
    out_path = out / "sensitivity_results.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nWrote {out_path}")
    skip = {"NOMINAL", "SENS_lens_status_phakic", "SENS_vitrectomy_FALSE"}
    weak = [
        x["case_id"]
        for x in report
        if x.get("status") == "OK"
        and x["case_id"] not in skip
        and abs(x.get("delta_pct_vs_nominal", 0)) < 1.0
    ]
    if weak:
        print("WARNING: |ΔV_max| < 1% vs nominal:", ", ".join(weak))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
