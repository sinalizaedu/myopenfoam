#!/usr/bin/env python3
"""
warp_centerline_sweep.py
========================
Varre (sweep) a malha reta de um .inp CalculiX ao longo de uma LINHA DE CENTRO
curva e SUAVE no plano XY, reorientando cada secao transversal perpendicular a
tangente. Transforma o tubo reto (eixo Z) num "J" tortuoso anatomico.

Linha de centro = arco de CURVATURA CONSTANTE (raio grande -> suave), medida A
PARTIR DO GLOBO (s=0 no globo, na ORIGEM):
    - globo (s=0, na origem 0,0): tangente theta0 (default -Y, nervo desce);
    - heading theta(s) = theta0 + (turn) * s/L  (vira no plano XY);
    - apice (s=L): tangente a theta0+turn de distancia.
      Default theta0=-90deg (-Y), turn=-135deg -> apice aponta +Y-X (cima-esq).

Comprimento de arco = comprimento original do tubo (preservado) -> NAO estica.
Raio da secao transversal (espessura) preservado (transform rigido por secao).
Curva planar (XY) com binormal fixo B=Z -> sem torcao (parallel transport).

Mapeamento de cada no (x0,y0,z0), com s medido do globo:
    s   = zmax - z0                (globo em z=zmax -> s=0)
    th  = theta0 + kappa*s         (kappa = turn/L)
    C(s)= ( (sin th - sin th0)/kappa , (cos th0 - cos th)/kappa , 0 )
    N   = (-sin th, cos th, 0)      (normal no plano)
    B   = (0,0,1)                   (fora do plano)
    novo = C(s) + y0*N + x0*B

Uso:
    python3 warp_centerline_sweep.py --mesh on-caso-2.4_mesh.inp \\
        --theta0-deg -90 --turn-deg -135
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path


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


def sweep(mesh_path: Path, theta0_deg: float, turn_deg: float,
          length: float | None, zmax_ref: float | None = None) -> None:
    lines = mesh_path.read_text().splitlines()
    # zmax_ref permite forcar a MESMA referencia de comprimento de arco em
    # arquivos diferentes (ex.: mesh tem globo ate z=30.8, mas winkler so vai
    # ate z=30). Sem isso, cada arquivo usaria seu proprio max(z) e os nos
    # ghost do Winkler ficariam dessincronizados dos nos da dura.
    zmax = zmax_ref if zmax_ref is not None else max_z(lines)
    L = length if length is not None else zmax
    th0 = math.radians(theta0_deg)
    turn = math.radians(turn_deg)
    kappa = turn / L                          # curvatura constante
    R = 1.0 / kappa

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
                sc = zmax - z0                # arc length medido do globo
                th = th0 + kappa * sc
                cx = (math.sin(th) - math.sin(th0)) * R
                cy = (math.cos(th0) - math.cos(th)) * R
                # N (in-plane), B = Z (out of plane)
                nx, ny = -math.sin(th), math.cos(th)
                X = cx + y0 * nx
                Y = cy + y0 * ny
                Z = x0  # out-of-plane (binormal)
                out.append(f"{nid:>8s}, {X: .8e}, {Y: .8e}, {Z: .8e}")
                n += 1
                continue
        out.append(line)

    mesh_path.write_text("\n".join(out) + "\n")
    print(f"[centerline_sweep] {n} nos varridos; globo na origem (s=0), "
          f"L_arco={L*1e3:.2f} mm (= tubo reto), theta0={theta0_deg:.0f}deg, "
          f"turn={turn_deg:.0f}deg, |R|={abs(R)*1e3:.2f} mm. Plano XY, espessura em Z.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mesh", required=True, type=Path)
    ap.add_argument("--theta0-deg", type=float, default=-90.0,
                    help="Tangente no globo (deg). -90 = -Y (nervo desce do globo).")
    ap.add_argument("--turn-deg", type=float, default=-135.0,
                    help="Giro total da tangente do globo ao apice (deg). "
                         "-135 com theta0=-90 -> apice aponta +Y-X.")
    ap.add_argument("--length", type=float, default=None,
                    help="Comprimento de arco (m); default = max z da malha (= tubo reto).")
    ap.add_argument("--zmax", type=float, default=None,
                    help="Referencia de z do globo (m) p/ medir s = zmax - z. "
                         "Use o MESMO valor para mesh e winkler (senao os nos "
                         "ghost do Winkler ficam dessincronizados da dura).")
    args = ap.parse_args()
    sweep(args.mesh, args.theta0_deg, args.turn_deg, args.length, args.zmax)


if __name__ == "__main__":
    main()
