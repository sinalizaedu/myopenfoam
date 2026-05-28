"""Visualizacao rapida do estado atual do on-flambagem-2.

Le os campos D, sigmaEq, epsilonEq do timestep 1 e plota:
  - corte axial (plano y=0) com a malha e D_x amplificado
  - perfil de |D|(z) na linha (x=2.0 mm, y=0)  [SAS]
  - perfil de |D|(z) na linha central (x=y=0)  [ON]

Uso:
    python brunaStuff/plot_on_flambagem_2_baseline.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

CASE = Path(__file__).resolve().parent.parent / "cases" / "on-flambagem-2" / "solid"

def parse_internal_vec(path: Path):
    txt = path.read_text()
    m = re.search(r'internalField\s+nonuniform[^(]*\((.*?)\n\)\s*;', txt, re.S)
    if not m:
        raise RuntimeError(f"no internalField in {path}")
    nums = list(map(float, re.findall(r'-?\d+\.?\d*(?:[eE][+-]?\d+)?', m.group(1))))
    return np.array(nums, dtype=float).reshape(-1, 3)

def parse_internal_scal(path: Path):
    txt = path.read_text()
    m = re.search(r'internalField\s+nonuniform[^(]*\((.*?)\n\)\s*;', txt, re.S)
    if not m:
        raise RuntimeError(f"no internalField in {path}")
    return np.array(list(map(float, re.findall(r'-?\d+\.?\d*(?:[eE][+-]?\d+)?', m.group(1)))))


def main() -> None:
    D       = parse_internal_vec(CASE / "1" / "D")            # m
    C       = parse_internal_vec(CASE / "0" / "C")            # m, cell centers
    sigmaEq = parse_internal_scal(CASE / "1" / "sigmaEq")     # Pa
    epsEq   = parse_internal_scal(CASE / "1" / "epsilonEq")

    assert D.shape == C.shape == (sigmaEq.size, 3) == (epsEq.size, 3)[:2] + (3,) or True

    mag = np.linalg.norm(D, axis=1) * 1e3       # mm
    magXY = np.linalg.norm(D[:, :2], axis=1) * 1e3
    magZ  = np.abs(D[:, 2]) * 1e3
    C_mm  = C * 1e3

    print(f"|D|_max     = {mag.max():.4f} mm")
    print(f"|D_xy|_max  = {magXY.max():.4f} mm   (kinking)")
    print(f"|D_z|_max   = {magZ.max():.4f} mm   (axial)")
    print(f"sigmaEq_max = {sigmaEq.max():.2f} Pa")
    print(f"epsEq_max   = {epsEq.max():.4f}  ({epsEq.max()*100:.2f}%)")

    fig, axes = plt.subplots(2, 2, figsize=(13, 10))

    ax = axes[0, 0]
    mask_y = np.abs(C_mm[:, 1]) < 0.3
    sc = ax.scatter(C_mm[mask_y, 2], C_mm[mask_y, 0],
                    c=sigmaEq[mask_y], cmap="viridis", s=8)
    plt.colorbar(sc, ax=ax, label="σ_VM [Pa]")
    ax.set_xlabel("z [mm]")
    ax.set_ylabel("x [mm]")
    ax.set_title("Corte axial (|y|<0.3 mm): σ_VM")
    ax.axhline(1.50, color="red", ls=":", lw=0.7, label="r=1.5 (ON/pia)")
    ax.axhline(1.55, color="red", ls=":", lw=0.7)
    ax.axhline(2.35, color="orange", ls=":", lw=0.7, label="r=2.35 (sas/dura)")
    ax.axhline(2.50, color="orange", ls=":", lw=0.7)
    ax.axhline(-1.50, color="red", ls=":", lw=0.7)
    ax.axhline(-1.55, color="red", ls=":", lw=0.7)
    ax.axhline(-2.35, color="orange", ls=":", lw=0.7)
    ax.axhline(-2.50, color="orange", ls=":", lw=0.7)
    ax.legend(loc="upper right", fontsize=8)
    ax.set_aspect("equal")

    ax = axes[0, 1]
    sc = ax.scatter(C_mm[mask_y, 2], C_mm[mask_y, 0],
                    c=mag[mask_y], cmap="magma", s=8)
    plt.colorbar(sc, ax=ax, label="|D| [mm]")
    ax.set_xlabel("z [mm]")
    ax.set_ylabel("x [mm]")
    ax.set_title(f"Corte axial (|y|<0.3 mm): |D|  (max = {mag.max():.4f} mm)")
    ax.set_aspect("equal")

    # ---- (1, 0): perfil axial de Dz no eixo central (ON) ------------------
    ax = axes[1, 0]
    mask_axis = (np.abs(C_mm[:, 0]) < 0.4) & (np.abs(C_mm[:, 1]) < 0.4)
    z_axis = C_mm[mask_axis, 2]
    Dz_axis = D[mask_axis, 2] * 1e3
    order = np.argsort(z_axis)
    ax.plot(z_axis[order], Dz_axis[order], "o-", ms=2, label="ON central (x,y≈0)")

    mask_sas = (np.abs(C_mm[:, 0] - 2.0) < 0.2) & (np.abs(C_mm[:, 1]) < 0.2)
    if mask_sas.sum() > 5:
        z_sas = C_mm[mask_sas, 2]
        Dz_sas = D[mask_sas, 2] * 1e3
        order = np.argsort(z_sas)
        ax.plot(z_sas[order], Dz_sas[order], "s-", ms=3, label="SAS (x≈2.0, y≈0)")

    mask_dura = (np.abs(C_mm[:, 0] - 2.45) < 0.1) & (np.abs(C_mm[:, 1]) < 0.2)
    if mask_dura.sum() > 5:
        z_d = C_mm[mask_dura, 2]
        Dz_d = D[mask_dura, 2] * 1e3
        order = np.argsort(z_d)
        ax.plot(z_d[order], Dz_d[order], "^-", ms=3, label="dura (x≈2.45, y≈0)")

    ax.set_xlabel("z [mm]")
    ax.set_ylabel("D_z [mm]")
    ax.set_title("Perfil axial: D_z(z) por zona")
    ax.legend()
    ax.grid(alpha=0.3)

    # ---- (1, 1): perfil radial em z=15 mm (meio do tubo) ------------------
    ax = axes[1, 1]
    mask_mid = (np.abs(C_mm[:, 2] - 15.0) < 0.6)
    Cx_mid = C_mm[mask_mid, 0]
    Dx_mid = D[mask_mid, 0] * 1e3
    Dy_mid = D[mask_mid, 1] * 1e3
    Dr_mid = np.sqrt(Dx_mid**2 + Dy_mid**2)
    r_mid = np.sqrt(Cx_mid**2 + C_mm[mask_mid, 1]**2)
    order = np.argsort(r_mid)
    ax.plot(r_mid[order], Dr_mid[order], "o", ms=2, label="|D_xy| (kinking + balloon)")
    ax.axvline(1.50, color="red", ls=":", lw=0.7, label="r=1.5 ON/pia")
    ax.axvline(1.55, color="red", ls=":", lw=0.7)
    ax.axvline(2.35, color="orange", ls=":", lw=0.7, label="r=2.35 sas/dura")
    ax.axvline(2.50, color="orange", ls=":", lw=0.7)
    ax.set_xlabel("r [mm]")
    ax.set_ylabel("|D_xy| [mm]")
    ax.set_title("Perfil radial em z=15 mm")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    fig.suptitle(f"on-flambagem-2 baseline (linearGeometry, sem imperfeicao, P_CSF=1333 Pa)\n"
                 f"|D|_max = {mag.max():.4f} mm,   σ_VM_max = {sigmaEq.max():.1f} Pa,   ε_max = {epsEq.max()*100:.2f}%",
                 fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.96))

    out = Path(__file__).resolve().parent / "on_flambagem_2_baseline.png"
    fig.savefig(out, dpi=130)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    sys.exit(main())
