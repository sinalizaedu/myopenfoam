#!/usr/bin/env python3
"""Check WP1.1 octant results at ne=6 (288 elem) vs wp1.tex tables."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WP1_1 = HERE.parent
OUT_OCT = WP1_1 / "output_octant"
SUMMARY = OUT_OCT / "summary.json"

# wp1.tex Tabela sensibilidade / independência @ 288 elementos equivalentes
REPORT_TARGETS = {
    "human": {
        "full_sphere_equiv_elements": 288,
        "K_FEA_mmHg_per_uL": 0.163338,
        "K_analytic_mmHg_per_uL": 0.162933,
        "error_pct": 0.25,
    },
    "rabbit": {
        "full_sphere_equiv_elements": 288,
        "K_FEA_mmHg_per_uL": 0.670183,
        "K_analytic_mmHg_per_uL": 0.668380,
        "error_pct": 0.27,
    },
}
NE_REF = 6
K_TOL = 5e-4
ERR_TOL = 0.04  # published +0.25% / +0.27% (2 decimals)


def check(name: str, got: float, expected: float, tol: float) -> dict:
    ok = abs(got - expected) <= tol
    return {"name": name, "got": got, "expected": expected, "abs_tol": tol, "ok": ok}


def check_bool(name: str, ok: bool, detail: str = "") -> dict:
    return {"name": name, "ok": bool(ok), "detail": detail}


def find_row(summary: dict, case: str, ne: int) -> dict | None:
    for r in summary.get("results", []):
        if r.get("case") == case and r.get("ne") == ne:
            return r
    return None


def main() -> int:
    if not SUMMARY.is_file():
        print(f"Missing {SUMMARY} — run ./Allrun (or reprocess_octant.py) first.")
        return 1

    summary = json.loads(SUMMARY.read_text())
    checks: list[dict] = []

    mesh_ok = summary.get("mesh_kind") in ("spherical_octant", "spherical") and summary.get(
        "bc_mode"
    ) == "symmetry_octant"
    checks.append(
        {
            "name": "summary_mesh_kind_octant",
            "ok": mesh_ok,
            "mesh_kind": summary.get("mesh_kind"),
            "bc_mode": summary.get("bc_mode"),
        }
    )

    checks.append(
        {
            "name": "summary_ne_recommended",
            "ok": summary.get("ne_recommended") == NE_REF,
            "got": summary.get("ne_recommended"),
            "expected": NE_REF,
        }
    )

    for case, tgt in REPORT_TARGETS.items():
        row = find_row(summary, case, NE_REF)
        if row is None:
            checks.append({"name": f"{case}_ne6_row", "ok": False, "detail": "missing in summary.results"})
            continue
        checks.append(
            check(
                f"{case}_full_sphere_equiv_elements",
                float(row["full_sphere_equiv_elements"]),
                float(tgt["full_sphere_equiv_elements"]),
                0.0,
            )
        )
        checks.append(
            check(f"{case}_K_FEA", float(row["K_FEA_mmHg_per_uL"]), tgt["K_FEA_mmHg_per_uL"], K_TOL)
        )
        err_recomputed = 100.0 * (
            float(row["K_FEA_mmHg_per_uL"]) - float(row["K_analytic_mmHg_per_uL"])
        ) / float(row["K_analytic_mmHg_per_uL"])
        checks.append(
            check_bool(
                f"{case}_error_pct_matches_recomputed",
                abs(float(row["error_pct"]) - err_recomputed) < 1e-6,
                f"stored={row['error_pct']}, recomputed={err_recomputed}",
            )
        )
        checks.append(
            check(f"{case}_error_pct", err_recomputed, tgt["error_pct"], ERR_TOL)
        )

    out = {"summary_path": str(SUMMARY), "checks": checks}
    out_path = WP1_1 / "output_wp1.1" / "verify_wp1_octant_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))

    failed = [c for c in checks if not c.get("ok", False)]
    print(json.dumps(out, indent=2))
    if failed:
        print(f"\n{len(failed)} report check(s) FAILED — {out_path}")
        return 1
    print(f"\nWP1.1 octant matches wp1.tex @ ne=6 (288 elem) — {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
