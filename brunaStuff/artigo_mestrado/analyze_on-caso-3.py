"""
Analise k_axial e P_cr Euler para on-caso-3 (SANS) e comparacao com
on-caso-2 (saudavel). Le os 4 arquivos solidForcesDisplacements*.dat de
cada caso e calcula:

  * k_axial total e por zona (on/pia/sas/dura) em N/m;
  * P_cr Euler com varios K (boundary conditions);
  * Margem de seguranca @ Dz = 1 mm;
  * Razao k_SANS / k_saudavel (efeito quantitativo da gordura edemaciada).

Caso 3 difere do caso 2 apenas pela rigidez da fundacao de Winkler em
dura_outer (k_SANS = 2.0 MPa/m vs k_healthy = 200 kPa/m, ~10x).
"""
import math
from pathlib import Path

ROOT = Path(__file__).parent.parent / "cases"
PATCHES = ["dura", "pia", "on", "sas"]

L = 0.030  # m
E_DURA = 3e6
R_INNER_DURA = 2.35e-3
R_OUTER_DURA = 2.50e-3

# k_Winkler em Pa/m (forca por area por deflexao). Para flambagem de viga
# sobre fundacao elastica (Hetenyi), precisamos converter para "k lineal"
# em N/m^2 = (forca por comprimento) por deflexao lateral. Para a dura
# cilindrica imersa na gordura: k_lineal = k_w_winkler * perimetro
# (assumindo contato uniforme em toda a circunferencia da dura externa).
PERIM_DURA = 2.0 * math.pi * R_OUTER_DURA  # m

K_WINKLER = {
    "on-caso-2": 200_000.0,    # saudavel: 200 kPa/m
    "on-caso-3": 2_000_000.0,  # SANS: 2 MPa/m (10x)
}


def read_forces(case_dir, patch):
    f = case_dir / f"solidForcesDisplacements{('anterior_' + patch)}.dat"
    rows = []
    with open(f) as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 7:
                rows.append((int(parts[0]), float(parts[3]), float(parts[6])))
    return rows


def summarize(case_name, k_winkler_label):
    case_dir = ROOT / case_name / "solid" / "postProcessing" / "0"
    if not case_dir.exists():
        print(f"[skip] {case_name}: nao rodado ainda ({case_dir} inexistente).")
        return None

    last_step = {}
    for p in PATCHES:
        try:
            rows = read_forces(case_dir, p)
        except FileNotFoundError as e:
            print(f"[skip] {case_name}: arquivo ausente {e.filename}")
            return None
        last_step[p] = rows[-1]

    Dz = last_step["dura"][1]
    F_total = sum(last_step[p][2] for p in PATCHES)

    k_axial = F_total / Dz
    I_dura = math.pi / 4 * (R_OUTER_DURA**4 - R_INNER_DURA**4)
    EI_dura = E_DURA * I_dura

    print("=" * 72)
    print(f"{case_name}  --  k_Winkler = {k_winkler_label}")
    print("=" * 72)
    print(f"  Dz imposto: {Dz*1e3:.3f} mm   (anterior, 4 zonas)")
    print(f"  Reacao axial composta no apice (Time=40):")
    for p in PATCHES:
        dz = last_step[p][1]
        fz = last_step[p][2]
        ki = fz / dz
        pct = abs(fz / F_total) * 100
        print(f"    anterior_{p:<5s}: F_z = {fz*1e3:8.3f} mN   k_i = {ki:7.2f} N/m   ({pct:5.1f}%)")
    print(f"    ---------------------------------------------------")
    print(f"    TOTAL          : F_z = {F_total*1e3:8.3f} mN   k   = {k_axial:7.2f} N/m")

    print(f"\n  Carga critica Euler P_cr(K) = pi^2 EI_dura / (KL)^2:")
    print(f"  {'K':<6}{'BC':<32}{'P_cr (mN)':>12}{'F_z/P_cr':>12}")
    print(f"  {'-'*6}{'-'*32}{'-'*12}{'-'*12}")
    for K, label in [
        (0.5, "fixed-fixed teorico"),
        (0.65, "fixed-fixed AISC"),
        (0.70, "fixed-pinned"),
        (1.0, "pinned-pinned"),
        (2.0, "fixed-free (cantilever)"),
    ]:
        Pcr = math.pi**2 * EI_dura / (K * L) ** 2
        ratio = abs(F_total) / Pcr
        print(f"  {K:<6}{label:<32}{Pcr*1e3:>9.2f}    {ratio*100:>9.1f} %")

    Pcr_AISC = math.pi**2 * EI_dura / (0.65 * L) ** 2
    safety = Pcr_AISC / abs(F_total)
    print(f"\n  Margem de seguranca @ Dz=1mm, K=0.65 (AISC): {safety:.2f} x")

    # Hetenyi: viga comprimida sobre fundacao elastica continua.
    #   P_cr(n) = n^2 pi^2 EI / L^2  +  k_lineal L^2 / (n^2 pi^2)
    # Minimizado em n* = (k_lineal L^4 / (EI pi^4))^(1/4); para o continuo
    # o minimo absoluto vale 2*sqrt(EI*k_lineal) (sem dependencia de L).
    # Como n deve ser inteiro (modo de meia-onda), avaliamos n=1..10 e
    # tomamos o menor P_cr.
    k_w = K_WINKLER.get(case_name)
    print(f"\n  Hetenyi (viga sobre fundacao elastica, k_w={k_w/1e3:.0f} kPa/m):")
    if k_w is not None:
        k_lineal = k_w * PERIM_DURA  # N/m^2 (forca por comprimento por defl)
        n_star_cont = (k_lineal * L**4 / (EI_dura * math.pi**4)) ** 0.25
        Pcr_inf = 2.0 * math.sqrt(EI_dura * k_lineal)
        print(f"    k_lineal = k_w * perim_dura = {k_lineal:.2f} N/m^2")
        print(f"    n* continuo = {n_star_cont:.2f}   (numero de meias-ondas otimo, sem quantizar)")
        print(f"    P_cr (continuo, infinito) = 2 sqrt(EI*k_lineal) = {Pcr_inf*1e3:.1f} mN")
        print(f"    {'n':<4}{'wavelength L/n (mm)':<24}{'P_cr (mN)':<14}{'F_z/P_cr':<10}")
        print(f"    {'-'*4}{'-'*24}{'-'*14}{'-'*10}")
        best_n, best_Pcr = 1, float("inf")
        for n in range(1, 11):
            Pcr_n = n**2 * math.pi**2 * EI_dura / L**2 + k_lineal * L**2 / (n**2 * math.pi**2)
            ratio = abs(F_total) / Pcr_n
            marker = ""
            if Pcr_n < best_Pcr:
                best_n, best_Pcr = n, Pcr_n
            print(f"    {n:<4}{L/n*1e3:<24.2f}{Pcr_n*1e3:<14.2f}{ratio*100:.1f} %")
        print(f"    => modo critico: n={best_n} (lambda = {L/best_n*1e3:.2f} mm), P_cr = {best_Pcr*1e3:.1f} mN")
        Pcr_hetenyi = best_Pcr
    else:
        Pcr_hetenyi = Pcr_AISC

    return {
        "case": case_name,
        "Dz": Dz,
        "F_total": F_total,
        "k_axial": k_axial,
        "k_per_patch": {p: last_step[p][2] / last_step[p][1] for p in PATCHES},
        "Pcr_AISC": Pcr_AISC,
        "Pcr_hetenyi": Pcr_hetenyi,
        "n_hetenyi": best_n if k_w is not None else None,
        "safety": safety,
    }


def compare(saud, sans):
    if saud is None or sans is None:
        print("\n[skip] comparacao: um dos casos nao rodou.")
        return

    print("=" * 72)
    print("COMPARACAO on-caso-3 (SANS, k=2.0 MPa/m) vs on-caso-2 (saudavel, 200 kPa/m)")
    print("=" * 72)
    ratio_k = sans["k_axial"] / saud["k_axial"]
    ratio_F = sans["F_total"] / saud["F_total"]
    print(f"  k_axial:  saudavel = {saud['k_axial']:.2f} N/m")
    print(f"            SANS     = {sans['k_axial']:.2f} N/m")
    print(f"            razao    = {ratio_k:.3f} x")
    print(f"  F_z@Dz=1mm: saudavel = {abs(saud['F_total'])*1e3:.2f} mN")
    print(f"              SANS     = {abs(sans['F_total'])*1e3:.2f} mN")
    print(f"              razao    = {ratio_F:.3f} x")
    print(f"  Margem AISC: saudavel = {saud['safety']:.2f} x")
    print(f"               SANS     = {sans['safety']:.2f} x")

    print("\n  Por zona (k_i = F_i/Dz, em N/m):")
    print(f"  {'zona':<8}{'saudavel':>12}{'SANS':>12}{'razao':>12}")
    print(f"  {'-'*8}{'-'*12}{'-'*12}{'-'*12}")
    for p in PATCHES:
        ks = saud["k_per_patch"][p]
        kn = sans["k_per_patch"][p]
        r = kn / ks if ks != 0 else float("nan")
        print(f"  {p:<8}{ks:>12.2f}{kn:>12.2f}{r:>12.3f}")

    print("\nHetenyi (viga sobre fundacao elastica - efeito da gordura SANS):")
    ratio_Pcr = sans["Pcr_hetenyi"] / saud["Pcr_hetenyi"]
    print(f"  P_cr: saudavel = {saud['Pcr_hetenyi']*1e3:.1f} mN  (modo critico n={saud['n_hetenyi']}, lambda={L/saud['n_hetenyi']*1e3:.1f} mm)")
    print(f"        SANS     = {sans['Pcr_hetenyi']*1e3:.1f} mN  (modo critico n={sans['n_hetenyi']}, lambda={L/sans['n_hetenyi']*1e3:.1f} mm)")
    print(f"        razao    = {ratio_Pcr:.2f} x")
    print(f"  F_z/P_cr (saudavel) = {abs(saud['F_total'])/saud['Pcr_hetenyi']*100:.1f} %")
    print(f"  F_z/P_cr (SANS)     = {abs(sans['F_total'])/sans['Pcr_hetenyi']*100:.1f} %")

    print("\nInterpretacao:")
    print(f"  * Rigidez axial total: praticamente identica ({(ratio_k-1)*100:+.2f}%).")
    print(f"    Esperado: o Winkler resiste a deflexao LATERAL, nao a compressao axial.")
    print(f"  * Carga critica P_cr (Hetenyi): aumenta {ratio_Pcr:.1f}x na SANS.")
    print(f"    Isto se traduz em maior margem de seguranca contra flambagem global,")
    print(f"    MAS o modo selecionado muda de n={saud['n_hetenyi']} para n={sans['n_hetenyi']}:")
    if sans['n_hetenyi'] > saud['n_hetenyi']:
        print(f"    - saudavel: arco suave em lambda={L/saud['n_hetenyi']*1e3:.0f} mm (deslocamento difuso);")
        print(f"    - SANS:     ondulacao mais focal em lambda={L/sans['n_hetenyi']*1e3:.0f} mm")
        print(f"                ({sans['n_hetenyi']} meios-comprimentos de onda ao longo do nervo).")
        print(f"    Isto e exatamente o padrao clinico SANS: tortuosidade mais focal e")
        print(f"    severa - 'pontos de estrangulamento' em vez de um arco suave.")
    else:
        print(f"    - mesmo modo: ambos com n={saud['n_hetenyi']}.")
        print(f"    - SANS so 'endurece' o sistema; nao muda o padrao da dobra.")
        print(f"    Para mudar de modo seria preciso aumentar k ainda mais (rigidez 100x).")


if __name__ == "__main__":
    saud = summarize("on-caso-2", "200 kPa/m (saudavel)")
    print()
    sans = summarize("on-caso-3", "2.0 MPa/m (SANS, 10x)")
    print()
    compare(saud, sans)
