#!/usr/bin/env python3
"""inspect_teste_2d_setup.py

Renderiza o layout 2D do caso teste-2d-contato-oa-on em PNG, com:
  - quadrado externo (20x20 mm)
  - faixa OA (parede arterial)
  - faixa fat_above e fat_below (gordura)
  - circulos da ON e ONS
  - linha do contato (y=10 mm)
  - setas pequenas mostrando f0 (circunferencial) em algumas celulas da ONS
  - patches de contorno com legenda colorida

Saida:
  brunaStuff/inspect_teste_2d_setup.png

Uso:
  python3 brunaStuff/inspect_teste_2d_setup.py
"""
from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, Rectangle, FancyArrow

REPO = Path(__file__).resolve().parents[0].parent
OUT_PNG = REPO / "brunaStuff" / "inspect_teste_2d_setup.png"

# Parametros do mesh (sincronizado com gen_teste_2d_blockmesh.py)
LX = 20.0       # mm
LY = 20.0       # mm
Y_SPLIT = 10.0
NX = 80
NY_SUB = 40

# Geometria interna (sincronizado com topoSetDict + gen_teste_2d_matdir.py)
ONS_CX = 10.0
ONS_CY = 7.5
R_ON  = 1.5
R_ONS = 2.5

# OA wall
OA_Y0 = 10.0
OA_Y1 = 11.5

# Cores das zonas (consistentes com a paleta dos plots do projeto)
COL_FAT       = "#fff2cc"   # amarelo claro
COL_OA        = "#f6b26b"   # laranja
COL_ONS       = "#9fc5e8"   # azul claro
COL_ON        = "#b6d7a8"   # verde claro
COL_CONTACT   = "#cc0000"   # vermelho
COL_MESHGRID  = "#dddddd"


def draw_main_layout(ax):
    """Desenha o quadrado, as faixas, os circulos e linha de contato."""
    # Fundo: fat (preenche o quadrado inteiro)
    ax.add_patch(Rectangle((0, 0), LX, LY, fc=COL_FAT, ec="black", lw=1.0,
                           label="fat (rho 900, E 500 Pa)"))

    # OA wall (faixa horizontal y in [10, 11.5])
    ax.add_patch(Rectangle((0, OA_Y0), LX, OA_Y1 - OA_Y0,
                           fc=COL_OA, ec="black", lw=0.5,
                           label="oa_wall (E 1 MPa)"))

    # ONS (annulus -- desenhamos o disco externo cinza e por cima o disco
    # da ON; o anel resultante e a ONS)
    ax.add_patch(Circle((ONS_CX, ONS_CY), R_ONS, fc=COL_ONS, ec="black", lw=0.5,
                        label="ons (E 3 MPa)"))

    # ON (disco interno)
    ax.add_patch(Circle((ONS_CX, ONS_CY), R_ON, fc=COL_ON, ec="black", lw=0.5,
                        label="on (E 30 kPa)"))

    # Linha do contato y = 10 mm (interface oa_mestrado <-> on_mestrado)
    ax.axhline(y=Y_SPLIT, color=COL_CONTACT, lw=1.6, ls="--",
               label=f"y={Y_SPLIT} mm: contato oa_mestrado <-> on_mestrado")

    # Linhas finas do grid blockMesh (so algumas, para nao poluir)
    dx = LX / NX
    dy = (LY / 2) / NY_SUB   # cada sub-malha tem NY_SUB celulas em LY/2
    for k in range(0, NX + 1, 8):
        ax.axvline(x=k * dx, color=COL_MESHGRID, lw=0.3, zorder=0)
    for k in range(0, NY_SUB + 1, 8):
        ax.axhline(y=k * dy, color=COL_MESHGRID, lw=0.3, zorder=0)
        ax.axhline(y=Y_SPLIT + k * dy, color=COL_MESHGRID, lw=0.3, zorder=0)

    # Anotacao do ponto de tangencia
    ax.plot(ONS_CX, ONS_CY + R_ONS, "ko", ms=4)
    ax.annotate(f"tangencia\n({ONS_CX:.1f}, {ONS_CY + R_ONS:.1f}) mm",
                xy=(ONS_CX, ONS_CY + R_ONS), xytext=(ONS_CX + 2.5, ONS_CY + R_ONS + 1.5),
                fontsize=8,
                arrowprops=dict(arrowstyle="->", color="black", lw=0.8))


def draw_f0_arrows(ax, n_per_quadrant=12, arrow_len=0.6):
    """Desenha setas curtas mostrando f0 = circunferencial em pts amostrados
    do annulus ONS."""
    n_total = 4 * n_per_quadrant
    for k in range(n_total):
        theta = 2 * math.pi * k / n_total
        r = 0.5 * (R_ON + R_ONS)  # meio do annulus
        x = ONS_CX + r * math.cos(theta)
        y = ONS_CY + r * math.sin(theta)
        # f0 = (-sin theta, cos theta) (circunferencial, sentido CCW)
        fx = -math.sin(theta)
        fy =  math.cos(theta)
        ax.add_patch(FancyArrow(x, y, arrow_len * fx, arrow_len * fy,
                                width=0.04, head_width=0.20, head_length=0.20,
                                fc="darkblue", ec="darkblue", length_includes_head=True))


def annotate_patches(ax):
    """Anota os patches de contorno na figura."""
    ax.annotate("outer_top  (solidTraction P)", xy=(LX / 2, LY),
                xytext=(LX / 2, LY + 0.7), ha="center", fontsize=9,
                arrowprops=dict(arrowstyle="-", color="black"))
    ax.annotate("outer_bottom  (fixedDisp 0)", xy=(LX / 2, 0),
                xytext=(LX / 2, -1.0), ha="center", fontsize=9,
                arrowprops=dict(arrowstyle="-", color="black"))
    ax.annotate("outer_left  (sym)", xy=(0, LY / 2),
                xytext=(-1.6, LY / 2), ha="center", rotation=90, fontsize=9,
                arrowprops=dict(arrowstyle="-", color="black"))
    ax.annotate("outer_right  (sym)", xy=(LX, LY / 2),
                xytext=(LX + 1.6, LY / 2), ha="center", rotation=-90, fontsize=9,
                arrowprops=dict(arrowstyle="-", color="black"))


def main() -> None:
    fig, ax = plt.subplots(figsize=(8.5, 8.5), dpi=140)
    draw_main_layout(ax)
    draw_f0_arrows(ax)
    annotate_patches(ax)

    ax.set_xlim(-2.5, LX + 2.5)
    ax.set_ylim(-2.0, LY + 2.0)
    ax.set_aspect("equal")
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.set_title(
        "teste-2d-contato-oa-on -- layout 20 x 20 mm\n"
        "Contato frictionless OA<->ONS em y = 10 mm; setas azuis = f0 (circunf.)"
    )

    # Legenda customizada (uma entrada por zona/feature)
    legend_handles = [
        mpatches.Patch(facecolor=COL_OA,  edgecolor="black", label="oa_wall (parede arterial, E=1 MPa)"),
        mpatches.Patch(facecolor=COL_ONS, edgecolor="black", label="ons (bainha, E=3 MPa)"),
        mpatches.Patch(facecolor=COL_ON,  edgecolor="black", label="on (tecido neural, E=30 kPa)"),
        mpatches.Patch(facecolor=COL_FAT, edgecolor="black", label="fat_above + fat_below (gordura, E=500 Pa)"),
        plt.Line2D([0], [0], color=COL_CONTACT, lw=1.5, ls="--",
                   label="interface de contato (oa_mestrado <-> on_mestrado)"),
        plt.Line2D([0], [0], color="darkblue", marker=">", lw=0, ms=8,
                   label="f0 = circunferencial (ONS, futuro Guccione)"),
    ]
    ax.legend(handles=legend_handles, loc="lower center", bbox_to_anchor=(0.5, -0.22),
              ncol=2, fontsize=9, frameon=True)

    plt.tight_layout()
    plt.savefig(OUT_PNG, bbox_inches="tight", dpi=140)
    print(f"Escrito: {OUT_PNG}")


if __name__ == "__main__":
    main()
