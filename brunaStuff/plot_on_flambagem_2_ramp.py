"""
plot_on_flambagem_2_ramp.py

Plots the response of on-flambagem-2 to the imposed displacement ramp
(D_z = 0 -> -1 mm in 20 steps) using linearGeometryTotalDisplacement.

Output:  brunaStuff/on_flambagem_2_ramp.png

Reads each timestep from cases/on-flambagem-2/solid/<n>/ and extracts:
  - Max |D| (mm)                      -> structural response magnitude
  - Max sigmaEq (kPa)                 -> peak von Mises stress
  - D_z at axial centerline (mm)      -> axial shortening profile
  - Lateral deflection |D_xy| at z=L/2 -> potential buckling signature
"""

from __future__ import annotations
import re
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "cases" / "on-flambagem-2" / "solid"
OUT = ROOT / "brunaStuff" / "on_flambagem_2_ramp.png"

NUM_RE = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")


def read_scalar_field(path: Path) -> np.ndarray:
    body = path.read_text()
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n?\s*(\d+)\s*\(", body)
    if not m:
        raise RuntimeError(f"could not parse scalar field {path}")
    n = int(m.group(1))
    start = m.end()
    end = body.index(")", start)
    nums = NUM_RE.findall(body[start:end])
    return np.array(nums[:n], dtype=float)


def read_vector_field(path: Path) -> np.ndarray:
    body = path.read_text()
    m = re.search(r"internalField\s+nonuniform\s+List<vector>\s*\n?\s*(\d+)\s*\(", body)
    if not m:
        raise RuntimeError(f"could not parse vector field {path}")
    n = int(m.group(1))
    start = m.end()
    end = body.index("\n)", start)
    chunk = body[start:end]
    tuples = re.findall(r"\(\s*([^)]+)\)", chunk)
    arr = np.array([[float(x) for x in NUM_RE.findall(t)[:3]] for t in tuples[:n]])
    return arr


def main() -> None:
    Cx = read_scalar_field(CASE / "0" / "Cx")
    Cy = read_scalar_field(CASE / "0" / "Cy")
    Cz = read_scalar_field(CASE / "0" / "Cz")

    times = sorted(
        [int(p.name) for p in CASE.iterdir() if p.is_dir() and p.name.isdigit() and int(p.name) > 0]
    )

    imposed_dz_mm = np.array([-0.05 * t for t in times])
    max_D = np.zeros(len(times))
    max_sigma_kPa = np.zeros(len(times))
    max_eps = np.zeros(len(times))
    max_lateral_mm = np.zeros(len(times))

    for i, t in enumerate(times):
        td = CASE / str(t)
        D = read_vector_field(td / "D")  # m
        sig = read_scalar_field(td / "sigmaEq")  # Pa
        eps = read_scalar_field(td / "epsilonEq")  # -
        max_D[i] = np.max(np.linalg.norm(D, axis=1)) * 1000.0
        max_sigma_kPa[i] = sig.max() / 1e3
        max_eps[i] = eps.max()
        max_lateral_mm[i] = np.max(np.sqrt(D[:, 0] ** 2 + D[:, 1] ** 2)) * 1000.0

    fig, axes = plt.subplots(2, 2, figsize=(11, 8.5))
    fig.suptitle(
        "on-flambagem-2 - Resposta a rampa de deslocamento imposto (linearGeometry)\n"
        "anterior_{on,pia,sas,dura} = D_z(t) rampando 0 -> -1 mm em 20 steps",
        fontsize=11,
    )

    ax = axes[0, 0]
    ax.plot(-imposed_dz_mm, max_sigma_kPa, "o-", color="C3", lw=2, ms=5)
    ax.set_xlabel("|D_z imposto| na tampa anterior (mm)")
    ax.set_ylabel("Max sigma_VM no dominio (kPa)")
    ax.set_title("Tensao max vs encurtamento imposto (linear? = sim)")
    ax.grid(alpha=0.3)
    # slope (kPa/mm) - se linear
    slope = np.polyfit(-imposed_dz_mm, max_sigma_kPa, 1)[0]
    ax.text(
        0.05, 0.95,
        f"slope = {slope:.1f} kPa/mm\n(linear: stress prop. a deslocamento)",
        transform=ax.transAxes, va="top", fontsize=9,
        bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8),
    )

    ax = axes[0, 1]
    ax.plot(times, max_D, "s-", color="C0", lw=2, ms=5, label="|D|_max")
    ax.plot(times, max_lateral_mm, "^-", color="C2", lw=2, ms=5, label="|D_xy|_max (lateral)")
    ax.plot(times, -imposed_dz_mm, "k--", lw=1.5, label="|D_z imposto|")
    ax.set_xlabel("Pseudo-tempo (s)")
    ax.set_ylabel("Deslocamento (mm)")
    ax.set_title("Componentes maximas de D")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(alpha=0.3)

    ax = axes[1, 0]
    ax.plot(-imposed_dz_mm, max_eps * 100, "d-", color="C4", lw=2, ms=5)
    ax.set_xlabel("|D_z imposto| na tampa anterior (mm)")
    ax.set_ylabel("Max epsilon_eq (%)")
    ax.set_title("Strain max vs encurtamento imposto")
    ax.grid(alpha=0.3)
    ax.text(
        0.95, 0.05,
        ("epsilon ~ 5%% constante - na realidade vem do desencontro entre\n"
         "as faces anteriores impostas e o material macio SAS (que tem que\n"
         "absorver a discontinuidade). Eh um artefato da BC simplificada,\n"
         "nao deformacao real do tubo."),
        transform=ax.transAxes, va="bottom", ha="right", fontsize=8,
        bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8),
    )

    # Axial profile of D_z at last timestep
    ax = axes[1, 1]
    D_final = read_vector_field(CASE / str(times[-1]) / "D") * 1000.0  # mm
    z_bins = np.linspace(0.0, 30.0, 31)
    z_centers = 0.5 * (z_bins[:-1] + z_bins[1:])
    Dz_mean = np.zeros_like(z_centers)
    for k in range(len(z_centers)):
        mask = (Cz * 1000.0 >= z_bins[k]) & (Cz * 1000.0 < z_bins[k + 1])
        if mask.any():
            Dz_mean[k] = np.mean(D_final[mask, 2])
    ax.plot(z_centers, Dz_mean, "o-", lw=2, ms=4, color="C5")
    ax.axhline(0.0, color="gray", lw=0.7)
    ax.axhline(-1.0, color="red", lw=0.7, ls=":", label="D_z imposto na tampa (z=30)")
    ax.set_xlabel("z (mm) - posicao axial")
    ax.set_ylabel("D_z medio (mm)")
    ax.set_title(f"Perfil axial de D_z no ultimo step (t={times[-1]})")
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(OUT, dpi=140)
    print(f"saved {OUT}")
    print()
    print("Resumo da rampa:")
    print(f"  D_z imposto final: -1.000 mm")
    print(f"  |D|_max final:    {max_D[-1]:.3f} mm")
    print(f"  |D_xy|_max final: {max_lateral_mm[-1]:.3f} mm (deflexao lateral)")
    print(f"  sigma_VM_max:     {max_sigma_kPa[-1]:.1f} kPa")
    print(f"  epsilon_max:      {max_eps[-1]*100:.1f}%")
    print(f"  slope sigma/disp: {slope:.1f} kPa/mm")


if __name__ == "__main__":
    main()
