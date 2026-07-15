#!/usr/bin/env python3
"""
gen_dura_ortho_orient.py
========================
Dura-mater ORTOTROPICA na geometria em "J" (on-caso-2.2 / Caso 2J).

Uma unica *ORIENTATION SYSTEM=CYLINDRICAL (eixo Z global) so vale enquanto o
nervo e' reto. Apos o sweep da linha de centro (warp_centerline_sweep.py), o
eixo axial do nervo muda de direcao ao longo do "J". Este script reintroduz a
ortotropia da dura via orientacoes cilindricas POR ANEL AXIAL: para cada estacao
axial dos elementos da dura, emite uma *ORIENTATION cujo eixo e' a TANGENTE LOCAL
da MESMA linha de centro varrida usada no warp:

    s    = zmax - z0                  (comprimento de arco medido do globo)
    th   = theta0 + kappa * s,  kappa = turn / L,  R = 1/kappa
    C(s) = ( (sin th - sin th0) R , (cos th0 - cos th) R , 0 )   (centro da secao)
    t(s) = ( cos th , sin th , 0 )                               (tangente=axial)

Eixo cilindrico do anel = reta por C(s) na direcao t(s) -> ponto a=C(s),
b=C(s)+t(s). Localmente CCX define 1=radial, 2=circunferencial, 3=axial(a->b),
batendo com a dura ortotropica (E_r, E_theta, E_z) dos demais casos.

IMPORTANTE: rode este script sobre a malha RETA (antes do warp). As coordenadas
dos nos sao usadas apenas para (a) ler o z0 original de cada elemento (estacao
axial) -- os eixos C(s)/t(s) sao calculados analiticamente, no referencial curvo.

Uso:
    python3 gen_dura_ortho_orient.py --mesh on-caso-2.2_mesh.inp \\
        --out on-caso-2.2_dura_orient.inp \\
        --theta0-deg -90 --turn-deg -53.130102 --zmax 0.0308
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path


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
    """Retorna {eid: [n1..n8]} apenas do *ELEMENT ELSET=DURA."""
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


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mesh", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--theta0-deg", type=float, required=True)
    ap.add_argument("--turn-deg", type=float, required=True)
    ap.add_argument("--zmax", type=float, required=True,
                    help="z do globo (m); MESMO valor passado ao warp.")
    ap.add_argument("--length", type=float, default=None,
                    help="Comprimento de arco (m); default = zmax (= warp).")
    ap.add_argument("--material", default="DURA_MAT")
    ap.add_argument("--round-decimals", type=int, default=6,
                    help="Arredondamento do z-centroide p/ agrupar aneis axiais.")
    a = ap.parse_args()

    lines = a.mesh.read_text().splitlines()
    nodes = parse_nodes(lines)
    elems = parse_dura_elems(lines)
    if not elems:
        raise SystemExit("[dura_ortho] ERRO: nenhum elemento *ELEMENT ELSET=DURA")

    L = a.length if a.length is not None else a.zmax
    th0 = math.radians(a.theta0_deg)
    turn = math.radians(a.turn_deg)
    kappa = turn / L
    R = 1.0 / kappa

    # z-centroide (malha RETA) -> estacao axial de cada elemento da dura
    zc = {eid: sum(nodes[n][2] for n in nds) / len(nds)
          for eid, nds in elems.items()}
    rings = {}
    for eid, z in zc.items():
        rings.setdefault(round(z, a.round_decimals), []).append(eid)

    out = []
    out.append('** ============================================================')
    out.append('** Dura-mater ORTOTROPICA em "J": orientacoes cilindricas por anel')
    out.append('** axial (gerado por gen_dura_ortho_orient.py). Eixo de cada anel =')
    out.append('** tangente local da linha de centro varrida C(s), t(s).')
    out.append(f'** theta0={a.theta0_deg} deg, turn={a.turn_deg} deg, '
               f'zmax={a.zmax} m, |R|={abs(R)*1e3:.2f} mm.')
    out.append(f'** {len(elems)} elementos da dura em {len(rings)} aneis axiais.')
    out.append('** ============================================================')
    for k, (zk, eids) in enumerate(sorted(rings.items())):
        s = a.zmax - zk
        th = th0 + kappa * s
        cx = (math.sin(th) - math.sin(th0)) * R
        cy = (math.cos(th0) - math.cos(th)) * R
        tx, ty = math.cos(th), math.sin(th)
        ax, ay, az = cx, cy, 0.0
        bx, by, bz = cx + tx, cy + ty, 0.0
        out.append(f"*ELSET, ELSET=DURA_R{k}")
        eids_sorted = sorted(eids)
        for i in range(0, len(eids_sorted), 8):
            out.append(", ".join(str(e) for e in eids_sorted[i:i + 8]))
        out.append(f"*ORIENTATION, NAME=ORI_DURA_R{k}, SYSTEM=CYLINDRICAL")
        out.append(f"{ax: .8e}, {ay: .8e}, {az: .8e}, "
                   f"{bx: .8e}, {by: .8e}, {bz: .8e}")
        out.append(f"*SOLID SECTION, ELSET=DURA_R{k}, MATERIAL={a.material}, "
                   f"ORIENTATION=ORI_DURA_R{k}")
    a.out.write_text("\n".join(out) + "\n")
    print(f"[dura_ortho] {len(elems)} elementos da dura em {len(rings)} aneis "
          f"axiais -> {a.out}")


if __name__ == "__main__":
    main()
