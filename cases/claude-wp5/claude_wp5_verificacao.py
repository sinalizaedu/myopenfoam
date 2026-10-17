#!/usr/bin/env python3
"""WP5 — verificacao da especificacao antes de implementar.

O WP5 ainda nao existe como codigo. Este script verifica, item por item, a
aritmetica e as hipoteses da Secao 5 do plano de tese, usando o solver 0D do WP0
(que ja tem o termo de paracentese de Poiseuille) e a lei constitutiva que o
WP1.2 adotou.

Achado principal (ver claude-REVISAO-WP5-WP6.md): a Secao 5.3 do plano calcula o
volume de paracentese por dV = dIOP/K, uma LINEARIZACAO, enquanto a tese adota
uma lei exponencial (Friedenwald). A linearizacao superestima o volume
necessario em ~1,8x, e e justamente isso que faz a paracentese "parecer"
inviavel na tabela do plano.

Uso no Docker:
    docker compose run --rm fsi bash -lc \
      'pip install numpy scipy --break-system-packages && \
       cd /simulation/claude-wp5 && python3 claude_wp5_verificacao.py'
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = HERE.parent
WP0 = CASES / "wp0"
if str(WP0) not in sys.path:
    sys.path.insert(0, str(WP0))

MMHG_PA = 133.322

# --- lei constitutiva adotada no WP1.2 ----------------------------------------
# Friedenwald recalibrada: P = P0 * 10^(Kf*V), com P0 = 16,9 mmHg e a previsao
# de 33,0 mmHg em 50 uL (WP1.2, "a curva de Friedenwald recalibrada e o alvo
# adotado daqui em diante").
P0_WP12 = 16.9
P_EM_50UL_WP12 = 33.0
KF_WP12 = math.log10(P_EM_50UL_WP12 / P0_WP12) / 50.0

# Faixa de Kf da literatura, conforme a lista de hedges do plano:
# "faixa real da literatura e 0,0126-0,0280 uL^-1 (Pallikaris et al. 2005 para o
# limite inferior, medido em 79 olhos vivos; ... Friedenwald 1937 original 0,0215)"
KF_LITERATURA = {
    "Pallikaris 2005 (limite inf.)": 0.0126,
    "Friedenwald 1937 (original)": 0.0215,
    "limite sup. da faixa do plano": 0.0280,
}


def V_de_P_friedenwald(P_mmHg: float, Kf: float, P0_mmHg: float) -> float:
    """Volume acima do basal para atingir P [uL], lei exponencial."""
    return math.log10(P_mmHg / P0_mmHg) / Kf


def K_basal_friedenwald(Kf: float, P0_mmHg: float) -> float:
    """dP/dV em P0 [mmHg/uL]: derivada de P0*10^(Kf*V) em V=0."""
    return math.log(10.0) * Kf * P0_mmHg


def resistencia_poiseuille(d_mm: float, L_mm: float, mu_Pa_s: float = 0.75e-3) -> float:
    """R = 8*mu*L/(pi*r^4) [Pa.s/m3]. mu do aquoso ~0,75 mPa.s (plano, WP7.4)."""
    r = (d_mm / 2.0) * 1e-3
    return 8.0 * mu_Pa_s * (L_mm * 1e-3) / (math.pi * r**4)


def vazao_paracentese(P_mmHg: float, R_Pa_s_per_m3: float, Patm_mmHg: float = 0.0) -> float:
    """Q [uL/s] por Poiseuille, com dP = P - Patm."""
    return (P_mmHg - Patm_mmHg) * MMHG_PA / R_Pa_s_per_m3 * 1e9


def tempo_para_drenar(
    V_alvo_uL: float, P_ini_mmHg: float, Kf: float, P0_mmHg: float,
    R_Pa_s_per_m3: float, dt_s: float = 0.01,
) -> dict:
    """Integra a drenagem por Poiseuille com P(V) exponencial, para testar se
    tratar a paracentese como instantanea e defensavel na escala de tau."""
    V = V_de_P_friedenwald(P_ini_mmHg, Kf, P0_mmHg)   # volume atual acima do basal
    V_fim = max(V - V_alvo_uL, 0.0)
    t = 0.0
    while V > V_fim and t < 600.0:
        P = P0_mmHg * 10.0 ** (Kf * V)
        Q = vazao_paracentese(P, R_Pa_s_per_m3)
        if Q <= 0:
            break
        V -= Q * dt_s
        t += dt_s
    return {"t_s": t, "P_final_mmHg": P0_mmHg * 10.0 ** (Kf * max(V, 0.0))}


def main() -> int:
    print("=" * 74)
    print("WP5 — verificacao da especificacao (Secao 5 do plano)")
    print("=" * 74)

    # ---- item 5.3: volume de paracentese -----------------------------------
    print("\n[5.3] Volume para baixar a IOP de 50 mmHg ate o basal")
    print("\n  (i) Tabela do plano — LINEARIZADA, dV = dIOP/K, 50->15 mmHg:")
    for K, lbl in ((0.196, "casca fina linear (WP1.1)"),
                   (0.34, "intermediario"),
                   (0.44, "Friedenwald in vivo")):
        dV = (50.0 - 15.0) / K
        print(f"      K={K:5.3f} ({lbl:26s}) dV={dV:6.1f} uL")

    print("\n  (ii) Mesma pergunta com a lei EXPONENCIAL que a tese adota:")
    print("       V(P) = log10(P/P0)/Kf  — integra a curva em vez de linearizar")
    for lbl, Kf in KF_LITERATURA.items():
        P0 = 15.0
        dV_exp = V_de_P_friedenwald(50.0, Kf, P0)
        Kb = K_basal_friedenwald(Kf, P0)
        dV_lin = (50.0 - P0) / Kb
        print(f"      {lbl:32s} exponencial={dV_exp:5.1f} uL | "
              f"linearizada={dV_lin:5.1f} uL | fator={dV_lin / dV_exp:.2f}x")

    print(f"\n  (iii) Com o Kf efetivamente adotado no WP1.2:")
    print(f"       Kf_recal = {KF_WP12:.6f} /uL (de P0={P0_WP12} e {P_EM_50UL_WP12} mmHg @50uL)")
    dV_exp = V_de_P_friedenwald(50.0, KF_WP12, P0_WP12)
    Kb = K_basal_friedenwald(KF_WP12, P0_WP12)
    dV_lin = (50.0 - P0_WP12) / Kb
    print(f"       K(basal) = {Kb:.4f} mmHg/uL")
    print(f"       dV 50->16,9 exponencial = {dV_exp:5.1f} uL")
    print(f"       dV 50->16,9 linearizada = {dV_lin:5.1f} uL  (fator {dV_lin / dV_exp:.2f}x)")

    print("\n  INCONSISTENCIA A RESOLVER: o Kf adotado no WP1.2 "
          f"({KF_WP12:.5f}) esta ABAIXO")
    print(f"  do limite inferior da faixa de literatura do plano "
          f"({min(KF_LITERATURA.values())}) por fator "
          f"{min(KF_LITERATURA.values()) / KF_WP12:.1f}x.")
    print("  Isso e consequencia deliberada da recalibracao contra o pico de Knecht")
    print("  (o plano avisa que Kf=0,0126 produz pico de 63 mmHg, alto demais), mas")
    print("  os dois valores nao podem coexistir na tese sem essa frase explicita.")

    # ---- fracao da camara anterior -----------------------------------------
    print("\n  Fracao da camara anterior (o plano usa ~250 uL — PRECISA DE FONTE):")
    for V_ca in (150.0, 200.0, 250.0):
        print(f"      CA={V_ca:5.1f} uL: exponencial={dV_exp / V_ca * 100:5.1f}% | "
              f"linearizada={dV_lin / V_ca * 100:5.1f}%")

    # ---- item 5.1/5.4: resistencia e tempo de drenagem ---------------------
    print("\n[5.1/5.4] Resistencia da via de paracentese e tempo de drenagem")
    R_plano = 6.2e11
    print(f"  Plano: R = {R_plano:.2e} Pa.s/m3 -> Q = "
          f"{vazao_paracentese(20.0, R_plano):.2f} uL/s @ 20 mmHg (plano diz 4,29)")
    print("  Checagem por Poiseuille (mu_aquoso = 0,75 mPa.s):")
    for d, L, lbl in ((0.159, 12.7, "30G, 1/2 pol"),
                      (0.159, 25.4, "30G, 1 pol"),
                      (0.241, 12.7, "25G, 1/2 pol")):
        R = resistencia_poiseuille(d, L)
        marca = " <-- compativel com o R do plano" if abs(R - R_plano) / R_plano < 0.15 else ""
        print(f"      {lbl:14s} R={R:.2e}  Q@20mmHg={vazao_paracentese(20.0, R):6.2f} uL/s{marca}")

    print("\n  Paracentese e 'instantanea'? (tau de Ruffini 2024 = 3,18 min = 191 s)")
    for lbl, Kf, P0 in (("Kf WP1.2", KF_WP12, P0_WP12),
                        ("Kf Pallikaris", 0.0126, 15.0)):
        alvo = V_de_P_friedenwald(50.0, Kf, P0)
        r = tempo_para_drenar(alvo, 50.0, Kf, P0, R_plano)
        print(f"      {lbl:14s} drenar {alvo:5.1f} uL de 50 mmHg leva "
              f"{r['t_s']:6.1f} s ({r['t_s'] / 191.0 * 100:4.1f}% de tau) "
              f"-> P={r['P_final_mmHg']:.1f} mmHg")
    print("  => tratar como instantanea e defensavel na escala de tau; mas o")
    print("     plano deve reportar esse numero em vez de assumir.")

    # ---- item 5.4: timing, com o solver 0D ---------------------------------
    print("\n[5.4] Timing da paracentese — requer o solver do WP0")
    try:
        from goldmann_iop_solver import FriedenwaldPV, Protocol, simulate  # noqa
    except Exception as exc:
        print(f"  solver 0D nao importavel aqui ({type(exc).__name__}); rode no container.")
        return 0

    sys.path.insert(0, str(CASES / "wp4"))
    try:
        from opp_perfusion import aplicar_cadeia
        from claude_wp4_fixes import dose_isquemica_exata
    except Exception:
        sys.path.insert(0, str(CASES / "claude-wp4"))
        from opp_perfusion import aplicar_cadeia  # type: ignore
        from claude_wp4_fixes import dose_isquemica_exata  # type: ignore

    pv = FriedenwaldPV(Kf_per_uL=KF_WP12, P0_mmHg=P0_WP12)
    print("  I(t_paracentese), MOPP, PAS=120/PAD=70, OPP_crit=50:")
    for t_par in (0.0, 1.0, 2.0, 5.0, 10.0, None):
        if t_par is None:
            proto = Protocol(t_end_min=40.0, par_enabled=False)
            rotulo = "sem paracentese"
        else:
            proto = Protocol(t_end_min=40.0, par_enabled=True,
                             t_par_start_min=t_par, R_par_Pa_s_per_m3=R_plano)
            rotulo = f"paracentese em t={t_par:.0f} min"
        try:
            t, _V, P = simulate(proto, pv)
        except TypeError as exc:
            print(f"    (assinatura de Protocol difere: {exc}) — ajustar os kwargs")
            break
        ch = aplicar_cadeia(t, P, pas=120, pad=70, opp_crit_ref=50.0)
        I = dose_isquemica_exata(t, ch["mopp"], ch["opp_crit_efetivo"])
        print(f"    {rotulo:22s} IOP_max={max(P):6.2f}  "
              f"MOPP_min={min(ch['mopp']):6.2f}  I={I:8.2f} mmHg.min")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
