"""Map LHS sample rows → geometry and material for WP1.4 sweep_full.

All modeling assumptions are documented in ../MODELING_NOTES.md.
"""
from __future__ import annotations

import math
from typing import Any

P0_MMHG = 16.9
P_FINAL_MMHG = 50.0
N_STEPS = 16

MU1_NOMINAL = 2.2708230587169704
ALPHA1_NOMINAL = 1.05617628707085
ACD_NOMINAL_MM = 3.25

LENS_DR_MM = {
    "phakic": 0.0,
    "pseudophakic": -0.22,
    "aphakic": 0.35,
}


def p_targets(p_final: float = P_FINAL_MMHG, n_steps: int = N_STEPS, p0: float = P0_MMHG) -> list[float]:
    return [p0 + (p_final - p0) * i / n_steps for i in range(1, n_steps + 1)]


def thickness_at_colatitude(
    theta_rad: float,
    t_equatorial_mm: float,
    t_posterior_mm: float,
    *,
    theta_min_rad: float,
    theta_max_rad: float = math.pi / 2.0,
) -> float:
    """Cosine blend: t_posterior at θ→θ_min (posterior pole), t_equatorial at θ→90°."""
    denom = max(theta_max_rad - theta_min_rad, 1e-9)
    u = (float(theta_rad) - theta_min_rad) / denom
    u = min(1.0, max(0.0, u))
    blend = 0.5 * (1.0 - math.cos(math.pi * u))
    return float(t_posterior_mm + (t_equatorial_mm - t_posterior_mm) * blend)


def _parse_bool(v: Any) -> bool:
    return v in (True, "True", "true", "sim", "Sim", 1, "1")


def resolve_case(row: dict, *, theta_min_deg: float = 3.0) -> dict:
    """Build resolved parameters for mesh, deck, and post-processing."""
    al = float(row["comprimento_axial_mm"])
    t_eq = float(row["t_equatorial_mm"])
    t_post = float(row["t_posterior_mm"])
    mu1 = float(row.get("mu1_MPa") or MU1_NOMINAL * float(row["mu1_factor"]))
    alpha1 = float(row.get("alpha1") or ALPHA1_NOMINAL * float(row["alpha1_factor"]))
    acd = float(row["ACD_mm"])
    lens = str(row.get("lens_status", "phakic")).lower()
    if lens not in LENS_DR_MM:
        lens = "phakic"
    vit = _parse_bool(row.get("vitrectomy", False))

    r_base = al / 2.0
    dr_acd = -0.11 * (acd - ACD_NOMINAL_MM)
    dr_lens = LENS_DR_MM[lens]
    r_mm = r_base + dr_acd + dr_lens

    theta_min = math.radians(theta_min_deg)
    # Representative thickness for FRD→midsurface mapping (volume-weighted in θ)
    n_s = 32
    ts = [
        thickness_at_colatitude(
            theta_min + (math.pi / 2.0 - theta_min) * k / (n_s - 1),
            t_eq,
            t_post,
            theta_min_rad=theta_min,
        )
        for k in range(n_s)
    ]
    t_mean_mm = sum(ts) / len(ts)

    vit_dv_scale = 1.085 if vit else 1.0

    return {
        "R_mm": round(r_mm, 4),
        "R_base_mm": round(r_base, 4),
        "t_equatorial_mm": t_eq,
        "t_posterior_mm": t_post,
        "t_mean_mm": round(t_mean_mm, 5),
        "mu1_MPa": mu1,
        "alpha1": alpha1,
        "ACD_mm": acd,
        "lens_status": lens,
        "vitrectomy": vit,
        "dr_acd_mm": round(dr_acd, 4),
        "dr_lens_mm": round(dr_lens, 4),
        "vit_dv_scale": vit_dv_scale,
        "theta_min_deg": theta_min_deg,
        "modeling": {
            "R": "AL/2 + dr_acd + dr_lens (ACD and lens shift mid-surface radius)",
            "thickness": "t(θ) cosine blend equator↔posterior pole; FE via banded shell sections",
            "vitrectomy": f"dV_uL × {vit_dv_scale} after FE (no vitreous cavity in model)",
        },
    }


def nominal_row() -> dict:
    return {
        "case_id": "NOMINAL",
        "comprimento_axial_mm": 25.0,
        "t_equatorial_mm": 0.55,
        "t_posterior_mm": 0.9,
        "mu1_factor": 1.0,
        "alpha1_factor": 1.0,
        "ACD_mm": ACD_NOMINAL_MM,
        "lens_status": "phakic",
        "vitrectomy": False,
        "mu1_MPa": MU1_NOMINAL,
        "alpha1": ALPHA1_NOMINAL,
    }
