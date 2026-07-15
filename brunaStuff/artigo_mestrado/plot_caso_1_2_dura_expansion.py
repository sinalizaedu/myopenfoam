#!/usr/bin/env python3
"""Figura da resposta estrutural do FSI (on-caso-1.2, Caso 3, Neo-Hookeano base).

Le cases/on-caso-1.2/_grid/grid_fsi_results.json (modelo Neo-Hookeano, d=1e15)
e plota o deslocamento radial maximo no CORPO DO NERVO ao longo da rampa de PIC
(1333->3800 Pa): a DURA expande para fora (distensao da bainha, achado da SANS)
e a PIA (nervo) e' comprimida para dentro -> compartimentalizacao do espaco
subaracnoide perioptico. A resposta independe de d (governada pela PIC).

Saida: brunaStuff/figs/on-caso-1.2-dura-expansion.png
"""
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON = os.path.join(ROOT, "cases", "on-caso-1.2", "_grid", "grid_fsi_results.json")
MAT = "neohooke"
D_FIX = 1e15
PICS = [1333.0, 2000.0, 3000.0, 3800.0]


def load():
    rows = json.loads(open(JSON).read())
    pts = []
    for r in rows:
        if r.get("status") != "OK" or r["mat"] != MAT:
            continue
        if abs(r["d"] - D_FIX) / D_FIX > 1e-6:
            continue
        if not any(abs(r["p_target_pa"] - p) < 1.0 for p in PICS):
            continue
        pts.append((r["p_target_pa"], r["dura_ur_max_um"], r["pia_ur_max_um"]))
    pts = np.array(sorted(pts))
    return pts[:, 0], pts[:, 1], pts[:, 2]


icp, dura_um, pia_um = load()

fig, ax = plt.subplots(figsize=(8.4, 5.6))

ax.axhline(0.0, color="0.6", lw=0.8, zorder=0)
ax.plot(icp, dura_um, "o-", color="#c0392b", lw=2.2, ms=8,
        label="Dura (r=2.35 mm) — bainha")
ax.plot(icp, pia_um, "s-", color="#2471a3", lw=2.2, ms=8,
        label="Pia (r=1.55 mm) — nervo")

# faixas clinicas
ax.axvspan(1200, 1500, color="#2ecc71", alpha=0.12, zorder=0)
ax.axvspan(2660, 3800, color="#e74c3c", alpha=0.10, zorder=0)
ax.text(1350, dura_um.max() * 0.92, "saudável\n(~10 mmHg)", color="#1e8449",
        ha="center", va="top", fontsize=9)
ax.text(3230, dura_um.max() * 0.92, "SANS / IIH\n(>20 mmHg)", color="#a93226",
        ha="center", va="top", fontsize=9)

ax.annotate("dura expande\n(distensão da bainha)",
            xy=(icp[-1], dura_um[-1]), xytext=(2050, dura_um.max() * 0.7),
            color="#c0392b", fontsize=9, ha="center",
            arrowprops=dict(arrowstyle="->", color="#c0392b"))
ax.annotate("pia comprime\n(nervo apertado)",
            xy=(icp[-1], pia_um[-1]), xytext=(2050, pia_um.min() * 1.8),
            color="#2471a3", fontsize=9, ha="center",
            arrowprops=dict(arrowstyle="->", color="#2471a3"))

ax.set_xlabel("PIC na cisterna quiasmática — entrada da SAS (Pa)")
ax.set_ylabel("Deslocamento radial máximo no corpo do nervo (µm)\n"
              "(+ para fora / − para dentro)")
ax.set_title("on-caso-1.2 — FSI 2-way (Neo-Hookeano): resposta da bainha\n"
             "LCR pressuriza a SAS → bainha (dura) expande, nervo (pia) comprime",
             fontsize=11)
ax.legend(loc="center left", framealpha=0.95)
ax.grid(True, alpha=0.3)


def pa2mmhg(p): return p / 133.322
def mmhg2pa(m): return m * 133.322
secax = ax.secondary_xaxis("top", functions=(pa2mmhg, mmhg2pa))
secax.set_xlabel("PIC (mmHg)")

fig.tight_layout()
out = os.path.join(ROOT, "brunaStuff", "figs", "on-caso-1.2-dura-expansion.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
fig.savefig(out, dpi=150)
print("Figura salva em:", out)

print("\nPIC(Pa)   dura_Ur(um)   pia_Ur(um)")
for i in range(len(icp)):
    print(f"{icp[i]:7.0f}   {dura_um[i]:+10.3f}   {pia_um[i]:+10.3f}")
print(f"\nDistensao da dura (1333->3800 Pa): {dura_um[-1]-dura_um[0]:+.3f} um")
print(f"Compressao da pia  (1333->3800 Pa): {pia_um[-1]-pia_um[0]:+.3f} um")
