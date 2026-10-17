"""WP4.1 — cadeia IOP(t) → pressão de perfusão ocular → limiares temporais.

Consome IOP(t) do solver 0D (``cases/wp0/goldmann_iop_solver.py``) sem alterá-lo.
A integral de isquemia 𝓘 fica no item 4.2.
"""
from __future__ import annotations

from typing import Union

import numpy as np

Number = Union[float, int, np.ndarray]
_trapz = getattr(np, "trapezoid", None) or np.trapz


def _as_float_array(x: Number) -> np.ndarray:
    return np.asarray(x, dtype=float)


def map_mmhg(pas: Number, pad: Number) -> np.ndarray | float:
    """Pressão arterial média: PAD + (PAS − PAD) / 3."""
    pas_a, pad_a = _as_float_array(pas), _as_float_array(pad)
    out = pad_a + (pas_a - pad_a) / 3.0
    if np.ndim(out) == 0:
        return float(out)
    return out


def mopp(
    iop: Number,
    pas: Number,
    pad: Number,
    fator_braquial_oftalmica: float = 2.0 / 3.0,
) -> np.ndarray | float:
    """
    Mean ocular perfusion pressure (convencão usual com MAP braquial escalada).

    MOPP = fator_braquial_oftalmica * MAP − IOP
    """
    iop_a = _as_float_array(iop)
    map_v = map_mmhg(pas, pad)
    if np.isscalar(map_v):
        out = fator_braquial_oftalmica * map_v - iop_a
    else:
        out = fator_braquial_oftalmica * map_v - iop_a
    if np.ndim(out) == 0:
        return float(out)
    return out


def opp_diastolica(iop: Number, pad_oftalmica: Number) -> np.ndarray | float:
    """OPP diastólica: PAD oftálmica − IOP."""
    out = _as_float_array(pad_oftalmica) - _as_float_array(iop)
    if np.ndim(out) == 0:
        return float(out)
    return out


def opp_crit_efetivo(opp_crit_ref: float, phi_vasc: float = 1.0) -> float:
    """
    Limiar de OPP ajustado por reserva vascular (comorbidades).

    OPP_crit_efetivo = OPP_crit_ref * phi_vasc, com phi_vasc >= 1.
    """
    if phi_vasc < 1.0:
        raise ValueError(f"phi_vasc must be >= 1.0, got {phi_vasc}")
    return float(opp_crit_ref * phi_vasc)


def _tempo_iop_acima(t_min: np.ndarray, iop_mmhg: np.ndarray, limiar: float) -> float:
    """Minutos com IOP(t) > limiar (integração trapezoidal do indicador)."""
    t = np.asarray(t_min, dtype=float)
    iop = np.asarray(iop_mmhg, dtype=float)
    if t.shape != iop.shape:
        raise ValueError("t and iop_t must have the same shape")
    mask = iop > limiar
    if not np.any(mask):
        return 0.0
    return float(_trapz(mask.astype(float), t))


def pad_oftalmica_from_braquial(
    pad: Number, fator_braquial_oftalmica: float = 2.0 / 3.0
) -> np.ndarray | float:
    """Estimativa de PAD na artéria oftálmica a partir da PAD braquial."""
    pad_a = _as_float_array(pad)
    out = fator_braquial_oftalmica * pad_a
    if np.ndim(out) == 0:
        return float(out)
    return out


def aplicar_cadeia(
    t: np.ndarray,
    iop_t: np.ndarray,
    pas: float,
    pad: float,
    opp_crit_ref: float,
    fator_braquial: float = 2.0 / 3.0,
    phi_vasc: float = 1.0,
) -> dict:
    """
    Aplica IOP(t) → MOPP(t), OPP diastólica e métricas de limiar temporal.

    ``pad_oftalmica`` é estimada como ``fator_braquial * PAD`` (mesmo fator
    usado na linha de MAP para MOPP).
    """
    t_arr = np.asarray(t, dtype=float)
    iop_arr = np.asarray(iop_t, dtype=float)
    if t_arr.shape != iop_arr.shape:
        raise ValueError("t and iop_t must have the same shape")
    if t_arr.size < 1:
        raise ValueError("t and iop_t must be non-empty")

    mopp_t = mopp(iop_arr, pas, pad, fator_braquial_oftalmica=fator_braquial)
    mopp_t = np.asarray(mopp_t, dtype=float)
    pad_oft = pad_oftalmica_from_braquial(pad, fator_braquial)
    opp_d = opp_diastolica(iop_arr, pad_oft)
    opp_d = np.asarray(opp_d, dtype=float)
    crit_eff = opp_crit_efetivo(opp_crit_ref, phi_vasc)

    return {
        "t_min": t_arr,
        "iop_mmHg": iop_arr,
        "mopp": mopp_t,
        "opp_diast": opp_d,
        "opp_crit_efetivo": crit_eff,
        "opp_crit_ref": float(opp_crit_ref),
        "phi_vasc": float(phi_vasc),
        "MAP_mmHg": float(map_mmhg(pas, pad)),
        "T_acima_30": _tempo_iop_acima(t_arr, iop_arr, 30.0),
        "T_acima_40": _tempo_iop_acima(t_arr, iop_arr, 40.0),
        "T_acima_50": _tempo_iop_acima(t_arr, iop_arr, 50.0),
        "opp_minima_atingida": float(np.min(mopp_t)),
        "mopp_min_mmHg": float(np.min(mopp_t)),
        "opp_diast_min_mmHg": float(np.min(opp_d)),
    }
