#!/usr/bin/env python3
"""E5 — WP1.3 pretension with validated Yeoh (fitted curve + dense forward)."""
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
from yeoh_forward_run import run_yeoh_forward  # noqa: E402
from yeoh_material import P0_MMHG, load_yeoh_params  # noqa: E402


def dedupe_curve(v: np.ndarray, p: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Average duplicate V entries from FRD sampling."""
    order = np.argsort(v)
    v, p = v[order], p[order]
    uniq_v: list[float] = []
    uniq_p: list[float] = []
    i = 0
    while i < len(v):
        j = i + 1
        while j < len(v) and abs(v[j] - v[i]) < 1e-9:
            j += 1
        uniq_v.append(float(np.mean(v[i:j])))
        uniq_p.append(float(np.mean(p[i:j])))
        i = j
    return np.array(uniq_v), np.array(uniq_p)


def slopes(v: np.ndarray, p_abs: np.ndarray, v_ref: float = 10.0) -> dict:
    dp = p_abs - P0_MMHG
    k0 = dp_dv_local(v, dp, 0.0)
    kr = dp_dv_local(v, dp, v_ref)
    return {
        "K_at_V0": k0,
        "K_at_Vref": kr,
        "V_ref_uL": v_ref,
        "rel_change_pct": 100.0 * (kr - k0) / k0 if abs(k0) > 1e-12 else float("nan"),
    }


def load_fitted_curve(fit: Path) -> tuple[np.ndarray, np.ndarray]:
    data = json.loads(fit.read_text())
    sel = data.get("fit") or data.get("selected")
    curve = sel["fea_curve"]
    v = np.array([r["V_uL"] for r in curve], dtype=float)
    pk = "P_abs_mmHg" if "P_abs_mmHg" in curve[0] else "P_mmHg"
    p = np.array([r[pk] for r in curve], dtype=float)
    return v, p


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fit", type=Path, default=None)
    ap.add_argument("--ne", type=int, default=8)
    ap.add_argument("--n-dense", type=int, default=40)
    ap.add_argument("--out", type=Path, default=HERE.parent / "output_e5_yeoh")
    args = ap.parse_args()

    fit = args.fit
    params = load_yeoh_params(fit)
    args.out.mkdir(parents=True, exist_ok=True)
    work = args.out / "ccx_runs"

    # A) Slopes on fitted P(V) from WP1.2 (primary for report)
    fit_path = fit or Path(WP12.parent / "output_exploration" / "e3_yeoh" / "fit_results.json")
    v_fit, p_fit = load_fitted_curve(fit_path)
    s_fit = slopes(v_fit, p_fit, v_ref=10.0)

    # B) Dense forward (sanity / resolution check)
    rows, _ = run_yeoh_forward(12.0, 0.5, work, "dense", ne=args.ne, n_steps=args.n_dense, fit_path=fit)
    v_d = np.array([r["dV_uL"] for r in rows])
    p_d = np.array([r["p_mmhg"] for r in rows])
    v_d, p_d = dedupe_curve(v_d, p_d)
    s_dense = slopes(v_d, p_d, v_ref=10.0)

    result = {
        "material": {"model": "yeoh2", **params},
        "P0_mmHg": P0_MMHG,
        "fitted_curve": s_fit,
        "dense_forward_deduped": s_dense,
        "n_dense_points": int(len(v_d)),
        "source_fit": str(fit_path),
        "report_guidance": (
            "Use fitted_curve rel_change for WP1.3 preliminary text. "
            "dense_forward compares resolution; large delta vs fitted indicates "
            "increment/extraction artifact in early-V region, not MULF pretension."
        ),
    }
    (args.out / "pretension_e5.json").write_text(json.dumps(result, indent=2))

    lines = [
        "# E5 — WP1.3 pretension (Yeoh validado)\n",
        f"- **Yeoh E3**: C10={params['C10_MPa']:.6e}, C20={params['C20_MPa']:.6e} MPa",
        f"- **P₀**: {P0_MMHG} mmHg",
        "",
        "## A) Curva do ajuste WP1.2 (recomendado para relatório)",
        "",
        f"- d(ΔP)/dV @ V≈0: {s_fit['K_at_V0']:.4f} mmHg/µL",
        f"- d(ΔP)/dV @ V={s_fit['V_ref_uL']:.1f} µL: {s_fit['K_at_Vref']:.4f} mmHg/µL",
        f"- **Variação relativa**: {s_fit['rel_change_pct']:+.2f}%",
        "",
        f"## B) Forward denso ({args.n_dense} passos, V deduplicados)",
        "",
        f"- Variação relativa: {s_dense['rel_change_pct']:+.2f}%",
        "",
        "## Nota metodológica",
        "",
        "- **MULF não implementado** — inclinações na curva FEA, não pré-tensionamento fisiológico.",
        "- Não usar o −19,7% da versão anterior (artefato de incremento + duplicatas FRD).",
        f"- {result['report_guidance']}",
    ]
    (args.out / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
