#!/usr/bin/env python3
"""diag_on-caso-3-inv_sanfona.py
=================================
Diagnostica o "sanfonamento" (accordion / concertina) do nervo no
on-caso-3-inv. Le o .frd (ASCII, CalculiX), extrai os nos do EIXO do nervo
(zona ON, r ~ 0) e plota, para cada passo de saida:

  - Uz(z)           : deslocamento axial ao longo do eixo
  - dUz/dz (strain) : compressao/extensao local -> sanfona = sinal alternado
  - Ux,Uy (z)       : deflexao lateral (modo de kink)
  - eixo deformado (z+Uz vs Ux) : enxerga visualmente a dobra

Sanfona = a derivada dUz/dz ALTERNA de sinal varias vezes ao longo de z
(zonas comprimem e esticam em serie, como uma sanfona), em vez de uma
compressao monotona suave. Tambem conta-se o numero de "dobras".

Uso (no HOST, sem dependencias exoticas alem de numpy/matplotlib):
    python3 brunaStuff/diag_on-caso-3-inv_sanfona.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parent.parent
FRD = REPO / "cases" / "on-caso-3-inv" / "ccx" / "on-caso-3-inv_Pc9034.frd"
OUT = REPO / "brunaStuff" / "on-caso-3-inv_sanfona.png"

R_AXIS = 0.35e-3  # raio max p/ considerar "no do eixo" (nervo r<1.5mm)


def parse_frd(path: Path):
    """Retorna (coords{node:(x,y,z)}, steps[list of (label, {node:(ux,uy,uz)})])."""
    coords: dict[int, tuple[float, float, float]] = {}
    steps: list[tuple[str, dict[int, tuple[float, float, float]]]] = []

    in_coords = False
    in_disp = False
    cur_disp: dict[int, tuple[float, float, float]] = {}
    cur_label = ""

    def fld(line, i):
        # campos E12.5 a partir da coluna 13 (apos "-1" + node I10)
        s = line[13 + i * 12: 13 + (i + 1) * 12]
        return float(s)

    with path.open() as fh:
        for line in fh:
            key = line[:3]
            # bloco de coordenadas: " 2C" inicia, "-1" sao nodes, "-3" fecha
            if "2C" in line[:6] and "C" == line[5:6]:
                in_coords = True
                continue
            if in_coords:
                if key == " -1":
                    node = int(line[3:13])
                    coords[node] = (fld(line, 0), fld(line, 1), fld(line, 2))
                    continue
                if key == " -3":
                    in_coords = False
                    continue
            # bloco DISP: cabecalho contem "DISP"
            if "DISP" in line and key.strip() in ("-4", ""):
                in_disp = True
                cur_disp = {}
                # tenta achar o tempo/contador no cabecalho 1PSTEP anterior;
                # rotulamos sequencialmente
                cur_label = f"step {len(steps)+1}"
                continue
            if in_disp:
                if key == " -1":
                    node = int(line[3:13])
                    cur_disp[node] = (fld(line, 0), fld(line, 1), fld(line, 2))
                    continue
                if key == " -3":
                    steps.append((cur_label, cur_disp))
                    in_disp = False
                    continue
    return coords, steps


def axis_profile(coords, disp):
    """Nos do eixo (r<R_AXIS), ordenados por z. Retorna z0, ux, uy, uz."""
    rows = []
    for node, (x, y, z) in coords.items():
        if node not in disp:
            continue
        r = (x * x + y * y) ** 0.5
        if r <= R_AXIS and z <= 0.0305:  # so' o nervo (z<=30mm), exclui globo
            ux, uy, uz = disp[node]
            rows.append((z, ux, uy, uz))
    rows.sort()
    arr = np.array(rows)
    if arr.size == 0:
        return None
    # media por nivel z (varios nos no nucleo cartesiano por nivel)
    zs = np.unique(np.round(arr[:, 0], 9))
    z0, ux, uy, uz = [], [], [], []
    for zv in zs:
        m = np.abs(arr[:, 0] - zv) < 1e-9
        z0.append(zv)
        ux.append(arr[m, 1].mean())
        uy.append(arr[m, 2].mean())
        uz.append(arr[m, 3].mean())
    return (np.array(z0), np.array(ux), np.array(uy), np.array(uz))


def count_folds(z, uz):
    """Numero de inversoes de sinal de dUz/dz (cada inversao ~ 1 dobra)."""
    if len(z) < 3:
        return 0, np.array([])
    dudz = np.gradient(uz, z)
    sign = np.sign(dudz)
    flips = np.where(np.diff(sign) != 0)[0]
    return len(flips), dudz


def main():
    if not FRD.exists():
        raise SystemExit(f"frd nao encontrado: {FRD}")
    coords, steps = parse_frd(FRD)
    print(f"nos lidos: {len(coords)}, passos DISP: {len(steps)}")
    if not steps:
        raise SystemExit("nenhum bloco DISP parseado")

    # ultimo passo (lambda=1, Dz=-1.5mm)
    label, disp = steps[-1]
    prof = axis_profile(coords, disp)
    if prof is None:
        raise SystemExit("nenhum no de eixo encontrado (ajustar R_AXIS)")
    z, ux, uy, uz = prof
    nfolds, dudz = count_folds(z, uz)
    uz_span = uz.max() - uz.min()       # amplitude de compressao axial
    ux_span = np.abs(ux).max()
    # so' faz sentido falar de "sanfona axial" se houver compressao axial
    # relevante (|Uz| da ordem de >50 um). Sem Dz prescrito o Uz ~ 0 e a
    # derivada dUz/dz vira ruido -> nao e' sanfona.
    AXIAL_MIN = 50e-6
    nlat = count_folds(z, ux)[0]        # inversoes laterais (sanfona lateral)

    print(f"\nEIXO DO NERVO ({len(z)} niveis z, ultimo passo = {label}):")
    print(f"  Uz: min={uz.min()*1e3:+.4f} mm  max={uz.max()*1e3:+.4f} mm  (span={uz_span*1e6:.1f} um)")
    print(f"  Ux: min={ux.min()*1e6:+.2f} um  max={ux.max()*1e6:+.2f} um  (lateral)")
    if uz_span < AXIAL_MIN:
        print(f"  compressao axial DESPREZIVEL (span<{AXIAL_MIN*1e6:.0f} um): so' carga lateral.")
        print(f"  -> 'sanfona axial' nao se aplica. Inversoes laterais de Ux = {nlat}")
        if nlat <= 1:
            print("  >>> LATERAL LIMPO: lobulo unico (sem sanfona)")
        else:
            print("  >>> sanfona LATERAL: Ux troca de lado varias vezes")
    else:
        print(f"  inversoes de dUz/dz (dobras de sanfona axial) = {nfolds}")
        if nfolds >= 3:
            print("  >>> SANFONA: o eixo comprime/estica em serie (modo axial alto)")
        elif nfolds <= 1:
            print("  >>> compressao ~monotona (sem sanfona)")

    # ---- figura ----
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))

    ax = axes[0, 0]
    ax.plot(z * 1e3, uz * 1e3, "o-", color="#d62728")
    ax.set_xlabel("z (mm)"); ax.set_ylabel("Uz (mm)")
    ax.set_title("(1) Deslocamento axial Uz(z) no eixo do nervo")
    ax.grid(alpha=0.3)

    ax = axes[0, 1]
    ax.plot(z * 1e3, dudz, "o-", color="#9467bd")
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xlabel("z (mm)"); ax.set_ylabel("dUz/dz (strain axial)")
    ax.set_title(f"(2) Strain axial local  (inversoes={nfolds})\n"
                 "sinal alternado = SANFONA")
    ax.grid(alpha=0.3)

    ax = axes[1, 0]
    ax.plot(z * 1e3, ux * 1e6, "o-", label="Ux", color="#1f77b4")
    ax.plot(z * 1e3, uy * 1e6, "s-", label="Uy", color="#2ca02c")
    ax.set_xlabel("z (mm)"); ax.set_ylabel("deflexao lateral (um)")
    ax.set_title("(3) Deflexao lateral do eixo (modo de kink)")
    ax.legend(); ax.grid(alpha=0.3)

    ax = axes[1, 1]
    # eixo deformado: posicao axial deformada vs lateral deformada
    ax.plot(ux * 1e6, (z + uz) * 1e3, "o-", color="#ff7f0e")
    ax.set_xlabel("Ux deformado (um)"); ax.set_ylabel("z + Uz (mm)")
    ax.set_title("(4) Eixo deformado (exagero real)")
    ax.grid(alpha=0.3)

    fig.suptitle(f"on-caso-3-inv Pc9034 - diagnostico de sanfona ({label})",
                 fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(OUT, dpi=140)
    print(f"\nfigura: {OUT}")

    # ---- evolucao temporal: Ux(z) do eixo em TODOS os passos ----
    fig2, ax2 = plt.subplots(figsize=(9, 6))
    cmap = plt.cm.viridis(np.linspace(0, 1, len(steps)))
    print("\nEVOLUCAO do lobulo lateral (Ux_max e sua posicao) por passo:")
    for k, (lab, dsp) in enumerate(steps):
        pr = axis_profile(coords, dsp)
        if pr is None:
            continue
        zz, uxx, _, _ = pr
        ax2.plot(zz * 1e3, uxx * 1e6, "o-", color=cmap[k], label=f"{k+1}/{len(steps)}")
        imax = int(np.argmax(np.abs(uxx)))
        print(f"  passo {k+1}: Ux_ext = {uxx[imax]*1e6:+8.2f} um @ z={zz[imax]*1e3:5.1f} mm")
    ax2.axhline(0, color="k", lw=0.8)
    ax2.set_xlabel("z (mm)"); ax2.set_ylabel("Ux do eixo (um)")
    ax2.set_title("Evolucao do eixo lateral por passo Riks\n"
                  "(troca de lado = sanfona temporal)")
    ax2.legend(title="passo", fontsize=8, ncol=2)
    ax2.grid(alpha=0.3)
    out2 = REPO / "brunaStuff" / "on-caso-3-inv_sanfona_evol.png"
    fig2.tight_layout()
    fig2.savefig(out2, dpi=140)
    print(f"figura evolucao: {out2}")


if __name__ == "__main__":
    main()
