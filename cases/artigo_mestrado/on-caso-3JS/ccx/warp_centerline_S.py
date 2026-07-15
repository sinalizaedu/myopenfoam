#!/usr/bin/env python3
"""
warp_centerline_S.py
====================
Variante de warp_centerline_sweep.py que varre a malha reta ao longo de uma
linha de centro em "S" (DUAS meias-ondas, antissimetrica) em vez do arco unico
em "J" (curvatura constante).

Motivacao (Caso 3JS, narrativa B): o "S" clinico da SANS NAO e' flambagem de
Euler espontanea (o sistema fisiologico tem modo natural n=1, vide 2G/2J/3F/3J),
e sim uma FORMA GEOMETRICA IMPOSTA pela folga redundante do nervo + ancoragem
nas duas pontas + contatos multiplos. Aqui representamos essa folga arranjada de
modo SINUOSO: a linha de centro descreve um "S" (curvatura troca de sinal no
meio), e a compressao axial + a arteria amplificam esse "S" fechando o SAS.

Linha de centro (offset lateral SINUSOIDAL -> "S" verdadeiro):
    th(s) = th0 + A * cos(2*pi*s/L)          (A = swing, em graus -> rad)
    -> o OFFSET LATERAL X(s) ~ integral(cos th) ~ (A L/2pi) sin(2*pi*s/L),
       que cruza zero em s=L/2 (positivo na 1a metade, negativo na 2a) => "S".
    -> tangente no globo (s=0) levemente inclinada de A em relacao a -Y (a folga
       sinuosa imposta); preserva o comprimento de arco (sem esticar).
    C(s) = integral de (cos th, sin th) ds   (cumulativo, preserva arco)
    N(s) = (-sin th, cos th)

Mapeamento de cada no (x0,y0,z0), s medido do globo (s = zmax - z0):
    novo = C(s) + y0*N(s)   no plano XY ;   Z = x0 (espessura/binormal)

Uso:
    python3 warp_centerline_S.py --mesh on-caso-3JS_mesh.inp \\
        --theta0-deg -90 --swing-deg 25 --zmax 0.0308
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np


def max_z(lines) -> float:
    zmax = 0.0
    in_node = False
    for line in lines:
        s = line.strip()
        if s.upper().startswith("*NODE"):
            in_node = True
            continue
        if in_node and s.startswith("*"):
            in_node = False
            continue
        if in_node and s and not s.startswith("**"):
            p = [q.strip() for q in line.split(",")]
            if len(p) == 4:
                z = float(p[3])
                if z > zmax:
                    zmax = z
    return zmax


def build_S_centerline(theta0_deg: float, swing_deg: float, L: float, ngrid: int = 4000):
    """Grid (s, cx, cy, nx, ny) da linha de centro em S (offset +N depois -N)."""
    th0 = math.radians(theta0_deg)
    A = math.radians(swing_deg)
    s = np.linspace(0.0, L, ngrid)
    th = th0 + A * np.cos(2.0 * math.pi * s / L)
    tx, ty = np.cos(th), np.sin(th)
    cx = np.concatenate([[0.0], np.cumsum(0.5 * (tx[1:] + tx[:-1]) * np.diff(s))])
    cy = np.concatenate([[0.0], np.cumsum(0.5 * (ty[1:] + ty[:-1]) * np.diff(s))])
    nx, ny = -ty, tx
    return s, cx, cy, nx, ny


def sweep(mesh_path: Path, theta0_deg: float, swing_deg: float,
          length: float | None, zmax_ref: float | None = None) -> None:
    lines = mesh_path.read_text().splitlines()
    zmax = zmax_ref if zmax_ref is not None else max_z(lines)
    L = length if length is not None else zmax
    s_g, cx_g, cy_g, nx_g, ny_g = build_S_centerline(theta0_deg, swing_deg, L)

    out: list[str] = []
    in_node = False
    n = 0
    for line in lines:
        s = line.strip()
        if s.upper().startswith("*NODE"):
            in_node = True
            out.append(line)
            continue
        if in_node and s.startswith("*"):
            in_node = False
            out.append(line)
            continue
        if in_node and s and not s.startswith("**"):
            p = [q.strip() for q in line.split(",")]
            if len(p) == 4:
                nid = p[0]
                x0, y0, z0 = float(p[1]), float(p[2]), float(p[3])
                sc = zmax - z0                     # arc length do globo
                cx = float(np.interp(sc, s_g, cx_g))
                cy = float(np.interp(sc, s_g, cy_g))
                nx = float(np.interp(sc, s_g, nx_g))
                ny = float(np.interp(sc, s_g, ny_g))
                X = cx + y0 * nx
                Y = cy + y0 * ny
                Z = x0
                out.append(f"{nid:>8s}, {X: .8e}, {Y: .8e}, {Z: .8e}")
                n += 1
                continue
        out.append(line)

    mesh_path.write_text("\n".join(out) + "\n")
    print(f"[centerline_S] {n} nos varridos em 'S'; globo na origem (s=0), "
          f"L_arco={L*1e3:.2f} mm, theta0={theta0_deg:.0f}deg, swing=+/-{swing_deg:.0f}deg "
          f"(offset lateral troca de sinal em s=L/2). Plano XY, espessura em Z.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mesh", required=True, type=Path)
    ap.add_argument("--theta0-deg", type=float, default=-90.0)
    ap.add_argument("--swing-deg", type=float, default=25.0,
                    help="Amplitude de oscilacao do heading (graus). Maior = S mais pronunciado.")
    ap.add_argument("--length", type=float, default=None)
    ap.add_argument("--zmax", type=float, default=None,
                    help="z do globo (m); use o MESMO valor para mesh e winkler.")
    a = ap.parse_args()
    sweep(a.mesh, a.theta0_deg, a.swing_deg, a.length, a.zmax)


if __name__ == "__main__":
    main()
