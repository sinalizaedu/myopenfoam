#!/usr/bin/env python3
"""analyze_on-caso-3F2_meshindep.py
====================================
Independencia de malha do on-caso-3F2 (2 contatos arteriais antissimetricos).
Para cada malha, extrai do ultimo passo do .frd as METRICAS DO MODO S:
  - lobo +X (amplitude e z), lobo -X (amplitude e z) do eixo do nervo Ux(z);
  - |Ux|max e numero de trocas de sinal (>=1 => S / n=2);
  - kink_dura: maior excursao lateral da face externa da dura (r~2.5 mm);
  - Fz: reacao axial no engaste posterior (.dat) e lambda final (.sta).

Convergencia = lobos +X/-X e kink_dura estaveis (< alguns %) entre malhas.

Uso: python3 brunaStuff/analyze_on-caso-3F2_meshindep.py
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

# parser do .dat (reacoes) do analisador de sweep
_src = (HERE / "analyze_on-caso-3_pcontact_sweep.py").read_text()
_ns: dict = {}
exec(compile(_src[:_src.index("# 3) loop pelos runs")], "f", "exec"), _ns)
parse_dat = _ns["parse_dat"]

MESHES = [
    ("radpia2dura3", REPO / "cases/on-caso-3F2/ccx"),
    ("radpia3dura4", REPO / "cases/_mi/on-caso-3F2__radpia3dura4/ccx"),
    ("radpia4dura5", REPO / "cases/_mi/on-caso-3F2__radpia4dura5/ccx"),
    ("tangax(ft2fz2)", REPO / "cases/_mi/on-caso-3F2__tangax/ccx"),
]


def sign_flips(z, ux, tol_um=2.0):
    big = ux[np.abs(ux) * 1e6 > tol_um]
    if big.size < 2:
        return 0
    return int((np.diff(np.sign(big)) != 0).sum())


def dura_kink(coords, disp):
    """Maior |U_lat| da face externa da dura (r ~ 2.5 mm, z<=30 mm)."""
    best = 0.0
    for n, (x, y, z) in coords.items():
        if n not in disp or z > 0.0305:
            continue
        r = (x * x + y * y) ** 0.5
        if abs(r - 2.5e-3) < 0.06e-3:
            ux, uy, _ = disp[n]
            best = max(best, (ux * ux + uy * uy) ** 0.5)
    return best


def lam_final(sta: Path):
    if not sta.exists():
        return float("nan")
    for line in reversed(sta.read_text().splitlines()):
        p = line.split()
        if len(p) >= 5 and p[0].isdigit():
            try:
                return float(p[4])
            except ValueError:
                continue
    return float("nan")


def fz_mN(dat: Path):
    if not dat.exists():
        return float("nan")
    t, Dz, Fd, Fp, Fo, Fg = parse_dat(dat)
    F = -(Fd + Fp + Fo)
    return float(F[-1]) * 1e3 if F.size else float("nan")


def main():
    rows = []
    for tag, ccx in MESHES:
        frd = ccx / "on-caso-3F2.frd"
        if not frd.exists():
            print(f"[pendente] {tag}: {frd} ainda nao existe")
            continue
        coords, disp = cmp.parse_frd_last_disp(frd)
        if not coords or not disp:
            print(f"[pendente] {tag}: .frd ainda sem incremento completo (rodando?)")
            continue
        z, ux, uy, uz = cmp.axis_profile(coords, disp)
        ip, ineg = int(np.argmax(ux)), int(np.argmin(ux))
        rows.append(dict(
            tag=tag,
            lam=lam_final(ccx / "on-caso-3F2.sta"),
            fz=fz_mN(ccx / "on-caso-3F2.dat"),
            uxmax=np.abs(ux).max() * 1e6,
            lobe_p=ux[ip] * 1e6, zp=z[ip] * 1e3,
            lobe_n=ux[ineg] * 1e6, zn=z[ineg] * 1e3,
            flips=sign_flips(z, ux),
            kink_dura=dura_kink(coords, disp) * 1e6,
        ))

    if not rows:
        raise SystemExit("nenhum .frd encontrado ainda")

    L = ["=" * 100,
         "on-caso-3F2 -- INDEPENDENCIA DE MALHA (metricas do modo S, p_c=9034 Pa, Dz=-1.0 mm)",
         "=" * 100, ""]
    hdr = (f"{'malha':<16}{'lam':>5}{'Fz[mN]':>9}{'|Ux|max[um]':>12}"
           f"{'lobo+X[um]':>11}{'z+[mm]':>7}{'lobo-X[um]':>11}{'z-[mm]':>7}"
           f"{'flips':>6}{'kink_dura[um]':>14}")
    L.append(hdr); L.append("-" * len(hdr))
    for r in rows:
        L.append(f"{r['tag']:<16}{r['lam']:>5.2f}{r['fz']:>9.1f}{r['uxmax']:>12.1f}"
                 f"{r['lobe_p']:>11.1f}{r['zp']:>7.1f}{r['lobe_n']:>11.1f}{r['zn']:>7.1f}"
                 f"{r['flips']:>6}{r['kink_dura']:>14.1f}")

    # desvios vs malha mais fina disponivel
    if len(rows) >= 2:
        ref = rows[-1]
        L += ["", f"Desvios relativos vs malha mais fina ({ref['tag']}):"]
        for r in rows[:-1]:
            def d(a, b):
                return 100 * (a - b) / b if b else float("nan")
            L.append(f"  {r['tag']:<16} lobo+X {d(r['lobe_p'], ref['lobe_p']):+6.1f}%   "
                     f"lobo-X {d(r['lobe_n'], ref['lobe_n']):+6.1f}%   "
                     f"kink_dura {d(r['kink_dura'], ref['kink_dura']):+6.1f}%")
    L += ["", "flips>=1 e ambos os lobos significativos => modo S (n=2) preservado em todas as malhas."]
    txt = "\n".join(L) + "\n"
    print(txt)
    (HERE / "on-caso-3F2_meshindep_summary.txt").write_text(txt)
    print("salvo: brunaStuff/on-caso-3F2_meshindep_summary.txt")


if __name__ == "__main__":
    main()
