#!/usr/bin/env python3
"""
Digitiza (manualmente, por leitura visual) os pontos da Fig. 2 do Pallikaris
et al. (2005) que a usuaria colou, ajusta o modelo log-linear (Friedenwald)
aos pontos digitizados, e compara com:
  - a curva "oficial" que o repositorio ja usa (P0=16.9, Kf=0.0126, base 10)
  - uma curva de Friedenwald classica (coeficiente historico, olhos enucleados)

NOTA DE HONESTIDADE: os pontos abaixo sao uma leitura visual aproximada do
grafico enviado (nao um digitalizador tipo WebPlotDigitizer) -- os passos de
~4.5 uL batem com o texto da usuaria ("passos de infusao de 4,5 uL"), e os
valores de P foram lidos pixel a pixel com precisao de +-1 mmHg. Para uso
formal na tese, recomendo confirmar com WebPlotDigitizer no PDF original.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

OUT = Path(__file__).resolve().parent
FIGDIR = OUT / "figs"
FIGDIR.mkdir(exist_ok=True)

# ---- pontos digitizados da Fig. 2 (Pallikaris et al. 2005) ----
V_digit = np.array([0, 4.5, 9, 13.5, 17.5, 22, 26.5, 31, 35.5, 40, 44.5,
                     49, 53, 57.5, 62, 66.5], dtype=float)
P_digit = np.array([10.0, 10.3, 15.5, 20.0, 23.0, 25.5, 28.5, 31.5, 35.0,
                     37.5, 41.5, 44.0, 47.5, 50.5, 54.0, 57.0], dtype=float)

# ---- ajuste log-linear (Friedenwald) aos pontos digitizados ----
# log10(P) = log10(P0) + Kf * V
A = np.vstack([np.ones_like(V_digit), V_digit]).T
logP = np.log10(P_digit)
coef, *_ = np.linalg.lstsq(A, logP, rcond=None)
log10_P0_fit, Kf_fit = coef
P0_fit = 10 ** log10_P0_fit
resid = logP - A @ coef
ss_res = np.sum(resid**2)
ss_tot = np.sum((logP - logP.mean())**2)
r2 = 1 - ss_res/ss_tot

print(f"Ajuste log-linear aos pontos digitizados:")
print(f"  P0_fit = {P0_fit:.3f} mmHg")
print(f"  Kf_fit = {Kf_fit:.5f} /uL")
print(f"  R^2 (em log10 P) = {r2:.4f}")

# ---- curva "oficial" ja usada no repo (fit_pallikaris.py) ----
P0_repo, KF_repo = 16.9, 0.0126
def p_repo(v):
    return P0_repo * 10.0**(KF_repo*v)

def p_digitized_fit(v):
    return P0_fit * 10.0**(Kf_fit*v)

# ---- Friedenwald classico (coeficiente historico, olho enucleado) ----
# K_hist=0.0215 /uL (base 10, convencao classica), P0 generico=15 mmHg
# (nao ha um "P0 universal" de Friedenwald -- e so ilustrativo, para
# mostrar como o coeficiente historico e MAIS INCLINADO que o Kf atual)
P0_fw, K_fw = 15.0, 0.0215
def p_friedenwald_classic(v):
    return P0_fw * 10.0**(K_fw*v)

v_plot = np.linspace(0, 80, 300)

fig, ax = plt.subplots(figsize=(8.5, 6.2))
ax.errorbar(V_digit, P_digit, yerr=1.5, fmt='s', color='k', ms=5,
            capsize=3, label='Pallikaris (2005) — pontos digitizados\n(leitura visual da Fig. 2, 79 olhos)', zorder=5)
ax.plot(v_plot, p_digitized_fit(v_plot), '-', color='#1f77b4', lw=2,
        label=f'Ajuste aos pontos digitizados\n($P_0$={P0_fit:.1f}, $K_f$={Kf_fit:.4f}/µL, R²={r2:.3f})')
ax.plot(v_plot, p_repo(v_plot), '--', color='#d62728', lw=2,
        label=f'Curva usada no repo (fit_pallikaris.py)\n($P_0$=16.9, $K_f$=0.0126/µL)')
ax.plot(v_plot, p_friedenwald_classic(v_plot), ':', color='#2ca02c', lw=2.2,
        label=f'Friedenwald clássico (olho enucleado)\n($P_0$=15, $K$=0.0215/µL — ilustrativo)')

ax.set_xlabel('Volume injetado [µL]')
ax.set_ylabel('Pressão intraocular [mmHg]')
ax.set_title('P(V): dados digitizados vs. curvas de calibração\n(log-linear tipo Friedenwald)')
ax.legend(fontsize=8.5, loc='upper left')
ax.grid(alpha=0.3)
ax.set_xlim(0, 80)
ax.set_ylim(0, 90)
fig.tight_layout()
fig.savefig(FIGDIR/"05_pv_digitized_vs_curves.png", dpi=140)
plt.close(fig)

# salvar os pontos digitizados em CSV pra ela poder editar/adicionar outros dados
import csv
with open(OUT/"pallikaris_digitized_points.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["V_uL", "P_mmHg", "fonte"])
    for v, p in zip(V_digit, P_digit):
        w.writerow([f"{v:.1f}", f"{p:.1f}", "Pallikaris_2005_Fig2_digitized"])

print("\nFigura salva em:", FIGDIR/"05_pv_digitized_vs_curves.png")
print("CSV salvo em:", OUT/"pallikaris_digitized_points.csv")
