#!/usr/bin/env python3
"""
analyze_on-caso-3-sf_force.py
=============================
Compara, no estudo de independencia de malha do 3F, DUAS especificacoes da carga
arterial:

  (P) PRESSAO FIXA  p_c = 9034 Pa  (formulacao do artigo)
  (F) FORCA  FIXA   ~71.7 mN       (P escalada por malha: P = 9034*71.7/F_lat)

Conclusao do experimento "poe uma forca":
  - Sob PRESSAO fixa, a deflexao lateral do eixo CONVERGE no refino radial
    (332.6 -> 333.0 -> 333.0 um; <0.2%).
  - Sob FORCA fixa, a MESMA serie NAO converge (332.6 -> 404 -> 426 um): manter a
    resultante exige aumentar p_c na lamina mais resolvida/compliante, e e' a
    PRESSAO (nao a resultante) que governa a deflexao. Alem disso, no refino
    GLOBAL fino (f150) a forca fixa exige p_c=19744 Pa > limiar de snap (~13.5 kPa
    do sweep), e o Riks diverge (colapso ~lambda=0.29).
  => a variavel de controle fisicamente convergente deste modelo de contato
     prescrito e' a PRESSAO; a resultante e' uma grandeza secundaria sensivel a'
     malha. "Por uma forca" PIORA a convergencia.

Saidas: brunaStuff/on-caso-3-sf_force.png e _force_summary.txt
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from importlib import import_module
mi = import_module("analyze_on-caso-3-sf_meshindep")

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "brunaStuff"
DECK = "on-caso-3-sf"


def frd_base(tag, prod=False):
    d = REPO / "cases" / DECK / "ccx" if prod else REPO / "cases/_mi" / f"{DECK}__{tag}" / "ccx"
    return d / f"{DECK}.frd"


def frd_force(tag, prod=False):
    d = REPO / "cases" / DECK / "ccx" if prod else REPO / "cases/_mi" / f"{DECK}__{tag}" / "ccx"
    return d / f"{DECK}_F.frd"


# (rotulo, tag, prod, pia/dura, P_force)
RADIAL = [
    ("f100 (pia1/dura2)", "f100", True, "1/2", 9034),
    ("radpia2dura3", "radpia2dura3", False, "2/3", 10671),
    ("radpia3dura4", "radpia3dura4", False, "3/4", 11200),
]


def ux(frd):
    m = mi.metrics(frd)
    return m["ux_axis_max_um"] if m else float("nan")


def main():
    L = []
    p = L.append
    p("=" * 84)
    p("3F: PRESSAO FIXA (p_c=9034) vs FORCA FIXA (~71.7 mN) no refino RADIAL")
    p("=" * 84)
    p(f"{'nivel':<20}{'pia/dura':>9}{'|Ux| (P fixa)':>15}{'P_forca[Pa]':>13}{'|Ux| (F fixa)':>15}")
    p("-" * 72)
    rows = []
    for lab, tag, prod, pd, pf in RADIAL:
        uxp = ux(frd_base(tag, prod))
        uxf = ux(frd_base(tag, prod)) if tag == "f100" else ux(frd_force(tag, prod))
        rows.append((lab, pd, uxp, pf, uxf))
        p(f"{lab:<20}{pd:>9}{uxp:>13.1f}um{pf:>13}{uxf:>13.1f}um")
    p("")
    up0, uf0 = rows[0][2], rows[0][4]
    p(f"Espalhamento radial sob PRESSAO fixa: "
      f"{min(r[2] for r in rows):.1f}..{max(r[2] for r in rows):.1f} um "
      f"({100*(max(r[2] for r in rows)-min(r[2] for r in rows))/up0:+.1f}% do f100) -> CONVERGE")
    p(f"Espalhamento radial sob FORCA   fixa: "
      f"{min(r[4] for r in rows):.1f}..{max(r[4] for r in rows):.1f} um "
      f"({100*(max(r[4] for r in rows)-min(r[4] for r in rows))/uf0:+.1f}% do f100) -> NAO converge")
    p("")
    p("GLOBAL fino f150 sob FORCA fixa: p_c=19744 Pa (> snap ~13.5 kPa) -> Riks DIVERGE")
    p("(blow-up ~lambda=0.29; deslocamento nodal -> metros). Sob PRESSAO fixa, f150")
    p("converge mas com footprint diferente (5 faces vs 2), ver on-caso-3-sf_meshindep.")
    p("")
    p("CONCLUSAO: a variavel de controle convergente deste contato prescrito e' a")
    p("PRESSAO p_c, nao a resultante. Fixar a forca PIORA a convergencia.")
    txt = "\n".join(L) + "\n"
    print(txt)
    (OUT / "on-caso-3-sf_force_summary.txt").write_text(txt)

    # figura
    fig, ax = plt.subplots(figsize=(8, 5.2))
    x = list(range(len(rows)))
    ax.plot(x, [r[2] for r in rows], "o-", lw=2, ms=9, color="#2ca02c",
            label="PRESSAO fixa (p_c=9034 Pa) -> converge")
    ax.plot(x, [r[4] for r in rows], "s--", lw=2, ms=9, color="#d62728",
            label="FORCA fixa (~71.7 mN) -> NAO converge")
    for i, r in enumerate(rows):
        ax.annotate(f"{r[2]:.0f}", (i, r[2]), textcoords="offset points",
                    xytext=(0, 8), ha="center", fontsize=9, color="#2ca02c")
        ax.annotate(f"{r[4]:.0f}", (i, r[4]), textcoords="offset points",
                    xytext=(0, 8), ha="center", fontsize=9, color="#d62728")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{r[0]}\n({r[1]})" for r in rows], fontsize=9)
    ax.set_ylabel("|Ux|max do eixo do nervo (um)")
    ax.set_title("3F - refino RADIAL: pressao fixa converge, forca fixa nao\n"
                 "(f150 global sob forca fixa diverge por snap; p_c=19744>13.5 kPa)",
                 fontsize=11)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9, loc="center left")
    fig.tight_layout()
    png = OUT / "on-caso-3-sf_force.png"
    fig.savefig(png, dpi=140)
    print(f"Figura: {png}")


if __name__ == "__main__":
    main()
