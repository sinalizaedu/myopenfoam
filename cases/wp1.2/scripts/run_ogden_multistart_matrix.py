#!/usr/bin/env python3
"""WP1.2 — Ogden N=1 multi-start for literature targets (P_final=50).

Mirrors the single-start setup in run_literature_matrix / fit_ogden1:
  - D1 tied to mu1
  - bounds mu1∈[0.05, 15], alpha1∈[0.5, 100] (default; override via CLI)
  - ne=8, symmetry octant

Tests whether the 4 Ogden single-start fits from output_literature_p50_v2
land in distinct local minima or share a global basin.
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

from ccx_utils import d1_from_ogden_mu1  # noqa: E402
from fit_hyperelastic import ExpPoint, fit_quality  # noqa: E402
from fit_pallikaris import (  # noqa: E402
    DP_FEA_FINAL,
    Geometry,
    P0_MMHG,
    PallikarisForward,
    pallikaris_pressure,
)
from literature_targets import MAIN_TARGETS, V_MAX_SAFE, generate_target  # noqa: E402


def generate_pallikaris_synthetic_v2(
    path: Path,
    *,
    v_max: float = 50.0,
    n_pts: int = 11,
    p0: float = P0_MMHG,
) -> list[ExpPoint]:
    """Same target as output_literature_p50_v2 (re-anchored formula, linspace)."""
    import csv

    path.parent.mkdir(parents=True, exist_ok=True)
    rows: list[ExpPoint] = []
    for v in np.linspace(0.0, v_max, n_pts):
        p_abs = pallikaris_pressure(float(v), p0_user=p0)
        rows.append(ExpPoint(V_uL=float(v), P_mmHg=float(p_abs - p0)))
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["V_uL", "P_mmHg", "eye_id"])
        for row in rows:
            w.writerow([f"{row.V_uL:.4f}", f"{row.P_mmHg:.4f}", "pallikaris_reanchored"])
    return rows

# (mu1, alpha1) — covers default x0, P80 minima, P50 single-start results, and spread
X0_CANDIDATES = [
    (2.14, 1.77),   # default single-start x0
    (7.16, 0.50),   # P80 bound-limited basin
    (4.24, 0.50),   # pallikaris P50 single-start
    (2.27, 1.06),   # friedenwald P50 single-start (caixa estreita, legado)
    (1.925, 10.38), # friedenwald P50 matriz principal (alpha ampliado)
    (5.50, 0.50),   # silver P50 single-start
    (5.19, 5.99),   # agra P50 single-start (near upper alpha bound)
    (1.00, 2.50),   # coverage: low mu1, high alpha
    (4.00, 1.00),   # coverage: mid-range
    (9.00, 0.60),   # coverage: high mu1
]

X0_WIDE_ALPHA_EXTRA = [
    (1.50, 0.55),
    (5.44, 0.60),
    (2.14, 0.55),
    (5.19, 7.50),
    (3.00, 8.00),
]


def x0_candidates_for_bounds(lo: np.ndarray, hi: np.ndarray) -> list[tuple[float, float]]:
    xs = list(X0_CANDIDATES)
    if lo[1] < 0.49 or hi[1] > 6.01:
        xs.extend(X0_WIDE_ALPHA_EXTRA)
    # dedupe rough
    seen: set[tuple[float, float]] = set()
    out: list[tuple[float, float]] = []
    for x in xs:
        if not (lo[0] <= x[0] <= hi[0] and lo[1] <= x[1] <= hi[1]):
            continue
        key = (round(x[0], 2), round(x[1], 2))
        if key not in seen:
            seen.add(key)
            out.append(x)
    return out

LO = np.array([0.05, 0.5])
HI = np.array([15.0, 100.0])  # alinhado a fit_ogden1 / matriz principal
TOL_MU1 = 0.4
TOL_ALPHA1 = 0.08


def fit_one_start(
    forward: PallikarisForward,
    exp: list[ExpPoint],
    x0: tuple[float, float],
    max_nfev: int,
    start_id: int,
    *,
    lo: np.ndarray | None = None,
    hi: np.ndarray | None = None,
) -> dict:
    lo_use = LO if lo is None else lo
    hi_use = HI if hi is None else hi
    v_exp = np.array([e.V_uL for e in exp])
    p_exp = np.array([e.P_mmHg for e in exp])
    n_eval = {"n": 0}

    def residuals(x: np.ndarray) -> np.ndarray:
        n_eval["n"] += 1
        tag = f"s{start_id:02d}_opt_{n_eval['n']:03d}"
        v_fea, p_fea = forward.run(float(x[0]), float(x[1]), tag=tag)
        order = np.argsort(v_fea)
        v_fea, p_fea = v_fea[order], p_fea[order]
        if v_fea.max() < v_exp.max() * 0.9:
            return np.ones_like(p_exp) * 50.0
        dp_fea = p_fea - forward.p0_mmhg
        dp_pred = np.interp(v_exp, v_fea, dp_fea)
        return dp_pred - p_exp

    t0 = time.time()
    res = least_squares(
        residuals,
        np.array(x0),
        bounds=(lo_use, hi_use),
        max_nfev=max_nfev,
        ftol=1e-8,
        xtol=1e-8,
        diff_step=0.02,
        x_scale="jac",
        verbose=0,
    )
    fit_time = time.time() - t0
    mu1, alpha1 = float(res.x[0]), float(res.x[1])
    v_fea, p_fea = forward.run(mu1, alpha1, tag=f"s{start_id:02d}_final")
    order = np.argsort(v_fea)
    v_fea, p_fea = v_fea[order], p_fea[order]
    dp_fea = p_fea - forward.p0_mmhg
    dp_at_exp = np.interp(v_exp, v_fea, dp_fea)
    quality = fit_quality(p_exp, dp_at_exp)
    at_lo_alpha = alpha1 <= lo_use[1] + 0.02
    at_hi_alpha = alpha1 >= hi_use[1] - 0.02

    return {
        "start": start_id,
        "x0": list(x0),
        "mu1_final": mu1,
        "alpha1_final": alpha1,
        "D1_final": d1_from_ogden_mu1(mu1),
        "R2": quality["R2"],
        "max_residual_mmHg": quality["max_residual_mmHg"],
        "cost": float(res.cost),
        "nfev": int(res.nfev),
        "success": bool(res.success),
        "message": res.message,
        "alpha1_at_lo_bound": bool(at_lo_alpha),
        "alpha1_at_hi_bound": bool(at_hi_alpha),
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
            if (
                abs(r["mu1_final"] - rj["mu1_final"]) < TOL_MU1
                and abs(r["alpha1_final"] - rj["alpha1_final"]) < TOL_ALPHA1
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
    R: float,
    t: float,
    pallikaris_mode: str = "v2_synthetic",
    lo: np.ndarray | None = None,
    hi: np.ndarray | None = None,
) -> dict:
    lo_use = LO if lo is None else lo
    hi_use = HI if hi is None else hi
    out.mkdir(parents=True, exist_ok=True)
    csv_path = out / f"{target}_target.csv"
    v_max = V_MAX_SAFE.get(target, 50.0)
    if target == "pallikaris" and pallikaris_mode == "v2_synthetic":
        exp = generate_pallikaris_synthetic_v2(csv_path, v_max=50.0, n_pts=11)
        v_max = 50.0
    else:
        exp = generate_target(target, csv_path, v_max=v_max)

    geom = Geometry(R_mm=R, t_mm=t, source=f"{target}_multistart")
    all_results: list[dict] = []

    x0_list = x0_candidates_for_bounds(lo_use, hi_use)
    for i, x0 in enumerate(x0_list, start=1):
        work = out / "ccx_runs" / f"start_{i:02d}"
        forward = PallikarisForward(geom, work, ne=ne, dp_fea_final=p_final)
        print(f"\n=== {target} start {i}/{len(x0_list)} x0={x0} ===", flush=True)
        try:
            all_results.append(
                fit_one_start(forward, exp, x0, max_nfev, i, lo=lo_use, hi=hi_use)
            )
            r = all_results[-1]
            print(
                f"  -> mu1={r['mu1_final']:.3f} alpha1={r['alpha1_final']:.3f} "
                f"R2={r['R2']:.4f} cost={r['cost']:.2f} nfev={r['nfev']}",
                flush=True,
            )
        except Exception as exc:
            all_results.append(
                {
                    "start": i,
                    "x0": list(x0),
                    "error": str(exc),
                    "cost": float("inf"),
                }
            )
            print(f"  -> FAILED: {exc}", flush=True)

    valid = [r for r in all_results if np.isfinite(r.get("cost", np.inf))]
    valid_sorted = sorted(valid, key=lambda r: r["cost"])
    clusters = cluster(all_results)

    payload = {
        "target": target,
        "material": "ogden",
        "v_max_uL": v_max,
        "geometry": asdict(geom),
        "fea_ramp": {"P_final_mmHg_abs": p_final, "P0_mmHg": P0_MMHG},
        "mesh": {"ne": ne, "bc_mode": "symmetry_octant"},
        "optimizer_setup": {
            "d1_tied_mu1": True,
            "bounds": {"mu1": [float(lo_use[0]), float(hi_use[0])], "alpha1": [float(lo_use[1]), float(hi_use[1])]},
            "x0_candidates": [list(x) for x in x0_list],
            "max_nfev": max_nfev,
            "pallikaris_mode": pallikaris_mode if target == "pallikaris" else None,
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
        best = valid_sorted[0]
        payload["global_best"] = best

    (out / "multistart_results.json").write_text(json.dumps(payload, indent=2))
    return payload


def write_summary(out_root: Path, payloads: list[dict]) -> None:
    lines = [
        "# WP1.2 Ogden multi-start (P_final=50, D1 tied)\n",
        "Mesmo setup do single-start em `output_literature_p50_v2`: "
        "D1 amarrado a mu1; bounds por corrida (ver optimizer_setup em multistart_results.json), ne=8.\n",
        f"**{len(X0_CANDIDATES)} pontos de partida** por alvo.\n",
        "## Resumo por alvo\n",
        "| target | clusters | best mu1 | best alpha1 | best R² | best cost | single-start mu1 | single-start alpha1 | single-start R² | global? |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]

    single_start_map = {
        "pallikaris": (4.243, 0.500, 0.934),
        "friedenwald": (1.925, 10.385, 0.987),
        "silver": (5.502, 0.500, 0.976),
        "agra": (5.185, 5.999, 0.938),
    }

    for p in payloads:
        target = p["target"]
        n_cl = p["n_clusters"]
        if p.get("global_best"):
            b = p["global_best"]
            ss = single_start_map.get(target, (float("nan"), float("nan"), float("nan")))
            same_basin = (
                abs(b["mu1_final"] - ss[0]) < TOL_MU1
                and abs(b["alpha1_final"] - ss[1]) < TOL_ALPHA1
            )
            global_note = "sim (single-start = global)" if same_basin else "**NAO** (single-start subotimo)"
            lines.append(
                f"| {target} | {n_cl} | {b['mu1_final']:.3f} | {b['alpha1_final']:.3f} "
                f"| {b['R2']:.4f} | {b['cost']:.2f} "
                f"| {ss[0]:.3f} | {ss[1]:.3f} | {ss[2]:.4f} | {global_note} |"
            )
        else:
            lines.append(f"| {target} | {n_cl} | — | — | — | — | — | — | — | all failed |")

    lines.append("\n## Clusters por alvo\n")
    for p in payloads:
        lines.append(f"### {p['target']}\n")
        for c in p.get("clusters", []):
            b = c["best"]
            lines.append(
                f"- **C{c['id']}** ({len(c['members'])} start(s)): "
                f"mu1={b['mu1_final']:.3f}, alpha1={b['alpha1_final']:.3f}, "
                f"R²={b['R2']:.4f}, cost={b['cost']:.2f}"
            )
        lines.append("")

    (out_root / "MULTISTART_SUMMARY.md").write_text("\n".join(lines))
    print("\n" + "\n".join(lines), flush=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--targets", default=",".join(MAIN_TARGETS))
    ap.add_argument("--p-final", type=float, default=DP_FEA_FINAL)
    ap.add_argument("--ne", type=int, default=8)
    ap.add_argument("--max-nfev", type=int, default=30)
    ap.add_argument("--R", type=float, default=12.0)
    ap.add_argument("--t", type=float, default=0.5)
    ap.add_argument("--out", type=Path, default=WP12 / "output_ogden_multistart_p50")
    ap.add_argument(
        "--pallikaris-mode",
        choices=("v2_synthetic", "digitized"),
        default="digitized",
        help="pallikaris: digitized (matriz principal) or v2_synthetic (grade 0–50 µL, legado)",
    )
    ap.add_argument("--alpha-lo", type=float, default=LO[1])
    ap.add_argument("--alpha-hi", type=float, default=HI[1])
    ap.add_argument("--mu1-lo", type=float, default=LO[0])
    ap.add_argument("--mu1-hi", type=float, default=HI[0])
    args = ap.parse_args()
    lo_bounds = np.array([args.mu1_lo, args.alpha_lo])
    hi_bounds = np.array([args.mu1_hi, args.alpha_hi])

    targets = [t.strip() for t in args.targets.split(",") if t.strip()]
    args.out.mkdir(parents=True, exist_ok=True)

    payloads: list[dict] = []
    for target in targets:
        sub = args.out / target
        payloads.append(
            run_target(
                target,
                sub,
                ne=args.ne,
                max_nfev=args.max_nfev,
                p_final=args.p_final,
                R=args.R,
                t=args.t,
                pallikaris_mode=args.pallikaris_mode,
                lo=lo_bounds,
                hi=hi_bounds,
            )
        )

    write_summary(args.out, payloads)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
