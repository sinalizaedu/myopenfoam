"""Health check do FSI ao-mestrado: Q, |U|max, |D| no watchpoint, sigma/eps."""

from __future__ import annotations

import os
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

DIAG = Path("/tmp/_diag_export")
OUT = Path(__file__).parent / "artoph_fsi_health_check.png"

RHO = 1060.0  # kg/m^3 (sangue)


def _load_inletQ(path: Path) -> tuple[np.ndarray, np.ndarray]:
    rows: list[tuple[float, float]] = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            t, *rest = re.split(r"\s+", line)
            try:
                rows.append((float(t), float(rest[-1])))
            except ValueError:
                continue
    arr = np.array(rows)
    return arr[:, 0], arr[:, 1]


def _load_volFieldValue(path: Path) -> tuple[np.ndarray, np.ndarray]:
    rows: list[tuple[float, float]] = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = re.split(r"\s+", line)
            try:
                rows.append((float(parts[0]), float(parts[-1])))
            except ValueError:
                continue
    arr = np.array(rows)
    return arr[:, 0], arr[:, 1]


def _load_watchpoint(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Returns t, |D| in m, magD column already provided."""
    data = np.loadtxt(path, comments="#")
    t = data[:, 0]
    Dx, Dy, Dz = data[:, 1], data[:, 2], data[:, 3]
    magD = np.sqrt(Dx**2 + Dy**2 + Dz**2)
    return t, magD, Dy  # Dy = componente radial dominante


def _load_sigma(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    data = np.loadtxt(path)
    return data[:, 0], data[:, 1], data[:, 2]


def main() -> None:
    t_q, Q_kin = _load_inletQ(DIAG / "inletQ.dat")
    Q = Q_kin  # phi ja eh m^3/s no incompressivel; nao multiplicar por rho
    Q_ml_per_min = Q * 1e6 * 60.0

    t_u, Umax = _load_volFieldValue(DIAG / "Umax.dat")
    Umax_cm = Umax * 100.0

    t_d, magD, Dy = _load_watchpoint(DIAG / "D_watch.dat")
    magD_um = magD * 1e6
    Dy_um = Dy * 1e6

    t_s, sigma, eps = _load_sigma(DIAG / "sigma_eps_per_time.dat")
    sigma_kPa = sigma / 1000.0

    fig, axes = plt.subplots(2, 2, figsize=(13, 9), sharex=True)

    ax = axes[0, 0]
    ax.plot(t_q, Q_ml_per_min, color="C0", lw=1.0)
    ax.axhspan(70, 200, alpha=0.15, color="green", label="fisiologico (70-200 mL/min)")
    ax.set_ylabel("Q_inlet [mL/min]")
    ax.set_title("Vazao no inlet (sinal ~ flat = nao pulsatil)")
    ax.grid(alpha=0.3)
    ax.legend(loc="best", fontsize=8)

    ax = axes[0, 1]
    ax.plot(t_u, Umax_cm, color="C1", lw=1.0)
    ax.axhspan(10, 20, alpha=0.15, color="green", label="pico fisiologico (10-20 cm/s)")
    ax.set_ylabel("|U|_max [cm/s]")
    ax.set_title("Velocidade maxima no dominio fluido")
    ax.grid(alpha=0.3)
    ax.legend(loc="best", fontsize=8)

    ax = axes[1, 0]
    ax.plot(t_d, magD_um, color="C2", lw=1.0, label="|D| total")
    ax.plot(t_d, Dy_um, color="C2", lw=0.6, ls="--", alpha=0.7, label="Dy (radial)")
    ax.axvspan(0.0, 0.03, alpha=0.15, color="orange", label="rampa Hann")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("|D| no watchpoint perto de P_contact [um]")
    ax.set_title("Deslocamento da parede (overshoot inicial = rampa)")
    ax.grid(alpha=0.3)
    ax.legend(loc="best", fontsize=8)

    ax = axes[1, 1]
    ax2 = ax.twinx()
    line1, = ax.plot(t_s, sigma_kPa, color="C3", lw=1.5, marker="o", ms=3, label="σ_vM max")
    line2, = ax2.plot(t_s, eps * 100, color="C4", lw=1.5, marker="s", ms=3, label="ε_vM max")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("σ_vM max [kPa]", color="C3")
    ax2.set_ylabel("ε_vM max [%]", color="C4")
    ax.tick_params(axis="y", labelcolor="C3")
    ax2.tick_params(axis="y", labelcolor="C4")
    ax.set_title("Tensao e deformacao maximas (campo)")
    ax.grid(alpha=0.3)
    ax.legend([line1, line2], [l.get_label() for l in (line1, line2)], loc="best", fontsize=8)

    fig.suptitle(
        "FSI ao-mestrado - panorama de saude (1 ciclo, T=0.870 s, HR=69 bpm)",
        fontsize=12, fontweight="bold",
    )
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(OUT, dpi=150)
    print(f"Saved: {OUT}")

    print("\n=== Sumario quantitativo ===")
    after_ramp = t_d > 0.03
    print(f"  |D|_max (apos rampa)    = {magD_um[after_ramp].max():.1f} um  @ t={t_d[after_ramp][np.argmax(magD_um[after_ramp])]:.3f} s")
    print(f"  |D|_pico_overshoot      = {magD_um.max():.1f} um  @ t={t_d[np.argmax(magD_um)]:.3f} s (rampa)")
    print(f"  Q_inlet medio (regime)  = {Q_ml_per_min[t_q > 0.3].mean():.4f} mL/min")
    print(f"  |U|_max regime          = {Umax_cm[t_u > 0.3].mean():.3f} cm/s")
    print(f"  σ_vM_max no ciclo       = {sigma_kPa.max():.1f} kPa @ t={t_s[np.argmax(sigma_kPa)]:.2f} s")
    print(f"  ε_vM_max no ciclo       = {eps.max() * 100:.1f} %  @ t={t_s[np.argmax(eps)]:.2f} s")


if __name__ == "__main__":
    main()
