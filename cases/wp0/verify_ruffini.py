#!/usr/bin/env python3
"""wp0.tex §4.1 — verificação Ruffini et al. 2024 (modelo 0D linear, τ de decaimento).

Protocolo fixo (documentado no JSON de saída):
  - IVI: 50 µL em 6 s (Δt_inj = 0,1 min), t=0 = início da injeção
  - refluxo desligado, paracentese desligada, f_uv = 0
  - Q_prod = Q_in = 2,2 µL/min, P_ev = 8 mmHg, K = 1 mmHg/µL (C = 1 µL/mmHg)
  - C_out = Q_in / (P_eq - P_ev) com equilíbrio em P_eq

IOP basal P_eq = 15 mmHg (baseline do ajuste exponencial):
  - O resumo do wp0.tex §4.1 cita τ ≈ 3,18 min de Ruffini et al. (2024), IOVS 65(4):9,
    com Q_in, P_ev e complacência C = 1 µL/mmHg (K = 1 mmHg/µL).
  - O artigo reporta τ analítico arredondado (3,18 min), não um IOP basal isolado.
  - P_eq = 15 mmHg é a pressão de equilíbrio *deste teste*: com f_uv = 0,
    Q_in = C_out (P_eq - P_ev) e τ = 1/(C_out K) ⇒ P_eq - P_ev = Q_in / C_out = Q_in τ K
    ⇒ P_eq = P_ev + Q_in/(1/(τK)) = 8 + 2,2/(1/(3,18×1)) ≈ 15 mmHg (mesma conta com
    τ = 1/(C_out K) e C_out = Q_in/(P_eq-P_ev)).

Saídas:
  - tau_analytic_min = 1/(C_out·K)  (referência exata do linearizado)
  - tau_fit_min = ajuste log-linear P(t) ≈ P_eq + A exp(-t/τ), baseline P_eq fixa
  - Erros relativos vs tau_analytic; relatório usa forma "inferior a X" (tolerâncias RK + janela).
  - Sensibilidade: janelas [t_inj_end, 30], [3, 30] e [5, 20] min.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from goldmann_iop_solver import (  # noqa: E402
    Protocol,
    ThinShellPV,
    Wp0Timeline,
    simulate_wp0_timeline,
)

# --- Parâmetros Ruffini / wp0.tex §4.1 ---------------------------------------
RUFFINI_Q_IN = 2.2  # µL/min (produção = influxo em equilíbrio)
RUFFINI_P_EV = 8.0  # mmHg
RUFFINI_P_EQ = 15.0  # mmHg — ver docstring (consistência τ=3,18 min + balanço)
RUFFINI_K_MMHG_PER_UL = 1.0  # C = 1 µL/mmHg
RUFFINI_C_OUT = RUFFINI_Q_IN / (RUFFINI_P_EQ - RUFFINI_P_EV)
RUFFINI_V_INJ_UL = 50.0
RUFFINI_T_INJ_DUR_MIN = 0.1  # 6 s
RUFFINI_TAU_ARTICLE_ROUNDED_MIN = 3.18  # Ruffini et al. 2024 (resumo analítico)

RTOL = 1e-8
ATOL = 1e-10


def tau_analytic_min() -> float:
    return 1.0 / (RUFFINI_C_OUT * RUFFINI_K_MMHG_PER_UL)


def ruffini_protocol_and_pv() -> tuple[Protocol, ThinShellPV]:
    pv = ThinShellPV(12e-3, 0.5e-3, 3e6, 0.47, RUFFINI_P_EQ)
    pv.K_mmHg_per_uL = RUFFINI_K_MMHG_PER_UL
    proto = Protocol(
        P0_mmHg=RUFFINI_P_EQ,
        Pev_mmHg=RUFFINI_P_EV,
        Q_prod_uL_min=RUFFINI_Q_IN,
        C_out_uL_min_mmHg=RUFFINI_C_OUT,
        frac_uveoscleral=0.0,
        reflux_mode="none",
        par_mode="volume",
        par_enabled=False,
        V_inj_uL=RUFFINI_V_INJ_UL,
        t_inj_start_min=0.0,
        t_inj_dur_min=RUFFINI_T_INJ_DUR_MIN,
    )
    return proto, pv


def fit_tau_log_linear(
    t_min: np.ndarray,
    p_mmHg: np.ndarray,
    *,
    t_lo: float,
    t_hi: float,
    p_eq: float,
) -> float | None:
    """log(P - P_eq) ~ a - t/τ em [t_lo, t_hi]."""
    mask = (t_min >= t_lo - 1e-12) & (t_min <= t_hi + 1e-12)
    n = int(np.sum(mask))
    if n < 10:
        return None
    tt = t_min[mask]
    pp = p_mmHg[mask]
    if np.any(pp <= p_eq):
        return None
    y = np.log(pp - p_eq)
    slope, _ = np.linalg.lstsq(np.vstack([tt, np.ones_like(tt)]).T, y, rcond=None)[0]
    if slope >= 0:
        return None
    return float(-1.0 / slope)


def rel_err(measured: float, reference: float) -> float:
    if reference == 0:
        return float("nan")
    return abs(measured - reference) / abs(reference)


def report_less_than(err: float) -> str:
    """Bound for prose: err reported as '< X' with X = next power of 10 above err."""
    if err != err or err < 0:  # nan
        return "nan"
    if err == 0.0:
        return "< 1e-16"
    exp = math.ceil(math.log10(err))
    bound = 10.0**exp
    if bound <= err:
        bound *= 10.0
    return f"< {bound:.0e}".replace("e+0", "e").replace("e-0", "e-")


def main() -> int:
    proto, pv = ruffini_protocol_and_pv()
    t_inj_end = proto.t_inj_start_min + proto.t_inj_dur_min
    tl = Wp0Timeline(0.0, 80.0, par_start_min=None, instant_reflux_uL=0.0)
    t, _, p, _ = simulate_wp0_timeline(proto, pv, tl, rtol=RTOL, atol=ATOL)

    tau_a = tau_analytic_min()
    err_vs_article = rel_err(tau_a, RUFFINI_TAU_ARTICLE_ROUNDED_MIN)

    windows: dict[str, tuple[float, float]] = {
        "from_injection_end_to_30min": (t_inj_end, 30.0),
        "minutes_3_to_30": (3.0, 30.0),
        "minutes_5_to_20": (5.0, 20.0),
    }
    sensitivity: dict = {}
    fit_primary_key = "from_injection_end_to_30min"
    tau_fit_primary: float | None = None

    for name, (t_lo, t_hi) in windows.items():
        tau_f = fit_tau_log_linear(t, p, t_lo=t_lo, t_hi=t_hi, p_eq=RUFFINI_P_EQ)
        err = rel_err(tau_f, tau_a) if tau_f is not None else float("nan")
        sensitivity[name] = {
            "t_lo_min": t_lo,
            "t_hi_min": t_hi,
            "tau_fit_min": tau_f,
            "relative_error_vs_tau_analytic": err,
            "relative_error_report": report_less_than(err) if tau_f is not None else None,
        }
        if name == fit_primary_key:
            tau_fit_primary = tau_f

    errs = [
        sensitivity[k]["relative_error_vs_tau_analytic"]
        for k in sensitivity
        if sensitivity[k]["tau_fit_min"] is not None
    ]
    sens_ok = True
    sens_note = ""
    if len(errs) >= 2:
        emin, emax = min(errs), max(errs)
        ratio = emax / emin if emin > 0 else float("inf")
        sens_ok = ratio < 10.0  # mesma ordem de grandeza
        sens_note = f"max/min rel err ratio = {ratio:.4g} across fit windows"
    else:
        sens_note = "insufficient windows for sensitivity ratio"

    err_fit_vs_analytic = (
        rel_err(tau_fit_primary, tau_a) if tau_fit_primary is not None else float("nan")
    )

    setup = {
        "V_inj_uL": RUFFINI_V_INJ_UL,
        "t_inj_dur_s": RUFFINI_T_INJ_DUR_MIN * 60.0,
        "reflux": "none",
        "paracentesis": False,
        "frac_uveoscleral": 0.0,
        "C_out_formula": "Q_in/(P_eq-P_ev)",
        "fit_baseline_P_eq_mmHg": RUFFINI_P_EQ,
        "fit_primary_window": fit_primary_key,
        "integrator_rtol": RTOL,
        "integrator_atol": ATOL,
    }

    out = {
        "setup": setup,
        "parameters": {
            "P_eq_mmHg": RUFFINI_P_EQ,
            "P_eq_source": (
                "Equilíbrio do teste wp0 §4.1: Q_in=2.2, P_ev=8, K=1 mmHg/µL, f_uv=0; "
                "consistente com τ≈3.18 min de Ruffini et al. 2024 (IOVS 65(4):9) — "
                "o artigo cita τ analítico, não P_basal isolado."
            ),
            "P_ev_mmHg": RUFFINI_P_EV,
            "Q_in_uL_min": RUFFINI_Q_IN,
            "C_out_uL_min_mmHg": RUFFINI_C_OUT,
            "K_mmHg_per_uL": RUFFINI_K_MMHG_PER_UL,
        },
        "tau_analytic_min": tau_a,
        "tau_article_rounded_min": RUFFINI_TAU_ARTICLE_ROUNDED_MIN,
        "relative_error_analytic_vs_article_rounded": err_vs_article,
        "relative_error_analytic_vs_article_report": report_less_than(err_vs_article),
        "tau_fit_primary_min": tau_fit_primary,
        "relative_error_fit_vs_analytic": err_fit_vs_analytic,
        "relative_error_fit_vs_analytic_report": report_less_than(err_fit_vs_analytic),
        "fit_window_sensitivity": sensitivity,
        "sensitivity_same_order_of_magnitude": sens_ok,
        "sensitivity_note": sens_note,
    }

    path = HERE / "output_wp0" / "verify_ruffini.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2))

    print("=== Ruffini §4.1 verify ===")
    print(f"tau_analytic = {tau_a:.12f} min")
    print(f"tau_fit (primary, t>={t_inj_end:.4f} min) = {tau_fit_primary}")
    print(f"rel err fit vs analytic = {err_fit_vs_analytic:.6e}  ({out['relative_error_fit_vs_analytic_report']})")
    print(f"rel err analytic vs article τ=3.18 = {err_vs_article:.6e}  ({out['relative_error_analytic_vs_article_report']})")
    print("--- window sensitivity (rel err vs tau_analytic) ---")
    for name, row in sensitivity.items():
        print(f"  {name}: tau_fit={row['tau_fit_min']}, err={row['relative_error_vs_tau_analytic']}")
    print(f"sensitivity_ok (ratio < 10): {sens_ok} — {sens_note}")
    print(json.dumps(out, indent=2))

    ok = tau_fit_primary is not None and err_fit_vs_analytic < 1e-6 and sens_ok
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
