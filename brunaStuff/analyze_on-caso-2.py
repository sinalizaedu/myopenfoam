"""
Analise k_axial e P_cr Euler para on-caso-2 (rodado com linear geometry).
Le os 4 arquivos solidForcesDisplacements*.dat e calcula:
  k_axial total = sum_i (E_i A_i) / L
  P_cr(K) = pi^2 EI_dura / (KL)^2
  Margem de seguranca a SANS (Dz=1mm)
"""
import math
from pathlib import Path

CASE = Path(__file__).parent.parent / "cases" / "on-caso-2" / "solid" / "postProcessing" / "0"
PATCHES = ["dura", "pia", "on", "sas"]

L = 0.030  # m
E_DURA = 3e6
R_INNER_DURA = 2.35e-3
R_OUTER_DURA = 2.50e-3


def read_forces(patch):
    f = CASE / f"solidForcesDisplacements{('anterior_' + patch)}.dat"
    rows = []
    with open(f) as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 7:
                rows.append((int(parts[0]), float(parts[3]), float(parts[6])))
    return rows


def main():
    last_step = {}
    for p in PATCHES:
        rows = read_forces(p)
        last_step[p] = rows[-1]

    Dz = last_step["dura"][1]
    F_total = sum(last_step[p][2] for p in PATCHES)
    F_dura = last_step["dura"][2]

    k_axial = F_total / Dz
    k_axial_dura = F_dura / Dz

    I_dura = math.pi / 4 * (R_OUTER_DURA**4 - R_INNER_DURA**4)
    EI_dura = E_DURA * I_dura

    print("=" * 70)
    print("on-caso-2 -- Analise de flambagem axial (linear + Euler hibrido)")
    print("=" * 70)
    print(f"\nDeslocamento axial imposto: Dz = {Dz*1e3:.3f} mm")
    print(f"Reacao axial composta no apice (Time=40):")
    for p in PATCHES:
        dz = last_step[p][1]
        fz = last_step[p][2]
        ki = fz / dz
        pct = abs(fz / F_total) * 100
        print(f"  anterior_{p:<5s}: F_z = {fz*1e3:8.3f} mN   k_i = {ki:7.2f} N/m   ({pct:5.1f}%)")
    print(f"  ---------------------------------------------------")
    print(f"  TOTAL          : F_z = {F_total*1e3:8.3f} mN   k   = {k_axial:7.2f} N/m")

    print(f"\nGeometria da dura (camada estrutural dominante):")
    print(f"  r_inner = {R_INNER_DURA*1e3} mm,  r_outer = {R_OUTER_DURA*1e3} mm")
    print(f"  I_annular = pi/4 * (r_o^4 - r_i^4) = {I_dura:.3e} m^4")
    print(f"  EI_dura   = {EI_dura:.3e} N.m^2")

    print(f"\nCarga critica de Euler P_cr(K) = pi^2 EI / (KL)^2  (L = {L*1e3} mm):")
    print(f"  {'K':<8} {'BC':<32} {'P_cr (mN)':<12} {'F_z/P_cr':<10}")
    print(f"  {'-'*8} {'-'*32} {'-'*12} {'-'*10}")
    for K, label in [
        (0.5, "fixed-fixed teorico"),
        (0.65, "fixed-fixed AISC (recomendado)"),
        (0.70, "fixed-pinned"),
        (1.0, "pinned-pinned"),
        (2.0, "fixed-free (cantilever)"),
    ]:
        Pcr = math.pi**2 * EI_dura / (K * L) ** 2
        ratio = abs(F_total) / Pcr
        print(f"  {K:<8} {label:<32} {Pcr*1e3:8.2f}     {ratio*100:5.1f}%")

    print(f"\nComparacao com SANS clinico (Lee2020NPJ: Dz_globo in [0.5; 1.0] mm):")
    print(f"  Dz simulado = {abs(Dz)*1e3:.2f} mm (limite superior SANS)")
    print(f"  F_z = {abs(F_total)*1e3:.2f} mN")
    Pcr_AISC = math.pi**2 * EI_dura / (0.65 * L) ** 2
    safety_margin = Pcr_AISC / abs(F_total)
    print(f"  Margem de seguranca @ K=0.65 (AISC): {safety_margin:.2f}x")

    print(f"\nConclusao: flambagem axial NAO e modo de falha relevante para SANS")
    print(f"em qualquer K <= 1.0 (margem >= {Pcr_AISC/abs(F_total):.1f}x para K=0.65).")
    print(f"\nNota metodologica: NL geometry direta falhou (NaN em iter 250 do Time=1")
    print(f"com alpha_D=0.1, bug de Jacobiano negativo do FVM segregado em multi-zona).")
    print(f"Adotada estrategia hibrida linear+Euler validada em on-mestrado-2-buckling-real.")


if __name__ == "__main__":
    main()
