#!/usr/bin/env python3
"""
analyze_on-caso-3_ccx.py
========================
Analise + comparacao direta:
  on-caso-2/ccx (saudavel, k_winkler = 200 kPa/m)  vs
  on-caso-3/ccx (SANS,     k_winkler = 2.0 MPa/m, 10x)

Ambas as simulacoes sao CalculiX 2.20 NLGEOM com Neo-Hooke. A unica
diferenca fisica e a rigidez da fundacao de Winkler em dura_outer.

Le os arquivos .dat de cada caso, extrai a curva F_z(Dz) do STEP 2, e
produz:
  - brunaStuff/on-caso-3_ccx_summary.txt   (numeros + Hetenyi cross-check)
  - brunaStuff/on-caso-3_ccx_comparison.png (3 paineis sobrepostos)

Para visualizar o modo de flambagem (n=1 saudavel vs n=2 SANS):
  cgx -c cases/on-caso-3/ccx/on-caso-3.frd
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "brunaStuff"
PNG = OUT_DIR / "on-caso-3_ccx_comparison.png"
SUMMARY = OUT_DIR / "on-caso-3_ccx_summary.txt"

NSETS = ["ANTERIOR_DURA", "ANTERIOR_PIA", "ANTERIOR_SAS", "ANTERIOR_ON"]

# Parametros geometricos (= on-caso-X.inp)
L = 0.030            # m
E_DURA = 3e6
R_INNER_DURA = 2.35e-3
R_OUTER_DURA = 2.50e-3
DZ_MAX = -1.0e-3     # m, rampa imposta no STEP 2

CASES = {
    "on-caso-2": {
        "label": "Saudavel (k=200 kPa/m)",
        "color": "#1f77b4",
        "k_winkler": 2.0e5,
        "dat": REPO / "cases" / "on-caso-2" / "ccx" / "on-caso-2.dat",
    },
    "on-caso-3": {
        "label": "SANS (k=2 MPa/m, 10x)",
        "color": "#d62728",
        "k_winkler": 2.0e6,
        "dat": REPO / "cases" / "on-caso-3" / "ccx" / "on-caso-3.dat",
    },
}


def parse_ccx_dat(path: Path) -> dict[str, list[tuple[float, float, float, float]]]:
    """Parse CalculiX .dat (*NODE PRINT TOTALS=ONLY RF blocks).

    Bloco:
        total force (fx,fy,fz) for set NAME and time  0.2500000E+00
            -1.234E-05    -3.456E-09    -6.789E-03
    """
    data: dict[str, list] = {n: [] for n in NSETS}
    if not path.exists():
        return data
    text = path.read_text()
    pattern = re.compile(
        r"total\s+force.*?for\s+set\s+(\w+)\s+and\s+time\s+([\-+\d\.E]+)"
        r"\s+([\-+\d\.E]+)\s+([\-+\d\.E]+)\s+([\-+\d\.E]+)",
        re.IGNORECASE | re.DOTALL,
    )
    for m in pattern.finditer(text):
        nset, t, fx, fy, fz = m.groups()
        if nset.upper() in data:
            data[nset.upper()].append(
                (float(t), float(fx), float(fy), float(fz))
            )
    return data


def extract_step2(dat: dict[str, list]) -> dict[str, np.ndarray]:
    """Filtra STEP 2 (t > 1) e retorna numpy arrays por NSET."""
    out: dict[str, np.ndarray] = {}
    for n, rows in dat.items():
        if not rows:
            out[n] = np.zeros((0, 4))
            continue
        arr = np.array(rows)
        mask = arr[:, 0] > 1.0 + 1e-9
        out[n] = arr[mask]
    return out


def compute_case(case_name: str) -> dict | None:
    cfg = CASES[case_name]
    raw = parse_ccx_dat(cfg["dat"])
    if not raw["ANTERIOR_DURA"]:
        return None
    step2 = extract_step2(raw)
    if step2["ANTERIOR_DURA"].size == 0:
        return None

    times = step2["ANTERIOR_DURA"][:, 0]
    Dz = DZ_MAX * (times - 1.0)
    Fz_dura = step2["ANTERIOR_DURA"][:, 3]
    Fz_pia = step2["ANTERIOR_PIA"][:, 3]
    Fz_sas = step2["ANTERIOR_SAS"][:, 3]
    Fz_on = step2["ANTERIOR_ON"][:, 3]
    Fz_total = Fz_dura + Fz_pia + Fz_sas + Fz_on

    Fx_total = sum(step2[n][:, 1] for n in NSETS)
    Fy_total = sum(step2[n][:, 2] for n in NSETS)
    Flat = np.hypot(Fx_total, Fy_total)

    idx_peak = int(np.argmax(np.abs(Fz_total)))
    Dz_cr = Dz[idx_peak]
    P_cr_sim = abs(Fz_total[idx_peak])

    # Bifurcacao real: o pico aparece NO MEIO da rampa (nao no fim) e |F_lat|
    # da um salto. Se idx_peak == len-1 e |F_lat| ~ 0, NAO houve bifurcacao
    # e o "P_cr_sim" e apenas a forca no fim da rampa (limite inferior).
    bifurcated = (idx_peak < len(Dz) - 1) or (Flat[-1] > 1e-9)

    # k axial pre-buckling: regressao na regiao linear (primeiros pontos).
    # Para case-2 (4 pontos: -0.25,-0.5,-0.75,-1.0 mm) usamos os 2 primeiros.
    # Para case-3 (22 pontos com Dz fino) usamos os 5 primeiros (~Dz ate 0.25 mm).
    pre_idx = min(5, len(Dz)) if len(Dz) > 5 else min(2, len(Dz))
    k_axial = float("nan")
    if pre_idx >= 2:
        slope = np.polyfit(Dz[:pre_idx], Fz_total[:pre_idx], 1)[0]
        k_axial = abs(slope)

    return dict(
        case=case_name,
        label=cfg["label"],
        color=cfg["color"],
        k_winkler=cfg["k_winkler"],
        times=times,
        Dz=Dz,
        Fz_total=Fz_total,
        Fz_dura=Fz_dura,
        Fz_pia=Fz_pia,
        Fz_sas=Fz_sas,
        Fz_on=Fz_on,
        Flat=Flat,
        idx_peak=idx_peak,
        Dz_cr=Dz_cr,
        P_cr=P_cr_sim,
        k_axial=k_axial,
        bifurcated=bifurcated,
    )


def hetenyi_predict(k_winkler: float) -> tuple[int, float]:
    """Retorna (n*, P_cr*) usando viga sobre fundacao elastica com fundacao
    transferida da pressao radial (k_w em Pa/m) para densidade lineal:
        k_lineal = k_w * perimetro_dura_outer
    e P_cr(n) = n^2 pi^2 EI/L^2 + k_lineal L^2 / (n^2 pi^2).
    """
    perim = 2 * math.pi * R_OUTER_DURA
    k_lin = k_winkler * perim
    I = math.pi / 4 * (R_OUTER_DURA**4 - R_INNER_DURA**4)
    EI = E_DURA * I
    best_n, best_P = 1, float("inf")
    for n in range(1, 11):
        P = n**2 * math.pi**2 * EI / L**2 + k_lin * L**2 / (n**2 * math.pi**2)
        if P < best_P:
            best_n, best_P = n, P
    return best_n, best_P


def write_summary(saud: dict, sans: dict) -> str:
    lines: list[str] = []
    p = lines.append
    p("=" * 76)
    p("on-caso-3 CCX (SANS, k=2 MPa/m) vs on-caso-2 CCX (saudavel, k=200 kPa/m)")
    p("=" * 76)
    p("\nCalculiX 2.20 NLGEOM + NeoHooke. Mesma malha, mesmos materiais, mesma")
    p("cinematica. UNICA diferenca fisica: rigidez da fundacao de Winkler.\n")

    for case in (saud, sans):
        p("-" * 76)
        p(f"{case['case']}  --  {case['label']}")
        p("-" * 76)
        p(f"  Incrementos STEP 2 lidos     : {len(case['Dz'])}")
        p(f"  Range Dz                     : {case['Dz'].min()*1e3:+.3f} a {case['Dz'].max()*1e3:+.3f} mm")
        p(f"  Rigidez axial pre-flambagem  : {case['k_axial']:7.2f} N/m")
        if case["bifurcated"]:
            p(f"  PICO (= P_cr NLGEOM)         : {case['P_cr']*1e3:7.2f} mN  @ Dz={case['Dz_cr']*1e3:+.3f} mm  [BIFURCOU]")
        else:
            p(f"  PICO (= F_z no fim da rampa) : {case['P_cr']*1e3:7.2f} mN  @ Dz={case['Dz_cr']*1e3:+.3f} mm  [NAO bifurcou]")
            p(f"     => F_z monotono crescente, |F_lat|~0: P_cr_real > {case['P_cr']*1e3:.0f} mN")
        p(f"  Final (|Dz|={abs(case['Dz'][-1])*1e3:.3f} mm):")
        p(f"     F_z_total = {abs(case['Fz_total'][-1])*1e3:7.2f} mN")
        p(f"        dura = {abs(case['Fz_dura'][-1])*1e3:7.2f} mN ({abs(case['Fz_dura'][-1]/case['Fz_total'][-1])*100:5.1f}%)")
        p(f"        pia  = {abs(case['Fz_pia'][-1])*1e3:7.2f} mN ({abs(case['Fz_pia'][-1]/case['Fz_total'][-1])*100:5.1f}%)")
        p(f"        sas  = {abs(case['Fz_sas'][-1])*1e3:7.2f} mN ({abs(case['Fz_sas'][-1]/case['Fz_total'][-1])*100:5.1f}%)")
        p(f"        on   = {abs(case['Fz_on'][-1])*1e3:7.2f} mN ({abs(case['Fz_on'][-1]/case['Fz_total'][-1])*100:5.1f}%)")
        p(f"     |F_lat|   = {case['Flat'][-1]*1e3:7.3f} mN  (sinal de bifurcacao lateral)")
        n_het, P_het = hetenyi_predict(case["k_winkler"])
        p(f"  Hetenyi (analitico, viga sobre fundacao elastica):")
        p(f"     P_cr* = {P_het*1e3:.1f} mN no modo n*={n_het} (lambda={L/n_het*1e3:.1f} mm)")
        if case["bifurcated"]:
            ratio_het = case["P_cr"] / P_het if P_het > 0 else float("nan")
            p(f"     CCX/Hetenyi = {ratio_het:.2f} x")
        else:
            p(f"     F_z_max(CCX)/P_cr*(Hetenyi) = {case['P_cr']/P_het*100:.0f}%  (sem bifurcacao)")
        p("")

    p("=" * 76)
    p("COMPARACAO DIRETA SANS vs SAUDAVEL")
    p("=" * 76)
    ratio_Fz = abs(sans["Fz_total"][-1]) / abs(saud["Fz_total"][-1]) if saud["Fz_total"][-1] else float("nan")
    ratio_k = sans["k_axial"] / saud["k_axial"] if saud["k_axial"] > 0 else float("nan")
    p(f"  F_z @ |Dz|=1mm: saudavel = {abs(saud['Fz_total'][-1])*1e3:.2f} mN, SANS = {abs(sans['Fz_total'][-1])*1e3:.2f} mN  (razao {ratio_Fz:.3f}x)")
    p(f"  k_axial pre-buckle: saudavel = {saud['k_axial']:.1f} N/m, SANS = {sans['k_axial']:.1f} N/m  (razao {ratio_k:.3f}x)")

    n_h_saud, P_h_saud = hetenyi_predict(saud["k_winkler"])
    n_h_sans, P_h_sans = hetenyi_predict(sans["k_winkler"])
    p(f"\n  Hetenyi (analitico, viga sobre fundacao elastica):")
    p(f"     saudavel: P_cr={P_h_saud*1e3:.0f} mN no modo n*={n_h_saud} (lambda={L/n_h_saud*1e3:.1f} mm)")
    p(f"     SANS    : P_cr={P_h_sans*1e3:.0f} mN no modo n*={n_h_sans} (lambda={L/n_h_sans*1e3:.1f} mm)")
    p(f"     razao Hetenyi P_cr: {P_h_sans/P_h_saud:.2f}x")
    if n_h_sans > n_h_saud:
        p(f"  => SANS prediz dobra mais focal (lambda {L/n_h_saud*1e3:.0f}mm -> {L/n_h_sans*1e3:.0f}mm)")
        p(f"     'arco suave' do saudavel vira 'pontos de estrangulamento' no SANS.")

    if not saud["bifurcated"] and not sans["bifurcated"]:
        p(f"\nOBSERVACAO IMPORTANTE: nenhum dos dois casos bifurcou ate Dz=1mm.")
        p(f"  F_z(Dz) e monotono crescente em ambos: a perturbacao lateral de 10 Pa")
        p(f"  e insuficiente para destabilizar o cilindro perfeito no NLGEOM. Os valores")
        p(f"  reportados como 'P_cr' sao apenas F_z no fim da rampa (limite inferior).")
        p(f"  Para detectar a bifurcacao real, precisariamos:")
        p(f"     - aumentar a perturbacao em ~100x (1000 Pa em vez de 10 Pa), ou")
        p(f"     - rodar *BUCKLE eigenanalysis e injetar o mode-shape como imperfeicao,")
        p(f"     - ou levar Dz a ~3-5 mm (acima do P_cr Hetenyi de 1.6 N no SANS).")
        p(f"\n  Conclusao quantitativa: F_z(Dz=1mm) << P_cr Hetenyi SANS ({P_h_sans*1e3:.0f} mN),")
        p(f"  confirmando que o nervo NAO atinge flambagem no regime SANS clinico")
        p(f"  (consistente com a conclusao do on-caso-2 antigo: 'flambagem axial nao e")
        p(f"  modo de falha relevante para SANS'). O ganho do CCX e capturar a")
        p(f"  curva F_z(Dz) real com NeoHooke (vs k_axial linear do s4f).")

    p("\n  Para visualizar o modo deformado no CCX:")
    p(f"    cgx -c cases/on-caso-3/ccx/on-caso-3.frd  # vs cases/on-caso-2/ccx/on-caso-2.frd")
    return "\n".join(lines) + "\n"


def make_plot(saud: dict, sans: dict, out_path: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))

    # Painel 1: F_z(|Dz|) sobreposto + linhas Hetenyi
    ax = axes[0]
    for case in (saud, sans):
        ax.plot(np.abs(case["Dz"]) * 1e3, np.abs(case["Fz_total"]) * 1e3,
                "o-", lw=1.7, ms=4, color=case["color"], label=case["label"])
        marker = "*" if case["bifurcated"] else "s"
        sufx = "P_cr" if case["bifurcated"] else "F_z@end"
        ax.plot([abs(case["Dz_cr"]) * 1e3], [case["P_cr"] * 1e3],
                marker, ms=14, color=case["color"], zorder=5,
                label=f"{sufx}={case['P_cr']*1e3:.0f} mN")
        n_het, P_het = hetenyi_predict(case["k_winkler"])
        ax.axhline(P_het * 1e3, ls="--", color=case["color"], alpha=0.4, lw=1)
        ax.text(0.02 * abs(case["Dz"]).max() * 1e3, P_het * 1e3 * 1.03,
                f"Hetenyi n={n_het}: {P_het*1e3:.0f} mN",
                fontsize=7, color=case["color"])
    ax.set_xlabel(r"$|\Delta z|$ (mm)")
    ax.set_ylabel(r"$|F_z|$ total (mN)")
    ax.set_title("(1) Curva F-d CCX NLGEOM (NeoHooke)\nlinhas tracejadas = P_cr Hetenyi analitico")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(alpha=0.3)

    # Painel 2: |F_lat|(Dz) em log -- assinatura de bifurcacao
    ax = axes[1]
    for case in (saud, sans):
        Flat_safe = np.maximum(case["Flat"], 1e-12)
        ax.semilogy(np.abs(case["Dz"]) * 1e3, Flat_safe * 1e3,
                    "o-", lw=1.7, ms=4, color=case["color"], label=case["label"])
        ax.axvline(abs(case["Dz_cr"]) * 1e3, ls="--", color=case["color"], alpha=0.4)
    ax.set_xlabel(r"$|\Delta z|$ (mm)")
    ax.set_ylabel(r"$|F_{lateral}|$ (mN, log)")
    ax.set_title("(2) Reacao lateral (log)\nSalto = onset de bifurcacao")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(alpha=0.3, which="both")

    # Painel 3: tabela-bar de P_cr (CCX vs Hetenyi) por caso
    ax = axes[2]
    cases_list = [saud, sans]
    labels = [c["label"] for c in cases_list]
    P_ccx = [c["P_cr"] * 1e3 for c in cases_list]
    P_het = [hetenyi_predict(c["k_winkler"])[1] * 1e3 for c in cases_list]
    n_het = [hetenyi_predict(c["k_winkler"])[0] for c in cases_list]
    x = np.arange(len(cases_list))
    w = 0.35
    bars_ccx = ax.bar(x - w / 2, P_ccx, w, label="P_cr CCX (NLGEOM)",
                      color=[c["color"] for c in cases_list], alpha=0.85)
    bars_het = ax.bar(x + w / 2, P_het, w, label="P_cr Hetenyi (analitico)",
                      color=[c["color"] for c in cases_list], alpha=0.45, hatch="//")
    for i, (b, val, n) in enumerate(zip(bars_het, P_het, n_het)):
        ax.text(b.get_x() + b.get_width() / 2, val, f"  n={n}",
                ha="left", va="bottom", fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels([lbl.replace(" ", "\n", 1) for lbl in labels], fontsize=9)
    ax.set_ylabel("P_cr (mN)")
    ax.set_title("(3) P_cr: CCX NLGEOM vs Hetenyi\nrotulo = modo n* analitico")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(alpha=0.3, axis="y")

    fig.suptitle("on-caso-3 (SANS, gordura edemaciada) vs on-caso-2 (saudavel) - CalculiX NLGEOM",
                 fontsize=12, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(out_path, dpi=140)
    print(f"Plot salvo em {out_path}")


def main():
    saud = compute_case("on-caso-2")
    sans = compute_case("on-caso-3")

    if saud is None:
        raise SystemExit(
            "on-caso-2/ccx/on-caso-2.dat nao encontrado / vazio. Rode primeiro:\n"
            "  docker compose run --rm fsi bash -lc 'cd /simulation/on-caso-2/ccx && ./Allrun'"
        )
    if sans is None:
        raise SystemExit(
            "on-caso-3/ccx/on-caso-3.dat nao encontrado / vazio. Rode primeiro:\n"
            "  docker compose run --rm fsi bash -lc 'cd /simulation/on-caso-3/ccx && ./Allrun'"
        )

    txt = write_summary(saud, sans)
    print(txt)
    SUMMARY.write_text(txt)
    print(f"Sumario salvo em {SUMMARY}\n")

    make_plot(saud, sans, PNG)


if __name__ == "__main__":
    main()
