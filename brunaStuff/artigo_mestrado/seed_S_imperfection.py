#!/usr/bin/env python3
"""Semeia uma imperfeicao geometrica inicial em "S" (modo 2) no 3F.

Representa a TORTUOSIDADE/FOLGA NATURAL do nervo: cada fatia axial z e'
deslocada lateralmente em X por
    dx(z) = A * sin(2*pi*z / L)
ou seja duas meias-ondas (modo 2) com no' no meio. Zero em z=0 (engaste) e
z=L (globo). Lobos em z=L/4 (+X) e z=3L/4 (-X ~ 23 mm, onde a arteria contata).

Para NAO introduzir tensao inicial nas molas de Winkler, o MESMO dx(z) e'
aplicado tanto aos nos da malha quanto aos nos-fantasma GHOST_WINKLER (a mola
liga no_dura<->ghost; deslocando os dois igualmente, o comprimento natural nao
muda -> semente stress-free).

Gera, na pasta da malha radpia2dura3:
    on-caso-3_Sseed_mesh.inp
    on-caso-3_Sseed_winkler.inp
e deixa pronto para o deck on-caso-3_Sseed.inp (que da' *INCLUDE nesses dois).

Uso: python3 brunaStuff/seed_S_imperfection.py [A_mm]
"""
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CCX = REPO / "cases/_mi/on-caso-3__radpia2dura3/ccx"

A = float(sys.argv[1]) * 1e-3 if len(sys.argv) > 1 else 0.2e-3   # amplitude (m)


def node_blocks(lines):
    """Itera (i, nid, x, y, z) para cada linha de *NODE (nid, x, y, z)."""
    in_node = False
    for i, L in enumerate(lines):
        s = L.strip()
        if s.startswith("*"):
            in_node = s.upper().startswith("*NODE")
            continue
        if not in_node or not s:
            continue
        parts = [p for p in s.split(",")]
        if len(parts) < 4:
            continue
        try:
            nid = int(parts[0])
            x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
        except ValueError:
            continue
        yield i, nid, x, y, z


def zmax_of(path):
    zs = [z for _, _, _, _, z in node_blocks(path.read_text().splitlines())]
    return max(zs)


def warp_file(path, out, L):
    lines = path.read_text().splitlines()
    out_lines = list(lines)
    n = 0
    for i, nid, x, y, z in node_blocks(lines):
        dx = A * math.sin(2.0 * math.pi * z / L)
        out_lines[i] = f"{nid:8d}, {x + dx: .8e}, {y: .8e}, {z: .8e}"
        n += 1
    out.write_text("\n".join(out_lines) + "\n")
    return n


def main():
    mesh = CCX / "on-caso-3_mesh.inp"
    wink = CCX / "on-caso-3_winkler.inp"
    L = zmax_of(mesh)
    print(f"A = {A*1e3:.3f} mm   L (zmax) = {L*1e3:.3f} mm")
    print(f"  lobo +X em z={L/4*1e3:.1f} mm   lobo -X em z={3*L/4*1e3:.1f} mm (arteria ~22.5)")
    nm = warp_file(mesh, CCX / "on-caso-3_Sseed_mesh.inp", L)
    nw = warp_file(wink, CCX / "on-caso-3_Sseed_winkler.inp", L)
    print(f"  malha:   {nm} nos deslocados -> on-caso-3_Sseed_mesh.inp")
    print(f"  winkler: {nw} nos-fantasma deslocados -> on-caso-3_Sseed_winkler.inp")


if __name__ == "__main__":
    main()
