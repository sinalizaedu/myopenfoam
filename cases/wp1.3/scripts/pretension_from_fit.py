#!/usr/bin/env python3
"""WP1.3 — pretension slopes from wp1.2 fit (Ogden or Yeoh JSON layouts)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
WP12 = HERE.parents[1] / "wp1.2" / "scripts"
sys.path.insert(0, str(WP12))

from fit_hyperelastic import dp_dv_local  # noqa: E402

P0_DEFAULT = 16.9


def load_curve(fit: Path) -> tuple[np.ndarray, np.ndarray, dict, str]:
    data = json.loads(fit.read_text())
    sel = data.get("selected") or data.get("fit")
    model = sel.get("model", "unknown")
    params = sel.get("params", {})
    curve = sel["fea_curve"]
    v = np.array([r["V_uL"] for r in curve], dtype=float)
    p_key = "P_abs_mmHg" if "P_abs_mmHg" in curve[0] else "P_mmHg"
    p_abs = np.array([r[p_key] for r in curve], dtype=float)
    p0 = float(data.get("pallikaris", {}).get("P0_mmHg", P0_DEFAULT))
    dp = p_abs - p0
    return v, dp, params, model


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fit", type=Path, required=True)
    ap.add_argument("--material", default="")
    ap.add_argument("--p0", type=float, default=P0_DEFAULT)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    v, dp, params, model = load_curve(args.fit)
    k_v0 = dp_dv_local(v, dp, 0.0)
    v_ref = min(10.0, float(v.max()) * 0.2) if v.max() > 1e-6 else 2.0
    k_ref = dp_dv_local(v, dp, v_ref)
    rel_pct = 100.0 * (k_ref - k_v0) / k_v0 if abs(k_v0) > 1e-12 else float("nan")

    result = {
        "material": args.material or model,
        "model": model,
        "params": params,
        "P0_mmHg": args.p0,
        "V_ref_uL": v_ref,
        "K_local_at_V0_mmHg_per_uL": k_v0,
        "K_local_at_ref_mmHg_per_uL": k_ref,
        "relative_change_pct": rel_pct,
        "source_fit": str(args.fit),
        "note": "Slopes on fitted FEA ΔP(V); MULF not implemented.",
    }

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "pretension_study.json").write_text(json.dumps(result, indent=2))

    tag = args.material or model
    lines = [
        f"# wp1.3-{tag} — pretension (preliminary)\n",
        f"- **Model**: {model}",
        f"- **P₀**: {args.p0} mmHg",
        f"- **V ref**: {v_ref:.3f} µL",
        f"- **dP/dV @ V≈0**: {k_v0:.4f} mmHg/µL",
        f"- **dP/dV @ V ref**: {k_ref:.4f} mmHg/µL",
        f"- **Relative change**: {rel_pct:+.2f}%",
        "",
        result["note"],
    ]
    (args.out / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
