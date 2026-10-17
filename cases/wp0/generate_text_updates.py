#!/usr/bin/env python3
"""Gera TEXT_UPDATES.md: resultados vs referência e desvio Q_prod 2,4 vs calibrado."""
from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT_MD = REPO / "TEXT_UPDATES.md"

from goldmann_iop_solver import (  # noqa: E402
    FriedenwaldPV,
    Protocol,
    Q_PROD_HUMAN_TABLE_ROUNDED_UL_MIN,
    Wp0Timeline,
    lobue_return_metrics,
    protocol_humano_relatorio,
    simulate_wp0_timeline,
)
from wp0_report import (  # noqa: E402
    KF_RECAL,
    PAR_VOL,
    P0_H,
    REFLUX_DV,
    collect_metrics,
    protocol_humano,
    pv_humano_friedenwald,
    pv_humano_linear,
    reflux_metrics,
    run_par_scenario,
)


def _section44(proto, pv):
    def run(par_start, t_begin=0.0):
        tl = Wp0Timeline(
            t_begin_min=t_begin,
            t_end_min=40.0,
            par_start_min=par_start,
            par_volume_uL=PAR_VOL,
        )
        t, _, p, _ = simulate_wp0_timeline(proto, pv, tl)
        return t, p

    def iop_at(t, p, tq):
        return float(np.interp(tq, t, p))

    t0, p0 = run(None)
    tp, pp = run(-0.5, t_begin=-0.5)
    tt, pt = run(2.0)
    return {
        "sem_par_2min": iop_at(t0, p0, 2.0),
        "soheilian_2min": iop_at(tp, pp, 2.0) - iop_at(t0, p0, 2.0),
        "soheilian_30min": iop_at(tp, pp, 30.0) - iop_at(t0, p0, 30.0),
        "chang_15min": iop_at(tt, pt, 15.0) - iop_at(t0, p0, 15.0),
        "zaman_5min": iop_at(tt, pt, 5.0) - iop_at(t0, p0, 5.0),
        "zaman_30min": iop_at(tt, pt, 30.0) - iop_at(t0, p0, 30.0),
    }


def metrics_with_q_prod(q_prod: float) -> dict:
    proto = replace(protocol_humano(), Q_prod_uL_min=q_prod)
    pf = pv_humano_friedenwald()
    pl = pv_humano_linear()

    def peak_dyn(pv):
        tl = Wp0Timeline(0, 40, None, REFLUX_DV)
        _, _, _, m = simulate_wp0_timeline(proto, pv, tl)
        return m["P_peak_mmHg"]

    rf = reflux_metrics(pf)
    # reflux uses protocol_humano() internally — patch via temporary monkey: use simulate directly
    tl = Wp0Timeline(0, 3, REFLUX_DV)
    t, _, p, _ = simulate_wp0_timeline(proto, pf, tl)
    t_inj_end = proto.t_inj_start_min + proto.t_inj_dur_min
    i_pre = max(0, int(np.searchsorted(t, t_inj_end, side="right")) - 1)
    after = np.where(t > t_inj_end + 1e-12)[0]
    i_post = int(after[0]) if after.size else i_pre
    rf = {
        "P_peak": float(p[i_pre]),
        "P_post": float(p[i_post]),
        "drop": float(p[i_pre] - p[i_post]),
    }

    _, _, p0, _ = simulate_wp0_timeline(
        proto, pf, Wp0Timeline(0, 40, None, REFLUX_DV)
    )
    t2 = 2.0
    sem2 = float(np.interp(t2, simulate_wp0_timeline(proto, pf, Wp0Timeline(0, 40, None, REFLUX_DV))[0], p0))

    s44 = _section44(proto, pf)

    par_reat = run_par_scenario(pf, 0.5, 0.0)
    par_tard = run_par_scenario(pf, 2.0, 0.0)
    # run_par uses protocol_humano() — need custom
    def par_min(t_start, t_begin):
        tl = Wp0Timeline(t_begin, 40, t_start, PAR_VOL, REFLUX_DV)
        t, _, p, m = simulate_wp0_timeline(proto, pf, tl)
        return float(np.min(p[t >= t_start])), m["par_duration_min"] * 60

    rmin, rdur = par_min(0.5, 0.0)
    tmin, tdur = par_min(2.0, 0.0)

    return {
        "peak_friedenwald_dynamic": peak_dyn(pf),
        "peak_linear_dynamic": peak_dyn(pl),
        "reflux_friedenwald": rf,
        "sem_par_2min_friedenwald": sem2,
        "section_44": s44,
        "par_reativa_Pmin": rmin,
        "par_tardia_Pmin": tmin,
        "par_tardia_duration_s": tdur,
    }


def main() -> int:
    m_cal = collect_metrics()
    q_old = Q_PROD_HUMAN_TABLE_ROUNDED_UL_MIN
    m_old = metrics_with_q_prod(q_old)
    m_new = metrics_with_q_prod(protocol_humano().Q_prod_uL_min)

    def dev(key_path):
        # simplified peak comparison
        pk_old = m_old["peak_friedenwald_dynamic"]
        pk_new = m_new["peak_friedenwald_dynamic"]
        return abs(pk_new - pk_old)

    lobue = lobue_return_metrics()

    ref = {
        "peak_friedenwald": (32.90, 32.9018),
        "reflux_drop_friedenwald": (0.52, None),
        "sem_par_2min": (29.33, None),
        "soheilian_2min": (-12.48, None),
        "soheilian_30min": (-1.32, None),
        "chang_15min": (-4.77, None),
        "zaman_5min": (-10.75, None),
        "zaman_30min": (-1.68, None),
        "par_reativa_Pmin": (16.16, None),
        "par_tardia_Pmin": (14.99, None),
    }

    lines = [
        "# TEXT_UPDATES — resultados WP0 (código calibrado)",
        "",
        "Gerado por `cases/wp0/generate_text_updates.py`. **Não edita `.tex`.**",
        "",
        "## Desvio Q_prod Tabela (2,4) vs equilíbrio calibrado",
        "",
        f"| Grandeza | Δ (mmHg ou unidade) |",
        f"|---|---|",
        f"| Pico Friedenwald dinâmico | {abs(m_new['peak_friedenwald_dynamic'] - m_old['peak_friedenwald_dynamic']):.6f} mmHg |",
        f"| IOP sem par @ 2 min | {abs(m_new['sem_par_2min_friedenwald'] - m_old['sem_par_2min_friedenwald']):.6f} mmHg |",
        "",
        "## Resultados atuais vs referência (recalibrada, Q_prod calibrado)",
        "",
        "| Seção / grandeza | Referência | Código agora | Arquivo |",
        "|---|---:|---:|---|",
    ]

    pf = m_cal.peaks["friedenwald_no_par"]
    lines.append(f"| §3.3 pico dinâmico recal. | 32,90 | {pf:.4f} | wp0_report.py / simulate_wp0_timeline |")

    rf = m_cal.reflux["friedenwald"]
    lines.append(
        f"| §3.3 queda refluxo recal. | 0,52 | {rf['drop']:.4f} | wp0_report.py reflux_metrics |"
    )

    pl = m_cal.peaks["linear_no_par"]
    lines.append(f"| §3.3 pico linear din. | 25,03 | {pl:.4f} | wp0_report.py |")
    lines.append(
        f"| Fig.6 aumento linear | +8,13 | {pl - P0_H:.4f} | wp0_report.py plot_camada2 |"
    )
    lines.append(
        f"| Fig.6 aumento recal. | +16,00 | {pf - P0_H:.4f} | wp0_report.py plot_camada2 |"
    )

    s44_path = HERE / "output_wp0" / "verify_wp0_standards.json"
    if s44_path.is_file():
        s44 = json.loads(s44_path.read_text()).get("section_44_smoke_results", {})
        for label, key, refv in [
            ("§4.4 Soheilian 2 min", "soheilian_prof_vs_none_2min_mmHg", -12.48),
            ("§4.4 Soheilian 30 min", "soheilian_prof_vs_none_30min_mmHg", -1.32),
            ("§4.4 Chang 15 min", "chang_tardia_vs_none_15min_mmHg", -4.77),
            ("§4.4 Zaman 5 min", "zaman_tardia_vs_none_5min_mmHg", -10.75),
            ("§4.4 Zaman 30 min", "zaman_tardia_vs_none_30min_mmHg", -1.68),
        ]:
            got = s44.get(key, float("nan"))
            lines.append(f"| {label} | {refv} | {got:.3f} | verify_wp0_standards.py |")

    for key, par in m_cal.par.items():
        if "friedenwald" in key and "duration" not in key:
            dur = par.get("par_duration_s")
            if dur is not None:
                lines.append(f"| Paracentese {key} duração (s) | — | {dur:.3f} | goldmann_iop_solver events |")

    exc = lobue["P_peak_mmHg"] - lobue["P0_ref_mmHg"]
    f10 = lobue.get("fraction_excess_dissipated_at_10min", float("nan"))
    f50 = lobue.get("fraction_excess_dissipated_at_50min", float("nan"))
    lines.extend(
        [
            "",
            "## LoBue (§4.3)",
            "",
            f"| Métrica | Código |",
            f"|---|---:|",
            f"| t retorno <4 mmHg (min) | {lobue['t_return_min']:.4f} |",
            f"| P(600 s)-P0 (mmHg) | {lobue['delta_P_at_600s_mmHg']:.4f} |",
            f"| Queda pico→10 min (mmHg) | {lobue['drop_from_peak_at_10min_mmHg']:.4f} |",
            f"| Queda pico→30 min (mmHg) | {lobue['drop_from_peak_at_30min_mmHg']:.4f} |",
            f"| Queda pico→50 min (mmHg) | {lobue['drop_from_peak_at_50min_mmHg']:.4f} |",
            f"| Fig.5 fração excesso dissipada @ 10 min | {100*f10:.1f} % (excesso {exc:.4f} mmHg) |",
            f"| Fig.5 fração excesso dissipada @ 50 min | {100*f50:.1f} % |",
            "",
            "## τ (§4.2 / §4.1)",
            "",
            f"| Espécie / teste | Valor | Origem |",
            f"|---|---:|---|",
            f"| Coelho τ (6 casas) | {m_cal.tau['coelho_tau_min_6dp']:.6f} min | {m_cal.tau['coelho_tau_formula']} |",
            "",
            "## Changelog código",
            "",
            "- `goldmann_iop_solver.py`: Q_prod calibrado; paracentese por evento; LoBue expandido",
            "- `verify_ruffini.py`: teste §4.1",
            "- `wp1_octant_ur_rms.py`: RMS u_r (B12)",
            "",
        ]
    )

    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"Wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
