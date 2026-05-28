"""Health check do FSI ao-mestrado v2: 3 ciclos cardiacos com:
  - rampa Hann TOTAL 100ms (mata overshoot)
  - outlet shift 5ms (cria gradiente pulsatil)
  - extrai metricas do CICLO 3 (regime estacionario)
"""

from __future__ import annotations

import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

DIAG = Path("/tmp/_diag_export_v2")
OUT = Path(__file__).parent / "artoph_fsi_3cycles_health.png"

T_CYCLE = 0.8696
T_RAMP = 0.10


def _load_field(path: Path, value_col: int = -1) -> tuple[np.ndarray, np.ndarray]:
    rows: list[tuple[float, float]] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = re.split(r"\s+", line)
        try:
            rows.append((float(parts[0]), float(parts[value_col])))
        except (ValueError, IndexError):
            continue
    arr = np.array(rows)
    return arr[:, 0], arr[:, 1]


def _load_watch(path: Path) -> tuple[np.ndarray, np.ndarray]:
    data = np.loadtxt(path, comments="#")
    t = data[:, 0]
    Dx, Dy, Dz = data[:, 1], data[:, 2], data[:, 3]
    return t, np.sqrt(Dx**2 + Dy**2 + Dz**2)


def _load_sigma(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    data = np.loadtxt(path)
    return data[:, 0], data[:, 1], data[:, 2]


def main() -> None:
    t_qi, Q_in = _load_field(DIAG / "inletQ.dat")
    t_qo, Q_out = _load_field(DIAG / "outletQ.dat")
    t_u, Umax = _load_field(DIAG / "Umax.dat")
    t_d, magD = _load_watch(DIAG / "D_watch.dat")
    t_s, sigma, eps = _load_sigma(DIAG / "sigma_eps.dat")

    # Convertions
    Q_in_mlmin = Q_in * 1e6 * 60.0  # m^3/s -> mL/min
    Q_out_mlmin = Q_out * 1e6 * 60.0
    Umax_cm = Umax * 100.0
    magD_um = magD * 1e6
    sigma_kPa = sigma / 1000.0

    fig, axes = plt.subplots(3, 2, figsize=(14, 12), sharex=True)

    def add_cycle_lines(ax: plt.Axes) -> None:
        for k in range(1, 4):
            ax.axvline(k * T_CYCLE, color="gray", lw=0.7, ls=":", alpha=0.6)
        ax.axvspan(0, T_RAMP, color="orange", alpha=0.15, label="rampa Hann (100ms)")
        ax.axvspan(2 * T_CYCLE, 3 * T_CYCLE, color="green", alpha=0.08, label="ciclo 3 (regime)")

    ax = axes[0, 0]
    ax.plot(t_qi, Q_in_mlmin, color="C0", lw=0.8, label="Q_inlet")
    ax.plot(t_qo, -Q_out_mlmin, color="C1", lw=0.8, ls="--", label="−Q_outlet (saida)")
    ax.axhspan(70, 200, alpha=0.10, color="green")
    ax.set_ylabel("Q [mL/min]")
    ax.set_title("Vazao volumetrica (faixa fisiologica 70-200 mL/min)")
    add_cycle_lines(ax)
    ax.grid(alpha=0.3); ax.legend(loc="best", fontsize=8)

    ax = axes[0, 1]
    ax.plot(t_u, Umax_cm, color="C2", lw=0.8)
    ax.axhspan(10, 20, alpha=0.10, color="green", label="pico fisiologico")
    ax.set_ylabel("|U|_max [cm/s]")
    ax.set_title("Velocidade maxima no fluido")
    add_cycle_lines(ax)
    ax.grid(alpha=0.3); ax.legend(loc="best", fontsize=8)

    ax = axes[1, 0]
    ax.plot(t_d, magD_um, color="C3", lw=0.7)
    ax.set_ylabel("|D| watchpoint [μm]")
    ax.set_title("Deslocamento da parede perto de P_contact")
    add_cycle_lines(ax)
    ax.grid(alpha=0.3); ax.legend(loc="best", fontsize=8)

    ax = axes[1, 1]
    ax.plot(t_s, sigma_kPa, color="C4", lw=1.0, marker="o", ms=2.5)
    ax.set_ylabel("σ_vM max [kPa]")
    ax.set_title("Tensao de von Mises maxima")
    add_cycle_lines(ax)
    ax.grid(alpha=0.3); ax.legend(loc="best", fontsize=8)

    ax = axes[2, 0]
    ax.plot(t_s, eps * 100, color="C5", lw=1.0, marker="s", ms=2.5)
    ax.set_xlabel("t [s]")
    ax.set_ylabel("ε_vM max [%]")
    ax.set_title("Deformacao maxima")
    add_cycle_lines(ax)
    ax.grid(alpha=0.3); ax.legend(loc="best", fontsize=8)

    ax = axes[2, 1]
    # zoom no ciclo 3 — Q and D superpostos
    mask = (t_qi >= 2*T_CYCLE) & (t_qi <= 3*T_CYCLE)
    if mask.any():
        t_local = t_qi[mask] - 2*T_CYCLE
        ax.plot(t_local, Q_in_mlmin[mask], color="C0", lw=1.4, label="Q_inlet")
        ax.set_ylabel("Q [mL/min]", color="C0")
        ax.tick_params(axis="y", labelcolor="C0")
        ax2 = ax.twinx()
        mask_d = (t_d >= 2*T_CYCLE) & (t_d <= 3*T_CYCLE)
        ax2.plot(t_d[mask_d] - 2*T_CYCLE, magD_um[mask_d], color="C3", lw=1.0, label="|D|")
        ax2.set_ylabel("|D| [μm]", color="C3")
        ax2.tick_params(axis="y", labelcolor="C3")
    ax.set_xlabel("t no ciclo (s)")
    ax.set_title("Zoom: ciclo 3 (regime)")
    ax.grid(alpha=0.3)

    fig.suptitle(
        "FSI ao-mestrado v2 — 3 ciclos OMVS, rampa total 100ms, outlet shift 5ms",
        fontsize=12, fontweight="bold",
    )
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(OUT, dpi=150)
    print(f"Saved: {OUT}")

    # Sumario do ciclo 3
    mask_qi3 = (t_qi >= 2*T_CYCLE) & (t_qi <= 3*T_CYCLE)
    mask_u3 = (t_u >= 2*T_CYCLE) & (t_u <= 3*T_CYCLE)
    mask_d3 = (t_d >= 2*T_CYCLE) & (t_d <= 3*T_CYCLE)
    mask_s3 = (t_s >= 2*T_CYCLE) & (t_s <= 3*T_CYCLE)

    print("\n=== CICLO 3 (regime) — t in [{:.2f}, {:.2f}] s ===".format(2*T_CYCLE, 3*T_CYCLE))
    print(f"  Q_in mean  = {Q_in_mlmin[mask_qi3].mean():+.4f} mL/min  (sinal=fluxo entrando se >0 OU sai se <0)")
    print(f"  Q_in peak  = {Q_in_mlmin[mask_qi3].min():+.4f} ... {Q_in_mlmin[mask_qi3].max():+.4f} mL/min")
    print(f"  |U|_max    = {Umax_cm[mask_u3].max():.3f} cm/s (pico no ciclo)")
    print(f"  |U|_mean   = {Umax_cm[mask_u3].mean():.3f} cm/s (medio do max)")
    print(f"  |D|_max    = {magD_um[mask_d3].max():.2f} μm")
    print(f"  |D|_min    = {magD_um[mask_d3].min():.2f} μm")
    print(f"  ΔD pulsatil= {magD_um[mask_d3].max() - magD_um[mask_d3].min():.2f} μm pico-a-pico")
    print(f"  σ_vM max   = {sigma_kPa[mask_s3].max():.1f} kPa")
    print(f"  ε_vM max   = {eps[mask_s3].max()*100:.2f} %")

    # Comparacao: ciclo 1 vs ciclo 3 (deriva?)
    print("\n=== Comparacao ciclo 1 vs ciclo 3 (deriva?) ===")
    for cycle, t0, t1 in [(1, 0.0, T_CYCLE), (3, 2*T_CYCLE, 3*T_CYCLE)]:
        m_d = (t_d >= t0) & (t_d <= t1)
        m_s = (t_s >= t0) & (t_s <= t1)
        print(f"  ciclo {cycle}: |D|_max={magD_um[m_d].max():.2f} μm  σ_max={sigma_kPa[m_s].max():.1f} kPa  ε_max={eps[m_s].max()*100:.2f}%")


if __name__ == "__main__":
    main()
