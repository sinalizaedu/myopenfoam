#!/usr/bin/env python3
"""WP1.3 — compare FEA (Table 10) vs analytic membrane reference + prototype model."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WP12 = HERE.parents[1] / "wp1.2" / "scripts"
sys.path.insert(0, str(WP12))
sys.path.insert(0, str(HERE))

from membrane_spherical import (  # noqa: E402
    R_OBS_MM,
    _cauchy_equibiaxial_ogden,
    _cauchy_equibiaxial_yeoh,
    backward_fixed_point_analytic,
    secant_delta_k_pct,
)
from run_wp13_backward_displacement import load_fit_params  # noqa: E402

T_MM = 0.5
P0 = 16.9
P_FINAL = 50.0
CASES = (
    ("friedenwald", "ogden"),
    ("friedenwald", "yeoh"),
    ("pallikaris", "ogden"),
    ("pallikaris", "yeoh"),
    ("silver", "ogden"),
    ("silver", "yeoh"),
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--fit-root",
        type=Path,
        default=HERE.parents[1] / "wp1.2" / "output_literature_p50_digitized",
    )
    ap.add_argument(
        "--fea-root",
        type=Path,
        default=HERE.parent / "output_backward_displacement_6",
    )
    ap.add_argument(
        "--reference",
        type=Path,
        default=HERE.parent / "data" / "analytic_membrane_reference_wp13.json",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=HERE.parent / "output_backward_displacement_6" / "analytic_membrane_audit.json",
    )
    args = ap.parse_args()

    ref_doc = json.loads(args.reference.read_text())
    ref_cases = ref_doc["cases"]

    rows: list[dict] = []
    for target, mat in CASES:
        label = f"{target}_{mat}"
        fit = args.fit_root / label / "fit_results.json"
        fea_json = args.fea_root / label / "table10_backward_displacement.json"
        model, params = load_fit_params(fit, mat)
        if model.startswith("ogden"):
            mu1, a1 = params["mu1_MPa"], params["alpha1"]

            def sigma_fn(lam: float, mu1=mu1, a1=a1) -> float:
                return _cauchy_equibiaxial_ogden(lam, mu1, a1)
        else:
            c10, c20 = params["C10_MPa"], params["C20_MPa"]

            def sigma_fn(lam: float, c10=c10, c20=c20) -> float:
                return _cauchy_equibiaxial_yeoh(lam, c10, c20)

        fp_proto = backward_fixed_point_analytic(
            r_obs=R_OBS_MM,
            t_mm=T_MM,
            p0_mmhg=P0,
            sigma_fn=sigma_fn,
        )
        dk_proto = secant_delta_k_pct(
            R_OBS_MM,
            fp_proto.r_ref_mm,
            T_MM,
            P0,
            P_FINAL,
            sigma_fn,
        )

        ref = ref_cases[label]
        u_ref = float(ref["u_analytic_mm"])
        dk_ref = float(ref["deltaK_analytic_pct"])

        fea = json.loads(fea_json.read_text())
        u_fea = fea["fixed_point"]["u_mm"]
        dk_fea = fea["relative_change_pct"]["secant_10mmHg_pct"]

        row = {
            "label": label,
            "material": mat,
            "params": params,
            "reference_analytic": {"u_mm": u_ref, "deltaK_pct": dk_ref, "source": str(args.reference)},
            "fea_ccx_preCICE_2_20": {"u_mm": u_fea, "deltaK_pct": dk_fea},
            "prototype_membrane_spherical": {
                "u_mm": fp_proto.u_mm,
                "deltaK_pct": dk_proto,
                "note": "Equibiaxial thin-membrane p–λ; does not yet reproduce reference_analytic for all cases.",
            },
            "gaps_fea_vs_reference": {
                "u_rel_err_pct": 100.0 * (u_fea - u_ref) / u_ref if u_ref else None,
                "deltaK_gap_pp": dk_fea - dk_ref,
            },
            "acceptance_vs_reference": {
                "u_within_5pct": abs(u_fea - u_ref) <= 0.05 * abs(u_ref),
                "dK_within_0p1pp": abs(dk_fea - dk_ref) <= 0.1,
            },
        }
        rows.append(row)

    payload = {
        "P0_mmHg": P0,
        "p_final_mmHg": P_FINAL,
        "R_obs_mm": R_OBS_MM,
        "t_mm": T_MM,
        "fit_root": str(args.fit_root),
        "fea_root": str(args.fea_root),
        "reference_json": str(args.reference),
        "cases": rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {args.out}")
    for r in rows:
        g = r["gaps_fea_vs_reference"]
        ok = r["acceptance_vs_reference"]
        print(
            f"{r['label']:20s} u_ref={r['reference_analytic']['u_mm']:.4f} u_fea={r['fea_ccx_preCICE_2_20']['u_mm']:.4f} "
            f"dK_gap={g['deltaK_gap_pp']:+.2f} pp  OK_u={ok['u_within_5pct']} OK_dK={ok['dK_within_0p1pp']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
