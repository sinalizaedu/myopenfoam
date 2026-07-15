#!/usr/bin/env python3
"""Figura + tabela de independencia de malha do on-caso-1.2 (solido CalculiX).

QoI: deslocamento radial medio do anel da DURA (r=2.35, expansao da bainha) e da
PIA (r=1.55, compressao do nervo) em z=30 mm, sob carga SANS-equivalente
(3800 Pa na parede da SAS + 1333 Pa esclera + 9034 Pa arteria), C3D8, ccx
spooles. 3 niveis de refino global (x1, x1.25, x1.5).
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "cases", "on-caso-1.2", "_mesh_indep", "results_C3D8.json")

data = sorted(json.load(open(RES)), key=lambda x: x["n_eq"])
neq = [x["n_eq"] for x in data]
dura = [x["dura_mean_um"] for x in data]
pia = [x["pia_mean_um"] for x in data]
labels = [f"x{x['factor']:g}" for x in data]

# variacao percentual relativa ao nivel mais fino
def pct(series):
    fine = series[-1]
    return [100.0 * (v - fine) / abs(fine) for v in series]

fig, (ax, axp) = plt.subplots(1, 2, figsize=(12.6, 5.3))

# --- painel 1: QoI vs DOF ---
ax.plot(neq, dura, "o-", color="#c0392b", lw=2.2, ms=9, label="Dura (r=2.35) — expansão")
ax.plot(neq, pia, "s-", color="#2471a3", lw=2.2, ms=9, label="Pia (r=1.55) — compressão")
ax.axhline(0, color="0.6", lw=0.8)
for x, y, l in zip(neq, dura, labels):
    ax.annotate(l, (x, y), textcoords="offset points", xytext=(0, 10),
                ha="center", fontsize=8, color="#c0392b")
for x, y, l in zip(neq, pia, labels):
    ax.annotate(l, (x, y), textcoords="offset points", xytext=(0, -14),
                ha="center", fontsize=8, color="#2471a3")
ax.set_xscale("log")
ax.set_xlabel("graus de liberdade (nº de equações)")
ax.set_ylabel("desloc. radial médio do anel em z=30 mm  (µm)")
ax.set_title("Independência de malha — on-caso-1.2 (sólido C3D8)\n"
             "carga SANS-equivalente fixa (ICP 3800 Pa)", fontsize=11)
ax.legend(loc="center right")
ax.grid(True, which="both", alpha=0.3)

# --- painel 2: variacao SUCESSIVA (nivel i vs i-1) = diagnostico de convergencia
def succ(series):
    return [abs(series[i] - series[i - 1]) / abs(series[i]) * 100
            for i in range(1, len(series))]

axp.plot(neq[1:], succ(dura), "o-", color="#c0392b", lw=2.2, ms=9, label="Dura")
axp.plot(neq[1:], succ(pia), "s-", color="#2471a3", lw=2.2, ms=9, label="Pia")
axp.axhline(5, color="#1e8449", ls="--", lw=1.2)
axp.text(neq[1], 6, "critério 5%", color="#1e8449", fontsize=9, va="bottom")
for x, y in zip(neq[1:], succ(dura)):
    axp.annotate(f"{y:.1f}%", (x, y), textcoords="offset points", xytext=(0, 8),
                 ha="center", fontsize=8, color="#c0392b")
for x, y in zip(neq[1:], succ(pia)):
    axp.annotate(f"{y:.1f}%", (x, y), textcoords="offset points", xytext=(0, 8),
                 ha="center", fontsize=8, color="#2471a3")
axp.set_xscale("log")
axp.set_xlabel("graus de liberdade (nº de equações)")
axp.set_ylabel("variação sucessiva |Δ| entre níveis (%)")
axp.set_title("Diagnóstico de convergência (nível i vs i−1)\n"
              "dura: cai → converge   |   pia: cresce → locking (não converge)",
              fontsize=10)
axp.legend()
axp.grid(True, which="both", alpha=0.3)

fig.tight_layout()
out = os.path.join(ROOT, "brunaStuff", "figs", "on-caso-1.2-mesh-independence.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
fig.savefig(out, dpi=150)
print("figura ->", out)

# --- tabela ---
print(f"\n{'nivel':>7} {'n_eq':>8} {'dura(um)':>10} {'d% vs fino':>11} "
      f"{'pia(um)':>10} {'p% vs fino':>11}")
dp, pp = pct(dura), pct(pia)
for i, x in enumerate(data):
    print(f"{labels[i]:>7} {x['n_eq']:>8} {dura[i]:>10.4f} {dp[i]:>10.1f}% "
          f"{pia[i]:>10.4f} {pp[i]:>10.1f}%")

# variacao entre os dois niveis mais finos (criterio de independencia)
d_change = 100 * (dura[-1] - dura[-2]) / abs(dura[-1])
p_change = 100 * (pia[-1] - pia[-2]) / abs(pia[-1])
print(f"\nVariacao no ultimo refino (x{data[-2]['factor']:g} -> x{data[-1]['factor']:g}):")
print(f"  dura: {d_change:+.1f}%   pia: {p_change:+.1f}%")
