#!/usr/bin/env python3
"""Verify WP1.1 inputs and methodology vs wp1.tex (octant, not full-sphere)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WP1_1 = HERE.parent
sys.path.insert(0, str(HERE))

from run_verification_octant import (  # noqa: E402
    CASES,
    CONVERGENCE_LEVELS,
    DP_MMHG,
    E_MPA,
    NE_RECOMMENDED,
    NU,
    write_deck,
)

REPORT = {
    "human": {"R_mm": 12.0, "t_mm": 0.5},
    "rabbit": {"R_mm": 7.6, "t_mm": 0.33},
    "E_MPa": 3.0,
    "nu": 0.47,
    "dP_mmHg": 1.0,
    "mesh": "spherical_octant",
    "ne_reference": 6,
    "full_sphere_equiv_elements": 288,
    "nlgeom": "NO",
}


def check(name: str, got, expected, tol: float = 0.0) -> dict:
    if isinstance(got, (int, float)) and isinstance(expected, (int, float)):
        ok = abs(float(got) - float(expected)) <= tol
    else:
        ok = got == expected
    return {"name": name, "got": got, "expected": expected, "ok": ok}


def main() -> int:
    checks: list[dict] = []

    checks.append(check("E_MPa", E_MPA, REPORT["E_MPa"], 1e-9))
    checks.append(check("nu", NU, REPORT["nu"], 1e-9))
    checks.append(check("dP_mmHg", DP_MMHG, REPORT["dP_mmHg"], 1e-9))
    checks.append(check("NE_RECOMMENDED", NE_RECOMMENDED, REPORT["ne_reference"], 1e-9))
    checks.append(
        check(
            "full_sphere_equiv_elements",
            NE_RECOMMENDED * NE_RECOMMENDED * 8,
            REPORT["full_sphere_equiv_elements"],
            1e-9,
        )
    )
    checks.append(check("convergence_includes_ne6", 6 in CONVERGENCE_LEVELS, True))

    for species in ("human", "rabbit"):
        g = CASES[species]
        r = REPORT[species]
        checks.append(check(f"{species}_R_mm", g["R"], r["R_mm"], 1e-9))
        checks.append(check(f"{species}_t_mm", g["t"], r["t_mm"], 1e-9))

    sample = WP1_1 / "ccx" / "_verify_octant_sample.inp"
    write_deck(sample, "dummy_mesh.inp", 12.0, 0.5, 1.0, "human (verify)")
    text = sample.read_text()
    sample.unlink(missing_ok=True)

    checks.append(check("deck_NLGEOM_NO", "NLGEOM=NO" in text, True))
    checks.append(check("deck_STATIC", "*STATIC" in text, True))
    checks.append(check("deck_DSLOAD_INNER", "INNER_SURF, P," in text, True))
    checks.append(check("deck_symmetry_SYM_X", "SYM_X, 1, 1" in text, True))
    checks.append(check("deck_octant_heading", "octant" in text.lower(), True))

    out = {
        "scope": "inputs_and_methodology_octant",
        "primary_runner": "scripts/run_verification_octant.py",
        "checks": checks,
    }
    out_path = WP1_1 / "output_wp1.1" / "verify_wp1_methodology.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))

    failed = [c for c in checks if not c["ok"]]
    print(json.dumps(out, indent=2))
    if failed:
        print(f"\n{len(failed)} check(s) FAILED — {out_path}")
        return 1
    print(f"\nAll WP1.1 octant input/methodology checks passed — {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
