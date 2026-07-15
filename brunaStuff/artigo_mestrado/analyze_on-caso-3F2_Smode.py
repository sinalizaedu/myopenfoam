#!/usr/bin/env python3
"""analyze_on-caso-3F2_Smode.py
================================
Verifica se o on-caso-3F2 (DOIS contatos arteriais antissimetricos: +X@z=22.5 mm
e -X@z=7.5 mm) produz o padrao em "S" (modo n=2 / duas meias-ondas) no eixo do
nervo, em contraste com o 3F de contato unico (kink monotonico de sentido unico).

Metrica = perfil Ux(z) do eixo do nervo (zona ON, r<=0.35 mm), media por anel
axial -- exatamente a do artigo (compare_on-caso-3_all.py). O modo S e
diagnosticado por:
  - inversao de sinal de Ux ao longo de z (um lobo +X e um lobo -X);
  - dois extremos locais de sinais opostos (duas meias-ondas).

Compara:
  - 3F2 (2 contatos)      : cases/on-caso-3F2/ccx/on-caso-3F2.frd
  - 3F baseline (1 contato): cases/_mi/on-caso-3__radpia2dura3/ccx/on-caso-3_Pc9034.frd

Uso (HOST): python3 brunaStuff/analyze_on-caso-3F2_Smode.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))

from importlib import import_module
cmp = import_module("compare_on-caso-3_all")

CASES = [
    dict(key="3F2", label="contato duplo", color="#d62728",
         frd=REPO / "cases/on-caso-3F2/ccx/on-caso-3F2.frd",
         sta=REPO / "cases/on-caso-3F2/ccx/on-caso-3F2.sta"),
    dict(key="3F1", label="contato único", color="#1f77b4",
         frd=REPO / "cases/_mi/on-caso-3__radpia2dura3/ccx/on-caso-3_Pc9034.frd",
         sta=REPO / "cases/_mi/on-caso-3__radpia2dura3/ccx/on-caso-3_Pc9034.sta"),
]


def sign_flips(ux, tol_um=2.0):
    """Numero de inversoes de sinal de Ux ao longo de z, ignorando ruido < tol."""
    big = ux[np.abs(ux) * 1e6 > tol_um]
    if big.size < 2:
        return 0
    s = np.sign(big)
    return int((np.diff(s) != 0).sum())


def main():
    rows = []
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    for c in CASES:
        if not c["frd"].exists():
            print(f"[FALTA] {c['key']}: {c['frd']}")
            continue
        coords, disp = cmp.parse_frd_last_disp(c["frd"])
        z, ux, uy, uz = cmp.axis_profile(coords, disp)
        i_pos = int(np.argmax(ux))   # lobo +X mais forte
        i_neg = int(np.argmin(ux))   # lobo -X mais forte
        lam = cmp.parse_sta(c["sta"])
        flips = sign_flips(ux)
        rows.append(dict(c=c, z=z, ux=ux, uz=uz,
                         ux_pos_um=ux[i_pos] * 1e6, z_pos=z[i_pos] * 1e3,
                         ux_neg_um=ux[i_neg] * 1e6, z_neg=z[i_neg] * 1e3,
                         flips=flips))
        axes[0].plot(z * 1e3, ux * 1e6, "o-", color=c["color"], label=c["label"])
        axes[1].plot(ux * 1e6, (z + uz) * 1e3, "o-", color=c["color"], label=c["label"])

    axes[0].axhline(0, color="k", lw=0.8)
    for zc, txt in [(22.5, "contato +X"), (7.5, "contato -X")]:
        axes[0].axvline(zc, color="grey", ls="--", lw=0.7)
    axes[0].set_xlabel("z (mm)"); axes[0].set_ylabel("Ux do eixo (µm)")
    axes[0].set_title("Deflexão lateral do eixo Ux(z)")
    axes[0].legend(fontsize=9); axes[0].grid(alpha=0.3)
    axes[1].axvline(0, color="k", lw=0.8)
    axes[1].set_xlabel("Ux deformado (µm)"); axes[1].set_ylabel("z + Uz (mm)")
    axes[1].set_title("Eixo deformado")
    axes[1].legend(fontsize=9); axes[1].grid(alpha=0.3)
    fig.tight_layout()
    out_png = HERE / "figs" / "on-caso-3F2_Smode.png"
    out_png.parent.mkdir(exist_ok=True)
    fig.savefig(out_png, dpi=140)

    L = ["=" * 82,
         "on-caso-3F2 -- diagnostico do modo S (Ux do eixo do nervo, r<=0.35 mm)",
         "=" * 82, ""]
    hdr = (f"{'caso':<40}{'+lobo[um]':>10}{'z+[mm]':>8}"
           f"{'-lobo[um]':>10}{'z-[mm]':>8}{'troca_sinal':>12}")
    L.append(hdr); L.append("-" * len(hdr))
    for r in rows:
        L.append(f"{r['c']['label']:<40}{r['ux_pos_um']:>10.1f}{r['z_pos']:>8.1f}"
                 f"{r['ux_neg_um']:>10.1f}{r['z_neg']:>8.1f}{r['flips']:>12}")
    L += ["",
          "Interpretacao:",
          "  troca_sinal >= 1  E  +lobo e -lobo ambos significativos  ->  MODO S (n=2)",
          "  troca_sinal == 0  (so um lobo)                            ->  kink unico (n=1)"]
    txt = "\n".join(L) + "\n"
    print(txt)
    (HERE / "on-caso-3F2_Smode.txt").write_text(txt)
    print(f"figura: {out_png}")


if __name__ == "__main__":
    main()
