#!/usr/bin/env python3
"""
Grafico combinado P(V): Pallikaris (digitizado), curva do repo (WP1.2),
Friedenwald classico, Silver & Geyer (2000) com coeficientes exatos,
Agra et al. (2023) modelo de bancada, E as duas curvas do proprio WP0
da usuaria (linear thin-shell e Friedenwald recalibrado contra Knecht).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.optimize import brentq

OUT = Path(__file__).resolve().parent
FIGDIR = OUT / "figs"
FIGDIR.mkdir(exist_ok=True)

P0 = 16.9  # basal do WP0, usado como referencia em todas as curvas

# ---- Pallikaris digitizado (Fig. 2, leitura visual) ----
V_pk = np.array([0, 4.5, 9, 13.5, 17.5, 22, 26.5, 31, 35.5, 40, 44.5,
                  49, 53, 57.5, 62, 66.5], dtype=float)
P_pk = np.array([10.0, 10.3, 15.5, 20.0, 23.0, 25.5, 28.5, 31.5, 35.0,
                  37.5, 41.5, 44.0, 47.5, 50.5, 54.0, 57.0], dtype=float)
A = np.vstack([np.ones_like(V_pk), V_pk]).T
logP = np.log10(P_pk)
coef, *_ = np.linalg.lstsq(A, logP, rcond=None)
P0_fit, Kf_fit = 10**coef[0], coef[1]
def p_digit_fit(v): return P0_fit * 10.0**(Kf_fit*v)

# ---- curva "oficial" do repo (WP1.2, Pallikaris bruto ate 80mmHg) ----
KF_repo = 0.0126
def p_repo(v): return P0 * 10.0**(KF_repo*v)

# ---- Friedenwald classico (ilustrativo, olho enucleado) ----
def p_friedenwald_classic(v): return P0 * 10.0**(0.0215*v)

# ---- WP0: forma linear (casca fina, K=0.163 mmHg/uL, humano) ----
K_LINEAR_WP0 = 0.163
def p_wp0_linear(v): return P0 + K_LINEAR_WP0*v

# ---- WP0: Friedenwald recalibrado contra Knecht (Kf=0.00581) ----
KF_WP0_RECAL = 0.00581
def p_wp0_recal(v): return P0 * 10.0**(KF_WP0_RECAL*v)

# ---- Silver & Geyer (2000) -- coeficientes exatos do artigo ----
def dV_silver(p): return -49.8 + 30.2*np.log(p) + 0.242*p
def v_inj_silver(p, p0=P0): return dV_silver(p) - dV_silver(p0)
def p_from_v_silver(v_target, p0=P0, p_hi=400.0):
    f = lambda p: v_inj_silver(p, p0) - v_target
    return brentq(f, p0, p_hi)

# ---- Agra et al. (2023) -- Tabela 2, bancada hidraulica ----
V_agra = np.array([20, 30, 40, 50, 60, 70, 80], dtype=float)
P_agra = np.array([32.3, 36.5, 43.5, 50.7, 65.4, 70.5, 76.5], dtype=float)
P_agra_sd = np.array([1.4, 2.7, 0.4, 0.1, 4.3, 1.8, 1.0], dtype=float)

# ---- pontos clinicos reais (Tabela literatura_master do WP0), pico p/ 50uL ----
clin_labels = ["Soheilian'17\n(sem parac.)", "Sharei'10", "Hu'22", "Papazoglou'26",
               "Knecht'09\n(reta)"]
clin_V = np.array([50, 50, 50, 50, 50], dtype=float)
clin_P = np.array([40.6, 47.9, 26.80, 31.15, 30.19], dtype=float)

v_plot = np.linspace(0.01, 80, 300)
p_silver_curve = np.array([p_from_v_silver(v) for v in v_plot])

fig, ax = plt.subplots(figsize=(10.5, 7.5))

ax.errorbar(V_pk, P_pk, yerr=1.5, fmt='s', color='k', ms=5, capsize=3,
            label='Pallikaris (2005) digitizado (79 olhos)', zorder=6)
ax.plot(v_plot, p_digit_fit(v_plot), '-', color='#1f77b4', lw=1.6,
        label=f'Ajuste ao Pallikaris digitizado ($K_f$={Kf_fit:.4f})')
ax.plot(v_plot, p_repo(v_plot), '--', color='#d62728', lw=2,
        label='WP1.2 atual (Pallikaris bruto, $K_f$=0.0126, até 80mmHg)')
ax.plot(v_plot, p_friedenwald_classic(v_plot), ':', color='#7f7f7f', lw=1.6,
        label='Friedenwald clássico (enucleado, K=0.0215 — ilustrativo)')
ax.plot(v_plot, p_wp0_linear(v_plot), '-', color='#2ca02c', lw=2.2,
        label='WP0 forma linear (casca fina, K=0.163)')
ax.plot(v_plot, p_wp0_recal(v_plot), '-', color='#9467bd', lw=2.6,
        label='WP0 Friedenwald recalibrado ($K_f$=0.00581) — ALVO ADOTADO')
ax.plot(v_plot, p_silver_curve, '-.', color='#e377c2', lw=1.8,
        label='Silver & Geyer (2000), olho médio')
ax.errorbar(V_agra, P_agra, yerr=P_agra_sd, fmt='^', color='#8c564b', ms=7,
            capsize=3, label='Agra et al. (2023) — bancada hidráulica (não é olho)', zorder=6)
ax.scatter(clin_V, clin_P, marker='D', s=55, color='#bcbd22', zorder=7,
           label='Picos clínicos reais @ 50µL (Tabela WP0)', edgecolor='k', linewidth=0.5)
for lbl, v, p in zip(clin_labels, clin_V, clin_P):
    ax.annotate(lbl, (v, p), textcoords="offset points", xytext=(6, -2), fontsize=6.5)

ax.axvline(50, color='gray', ls=':', lw=1, alpha=0.6)
ax.text(51, 85, '50 µL\n(IVI padrão)', fontsize=8, color='gray')

ax.set_xlabel('Volume injetado [µL]', fontsize=11)
ax.set_ylabel('Pressão intraocular [mmHg]', fontsize=11)
ax.set_title('P(V): todas as fontes — o alvo do WP1.2 (vermelho) diverge\ndo alvo já validado no WP0 (roxo) e dos picos clínicos reais',
             fontsize=12)
ax.legend(fontsize=7.3, loc='upper left', framealpha=0.95, ncol=1)
ax.grid(alpha=0.3)
ax.set_xlim(0, 82)
ax.set_ylim(0, 95)
fig.tight_layout()
fig.savefig(FIGDIR/"06_pv_all_sources_combined.png", dpi=140)
plt.close(fig)

print("Salvo:", FIGDIR/"06_pv_all_sources_combined.png")
print(f"\nEm V=50uL:")
print(f"  WP1.2 atual (Pallikaris bruto): {p_repo(50):.1f} mmHg")
print(f"  WP0 recalibrado (alvo adotado): {p_wp0_recal(50):.1f} mmHg")
print(f"  WP0 linear:                     {p_wp0_linear(50):.1f} mmHg")
print(f"  Media picos clinicos reais:      {clin_P.mean():.1f} mmHg")
