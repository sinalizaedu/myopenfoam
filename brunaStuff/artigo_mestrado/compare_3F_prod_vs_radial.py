#!/usr/bin/env python3
"""
compare_3F_prod_vs_radial.py
============================
Compara a deflexao lateral do nervo no caso 3F (on-caso-3-sf: SO a carga focal
da arteria, p_c=9034 Pa, +X, sem Dz/EOM) entre a malha de PRODUCAO (f100, 1
celula radial na pia) e a malha RADIAL refinada (radpia2dura3 / radpia3dura4).

Usa EXATAMENTE a mesma metrica do artigo (compare_on-caso-3_all.py): perfil do
eixo do nervo (r<=0.35 mm, z<=30.5 mm), media de Ux por anel axial, e |Ux|max
ao longo de z. Assim o numero e' diretamente comparavel aos 326.9 um da Tabela
tab:res-caso3sf.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))

from importlib import import_module
cmp = import_module("compare_on-caso-3_all")

CASES = [
    ("producao f100 (pia1/dura2)",
     REPO / "cases/on-caso-3-sf/ccx/on-caso-3-sf.frd",
     REPO / "cases/on-caso-3-sf/ccx/on-caso-3-sf.sta"),
    ("radial radpia2dura3 (pia2/dura3)",
     REPO / "cases/_mi/on-caso-3-sf__radpia2dura3/ccx/on-caso-3-sf.frd",
     REPO / "cases/_mi/on-caso-3-sf__radpia2dura3/ccx/on-caso-3-sf.sta"),
    ("radial radpia3dura4 (pia3/dura4)",
     REPO / "cases/_mi/on-caso-3-sf__radpia3dura4/ccx/on-caso-3-sf.frd",
     REPO / "cases/_mi/on-caso-3-sf__radpia3dura4/ccx/on-caso-3-sf.sta"),
]


def extract(frd: Path):
    coords, disp = cmp.parse_frd_last_disp(frd)
    z, ux, uy, uz = cmp.axis_profile(coords, disp)
    imax = int(np.argmax(np.abs(ux)))
    return dict(ux_ext_um=ux[imax] * 1e6, z_ext_mm=z[imax] * 1e3,
                uz_span_um=(uz.max() - uz.min()) * 1e6)


def main():
    rows = []
    for label, frd, sta in CASES:
        if not frd.exists():
            print(f"[FALTA] {label}: {frd}")
            continue
        m = extract(frd)
        ninc, ncut = cmp.parse_sta(sta)
        rows.append((label, m, ninc, ncut))

    if not rows:
        raise SystemExit("nenhum frd encontrado")

    ref = abs(rows[0][1]["ux_ext_um"])  # producao
    print("=" * 84)
    print("Caso 3F (on-caso-3-sf, p_c=9034 Pa, so arteria): PRODUCAO vs RADIAL")
    print("metrica = |Ux|max do eixo do nervo (media por anel), igual ao artigo")
    print("=" * 84)
    hdr = f"{'malha':<34}{'|Ux|max[um]':>12}{'z[mm]':>7}{'lado':>6}{'Uz span[um]':>12}{'desvio vs prod':>16}{'inc/cut':>9}"
    print(hdr)
    print("-" * len(hdr))
    for label, m, ninc, ncut in rows:
        ux = m["ux_ext_um"]
        lado = "+X" if ux > 0 else "-X"
        dev = 100 * (abs(ux) - ref) / ref
        print(f"{label:<34}{abs(ux):>12.1f}{m['z_ext_mm']:>7.1f}{lado:>6}"
              f"{m['uz_span_um']:>12.1f}{dev:>+15.2f}%{f'{ninc}/{ncut}':>9}")
    print("")
    print(f"Producao (artigo): {ref:.1f} um")


if __name__ == "__main__":
    main()
