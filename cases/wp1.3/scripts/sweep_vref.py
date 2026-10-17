#!/usr/bin/env python3
"""WP1.3 — V_ref sensitivity sweep on an existing P(V) curve (no CCX).

Tests whether the pretension metric (relative change in local dP/dV between V≈0
and V=V_ref) is stable when V_ref is moved along the curve, or is an artifact of
where the finite-difference stencil lands on sparse CCX load steps.

Uses two derivative estimators:
  - finite_diff: existing dp_dv_local (linear interp + central difference)
  - pchip: monotonic cubic spline fit, analytic derivative
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator

HERE = Path(__file__).resolve().parent
WP12 = HERE.parents[1] / "wp1.2" / "scripts"
sys.path.insert(0, str(WP12))

from fit_hyperelastic import dp_dv_local  # noqa: E402

P0_DEFAULT = 16.9
DEFAULT_FRACTIONS = (0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40)


def load_curve(
    *,
    pretension: Path | None,
    pv: Path | None,
    fit: Path | None,
    p0: float | None,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """Return (v, dP, meta) from pretension_mulf.json, pv_mulf.json, or fit fea_curve."""
    if pretension is not None:
        data = json.loads(pretension.read_text())
        if "pv_curve" in data:
            curve = data["pv_curve"]
            v = np.array([r["V_uL"] for r in curve], dtype=float)
            dp = np.array([r["dP_mmHg"] for r in curve], dtype=float)
        else:
            raise ValueError(f"{pretension}: missing pv_curve")
        meta = {
            "source": str(pretension),
            "source_kind": "pretension_mulf",
            "material": data.get("material", ""),
            "model": data.get("model", ""),
            "P0_mmHg": float(data.get("P0_mmHg", p0 or P0_DEFAULT)),
            "V_ref_fixed_uL": data.get("V_ref_uL"),
            "relative_change_pct_fixed": data.get("relative_change_pct"),
        }
        return v, dp, meta

    if pv is not None:
        rows = json.loads(pv.read_text())
        if not isinstance(rows, list):
            raise ValueError(f"{pv}: expected list of P(V) rows")
        p0_use = p0 if p0 is not None else P0_DEFAULT
        v = np.array([r["dV_uL"] for r in rows], dtype=float)
        dp = np.array([r["p_mmhg"] - p0_use for r in rows], dtype=float)
        meta = {
            "source": str(pv),
            "source_kind": "pv_mulf",
            "P0_mmHg": p0_use,
        }
        return v, dp, meta

    if fit is not None:
        data = json.loads(fit.read_text())
        sel = data.get("selected") or data.get("fit")
        curve = sel["fea_curve"]
        v = np.array([r["V_uL"] for r in curve], dtype=float)
        p_key = "P_abs_mmHg" if "P_abs_mmHg" in curve[0] else "P_mmHg"
        p_abs = np.array([r[p_key] for r in curve], dtype=float)
        p0_use = float(p0 if p0 is not None else data.get("pallikaris", {}).get("P0_mmHg", P0_DEFAULT))
        meta = {
            "source": str(fit),
            "source_kind": "fit_fea_curve",
            "model": sel.get("model", ""),
            "P0_mmHg": p0_use,
        }
        return v, p_abs - p0_use, meta

    raise ValueError("Provide one of --pretension, --pv, or --fit")


def dp_dv_pchip(v: np.ndarray, dp: np.ndarray, v_query: float) -> float:
    """Analytic d(ΔP)/dV from a monotonic PCHIP through the discrete curve."""
    order = np.argsort(v)
    v, dp = v[order], dp[order]
    # Collapse duplicate V (shouldn't happen, but keeps PCHIP well-defined).
    v_u, idx = np.unique(v, return_index=True)
    dp_u = dp[idx]
    if len(v_u) < 2:
        return float("nan")
    spl = PchipInterpolator(v_u, dp_u, extrapolate=True)
    return float(spl.derivative()(v_query))


def slope_at(method: str, v: np.ndarray, dp: np.ndarray, v_query: float) -> float:
    if method == "finite_diff":
        return dp_dv_local(v, dp, v_query)
    if method == "pchip":
        return dp_dv_pchip(v, dp, v_query)
    raise ValueError(f"unknown method {method!r}")


def _assess_subset(rows: list[dict]) -> dict:
    rel = [r["relative_change_pct"] for r in rows if np.isfinite(r["relative_change_pct"])]
    if not rel:
        return {
            "n_valid": 0,
            "sign_stable": False,
            "magnitude_ratio": float("nan"),
            "verdict": "insufficient_data",
            "note": "No finite relative-change values.",
        }

    signs = {1 if x > 0 else (-1 if x < 0 else 0) for x in rel}
    nonzero_signs = {s for s in signs if s != 0}
    sign_stable = len(nonzero_signs) <= 1

    abs_rel = [abs(x) for x in rel if abs(x) > 1e-9]
    if len(abs_rel) >= 2:
        magnitude_ratio = max(abs_rel) / min(abs_rel)
    elif len(abs_rel) == 1:
        magnitude_ratio = 1.0
    else:
        magnitude_ratio = float("nan")

    if not sign_stable:
        verdict = "sampling_artifact"
        note = "Sign flips — metric is not robust to reference point."
    elif np.isfinite(magnitude_ratio) and magnitude_ratio >= 2.5:
        verdict = "sampling_artifact"
        note = f"Magnitude varies by {magnitude_ratio:.1f}x (≥2.5x) — sampling/noise dominated."
    else:
        verdict = "stable"
        note = "Sign and order of magnitude stable — effect appears real."

    return {
        "n_valid": len(rel),
        "sign_stable": sign_stable,
        "unique_signs": sorted(nonzero_signs),
        "rel_change_min_pct": float(min(rel)),
        "rel_change_max_pct": float(max(rel)),
        "magnitude_ratio": float(magnitude_ratio) if np.isfinite(magnitude_ratio) else magnitude_ratio,
        "verdict": verdict,
        "note": note,
    }


def assess_sweep(rows: list[dict]) -> dict:
    """Heuristic stability on full grid and on core band (10–30% V_max)."""
    core = [r for r in rows if 0.09 <= r["V_ref_fraction"] <= 0.31]
    full = _assess_subset(rows)
    core_assess = _assess_subset(core)
    return {
        **full,
        "core_fractions_10_to_30pct": core_assess,
        "note": (
            f"Full grid: {full['note']} "
            f"Core band (10–30% V_max): {core_assess['note']}"
        ),
        "verdict": core_assess["verdict"],
    }


def run_sweep(
    v: np.ndarray,
    dp: np.ndarray,
    *,
    fractions: tuple[float, ...],
    methods: tuple[str, ...],
) -> dict:
    order = np.argsort(v)
    v, dp = v[order], dp[order]
    v_max = float(v.max())

    out: dict = {
        "n_points": int(len(v)),
        "V_max_uL": v_max,
        "V_ref_fractions": list(fractions),
        "methods": {},
    }

    for method in methods:
        k_v0 = slope_at(method, v, dp, 0.0)
        rows = []
        for frac in fractions:
            v_ref = frac * v_max
            k_ref = slope_at(method, v, dp, v_ref)
            rel_pct = 100.0 * (k_ref - k_v0) / k_v0 if abs(k_v0) > 1e-12 else float("nan")
            rows.append(
                {
                    "V_ref_fraction": frac,
                    "V_ref_uL": v_ref,
                    "K_at_V0_mmHg_per_uL": k_v0,
                    "K_at_Vref_mmHg_per_uL": k_ref,
                    "relative_change_pct": rel_pct,
                }
            )

        v_ref_fixed = min(10.0, v_max * 0.2) if v_max > 1e-6 else 2.0
        k_ref_fixed = slope_at(method, v, dp, v_ref_fixed)
        rel_fixed = 100.0 * (k_ref_fixed - k_v0) / k_v0 if abs(k_v0) > 1e-12 else float("nan")

        out["methods"][method] = {
            "K_at_V0_mmHg_per_uL": k_v0,
            "V_ref_fixed_uL": v_ref_fixed,
            "relative_change_pct_at_fixed_Vref": rel_fixed,
            "sweep": rows,
            "assessment": assess_sweep(rows),
        }

    return out


def write_results_md(path: Path, meta: dict, sweep: dict) -> None:
    lines = [
        "# WP1.3 — V_ref sensitivity sweep\n",
        f"- **Source**: `{meta.get('source', '?')}` ({meta.get('source_kind', '?')})",
        f"- **P₀**: {meta.get('P0_mmHg', '?')} mmHg",
        f"- **Curve points**: {sweep['n_points']}, V_max = {sweep['V_max_uL']:.3f} µL",
    ]
    if meta.get("material"):
        lines.append(f"- **Material**: {meta['material']} ({meta.get('model', '')})")
    if meta.get("relative_change_pct_fixed") is not None:
        lines.append(
            f"- **Fixed V_ref result (MULF run)**: {meta['relative_change_pct_fixed']:+.2f}% "
            f"@ V_ref={meta.get('V_ref_fixed_uL')} µL"
        )
    lines.append("")

    for method, block in sweep["methods"].items():
        assess = block["assessment"]
        core = assess["core_fractions_10_to_30pct"]
        lines.extend(
            [
                f"## Method: `{method}`",
                "",
                f"- dP/dV @ V≈0: **{block['K_at_V0_mmHg_per_uL']:.4f}** mmHg/µL",
                f"- Fixed V_ref = min(10, 0.2·V_max) = {block['V_ref_fixed_uL']:.3f} µL → "
                f"**{block['relative_change_pct_at_fixed_Vref']:+.2f}%**",
                f"- **Verdict (core 10–30%)**: `{assess['verdict']}` — {core['note']}",
                f"- Full grid: {assess['rel_change_min_pct']:+.1f}% … {assess['rel_change_max_pct']:+.1f}% "
                f"(ratio {assess['magnitude_ratio']:.1f}x)",
                "",
                "| V_ref frac | V_ref [µL] | dP/dV @ V_ref | Δ% vs V≈0 |",
                "|---:|---:|---:|---:|",
            ]
        )
        for row in block["sweep"]:
            lines.append(
                f"| {100 * row['V_ref_fraction']:.0f}% | {row['V_ref_uL']:.3f} | "
                f"{row['K_at_Vref_mmHg_per_uL']:.4f} | {row['relative_change_pct']:+.2f}% |"
            )
        lines.append("")

    path.write_text("\n".join(lines) + "\n")


def write_plot(path: Path, sweep: dict, title: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7, 4.5))
    for method, block in sweep["methods"].items():
        xs = [r["V_ref_uL"] for r in block["sweep"]]
        ys = [r["relative_change_pct"] for r in block["sweep"]]
        ax.plot(xs, ys, "o-", label=method, linewidth=2, markersize=6)
        ax.axhline(block["relative_change_pct_at_fixed_Vref"], color=ax.lines[-1].get_color(), ls=":", alpha=0.5)

    ax.axhline(0.0, color="k", lw=0.8, alpha=0.4)
    ax.set_xlabel("V_ref [µL]")
    ax.set_ylabel("Relative change in dP/dV vs V≈0 [%]")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--pretension", type=Path, help="pretension_mulf.json (preferred)")
    src.add_argument("--pv", type=Path, help="pv_mulf.json from CCX extraction")
    src.add_argument("--fit", type=Path, help="wp1.2 fit_results.json fea_curve")
    ap.add_argument("--p0", type=float, default=None, help="P0 [mmHg] when using --pv")
    ap.add_argument(
        "--fractions",
        type=float,
        nargs="+",
        default=list(DEFAULT_FRACTIONS),
        help="V_ref as fraction of V_max (default: 2%% … 40%%)",
    )
    ap.add_argument(
        "--methods",
        nargs="+",
        choices=["finite_diff", "pchip"],
        default=["finite_diff", "pchip"],
    )
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--tag", default="", help="Label for plot title / JSON")
    args = ap.parse_args()

    v, dp, meta = load_curve(
        pretension=args.pretension,
        pv=args.pv,
        fit=args.fit,
        p0=args.p0,
    )
    sweep = run_sweep(v, dp, fractions=tuple(args.fractions), methods=tuple(args.methods))

    result = {"meta": meta, "tag": args.tag, **sweep}
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "vref_sweep.json").write_text(json.dumps(result, indent=2))
    write_results_md(args.out / "VREF_SWEEP.md", meta, sweep)

    tag = args.tag or meta.get("material") or meta.get("model") or "P(V)"
    write_plot(args.out / "vref_sweep.png", sweep, f"V_ref sweep — {tag}")

    print((args.out / "VREF_SWEEP.md").read_text())
    print(f"wrote {args.out / 'vref_sweep.json'}")
    print(f"wrote {args.out / 'vref_sweep.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
