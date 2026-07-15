"""
Plot comparativo on-caso-2 (saudavel) vs on-caso-3 (SANS).
Tres paineis:
  1) F_z(Dz) -- curvas axiais sobrepostas (devem ser quase identicas);
  2) P_cr Hetenyi vs modo n -- mostra onde o minimo migra de n=1 para n=2;
  3) Mode-shape qualitativo -- senoide pura para visualizar arco vs duplo lobo.
"""
import math
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).parent.parent / "cases"
OUT = Path(__file__).parent / "on-caso-3_comparison.png"

PATCHES = ["dura", "pia", "on", "sas"]
L = 0.030
E_DURA = 3e6
R_OUTER = 2.50e-3
PERIM = 2 * math.pi * R_OUTER
I_DURA = math.pi / 4 * (R_OUTER**4 - 2.35e-3**4)
EI_DURA = E_DURA * I_DURA

K_W = {"on-caso-2": 2.0e5, "on-caso-3": 2.0e6}
LABELS = {"on-caso-2": "Saudavel (k=200 kPa/m)", "on-caso-3": "SANS (k=2 MPa/m, 10x)"}
COLORS = {"on-caso-2": "#1f77b4", "on-caso-3": "#d62728"}


def read_forces(case_name):
    pp = ROOT / case_name / "solid" / "postProcessing" / "0"
    by_patch = {}
    for p in PATCHES:
        f = pp / f"solidForcesDisplacementsanterior_{p}.dat"
        rows = []
        with open(f) as fh:
            for line in fh:
                if line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) >= 7:
                    rows.append((int(parts[0]), float(parts[3]), float(parts[6])))
        by_patch[p] = rows
    n = len(by_patch["dura"])
    t = np.array([by_patch["dura"][i][0] for i in range(n)])
    dz = np.array([by_patch["dura"][i][1] for i in range(n)])
    F = np.array([sum(by_patch[p][i][2] for p in PATCHES) for i in range(n)])
    return t, dz, F


def hetenyi_curve(k_w, n_max=8):
    k_lineal = k_w * PERIM
    ns = np.arange(1, n_max + 1)
    P = ns**2 * math.pi**2 * EI_DURA / L**2 + k_lineal * L**2 / (ns**2 * math.pi**2)
    return ns, P, int(ns[np.argmin(P)]), float(np.min(P))


def main():
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

    ax = axes[0]
    for case in ["on-caso-2", "on-caso-3"]:
        t, dz, F = read_forces(case)
        ax.plot(np.abs(dz) * 1e3, np.abs(F) * 1e3, "o-", lw=1.8, ms=4,
                color=COLORS[case], label=LABELS[case])
    ax.set_xlabel("|Dz| imposto (mm)")
    ax.set_ylabel("|F_z| reacao total na tampa anterior (mN)")
    ax.set_title("(1) Rigidez axial: curvas sobrepostas\n"
                 "(Winkler atua lateralmente, nao axialmente)")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    n_max = 8
    results = {}
    for case in ["on-caso-2", "on-caso-3"]:
        ns, P, n_star, P_star = hetenyi_curve(K_W[case], n_max)
        results[case] = (ns, P, n_star, P_star)
        ax.plot(ns, P * 1e3, "o-", lw=2, ms=7, color=COLORS[case],
                label=f"{LABELS[case]}\n  min: n={n_star}, P_cr={P_star*1e3:.0f} mN")
        ax.axvline(n_star, color=COLORS[case], ls="--", alpha=0.4)
    ax.set_xlabel("modo n (numero de meias-ondas)")
    ax.set_ylabel("P_cr (mN)")
    ax.set_title("(2) Hetenyi: P_cr(n) = n^2 pi^2 EI/L^2 + k_w L^2/(n^2 pi^2)\n"
                 "modo critico migra de n=1 (arco) para n=2 (focal)")
    ax.set_yscale("log")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(True, alpha=0.3, which="both")

    ax = axes[2]
    z = np.linspace(0, L * 1e3, 200)
    for case in ["on-caso-2", "on-caso-3"]:
        _, _, n_star, _ = results[case]
        y = np.sin(n_star * math.pi * z / (L * 1e3))
        ax.plot(z, y, lw=2.5, color=COLORS[case],
                label=f"{LABELS[case]} - n={n_star}")
    ax.set_xlabel("z ao longo do nervo (mm)")
    ax.set_ylabel("deflexao lateral (qualitativa, unidade arbitraria)")
    ax.set_title("(3) Modo de flambagem previsto (forma de meia-onda)\n"
                 "saudavel: arco suave  |  SANS: dois lobos focais")
    ax.axhline(0, color="k", lw=0.5)
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(True, alpha=0.3)

    fig.suptitle("on-caso-3 (SANS, gordura orbital edemaciada) vs on-caso-2 (saudavel)",
                 fontsize=12, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(OUT, dpi=150)
    print(f"Salvo: {OUT}")


if __name__ == "__main__":
    main()
