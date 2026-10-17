#!/usr/bin/env python3
"""Synthetic P(V) targets for WP1.2 literature matrix (ΔP above P₀ convention)."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Literal

import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import brentq

from fit_hyperelastic import ExpPoint
from fit_pallikaris import (
    KF_PER_UL,
    P0_MMHG,
    P0_PALLIKARIS_MMHG,
    V_MAX_PALLIKARIS_DIGIT,
    pallikaris_digitized_points,
    pallikaris_pressure,
)

P0 = P0_MMHG
KF_PALLIKARIS = KF_PER_UL
KF_FRIEDENWALD_WP0 = 0.00581

V_AGRA = np.array([20.0, 30.0, 40.0, 50.0], dtype=float)
P_AGRA = np.array([32.3, 36.5, 43.5, 50.7], dtype=float)

TARGETS = ("pallikaris", "silver", "agra", "friedenwald")
# Main WP1.2 matrix: three literature targets × two materials (no synthetic Pallikaris grid / "agra").
MAIN_TARGETS = ("friedenwald", "pallikaris", "silver")

# Pallikaris digitized anomaly (excluded by default — see PALLIKARIS_EXCLUDED_V_UL).
PALLIKARIS_EXCLUDED_V_UL = 4.5
PALLIKARIS_EXCLUSION_NOTE = "excluded_digitized_point_at_4.5_uL"


def pallikaris_law_scaled(v_uL: float, p0: float = P0, kf: float = KF_PALLIKARIS) -> float:
    """P = P₀ · 10^(kf V) (multiplicative baseline)."""
    return p0 * (10.0 ** (kf * v_uL))


def pallikaris_additive(v_uL: float, p0: float = P0, kf: float = KF_PALLIKARIS, p0_art: float = P0_PALLIKARIS_MMHG) -> float:
    """P = P₀ + P_art·(10^(kf V) − 1) (article increment on user P₀)."""
    return p0 + p0_art * (10.0 ** (kf * v_uL) - 1.0)


BaselineMode = Literal["additive", "law_scaled"]


def dV_silver(p: float) -> float:
    return -49.8 + 30.2 * np.log(p) + 0.242 * p


def v_inj_silver(p: float, p0: float = P0) -> float:
    return dV_silver(p) - dV_silver(p0)


def p_from_v_silver(v_target: float, p0: float = P0, p_hi: float = 400.0) -> float:
    if abs(v_target) < 1e-12:
        return p0
    f = lambda p: v_inj_silver(p, p0) - v_target
    return float(brentq(f, p0, p_hi))


def silver_v_max_at_p_cap(p_cap: float = 50.0, p0: float = P0) -> float:
    """Volume increment [µL] at absolute cap pressure (not hard-coded 38 µL)."""
    return float(v_inj_silver(p_cap, p0))


# Silver: fit/training cap at 38 µL (~46.8 mmHg at P₀=16.9 per Silver–Geyer); FEA ramp may still go to 50 mmHg.
SILVER_V_MAX_UPL = 38.0

V_MAX_SAFE = {
    "pallikaris": V_MAX_PALLIKARIS_DIGIT,
    "silver": SILVER_V_MAX_UPL,
    "friedenwald": 50.0,
    "agra": 40.0,
}


def friedenwald_wp0_pressure(v_uL: float, p0: float = P0, kf: float = KF_FRIEDENWALD_WP0) -> float:
    return p0 * (10.0 ** (kf * v_uL))


def pallikaris_digitized_points_filtered(
    v_max: float = V_MAX_PALLIKARIS_DIGIT,
    p0_pallikaris: float = P0_PALLIKARIS_MMHG,
    exclude_v: float = PALLIKARIS_EXCLUDED_V_UL,
) -> list[ExpPoint]:
    rows = pallikaris_digitized_points(v_max=v_max, p0_pallikaris=p0_pallikaris)
    return [r for r in rows if abs(r.V_uL - exclude_v) > 0.05]


def target_dp_on_grid(
    target: str,
    v_grid: np.ndarray,
    *,
    p0: float = P0,
    p_cap: float = 50.0,
    pallikaris_mode: BaselineMode = "additive",
) -> tuple[np.ndarray, dict]:
    """ΔP above P₀ on equispaced volumes; returns (dp, meta)."""
    target = target.lower()
    meta: dict = {"p0_mmHg": p0, "p_cap_mmHg": p_cap}
    vs = np.asarray(v_grid, dtype=float)

    if target == "friedenwald":
        p_abs = np.array([friedenwald_wp0_pressure(float(v), p0) for v in vs])
        meta["law"] = "friedenwald_recalibrated"
        return p_abs - p0, meta

    if target == "silver":
        meta["v_max_uL"] = silver_v_max_at_p_cap(p_cap, p0)
        p_abs = np.array([p_from_v_silver(float(v), p0) for v in vs])
        meta["law"] = "silver_geyer_ln"
        return p_abs - p0, meta

    if target == "pallikaris":
        meta["pallikaris_baseline_mode"] = pallikaris_mode
        meta["pallikaris_point_handling"] = PALLIKARIS_EXCLUSION_NOTE
        if pallikaris_mode == "law_scaled":
            p_abs = np.array([pallikaris_law_scaled(float(v), p0) for v in vs])
        else:
            p_abs = np.array([pallikaris_additive(float(v), p0) for v in vs])
        meta["law"] = f"pallikaris_{pallikaris_mode}"
        return p_abs - p0, meta

    if target == "agra":
        f = interp1d(V_AGRA, P_AGRA, kind="linear", fill_value="extrapolate")
        p_abs = f(vs)
        meta["law"] = "agra_tabulated"
        return p_abs - p0, meta

    raise ValueError(f"Unknown target {target!r}")


def _write_csv(path: Path, rows: list[ExpPoint], eye_id: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["V_uL", "P_mmHg", "eye_id"])
        for row in rows:
            w.writerow([f"{row.V_uL:.4f}", f"{row.P_mmHg:.4f}", eye_id])


def generate_target(
    target: str,
    path: Path,
    *,
    v_max: float | None = None,
    n_pts: int = 11,
    p0: float = P0,
    p_cap: float = 50.0,
    pallikaris_mode: BaselineMode = "additive",
) -> list[ExpPoint]:
    """Build target curve CSV and return ExpPoint list (ΔP above P₀)."""
    target = target.lower().strip()
    if v_max is None:
        if target == "silver":
            v_max = silver_v_max_at_p_cap(p_cap, p0)
        elif target == "pallikaris":
            v_max = V_MAX_PALLIKARIS_DIGIT
        elif target == "friedenwald":
            v_max = 50.0
        elif target == "agra":
            v_max = 40.0
        else:
            v_max = 50.0

    if target == "pallikaris":
        rows = pallikaris_digitized_points_filtered(v_max=float(v_max))
        meta = {
            "p0_mmHg": p0,
            "p_cap_mmHg": p_cap,
            "law": "pallikaris_digitized_fig2",
            "pallikaris_point_handling": PALLIKARIS_EXCLUSION_NOTE,
            "v_max_uL": float(v_max),
        }
        eye_id = "pallikaris_digitized"
    else:
        v_grid = np.linspace(0.0, float(v_max), int(n_pts))
        dp, meta = target_dp_on_grid(
            target, v_grid, p0=p0, p_cap=p_cap, pallikaris_mode=pallikaris_mode
        )
        rows = [ExpPoint(V_uL=float(v), P_mmHg=float(d)) for v, d in zip(v_grid, dp)]

    if target == "pallikaris":
        pass
    elif target == "friedenwald":
        eye_id = "friedenwald_wp0_recalibrated"
    elif target == "silver":
        eye_id = "silver_geyer_2000"
    elif target == "agra":
        eye_id = "agra_2023_bench"
    else:
        eye_id = target

    meta_path = path.with_suffix(".meta.json")
    meta_path.write_text(__import__("json").dumps({"target": target, **meta}, indent=2))
    _write_csv(path, rows, eye_id)
    return rows
