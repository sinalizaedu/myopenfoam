#!/usr/bin/env python3
"""Generate all charts for the Ogden-vs-Yeoh pretension investigation."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.optimize import brentq

OUT = Path(__file__).resolve().parent
FIGDIR = OUT / "figs"
FIGDIR.mkdir(exist_ok=True)

MU1, ALPHA1 = 7.1586, 0.5000000711
C10, C20 = 4.3639, 4.9950
C10_ALT, C20_ALT = 4.3663, 7.9909   # second Yeoh cluster (equally good fit)
D1_OGDEN = 1.0e-6
D1_YEOH = 0.12
R0_MM, T0_MM = 12.0, 0.5
P0_MMHG = 16.9
V_REF_UL = 10.0
MMHG_TO_MPA = 1.333223684e-4

plt.rcParams.update({"figure.dpi": 130, "font.size": 10.5, "axes.grid": True,
                      "grid.alpha": 0.3, "figure.autolayout": True})

# ---------------------------------------------------------------
# 1) Incompressible equibiaxial stress-stretch + tangent modulus
#    (illustrative range lambda in [1, 1.5] -- well beyond physiological,
#     to make the qualitative shapes visible)
# ---------------------------------------------------------------
lam = np.linspace(1.0001, 1.5, 400)

def sigma_ogden(l, mu1=MU1, a1=ALPHA1):
    return (2*mu1/a1)*(l**a1 - l**(-2*a1))

def sigma_yeoh(l, c10=C10, c20=C20):
    I1 = 2*l**2 + l**-4
    return 2*(l**2 - l**-4)*(c10 + 2*c20*(I1-3))

def dsigma(f, l, h=1e-6):
    return (f(l+h)-f(l-h))/(2*h)

fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))
ax = axes[0]
ax.plot(lam, sigma_ogden(lam), label="Ogden N=1 ($\\mu_1$=7.16, $\\alpha_1$=0.50)", lw=2, color="#1f77b4")
ax.plot(lam, sigma_yeoh(lam, C10, C20), label=f"Yeoh-2, C20=4.995 (Composer x0)", lw=2, color="#d62728")
ax.plot(lam, sigma_yeoh(lam, C10_ALT, C20_ALT), label=f"Yeoh-2, C20=7.991 (cluster global)", lw=2, ls="--", color="#ff7f0e")
ax.set_xlabel(r"estiramento equibiaxial $\lambda$")
ax.set_ylabel(r"$\sigma_{eq}$ [MPa]")
ax.set_title("Tensão de Cauchy equibiaxial (membrana incompressível)")
ax.legend(fontsize=8)

ax2 = axes[1]
ax2.plot(lam, dsigma(sigma_ogden, lam), label="Ogden N=1", lw=2, color="#1f77b4")
ax2.plot(lam, dsigma(lambda l: sigma_yeoh(l, C10, C20), lam), label="Yeoh-2 (C20=4.995)", lw=2, color="#d62728")
ax2.plot(lam, dsigma(lambda l: sigma_yeoh(l, C10_ALT, C20_ALT), lam), label="Yeoh-2 (C20=7.991)", lw=2, ls="--", color="#ff7f0e")
ax2.set_xlabel(r"estiramento equibiaxial $\lambda$")
ax2.set_ylabel(r"$d\sigma_{eq}/d\lambda$ [MPa]")
ax2.set_title("Módulo tangente material")
ax2.legend(fontsize=8)
fig.suptitle("Por que 'Ogden endurece / Yeoh amolece' NÃO se sustenta em pequenas deformações", fontsize=10.5, y=1.03)
fig.savefig(FIGDIR/"01_stress_stretch_tangent.png", bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------
# 2) Physiological-range P(V) curves (from the compressible model, dense)
# ---------------------------------------------------------------
curves = json.loads((OUT/"thin_shell_compressible_curves.json").read_text())
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))
ax = axes[0]
for name, c, color in [("ogden","Ogden N=1","#1f77b4"), ("yeoh","Yeoh-2","#d62728")]:
    V = np.array(curves[name]["V_mm3"])
    P = np.array(curves[name]["P_mmHg"])
    ax.plot(V - V[0], P, label=c, lw=2, color=color)
ax.axvline(V_REF_UL, color="gray", ls=":", lw=1, label=f"$V_{{ref}}$={V_REF_UL} µL")
ax.set_xlabel(r"$\Delta V$ injetado [µL]")
ax.set_ylabel("P [mmHg]")
ax.set_title("Curva P(V) — modelo casca-fina fechado\n(mesma faixa fisiológica da FEA)")
ax.legend(fontsize=9)

ax2 = axes[1]
for name, c, color in [("ogden","Ogden N=1","#1f77b4"), ("yeoh","Yeoh-2","#d62728")]:
    V = np.array(curves[name]["V_mm3"])
    K = np.array(curves[name]["K_mmHg_per_uL"])
    ax2.plot(V - V[0], K, label=c, lw=2, color=color)
ax2.axvline(V_REF_UL, color="gray", ls=":", lw=1)
ax2.set_xlabel(r"$\Delta V$ injetado [µL]")
ax2.set_ylabel(r"$K=dP/dV$ [mmHg/µL]")
ax2.set_title("K local ao longo da curva\n(modelo analítico: AMBOS amolecem ligeiramente)")
ax2.legend(fontsize=9)
fig.savefig(FIGDIR/"02_pv_and_k_analytic.png", bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------
# 3) The key comparison bar chart: analytic prediction vs FEA-reported
# ---------------------------------------------------------------
res = json.loads((OUT/"thin_shell_compressible_results.json").read_text())
labels = ["Ogden N=1", "Yeoh-2 (C20=4.995)"]
analytic = [res["ogden"]["rel_change_pct"], res["yeoh"]["rel_change_pct"]]
fea = [1.28, -37.5]

fig, ax = plt.subplots(figsize=(7.5, 4.6))
x = np.arange(2)
w = 0.35
b1 = ax.bar(x - w/2, analytic, w, label="Modelo analítico\n(casca fina, compressível)", color="#2ca02c")
b2 = ax.bar(x + w/2, fea, w, label="FEA octante (Composer,\nMULF two-step)", color="#9467bd")
ax.axhline(0, color="k", lw=0.8)
ax.set_xticks(x); ax.set_xticklabels(labels)
ax.set_ylabel("variação % de K entre V=0 e V_ref=10 µL")
ax.set_title("O modelo analítico NÃO reproduz a divergência de sinal/magnitude\nda FEA — o efeito de pré-tensão medido é provavelmente numérico")
for bars in (b1, b2):
    for r in bars:
        h = r.get_height()
        ax.annotate(f"{h:+.2f}%", (r.get_x()+r.get_width()/2, h),
                    textcoords="offset points", xytext=(0, 6 if h>=0 else -14),
                    ha="center", fontsize=9)
ax.legend(fontsize=9)
fig.savefig(FIGDIR/"03_analytic_vs_fea.png", bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------
# 4) Yeoh identifiability: two equally-good clusters give ~identical
#    analytic pretension sensitivity -> C20 is NOT the driver of -37.5%
# ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.0, 4.4))
clusters = ["C2: C10=4.36\nC20=4.99\n(cost=102.56)", "C1: C10=4.37\nC20=7.99\n(cost=102.39, 4/6 starts)"]
vals = [-0.340, -0.338]
bars = ax.bar(clusters, vals, color=["#d62728", "#ff7f0e"], width=0.5)
ax.axhline(-37.5, color="k", ls="--", lw=1.2, label="FEA reportado (-37.5%)")
ax.set_ylabel("variação % analítica de K (V=0 -> V_ref)")
ax.set_title("Os dois mínimos Yeoh (R² quase idêntico) preveem\na MESMA sensibilidade analítica -> C20 não explica o -37,5% da FEA")
for r, v in zip(bars, vals):
    ax.annotate(f"{v:+.3f}%", (r.get_x()+r.get_width()/2, v), textcoords="offset points",
                xytext=(0, -14), ha="center", fontsize=9)
ax.legend(fontsize=9, loc="lower right")
fig.savefig(FIGDIR/"04_yeoh_identifiability.png", bbox_inches="tight")
plt.close(fig)

print("Figuras salvas em:", FIGDIR)
for p in sorted(FIGDIR.glob("*.png")):
    print(" -", p.name)
