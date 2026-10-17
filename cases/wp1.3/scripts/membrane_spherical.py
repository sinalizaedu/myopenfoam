"""Analytic spherical membrane (equibiaxial) for WP1.3 backward-displacement checks.

Uses the same fixed-point volume map as run_wp13_backward_displacement.py
(R_new from ΔV) with ΔV from a thin-membrane p–λ relation (Ogden N=1 / Yeoh).
Pressures in mmHg; moduli in MPa; lengths in mm.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable

import numpy as np
from scipy.optimize import brentq, root_scalar

from ccx_utils import mmhg_to_mpa

R_OBS_MM = 12.0
BETA = 0.7
TOL_MM = 1e-3
MAX_ITER = 20


def _cauchy_equibiaxial_ogden(lam: float, mu1: float, alpha1: float) -> float:
    """Cauchy stress [MPa] (equibiaxial, incompressible Ogden N=1, CCX form)."""
    if lam <= 0:
        return float("nan")
    return (mu1 / alpha1) * (lam**alpha1 - lam ** (-alpha1 / 2.0))


def _cauchy_equibiaxial_yeoh(lam: float, c10: float, c20: float) -> float:
    """Cauchy stress [MPa] (equibiaxial Yeoh, W = C10(I1-3) + C20(I1-3)^2)."""
    i1 = 2.0 * lam**2 + lam ** (-4.0)
    dw_di1 = c10 + 2.0 * c20 * (i1 - 3.0)
    return 2.0 * dw_di1 * (lam - lam ** (-5.0))


def _pressure_from_lam(lam: float, r_ref: float, t_mm: float, sigma: float) -> float:
    """Internal pressure [MPa] for current radius λ R_ref."""
    r_cur = lam * r_ref
    return 2.0 * t_mm * sigma / max(r_cur, 1e-12)


def solve_lambda_at_pressure(
    p_mmhg: float,
    r_ref: float,
    t_mm: float,
    sigma_fn: Callable[[float], float],
    *,
    lam_lo: float = 0.85,
    lam_hi: float = 1.25,
) -> float:
    p_mpa = mmhg_to_mpa(p_mmhg)

    def f(lam: float) -> float:
        return _pressure_from_lam(lam, r_ref, t_mm, sigma_fn(lam)) - p_mpa

    try:
        return float(brentq(f, lam_lo, lam_hi, xtol=1e-10, rtol=1e-10))
    except ValueError:
        sol = root_scalar(f, bracket=(lam_lo, lam_hi), method="brentq")
        return float(sol.root)


def cavity_dv_uL(r_ref: float, lam: float) -> float:
    """Full-sphere cavity volume increment [µL] vs undeformed reference radius r_ref."""
    dv_mm3 = (4.0 / 3.0) * math.pi * (r_ref**3) * (lam**3 - 1.0)
    return float(dv_mm3)


def p0_dv_uL(
    r_ref: float,
    t_mm: float,
    p0_mmhg: float,
    sigma_fn: Callable[[float], float],
) -> float:
    lam = solve_lambda_at_pressure(p0_mmhg, r_ref, t_mm, sigma_fn)
    return cavity_dv_uL(r_ref, lam)


def r_new_from_dv(r_ref: float, dv_uL: float) -> float:
    dv_mm3 = dv_uL
    return float((r_ref**3 + 3.0 * dv_mm3 / (4.0 * math.pi)) ** (1.0 / 3.0))


@dataclass
class MembraneFixedPoint:
    converged: bool
    n_iter: int
    r_ref_mm: float
    u_mm: float
    four_u_over_r_pct: float
    history: list[dict]


def backward_fixed_point_analytic(
    *,
    r_obs: float,
    t_mm: float,
    p0_mmhg: float,
    sigma_fn: Callable[[float], float],
    beta: float = BETA,
    tol_mm: float = TOL_MM,
    max_iter: int = MAX_ITER,
) -> MembraneFixedPoint:
    r_ref = r_obs
    history: list[dict] = []
    converged = False
    for k in range(max_iter):
        dv = p0_dv_uL(r_ref, t_mm, p0_mmhg, sigma_fn)
        r_new = r_new_from_dv(r_ref, dv)
        delta = beta * (r_new - r_obs)
        history.append(
            {
                "iter": k,
                "R_ref_mm": r_ref,
                "dV_P0_uL": dv,
                "R_new_mm": r_new,
                "delta_mm": delta,
            }
        )
        if abs(delta) < tol_mm:
            converged = True
            break
        r_ref = r_ref - delta
    u = r_obs - r_ref
    return MembraneFixedPoint(
        converged=converged,
        n_iter=len(history),
        r_ref_mm=r_ref,
        u_mm=u,
        four_u_over_r_pct=100.0 * 4.0 * u / r_obs,
        history=history,
    )


def pv_curve_analytic(
    r_ref: float,
    t_mm: float,
    p0_mmhg: float,
    p_final_mmhg: float,
    n_steps: int,
    sigma_fn: Callable[[float], float],
) -> tuple[np.ndarray, np.ndarray]:
    """Monotone P(V) with V=0 at p0 (relative cavity volume increment)."""
    pressures = np.linspace(p0_mmhg, p_final_mmhg, n_steps + 1)
    v_rel: list[float] = []
    lam0 = solve_lambda_at_pressure(p0_mmhg, r_ref, t_mm, sigma_fn)
    v0 = cavity_dv_uL(r_ref, lam0)
    for p in pressures:
        lam = solve_lambda_at_pressure(float(p), r_ref, t_mm, sigma_fn)
        v_rel.append(cavity_dv_uL(r_ref, lam) - v0)
    return np.array(v_rel, dtype=float), pressures.astype(float)


def secant_delta_k_pct(
    r_obs: float,
    r_ref: float,
    t_mm: float,
    p0_mmhg: float,
    p_final_mmhg: float,
    sigma_fn: Callable[[float], float],
    *,
    n_steps: int = 24,
    dp: float = 10.0,
) -> float:
    v_ref, p_ref = pv_curve_analytic(r_obs, t_mm, p0_mmhg, p_final_mmhg, n_steps, sigma_fn)
    v_pre, p_pre = pv_curve_analytic(r_ref, t_mm, p0_mmhg, p_final_mmhg, n_steps, sigma_fn)
    from scipy.interpolate import PchipInterpolator

    def k_at(p_arr: np.ndarray, v_arr: np.ndarray) -> float:
        pchip = PchipInterpolator(p_arr, v_arr, extrapolate=False)
        v0 = float(pchip(p0_mmhg))
        v1 = float(pchip(p0_mmhg + dp))
        return dp / max(v1 - v0, 1e-12)

    kr = k_at(p_ref, v_ref)
    kp = k_at(p_pre, v_pre)
    return 100.0 * (kp - kr) / kr
