#!/usr/bin/env python3
"""WP1.2 — Ogden N=1 multi-start, D1 livre, literature targets, P_final=50.

Tests ressalva #2: whether freeing D1 reopens multiple local minima (as at P80).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

HERE = Path(__file__).resolve().parent
WP12 = HERE.parent
sys.path.insert(0, str(HERE))

from ccx_utils import run_ccx  # noqa: E402
from extract_pv_curve import extract_pv  # noqa: E402
from fit_hyperelastic import ExpPoint, fit_quality  # noqa: E402
from fit_pallikaris import DP_FEA_FINAL, Geometry, P0_MMHG, PallikarisForward  # noqa: E402
from literature_targets import MAIN_TARGETS, V_MAX_SAFE, generate_target  # noqa: E402
from run_ogden_multistart_matrix import generate_pallikaris_synthetic_v2  # noqa: E402
from write_deck import write_deck  # noqa: E402

X0_CANDIDATES = [
    (2.14, 1.77, np.log10(0.238446)),
    (7.16, 0.50, np.log10(0.0713)),
    (4.24, 0.50, np.log10(0.1202)),
    (5.44, 0.49, np.log10(2.26e-4)),
    (3.00, 0.90, np.log10(0.05)),
    (1.50, 0.35, -6.0),
    (9.00, 1.50, np.log10(0.02)),
]

LO = np.array([0.15, 0.15, -8.0])
HI = np.array([12.0, 3.5, 0.0])
TOL_MU1 = 0.5
TOL_ALPHA1 = 0.08
TOL_LOGD1 = 1.0


def forward_run_with_d1(forward: PallikarisForward, mu1: float, alpha1: float, d1: float, tag: str):
    params = {"mu1_MPa": mu1, "alpha1": alpha1, "d1_tied_mu1": False, "D1": d1}
    deck = forward.work_dir / f"{tag}.inp"
    write_deck(
        deck,
        forward.mesh_path.name,
        forward.geom.t_mm,
        "ogden1",
        params,
        forward._p_targets(),
        label=f"d1free ms {tag}",
        nu=forward.geom.nu,
        E_mpa=forward.geom.E_mpa,
        bc_mode="symmetry_octant",
        p0_mmhg=forward.p0_mmhg,
    )
    frd = run_ccx(deck, clean=True)
    rows = extract_pv(deck, frd, forward.geom.R_mm, p0_mmhg=forward.p0_mmhg)
    v = np.array([r["dV_uL"] for r in rows], dtype=float)
    p = np.array([r["p_mmhg"] for r in rows], dtype=float)
    return v, p


def fit_one_start(
    forward: PallikarisForward,
    exp: list[ExpPoint],
    x0: tuple[float, float, float],
    max_nfev: int,
    start_id: int,
) -> dict:
    v_exp = np.array([e.V_uL for e in exp])
    p_exp = np.array([e.P_mmHg for e in exp])
    n_eval = {"n": 0}

    def residuals(x: np.ndarray) -> np.ndarray:
        n_eval["n"] += 1
        mu1, alpha1, log_d1 = float(x[0]), float(x[1]), float(x[2])
        d1 = 10.0 ** log_d1
        tag = f"s{start_id:02d}_opt_{n_eval['n']:03d}"
        try:
            v_fea, p_fea = forward_run_with_d1(forward, mu1, alpha1, d1, tag)
        except Exception:
            return np.ones_like(p_exp) * 200.0
        order = np.argsort(v_fea)
        v_fea, p_fea = v_fea[order], p_fea[order]
        if v_fea.size == 0 or v_fea.max() < v_exp.max() * 0.9:
            return np.ones_like(p_exp) * 50.0
        dp_fea = p_fea - forward.p0_mmhg
        dp_pred = np.interp(v_exp, v_fea, dp_fea)
        return dp_pred - p_exp

    t0 = time.time()
    res = least_squares(
        residuals,
        np.array(x0),
        bounds=(LO, HI),
        max_nfev=max_nfev,
        ftol=1e-9,
        xtol=1e-9,
        diff_step=0.01,
        x_scale=[3.0, 0.5, 2.0],
        verbose=0,
    )
    fit_time = time.time() - t0
    mu1, alpha1, log_d1 = float(res.x[0]), float(res.x[1]), float(res.x[2])
    d1 = 10.0 ** log_d1
    v_fea, p_fea = forward_run_with_d1(forward, mu1, alpha1, d1, f"s{start_id:02d}_final")
    order = np.argsort(v_fea)
    v_fea, p_fea = v_fea[order], p_fea[order]
    dp_fea = p_fea - forward.p0_mmhg
    dp_at_exp = np.interp(v_exp, v_fea, dp_fea)
    quality = fit_quality(p_exp, dp_at_exp)

    return {
        "start": start_id,
        "x0": [float(x0[0]), float(x0[1]), float(x0[2])],
        "mu1_final": mu1,
        "alpha1_final": alpha1,
        "D1_final": d1,
        "R2": quality["R2"],
        "max_residual_mmHg": quality["max_residual_mmHg"],
        "cost": float(res.cost),
        "nfev": int(res.nfev),
        "success": bool(res.success),
        "message": res.message,
        "fit_time_s": fit_time,
    }


def cluster(results: list[dict]) -> list[list[int]]:
    clusters: list[list[int]] = []
    for i, r in enumerate(results):
        if not np.isfinite(r.get("cost", np.inf)) or r.get("R2", -999) < 0.5:
            continue
        placed = False
        for c in clusters:
            j = c[0]
            rj = results[j]
            if (
                abs(r["mu1_final"] - rj["mu1_final"]) < TOL_MU1
                and abs(r["alpha1_final"] - rj["alpha1_final"]) < TOL_ALPHA1
                and abs(np.log10(max(r["D1_final"], 1e-12)) - np.log10(max(rj["D1_final"], 1e-12))) < TOL_LOGD1
            ):
                c.append(i)
                placed = True
                break
        if not placed:
            clusters.append([i])
    return clusters


def run_target(
    target: str,
    out: Path,
    *,
    ne: int,
    max_nfev: int,
    p_final: float,
    pallikaris_mode: str,
) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    csv_path = out / f"{target}_target.csv"
    v_max = V_MAX_SAFE.get(target, 50.0)
    if target == "pallikaris" and pallikaris_mode == "v2_synthetic":
        exp = generate_pallikaris_synthetic_v2(csv_path, v_max=50.0, n_pts=11)
        v_max = 50.0
    else:
        exp = generate_target(target, csv_path, v_max=v_max)

    geom = Geometry(R_mm=12.0, t_mm=0.5, source=f"{target}_d1free_ms")
    all_results: list[dict] = []
    for i, x0 in enumerate(X0_CANDIDATES, start=1):
        work = out / "ccx_runs" / f"start_{i:02d}"
        forward = PallikarisForward(geom, work, ne=ne, dp_fea_final=p_final)
        print(f"\n=== {target} D1-free start {i}/{len(X0_CANDIDATES)} ===", flush=True)
        try:
            all_results.append(fit_one_start(forward, exp, x0, max_nfev, i))
            r = all_results[-1]
            print(
                f"  -> mu1={r['mu1_final']:.3f} a1={r['alpha1_final']:.3f} D1={r['D1_final']:.2e} "
                f"R2={r['R2']:.4f} cost={r['cost']:.2f}",
                flush=True,
            )
        except Exception as exc:
            all_results.append({"start": i, "x0": list(x0), "error": str(exc), "cost": float("inf")})
            print(f"  -> FAILED: {exc}", flush=True)

    valid = [r for r in all_results if np.isfinite(r.get("cost", np.inf)) and r.get("R2", -1) > 0.5]
    valid_sorted = sorted(valid, key=lambda r: r["cost"])
    clusters = cluster(all_results)
    payload = {
        "target": target,
        "material": "ogden1_d1_free",
        "v_max_uL": v_max,
        "geometry": asdict(geom),
        "fea_ramp": {"P_final_mmHg_abs": p_final, "P0_mmHg": P0_MMHG},
        "mesh": {"ne": ne},
        "optimizer_setup": {
            "d1_tied_mu1": False,
            "bounds": {"mu1": [LO[0], HI[0]], "alpha1": [LO[1], HI[1]], "log10_D1": [LO[2], HI[2]]},
            "x0_candidates": [[float(a), float(b), float(c)] for a, b, c in X0_CANDIDATES],
            "max_nfev": max_nfev,
        },
        "all_results": all_results,
        "ranked_by_cost": valid_sorted,
        "n_good_clusters": len(clusters),
        "clusters": [
            {
                "id": ci,
                "members": members,
                "best": min(
                    (all_results[m] for m in members),
                    key=lambda r: r["cost"],
                ),
            }
            for ci, members in enumerate(clusters, start=1)
        ],
    }
    if valid_sorted:
        payload["global_best"] = valid_sorted[0]
    (out / "multistart_results.json").write_text(json.dumps(payload, indent=2))
    return payload


def write_summary(out_root: Path, payloads: list[dict]) -> None:
    lines = [
        "# Ogden multi-start P50, D1 livre\n",
        "| target | good clusters (R²>0.5) | best mu1 | best α1 | best D1 | best R² | best cost |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for p in payloads:
        b = p.get("global_best")
        if not b:
            lines.append(f"| {p['target']} | 0 | — | — | — | — | — |")
            continue
        lines.append(
            f"| {p['target']} | {p['n_good_clusters']} | {b['mu1_final']:.3f} | {b['alpha1_final']:.3f} "
            f"| {b['D1_final']:.2e} | {b['R2']:.4f} | {b['cost']:.2f} |"
        )
    (out_root / "MULTISTART_SUMMARY.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines), flush=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--targets", default=",".join(MAIN_TARGETS))
    ap.add_argument("--p-final", type=float, default=DP_FEA_FINAL)
    ap.add_argument("--ne", type=int, default=8)
    ap.add_argument("--max-nfev", type=int, default=40)
    ap.add_argument("--pallikaris-mode", default="digitized", choices=("v2_synthetic", "digitized"))
    ap.add_argument("--out", type=Path, default=WP12 / "output_caveats_p50" / "ogden_d1free_multistart")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    targets = [t.strip() for t in args.targets.split(",") if t.strip()]
    payloads = [
        run_target(t, args.out / t, ne=args.ne, max_nfev=args.max_nfev, p_final=args.p_final, pallikaris_mode=args.pallikaris_mode)
        for t in targets
    ]
    write_summary(args.out, payloads)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
