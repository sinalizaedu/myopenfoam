#!/usr/bin/env python3
"""compare_on-caso-3_all.py
============================
Compara os tres casos da familia caso-3 (todos CalculiX NLGEOM NeoHooke,
mesma malha 8 zonas, Winkler 200 kPa/m, P_contact=9034 Pa):

  - on-caso-3      (puro): caso-2 + P_contact(+X). TEM Dz=-1.5mm axial + EOM
                           + perturbacao artificial. Compressao + arteria.
  - on-caso-3-sf   (sf)  : SO P_contact(+X). Sem Dz, sem EOM, sem pert.
                           Isola o efeito da arteria no lado +X.
  - on-caso-3-inv  (inv) : SO P_contact(-X). Igual ao sf, contato espelhado.
                           Isola o efeito da arteria no lado -X (oposto).

Le o eixo do nervo (zona ON, r<R_AXIS) do ultimo passo de cada .frd e a
qualidade de convergencia do .sta. Gera figura + sumario.

Uso (HOST): python3 brunaStuff/compare_on-caso-3_all.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parent.parent
OUT_PNG = REPO / "brunaStuff" / "on-caso-3_all_comparison.png"
OUT_TXT = REPO / "brunaStuff" / "on-caso-3_all_comparison.txt"
R_AXIS = 0.35e-3

CASES = [
    dict(key="puro", label="caso-3 puro (+X, Dz+pert+arteria)", color="#1f77b4",
         frd=REPO / "cases/on-caso-3/ccx/on-caso-3.frd",
         sta=REPO / "cases/on-caso-3/ccx/on-caso-3.sta"),
    dict(key="sf", label="caso-3 sf (+X, so arteria)", color="#2ca02c",
         frd=REPO / "cases/on-caso-3-sf/ccx/on-caso-3-sf_Pc9034.frd",
         sta=REPO / "cases/on-caso-3-sf/ccx/on-caso-3-sf_Pc9034.sta"),
    dict(key="inv", label="caso-3 inv (-X, so arteria)", color="#d62728",
         frd=REPO / "cases/on-caso-3-inv/ccx/on-caso-3-inv_Pc9034.frd",
         sta=REPO / "cases/on-caso-3-inv/ccx/on-caso-3-inv_Pc9034.sta"),
]


def parse_frd_last_disp(path: Path):
    """Retorna (coords{n:(x,y,z)}, last_disp{n:(ux,uy,uz)})."""
    coords, last = {}, {}
    inc = ind = False
    cur = {}

    def fld(line, i):
        return float(line[13 + i * 12: 13 + (i + 1) * 12])

    for line in path.open():
        if "C" == line[5:6] and "2C" in line[:6]:
            inc = True
            continue
        if inc:
            if line[:3] == " -1":
                coords[int(line[3:13])] = (fld(line, 0), fld(line, 1), fld(line, 2))
                continue
            if line[:3] == " -3":
                inc = False
                continue
        if "DISP" in line and line[:3].strip() in ("-4", ""):
            ind = True
            cur = {}
            continue
        if ind:
            if line[:3] == " -1":
                cur[int(line[3:13])] = (fld(line, 0), fld(line, 1), fld(line, 2))
                continue
            if line[:3] == " -3":
                last = cur
                ind = False
                continue
    return coords, last


def axis_profile(coords, disp):
    rows = []
    for n, (x, y, z) in coords.items():
        if n not in disp:
            continue
        if (x * x + y * y) ** 0.5 <= R_AXIS and z <= 0.0305:
            ux, uy, uz = disp[n]
            rows.append((z, ux, uy, uz))
    rows.sort()
    arr = np.array(rows)
    zs = np.unique(np.round(arr[:, 0], 9))
    z0, ux, uy, uz = [], [], [], []
    for zv in zs:
        m = np.abs(arr[:, 0] - zv) < 1e-9
        z0.append(zv); ux.append(arr[m, 1].mean())
        uy.append(arr[m, 2].mean()); uz.append(arr[m, 3].mean())
    return np.array(z0), np.array(ux), np.array(uy), np.array(uz)


def parse_sta(path: Path):
    """(n_incrementos, n_cutbacks). cutback = linha com 'U' (attempt falho) ou ATT>1."""
    if not path.exists():
        return 0, 0
    n_inc = n_cut = 0
    for line in path.open():
        s = line.split()
        if len(s) >= 4 and s[0].isdigit():
            n_inc += 1
            if "U" in line:
                n_cut += 1
    return n_inc, n_cut


def main():
    results = []
    for c in CASES:
        if not c["frd"].exists():
            print(f"[FALTA] {c['key']}: {c['frd']} nao existe -- rode o Allrun.")
            continue
        coords, disp = parse_frd_last_disp(c["frd"])
        z, ux, uy, uz = axis_profile(coords, disp)
        imax = int(np.argmax(np.abs(ux)))
        ninc, ncut = parse_sta(c["sta"])
        results.append(dict(c=c, z=z, ux=ux, uy=uy, uz=uz,
                            ux_ext=ux[imax], z_ext=z[imax],
                            uz_span=(uz.max() - uz.min()), ninc=ninc, ncut=ncut,
                            nlat=int((np.diff(np.sign(np.gradient(ux, z))) != 0).sum())))

    # --- sumario texto ---
    lines = ["=" * 78,
             "COMPARACAO caso-3: puro vs sf vs inv  (P_contact=9034 Pa, Winkler 200 kPa/m)",
             "=" * 78, ""]
    hdr = f"{'caso':<32}{'|Ux|max':>10}{'z(mm)':>8}{'lado':>6}{'Uz span':>10}{'inc':>5}{'cut':>5}{'lat':>5}"
    lines.append(hdr); lines.append("-" * 78)
    for r in results:
        lado = "+X" if r["ux_ext"] > 0 else "-X"
        lines.append(f"{r['c']['label']:<32}{abs(r['ux_ext'])*1e6:>8.1f}um"
                     f"{r['z_ext']*1e3:>8.1f}{lado:>6}{r['uz_span']*1e6:>8.1f}um"
                     f"{r['ninc']:>5}{r['ncut']:>5}{r['nlat']:>5}")
    lines += ["", "Legenda:",
              "  |Ux|max : deflexao lateral max do eixo do nervo (kink da arteria)",
              "  z       : posicao axial do pico de deflexao",
              "  Uz span : amplitude de compressao axial (puro tem Dz=-1.5mm; sf/inv ~0)",
              "  inc/cut : incrementos Riks / cortes de passo (cut alto = sanfona numerica)",
              "  lat     : inversoes de sinal de Ux ao longo de z (>1 = sanfona lateral)"]
    txt = "\n".join(lines) + "\n"
    print(txt)
    OUT_TXT.write_text(txt)

    # --- figura ---
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    ax = axes[0]
    for r in results:
        ax.plot(r["z"] * 1e3, r["ux"] * 1e6, "o-", color=r["c"]["color"],
                label=r["c"]["label"])
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xlabel("z (mm)"); ax.set_ylabel("Ux do eixo (um)")
    ax.set_title("Deflexao lateral do eixo do nervo Ux(z)")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    ax = axes[1]
    for r in results:
        ax.plot(r["ux"] * 1e6, (r["z"] + r["uz"]) * 1e3, "o-", color=r["c"]["color"],
                label=r["c"]["label"])
    ax.set_xlabel("Ux deformado (um)"); ax.set_ylabel("z + Uz (mm)")
    ax.set_title("Eixo deformado (exagero real)")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    fig.suptitle("Familia caso-3 - efeito da arteria oftalmica no eixo do nervo",
                 fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(OUT_PNG, dpi=140)
    print(f"figura: {OUT_PNG}")
    print(f"sumario: {OUT_TXT}")


if __name__ == "__main__":
    main()
