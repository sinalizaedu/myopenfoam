#!/usr/bin/env python3
"""Figura de compartimentalizacao do LCR (on-caso-1.2), grade PIC x d.

Le cases/on-caso-1.2/_grid/coupled_q_nh.json (vazao de drenagem Q medida no
lado FLUIDO do FSI ACOPLADO, modelo Neo-Hookeano de base, modo pressao-prescrita)
e plota Q vs d (log-log) para cada PIC alvo. As retas paralelas de inclinacao
-1 evidenciam o escalamento de Darcy puro (Q cai 100x por 100x em d) e a
separacao vertical reflete Q ~ PIC (a d fixo).

Saida: brunaStuff/figs/on-caso-1.2-comp-grid.png
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parent.parent
JSON = REPO / "cases" / "on-caso-1.2" / "_grid" / "coupled_q_nh.json"
OUT = REPO / "brunaStuff" / "figs" / "on-caso-1.2-comp-grid.png"

PICS = [1333, 2000, 3000, 3800]
DS = [1e15, 1e17, 1e19]


def load():
    blob = json.loads(JSON.read_text())
    table = {}  # (round PIC, round log10 d) -> Q
    for pic_str, qs in blob["q_by_pic"].items():
        for d, q in zip(blob["d_values"], qs):
            table[(round(float(pic_str)), round(np.log10(d)))] = q
    return table


def main():
    t = load()
    fig, ax = plt.subplots(figsize=(7.0, 5.2))
    colors = ["#1f77b4", "#2ca02c", "#ff7f0e", "#d62728"]
    for pic, c in zip(PICS, colors):
        q = [t[(pic, round(np.log10(d)))] for d in DS]
        ax.loglog(DS, q, "o-", color=c, lw=2, ms=8, label=f"PIC = {pic} Pa")

    # faixas de regime
    ax.axhspan(5e-12, 5e-11, color="green", alpha=0.07)
    ax.text(1.05e15, 3.2e-11, "fisiológico", fontsize=8, color="green", alpha=0.8)
    ax.axhspan(1e-16, 1e-14, color="red", alpha=0.06)
    ax.text(1.3e18, 1.3e-15, "compartimentalizado\n(SANS/IIH)", fontsize=8,
            color="firebrick", alpha=0.85, ha="center")

    ax.set_xlabel(r"Coeficiente de Darcy $d$ (m$^{-2}$)", fontsize=11)
    ax.set_ylabel(r"Vazão de drenagem $Q$ (m$^3$/s)", fontsize=11)
    ax.set_title(r"Compartimentalização do LCR: $Q \propto 1/d$ (Darcy puro)" "\n"
                 "(PIC fixa no inlet; cada reta uma PIC alvo)", fontsize=11)
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=9, loc="upper right")
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=140, bbox_inches="tight")
    print(f"saved -> {OUT}")

    # tabela no terminal (conferencia)
    print(f"\n{'PIC':>6} | {'d=1e15':>11} {'d=1e17':>11} {'d=1e19':>11}")
    for pic in PICS:
        qs = [t[(pic, round(np.log10(d)))] for d in DS]
        print(f"{pic:>6} | " + " ".join(f"{q:>11.3e}" for q in qs))


if __name__ == "__main__":
    main()
