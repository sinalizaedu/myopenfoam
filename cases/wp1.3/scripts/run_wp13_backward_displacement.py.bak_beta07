#!/usr/bin/env python3
"""WP1.3 — backward displacement (Bols et al. 2013) pretension on spherical octant.

Compares reference (R=12 mm) vs pretensioned geometry (R_ref from fixed-point on ΔV at P₀).
Stiffness at P₀+10/+20/+30 mmHg via PCHIP on monotone P(V), both relative to P₀ volume.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator

HERE = Path(__file__).resolve().parent
WP12 = HERE.parents[1] / "wp1.2" / "scripts"
sys.path.insert(0, str(WP12))

from ccx_utils import YEOH_D1_MPA, ccx_diagnostics, d1_from_ogden_mu1  # noqa: E402
from fit_inverse_engine import HyperelasticForward  # noqa: E402
from fit_pallikaris import Geometry, P0_MMHG  # noqa: E402

R_OBS_MM = 12.0
T_MM = 0.5
BETA = 0.7
TOL_MM = 1e-3
MAX_ITER = 20
N_LOAD_STEPS = 24
EVAL_DP = (10.0, 20.0, 30.0)


def load_fit_params(fit: Path, material: str) -> tuple[str, dict]:
    data = json.loads(fit.read_text())
    sel = data.get("selected") or data
    if "params" in sel:
        params = dict(sel["params"])
        model = sel.get("model", "ogden1" if material == "ogden" else "yeoh2")
    else:
        params = dict(data.get("params", {}))
        model = data.get("model", "ogden1" if material == "ogden" else "yeoh2")
    if material == "ogden" or model.startswith("ogden"):
        return "ogden1", {
            "mu1_MPa": params["mu1_MPa"],
            "alpha1": params["alpha1"],
            "D1": params.get("D1", d1_from_ogden_mu1(params["mu1_MPa"])),
            "d1_tied_mu1": True,
        }
    return "yeoh2", {
        "C10_MPa": params["C10_MPa"],
        "C20_MPa": params.get("C20_MPa", 0.0),
        "D1": params.get("D1", YEOH_D1_MPA),
    }


def run_curve(
    work: Path,
    model: str,
    params: dict,
    *,
    r_mm: float,
    p0: float,
    p_final: float,
    ne: int,
) -> tuple[np.ndarray, np.ndarray]:
    fwd = HyperelasticForward(
        work,
        geom=Geometry(R_mm=R_OBS_MM, t_mm=T_MM),
        ne=ne,
        p_final=p_final,
        p0=p0,
        n_load_steps=N_LOAD_STEPS,
        r_mm=r_mm,
    )
    if model == "yeoh2":
        v, p = fwd.run_yeoh(params["C10_MPa"], params["C20_MPa"], "load")
    else:
        v, p = fwd.run_ogden(params["mu1_MPa"], params["alpha1"], "load")
    order = np.argsort(p)
    return v[order], p[order]


def p0_volume_increment(
    work: Path,
    model: str,
    params: dict,
    r_ref: float,
    p0: float,
    ne: int,
) -> float:
    fwd = HyperelasticForward(
        work,
        geom=Geometry(R_mm=R_OBS_MM, t_mm=T_MM),
        ne=ne,
        p_final=p0,
        p0=p0,
        n_load_steps=1,
        r_mm=r_ref,
    )
    return fwd.run_p0_only(model, params, "p0_probe")


def backward_displacement_fixed_point(
    work: Path,
    model: str,
    params: dict,
    *,
    p0: float,
    ne: int,
) -> dict:
    r_ref = R_OBS_MM
    history = []
    for k in range(MAX_ITER):
        dv = p0_volume_increment(work / f"fp_{k:02d}", model, params, r_ref, p0, ne)
        r_new = (r_ref**3 + 3.0 * dv / (4.0 * math.pi)) ** (1.0 / 3.0)
        r_next = r_ref - BETA * (r_new - R_OBS_MM)
        delta = abs(r_next - r_ref)
        history.append({"iter": k, "R_ref_mm": r_ref, "dV_P0_uL": dv, "R_new_mm": r_new, "delta_mm": delta})
        r_ref = r_next
        if delta < TOL_MM:
            break
    u = R_OBS_MM - r_ref
    return {
        "converged": history[-1]["delta_mm"] < TOL_MM if history else False,
        "n_iter": len(history),
        "R_ref_mm": r_ref,
        "u_mm": u,
        "four_u_over_R_pct": 100.0 * 4.0 * u / R_OBS_MM,
        "history": history,
    }


def stiffness_metrics(v: np.ndarray, p_abs: np.ndarray, p0: float) -> dict:
    """Secant at +10/+20/+30 mmHg and mean tangent 10→30 mmHg (PCHIP)."""
    pchip = PchipInterpolator(p_abs, v, extrapolate=False)
    v0 = float(pchip(p0))
    out = {"V_at_P0_uL": v0}
    v_at = {}
    for dp in EVAL_DP:
        p_eval = p0 + dp
        v_at[dp] = float(pchip(p_eval))
        out[f"K_secant_{int(dp)}mmHg"] = dp / max(v_at[dp] - v0, 1e-12)
    v10, v30 = v_at[10.0], v_at[30.0]
    k_tang = 20.0 / max(v30 - v10, 1e-12)
    out["K_tangent_mean_10_30"] = k_tang
    rel = {}
    for dp in EVAL_DP:
        k = out[f"K_secant_{int(dp)}mmHg"]
        rel[f"rel_vs_ref_{int(dp)}mmHg_pct"] = float("nan")
        out[f"K_secant_{int(dp)}mmHg"] = k
    out["_v_at"] = v_at
    return out


def relative_vs_reference(ref: dict, pret: dict) -> dict:
    rel = {}
    for dp in EVAL_DP:
        key = f"K_secant_{int(dp)}mmHg"
        kr, kp = ref[key], pret[key]
        rel[f"secant_{int(dp)}mmHg_pct"] = 100.0 * (kp - kr) / kr if abs(kr) > 1e-12 else float("nan")
    kt_r, kt_p = ref["K_tangent_mean_10_30"], pret["K_tangent_mean_10_30"]
    rel["tangent_10_30_pct"] = 100.0 * (kt_p - kt_r) / kt_r if abs(kt_r) > 1e-12 else float("nan")
    return rel


def run_one(
    fit: Path,
    material: str,
    out: Path,
    *,
    ne: int,
    p_final: float,
    p0: float,
    c20_zero: bool,
) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    model, params = load_fit_params(fit, material)
    if c20_zero and model == "yeoh2":
        params = {**params, "C20_MPa": 0.0}

    fp = backward_displacement_fixed_point(out / "fixed_point", model, params, p0=p0, ne=ne)
    r_ref = fp["R_ref_mm"]

    v_ref, p_ref = run_curve(out / "reference", model, params, r_mm=R_OBS_MM, p0=p0, p_final=p_final, ne=ne)
    v_pre, p_pre = run_curve(out / "backward_displacement", model, params, r_mm=r_ref, p0=p0, p_final=p_final, ne=ne)

    m_ref = stiffness_metrics(v_ref, p_ref, p0)
    m_pre = stiffness_metrics(v_pre, p_pre, p0)
    rel = relative_vs_reference(m_ref, m_pre)

    result = {
        "method": "backward_displacement_Bols2013",
        "material": material,
        "model": model,
        "params": params,
        "P0_mmHg": p0,
        "p_final_mmHg": p_final,
        "fixed_point": fp,
        "reference_R_mm": R_OBS_MM,
        "pretension_R_ref_mm": r_ref,
        "metrics_reference": m_ref,
        "metrics_backward_displacement": m_pre,
        "relative_change_pct": rel,
        "source_fit": str(fit),
        "ccx": ccx_diagnostics(),
        "c20_zero_diagnostic": c20_zero,
    }
    (out / "table10_backward_displacement.json").write_text(json.dumps(result, indent=2))
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fit", type=Path, action="append", required=True, help="fit JSON (repeat for matrix)")
    ap.add_argument("--material", action="append", required=True, help="ogden|yeoh parallel to --fit")
    ap.add_argument("--label", action="append", default=[], help="row label parallel to --fit")
    ap.add_argument("--ne", type=int, default=8)
    ap.add_argument("--p-final", type=float, default=50.0)
    ap.add_argument("--p0", type=float, default=P0_MMHG)
    ap.add_argument("--c20-zero", action="store_true", help="Yeoh diagnostic: C20=0 neo-Hooke")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    if len(args.fit) != len(args.material):
        raise SystemExit("--fit and --material must have same length")

    args.out.mkdir(parents=True, exist_ok=True)
    rows = []
    labels = args.label or [f"case_{i}" for i in range(len(args.fit))]
    for fit, mat, lab in zip(args.fit, args.material, labels):
        sub = args.out / lab
        row = run_one(fit, mat, sub, ne=args.ne, p_final=args.p_final, p0=args.p0, c20_zero=args.c20_zero)
        row["label"] = lab
        rows.append(row)

    (args.out / "table10_summary.json").write_text(json.dumps(rows, indent=2))
    lines = ["# WP1.3 Table 10 (backward displacement)\n", "| label | u [mm] | 4u/R [%] | ΔK+10 | ΔK+20 | ΔK+30 | ΔK_tang |"]
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        fp = r["fixed_point"]
        rel = r["relative_change_pct"]
        lines.append(
            f"| {r['label']} | {fp['u_mm']:.4f} | {fp['four_u_over_R_pct']:.2f} | "
            f"{rel.get('secant_10mmHg_pct', float('nan')):+.2f} | "
            f"{rel.get('secant_20mmHg_pct', float('nan')):+.2f} | "
            f"{rel.get('secant_30mmHg_pct', float('nan')):+.2f} | "
            f"{rel.get('tangent_10_30_pct', float('nan')):+.2f} |"
        )
    (args.out / "TABLE10.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
