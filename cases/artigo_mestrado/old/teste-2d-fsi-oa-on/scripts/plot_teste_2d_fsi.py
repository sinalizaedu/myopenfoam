#!/usr/bin/env python3
"""plot_teste_2d_fsi.py

Plota resultados do caso `cases/teste-2d-fsi-oa-on/` (FSI one-way preCICE):

    1. teste_2d_fsi_pressure_input.png  -- onda OMVS de pressao no inlet/outlet
       lida de fluid/constant/{inlet,outlet}_pressure.dat (input)

    2. teste_2d_fsi_force_watchpoints.png -- forca Y no centro de lumen_bot e
       lumen_top ao longo do tempo (preCICE watchpoints)

    3. teste_2d_fsi_uy_field.png -- campo de deslocamento Dy no solido no
       ultimo timestep (final), com sobreposicao dos contornos da OA e da
       ONS para contexto geometrico
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Tuple

import matplotlib.pyplot as plt
import numpy as np

# Detecta automaticamente o local: brunaStuff/ ou cases/<x>/scripts/
SCRIPT_DIR = Path(__file__).resolve().parent
if SCRIPT_DIR.name == "scripts":
    CASE = SCRIPT_DIR.parent
    OUT_DIR = SCRIPT_DIR.parent  # plots no proprio caso
else:
    REPO = SCRIPT_DIR.parent
    CASE = REPO / "cases" / "teste-2d-fsi-oa-on"
    OUT_DIR = SCRIPT_DIR

RHO = 1050.0
MMHG_TO_PA = 133.322387415


def read_openfoam_table(path: Path) -> Tuple[np.ndarray, np.ndarray]:
    """Le tabela OpenFOAM Function1: linhas '(t v)' entre parenteses."""
    pattern = re.compile(r"\(\s*([-+0-9.eE]+)\s+([-+0-9.eE]+)\s*\)")
    times, vals = [], []
    with path.open() as fh:
        for line in fh:
            m = pattern.search(line)
            if m:
                times.append(float(m.group(1)))
                vals.append(float(m.group(2)))
    return np.array(times), np.array(vals)


def read_precice_watchpoint(path: Path) -> dict:
    """Le watchpoint preCICE (header + colunas)."""
    with path.open() as fh:
        header = fh.readline().split()
    data = np.loadtxt(path, skiprows=1)
    return {col: data[:, i] for i, col in enumerate(header)}


def read_internal_field_y(D_path: Path) -> Tuple[np.ndarray, np.ndarray]:
    """Le internalField do volVectorField D e retorna (cell_idx, Dy).

    Estrutura esperada:
        internalField   nonuniform List<vector>
        <N>
        (
        (Dx Dy Dz)
        (Dx Dy Dz)
        ...
        )
    """
    txt = D_path.read_text()
    m = re.search(r"internalField\s+nonuniform\s+List<vector>\s+(\d+)\s*\(([^)]*\).*?)\n\)", txt, re.S)
    if not m:
        # Fallback: parse manualmente
        in_field = False
        Dy = []
        for line in txt.splitlines():
            if "internalField" in line:
                in_field = True
                continue
            if "boundaryField" in line:
                in_field = False
                break
            if in_field:
                mm = re.match(r"\s*\(([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s*\)", line)
                if mm:
                    Dy.append(float(mm.group(2)))
        return np.arange(len(Dy)), np.array(Dy)

    n = int(m.group(1))
    vectors = re.findall(r"\(([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s*\)", m.group(2))
    Dy = np.array([float(v[1]) for v in vectors])
    return np.arange(len(Dy)), Dy


def latest_time_dir(side_dir: Path) -> Path:
    """Encontra a maior pasta numerica em side_dir/ (excluindo 0/)."""
    candidates = []
    for p in side_dir.iterdir():
        if p.is_dir():
            try:
                t = float(p.name)
                if t > 0:
                    candidates.append((t, p))
            except ValueError:
                continue
    if not candidates:
        return side_dir / "0"
    return max(candidates, key=lambda x: x[0])[1]


def plot_pressure_input() -> None:
    fluid_const = CASE / "fluid" / "constant"
    t_in, p_in = read_openfoam_table(fluid_const / "inlet_pressure.dat")
    t_out, p_out = read_openfoam_table(fluid_const / "outlet_pressure.dat")

    # Converte p/rho [m^2/s^2] de volta para mmHg para legibilidade
    p_in_mmhg = p_in * RHO / MMHG_TO_PA
    p_out_mmhg = p_out * RHO / MMHG_TO_PA

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(t_in, p_in_mmhg, label="inlet", linewidth=1.2)
    ax.plot(t_out, p_out_mmhg, label="outlet (lag 5 ms)", linewidth=1.0, alpha=0.7)
    ax.axvline(0.05, color="gray", linestyle=":", linewidth=0.8, label="smoke end")
    ax.set_xlabel("tempo [s]")
    ax.set_ylabel("pressao [mmHg]")
    ax.set_title("Onda OMVS de pressao arterial (input do FSI)\n80-120 mmHg, HR=69 bpm, Hann ramp 100 ms")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right")
    out = OUT_DIR / "teste_2d_fsi_pressure_input.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    print(f"Plotado: {out}")
    plt.close(fig)


def plot_force_watchpoints() -> None:
    solid = CASE / "solid"
    wb = solid / "precice-Solid-watchpoint-wallBotCenter.log"
    wt = solid / "precice-Solid-watchpoint-wallTopCenter.log"
    if not wb.exists() or not wt.exists():
        print(f"AVISO: watchpoints nao encontrados ({wb}, {wt}). Pulando.")
        return
    d_bot = read_precice_watchpoint(wb)
    d_top = read_precice_watchpoint(wt)

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(d_bot["Time"], d_bot["Force1"] * 1e3, label="lumen_bot (Y)", color="C0")
    ax.plot(d_top["Time"], d_top["Force1"] * 1e3, label="lumen_top (Y)", color="C3")
    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_xlabel("tempo [s]")
    ax.set_ylabel("Fy por face [mN]")
    ax.set_title("Forca Y do fluido na parede (preCICE) -- watchpoints no x=11.25mm\n"
                 "lumen_bot recebe forca -Y (empurra parede para baixo). lumen_top recebe +Y (empurra para cima).")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower left")
    out = OUT_DIR / "teste_2d_fsi_force_watchpoints.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    print(f"Plotado: {out}")
    plt.close(fig)


def plot_uy_field() -> None:
    """Plot 2D do Dy no solido no ultimo timestep."""
    solid = CASE / "solid"
    last_dir = latest_time_dir(solid)
    if last_dir == solid / "0":
        print(f"AVISO: nenhum timestep > 0 em {solid}. Pulando uy_field.")
        return
    D_path = last_dir / "D"
    if not D_path.exists():
        print(f"AVISO: {D_path} nao existe. Pulando uy_field.")
        return

    _, Dy = read_internal_field_y(D_path)
    # Reconstruir grid: 4 blocos solidos em y, dx = LX/NX = 0.25 mm
    LX, NX = 0.020, 80
    Y_CONTACT, Y_WALL_BOT, Y_WALL_TOP, Y_OA_TOP, Y_TOP = 0.010, 0.0102, 0.0113, 0.0115, 0.020

    # Cell centers per block (NY_A=40, NY_B=2, NY_C=2, NY_D=34)
    def linspace_centers(y0, y1, n):
        dy = (y1 - y0) / n
        return np.linspace(y0 + dy / 2, y1 - dy / 2, n)

    yA = linspace_centers(0.0, Y_CONTACT, 40)
    yB = linspace_centers(Y_CONTACT, Y_WALL_BOT, 2)
    yC = linspace_centers(Y_WALL_TOP, Y_OA_TOP, 2)
    yD = linspace_centers(Y_OA_TOP, Y_TOP, 34)
    x_centers = linspace_centers(0.0, LX, NX)

    # Reshape Dy em 4 sub-blocos
    n_A = 40 * NX
    n_B = 2 * NX
    n_C = 2 * NX
    n_D = 34 * NX
    assert len(Dy) == n_A + n_B + n_C + n_D, f"Mismatch: {len(Dy)} vs {n_A+n_B+n_C+n_D}"

    Dy_A = Dy[:n_A].reshape(40, NX)
    Dy_B = Dy[n_A:n_A + n_B].reshape(2, NX)
    Dy_C = Dy[n_A + n_B:n_A + n_B + n_C].reshape(2, NX)
    Dy_D = Dy[n_A + n_B + n_C:].reshape(34, NX)

    fig, ax = plt.subplots(figsize=(7, 9))
    # Combinar em um unico campo plotavel: stack y de cada bloco
    extent_um = lambda y0, y1: [0, LX * 1e3, y0 * 1e3, y1 * 1e3]
    cmap = "RdBu_r"
    vmax = float(np.max(np.abs(Dy))) * 1e6  # em micrometros
    norm = plt.matplotlib.colors.Normalize(vmin=-vmax, vmax=vmax)

    ax.imshow(Dy_A * 1e6, extent=extent_um(0, Y_CONTACT), origin="lower",
              aspect="auto", cmap=cmap, norm=norm)
    ax.imshow(Dy_B * 1e6, extent=extent_um(Y_CONTACT, Y_WALL_BOT), origin="lower",
              aspect="auto", cmap=cmap, norm=norm)
    ax.imshow(Dy_C * 1e6, extent=extent_um(Y_WALL_TOP, Y_OA_TOP), origin="lower",
              aspect="auto", cmap=cmap, norm=norm)
    im = ax.imshow(Dy_D * 1e6, extent=extent_um(Y_OA_TOP, Y_TOP), origin="lower",
                   aspect="auto", cmap=cmap, norm=norm)

    # Highlight do LUMEN (sem solido) em cinza
    ax.add_patch(plt.matplotlib.patches.Rectangle(
        (0, Y_WALL_BOT * 1e3), LX * 1e3, (Y_WALL_TOP - Y_WALL_BOT) * 1e3,
        facecolor="lightgray", alpha=0.7, edgecolor="black", linewidth=0.5,
        label="lumen (fluido)",
    ))

    # ONS e ON
    theta = np.linspace(0, 2 * np.pi, 200)
    x_ons = 10 + 2.5 * np.cos(theta)
    y_ons = 7.5 + 2.5 * np.sin(theta)
    x_on = 10 + 1.5 * np.cos(theta)
    y_on = 7.5 + 1.5 * np.sin(theta)
    ax.plot(x_ons, y_ons, "k-", linewidth=0.7, label="ONS")
    ax.plot(x_on, y_on, "k--", linewidth=0.7, label="ON")

    # Marcadores
    ax.axhline(Y_CONTACT * 1e3, color="purple", linestyle="-", linewidth=0.8,
               label="contato OA/ONS (FIXED no smoke FSI)")
    ax.axhline(Y_WALL_BOT * 1e3, color="C0", linestyle="--", linewidth=0.7,
               label="lumen_bot (FSI)")
    ax.axhline(Y_WALL_TOP * 1e3, color="C3", linestyle="--", linewidth=0.7,
               label="lumen_top (FSI)")

    ax.set_xlim(0, LX * 1e3)
    ax.set_ylim(0, Y_TOP * 1e3)
    ax.set_xlabel("x [mm]")
    ax.set_ylabel("y [mm]")
    t_final = float(last_dir.name)
    ax.set_title(f"FSI one-way: deslocamento Dy do solido em t={t_final}s\n"
                 f"max |Dy| = {vmax:.2f} um  (lumen em cinza)")
    cbar = fig.colorbar(im, ax=ax, label="Dy [um]", fraction=0.04)
    ax.legend(loc="upper right", fontsize=7, framealpha=0.85)

    out = OUT_DIR / "teste_2d_fsi_uy_field.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    print(f"Plotado: {out}")
    plt.close(fig)


def main() -> None:
    print(f"CASE: {CASE}")
    plot_pressure_input()
    plot_force_watchpoints()
    plot_uy_field()


if __name__ == "__main__":
    main()
