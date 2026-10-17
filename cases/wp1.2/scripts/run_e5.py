#!/usr/bin/env python3
"""E5 — WP1.3 pretension slopes from dense Yeoh forward (post-E3)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
WP13 = HERE.parents[1] / "wp1.3"
sys.path.insert(0, str(HERE))

from fit_hyperelastic import dp_dv_local  # noqa: E402
from fit_pallikaris import DP_FEA_FINAL, P0_MMHG  # noqa: E402
from run_e3_e1b import PallikarisYeohForward  # noqa: E402


def slopes_from_curve(
    v: np.ndarray,
    p_abs: np.ndarray,
    p0: float,
) -> dict:
    """Local d(ΔP)/dV with ΔP = P_abs − P₀."""
    dp = p_abs - p0
    order = np.argsort(v)
    v, dp, p_abs = v[order], dp[order], p_abs[order]

    k_v0 = dp_dv_local(v, dp, 0.0)
    # Volume where |P_abs − P₀| is minimal after V>0 (first loaded increment)
    mask = v > 1e-6
    if mask.any():
        idx = int(np.argmin(np.abs(p_abs[mask] - p0)))
        v_near_p0 = float(v[mask][idx])
    else:
        v_near_p0 = float(v[1]) if len(v) > 1 else 0.0
    k_at_p0 = dp_dv_local(v, dp, v_near_p0)

    # Early-volume comparison (resolution-sensitive region)
    v_early = min(2.0, float(v.max()) * 0.05) if v.max() > 0 else 1.0
    k_early = dp_dv_local(v, dp, v_early)

    rel_pct = 100.0 * (k_at_p0 - k_v0) / k_v0 if abs(k_v0) > 1e-12 else float("nan")
    rel_early_pct = 100.0 * (k_early - k_v0) / k_v0 if abs(k_v0) > 1e-12 else float("nan")

    return {
        "n_points": int(len(v)),
        "V_at_P0_uL": v_near_p0,
        "V_early_uL": v_early,
        "K_local_at_V0_mmHg_per_uL": k_v0,
        "K_local_at_P0_mmHg_per_uL": k_at_p0,
        "K_local_at_V_early_mmHg_per_uL": k_early,
        "relative_change_V0_vs_P0_pct": rel_pct,
        "relative_change_V0_vs_early_pct": rel_early_pct,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--fit",
        type=Path,
        default=HERE.parent / "output_exploration" / "e3_yeoh" / "fit_results.json",
    )
    ap.add_argument("--ne", type=int, default=8)
    ap.add_argument("--n-steps-dense", type=int, default=40, help="≥25 per E5 plan")
    ap.add_argument("--n-steps-sparse", type=int, default=16, help="Baseline resolution")
    ap.add_argument("--out", type=Path, default=WP13 / "output_exploration")
    args = ap.parse_args()

    data = json.loads(args.fit.read_text())
    params = data["fit"]["params"]
    c10, c20 = params["C10_MPa"], params["C20_MPa"]

    args.out.mkdir(parents=True, exist_ok=True)
    work = args.out / "ccx_runs"
    forward = PallikarisYeohForward(work, ne=args.ne, p_final=DP_FEA_FINAL)

    # Override load steps via custom p_targets count
    def run_nsteps(n_steps: int, tag: str) -> tuple[np.ndarray, np.ndarray]:
        targets = [
            P0_MMHG + (DP_FEA_FINAL - P0_MMHG) * i / n_steps for i in range(1, n_steps + 1)
        ]
        from write_deck import write_deck  # noqa: E402

        deck = work / f"{tag}.inp"
        write_deck(
            deck,
            forward.mesh_path.name,
            forward.geom.t_mm,
            "yeoh2",
            {"C10_MPa": c10, "C20_MPa": c20},
            targets,
            label=f"E5 {tag} n={n_steps}",
            bc_mode="symmetry_octant",
            p0_mmhg=P0_MMHG,
        )
        from ccx_utils import run_ccx  # noqa: E402
        from extract_pv_curve import extract_pv  # noqa: E402

        frd = run_ccx(deck, clean=True)
        rows = extract_pv(deck, frd, forward.geom.R_mm, p0_mmhg=P0_MMHG)
        v = np.array([r["dV_uL"] for r in rows], dtype=float)
        p = np.array([r["p_mmhg"] for r in rows], dtype=float)
        return v, p

    print(f"=== E5 dense forward (Yeoh C10={c10:.4f}, C20={c20:.4f}) ===")
    v_dense, p_dense = run_nsteps(args.n_steps_dense, "dense")
    v_sparse, p_sparse = run_nsteps(args.n_steps_sparse, "sparse")

    dense = slopes_from_curve(v_dense, p_dense, P0_MMHG)
    sparse = slopes_from_curve(v_sparse, p_sparse, P0_MMHG)

    result = {
        "P0_mmHg": P0_MMHG,
        "material": {"model": "yeoh2", "C10_MPa": c10, "C20_MPa": c20},
        "source_fit": str(args.fit),
        "dense": dense,
        "sparse": sparse,
        "resolution_artifact_pct": (
            100.0
            * (sparse["relative_change_V0_vs_P0_pct"] - dense["relative_change_V0_vs_P0_pct"])
            / dense["relative_change_V0_vs_P0_pct"]
            if abs(dense["relative_change_V0_vs_P0_pct"]) > 1e-6
            else float("nan")
        ),
        "fea_curve_dense": [
            {"V_uL": float(v), "P_abs_mmHg": float(p)} for v, p in zip(v_dense, p_dense)
        ],
    }

    (args.out / "pretension_study.json").write_text(json.dumps(result, indent=2))

    d, s = dense, sparse
    lines = [
        "# E5 — wp1.3 pretension (Yeoh, dense FEA)\n",
        f"- **Material**: Yeoh-2 from E3 (C10={c10:.6e}, C20={c20:.6e} MPa)",
        f"- **P₀**: {P0_MMHG} mmHg",
        f"- **Dense steps**: {args.n_steps_dense} | **Sparse**: {args.n_steps_sparse}",
        "",
        "## Dense curve (≥25 points)",
        "",
        f"- **dP/dV @ V≈0**: {d['K_local_at_V0_mmHg_per_uL']:.6f} mmHg/µL",
        f"- **dP/dV @ V≈P₀** (V={d['V_at_P0_uL']:.4f} µL): {d['K_local_at_P0_mmHg_per_uL']:.6f} mmHg/µL",
        f"- **Relative change (V0 vs P₀)**: {d['relative_change_V0_vs_P0_pct']:+.4f}%",
        f"- **Relative change (V0 vs V={d['V_early_uL']:.2f} µL)**: {d['relative_change_V0_vs_early_pct']:+.4f}%",
        "",
        "## Sparse vs dense (resolution check)",
        "",
        f"- Sparse relative change: {s['relative_change_V0_vs_P0_pct']:+.4f}%",
        f"- Dense relative change: {d['relative_change_V0_vs_P0_pct']:+.4f}%",
        "",
        "Note: slope comparison on FEA P(V); MULF not implemented.",
    ]
    (args.out / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
