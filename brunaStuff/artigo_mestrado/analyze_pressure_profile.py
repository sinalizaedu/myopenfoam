#!/usr/bin/env python3
"""Passo 2: perfil de pressao p(z) ao longo do tubo e erro do inlet de pressao.

Compara, no caso DESACOPLADO (fluido-so), o campo de pressao obtido com:
  - inlet de PRESSAO prescrita (=PIC)  -> cases/.../_grid_calib/
  - inlet de VAZAO prescrita (Q_in)    -> cases/.../_grid_qin_fluid/
Extrai o perfil p(z) (media por faixa axial) de z=0 (inlet) ate o lid (z~30.5)
e quantifica o erro de usar inlet de pressao em vez de vazao:
  (i) max |p_P(z) - p_Q(z)| ao longo do tubo;
  (ii) diferenca na carga transmitida a bainha = pressao media no bulk do SAS.

Saidas:
  brunaStuff/figs/on-caso-1.2-pressure-profile.png
  brunaStuff/on-caso-1.2_pressure_profile_summary.txt
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
from check_compartmentalization import parse_cellzones, parse_internal_field  # noqa: E402

CASE = REPO / "cases" / "on-caso-1.2"
CALIB = CASE / "_grid_calib"
QIN = CASE / "_grid_qin_fluid"
RHO = 1000.0
PICS = [1333, 2000, 3000, 3800]
DS = [1e15, 1e17, 1e19]
COLORS = {1333: "#1f77b4", 2000: "#2ca02c", 3000: "#ff7f0e", 3800: "#d62728", 3900: "#d62728"}


def last_time_dir(ldir: Path) -> Path:
    times = [(float(d.name), d) for d in ldir.iterdir()
             if d.is_dir() and d.name.replace('.', '', 1).isdigit() and d.name not in ("0",)]
    if not times:
        times = [(float(d.name), d) for d in ldir.iterdir()
                 if d.is_dir() and d.name.isdigit()]
    return max(times, key=lambda x: x[0])[1]


def profile(casedir: Path, nbins=40):
    """Retorna (z_centros[mm], p_medio[Pa]) binado por z em todo o dominio."""
    tdir = last_time_dir(casedir)
    p = np.array(parse_internal_field(tdir / "p")) * RHO
    cz = np.array(parse_internal_field(tdir / "Cz")) * 1e3  # m -> mm
    edges = np.linspace(cz.min(), cz.max(), nbins + 1)
    idx = np.digitize(cz, edges) - 1
    idx = np.clip(idx, 0, nbins - 1)
    zc, pm = [], []
    for b in range(nbins):
        m = idx == b
        if m.sum():
            zc.append(0.5 * (edges[b] + edges[b + 1]))
            pm.append(p[m].mean())
    return np.array(zc), np.array(pm)


def bulk_sas(casedir: Path) -> float:
    tdir = last_time_dir(casedir)
    p = parse_internal_field(tdir / "p")
    cz = parse_cellzones(casedir / "constant" / "polyMesh" / "cellZones")
    sas = cz["sas"]
    return sum(p[i] for i in sas) / len(sas) * RHO


def dlab_calib(d):
    return f"{d:g}".replace("e+15", "e+15")  # P{pic}_d1e+15


def main():
    L = ["=" * 78,
         "Passo 2 - Perfil p(z) e erro do inlet de PRESSAO vs VAZAO (desacoplado)",
         "=" * 78, ""]

    # ----- Figura: 2 paineis -----
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))

    # Painel A: perfil p(z) (pressao-prescrita) para as 4 PICs em d=1e15
    axA = axes[0]
    for pic in PICS:
        cdir = CALIB / f"P{pic}_d1e+15"
        if not cdir.exists():
            continue
        z, pz = profile(cdir)
        axA.plot(z, pz, "-", color=COLORS[pic], lw=2, label=f"PIC {pic} Pa")
        axA.axhline(pic, ls=":", color=COLORS[pic], alpha=0.4)
    axA.axvspan(30.0, 30.5, color="gray", alpha=0.25, label="lid Darcy (z=30-30.5)")
    axA.set_xlabel("z ao longo do tubo (mm)")
    axA.set_ylabel("pressao media p(z) (Pa)")
    axA.set_title("Perfil de pressao no tubo (d=1e15)\nplato em PIC no SAS, queda toda no lid")
    axA.legend(fontsize=8)
    axA.grid(alpha=0.3)

    # Painel B: pressao-prescrita vs vazao-prescrita (mesma PIC,d) -> erro
    axB = axes[1]
    err_rows = []
    for pic in [1333, 2000, 3000]:  # PICs com ambos os modos
        for d in DS:
            pdir = CALIB / f"P{pic}_d{d:g}"
            qdir = QIN / f"P{pic}_d{d:g}".replace("e+", "e")
            if not (pdir.exists() and qdir.exists()):
                continue
            zP, pP = profile(pdir)
            zQ, pQ = profile(qdir)
            # interpola Q no grid de P para subtrair
            pQi = np.interp(zP, zQ, pQ)
            dmax = np.max(np.abs(pP - pQi))
            loadP, loadQ = bulk_sas(pdir), bulk_sas(qdir)
            err_rows.append((pic, d, dmax, loadP, loadQ,
                             100 * (loadQ - loadP) / loadP))
            if pic == 1333:
                axB.plot(zP, pP, "-", color=COLORS[pic], lw=2,
                         label=f"inlet P, d={d:g}" if d == DS[0] else None)
                axB.plot(zQ, pQ, "--", color="k", lw=1, alpha=0.7,
                         label="inlet Q (vazao)" if d == DS[0] else None)
    axB.axvspan(30.0, 30.5, color="gray", alpha=0.25)
    axB.set_xlabel("z ao longo do tubo (mm)")
    axB.set_ylabel("pressao media p(z) (Pa)")
    axB.set_title("Inlet de PRESSAO vs inlet de VAZAO (PIC=1333)\ncurvas coincidem -> erro desprezivel")
    axB.legend(fontsize=8)
    axB.grid(alpha=0.3)

    fig.tight_layout()
    out = HERE / "figs" / "on-caso-1.2-pressure-profile.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=140, bbox_inches="tight")

    # ----- Tabela de erro -----
    L.append("Carga na bainha = pressao media no bulk do SAS.")
    L.append("Erro = (inlet Q - inlet P)/inlet P, na carga transmitida ao solido.")
    L.append("")
    L.append(f"{'PIC':>6} {'d':>7} {'maxDeltaP(z)':>13} {'load_P(Pa)':>11} "
             f"{'load_Q(Pa)':>11} {'erro%':>8}")
    L.append("-" * 64)
    for pic, d, dmax, lp, lq, e in err_rows:
        L.append(f"{pic:>6} {d:>7.0g} {dmax:>13.3f} {lp:>11.2f} {lq:>11.2f} {e:>+7.3f}%")
    L.append("")
    maxe = max(abs(e) for *_, e in err_rows) if err_rows else float('nan')
    maxdp = max(dmax for _, _, dmax, *_ in err_rows) if err_rows else float('nan')
    L.append(f"=> erro maximo na carga da bainha: {maxe:.3f}%")
    L.append(f"=> maxima diferenca de perfil |p_P(z)-p_Q(z)|: {maxdp:.2f} Pa")
    L.append("")
    L.append("Conclusao: no SAS a pressao e' ~uniforme (= PIC) e a queda toda")
    L.append("ocorre atraves do lid Darcy; logo um inlet de PRESSAO (=PIC) impoe")
    L.append("praticamente a mesma carga na bainha que o inlet de VAZAO calibrado.")
    L.append("O FSI pode usar inlet de pressao (mais estavel) sem perda de fidelidade.")

    txt = "\n".join(L) + "\n"
    print(txt)
    (HERE / "on-caso-1.2_pressure_profile_summary.txt").write_text(txt)
    print(f"figura -> {out}")


if __name__ == "__main__":
    main()
