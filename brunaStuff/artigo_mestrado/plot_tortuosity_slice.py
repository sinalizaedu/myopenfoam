#!/usr/bin/env python3
"""
plot_tortuosity_slice.py
========================
Le um .inp CalculiX (nodes + hex por ELSET) e plota um corte longitudinal
Y~=0 (plano XZ) colorido por zona, evidenciando a TORTUOSIDADE inicial do
nervo+pia dentro da dura reta (on-caso-2.2).

Uso:
    python3 plot_tortuosity_slice.py --inp caso_mesh.inp --out fig.png
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HEX_TYPES = {"C3D8", "C3D8I", "C3D8R"}
ZONE_COLORS = {
    "ON": "#1f9e89", "PIA": "#fb8c00", "SAS": "#bbbbbb",
    "DURA": "#1f3fa0", "LC": "#9c27b0", "SCLERA_PERI": "#8d6e63",
    "SCLERA_RING": "#5d4037", "GLOBO": "#37474f",
}


def parse_inp(path: Path):
    nodes, elems = {}, []
    mode, zone, is_hex = None, "UNSET", False
    for raw in path.read_text().splitlines():
        s = raw.strip()
        if not s or s.startswith("**"):
            continue
        if s.startswith("*"):
            kw = s.upper()
            if kw.startswith("*NODE") and "PRINT" not in kw and "FILE" not in kw:
                mode = "node"
            elif kw.startswith("*ELEMENT"):
                mode = "elem"
                et = ""
                for tok in s.split(","):
                    t = tok.strip()
                    if t.upper().startswith("TYPE="):
                        et = t.split("=", 1)[1].strip().upper()
                    if t.upper().startswith("ELSET="):
                        zone = t.split("=", 1)[1].strip()
                is_hex = et in HEX_TYPES
            else:
                mode = None
            continue
        p = [q.strip() for q in s.split(",") if q.strip()]
        if mode == "node" and len(p) >= 4:
            nodes[int(p[0])] = (float(p[1]), float(p[2]), float(p[3]))
        elif mode == "elem" and is_hex and len(p) >= 9:
            elems.append(([int(x) for x in p[1:9]], zone))
    return nodes, elems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inp", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--ytol", type=float, default=0.30e-3,
                    help="tolerancia |y| para o corte (m)")
    ap.add_argument("--title", default=None, help="titulo do grafico")
    args = ap.parse_args()

    nodes, elems = parse_inp(args.inp)

    fig, ax = plt.subplots(figsize=(13, 4.2))
    drawn = set()
    # desenha cada hex cujo centroide esta perto de y=0 como um quad (x,z)
    for conn, zone in elems:
        ys = [nodes[n][1] for n in conn]
        yc = sum(ys) / len(ys)
        if abs(yc) > args.ytol:
            continue
        # face media: usa os 8 nos projetados em (z, x); contorno convexo simples
        pts = [(nodes[n][2] * 1e3, nodes[n][0] * 1e3) for n in conn]
        # ordena por angulo em torno do centroide p/ poligono
        cz = sum(p[0] for p in pts) / 8
        cx = sum(p[1] for p in pts) / 8
        pts.sort(key=lambda p: math.atan2(p[1] - cx, p[0] - cz))
        poly = plt.Polygon(pts, closed=True,
                           facecolor=ZONE_COLORS.get(zone, "#999999"),
                           edgecolor="k", linewidth=0.15, alpha=0.95)
        ax.add_patch(poly)
        drawn.add(zone)

    # legenda
    handles = [plt.Line2D([0], [0], marker="s", linestyle="", markersize=11,
                          markerfacecolor=ZONE_COLORS.get(z, "#999"),
                          markeredgecolor="k", label=z)
               for z in ["ON", "PIA", "SAS", "DURA"] if z in drawn]
    ax.legend(handles=handles, loc="upper right", ncol=4, fontsize=10,
              framealpha=0.9)

    ax.set_xlabel("z (mm)  -  eixo do nervo")
    ax.set_ylabel("x (mm)")
    ax.set_title(args.title or "corte longitudinal Y~=0: tortuosidade do nervo")
    ax.set_aspect("equal")
    ax.autoscale_view()
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(args.out, dpi=140)
    print(f"[plot_tortuosity_slice] salvo {args.out}  (zonas no corte: {sorted(drawn)})")


if __name__ == "__main__":
    main()
