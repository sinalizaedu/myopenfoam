#!/usr/bin/env python3
"""Figura Track A: PIC emergente (Q_in calibrado) ~ invariante e proxima do alvo.

Le cases/on-caso-1.2/_grid_qin_fluid/qin_grid_results.json e mostra, para cada
PIC alvo, a PIC que emerge no bulk do SAS ao prescrever a Q_in calibrada, em
funcao de d. As curvas ficam praticamente horizontais sobre o alvo (desvio
<0,3%), evidenciando que a Q_in calibrada reproduz a PIC desejada
independentemente de d.

Saida: brunaStuff/figs/on-caso-1.2-qin-validation.png
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parent.parent
JSON = REPO / "cases" / "on-caso-1.2" / "_grid_qin_fluid" / "qin_grid_results.json"
OUT = REPO / "brunaStuff" / "figs" / "on-caso-1.2-qin-validation.png"

PICS = [1333, 2000, 3000, 3900]
DS = [1e15, 1e17, 1e19]


def main():
    rows = json.loads(JSON.read_text())
    t = {(round(r["p_target_pa"]), round(np.log10(r["d"]))): r["pic_bulk_pa"] for r in rows}
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    colors = ["#1f77b4", "#2ca02c", "#ff7f0e", "#d62728"]
    for pic, c in zip(PICS, colors):
        y = [t[(pic, round(np.log10(d)))] for d in DS]
        ax.semilogx(DS, y, "o-", color=c, lw=2, ms=9, label=f"alvo {pic} Pa")
        ax.axhline(pic, ls=":", color=c, alpha=0.5)
    ax.set_xlabel(r"Coeficiente de Darcy $d$ (m$^{-2}$)", fontsize=11)
    ax.set_ylabel(r"PIC emergente no bulk do SAS (Pa)", fontsize=11)
    ax.set_title("Vazão calibrada reproduz a PIC alvo (desvio < 0,3%)\n"
                 "curvas ~horizontais: PIC praticamente invariante com $d$", fontsize=11)
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=9, loc="center left")
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=140, bbox_inches="tight")
    print(f"saved -> {OUT}")


if __name__ == "__main__":
    main()
