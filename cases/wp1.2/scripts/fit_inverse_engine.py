#!/usr/bin/env python3
"""Shared inverse FEA engine for WP1.2 (log bounds, multi-start, dual objectives)."""
from __future__ import annotations

import csv
import json
import shutil
import time
from dataclasses import asdict
from pathlib import Path
from typing import Callable, Literal

import numpy as np
from scipy.optimize import least_squares

from ccx_utils import YEOH_D1_MPA, ccx_diagnostics, d1_from_ogden_mu1, run_ccx
from extract_pv_curve import extract_pv
from fit_hyperelastic import ExpPoint, fit_quality
from fit_pallikaris import Geometry, P0_MMHG
from gen_sphere_shell_mesh import write_mesh
from write_deck import write_deck
from yeoh_fit_bounds import YEOH_C20_HI_MPA, decode_yeoh, yeoh_bounds

ObjectiveMode = Literal["pressure", "pressure_and_secant_K"]
N_EVAL_PTS = 11
N_LOAD_STEPS_DEFAULT = 25
SECANT_V_MIN_UL = 2.5
TANGENT_STRAINS = (0.002, 0.005, 0.01, 0.02, 0.03, 0.05, 0.08)
TANGENT_WARN_MPA = 30.0
TANGENT_WARN_STRAIN = 0.03
BOUND_FRAC = 0.02
N_MULTISTART = 15


def equispaced_v_grid(v_max: float, n: int = N_EVAL_PTS) -> np.ndarray:
    return np.linspace(0.0, float(v_max), int(n))


def linear_baseline_fit(v_grid: np.ndarray, dp_target: np.ndarray) -> dict:
    """P = P0 + K V  →  least squares K through origin on ΔP."""
    mask = v_grid > 1e-9
    if mask.sum() < 2:
        return {"K_mmHg_per_uL": float("nan"), "quality": {}}
    v, dp = v_grid[mask], dp_target[mask]
    k = float(np.dot(v, dp) / np.dot(v, v))
    dp_mod = k * v_grid
    q = fit_quality(dp_target, dp_mod)
    return {"K_mmHg_per_uL": k, "quality": q, "dp_model": dp_mod}


def secant_stiffness(v: np.ndarray, dp: np.ndarray) -> np.ndarray:
    k = np.zeros_like(v, dtype=float)
    for i, vi in enumerate(v):
        if vi > 1e-9:
            k[i] = dp[i] / vi
    return k


def yeoh_uniaxial_tangent_mpa(c10: float, c20: float, eps: float) -> float:
    lam = float(np.sqrt(1.0 + 2.0 * eps))
    i1 = lam**2 + 2.0 / lam
    sigma = 2.0 * (c10 + 2.0 * c20 * (i1 - 3.0)) * (lam**2 - lam**-1)
    deps = max(eps * 1e-4, 1e-6)
    lam2 = float(np.sqrt(1.0 + 2.0 * (eps + deps)))
    i12 = lam2**2 + 2.0 / lam2
    sig2 = 2.0 * (c10 + 2.0 * c20 * (i12 - 3.0)) * (lam2**2 - lam2**-1)
    return float((sig2 - sigma) / deps)


def effective_nu(d1_mpa: float, g_mpa: float) -> float:
    k0 = 2.0 / float(d1_mpa)
    return float((3.0 * k0 - 2.0 * g_mpa) / (2.0 * (3.0 * k0 + g_mpa)))


def near_bound(value: float, lo: float, hi: float, frac: float = BOUND_FRAC) -> str | None:
    span = hi - lo
    if span <= 0:
        return None
    if value <= lo + frac * span:
        return "lo"
    if value >= hi - frac * span:
        return "hi"
    return None


def log_uniform(rng: np.random.Generator, lo: float, hi: float) -> float:
    return float(np.exp(rng.uniform(np.log(lo), np.log(hi))))


class HyperelasticForward:
    """CalculiX octant forward model with configurable R (backward displacement)."""

    def __init__(
        self,
        work_dir: Path,
        *,
        geom: Geometry | None = None,
        ne: int = 8,
        p_final: float = 50.0,
        p0: float = P0_MMHG,
        n_load_steps: int = N_LOAD_STEPS_DEFAULT,
        r_mm: float | None = None,
    ):
        self.geom = geom or Geometry(R_mm=12.0, t_mm=0.5)
        self.r_mm = float(r_mm if r_mm is not None else self.geom.R_mm)
        self.work_dir = work_dir
        self.ne = ne
        self.p_final = float(p_final)
        self.p0 = float(p0)
        self.n_load_steps = n_load_steps
        work_dir.mkdir(parents=True, exist_ok=True)
        self.mesh_path = work_dir / "mesh.inp"
        self._write_mesh()

    def _write_mesh(self) -> None:
        write_mesh(
            self.mesh_path,
            self.r_mm,
            self.geom.t_mm,
            self.ne,
            2,
            label=f"inverse ne={self.ne} R={self.r_mm}",
            bc_mode="symmetry_octant",
            mesh_kind="spherical",
            theta_min_deg=3.0,
            reduced=True,
        )

    def _p_targets(self) -> list[float]:
        return [
            self.p0 + (self.p_final - self.p0) * i / self.n_load_steps
            for i in range(1, self.n_load_steps + 1)
        ]

    def run_yeoh(self, c10: float, c20: float, tag: str) -> tuple[np.ndarray, np.ndarray]:
        params = {
            "C10_MPa": float(c10),
            "C20_MPa": float(c20),
            "D1": YEOH_D1_MPA,
        }
        return self._run("yeoh2", params, tag)

    def run_ogden(self, mu1: float, alpha1: float, tag: str) -> tuple[np.ndarray, np.ndarray]:
        params = {
            "mu1_MPa": float(mu1),
            "alpha1": float(alpha1),
            "D1": d1_from_ogden_mu1(mu1),
            "d1_tied_mu1": True,
        }
        return self._run("ogden1", params, tag)

    def run_p0_only(self, model: str, params: dict, tag: str) -> float:
        """Return ΔV [µL] at P0 relative to zero-pressure state (single step to P0)."""
        deck = self.work_dir / f"{tag}.inp"
        write_deck(
            deck,
            self.mesh_path.name,
            self.geom.t_mm,
            model,
            params,
            [self.p0],
            label=f"P0 probe {tag}",
            bc_mode="symmetry_octant",
            p0_mmhg=self.p0,
        )
        frd = run_ccx(deck, clean=True)
        rows = extract_pv(deck, frd, self.r_mm, p0_mmhg=self.p0)
        if not rows:
            return 0.0
        # Absolute cavity increment from zero-pressure mesh (not ΔV re-anchored at P₀).
        return float(rows[-1].get("v_abs_uL", rows[-1]["dV_uL"]))

    def _run(self, model: str, params: dict, tag: str) -> tuple[np.ndarray, np.ndarray]:
        deck = self.work_dir / f"{tag}.inp"
        write_deck(
            deck,
            self.mesh_path.name,
            self.geom.t_mm,
            model,
            params,
            self._p_targets(),
            label=f"wp1.2 {model} {tag}",
            bc_mode="symmetry_octant",
            p0_mmhg=self.p0,
            nu=self.geom.nu,
            E_mpa=self.geom.E_mpa,
        )
        frd = run_ccx(deck, clean=True)
        rows = extract_pv(deck, frd, self.r_mm, p0_mmhg=self.p0)
        v = np.array([r["dV_uL"] for r in rows], dtype=float)
        p = np.array([r["p_mmhg"] for r in rows], dtype=float)
        return v, p


def decode_ogden(x: np.ndarray) -> tuple[float, float]:
    mu1 = float(x[0])
    alpha1 = float(np.exp(x[1]))
    return mu1, alpha1


def ogden_bounds() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    lo = np.array([0.1, np.log(0.3)])
    hi = np.array([20.0, np.log(100.0)])
    x0 = np.array([2.0, np.log(1.5)])
    return x0, lo, hi


def multistart_inits(material: str, rng: np.random.Generator, n: int = N_MULTISTART) -> list[np.ndarray]:
    if material == "yeoh":
        _, lo, hi = yeoh_bounds()
        starts = []
        for _ in range(n):
            c10 = log_uniform(rng, lo[0], hi[0])
            q = rng.uniform(lo[1], hi[1])
            starts.append(np.array([c10, q]))
        return starts
    _, lo, hi = ogden_bounds()
    starts = []
    for _ in range(n):
        mu1 = log_uniform(rng, lo[0], hi[0])
        log_a = rng.uniform(lo[1], hi[1])
        starts.append(np.array([mu1, log_a]))
    return starts


def expand_bounds_if_needed(
    material: str,
    x_opt: np.ndarray,
    lo: np.ndarray,
    hi: np.ndarray,
    flags: dict,
) -> tuple[np.ndarray, np.ndarray, bool]:
    """Expand any bound hit within BOUND_FRAC; return updated (lo, hi, expanded?)."""
    expanded = False
    lo2, hi2 = lo.copy(), hi.copy()
    if material == "yeoh":
        c10, c20 = decode_yeoh(x_opt)
        checks = [(c10, 0, "C10"), (c20, None, "C20")]
        if near_bound(c10, lo2[0], hi2[0]):
            hi2[0] = min(hi2[0] * 1.5, 20.0)
            expanded = True
        q = x_opt[1]
        if near_bound(q, lo2[1], hi2[1]):
            hi2[1] = min(hi2[1] + 0.5, np.log10(YEOH_C20_HI_MPA))
            expanded = True
    else:
        mu1, alpha1 = decode_ogden(x_opt)
        if near_bound(mu1, lo2[0], hi2[0]):
            hi2[0] = min(hi2[0] * 1.5, 50.0)
            expanded = True
        if near_bound(alpha1, np.exp(lo2[1]), np.exp(hi2[1])):
            hi2[1] = min(hi2[1] + np.log(2.0), np.log(600.0))
            expanded = True
    flags.update({"bounds_expanded": expanded, "bounds_lo": lo2.tolist(), "bounds_hi": hi2.tolist()})
    return lo2, hi2, expanded


def build_residual_fn(
    forward: HyperelasticForward,
    material: str,
    v_grid: np.ndarray,
    dp_target: np.ndarray,
    k_target: np.ndarray,
    mode: ObjectiveMode,
) -> Callable[[np.ndarray], np.ndarray]:
    n_eval = {"n": 0}

    def residuals(x: np.ndarray) -> np.ndarray:
        n_eval["n"] += 1
        tag = f"opt_{n_eval['n']:03d}"
        try:
            if material == "yeoh":
                c10, c20 = decode_yeoh(x)
                v_fea, p_fea = forward.run_yeoh(c10, c20, tag)
            else:
                mu1, a1 = decode_ogden(x)
                v_fea, p_fea = forward.run_ogden(mu1, a1, tag)
        except Exception:
            return np.ones(len(v_grid) + (len(v_grid) if mode == "pressure_and_secant_K" else 0)) * 1e3
        order = np.argsort(v_fea)
        v_fea, p_fea = v_fea[order], p_fea[order]
        if v_fea.max() < v_grid.max() * 0.92:
            return np.ones(len(v_grid) + (len(v_grid) if mode == "pressure_and_secant_K" else 0)) * 50.0
        dp_fea = p_fea - forward.p0
        dp_pred = np.interp(v_grid, v_fea, dp_fea)
        res_p = dp_pred - dp_target
        if mode == "pressure":
            return res_p
        k_mod = secant_stiffness(v_grid, dp_pred)
        mask = v_grid > SECANT_V_MIN_UL
        rel_k = np.zeros(int(mask.sum()))
        for j, idx in enumerate(np.where(mask)[0]):
            kt = k_target[idx]
            if abs(kt) > 1e-9:
                rel_k[j] = (k_mod[idx] - kt) / kt
            else:
                rel_k[j] = k_mod[idx]
        return np.concatenate([res_p, rel_k])

    return residuals


def isolated_repro_runs(
    forward: HyperelasticForward,
    material: str,
    params_decoded: dict,
    out_dir: Path,
    n_trials: int = 3,
) -> list[str]:
    statuses: list[str] = []
    for trial in range(1, n_trials + 1):
        sub = out_dir / f"isolated_{trial:02d}"
        if sub.is_dir():
            shutil.rmtree(sub)
        sub.mkdir(parents=True)
        fwd = HyperelasticForward(
            sub,
            geom=forward.geom,
            ne=forward.ne,
            p_final=forward.p_final,
            p0=forward.p0,
            n_load_steps=forward.n_load_steps,
            r_mm=forward.r_mm,
        )
        tag = "isolated"
        try:
            if material == "yeoh":
                fwd.run_yeoh(params_decoded["C10_MPa"], params_decoded["C20_MPa"], tag)
            else:
                fwd.run_ogden(params_decoded["mu1_MPa"], params_decoded["alpha1"], tag)
            statuses.append("OK")
        except Exception as exc:
            statuses.append(f"FAIL: {exc}")
    return statuses


def fit_material(
    forward: HyperelasticForward,
    target_name: str,
    dp_target_on_grid: np.ndarray,
    v_grid: np.ndarray,
    material: str,
    *,
    mode: ObjectiveMode = "pressure",
    max_nfev: int = 35,
    rng_seed: int = 42,
) -> dict:
    k_target = secant_stiffness(v_grid, dp_target_on_grid)
    if material == "yeoh":
        _, lo, hi = yeoh_bounds()
        decode = decode_yeoh
    else:
        _, lo, hi = ogden_bounds()
        decode = decode_ogden

    rng = np.random.default_rng(rng_seed)
    starts = multistart_inits(material, rng)
    best: dict | None = None
    all_starts: list[dict] = []

    for si, x0 in enumerate(starts, start=1):
        res_fn = build_residual_fn(forward, material, v_grid, dp_target_on_grid, k_target, mode)
        t0 = time.time()
        try:
            res = least_squares(
                res_fn,
                x0,
                bounds=(lo, hi),
                max_nfev=max_nfev,
                ftol=1e-9,
                xtol=1e-9,
                diff_step=0.02,
                x_scale="jac",
                verbose=0,
            )
        except Exception as exc:
            all_starts.append({"start": si, "error": str(exc), "cost": float("inf")})
            continue
        fit_time = time.time() - t0
        row = {
            "start": si,
            "x_opt": res.x.tolist(),
            "cost": float(res.cost),
            "nfev": int(res.nfev),
            "success": bool(res.success),
            "fit_time_s": fit_time,
        }
        all_starts.append(row)
        if best is None or row["cost"] < best["cost"]:
            best = {**row, "x": res.x.copy()}

    if best is None:
        raise RuntimeError(f"All multistart fits failed for {target_name}/{material}")

    flags: dict = {}
    lo2, hi2, expanded = expand_bounds_if_needed(material, best["x"], lo, hi, flags)
    if expanded:
        res_fn = build_residual_fn(forward, material, v_grid, dp_target_on_grid, k_target, mode)
        res = least_squares(
            res_fn,
            best["x"],
            bounds=(lo2, hi2),
            max_nfev=max_nfev,
            ftol=1e-9,
            xtol=1e-9,
            verbose=0,
        )
        best = {**best, "x": res.x.copy(), "cost": float(res.cost), "nfev": int(res.nfev), "refit_after_expand": True}

    x = best["x"]
    if material == "yeoh":
        c10, c20 = decode_yeoh(x)
        v_fea, p_fea = forward.run_yeoh(c10, c20, "final")
        params = {"C10_MPa": c10, "C20_MPa": c20, "D1": YEOH_D1_MPA}
        d1 = YEOH_D1_MPA
        g = 2.0 * c10
        tangents = {f"eps_{int(e*1000)/10}pct_MPa": yeoh_uniaxial_tangent_mpa(c10, c20, e) for e in TANGENT_STRAINS}
        bound_checks = {
            "C10": near_bound(c10, lo2[0], hi2[0]),
            "C20_log": near_bound(x[1], lo2[1], hi2[1]),
        }
    else:
        mu1, alpha1 = decode_ogden(x)
        v_fea, p_fea = forward.run_ogden(mu1, alpha1, "final")
        d1 = d1_from_ogden_mu1(mu1)
        params = {"mu1_MPa": mu1, "alpha1": alpha1, "D1": d1, "d1_tied_mu1": True}
        g = mu1
        tangents = {}
        bound_checks = {
            "mu1": near_bound(mu1, lo2[0], hi2[0]),
            "log_alpha1": near_bound(x[1], lo2[1], hi2[1]),
        }

    order = np.argsort(v_fea)
    v_fea, p_fea = v_fea[order], p_fea[order]
    dp_fea = p_fea - forward.p0
    dp_at = np.interp(v_grid, v_fea, dp_fea)
    quality = fit_quality(dp_target_on_grid, dp_at)
    k_mod = secant_stiffness(v_grid, dp_at)
    k_tgt = secant_stiffness(v_grid, dp_target_on_grid)

    tangent_warn = any(
        tangents.get(k, 0) > TANGENT_WARN_MPA for k in tangents if "eps_0.2" in k or "eps_0.5" in k or "eps_1" in k
    )

    repro = isolated_repro_runs(forward, material, params, forward.work_dir / "isolated_repro")

    return {
        "target": target_name,
        "material": material,
        "objective_mode": mode,
        "model": "yeoh2" if material == "yeoh" else "ogden1",
        "params": params,
        "quality": quality,
        "v_grid_uL": v_grid.tolist(),
        "secant_K": {
            "target_initial": float(k_tgt[1]) if len(k_tgt) > 1 else float("nan"),
            "target_final": float(k_tgt[-1]),
            "model_initial": float(k_mod[1]) if len(k_mod) > 1 else float("nan"),
            "model_final": float(k_mod[-1]),
        },
        "nu_effective": effective_nu(d1, g),
        "implicit_tangent_uniaxial_MPa": tangents,
        "tangent_warn_above_30MPa_below_3pct": tangent_warn,
        "parameters_at_bound": {k: v for k, v in bound_checks.items() if v},
        "optimizer": best,
        "multistart_runs": all_starts,
        "bounds_expand": flags,
        "isolated_repro": repro,
        "fea_curve": [{"V_uL": float(v), "P_abs_mmHg": float(p)} for v, p in zip(v_fea, p_fea)],
        "eval_at_grid": [
            {
                "V_uL": float(v),
                "P_target_dP": float(pt),
                "P_model_dP": float(pm),
                "K_target": float(kt),
                "K_model": float(km),
            }
            for v, pt, pm, kt, km in zip(v_grid, dp_target_on_grid, dp_at, k_tgt, k_mod)
        ],
    }


def export_curve_csvs(out_dir: Path, target: str, results: list[dict], linear: dict, v_grid: np.ndarray, dp_target: np.ndarray) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    pv_path = out_dir / f"{target}_pv_curves.csv"
    with open(pv_path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["alvo", "modelo", "V_uL", "P_mmHg"])
        for v, dp in zip(v_grid, dp_target):
            w.writerow([target, "alvo", f"{v:.6f}", f"{dp + P0_MMHG:.6f}"])
        k_lin = linear.get("K_mmHg_per_uL", float("nan"))
        for v in v_grid:
            w.writerow([target, "linear_ajustado", f"{v:.6f}", f"{P0_MMHG + k_lin * v:.6f}"])
        for r in results:
            mode = r.get("objective_mode", "pressure")
            label = f"{r['material']}_{mode}"
            for row in r["eval_at_grid"]:
                w.writerow([target, label, f"{row['V_uL']:.6f}", f"{row['P_model_dP'] + P0_MMHG:.6f}"])

    resid_path = out_dir / f"{target}_residuals.csv"
    with open(resid_path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["alvo", "modelo", "V_uL", "P_mmHg"])
        for r in results:
            label = f"{r['material']}_{r['objective_mode']}"
            for row in r["eval_at_grid"]:
                resid = row["P_model_dP"] - row["P_target_dP"]
                w.writerow([target, label, f"{row['V_uL']:.6f}", f"{resid:.6f}"])

    k_path = out_dir / f"{target}_secant_stiffness.csv"
    with open(k_path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["alvo", "modelo", "V_uL", "P_mmHg"])
        k_tgt = secant_stiffness(v_grid, dp_target)
        for v, k in zip(v_grid, k_tgt):
            w.writerow([target, "alvo", f"{v:.6f}", f"{k:.6f}"])
        for r in results:
            label = f"{r['material']}_{r['objective_mode']}"
            for row in r["eval_at_grid"]:
                w.writerow([target, label, f"{row['V_uL']:.6f}", f"{row['K_model']:.6f}"])


def write_summary_table(out_path: Path, rows: list[dict]) -> None:
    lines = [
        "# WP1.2 corrected fits\n",
        "| alvo | material | obj | C10/μ1 | C20/α1 | R² | max|res| | K0→Kf mod | ν | no limite? |",
        "|---|---|---|---:|---:|---:|---:|---|---:|---|",
    ]
    for r in rows:
        p = r["params"]
        if r["material"] == "yeoh":
            p1 = f"{p['C10_MPa']:.4f}"
            p2 = f"{p['C20_MPa']:.4g}"
        else:
            p1 = f"{p['mu1_MPa']:.4f}"
            p2 = f"{p['alpha1']:.4f}"
        sk = r["secant_K"]
        q = r["quality"]
        at_b = "sim" if not r.get("parameters_at_bound") else "**NÃO**"
        lines.append(
            f"| {r['target']} | {r['material']} | {r['objective_mode']} | {p1} | {p2} | "
            f"{q['R2']:.5f} | {q['max_residual_mmHg']:.3f} | "
            f"{sk['model_initial']:.3f}→{sk['model_final']:.3f} | {r['nu_effective']:.3f} | {at_b} |"
        )
    out_path.write_text("\n".join(lines) + "\n")


def save_change_log(out_path: Path, entries: list[str], ccx_info: dict) -> None:
    lines = ["# WP1.2/WP1.3 code change log (auto)\n", "## ccx environment", json.dumps(ccx_info, indent=2), "", "## notes"]
    lines.extend(f"- {e}" for e in entries)
    out_path.write_text("\n".join(lines) + "\n")
