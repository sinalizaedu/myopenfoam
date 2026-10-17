#!/usr/bin/env python3
"""WP1.3 — Gee et al. (2010) MULF + local dP/dV from relaxed reference X_ref*."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
WP11 = HERE.parents[1] / "wp1.1" / "scripts"
WP12 = HERE.parents[1] / "wp1.2" / "scripts"
sys.path.insert(0, str(WP11))
sys.path.insert(0, str(WP12))

from ccx_utils import d1_from_ogden_mu1, run_ccx  # noqa: E402
from extract_pv_curve import extract_pv  # noqa: E402
from fit_hyperelastic import dp_dv_local  # noqa: E402
from mulf_gee import mulf_iterate, prepare_observed_mesh, verify_ccx_ok  # noqa: E402
from write_deck import write_deck  # noqa: E402

R_MM, T_MM = 12.0, 0.5
P0_DEFAULT = 16.9


def load_model_params(fit: Path, material: str) -> tuple[str, dict, float]:
    data = json.loads(fit.read_text())
    sel = data.get("selected") or data.get("fit")
    model = sel.get("model", material)
    params = dict(sel["params"])
    p0 = float(data.get("pallikaris", {}).get("P0_mmHg", P0_DEFAULT))
    if model.startswith("ogden") or material == "ogden":
        return "ogden1", {
            "mu1_MPa": params["mu1_MPa"],
            "alpha1": params["alpha1"],
            "D1": params.get("D1", d1_from_ogden_mu1(params["mu1_MPa"])),
            "d1_tied_mu1": params.get("d1_tied_mu1", True),
        }, p0
    return "yeoh2", {
        "C10_MPa": params["C10_MPa"],
        "C20_MPa": params["C20_MPa"],
    }, p0


def run_loading_curve(
    work: Path,
    mesh_name: str,
    model: str,
    params: dict,
    p0: float,
    p_final: float,
    n_steps: int,
) -> tuple[list[dict], str]:
    p_targets = [p0 + (p_final - p0) * i / n_steps for i in range(1, n_steps + 1)]
    deck = work / "loading.inp"
    write_deck(
        deck,
        mesh_name,
        T_MM,
        model,
        params,
        p_targets,
        label="WP1.3 MULF loading from X_ref*",
        bc_mode="symmetry_octant",
        p0_mmhg=p0,
    )
    frd = run_ccx(deck, clean=True)
    log = work / "log_loading.txt"
    ok, msg = verify_ccx_ok(log)
    if not ok:
        raise RuntimeError(f"Loading curve failed: {msg}")
    rows = extract_pv(deck, frd, R_MM, p0_mmhg=p0)
    return rows, msg


def v_ref_sweep(v: np.ndarray, dp: np.ndarray) -> list[dict]:
    """Relative stiffness change vs several V_ref choices."""
    if len(v) < 3:
        return []
    k0 = dp_dv_local(v, dp, 0.0)
    rows = []
    vmax = float(v.max())
    candidates = sorted(
        {
            round(x, 4)
            for x in (
                1.0,
                2.0,
                5.0,
                10.0,
                15.0,
                20.0,
                0.05 * vmax,
                0.10 * vmax,
                0.20 * vmax,
                0.30 * vmax,
            )
            if x < 0.95 * vmax
        }
    )
    for vref in candidates:
        kr = dp_dv_local(v, dp, vref)
        rel = 100.0 * (kr - k0) / k0 if abs(k0) > 1e-12 else float("nan")
        rows.append(
            {
                "V_ref_uL": vref,
                "K_at_V0": k0,
                "K_at_Vref": kr,
                "relative_change_pct": rel,
            }
        )
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fit", type=Path, required=True)
    ap.add_argument("--material", choices=["ogden", "yeoh"], required=True)
    ap.add_argument("--ne", type=int, default=8)
    ap.add_argument("--p-final", type=float, default=80.0)
    ap.add_argument("--n-steps", type=int, default=24)
    ap.add_argument("--max-iter", type=int, default=12)
    ap.add_argument("--tol-mm", type=float, default=1e-3)
    ap.add_argument("--beta", type=float, default=0.7)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    work = args.out / "mulf_gee"
    work.mkdir(parents=True, exist_ok=True)

    model, params, p0 = load_model_params(args.fit, args.material)
    work_dir, mesh_name, x_obs, nsets = prepare_observed_mesh(
        R_MM, T_MM, args.ne, work, f"wp1.3-mulf-{args.material}"
    )

    mulf = mulf_iterate(
        x_obs,
        work_dir,
        mesh_name,
        nsets,
        t_mm=T_MM,
        model=model,
        params=params,
        p0_mmhg=p0,
        max_iter=args.max_iter,
        tol_mm=args.tol_mm,
        beta=args.beta,
    )

    rows, load_status = run_loading_curve(
        work_dir,
        mesh_name,
        model,
        params,
        p0,
        args.p_final,
        args.n_steps,
    )

    v = np.array([r["dV_uL"] for r in rows], dtype=float)
    dp = np.array([r["p_mmhg"] - p0 for r in rows], dtype=float)
    order = np.argsort(v)
    v, dp = v[order], dp[order]

    v_ref_default = min(10.0, float(v.max()) * 0.2) if v.max() > 1e-6 else 2.0
    k_v0 = dp_dv_local(v, dp, 0.0)
    k_ref = dp_dv_local(v, dp, v_ref_default)
    rel_pct = 100.0 * (k_ref - k_v0) / k_v0 if abs(k_v0) > 1e-12 else float("nan")
    sweep = v_ref_sweep(v, dp)

    result = {
        "material": args.material,
        "model": model,
        "params": params,
        "method": "Gee2010_MULF_fixed_point",
        "geometry": {
            "R_mm": R_MM,
            "t_mm": T_MM,
            "bc_mode": "symmetry_octant",
            "ne": args.ne,
            "X_obs": "mesh at R,t (in vivo shape at P0)",
        },
        "P0_mmHg": p0,
        "p_final_mmHg": args.p_final,
        "mulf": asdict(mulf),
        "mulf_iterations": [asdict(it) for it in mulf.iterations],
        "verify_error_mm": mulf.verify_error_mm,
        "loading_ccx": load_status,
        "V_ref_default_uL": v_ref_default,
        "K_local_at_V0_mmHg_per_uL": k_v0,
        "K_local_at_ref_mmHg_per_uL": k_ref,
        "relative_change_pct": rel_pct,
        "v_ref_sweep": sweep,
        "source_fit": str(args.fit),
        "pv_curve": [{"V_uL": float(vv), "dP_mmHg": float(pp)} for vv, pp in zip(v, dp)],
    }

    (args.out / "pretension_mulf_gee.json").write_text(json.dumps(result, indent=2))
    (args.out / "pv_mulf_gee.json").write_text(json.dumps(rows, indent=2))

    conv = "CONVERGED" if mulf.converged else "NOT CONVERGED"
    lines = [
        f"# wp1.3-{args.material} — pré-tensão (MULF Gee et al. 2010)\n",
        f"- **Model**: {model}",
        f"- **MULF**: {conv} em {mulf.n_iter} iterações (ΔX_ref final = {mulf.x_ref_delta_mm:.4e} mm)",
        f"- **Verificação** max‖X_pred − X_obs‖ = {mulf.verify_error_mm:.4e} mm",
        f"- **Geometria observada**: R={R_MM} mm, t={T_MM} mm, octant ne={args.ne}",
        f"- **Curva de carga**: partindo de X_ref* relaxado, P₀→{args.p_final} mmHg",
        f"- **dP/dV @ V≈0**: {k_v0:.4f} mmHg/µL",
        f"- **dP/dV @ V_ref={v_ref_default:.1f} µL**: {k_ref:.4f} mmHg/µL",
        f"- **Δ rel. (V_ref default)**: {rel_pct:+.2f}%",
        "",
        "## Sweep V_ref (robustez da métrica)",
        "",
        "| V_ref [µL] | K(V_ref) | Δ% vs K(V≈0) |",
        "|---:|---:|---:|",
    ]
    for row in sweep:
        lines.append(
            f"| {row['V_ref_uL']:.2f} | {row['K_at_Vref']:.4f} | {row['relative_change_pct']:+.2f}% |"
        )
    lines.extend(
        [
            "",
            "MULF: X_ref^(k+1) ← (1−β)X_ref^(k) + β(X_obs − u(P₀|X_ref^(k))); não confundir com deck two-step.",
        ]
    )
    (args.out / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0 if mulf.converged and mulf.verify_error_mm < 0.05 else 1


if __name__ == "__main__":
    raise SystemExit(main())
