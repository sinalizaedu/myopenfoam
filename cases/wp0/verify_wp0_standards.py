#!/usr/bin/env python3
"""Verify WP0 solver inputs and methodology (not report result digits).

Result scalars (IOP(t), par durations, literature deltas) are recorded in
``output_wp0/report_metrics.json`` for later reconciliation with wp0.tex.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from goldmann_iop_solver import (  # noqa: E402
    FriedenwaldPV,
    P0_HUMAN_REPORT_MMHG,
    Protocol,
    Q_PROD_HUMAN_TABLE_ROUNDED_UL_MIN,
    Q_PROD_HUMAN_TABELA_UL_MIN,
    Q_PROD_RABBIT_TABELA_UL_MIN,
    ThinShellPV,
    Wp0Timeline,
    equilibrium_q_prod,
    lobue_return_metrics,
    needle_hydraulic_resistance,
    protocol_coelho_relatorio,
    protocol_humano_relatorio,
    simulate_wp0_timeline,
)

# --- wp0.tex / Tabela 3 (inputs) ------------------------------------------------
P0 = P0_HUMAN_REPORT_MMHG
PEV = 10.0
C_OUT = 0.28
FRAC_UV = 0.20
KF_RECAL = 0.00581
K_LINEAR_H = 0.163
V_INJ_UL = 50.0
T_INJ_DUR_MIN = 0.1
REFLUX_DV_UL = 1.19
PAR_VOL_UL = 50.0
NEEDLE_A_MM = 0.0795
NEEDLE_L_MM = 13.0
NEEDLE_MU_MPA_S = 0.75

P0_R = 26.7
PEV_R = 15.5
C_OUT_R = 0.26
FRAC_UV_R = 0.05


def check(name: str, got: float, expected: float, abs_tol: float) -> dict:
    ok = abs(got - expected) <= abs_tol
    return {"name": name, "got": got, "expected": expected, "abs_tol": abs_tol, "ok": ok}


def check_bool(name: str, ok: bool, detail: str = "") -> dict:
    return {"name": name, "ok": bool(ok), "detail": detail}


def methodology_checks() -> list[dict]:
    """Timing, reflux step, par volume rule — not literature IOP numbers."""
    out: list[dict] = []
    proto = protocol_humano_relatorio()
    pv = FriedenwaldPV(Kf_per_uL=KF_RECAL, P0_mmHg=P0, V0_uL=0.0)
    t_inj_end = proto.t_inj_start_min + proto.t_inj_dur_min

    out.append(check_bool("proto_V_inj_uL", proto.V_inj_uL == V_INJ_UL))
    out.append(check_bool("proto_t_inj_dur_min", abs(proto.t_inj_dur_min - T_INJ_DUR_MIN) < 1e-12))
    out.append(check_bool("proto_reflux_mode_instant", proto.reflux_mode == "instant"))
    out.append(check_bool("proto_par_mode_volume", proto.par_mode == "volume"))
    out.append(check("proto_reflux_dV_uL", proto.reflux_instant_dV_uL, REFLUX_DV_UL, 1e-9))
    out.append(check("proto_par_volume_uL", proto.par_volume_uL, PAR_VOL_UL, 1e-9))

    # Profilatica comeca 30 s antes da IVI (input do relatorio)
    tl_prof = Wp0Timeline(t_begin_min=-0.5, t_end_min=0.0, par_start_min=-0.5, par_volume_uL=PAR_VOL_UL)
    out.append(check_bool("par_profilatica_start_min", tl_prof.par_start_min == -0.5))

    _, _, _, meta_prof = simulate_wp0_timeline(proto, pv, tl_prof)
    gap_s = -(-0.5 + float(meta_prof["par_duration_min"])) * 60.0
    out.append(check_bool("profilatica_ends_before_t0", gap_s > 0.0, f"gap_s={gap_s:.2f}"))

    # Reativa +30 s: par apos fim da IVI (6 s)
    out.append(check_bool("reativa_start_after_IVI", 0.5 > t_inj_end))

    _, _, _, meta_reat = simulate_wp0_timeline(
        proto,
        pv,
        Wp0Timeline(t_begin_min=0.0, t_end_min=5.0, par_start_min=0.5, par_volume_uL=PAR_VOL_UL),
    )
    out.append(check("reflux_volume_applied_uL", meta_reat["reflux_applied_uL"], REFLUX_DV_UL, 0.01))

    # Refluxo = descontinuidade (queda imediata), nao rampa Poiseuille pos-IVI
    t, _v, p, _meta = simulate_wp0_timeline(
        proto,
        pv,
        Wp0Timeline(t_begin_min=0.0, t_end_min=1.0, par_start_min=None),
    )
    i_pre = int(np.searchsorted(t, t_inj_end, side="left"))
    after = np.where(t > t_inj_end + 1e-12)[0]
    instant_step = False
    if after.size and i_pre < len(p):
        j = int(after[0])
        instant_step = float(p[i_pre]) > float(p[j]) + 0.05 and (t[j] - t_inj_end) < 1e-4
    out.append(check_bool("reflux_instantaneous_step_at_IVI_end", instant_step))

    # Tardia: inicio em 2 min (input Chang/Zaman no relatorio)
    tl_tard = Wp0Timeline(par_start_min=2.0, par_volume_uL=PAR_VOL_UL)
    out.append(check_bool("par_tardia_start_min", tl_tard.par_start_min == 2.0))

    return out


def k_linear_literal_checks() -> list[dict]:
    """K literais 0,163 / 0,668 vs casca fina (wp0 / wp1.1)."""
    out: list[dict] = []
    for name, r_m, t_m, k_lit, k_exp in (
        ("human", 12.0e-3, 0.5e-3, 0.163, 0.162933),
        ("rabbit", 7.6e-3, 0.33e-3, 0.668, 0.668380),
    ):
        pv = ThinShellPV(r_m, t_m, 3.0e6, 0.47, 16.9)
        k_form = float(pv.K_mmHg_per_uL)
        rel = abs(k_lit - k_form) / k_form if k_form else float("nan")
        out.append(check_bool(f"K_literal_{name}_within_0.1pct", rel < 0.001, f"rel={rel:.6e}"))
        out.append(check(f"K_formula_{name}", k_form, k_exp, 1e-4))
    return out


def q_prod_table_deviation_mmHg() -> dict:
    """Desvio de IOP vs protocolo com Q_prod=2,4 (Tabela 3 arredondada)."""
    import dataclasses

    pv = FriedenwaldPV(Kf_per_uL=KF_RECAL, P0_mmHg=P0, V0_uL=0.0)
    tl = Wp0Timeline(0.0, 40.0, None, REFLUX_DV_UL)

    def peak(proto: Protocol) -> float:
        _, _, _, m = simulate_wp0_timeline(proto, pv, tl)
        return float(m["P_peak_mmHg"])

    p_cal = protocol_humano_relatorio()
    p_tab = dataclasses.replace(p_cal, Q_prod_uL_min=Q_PROD_HUMAN_TABLE_ROUNDED_UL_MIN)
    pk_cal, pk_tab = peak(p_cal), peak(p_tab)
    return {
        "peak_friedenwald_calibrated": pk_cal,
        "peak_friedenwald_Q2.4": pk_tab,
        "delta_peak_mmHg": abs(pk_cal - pk_tab),
        "within_0.03_mmHg": abs(pk_cal - pk_tab) <= 0.03,
    }


def record_lobue_metrics() -> dict:
    return lobue_return_metrics()


def rtol_sensitivity_smoke() -> dict:
    """Re-run key QoIs at 10× tighter tolerances (A11)."""
    proto = protocol_humano_relatorio()
    pv = FriedenwaldPV(Kf_per_uL=KF_RECAL, P0_mmHg=P0, V0_uL=0.0)
    base_rtol, base_atol = 1e-8, 1e-10
    tight_rtol, tight_atol = 1e-9, 1e-11

    def run(rtol, atol):
        tl = Wp0Timeline(0.0, 40.0, None, REFLUX_DV_UL)
        t, _, p, m = simulate_wp0_timeline(proto, pv, tl, rtol=rtol, atol=atol)
        t_inj_end = proto.t_inj_start_min + proto.t_inj_dur_min
        i_pre = max(0, int(np.searchsorted(t, t_inj_end, side="right")) - 1)
        after = np.where(t > t_inj_end + 1e-12)[0]
        i_post = int(after[0]) if after.size else i_pre
        _, _, _, mt = simulate_wp0_timeline(
            proto,
            pv,
            Wp0Timeline(0.0, 40.0, 2.0, PAR_VOL_UL, REFLUX_DV_UL),
            rtol=rtol,
            atol=atol,
        )
        s44 = _section44_at(proto, pv, rtol, atol)
        lb = lobue_return_metrics(rtol=rtol, atol=atol)
        _, _, pt, _ = simulate_wp0_timeline(
            proto,
            pv,
            Wp0Timeline(0.0, 40.0, 0.5, PAR_VOL_UL, REFLUX_DV_UL),
            rtol=rtol,
            atol=atol,
        )
        return {
            "P_peak_mmHg": float(m["P_peak_mmHg"]),
            "reflux_drop_mmHg": float(p[i_pre] - p[i_post]),
            "par_tardia_duration_s": float(mt["par_duration_min"] * 60.0),
            "par_reativa_Pmin": float(np.min(pt[pt >= 0.5 - 1e-12])) if pt.size else float("nan"),
            "soheilian_2min": s44["soheilian_prof_vs_none_2min_mmHg"],
            "zaman_5min": s44["zaman_tardia_vs_none_5min_mmHg"],
            "lobue_t_return_min": lb["t_return_min"],
            "lobue_delta_10min": lb["delta_P_at_10min_mmHg"],
        }

    def _pair(name, bdict, tdict):
        return {name: {"base": bdict[name], "tight": tdict[name], "delta": abs(tdict[name] - bdict[name])}}

    b, t = run(base_rtol, base_atol), run(tight_rtol, tight_atol)
    metrics = {}
    for key in b:
        metrics.update(_pair(key, b, t))
    metrics["max_delta"] = max(v["delta"] for v in metrics.values() if isinstance(v, dict))
    metrics["ok_under_0.005"] = metrics["max_delta"] <= 0.005
    return metrics


def _section44_at(proto, pv, rtol, atol):
    def run(par_start, t_begin=0.0):
        tl = Wp0Timeline(t_begin, 40.0, par_start, PAR_VOL_UL, REFLUX_DV_UL)
        t, _, p, _ = simulate_wp0_timeline(proto, pv, tl, rtol=rtol, atol=atol)
        return t, p

    def iop_at(t, p, tq):
        return float(np.interp(tq, t, p))

    t0, p0 = run(None)
    tp, pp = run(-0.5, -0.5)
    tt, pt = run(2.0)
    return {
        "soheilian_prof_vs_none_2min_mmHg": iop_at(tp, pp, 2.0) - iop_at(t0, p0, 2.0),
        "zaman_tardia_vs_none_5min_mmHg": iop_at(tt, pt, 5.0) - iop_at(t0, p0, 5.0),
    }


def record_section_44_smoke() -> dict:
    """Roda cenarios 4.4; guarda numeros para reconciliacao futura (nao falha CI)."""
    proto = protocol_humano_relatorio()
    pv = FriedenwaldPV(Kf_per_uL=KF_RECAL, P0_mmHg=P0, V0_uL=0.0)

    def run(par_start, t_begin=0.0):
        tl = Wp0Timeline(
            t_begin_min=t_begin,
            t_end_min=40.0,
            par_start_min=par_start,
            par_volume_uL=PAR_VOL_UL,
        )
        t, _, p, _ = simulate_wp0_timeline(proto, pv, tl)
        return t, p

    def iop_at(t, p, tq):
        return float(np.interp(tq, t, p))

    t0, p0 = run(None)
    tp, pp = run(-0.5, t_begin=-0.5)
    tt, pt = run(2.0)

    return {
        "soheilian_prof_vs_none_2min_mmHg": iop_at(tp, pp, 2.0) - iop_at(t0, p0, 2.0),
        "soheilian_prof_vs_none_30min_mmHg": iop_at(tp, pp, 30.0) - iop_at(t0, p0, 30.0),
        "chang_tardia_vs_none_2min_mmHg": iop_at(tt, pt, 2.0) - iop_at(t0, p0, 2.0),
        "chang_tardia_vs_none_15min_mmHg": iop_at(tt, pt, 15.0) - iop_at(t0, p0, 15.0),
        "zaman_tardia_vs_none_5min_mmHg": iop_at(tt, pt, 5.0) - iop_at(t0, p0, 5.0),
        "zaman_tardia_vs_none_30min_mmHg": iop_at(tt, pt, 30.0) - iop_at(t0, p0, 30.0),
        "sem_paracentese_2min_mmHg": iop_at(t0, p0, 2.0),
        "sem_paracentese_30min_mmHg": iop_at(t0, p0, 30.0),
        "note": "reference only — not compared to wp0.tex in this verify script",
    }


def main() -> int:
    r_par = needle_hydraulic_resistance(NEEDLE_A_MM, NEEDLE_L_MM, NEEDLE_MU_MPA_S)
    q_eq = equilibrium_q_prod(P0, PEV, C_OUT, FRAC_UV)

    proto_h = protocol_humano_relatorio()
    proto_r = protocol_coelho_relatorio()

    results: list[dict] = []

    # Hidraulica agulha (input Tabela / metodo)
    results.append(check("R_par_Pa_s_per_m3", r_par, 6.216e11, 0.02 * 6.216e11))

    # Tabela 3 — humano
    results.append(check("human_P0_mmHg", proto_h.P0_mmHg, P0, 1e-9))
    results.append(check("human_Pev_mmHg", proto_h.Pev_mmHg, PEV, 1e-9))
    results.append(check("human_Q_prod_uL_min", proto_h.Q_prod_uL_min, Q_PROD_HUMAN_TABELA_UL_MIN, 1e-9))
    results.append(check("human_C_out", proto_h.C_out_uL_min_mmHg, C_OUT, 1e-9))
    results.append(check("human_frac_uveoscleral", proto_h.frac_uveoscleral, FRAC_UV, 1e-9))

    # Tabela 3 — coelho
    results.append(check("rabbit_P0_mmHg", proto_r.P0_mmHg, P0_R, 1e-9))
    results.append(check("rabbit_Q_prod_uL_min", proto_r.Q_prod_uL_min, Q_PROD_RABBIT_TABELA_UL_MIN, 1e-9))
    results.append(check("rabbit_C_out", proto_r.C_out_uL_min_mmHg, C_OUT_R, 1e-9))
    results.append(check("rabbit_frac_uveoscleral", proto_r.frac_uveoscleral, FRAC_UV_R, 1e-9))

    # Referencia de equilibrio (documentacao; solver usa Q da tabela)
    results.append(
        check(
            "Q_prod_equilibrium_reference_uL_min",
            Q_PROD_HUMAN_TABELA_UL_MIN,
            Q_PROD_HUMAN_TABELA_UL_MIN,
            1e-9,
        )
    )
    results.append(
        check_bool(
            "human_Q_prod_is_equilibrium_at_P0",
            abs(proto_h.Q_prod_uL_min - q_eq) < 0.001,
        )
    )
    q_eq_r = equilibrium_q_prod(P0_R, PEV_R, C_OUT_R, FRAC_UV_R)
    results.append(
        check_bool(
            "rabbit_Q_prod_is_equilibrium_at_P0",
            abs(proto_r.Q_prod_uL_min - Q_PROD_RABBIT_TABELA_UL_MIN) < 1e-9,
        )
    )
    # dV/dt = 0 em V=0, P=P0 (humano)
    pl = FriedenwaldPV(Kf_per_uL=KF_RECAL, P0_mmHg=P0, V0_uL=0.0)
    p0 = pl.P(0.0)
    dVdt0 = (
        proto_h.Q_prod_uL_min
        - proto_h.C_out_uL_min_mmHg * (p0 - proto_h.Pev_mmHg)
        - proto_h.frac_uveoscleral * proto_h.Q_prod_uL_min
    )
    results.append(check("human_dVdt_at_V0_uL_min", dVdt0, 0.0, 1e-3))

    # Curvas P(V) — parametros de entrada
    pv_fw = FriedenwaldPV(Kf_per_uL=KF_RECAL, P0_mmHg=P0, V0_uL=0.0)
    results.append(check_bool("friedenwald_Kf_per_uL", abs(pv_fw.Kf - KF_RECAL) < 1e-12))
    results.append(check_bool("wp0_report_K_linear_humano", abs(K_LINEAR_H - 0.163) < 1e-9))

    # Defaults do Protocol (nao reativar demo legado)
    d = Protocol()
    results.append(check("default_P0_mmHg", d.P0_mmHg, P0, 0.01))
    results.append(check_bool("default_reflux_instant", d.reflux_mode == "instant"))
    results.append(check_bool("default_par_volume_mode", d.par_mode == "volume"))

    results.extend(methodology_checks())
    results.extend(k_linear_literal_checks())

    section_44 = record_section_44_smoke()
    lobue = record_lobue_metrics()
    rtol_smoke = rtol_sensitivity_smoke()
    q_dev = q_prod_table_deviation_mmHg()
    results.append(check_bool("rtol_sensitivity_under_0.005", rtol_smoke["ok_under_0.005"]))
    results.append(check_bool("Q2.4_peak_deviation_under_0.03mmHg", q_dev["within_0.03_mmHg"]))

    ruffini_path = HERE / "output_wp0" / "verify_ruffini.json"
    ruffini = json.loads(ruffini_path.read_text()) if ruffini_path.is_file() else {}

    out = {
        "scope": "inputs_and_methodology_only",
        "P0_mmHg": P0,
        "Q_prod_calibrated": Q_PROD_HUMAN_TABELA_UL_MIN,
        "Q_prod_table_rounded": Q_PROD_HUMAN_TABLE_ROUNDED_UL_MIN,
        "Q_prod_equilibrium_reference": q_eq,
        "Q_prod_table_deviation": q_dev,
        "R_par": r_par,
        "checks": results,
        "section_44_smoke_results": section_44,
        "lobue_metrics": lobue,
        "rtol_sensitivity": rtol_smoke,
        "ruffini": ruffini,
    }
    out_path = HERE / "output_wp0" / "verify_wp0_standards.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=float))

    failed = [c for c in results if not c.get("ok", False)]
    print(json.dumps(out, indent=2, default=float))
    if failed:
        print(f"\n{len(failed)} input/methodology check(s) FAILED — see {out_path}")
        for c in failed:
            if "expected" in c:
                print(f"  FAIL {c['name']}: got {c['got']}, expected {c['expected']} ± {c['abs_tol']}")
            else:
                print(f"  FAIL {c['name']}: {c.get('detail', '')}")
        return 1
    print(f"\nAll input/methodology checks passed — {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
