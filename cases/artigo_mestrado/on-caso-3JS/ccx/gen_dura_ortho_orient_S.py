#!/usr/bin/env python3
"""
gen_dura_ortho_orient_S.py
==========================
Dura ORTOTROPICA na geometria em "S" (Caso 3JS). Identico a gen_dura_ortho_orient.py
do Caso 2J, porem a linha de centro e' o "S" (dupla meia-onda) do warp_centerline_S.py,
e nao o arco em "J" de curvatura constante.

Para cada anel axial dos elementos da dura (agrupado pelo z0 centroide da malha
RETA), emite uma *ORIENTATION cilindrica cujo eixo e' a TANGENTE LOCAL t(s) da
linha de centro em S:
    th(s) = th0 + A*sin(2*pi*s/L) ;  s = zmax - z0
    C(s)  = integral de (cos th, sin th) ds  (cumulativo)
    t(s)  = (cos th, sin th)
Localmente CCX define 1=radial, 2=circ, 3=axial(a->b), com a=C(s), b=C(s)+t(s).

Uso:
    python3 gen_dura_ortho_orient_S.py --mesh on-caso-3JS_mesh.inp \\
        --out on-caso-3JS_dura_orient.inp --theta0-deg -90 --swing-deg 25 --zmax 0.0308
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np


def parse_nodes(lines):
    nodes = {}
    in_node = False
    for L in lines:
        s = L.strip()
        if s.upper().startswith("*NODE"):
            in_node = True
            continue
        if in_node and s.startswith("*"):
            in_node = False
        if in_node and s and not s.startswith("**"):
            p = [q.strip() for q in s.split(",")]
            if len(p) == 4:
                nodes[int(p[0])] = (float(p[1]), float(p[2]), float(p[3]))
    return nodes


def parse_dura_elems(lines):
    elems = {}
    in_dura = False
    for L in lines:
        s = L.strip()
        if s.upper().startswith("*ELEMENT"):
            in_dura = "ELSET=DURA" in s.upper().replace(" ", "")
            continue
        if in_dura and s.startswith("*"):
            in_dura = False
        if in_dura and s and not s.startswith("**"):
            p = [q.strip() for q in s.split(",")]
            if len(p) >= 9:
                elems[int(p[0])] = [int(x) for x in p[1:9]]
    return elems


def build_S(theta0_deg, swing_deg, L, ngrid=4000):
    th0 = math.radians(theta0_deg)
    A = math.radians(swing_deg)
    s = np.linspace(0.0, L, ngrid)
    th = th0 + A * np.cos(2.0 * math.pi * s / L)
    tx, ty = np.cos(th), np.sin(th)
    cx = np.concatenate([[0.0], np.cumsum(0.5 * (tx[1:] + tx[:-1]) * np.diff(s))])
    cy = np.concatenate([[0.0], np.cumsum(0.5 * (ty[1:] + ty[:-1]) * np.diff(s))])
    return s, cx, cy, tx, ty


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mesh", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--theta0-deg", type=float, required=True)
    ap.add_argument("--swing-deg", type=float, required=True)
    ap.add_argument("--zmax", type=float, required=True)
    ap.add_argument("--length", type=float, default=None)
    ap.add_argument("--material", default="DURA_MAT")
    ap.add_argument("--round-decimals", type=int, default=6)
    a = ap.parse_args()

    lines = a.mesh.read_text().splitlines()
    nodes = parse_nodes(lines)
    elems = parse_dura_elems(lines)
    if not elems:
        raise SystemExit("[dura_ortho_S] ERRO: nenhum *ELEMENT ELSET=DURA")

    L = a.length if a.length is not None else a.zmax
    s_g, cx_g, cy_g, tx_g, ty_g = build_S(a.theta0_deg, a.swing_deg, L)

    zc = {eid: sum(nodes[n][2] for n in nds) / len(nds) for eid, nds in elems.items()}
    rings = {}
    for eid, z in zc.items():
        rings.setdefault(round(z, a.round_decimals), []).append(eid)

    out = []
    out.append('** ============================================================')
    out.append('** Dura ORTOTROPICA em "S" (Caso 3JS): orientacoes cilindricas por')
    out.append('** anel axial; eixo = tangente local da linha de centro em S t(s).')
    out.append(f'** theta0={a.theta0_deg} deg, swing=+/-{a.swing_deg} deg, zmax={a.zmax} m.')
    out.append(f'** {len(elems)} elementos da dura em {len(rings)} aneis axiais.')
    out.append('** ============================================================')
    for k, (zk, eids) in enumerate(sorted(rings.items())):
        s = a.zmax - zk
        cx = float(np.interp(s, s_g, cx_g)); cy = float(np.interp(s, s_g, cy_g))
        tx = float(np.interp(s, s_g, tx_g)); ty = float(np.interp(s, s_g, ty_g))
        ax, ay, az = cx, cy, 0.0
        bx, by, bz = cx + tx, cy + ty, 0.0
        out.append(f"*ELSET, ELSET=DURA_R{k}")
        eids_sorted = sorted(eids)
        for i in range(0, len(eids_sorted), 8):
            out.append(", ".join(str(e) for e in eids_sorted[i:i + 8]))
        out.append(f"*ORIENTATION, NAME=ORI_DURA_R{k}, SYSTEM=CYLINDRICAL")
        out.append(f"{ax: .8e}, {ay: .8e}, {az: .8e}, {bx: .8e}, {by: .8e}, {bz: .8e}")
        out.append(f"*SOLID SECTION, ELSET=DURA_R{k}, MATERIAL={a.material}, "
                   f"ORIENTATION=ORI_DURA_R{k}")
    a.out.write_text("\n".join(out) + "\n")
    print(f"[dura_ortho_S] {len(elems)} elementos da dura em {len(rings)} aneis -> {a.out}")


if __name__ == "__main__":
    main()
