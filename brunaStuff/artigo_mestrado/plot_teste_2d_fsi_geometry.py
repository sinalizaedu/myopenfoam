#!/usr/bin/env python3
"""plot_teste_2d_fsi_geometry.py

Renderiza a geometria 2D do caso `cases/teste-2d-fsi-oa-on/`:

    - 4 blocos do solido (A=lower, B=wall_inf, C=wall_sup, D=fat_above)
    - 1 bloco do fluido (lumen)
    - Inclusao circular do nervo optico (ON) e bainha (ONS) dentro do Block A,
      via topoSet (cylinder em (10, 7.5) mm, raios 1.5 e 2.5 mm)
    - Interfaces destacadas:
        * oa_mestrado / on_mestrado em y=10 mm  (contato OA x ONS, frictionless)
        * lumen_bot / lumen_top em y=10.2 e y=11.3 mm  (FSI via preCICE)
    - Coordenadas em mm, scale-aware (mesma escala em x e y).

Saidas em brunaStuff/:
    teste_2d_fsi_geometry.png    -- figura unica do dominio + zoom da OA

Uso:
    python3 brunaStuff/plot_teste_2d_fsi_geometry.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle


# Dimensoes do dominio (mm) -- ESPELHAM o gerador blockMeshDict.
LX = 20.0
INITIAL_GAP = 0.05            # 50 um (= gen_teste_2d_fsi_blockmesh.py)
Y_A_TOP = 10.0 - INITIAL_GAP  # 9.95 mm (topo Block A, on_mestrado)
Y_B_BOT = 10.0                # 10.00 mm (base Block B, oa_mestrado)
Y_CONTACT = Y_B_BOT           # plano nominal do contato (legacy)
Y_WALL_BOT = 10.2
Y_WALL_TOP = 11.3
Y_OA_TOP = 11.5
Y_TOP = 20.0

# Inclusao ON/ONS (centro e raios em mm)
ON_X, ON_Y = 10.0, 7.5
R_ON = 1.5
R_ONS = 2.5

# Cores por material (E_modulus-aware: mole -> claro, rigido -> escuro)
COLORS = {
    "fat":     "#fde6d4",
    "ons":     "#a26d3d",
    "on":      "#f6c89f",
    "oa_wall": "#c0392b",
    "lumen":   "#bcd9e8",
}

OUT = Path(__file__).resolve().parent / "teste_2d_fsi_geometry.png"


def draw_block(ax, x0, y0, w, h, color, label=None, label_xy=None, edgecolor="black", lw=0.8):
    rect = Rectangle((x0, y0), w, h, facecolor=color, edgecolor=edgecolor, linewidth=lw, zorder=1)
    ax.add_patch(rect)
    if label and label_xy is not None:
        ax.text(*label_xy, label, ha="center", va="center", fontsize=9, zorder=5)


def draw_domain(ax, *, zoom: bool = False, show_mesh_hint: bool = False) -> None:
    """Desenha um plot completo da geometria.

    Se zoom=True, recorta em y=[9.5, 12.0] para mostrar parede OA + lumen.
    """
    if zoom:
        ax.set_xlim(-0.5, LX + 0.5)
        ax.set_ylim(9.0, 12.4)
    else:
        ax.set_xlim(-1.0, LX + 1.0)
        ax.set_ylim(-1.0, Y_TOP + 1.0)

    # Block A (lower) -- vai virar fat_below ao redor da ON/ONS.
    # Agora termina em Y_A_TOP = 9.95 mm; o gap inicial vai ate Y_B_BOT = 10.0.
    draw_block(ax, 0, 0, LX, Y_A_TOP, COLORS["fat"], None)

    # ON disco + ONS anel (so quando o A esta visivel)
    if not zoom:
        ons_circle = Circle((ON_X, ON_Y), R_ONS, facecolor=COLORS["ons"], edgecolor="black", linewidth=0.8, zorder=2)
        on_circle = Circle((ON_X, ON_Y), R_ON, facecolor=COLORS["on"], edgecolor="black", linewidth=0.8, zorder=3)
        ax.add_patch(ons_circle)
        ax.add_patch(on_circle)

    # Block B (wall_inf) e Block C (wall_sup) -- partes da artéria oftálmica
    draw_block(ax, 0, Y_B_BOT, LX, Y_WALL_BOT - Y_B_BOT, COLORS["oa_wall"])
    draw_block(ax, 0, Y_WALL_TOP, LX, Y_OA_TOP - Y_WALL_TOP, COLORS["oa_wall"])

    # Lumen (fluido) -- bloco distinto
    draw_block(ax, 0, Y_WALL_BOT, LX, Y_WALL_TOP - Y_WALL_BOT, COLORS["lumen"])

    # Block D (fat_above)
    if not zoom:
        draw_block(ax, 0, Y_OA_TOP, LX, Y_TOP - Y_OA_TOP, COLORS["fat"])

    # ---- Anotacoes de texto dentro do dominio --------------------------------
    if not zoom:
        ax.text(LX / 2, 5.0,            "Block A — fat_below (E=100 kPa)", ha="center", va="center", fontsize=10)
        ax.text(LX / 2, 15.75,           "Block D — fat_above (E=100 kPa)", ha="center", va="center", fontsize=10)
        ax.text(ON_X, ON_Y,             "ON\n(E=30 kPa)", ha="center", va="center", fontsize=8.5, weight="bold")
        ax.text(ON_X + 1.95, ON_Y,      "ONS\n(E=3 MPa)", ha="center", va="center", fontsize=7.5, color="white", weight="bold")

    # Anotacoes da OA + lumen (variam entre completo e zoom)
    if zoom:
        wall_label_B = "Block B — oa_wall (E=0.3 MPa, 0.2 mm, 80×2 cells)"
        wall_label_C = "Block C — oa_wall (E=0.3 MPa, 0.2 mm, 80×2 cells)"
        lumen_label = "LUMEN — fluido (sangue, ν=3.5e-6 m²/s)  •  pimpleFoam, 80×11 cells"
    else:
        wall_label_B = "Block B — oa_wall (E=0.3 MPa)"
        wall_label_C = "Block C — oa_wall (E=0.3 MPa)"
        lumen_label = "LUMEN — fluido"
    ax.text(LX / 2, (Y_B_BOT + Y_WALL_BOT) / 2, wall_label_B,
            ha="center", va="center", fontsize=8.5, color="white", weight="bold")
    ax.text(LX / 2, (Y_WALL_TOP + Y_OA_TOP) / 2, wall_label_C,
            ha="center", va="center", fontsize=8.5, color="white", weight="bold")
    ax.text(LX / 2, (Y_WALL_BOT + Y_WALL_TOP) / 2, lumen_label,
            ha="center", va="center", fontsize=9, style="italic")

    # ---- Interfaces (linhas + setas) -----------------------------------------
    # Gap inicial: faixa hachurada entre Y_A_TOP=9.95 e Y_B_BOT=10.0 (50 um)
    gap_rect = Rectangle((0, Y_A_TOP), LX, Y_B_BOT - Y_A_TOP,
                         facecolor="white", edgecolor="#27ae60",
                         linewidth=0.6, hatch="////", alpha=0.7, zorder=2)
    ax.add_patch(gap_rect)
    # Contato MASTER (topo Block A, y=9.95) e SHADOW (base Block B, y=10.0)
    ax.plot([0, LX], [Y_A_TOP, Y_A_TOP], color="#27ae60", linewidth=2.0, zorder=4)
    ax.plot([0, LX], [Y_B_BOT, Y_B_BOT], color="#27ae60", linewidth=2.0, zorder=4)
    # FSI inferior em y=10.2
    ax.plot([0, LX], [Y_WALL_BOT, Y_WALL_BOT], color="#8e44ad", linewidth=1.8, zorder=4)
    # FSI superior em y=11.3
    ax.plot([0, LX], [Y_WALL_TOP, Y_WALL_TOP], color="#8e44ad", linewidth=1.8, zorder=4)

    if zoom:
        ax.annotate("on_mestrado (MASTER, y=9.95 mm)\n"
                    "oa_mestrado (SHADOW, y=10.00 mm)\n"
                    "GAP INICIAL = 50 μm (// hatching)",
                    xy=(3.0, (Y_A_TOP + Y_B_BOT) / 2), xytext=(3.0, 9.20),
                    fontsize=8.5, color="#27ae60", ha="center",
                    arrowprops=dict(arrowstyle="->", color="#27ae60", lw=1.2))
        ax.annotate("lumen_bot ↔ wall_bot  (FSI preCICE)",
                    xy=(16, Y_WALL_BOT), xytext=(16, 9.25),
                    fontsize=8.5, color="#8e44ad", ha="center",
                    arrowprops=dict(arrowstyle="->", color="#8e44ad", lw=1.2))
        ax.annotate("lumen_top ↔ wall_top  (FSI preCICE)",
                    xy=(16, Y_WALL_TOP), xytext=(16, 12.15),
                    fontsize=8.5, color="#8e44ad", ha="center",
                    arrowprops=dict(arrowstyle="->", color="#8e44ad", lw=1.2))
        # Setas inlet/outlet (com texto acima do lumen para nao colidir)
        ax.annotate("", xy=(1.2, 10.75), xytext=(-0.3, 10.75),
                    arrowprops=dict(arrowstyle="->", color="#1f77b4", lw=2.0))
        ax.text(2.5, 12.15, "inlet  P(t) — OMVS 80–120 mmHg",
                fontsize=8.5, color="#1f77b4", ha="center")
        ax.annotate("", xy=(LX + 0.3, 10.75), xytext=(LX - 1.2, 10.75),
                    arrowprops=dict(arrowstyle="->", color="#1f77b4", lw=2.0))

    # ---- BCs externos (so na vista geral) ------------------------------------
    if not zoom:
        # outer_top / outer_bottom -- linhas grossas (fixedDisplacement)
        ax.plot([0, LX], [0, 0], color="black", linewidth=3.0, zorder=6)
        ax.plot([0, LX], [Y_TOP, Y_TOP], color="black", linewidth=3.0, zorder=6)
        ax.text(LX / 2, -0.45, "outer_bottom — fixedDisplacement (0 0 0)",
                ha="center", va="top", fontsize=8.5)
        ax.text(LX / 2, Y_TOP + 0.45, "outer_top — fixedDisplacement (0 0 0)",
                ha="center", va="bottom", fontsize=8.5)
        # Laterais (symmetry) -- linhas tracejadas
        for xL in (0, LX):
            ax.plot([xL, xL], [0, Y_TOP], color="gray", linestyle="--", linewidth=1.0, zorder=6)
        ax.text(-0.6, Y_TOP / 2, "symmetry", rotation=90, ha="right", va="center",
                fontsize=8, color="gray")
        ax.text(LX + 0.6, Y_TOP / 2, "symmetry", rotation=-90, ha="left", va="center",
                fontsize=8, color="gray")

    # Y-ticks marcando interfaces
    if zoom:
        ticks = [Y_A_TOP, Y_B_BOT, Y_WALL_BOT, Y_WALL_TOP, Y_OA_TOP]
        ax.set_yticks(ticks)
        ax.set_yticklabels([f"{v:.2f}" for v in ticks])
    else:
        ax.set_yticks([0, Y_B_BOT, Y_WALL_BOT, Y_WALL_TOP, Y_OA_TOP, Y_TOP])

    ax.set_xlabel("x [mm]")
    ax.set_ylabel("y [mm]")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.25)


def build_legend(ax) -> None:
    handles = [
        mpatches.Patch(facecolor=COLORS["fat"], edgecolor="black", label="fat (E=100 kPa)"),
        mpatches.Patch(facecolor=COLORS["on"], edgecolor="black", label="ON — disco r≤1.5 mm (E=30 kPa)"),
        mpatches.Patch(facecolor=COLORS["ons"], edgecolor="black", label="ONS — anel 1.5–2.5 mm (E=3 MPa)"),
        mpatches.Patch(facecolor=COLORS["oa_wall"], edgecolor="black", label="oa_wall (E=0.3 MPa)"),
        mpatches.Patch(facecolor=COLORS["lumen"], edgecolor="black", label="lumen — fluido (ρ=1050)"),
        mpatches.Patch(facecolor="white", edgecolor="#27ae60", hatch="////",
                       label="GAP INICIAL 50 μm (vacuo)"),
        Line2D([0], [0], color="#27ae60", lw=2.0,
               label="patches on_/oa_mestrado (solidContact)"),
        Line2D([0], [0], color="#8e44ad", lw=1.8, label="interface FSI (preCICE)"),
        Line2D([0], [0], color="black", lw=3.0, label="fixedDisplacement (top/bot)"),
        Line2D([0], [0], color="gray", lw=1.0, linestyle="--", label="symmetry (lados)"),
    ]
    ax.legend(handles=handles, loc="center", ncol=1, fontsize=9, frameon=False)
    ax.axis("off")


def main() -> None:
    # Layout: linha 0 -> [completo (8x8 equiv) | legenda] | linha 1 -> zoom full-width
    fig = plt.figure(figsize=(13, 13))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.6, 1.0], height_ratios=[2.8, 1.0],
                          hspace=0.18, wspace=0.05)

    ax_full = fig.add_subplot(gs[0, 0])
    ax_leg = fig.add_subplot(gs[0, 1])
    ax_zoom = fig.add_subplot(gs[1, :])

    draw_domain(ax_full, zoom=False)
    ax_full.set_title("teste-2d-fsi-oa-on  —  geometria completa (20 × 20 mm, plane-strain z=1 mm)",
                      fontsize=11, pad=8)

    draw_domain(ax_zoom, zoom=True)
    ax_zoom.set_title("zoom: parede OA + lúmen + gap inicial 50 μm  (y ∈ [9.0, 12.4] mm)",
                      fontsize=10, pad=8)

    build_legend(ax_leg)
    ax_leg.set_title("Legenda", fontsize=10, loc="left", pad=8)

    fig.suptitle(
        "Mesh: sólido 6240 cells (4 blocos: A=80×40, B=80×2, C=80×2, D=80×34)  |  "
        "fluido 880 cells (80×11)  |  scale 0.001 (mm → m)",
        fontsize=10, y=0.99,
    )

    fig.savefig(OUT, dpi=160, bbox_inches="tight")
    print(f"Escrito: {OUT}")


if __name__ == "__main__":
    main()
