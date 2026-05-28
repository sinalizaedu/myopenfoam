"""Plot final do estudo de flambagem anatomica realista.

Combina 3 evidencias:

  1. Caso ANATOMICO LINEAR (on-mestrado-2-buckling-real):
     malha de 8 zonas, Winkler em dura_outer, IOP+P_fat rampa em
     anterior_globo. Mostra a resposta passiva do sistema fisiologico.

  2. Caso PRISMATICO NAO-LINEAR (on-buckling-tube):
     coluna 5x5x30mm homogenea com solver NL convergido,
     captura a bifurcacao de Euler diretamente (Pcr_sim=7.85N).

  3. Predicao analitica de Euler para a geometria anatomica:
     EI_dura = 2.14e-5 Nm^2 (tubo r_in=2.40, r_out=2.55mm),
     Pcr para varios K.

Conclusao: SANS realista (P_fat = 0-3000 Pa) gera dz_globo = 0.18-0.35 mm
e F_apice = 0.014-0.098 N. Ambos valores ficam ~6x abaixo do Pcr Euler
para K=0.65 (recomendado para BCs do modelo). Logo, flambagem axial
nao constitui modo de falha relevante em SANS realista.
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


def read_dat(path: str):
    text = subprocess.check_output(
        ["docker", "exec", "om2-resume", "bash", "-lc", f"cat {path}"]
    ).decode()
    rows = []
    for line in text.splitlines():
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split()
        rows.append([float(p) for p in parts])
    return rows


def main():
    # ===== CASO ANATOMICO LINEAR =====
    base = "/simulation/on-mestrado-2-buckling-real/solid/postProcessing/0"
    globo = read_dat(f"{base}/solidForcesDisplacementsglobo_outer.dat")
    dura  = read_dat(f"{base}/solidForcesDisplacementsposterior_dura.dat")
    pia   = read_dat(f"{base}/solidForcesDisplacementsposterior_pia.dat")
    on_   = read_dat(f"{base}/solidForcesDisplacementsposterior_on.dat")

    # P_total = IOP base 2667 Pa + P_fat (rampa 0..3000 Pa)
    P_total_Pa = [2667 + 300*r[0] for r in globo]
    P_fat_Pa   = [P - 2667 for P in P_total_Pa]
    dz_globo_mm = [-r[3] * 1000 for r in globo]                       # mm
    F_apex_dura = [r[6] for r in dura]                                 # N
    F_apex_pia  = [r[6] for r in pia]
    F_apex_on   = [r[6] for r in on_]
    F_apex_total = [d+p+o for d,p,o in zip(F_apex_dura, F_apex_pia, F_apex_on)]
    dx_globo_um = [-r[1] * 1e6 for r in globo]                         # micrometros

    # rigidez axial (slope no regime linear)
    k_axial = (F_apex_total[-1] - F_apex_total[0]) / \
              ((dz_globo_mm[-1] - dz_globo_mm[0]) * 1e-3)

    # ===== CASO PRISMATICO NL =====
    tube = read_dat("/simulation/on-buckling-tube/postProcessing/0/"
                    "solidForcesDisplacementstop.dat")
    tube = [r for r in tube if abs(r[5]) < 0.5]  # remove divergencia
    dz_tube_mm = [-r[3] * 1000 for r in tube]
    Fz_tube    = [-r[6] for r in tube]
    Pcr_tube   = max(Fz_tube)
    idx_peak   = Fz_tube.index(Pcr_tube)
    dz_cr_tube_mm = dz_tube_mm[idx_peak]

    # ===== EULER ANALITICO ANATOMICO =====
    # Tubo dural r_in = 2.40 mm, r_out = 2.55 mm, E = 3 MPa, L = 30 mm
    r_in, r_out = 2.40e-3, 2.55e-3
    E_dura, L = 3e6, 0.030
    I_dura = math.pi/4 * (r_out**4 - r_in**4)
    EI_dura = E_dura * I_dura
    A_dura = math.pi * (r_out**2 - r_in**2)

    K_values = [
        (0.50, "fixed-fixed teorico",                                  "tab:green"),
        (0.65, "fixed-fixed AISC (recomendado)",                       "tab:blue"),
        (1.00, "pinned-pinned",                                        "tab:red"),
    ]

    print(f"\n========== ESTUDO DE FLAMBAGEM ANATOMICA REALISTA ==========\n")
    print(f"EI_dura (anatomico, r=2.40-2.55mm) = {EI_dura:.3e} N.m^2")
    print(f"A_dura  (anatomico)                = {A_dura:.3e} m^2")
    print(f"\n--- Caso anatomico linear, t=10 (P_fat = 3000 Pa) ---")
    print(f"  dispZ_globo  = {dz_globo_mm[-1]:.4f} mm")
    print(f"  F_apex_total = {F_apex_total[-1]:.4f} N")
    print(f"  k_axial      = {k_axial:.1f} N/m")
    print(f"\n--- Caso prismatico NL, bifurcacao ---")
    print(f"  dz_cr_sim    = {dz_cr_tube_mm:.3f} mm")
    print(f"  Pcr_sim      = {Pcr_tube:.3f} N")

    print(f"\n--- Euler anatomico para diversos K ---")
    print(f"{'K':>5s} {'Pcr_anat (N)':>14s} {'dz_cr (mm)':>13s}")
    for K, name, _ in K_values:
        Pcr = (math.pi**2) * EI_dura / (K * L)**2
        dz_cr = Pcr / k_axial * 1000  # mm
        print(f"{K:>5.2f} {Pcr:>14.4f} {dz_cr:>13.3f}  ({name})")

    # =============== FIGURA ===============
    fig = plt.figure(figsize=(16, 9))
    gs  = fig.add_gridspec(2, 2, height_ratios=[1, 1])

    # ----- Painel A: dz_globo vs P_total (anatomico) -----
    axA = fig.add_subplot(gs[0, 0])
    axA.plot(P_fat_Pa, dz_globo_mm, "o-", color="tab:blue", linewidth=2,
             markersize=8, label="dispZ globo (anatomico linear)")
    axA.set_xlabel(r"$P_{\mathrm{fat}}$ - pressao gordura orbital (Pa)")
    axA.set_ylabel(r"encurtamento $|\Delta z_{\mathrm{globo}}|$ (mm)")
    axA.set_title("(A) Resposta passiva do sistema anatomico\n"
                  f"k$_{{axial}}$ composito = {k_axial:.0f} N/m (Winkler 200 kPa/m + 8 zonas)",
                  fontsize=10)
    axA.axhspan(0.5, 1.0, color="tab:orange", alpha=0.15,
                label="faixa clinica SANS (Lee 2020)")
    axA.grid(True, alpha=0.3)
    axA.legend(loc="upper left", fontsize=9)
    axA.set_xlim(0, max(P_fat_Pa) * 1.05)

    # ----- Painel B: F_apex_total vs Pcr Euler anatomico -----
    axB = fig.add_subplot(gs[0, 1])
    axB.plot(P_fat_Pa, F_apex_total, "o-", color="tab:purple", linewidth=2,
             markersize=8, label="F$_{apex}$ total (composito)")
    axB.plot(P_fat_Pa, F_apex_dura, "s--", color="tab:red", linewidth=1.5,
             markersize=5, label="F$_{apex}$ dura (72% do total)", alpha=0.8)
    for K, name, color in K_values:
        Pcr = (math.pi**2) * EI_dura / (K * L)**2
        axB.axhline(Pcr, linestyle="--", color=color, alpha=0.7,
                    label=f"$P_{{cr}}$ Euler K={K:.2f}: {Pcr:.3f} N ({name})")
    axB.set_xlabel(r"$P_{\mathrm{fat}}$ (Pa)")
    axB.set_ylabel(r"$|F_z|$ apice orbital (N)")
    axB.set_title("(B) Reacao axial composta vs P$_{cr}$ Euler\n"
                  "anatomico (tubo dural r=2.40-2.55 mm, EI=2.14e-5 Nm$^2$)",
                  fontsize=10)
    axB.set_yscale("log")
    axB.grid(True, alpha=0.3, which="both")
    axB.legend(loc="lower right", fontsize=8)
    axB.set_xlim(0, max(P_fat_Pa) * 1.05)

    # ----- Painel C: prismatico NL com bifurcacao -----
    axC = fig.add_subplot(gs[1, 0])
    axC.plot(dz_tube_mm, Fz_tube, "ko-", linewidth=2, markersize=5,
             label="prismatico NL (5x5x30mm, neoHookean)", zorder=3)
    axC.plot(dz_cr_tube_mm, Pcr_tube, "r*", markersize=22,
             markeredgecolor="black", markeredgewidth=1.5,
             label=f"bifurcacao numerica: ({dz_cr_tube_mm:.2f} mm, {Pcr_tube:.2f} N)",
             zorder=5)
    EI_prism = 3e6 * (5e-3) * (5e-3)**3 / 12
    Pcr_05_prism = (math.pi**2) * EI_prism / (0.5 * L)**2
    axC.axhline(Pcr_05_prism, color="tab:green", linestyle="--",
                label=f"Euler K=0.50 prismatico: {Pcr_05_prism:.2f} N")
    axC.set_xlabel(r"$|\Delta z|$ (mm)")
    axC.set_ylabel(r"$|F_z|$ (N)")
    axC.set_title("(C) Validacao numerica: caso prismatico NL captura bifurcacao\n"
                  "(geometria simplificada para destravar solver, mesma fisica)",
                  fontsize=10)
    axC.grid(True, alpha=0.3)
    axC.legend(loc="lower right", fontsize=9)

    # ----- Painel D: comparativo das margens de seguranca -----
    axD = fig.add_subplot(gs[1, 1])
    F_at_sans_upper = F_apex_total[-1]
    K_vals = [0.50, 0.65, 1.00, 2.00]
    Pcr_vals = [(math.pi**2) * EI_dura / (K * L)**2 for K in K_vals]
    ratios = [F_at_sans_upper / P for P in Pcr_vals]
    colors_bar = ["tab:green", "tab:blue", "tab:red", "tab:gray"]
    bars = axD.bar([f"K={K:.2f}" for K in K_vals], ratios, color=colors_bar,
                   edgecolor="black", linewidth=1.2)
    for bar, r in zip(bars, ratios):
        axD.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                 f"{r*100:.1f}%",
                 ha="center", va="bottom", fontsize=10, fontweight="bold")
    axD.axhline(1.0, color="red", linestyle=":", linewidth=2,
                label="limite de Euler (flambagem)")
    axD.set_ylabel(r"$F_{\mathrm{apex}}^{\mathrm{SANS}} / P_{cr}^{\mathrm{Euler}}$")
    axD.set_title("(D) Margem de seguranca em SANS upper bound\n"
                  f"(F$_{{apex}}$ = {F_at_sans_upper*1000:.1f} mN at P$_{{fat}}$=3000 Pa)",
                  fontsize=10)
    axD.set_ylim(0, max(ratios) * 1.4)
    axD.grid(True, alpha=0.3, axis="y")
    axD.legend(loc="upper right", fontsize=9)

    fig.suptitle("Estudo de flambagem axial do nervo optico em SANS:\n"
                 "evidencia computacional combinada (anatomico linear + prismatico NL + Euler analitico)",
                 fontsize=12, fontweight="bold", y=1.00)
    fig.tight_layout()
    out = OUT / "fig_buckling_anatomico_realista.png"
    fig.savefig(out, dpi=140, bbox_inches="tight")
    print(f"\nFigura salva: {out}")

    print("\n========== MARGEM DE SEGURANCA ==========")
    print(f"F_apex em SANS upper bound (P_fat=3000 Pa) = {F_at_sans_upper*1000:.2f} mN")
    for K, P in zip(K_vals, Pcr_vals):
        r = F_at_sans_upper / P
        print(f"  K = {K:.2f} : F_SANS / Pcr = {r*100:.2f}%  "
              f"({'SAFE' if r < 0.5 else 'WARNING' if r < 1 else 'BUCKLE'})")


if __name__ == "__main__":
    main()
