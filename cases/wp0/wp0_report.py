#!/usr/bin/env python3
"""Reproduce WP0 report (wp0.tex): simulations, metrics, and figure PNGs."""
from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from goldmann_iop_solver import (
    FriedenwaldPV,
    Protocol,
    Q_PROD_HUMAN_TABELA_UL_MIN,
    Q_PROD_RABBIT_TABELA_UL_MIN,
    ThinShellPV,
    Wp0Timeline,
    equilibrium_q_prod,
    needle_hydraulic_resistance,
    protocol_coelho_relatorio,
    protocol_humano_relatorio,
    simulate,
    simulate_wp0_timeline,
)

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT = HERE / "output_wp0"
FIG_OUT = OUT / "figures"
LATEX_FIG = REPO / "brunaStuff" / "latex" / "report" / "Figuras"

# --- Report constants (wp0.tex) ------------------------------------------------
P0_H = 16.9
PEV_H = 10.0
C_OUT_H = 0.28
F_UV_H = 0.20
KF_RECAL = 0.00581
K_LINEAR_H = 0.163
V_INJ = 50.0
T_INJ_DUR_MIN = 0.1
REFLUX_DV = 1.19
PAR_VOL = 50.0

P0_R = 26.7
PEV_R = 15.5
C_OUT_R = 0.26
F_UV_R = 0.05
K_LINEAR_R = 0.668

R_PAR = needle_hydraulic_resistance(0.0795, 13.0, 0.75)
E_PA = 3.0e6
R_H, T_H = 12.0e-3, 0.5e-3
R_R, T_R = 7.6e-3, 0.33e-3


def _thin(R_m: float, t_m: float, P0: float, K: float) -> ThinShellPV:
    pv = ThinShellPV(R_m=R_m, t_m=t_m, E_Pa=E_PA, nu=0.47, P0_mmHg=P0)
    pv.K_mmHg_per_uL = K
    return pv


def pv_humano_linear() -> ThinShellPV:
    return _thin(R_H, T_H, P0_H, K_LINEAR_H)


def pv_humano_friedenwald() -> FriedenwaldPV:
    return FriedenwaldPV(Kf_per_uL=KF_RECAL, P0_mmHg=P0_H)


def pv_coelho_linear() -> ThinShellPV:
    return _thin(R_R, T_R, P0_R, K_LINEAR_R)


def protocol_humano() -> Protocol:
    return protocol_humano_relatorio(
        R_par_Pa_s_per_m3=R_PAR,
        par_volume_uL=PAR_VOL,
        reflux_instant_dV_uL=REFLUX_DV,
    )


def protocol_coelho() -> Protocol:
    return protocol_coelho_relatorio(
        P0_mmHg=P0_R,
        Pev_mmHg=PEV_R,
        Q_prod_uL_min=Q_PROD_RABBIT_TABELA_UL_MIN,
        C_out_uL_min_mmHg=C_OUT_R,
        frac_uveoscleral=F_UV_R,
    )


def peak_static_at_v_inj(pv) -> float:
    """P(V_inj) estatico (sem escoamento durante a IVI)."""
    return float(pv.P(V_INJ))


def peak_dynamic_no_intervention(pv) -> float:
    """Pico do relatorio: max IOP(t) em t>=0, IVI + refluxo instantaneo, sem paracentese."""
    proto = protocol_humano()
    tl = Wp0Timeline(
        t_begin_min=0.0,
        t_end_min=40.0,
        par_start_min=None,
        instant_reflux_uL=REFLUX_DV,
    )
    _, _, _, meta = simulate_wp0_timeline(proto, pv, tl, r_par=R_PAR)
    return float(meta["P_peak_mmHg"])


def reflux_metrics(pv) -> dict:
    """Queda pos-refluxo na trajetoria dinamica (wp0.tex §3.3: 32,92 -> 32,40)."""
    proto = protocol_humano()
    tl = Wp0Timeline(t_begin_min=0, t_end_min=3, instant_reflux_uL=REFLUX_DV)
    t, _, p, _ = simulate_wp0_timeline(proto, pv, tl, r_par=R_PAR)
    t_inj_end = proto.t_inj_start_min + proto.t_inj_dur_min
    i_pre = int(np.searchsorted(t, t_inj_end, side="right")) - 1
    i_pre = max(0, min(i_pre, len(p) - 1))
    after = np.where(t > t_inj_end + 1e-12)[0]
    i_post = int(after[0]) if after.size else i_pre
    p_peak = float(p[i_pre])
    p_after = float(p[i_post])
    return {"P_peak": p_peak, "P_post_reflux": p_after, "drop": p_peak - p_after}


def run_par_scenario(pv, par_start_min: float, t_begin: float = 0.0) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    proto = protocol_humano()
    tl = Wp0Timeline(
        t_begin_min=t_begin,
        t_end_min=40.0,
        par_start_min=par_start_min,
        par_volume_uL=PAR_VOL,
        instant_reflux_uL=REFLUX_DV,
    )
    return simulate_wp0_timeline(proto, pv, tl, r_par=R_PAR)


def tau_minutes(C_out: float, K_mmHg_per_uL: float) -> float:
    return 1.0 / (C_out * K_mmHg_per_uL)


def k_local_friedenwald(P0: float = P0_H, kf: float = KF_RECAL) -> float:
    return np.log(10) * kf * P0


@dataclass
class ReportMetrics:
    peaks: dict
    reflux: dict
    par: dict
    tau: dict


def collect_metrics() -> ReportMetrics:
    pl = pv_humano_linear()
    pf = pv_humano_friedenwald()
    pr = pv_coelho_linear()

    peaks = {
        "peak_static_linear": peak_static_at_v_inj(pl),
        "peak_static_friedenwald": peak_static_at_v_inj(pf),
        "peak_dynamic_linear": peak_dynamic_no_intervention(pl),
        "peak_dynamic_friedenwald": peak_dynamic_no_intervention(pf),
        "linear_no_par": peak_dynamic_no_intervention(pl),
        "friedenwald_no_par": peak_dynamic_no_intervention(pf),
    }
    reflux = {
        "linear": reflux_metrics(pl),
        "friedenwald": reflux_metrics(pf),
    }
    par: dict = {}
    for name, t_start, t0 in (
        ("profilatica", -0.5, -0.5),
        ("reativa", 0.5, 0.0),
        ("tardia", 2.0, 0.0),
    ):
        for pv_name, pv in (("linear", pl), ("friedenwald", pf)):
            t, _, p, m = run_par_scenario(pv, t_start, t_begin=t0)
            key = f"{name}_{pv_name}"
            t_par = float(t_start)
            p_after_par = p[t >= t_par - 1e-12] if t.size else p
            par[key] = {
                "P_peak": float(np.max(p)),
                "P_min": float(np.min(p_after_par)) if p_after_par.size else float(np.min(p)),
                "par_duration_s": float(m["par_duration_min"] * 60.0),
                **m,
            }

    tau_coelho = tau_minutes(C_OUT_R, K_LINEAR_R)
    tau = {
        "humano_friedenwald_local_min": tau_minutes(C_OUT_H, k_local_friedenwald()),
        "coelho_linear_min": tau_coelho,
        "coelho_tau_min_6dp": round(tau_coelho, 6),
        "coelho_K_mmHg_per_uL": K_LINEAR_R,
        "coelho_C_out_uL_min_mmHg": C_OUT_R,
        "coelho_tau_formula": "1/(C_out*K) with K=0.668 literal (wp0.tex eq. casca fina), C_out=0.26 Tabela 3",
    }
    return ReportMetrics(peaks=peaks, reflux=reflux, par=par, tau=tau)


def _save(fig: plt.Figure, name: str) -> None:
    FIG_OUT.mkdir(parents=True, exist_ok=True)
    p1 = FIG_OUT / name
    fig.savefig(p1, dpi=160, bbox_inches="tight")
    if LATEX_FIG.is_dir():
        shutil.copy2(p1, LATEX_FIG / name)
    plt.close(fig)


def plot_linear_comparativo() -> None:
    vs = np.linspace(0, 60, 200)
    pl = pv_humano_linear()
    pc = pv_coelho_linear()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(vs, [pl.P(v) for v in vs], label=f"Humano ($P_0={P0_H}$ mmHg)")
    ax.plot(vs, [pc.P(v) for v in vs], label=f"Coelho ($P_0={P0_R}$ mmHg)")
    ax.set_xlabel("Volume relativo (µL)")
    ax.set_ylabel("IOP (mmHg)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    _save(fig, "fig1_linear_comparativo.png")


def plot_humano_friedenwald() -> None:
    vs = np.linspace(0, 55, 300)
    pl = pv_humano_linear()
    kfs = [("Pallikaris", 0.0126), ("Kazemi norm.", 0.0252), ("Recalibrado", KF_RECAL)]
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.plot(vs, [pl.P(v) for v in vs], "k-", lw=2, label="Linear ($K=0.163$)")
    colors = ["#888", "#aaa", "#6a3d9a"]
    for (lab, kf), c in zip(kfs, colors):
        fw = FriedenwaldPV(kf, P0_H)
        ax.plot(vs, [fw.P(v) for v in vs], color=c, label=f"Friedenwald $K_f={kf}$")
    ax.set_ylim(0, 120)
    ax.set_xlabel("Volume relativo (µL)")
    ax.set_ylabel("IOP (mmHg)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    _save(fig, "fig2_humano_friedenwald.png")


def plot_refluxo() -> None:
    proto = protocol_humano()
    fig, ax = plt.subplots(figsize=(9, 4))
    for pv, lab, col in (
        (pv_humano_linear(), "Linear", "#D85A30"),
        (pv_humano_friedenwald(), "Friedenwald recal.", "#378ADD"),
    ):
        tl0 = Wp0Timeline(t_begin_min=0, t_end_min=3, instant_reflux_uL=0.0)
        t0, _, p0, _ = simulate_wp0_timeline(proto, pv, tl0)
        tl1 = Wp0Timeline(t_begin_min=0, t_end_min=3, instant_reflux_uL=REFLUX_DV)
        t1, _, p1, _ = simulate_wp0_timeline(proto, pv, tl1)
        ax.plot(t0 * 60, p0, "--", color=col, alpha=0.45)
        ax.plot(t1 * 60, p1, "-", color=col, label=lab)
    ax.set_xlim(0, 180)
    ax.set_xlabel("Tempo (s)")
    ax.set_ylabel("IOP (mmHg)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    _save(fig, "fig_refluxo_humano.png")


def plot_paracentese() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
    specs = (
        ("Profilática (−30 s)", -0.5, -0.5),
        ("Reativa (+30 s)", 0.5, 0.0),
        ("Tardia (+2 min)", 2.0, 0.0),
    )
    for ax, (pv, title) in zip(
        axes,
        ((pv_humano_linear(), "Linear"), (pv_humano_friedenwald(), "Friedenwald recal.")),
    ):
        tl_base = Wp0Timeline(t_begin_min=0, t_end_min=40, instant_reflux_uL=REFLUX_DV)
        t_base, _, p_base, _ = simulate_wp0_timeline(protocol_humano(), pv, tl_base)
        ax.plot(t_base * 60, p_base, "k--", alpha=0.5, label="Sem paracentese")
        for lab, ts, tb in specs:
            t, _, p, _ = run_par_scenario(pv, ts, t_begin=tb)
            ax.plot(t * 60, p, label=lab)
        ax.set_title(title)
        ax.set_xlabel("Tempo (s)")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=7)
    axes[0].set_ylabel("IOP (mmHg)")
    fig.tight_layout()
    _save(fig, "fig_paracentese_3cenarios.png")


def plot_decaimento() -> None:
    proto_h = protocol_humano()
    proto_r = protocol_coelho()
    tl = Wp0Timeline(t_begin_min=0, t_end_min=40, instant_reflux_uL=REFLUX_DV)
    th, _, ph, _ = simulate_wp0_timeline(proto_h, pv_humano_friedenwald(), tl)
    tr, _, pr, _ = simulate_wp0_timeline(proto_r, pv_coelho_linear(), tl)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(th, ph, label=f"Humano Friedenwald ($P_0={P0_H}$)")
    ax.plot(tr, pr, label=f"Coelho linear ($P_0={P0_R}$)")
    ax.axhline(P0_H, color="C0", ls=":", lw=0.8)
    ax.axhline(P0_R, color="C1", ls=":", lw=0.8)
    ax.set_xlabel("Tempo (min)")
    ax.set_ylabel("IOP (mmHg)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    _save(fig, "fig_decaimento.png")


def plot_camada2_picos() -> None:
    """Model peaks vs literature (report Table)."""
    pl = pv_humano_linear()
    pf = pv_humano_friedenwald()
    model = {
        "Linear": peak_dynamic_no_intervention(pl),
        "Friedenwald recal.": peak_dynamic_no_intervention(pf),
    }
    lit = {
        "Knecht 2009": 33.0,
        "Hu 2022": 26.8,
        "Papazoglou 2026": 31.15,
        "Sharei 2010": 47.9,
    }
    fig, ax = plt.subplots(figsize=(9, 4))
    x = np.arange(len(lit))
    w = 0.35
    ax.bar(x - w / 2, list(lit.values()), w, label="Literatura (pico)", color="#aaa")
    ax.axhline(model["Linear"], color="#D85A30", ls="--", label=f"Modelo linear ({model['Linear']:.1f})")
    ax.axhline(model["Friedenwald recal."], color="#378ADD", ls="-", label=f"Modelo recal. ({model['Friedenwald recal.']:.1f})")
    ax.set_xticks(x)
    ax.set_xticklabels(list(lit.keys()), rotation=20, ha="right")
    ax.set_ylabel("IOP pico (mmHg)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    _save(fig, "fig_camada2_picos.png")


def compare_to_report(metrics: ReportMetrics) -> dict:
    """Expected scalars from wp0.tex vs simulation."""
    exp = {
        "peak_linear": 25.0,
        "peak_friedenwald": 32.9,
        "reflux_drop_linear": 0.194,
        "reflux_drop_friedenwald": 0.520,
        "par_profilatica_linear_s": 18.8,
        "par_profilatica_friedenwald_s": 19.6,
        "par_reativa_linear_s": 11.4,
        "par_reativa_friedenwald_s": 10.4,
        "par_tardia_linear_s": 11.7,
        "par_tardia_friedenwald_s": 11.2,
        "peak_profilatica_linear": 17.0,
        "peak_profilatica_friedenwald": 17.1,
        "tau_humano_min": 15.8,
        "tau_coelho_min": 5.76,
    }
    got = {
        "peak_linear": metrics.peaks["linear_no_par"],
        "peak_friedenwald": metrics.peaks["friedenwald_no_par"],
        "reflux_drop_linear": metrics.reflux["linear"]["drop"],
        "reflux_drop_friedenwald": metrics.reflux["friedenwald"]["drop"],
        "par_profilatica_linear_s": metrics.par["profilatica_linear"]["par_duration_s"],
        "par_profilatica_friedenwald_s": metrics.par["profilatica_friedenwald"]["par_duration_s"],
        "par_reativa_linear_s": metrics.par["reativa_linear"]["par_duration_s"],
        "par_reativa_friedenwald_s": metrics.par["reativa_friedenwald"]["par_duration_s"],
        "par_tardia_linear_s": metrics.par["tardia_linear"]["par_duration_s"],
        "par_tardia_friedenwald_s": metrics.par["tardia_friedenwald"]["par_duration_s"],
        "peak_profilatica_linear": metrics.par["profilatica_linear"]["P_peak"],
        "peak_profilatica_friedenwald": metrics.par["profilatica_friedenwald"]["P_peak"],
        "tau_humano_min": metrics.tau["humano_friedenwald_local_min"],
        "tau_coelho_min": metrics.tau["coelho_linear_min"],
    }
    tol = {
        "peak_linear": 0.4,
        "peak_friedenwald": 0.6,
        "reflux_drop_linear": 0.08,
        "reflux_drop_friedenwald": 0.12,
        "par_profilatica_linear_s": 1.5,
        "par_profilatica_friedenwald_s": 1.5,
        "par_reativa_linear_s": 1.5,
        "par_reativa_friedenwald_s": 1.5,
        "par_tardia_linear_s": 1.5,
        "par_tardia_friedenwald_s": 1.5,
        "peak_profilatica_linear": 1.0,
        "peak_profilatica_friedenwald": 1.0,
        "tau_humano_min": 0.8,
        "tau_coelho_min": 0.4,
    }
    checks = []
    for k, expected in exp.items():
        g = got[k]
        ok = bool(abs(float(g) - expected) <= tol[k])
        checks.append(
            {
                "name": k,
                "expected": expected,
                "got": float(g),
                "tol": tol[k],
                "ok": ok,
            }
        )
    return {"checks": checks, "R_par": float(R_PAR)}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    metrics = collect_metrics()
    comparison = compare_to_report(metrics)
    (OUT / "report_metrics.json").write_text(
        json.dumps({**comparison, "metrics_raw": asdict(metrics)}, indent=2, default=float)
    )

    plot_linear_comparativo()
    plot_humano_friedenwald()
    plot_refluxo()
    plot_paracentese()
    plot_decaimento()
    plot_camada2_picos()

    failed = [c for c in comparison["checks"] if not c["ok"]]
    print(json.dumps(comparison["checks"], indent=2))
    if failed:
        print(
            f"\n{len(failed)} result scalar(s) differ from wp0.tex (informational only) — "
            f"see {OUT / 'report_metrics.json'}"
        )
    else:
        print("\nAll recorded result scalars match wp0.tex tolerances (informational).")
    print(f"Figures written — {FIG_OUT} (copied to {LATEX_FIG})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
