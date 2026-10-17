#!/usr/bin/env python3
"""E3 — Yeoh-2 fit vs Pallikaris + isolated repro. E1b — known failing Ogden points."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

HERE = Path(__file__).resolve().parent
WP1 = HERE.parents[1] / "wp1.1"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(WP1 / "scripts"))

from ccx_utils import ccx_bin, d1_from_ogden_mu1, run_ccx  # noqa: E402
from extract_pv_curve import extract_pv  # noqa: E402
from fit_hyperelastic import ExpPoint, fit_quality  # noqa: E402
from fit_pallikaris import (  # noqa: E402
    DP_FEA_FINAL,
    KF_PER_UL,
    P0_MMHG,
    Geometry,
    generate_pallikaris_csv,
)
from gen_sphere_shell_mesh import write_mesh  # noqa: E402
from write_deck import write_deck  # noqa: E402
from yeoh_fit_bounds import decode_yeoh, yeoh_bounds  # noqa: E402

# Ogden points that failed isolated repro in prior investigation
E1B_POINTS = [
    (2.08, 0.1841, "opt_elipsoid"),
    (7.1585, 0.50, "opt_octant_cursor"),
    (5.610785, 0.793516, "opt_octant_kf_fixed"),
]

R_MM = 12.0
T_MM = 0.5
N_LOAD_STEPS = 16


def p_targets(p_final: float = DP_FEA_FINAL) -> list[float]:
    return [
        P0_MMHG + (p_final - P0_MMHG) * i / N_LOAD_STEPS
        for i in range(1, N_LOAD_STEPS + 1)
    ]


class PallikarisYeohForward:
    def __init__(self, work_dir: Path, ne: int = 8, p_final: float = DP_FEA_FINAL):
        self.geom = Geometry(R_mm=R_MM, t_mm=T_MM)
        self.work_dir = work_dir
        self.ne = ne
        self.p_final = p_final
        work_dir.mkdir(parents=True, exist_ok=True)
        self._write_mesh()

    def _write_mesh(self) -> None:
        self.mesh_path = self.work_dir / "mesh.inp"
        write_mesh(
            self.mesh_path,
            R_MM,
            T_MM,
            self.ne,
            2,
            label=f"e3 yeoh ne={self.ne}",
            bc_mode="symmetry_octant",
            mesh_kind="spherical",
            theta_min_deg=3.0,
            reduced=True,
        )

    def run(self, c10: float, c20: float, tag: str = "run") -> tuple[np.ndarray, np.ndarray]:
        params = {"C10_MPa": float(c10), "C20_MPa": float(c20)}
        deck = self.work_dir / f"{tag}.inp"
        write_deck(
            deck,
            self.mesh_path.name,
            T_MM,
            "yeoh2",
            params,
            p_targets(self.p_final),
            label=f"E3 yeoh2 {tag}",
            bc_mode="symmetry_octant",
            p0_mmhg=P0_MMHG,
        )
        frd = run_ccx(deck, clean=True)
        rows = extract_pv(deck, frd, R_MM, p0_mmhg=P0_MMHG)
        v = np.array([r["dV_uL"] for r in rows], dtype=float)
        p = np.array([r["p_mmhg"] for r in rows], dtype=float)
        return v, p


def fit_yeoh2(
    forward: PallikarisYeohForward,
    exp: list[ExpPoint],
    max_nfev: int = 30,
    c10_max: float | None = None,
    c20_max_mpa: float | None = None,
    x0: np.ndarray | None = None,
) -> dict:
    """Yeoh-2 inverse fit; optimizer vector is [C10, log10(C20)] with canonical log bounds."""
    v_exp = np.array([e.V_uL for e in exp])
    p_exp = np.array([e.P_mmHg for e in exp])
    x0_def, lo, hi = yeoh_bounds()
    if x0 is None:
        x0 = x0_def.copy()
    if c10_max is not None:
        hi = hi.copy()
        hi[0] = float(c10_max)
    if c20_max_mpa is not None:
        hi = hi.copy()
        hi[1] = float(np.log10(c20_max_mpa))
    n_eval = {"n": 0}

    def residuals(x: np.ndarray) -> np.ndarray:
        n_eval["n"] += 1
        tag = f"opt_{n_eval['n']:03d}"
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
        x0,
        bounds=(lo, hi),
        max_nfev=max_nfev,
        ftol=1e-8,
        xtol=1e-8,
        diff_step=0.02,
        verbose=2,
    )
    fit_time = time.time() - t0
    c10, c20 = decode_yeoh(res.x)
    v_fea, p_fea = forward.run(c10, c20, tag="final")
    order = np.argsort(v_fea)
    v_fea, p_fea = v_fea[order], p_fea[order]
    dp_fea = p_fea - P0_MMHG
    dp_at_exp = np.interp(v_exp, v_fea, dp_fea)
    quality = fit_quality(p_exp, dp_at_exp)

    return {
        "model": "yeoh2",
        "params": {"C10_MPa": c10, "C20_MPa": c20},
        "params_full_precision": {"C10_MPa": repr(c10), "C20_MPa": repr(c20)},
        "quality": quality,
        "optimizer": {
            "success": bool(res.success),
            "message": res.message,
            "nfev": int(res.nfev),
            "cost": float(res.cost),
            "fit_time_s": fit_time,
            "bounds": {"C10": [float(lo[0]), float(hi[0])], "log10_C20": [float(lo[1]), float(hi[1])]},
            "x_opt": [float(res.x[0]), float(res.x[1])],
        },
        "fea_curve": [{"V_uL": float(v), "P_abs_mmHg": float(p)} for v, p in zip(v_fea, p_fea)],
        "exp_at_fit": [
            {"V_uL": float(v), "P_exp_dP_mmHg": float(pe), "P_fea_dP_mmHg": float(pm)}
            for v, pe, pm in zip(v_exp, p_exp, dp_at_exp)
        ],
        "fit_convention": "delta_P_above_P0",
    }


def isolated_yeoh_repro(
    c10: float,
    c20: float,
    trial: int,
    out: Path,
    ne: int,
    p_final: float,
) -> str:
    work = out / f"trial_{trial:02d}"
    if work.is_dir():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    mesh = work / "mesh.inp"
    write_mesh(
        mesh,
        R_MM,
        T_MM,
        ne,
        2,
        "e3_repro",
        bc_mode="symmetry_octant",
        mesh_kind="spherical",
        theta_min_deg=3.0,
        reduced=True,
    )
    deck = work / "isolated.inp"
    write_deck(
        deck,
        mesh.name,
        T_MM,
        "yeoh2",
        {"C10_MPa": c10, "C20_MPa": c20},
        p_targets(p_final),
        label=f"E3 isolated trial {trial}",
        bc_mode="symmetry_octant",
        p0_mmhg=P0_MMHG,
    )
    try:
        run_ccx(deck, clean=True)
    except Exception as exc:
        log = work / "log_isolated.txt"
        tail = log.read_text().splitlines()[-8:] if log.is_file() else []
        return f"FAIL: {exc} | tail={tail}"
    log = work / "log_isolated.txt"
    text = log.read_text() if log.is_file() else ""
    if "Job finished" not in text:
        return "FAIL: no Job finished"
    if "*ERROR" in text and "Job finished" not in text:
        return "FAIL: CCX error"
    return "OK"


def run_ogden_e1b(
    mu1: float,
    alpha1: float,
    tag: str,
    rep: int,
    work: Path,
    ne: int,
    p_final: float,
) -> dict:
    sub = work / tag
    sub.mkdir(parents=True, exist_ok=True)
    mesh = sub / f"mesh_r{rep}.inp"
    write_mesh(
        mesh,
        R_MM,
        T_MM,
        ne,
        2,
        f"e1b_{tag}",
        bc_mode="symmetry_octant",
        mesh_kind="spherical",
        reduced=True,
    )
    d1 = d1_from_ogden_mu1(mu1)
    deck = sub / f"{tag}_r{rep}.inp"
    write_deck(
        deck,
        mesh.name,
        T_MM,
        "ogden1",
        {"mu1_MPa": mu1, "alpha1": alpha1, "D1": d1},
        p_targets(p_final),
        label=f"E1b {tag} r{rep}",
        bc_mode="symmetry_octant",
        p0_mmhg=P0_MMHG,
    )
    t0 = time.perf_counter()
    try:
        run_ccx(deck, clean=True)
        status = "OK"
    except Exception as exc:
        status = f"FAIL: {exc}"
    elapsed = time.perf_counter() - t0
    return {
        "tag": tag,
        "mu1": mu1,
        "alpha1": alpha1,
        "rep": rep,
        "status": status,
        "elapsed_s": elapsed,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ne", type=int, default=8)
    ap.add_argument("--max-nfev", type=int, default=30)
    ap.add_argument("--repro-trials", type=int, default=5)
    ap.add_argument("--e1b-rep", type=int, default=3)
    ap.add_argument("--out", type=Path, default=HERE.parent / "output_exploration" / "e3_yeoh")
    ap.add_argument("--skip-e1b", action="store_true")
    ap.add_argument("--skip-e3", action="store_true")
    ap.add_argument(
        "--dp-fea-final",
        type=float,
        default=DP_FEA_FINAL,
        help="Absolute P at end of FEA ramp [mmHg] (default: %(default)s)",
    )
    ap.add_argument("--ccx-bin", default=os.environ.get("CCX_BIN", ""))
    args = ap.parse_args()

    if args.ccx_bin:
        os.environ["CCX_BIN"] = args.ccx_bin

    ccx = ccx_bin()
    args.out.mkdir(parents=True, exist_ok=True)
    exploration = args.out.parent

    e3_result: dict | None = None
    repro_results: list[tuple[int, str]] = []
    e1b_results: list[dict] = []

    if not args.skip_e3:
        print(f"=== E3: Yeoh-2 fit vs Pallikaris (ne={args.ne}) ===")
        csv_path = args.out / "pallikaris_synthetic.csv"
        exp = generate_pallikaris_csv(csv_path)
        work = args.out / "ccx_runs"
        forward = PallikarisYeohForward(work, ne=args.ne, p_final=args.dp_fea_final)
        e3_result = fit_yeoh2(forward, exp, max_nfev=args.max_nfev)

        c10 = e3_result["params"]["C10_MPa"]
        c20 = e3_result["params"]["C20_MPa"]
        print(f"\n--- E3 isolated repro ({args.repro_trials} trials) ---")
        repro_dir = args.out / "isolated_repro"
        for i in range(1, args.repro_trials + 1):
            status = isolated_yeoh_repro(c10, c20, i, repro_dir, args.ne, args.dp_fea_final)
            repro_results.append((i, status))
            print(f"  trial {i}: {status}")

        payload = {
            "ccx": ccx,
            "geometry": asdict(forward.geom),
            "pallikaris": {"P0_mmHg": P0_MMHG, "Kf_per_uL": KF_PER_UL},
            "fea_ramp": {"P_final_mmHg_abs": args.dp_fea_final},
            "mesh": {"ne": args.ne, "bc_mode": "symmetry_octant"},
            "fit": e3_result,
            "isolated_repro": [{"trial": t, "status": s} for t, s in repro_results],
        }
        (args.out / "fit_results.json").write_text(json.dumps(payload, indent=2))

    if not args.skip_e1b:
        print("\n=== E1b: known failing Ogden points ===")
        e1b_work = exploration / "e1b_ogden"
        for mu1, alpha1, tag in E1B_POINTS:
            for rep in range(1, args.e1b_rep + 1):
                r = run_ogden_e1b(mu1, alpha1, tag, rep, e1b_work, args.ne, DP_FEA_FINAL)
                e1b_results.append(r)
                print(f"  {tag} μ₁={mu1} α₁={alpha1} rep={rep} -> {r['status']}")

    # Combined RESULTS.md
    lines = [
        "# E3 + E1b — Yeoh fit and Ogden failure repro\n",
        f"- **ccx**: `{ccx}`",
        f"- **geometry**: R={R_MM} mm, t={T_MM} mm, octant, ne={args.ne}",
        f"- **Pallikaris**: P₀={P0_MMHG} mmHg, Kf={KF_PER_UL} /µL, P_final={args.dp_fea_final} mmHg",
        "",
    ]

    if e3_result:
        q = e3_result["quality"]
        p = e3_result["params"]
        ok = sum(1 for _, s in repro_results if s == "OK")
        lines.extend(
            [
                "## E3 — Yeoh-2 fit",
                "",
                f"- **C10**: {p['C10_MPa']:.12e} MPa",
                f"- **C20**: {p['C20_MPa']:.12e} MPa",
                f"- **R²**: {q['R2']:.6f}",
                f"- **Max residual**: {q['max_residual_mmHg']:.4f} mmHg",
                f"- **Optimizer nfev**: {e3_result['optimizer']['nfev']}",
                "",
                f"### Isolated repro: {ok}/{args.repro_trials} OK",
                "",
                "| trial | status |",
                "|---:|---|",
            ]
        )
        for t, s in repro_results:
            lines.append(f"| {t} | {s} |")
        lines.append("")

    if e1b_results:
        lines.extend(["## E1b — Ogden points that failed before", ""])
        lines.append("| tag | μ₁ | α₁ | rep | status |")
        lines.append("|---|---:|---:|---:|---|")
        for r in e1b_results:
            lines.append(
                f"| {r['tag']} | {r['mu1']} | {r['alpha1']} | {r['rep']} | {r['status']} |"
            )
        # summary by tag
        lines.append("")
        for mu1, alpha1, tag in E1B_POINTS:
            trials = [r for r in e1b_results if r["tag"] == tag]
            n_ok = sum(1 for r in trials if r["status"] == "OK")
            lines.append(f"- **{tag}** ({mu1}, {alpha1}): {n_ok}/{len(trials)} OK")

    summary_path = exploration / "RESULTS_E3_E1B.md"
    summary_path.write_text("\n".join(lines) + "\n")
    print(f"\nWrote {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
