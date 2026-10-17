#!/usr/bin/env python3
"""WP1.3 — compare local dP/dV at V≈0 vs at P₀ from wp1.2 FEA curve."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WP12_SCRIPTS = HERE.parents[1] / "wp1.2" / "scripts"
sys.path.insert(0, str(WP12_SCRIPTS))

from fit_hyperelastic import dp_dv_local  # noqa: E402

P0_DEFAULT = 16.9


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--fit",
        type=Path,
        default=HERE.parents[1] / "wp1.2" / "output_octant" / "fit_results.json",
    )
    ap.add_argument("--p0", type=float, default=P0_DEFAULT, help="Reference pressure [mmHg]")
    ap.add_argument("--out", type=Path, default=HERE.parent / "output_octant")
    args = ap.parse_args()

    data = json.loads(args.fit.read_text())
    curve = data["selected"]["fea_curve"]
    import numpy as np

    v = np.array([r["V_uL"] for r in curve], dtype=float)
    p = np.array([r["P_mmHg"] for r in curve], dtype=float)

    k_v0 = dp_dv_local(v, p, 0.0)
    # Slope at a small post-baseline volume (handoff compares V≈0 vs mid-range stiffness)
    v_ref = min(10.0, float(v.max()) * 0.2) if v.max() > 1e-6 else 5.0
    k_at_ref = dp_dv_local(v, p, v_ref)
    v_at_p0 = v_ref
    k_at_p0 = k_at_ref
    rel_pct = 100.0 * (k_at_p0 - k_v0) / k_v0 if abs(k_v0) > 1e-12 else float("nan")

    result = {
        "P0_mmHg": args.p0,
        "V_at_P0_uL": v_at_p0,
        "K_local_at_V0_mmHg_per_uL": k_v0,
        "K_local_at_P0_mmHg_per_uL": k_at_p0,
        "relative_change_pct": rel_pct,
        "source_fit": str(args.fit),
        "ogden_params": data["selected"].get("params", {}),
    }

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "pretension_study.json").write_text(json.dumps(result, indent=2))

    lines = [
        "# wp1.3 — pretension quantification (preliminary)\n",
        f"- **P₀**: {args.p0} mmHg",
        f"- **V @ P₀** (from FEA curve): {v_at_p0:.3f} µL",
        f"- **dP/dV @ V≈0**: {k_v0:.4f} mmHg/µL",
        f"- **dP/dV @ P₀**: {k_at_p0:.4f} mmHg/µL",
        f"- **Relative change**: {rel_pct:+.2f}%",
        "",
        "Note: slope comparison on fitted P(V) curve; MULF not implemented yet.",
    ]
    (args.out / "RESULTS.md").write_text("\n".join(lines))
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
