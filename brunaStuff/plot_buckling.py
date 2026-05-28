"""Plota a curva F-dz do estudo de flambagem em on-buckling-tube
(coluna prismatica 5mm x 5mm x 30mm, neoHookean, E = 3 MPa, nu = 0.30,
solver nonLinearGeometryUpdatedLagrangian).

Compara a curva NL com as predicoes analiticas de Euler P_cr para
varios fatores de comprimento efetivo K, e marca a bifurcacao
numerica visivel como pico da curva.

A interseccao entre F_z(dz) e P_cr_K indica o shift cefalico critico
previsto pela teoria de Euler para cada hipotese de condicoes de contorno.
"""

from __future__ import annotations

import math
import subprocess
from pathlib import Path

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception as exc:
    raise SystemExit(f"matplotlib indisponivel: {exc}")

OUT = Path(__file__).resolve().parent / "sans_outputs"
OUT.mkdir(exist_ok=True)

DAT = (
    "/simulation/on-buckling-tube/postProcessing/0/"
    "solidForcesDisplacementstop.dat"
)


def read_force_curve():
    text = subprocess.check_output(
        ["docker", "exec", "om2-resume", "bash", "-lc", f"cat {DAT}"]
    ).decode()
    rows = []
    for line in text.splitlines():
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split()
        rows.append({
            "t":   float(parts[0]),
            "dz":  float(parts[3]),
            "Fx":  float(parts[4]),
            "Fy":  float(parts[5]),
            "Fz":  float(parts[6]),
        })
    return rows


def main():
    rows = read_force_curve()

    # Descarta o ultimo ponto se divergiu (Fy gigante)
    rows = [r for r in rows if abs(r["Fy"]) < 0.5]

    dz_mm = [0.0] + [-r["dz"] * 1000 for r in rows]
    Fz_N  = [0.0] + [-r["Fz"]        for r in rows]
    Fy_N  = [0.0] + [r["Fy"]         for r in rows]

    # Identifica o pico = Pcr numerica
    idx_peak = max(range(len(Fz_N)), key=lambda i: Fz_N[i])
    Pcr_sim_N    = Fz_N[idx_peak]
    dz_cr_sim_mm = dz_mm[idx_peak]
    print(f"\n==== BIFURCACAO NUMERICA ====")
    print(f"  dz_cr numerica = {dz_cr_sim_mm:.3f} mm")
    print(f"  P_cr numerica  = {Pcr_sim_N:.3f} N")

    # rigidez axial linear no inicio do ramp (pre-buckling)
    pre_buckle_idx = max(1, idx_peak // 3)
    k_axial = Fz_N[pre_buckle_idx] / (dz_mm[pre_buckle_idx] * 1e-3)
    EA_L_teorico = 3e6 * (5e-3)**2 / 30e-3
    print(f"\n  k_axial (sim, pre-buckle) = {k_axial:.1f} N/m")
    print(f"  k_axial (EA/L)            = {EA_L_teorico:.1f} N/m")

    # Euler P_cr classico: coluna prismatica 5x5 mm, E = 3 MPa, L = 30 mm.
    # I = b * h^3 / 12 = 5e-3 * (5e-3)^3 / 12 = 5.21e-11 m^4
    # EI = 3e6 * 5.21e-11 = 1.56e-4 N.m^2
    EI = 3e6 * (5e-3) * (5e-3)**3 / 12
    L  = 0.030
    print(f"\n  EI = {EI:.3e} N.m^2  (coluna prismatica 5mm x 5mm)")

    K_values = [
        (0.50, "fixed-fixed (rotacao+translacao restritas)", "tab:green"),
        (0.65, "fixed-fixed AISC (com complacencia residual)", "tab:blue"),
        (0.70, "fixed-pinned",                                "tab:orange"),
        (1.00, "pinned-pinned",                               "tab:red"),
        (2.00, "cantilever (fixed-free)",                     "tab:gray"),
    ]

    # ===================== plot principal =====================
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Esquerdo: F_z vs dz
    ax.plot(dz_mm, Fz_N, "ko-", linewidth=2, markersize=6,
            label="simulado (NL Updated Lagrangian, neoHookean)",
            zorder=3)
    ax.plot(dz_cr_sim_mm, Pcr_sim_N, "k*", markersize=20,
            markeredgecolor="red", markeredgewidth=1.5,
            label=f"pico = bifurcacao numerica "
                  f"({dz_cr_sim_mm:.2f} mm, {Pcr_sim_N:.2f} N)",
            zorder=5)

    for K, name, color in K_values:
        Pcr = (math.pi**2) * EI / (K * L)**2
        dz_cr_mm = Pcr / k_axial * 1000
        ax.axhline(Pcr, color=color, linestyle="--", linewidth=1.3, alpha=0.85,
                   label=f"$P_{{cr}}$ Euler K={K:.2f}: {Pcr:.2f} N ({name})")
        if 0 <= dz_cr_mm <= max(dz_mm) * 1.1:
            ax.plot(dz_cr_mm, Pcr, "v", color=color, markersize=10,
                    markeredgecolor="black", markeredgewidth=0.8, zorder=4)

    ax.set_xlabel(r"deslocamento axial $|\Delta z|$ (mm)")
    ax.set_ylabel(r"reacao axial $|F_z|$ (N)")
    ax.set_title("Curva F-dz com bifurcacao numerica de flambagem axial\n"
                 "Coluna prismatica 5mm x 5mm x 30 mm, "
                 "$E = 3$ MPa, $\\nu = 0.30$, neoHookean",
                 fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left", fontsize=8, framealpha=0.92)
    ax.set_xlim(0, max(dz_mm) * 1.05)
    ax.set_ylim(0, max(Fz_N) * 1.20)

    # Direito: reacao lateral F_y (indicador da bifurcacao)
    ax2.semilogy(dz_mm, [abs(f) + 1e-10 for f in Fy_N], "ro-",
                 linewidth=2, markersize=6,
                 label="$|F_y|$ (reacao lateral na imperfeicao)")
    ax2.axvline(dz_cr_sim_mm, color="black", linestyle=":", linewidth=2,
                label=f"bifurcacao em $\\Delta z = {dz_cr_sim_mm:.2f}$ mm")
    ax2.set_xlabel(r"deslocamento axial $|\Delta z|$ (mm)")
    ax2.set_ylabel(r"$|F_y|$ (N) [escala log]")
    ax2.set_title("Crescimento brusco de $F_y$ = assinatura da bifurcacao\n"
                  "Salto de 4 ordens de magnitude em $\\Delta z_{cr}$",
                  fontsize=10)
    ax2.grid(True, alpha=0.3, which="both")
    ax2.legend(loc="lower right", fontsize=10)
    ax2.set_xlim(0, max(dz_mm) * 1.05)

    fig.tight_layout()
    out = OUT / "fig_buckling_NL_F_vs_dz.png"
    fig.savefig(out, dpi=150)
    print(f"\nFigura salva: {out}")

    # =====================  tabela final  =====================
    print(f"\nResumo F vs dz:")
    print(f"{'dz (mm)':>9s} {'F_z (N)':>9s} {'F_y (N)':>11s}  estado")
    for i in range(len(dz_mm)):
        d, f, fy = dz_mm[i], Fz_N[i], Fy_N[i]
        if i == idx_peak:
            state = "<-- PICO (bifurcacao)"
        elif i > idx_peak:
            state = "pos-flambagem"
        else:
            state = ""
        print(f"{d:>9.3f} {f:>9.4f} {fy:>11.4e}  {state}")

    print(f"\n==== COMPARACAO COM EULER ====")
    print(f"{'K':>5s} {'Pcr teorico (N)':>17s} {'dz_cr teorico (mm)':>20s} "
          f"{'razao Pcr_sim/Pcr_teo':>24s}")
    for K, name, _ in K_values:
        Pcr = (math.pi**2) * EI / (K * L)**2
        dz_cr_mm = Pcr / k_axial * 1000
        ratio = Pcr_sim_N / Pcr
        print(f"{K:>5.2f} {Pcr:>17.3f} {dz_cr_mm:>20.3f} {ratio:>24.3f}")

    K_eff = math.sqrt((math.pi**2) * EI / (L**2 * Pcr_sim_N))
    print(f"\n==== K EFETIVO IDENTIFICADO ====")
    print(f"  K_eff = sqrt(pi^2 EI / (L^2 Pcr_sim)) = {K_eff:.4f}")
    print(f"  Compatibilidade: K_eff < 0.5 implica restricao MAIS RIGIDA")
    print(f"  do que o fixed-fixed ideal (consistente com BCs fixedDisplacement")
    print(f"  enforcando translacao + flatness do patch).")


if __name__ == "__main__":
    main()
