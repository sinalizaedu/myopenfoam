#!/usr/bin/env python3
"""WP1.2 — Yeoh-2 multi-start for literature targets (P_final=50).

Same setup as run_literature_matrix / fit_yeoh2:
  C10∈[1e-4, 5] MPa, C20∈[0.1, 10³] MPa via log10(C20), ne=8.
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

from fit_hyperelastic import ExpPoint, fit_quality  # noqa: E402
from fit_pallikaris import DP_FEA_FINAL, Geometry, P0_MMHG, pallikaris_pressure  # noqa: E402
from literature_targets import MAIN_TARGETS, V_MAX_SAFE, generate_target  # noqa: E402
from run_e3_e1b import PallikarisYeohForward  # noqa: E402
from run_ogden_multistart_matrix import generate_pallikaris_synthetic_v2  # noqa: E402
from yeoh_fit_bounds import decode_yeoh, yeoh_bounds  # noqa: E402

X0_CANDIDATES = [
    (0.612, np.log10(0.058)),
    (2.046, np.log10(4.993)),
    (2.949, np.log10(4.187)),
    (2.702, np.log10(0.1)),
    (1.020, np.log10(4.991)),
    (0.30, np.log10(0.1)),
    (1.50, np.log10(1.50)),
    (3.0, np.log10(0.1)),
    (0.05, np.log10(3.0)),
]

_, LO, HI = yeoh_bounds()
TOL_C10 = 0.35
TOL_C20 = 0.35


def fit_one_start(
    forward: PallikarisYeohForward,
    exp: list[ExpPoint],
    x0: tuple[float, float],
    max_nfev: int,
    start_id: int,
) -> dict:
    v_exp = np.array([e.V_uL for e in exp])
    p_exp = np.array([e.P_mmHg for e in exp])
    n_eval = {"n": 0}

    def residuals(x: np.ndarray) -> np.ndarray:
        n_eval["n"] += 1
        tag = f"s{start_id:02d}_opt_{n_eval['n']:03d}"
        c10, c20 = decode_yeoh(x)
        try:
            v_fea, p_fea = forward.run(c10, c20, tag=tag)
        except Exception:
            return np.ones_like(p_exp) * 1e3
        order = np.argsort(v_fea)
        v_fea, p_fea = v_fea[order], p_fea[order]
        if v_fea.max() < v_exp.max() * 0.9:
            return np.ones_like(p_exp) * 50.0
        dp_fea = p_fea - P0_MMHG
        dp_pred = np.interp(v_exp, v_fea, dp_fea)
        return dp_pred - p_exp

    t0 = time.time()
    res = least_squares(
        residuals,
        np.array(x0),
        bounds=(LO, HI),
        max_nfev=max_nfev,
        ftol=1e-8,
        xtol=1e-8,
        diff_step=0.02,
        x_scale="jac",
        verbose=0,
    )
    fit_time = time.time() - t0
    c10, c20 = decode_yeoh(res.x)
    v_fea, p_fea = forward.run(c10, c20, tag=f"s{start_id:02d}_final")
    order = np.argsort(v_fea)
    v_fea, p_fea = v_fea[order], p_fea[order]
    dp_fea = p_fea - P0_MMHG
    dp_at_exp = np.interp(v_exp, v_fea, dp_fea)
    quality = fit_quality(p_exp, dp_at_exp)

    return {
        "start": start_id,
        "x0": list(x0),
        "C10_final": c10,
        "C20_final": c20,
        "R2": quality["R2"],
        "max_residual_mmHg": quality["max_residual_mmHg"],
        "cost": float(res.cost),
        "nfev": int(res.nfev),
        "success": bool(res.success),
        "message": res.message,
        "C10_at_lo_bound": bool(c10 <= LO[0] * 1.01 + 1e-6),
        "C10_at_hi_bound": bool(c10 >= HI[0] - 0.02),
        "C20_at_lo_bound": bool(res.x[1] <= LO[1] + 0.02),
        "C20_at_hi_bound": bool(res.x[1] >= HI[1] - 0.02),
        "fit_time_s": fit_time,
    }


def cluster(results: list[dict]) -> list[list[int]]:
    clusters: list[list[int]] = []
    for i, r in enumerate(results):
        if not np.isfinite(r.get("cost", np.inf)):
            continue
        placed = False
        for c in clusters:
            j = c[0]
            rj = results[j]
            if abs(r["C10_final"] - rj["C10_final"]) < TOL_C10 and abs(r["C20_final"] - rj["C20_final"]) < TOL_C20:
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

    forward = PallikarisYeohForward(out / "ccx_runs" / "mesh", ne=ne, p_final=p_final)
    forward.geom = Geometry(R_mm=12.0, t_mm=0.5, source=f"{target}_yeoh_ms")

    all_results: list[dict] = []
    for i, x0 in enumerate(X0_CANDIDATES, start=1):
        work = out / "ccx_runs" / f"start_{i:02d}"
        forward.work_dir = work
        forward._write_mesh()
        print(f"\n=== {target} yeoh start {i}/{len(X0_CANDIDATES)} x0={x0} ===", flush=True)
        try:
            all_results.append(fit_one_start(forward, exp, x0, max_nfev, i))
            r = all_results[-1]
            print(
                f"  -> C10={r['C10_final']:.3f} C20={r['C20_final']:.3f} "
                f"R2={r['R2']:.4f} cost={r['cost']:.2f}",
                flush=True,
            )
        except Exception as exc:
            all_results.append({"start": i, "x0": list(x0), "error": str(exc), "cost": float("inf")})
            print(f"  -> FAILED: {exc}", flush=True)

    valid = [r for r in all_results if np.isfinite(r.get("cost", np.inf))]
    valid_sorted = sorted(valid, key=lambda r: r["cost"])
    clusters = cluster(all_results)
    payload = {
        "target": target,
        "material": "yeoh2",
        "v_max_uL": v_max,
        "fea_ramp": {"P_final_mmHg_abs": p_final, "P0_mmHg": P0_MMHG},
        "mesh": {"ne": ne, "bc_mode": "symmetry_octant"},
        "optimizer_setup": {
            "bounds": {
                "C10_MPa": [float(LO[0]), float(HI[0])],
                "C20_MPa": [float(10 ** LO[1]), float(10 ** HI[1])],
                "log10_C20": [float(LO[1]), float(HI[1])],
            },
            "x0_candidates": [list(x) for x in X0_CANDIDATES],
            "max_nfev": max_nfev,
        },
        "all_results": all_results,
        "ranked_by_cost": valid_sorted,
        "n_clusters": len(clusters),
        "clusters": [
            {
                "id": ci,
                "members": members,
                "best": min(
                    (all_results[m] for m in members if np.isfinite(all_results[m].get("cost", np.inf))),
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
    ss = {
        "pallikaris": (2.046, 4.993, 0.933),
        "silver": (2.949, 4.187, 0.975),
        "agra": (2.702, -3.671, 0.925),
        "friedenwald": (1.020, 4.991, 0.970),
    }
    lines = [
        "# WP1.2 Yeoh multi-start (P_final=50)\n",
        "| target | clusters | best C10 | best C20 | best R² | single-start C10 | single-start C20 | match? |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for p in payloads:
        b = p.get("global_best")
        if not b:
            lines.append(f"| {p['target']} | {p['n_clusters']} | — | — | — | — | — | failed |")
            continue
        s = ss.get(p["target"], (float("nan"), float("nan"), float("nan")))
        match = abs(b["C10_final"] - s[0]) < TOL_C10 and abs(b["C20_final"] - s[1]) < TOL_C20
        lines.append(
            f"| {p['target']} | {p['n_clusters']} | {b['C10_final']:.3f} | {b['C20_final']:.3f} "
            f"| {b['R2']:.4f} | {s[0]:.3f} | {s[1]:.3f} | {'sim' if match else '**NAO**'} |"
        )
    (out_root / "MULTISTART_SUMMARY.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines), flush=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--targets", default=",".join(MAIN_TARGETS))
    ap.add_argument("--p-final", type=float, default=DP_FEA_FINAL)
    ap.add_argument("--ne", type=int, default=8)
    ap.add_argument("--max-nfev", type=int, default=30)
    ap.add_argument("--pallikaris-mode", default="digitized", choices=("v2_synthetic", "digitized"))
    ap.add_argument("--out", type=Path, default=WP12 / "output_caveats_p50" / "yeoh_multistart")
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
