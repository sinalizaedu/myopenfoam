#!/usr/bin/env python3
"""WP1.3 — pretension (legacy two-step deck; prefer run_wp13_backward_displacement.py)."""
from __future__ import annotations

import argparse
import json
import sys
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
from gen_sphere_shell_mesh import write_mesh  # noqa: E402
from write_deck_mulf import write_deck_mulf  # noqa: E402

R_MM, T_MM = 12.0, 0.5
P0_DEFAULT = 16.9


def load_model_params(fit: Path, material: str) -> tuple[str, dict, float]:
    data = json.loads(fit.read_text())
    sel = data.get("selected") or data.get("fit")
    model = sel.get("model", material)
    params = dict(sel["params"])
    p0 = float(data.get("pallikaris", {}).get("P0_mmHg", P0_DEFAULT))
    if model.startswith("ogden") or material == "ogden":
        deck_model = "ogden1"
        deck_params = {
            "mu1_MPa": params["mu1_MPa"],
            "alpha1": params["alpha1"],
            "D1": params.get("D1", d1_from_ogden_mu1(params["mu1_MPa"])),
            "d1_tied_mu1": params.get("d1_tied_mu1", True),
        }
    else:
        deck_model = "yeoh2"
        deck_params = {
            "C10_MPa": params["C10_MPa"],
            "C20_MPa": params["C20_MPa"],
        }
    return deck_model, deck_params, p0


def verify_ccx_converged(log_path: Path) -> tuple[bool, str]:
    if not log_path.is_file():
        return False, f"missing log {log_path}"
    text = log_path.read_text(errors="replace")
    if "***ERROR" in text or "*** error" in text.lower():
        return False, "CalculiX ERROR in log"
    if "SOLUTION IS NOT CONVERGED" in text.upper():
        return False, "solution not converged"
    ok_markers = ("THE ANALYSIS HAS BEEN COMPLETED", "JOB FINISHED")
    if not any(m in text.upper() for m in ok_markers):
        return False, "analysis did not complete"
    return True, "OK"


def run_mulf_forward(
    model: str,
    params: dict,
    *,
    ne: int,
    p0: float,
    p_final: float,
    n_steps: int,
    work: Path,
    tag: str,
) -> tuple[list[dict], dict]:
    work.mkdir(parents=True, exist_ok=True)
    mesh = work / "mesh.inp"
    write_mesh(
        mesh,
        R_MM,
        T_MM,
        ne,
        2,
        tag,
        bc_mode="symmetry_octant",
        mesh_kind="spherical",
        theta_min_deg=3.0,
        reduced=True,
    )
    deck = work / "mulf.inp"
    write_deck_mulf(
        deck,
        mesh.name,
        T_MM,
        model,
        params,
        p0_mmhg=p0,
        p_final_mmhg=p_final,
        n_load_steps=n_steps,
        label=f"wp1.3 MULF {tag}",
        bc_mode="symmetry_octant",
    )
    frd = run_ccx(deck, clean=True)
    log = work / "log_mulf.txt"
    ok, msg = verify_ccx_converged(log)
    if not ok:
        raise RuntimeError(f"CCX failed ({tag}): {msg}")
    rows = extract_pv(deck, frd, R_MM, p0_mmhg=p0)
    return rows, {"status": msg, "n_points": len(rows), "log": str(log)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fit", type=Path, required=True)
    ap.add_argument("--material", choices=["ogden", "yeoh"], required=True)
    ap.add_argument("--ne", type=int, default=8)
    ap.add_argument("--p-final", type=float, default=80.0)
    ap.add_argument("--n-steps", type=int, default=24)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    model, params, p0 = load_model_params(args.fit, args.material)

    rows, run_meta = run_mulf_forward(
        model,
        params,
        ne=args.ne,
        p0=p0,
        p_final=args.p_final,
        n_steps=args.n_steps,
        work=args.out / "ccx",
        tag=args.material,
    )

    v = np.array([r["dV_uL"] for r in rows], dtype=float)
    dp = np.array([r["p_mmhg"] - p0 for r in rows], dtype=float)
    order = np.argsort(v)
    v, dp = v[order], dp[order]

    v_ref = min(10.0, float(v.max()) * 0.2) if v.max() > 1e-6 else 2.0
    k_v0 = dp_dv_local(v, dp, 0.0)
    k_ref = dp_dv_local(v, dp, v_ref)
    rel_pct = 100.0 * (k_ref - k_v0) / k_v0 if abs(k_v0) > 1e-12 else float("nan")

    result = {
        "material": args.material,
        "model": model,
        "params": params,
        "method": "legacy_two_step_not_backward_displacement",
        "geometry": {
            "R_mm": R_MM,
            "t_mm": T_MM,
            "bc_mode": "symmetry_octant",
            "ne": args.ne,
        },
        "P0_mmHg": p0,
        "p_final_mmHg": args.p_final,
        "V_ref_uL": v_ref,
        "K_local_at_V0_mmHg_per_uL": k_v0,
        "K_local_at_ref_mmHg_per_uL": k_ref,
        "relative_change_pct": rel_pct,
        "ccx": run_meta,
        "source_fit": str(args.fit),
        "pv_curve": [{"V_uL": float(vv), "dP_mmHg": float(pp)} for vv, pp in zip(v, dp)],
    }

    (args.out / "pretension_backward_displacement_legacy_two_step.json").write_text(
        json.dumps(result, indent=2)
    )
    (args.out / "pv_backward_displacement_legacy.json").write_text(json.dumps(rows, indent=2))

    lines = [
        f"# wp1.3-{args.material} — pretension (MULF)\n",
        f"- **Model**: {model}",
        f"- **Params**: {json.dumps(params)}",
        f"- **Geometry**: R={R_MM} mm, t={T_MM} mm, octant ne={args.ne}",
        f"- **Method**: two-step NLGEOM (prestress to P₀, then incremental load)",
        f"- **P₀**: {p0} mmHg → P_final={args.p_final} mmHg",
        f"- **V ref**: {v_ref:.3f} µL",
        f"- **dP/dV @ V≈0 (MULF)**: {k_v0:.4f} mmHg/µL",
        f"- **dP/dV @ V ref (MULF)**: {k_ref:.4f} mmHg/µL",
        f"- **Relative change**: {rel_pct:+.2f}%",
        f"- **CCX**: {run_meta['status']} ({run_meta['n_points']} P(V) points)",
    ]
    (args.out / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
