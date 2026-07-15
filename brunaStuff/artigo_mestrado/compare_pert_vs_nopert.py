#!/usr/bin/env python3
"""
compare_pert_vs_nopert.py
=========================
Compara a forma deformada do complexo nervo optico entre:
  - on-caso-2     : COM perturbacao lateral antissimetrica A/B (gatilho modo S)
  - on-caso-2sP   : SEM perturbacao lateral (apenas driving do globo)

Objetivo: caracterizar quantitativamente a observacao visual de que, sem
perturbacao, o nervo assume uma forma suave (sino/seno-like), enquanto com
a perturbacao o resultado fica "baguncado" (multi-lobo / forcado).

Para cada caso, le o ULTIMO incremento .vtu (lambda=1.0, Dz=-1.5 mm) e:
  1) reconstroi o eixo deformado do nervo: para cada fatia em z (coord. nao
     deformada), calcula o centroide lateral (x0+Ux, y0+Uy) dos nos do nucleo
     ON (r0 < 1.5 mm). -> axis_x(z), axis_y(z)
  2) mede o kink lateral max e conta inflexoes (zero-crossings da curvatura)
     para distinguir modo suave (1 arco) de bagunca (multi-lobo).
  3) plota: (A) eixo lateral X(z) sobreposto; (B,C) vista XZ deformada (warp x1)
     de cada caso.

Rodar com o python que tem vtk: /tmp/ccx2pv/bin/python3
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "brunaStuff" / "on-caso-2_pert_vs_nopert.png"

CASES = {
    "COM perturbacao A/B\n(on-caso-2)": REPO / "cases" / "on-caso-2" / "ccx",
    "SEM perturbacao\n(on-caso-2sP)": REPO / "cases" / "on-caso-2sP" / "ccx",
}

R_ON = 1.5e-3   # m, raio do nucleo neural (ON)


def last_vtu(ccx_dir: Path) -> Path:
    vtus = list(ccx_dir.glob("*.vtu"))
    if not vtus:
        raise SystemExit(f"Nenhum .vtu em {ccx_dir}")

    def inc(p: Path) -> int:
        return int(p.stem.split(".")[-1])

    return max(vtus, key=inc)


def read_case(ccx_dir: Path):
    f = last_vtu(ccx_dir)
    rdr = vtk.vtkXMLUnstructuredGridReader()
    rdr.SetFileName(str(f))
    rdr.Update()
    g = rdr.GetOutput()
    pts = vtk_to_numpy(g.GetPoints().GetData())  # coords NAO deformadas (m)
    U = vtk_to_numpy(g.GetPointData().GetArray("U"))  # deslocamento (m)
    return f.name, pts, U


def nerve_axis(pts, U, nbins=12):
    """Centroide lateral do nucleo ON por fatia de z (coord nao deformada)."""
    x0, y0, z0 = pts[:, 0], pts[:, 1], pts[:, 2]
    r0 = np.hypot(x0, y0)
    core = r0 < R_ON * 1.001
    xc = x0[core] + U[core, 0]
    yc = y0[core] + U[core, 1]
    zc = z0[core]
    zmin, zmax = z0.min(), z0.max()
    edges = np.linspace(zmin, zmax, nbins + 1)
    zmid, ax_x, ax_y = [], [], []
    for i in range(nbins):
        m = (zc >= edges[i]) & (zc < edges[i + 1])
        if m.sum() == 0:
            continue
        zmid.append(0.5 * (edges[i] + edges[i + 1]))
        ax_x.append(xc[m].mean())
        ax_y.append(yc[m].mean())
    return np.array(zmid), np.array(ax_x), np.array(ax_y)


def count_inflections(z, x):
    """Numero de zero-crossings da 2a derivada (mudancas de concavidade)."""
    if len(z) < 5:
        return 0
    d2 = np.gradient(np.gradient(x, z), z)
    s = np.sign(d2)
    s = s[s != 0]
    return int(np.sum(np.diff(s) != 0))


def main():
    fig = plt.figure(figsize=(15, 5.5))
    gsA = fig.add_axes([0.06, 0.13, 0.40, 0.74])
    axes_xz = [fig.add_axes([0.53, 0.13, 0.20, 0.74]),
               fig.add_axes([0.77, 0.13, 0.20, 0.74])]

    colors = ["#c0392b", "#2471a3"]
    summary = []

    for (label, ccx_dir), col, ax_xz in zip(CASES.items(), colors, axes_xz):
        fname, pts, U = read_case(ccx_dir)
        z, ax_x, ax_y = nerve_axis(pts, U)
        lat = np.hypot(ax_x, ax_y)

        # kink lateral max (todos os nos, nao so o eixo)
        ulat_all = np.hypot(U[:, 0], U[:, 1])
        kink_mm = ulat_all.max() * 1e3
        ninfl = count_inflections(z, ax_x)
        summary.append((label, kink_mm, ninfl, fname))

        # Painel A: eixo lateral X(z)
        gsA.plot(ax_x * 1e3, z * 1e3, "-o", color=col, ms=4, lw=2,
                 label=f"{label.splitlines()[0]}  (|U_lat|max={kink_mm:.2f} mm)")

        # Painel XZ: nuvem deformada com WARP LATERAL amplificado (x:15) para
        # a forma de flambagem ficar visivel (deslocamento real e' sub-mm).
        WARP = 15.0
        defx = (pts[:, 0] + WARP * U[:, 0]) * 1e3
        defz = (pts[:, 2] + U[:, 2]) * 1e3
        sc = ax_xz.scatter(defx, defz, c=ulat_all * 1e3, s=3, cmap="viridis",
                           vmin=0, vmax=max(kink_mm, 0.05))
        # sobrepoe o eixo deformado (mesmo warp lateral)
        ax_xz.plot(ax_x * 1e3 * WARP, z * 1e3, "r-", lw=2, label="eixo ON")
        ax_xz.set_title(f"{label}\n(warp lateral x{WARP:.0f})", fontsize=8)
        ax_xz.set_xlabel(f"x + {WARP:.0f}*Ux (mm)")
        ax_xz.grid(alpha=0.3)
        fig.colorbar(sc, ax=ax_xz, fraction=0.046, pad=0.04, label="|U_lat| (mm)")

    axes_xz[0].set_ylabel("z (mm)")
    gsA.set_xlabel("deslocamento lateral do eixo do nervo  X(z)  (mm)")
    gsA.set_ylabel("z (mm)  [0=canal optico, 30=lamina cribrosa]")
    gsA.axvline(0, color="k", lw=0.7, alpha=0.5)
    gsA.set_title("Eixo deformado do nucleo neural (ON, r<1.5 mm)")
    gsA.legend(loc="upper right", fontsize=8)
    gsA.grid(alpha=0.3)

    fig.suptitle("on-caso-2: efeito da perturbacao lateral A/B na forma de flambagem "
                 "(lambda=1.0, Dz=-1.5 mm)", fontsize=11)
    fig.savefig(OUT, dpi=130)
    print(f"Figura salva em {OUT}")
    print("\n=== Resumo ===")
    for label, kink, ninfl, fname in summary:
        lab = label.replace("\n", " ")
        print(f"  {lab:35s}  kink={kink:.3f} mm  inflexoes={ninfl}  ({fname})")


if __name__ == "__main__":
    main()
