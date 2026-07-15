#!/usr/bin/env python3
"""analyze_caso_1_2_nh_vs_linear.py
====================================
Compara o lado solido do FSI do on-caso-1.2 (Caso 3) sob dois modelos
constitutivos -- elastico LINEAR (*ELASTIC, nu=0.45) vs NEO-HOOKEANO
(*HYPERELASTIC, NEO HOOKE, nu=0.49) -- ao longo da rampa de PIC, com a mesma
malha, a mesma tampa de Darcy (d=1e15) e o mesmo acoplamento preCICE.

Grandezas (distensao radial maxima no corpo do nervo, em micrometros):
  - dura_ur_max_um : expansao radial da bainha (achado clinico da SANS, +para fora)
  - pia_ur_max_um  : compressao radial da pia (-para dentro)

Fonte: cases/on-caso-1.2/_grid/grid_fsi_results.json (gerado por run_grid_fsi.py).

Figura (figs/on-caso-1.2-nh-vs-linear.png):
  (A) Ur(dura) e Ur(pia) vs PIC, linear vs Neo-Hooke
  (B) diferenca por ponto (linear - Neo-Hooke) vs PIC, em micrometros e em %

Uso: python3 brunaStuff/analyze_caso_1_2_nh_vs_linear.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
JSON = REPO / "cases" / "on-caso-1.2" / "_grid" / "grid_fsi_results.json"
D_FIX = 1e15  # tampa de Darcy fixa para isolar o efeito do material
PICS = [1333.0, 2000.0, 3000.0, 3800.0]  # grade de producao (exclui legado 3900)

C_LIN = "#1f77b4"
C_NH = "#d62728"


def load():
    rows = json.loads(JSON.read_text())
    data = {}  # (mat) -> list of (P, dura, pia)
    for r in rows:
        if r.get("status") != "OK" or abs(r["d"] - D_FIX) / D_FIX > 1e-6:
            continue
        if not any(abs(r["p_target_pa"] - p) < 1.0 for p in PICS):
            continue
        data.setdefault(r["mat"], []).append(
            (r["p_target_pa"], r["dura_ur_max_um"], r["pia_ur_max_um"]))
    for m in data:
        data[m] = np.array(sorted(data[m]))
    return data


def main():
    data = load()
    lin, nh = data["linear"], data["neohooke"]
    # alinha por pressao comum
    P = np.array(sorted(set(lin[:, 0]) & set(nh[:, 0])))
    li = {p: lin[lin[:, 0] == p][0] for p in P}
    ni = {p: nh[nh[:, 0] == p][0] for p in P}
    dura_l = np.array([li[p][1] for p in P]); dura_n = np.array([ni[p][1] for p in P])
    pia_l = np.array([li[p][2] for p in P]); pia_n = np.array([ni[p][2] for p in P])

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

    ax = axes[0]
    ax.plot(P, dura_n, "o-", color=C_LIN, label="dura, Neo-Hooke (base)")
    ax.plot(P, dura_l, "s--", color=C_LIN, mfc="white", label="dura, linear")
    ax.plot(P, pia_n, "o-", color=C_NH, label="pia, Neo-Hooke (base)")
    ax.plot(P, pia_l, "s--", color=C_NH, mfc="white", label="pia, linear")
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xlabel("PIC prescrita (Pa)")
    ax.set_ylabel("Distensão radial máxima Ur (µm)")
    ax.set_title("Distensão radial vs PIC (d = 1e15)")
    ax.legend(fontsize=9); ax.grid(alpha=0.3)

    ax = axes[1]
    ddura = dura_l - dura_n
    dpia = pia_l - pia_n
    w = 90.0
    ax.bar(P - w / 2, ddura, width=w, color=C_LIN, label="dura (linear − Neo-Hooke)")
    ax.bar(P + w / 2, dpia, width=w, color=C_NH, label="pia (linear − Neo-Hooke)")
    ax.axhline(0, color="k", lw=0.8)
    for p, dv in zip(P, ddura):
        ax.annotate(f"{dv:+.2f}", (p - w / 2, dv), ha="center",
                    va="bottom" if dv >= 0 else "top", fontsize=7)
    for p, dv in zip(P, dpia):
        ax.annotate(f"{dv:+.2f}", (p + w / 2, dv), ha="center",
                    va="bottom" if dv >= 0 else "top", fontsize=7)
    ax.set_xlabel("PIC prescrita (Pa)")
    ax.set_ylabel("Diferença Ur por ponto (µm)")
    ax.set_title("Diferença linear − Neo-Hooke por ponto")
    ax.legend(fontsize=9); ax.grid(alpha=0.3, axis="y")

    fig.tight_layout()
    out = HERE / "figs" / "on-caso-1.2-nh-vs-linear.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=140)

    # ---- tabela texto ----
    L = ["=" * 78,
         "on-caso-1.2 (Caso 3 FSI) -- modelo LINEAR vs NEO-HOOKE (d=1e15)",
         "=" * 78, "",
         f"{'PIC[Pa]':>8}{'dura_lin':>10}{'dura_NH':>10}{'Δdura':>8}{'Δ%':>7}"
         f"{'pia_lin':>10}{'pia_NH':>10}{'Δpia':>8}{'Δ%':>7}",
         "-" * 78]
    for i, p in enumerate(P):
        ddp = 100 * ddura[i] / dura_n[i]
        dpp = 100 * dpia[i] / pia_n[i]
        L.append(f"{p:>8.0f}{dura_l[i]:>10.2f}{dura_n[i]:>10.2f}{ddura[i]:>8.2f}"
                 f"{ddp:>7.1f}{pia_l[i]:>10.2f}{pia_n[i]:>10.2f}{dpia[i]:>8.2f}"
                 f"{dpp:>7.1f}")
    L += ["",
          "Notas:",
          "  - dura (QoI clinica): linear e Neo-Hooke praticamente coincidem",
          f"    (max |Δ| = {np.max(np.abs(ddura)):.2f} µm, "
          f"{np.max(np.abs(100*ddura/dura_n)):.1f}%).",
          "  - pia: modelos divergem (Neo-Hooke nu=0.49 quase-incompressivel",
          "    comprime menos a pia que o linear nu=0.45).",
          f"    max |Δ| = {np.max(np.abs(dpia)):.2f} µm "
          f"({np.max(np.abs(100*dpia/pia_n)):.0f}%)."]
    txt = "\n".join(L) + "\n"
    print(txt)
    (HERE / "on-caso-1.2_nh_vs_linear_summary.txt").write_text(txt)
    print(f"figura: {out}")


if __name__ == "__main__":
    main()
