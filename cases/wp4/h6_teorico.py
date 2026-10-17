"""WP4.3 — resultado teórico H6 (versão corrigida, Seção 1/4.3 do plano) e
suas três consequências, em termos dos parâmetros primitivos (K, ΔV, C_out, dPth).

Construído sobre o 4.2 (``dose_isquemica.py``), que já VALIDA a fórmula
fechada contra o solver 0D (``validacao_fechada_H6``). Este módulo não
revalida — reescreve a fórmula em primitivos para varrer cada parâmetro
sem rodar o solver 0D a cada ponto:

    I = dV/C − dPth/(C·K) · [1 + ln(K·dV/dPth)]   se K·dV > dPth
    I = 0                                          se K·dV ≤ dPth
    K_crit = dPth / dV

Três consequências (Seção 4.3 do plano):
  1. Sem limiar, K cancela — I → dV/C é o limite superior assintótico (K→∞).
  2. Com limiar, existe K_crit abaixo do qual a dose é EXATAMENTE zero —
     quase binário.
  3. C_out escala tudo linearmente — I(C/2) = 2·I(C) EXATAMENTE, para
     qualquer K (τ = 1/(C·K) é o único lugar onde C aparece, multiplicando
     a expressão inteira).

ALERTA METODOLÓGICO do plano (citação literal): "todo o resultado depende
do valor de dPth, que é justamente o parâmetro mais mal conhecido do
modelo... Apresente 𝓘 e K_crit como função de dPth, nunca com um valor
fixo." Por construção, nenhuma função pública deste módulo tem dPth
hardcoded — todas recebem dPth (ou uma faixa dele) como argumento.
"""
from __future__ import annotations

import numpy as np


def dose_fechada_H6(
    K_mmHg_per_uL: float,
    dV_uL: float,
    C_out_uL_min_mmHg: float,
    dPth_mmHg: float,
) -> float:
    """Fórmula fechada de H6 em primitivos.

    ``dV_uL`` é o volume líquido do bólus (no WP0/WP4: ``V_inj − ΔV_refluxo``
    para refluxo instantâneo pós-IVI). ValueError (não NaN) se dPth ≤ 0
    (perfusão basal já abaixo do limiar sem injeção — fora do domínio de H6;
    mesma checagem de ``validacao_fechada_H6`` no 4.2)."""
    if dPth_mmHg <= 0:
        raise ValueError(
            f"dPth={dPth_mmHg:.3f} <= 0: perfusão basal já abaixo do limiar "
            "mesmo sem injeção — fora do domínio de H6 (ver "
            "validacao_fechada_H6 em dose_isquemica.py, mesma checagem)."
        )
    dP0 = K_mmHg_per_uL * dV_uL
    if dP0 <= dPth_mmHg:
        return 0.0
    tau = 1.0 / (C_out_uL_min_mmHg * K_mmHg_per_uL)
    return float(tau * (dP0 - dPth_mmHg - dPth_mmHg * np.log(dP0 / dPth_mmHg)))


def K_crit(dPth_mmHg: float, dV_uL: float) -> float:
    """K_crit = dPth/ΔV [mmHg/µL]. Abaixo dele, I = 0 EXATAMENTE (o pico
    K·ΔV nunca ultrapassa o limiar); acima, I > 0 e cresce."""
    if dPth_mmHg <= 0:
        raise ValueError(
            f"dPth={dPth_mmHg:.3f} <= 0: K_crit indefinido nesse regime "
            "(ver dose_fechada_H6)."
        )
    if dV_uL <= 0:
        raise ValueError(f"dV_uL={dV_uL} deve ser > 0.")
    return dPth_mmHg / dV_uL


def limite_superior_dV_sobre_C(dV_uL: float, C_out_uL_min_mmHg: float) -> float:
    """Consequência 1: sem limiar (ou K→∞), I → ΔV/C — limite superior
    assintótico de ``dose_fechada_H6``, independente de K."""
    return dV_uL / C_out_uL_min_mmHg


def curva_I_vs_K(K_range_mmHg_per_uL, dV_uL: float, C_out_uL_min_mmHg: float,
                 dPth_mmHg: float) -> dict:
    """I(K) para uma faixa de K, no mesmo (ΔV, C, dPth) — mostra a transição
    quase-binária em K_crit e a saturação assintótica em ΔV/C."""
    return {
        float(K): dose_fechada_H6(K, dV_uL, C_out_uL_min_mmHg, dPth_mmHg)
        for K in K_range_mmHg_per_uL
    }


def curva_I_vs_dPth(dPth_range_mmHg, K_mmHg_per_uL: float, dV_uL: float,
                    C_out_uL_min_mmHg: float) -> dict:
    """I(dPth) para o mesmo (K, ΔV, C) — exigência do alerta metodológico.
    dPth ≤ 0 é marcado como ``None`` (fora de domínio), sem quebrar a
    varredura inteira por um único ponto."""
    out = {}
    for dPth in dPth_range_mmHg:
        dPth = float(dPth)
        out[dPth] = (
            None if dPth <= 0
            else dose_fechada_H6(K_mmHg_per_uL, dV_uL, C_out_uL_min_mmHg, dPth)
        )
    return out


def K_crit_vs_dPth(dPth_range_mmHg, dV_uL: float) -> dict:
    """K_crit(dPth) — mesma exigência do plano: nunca um K_crit fixo.
    dPth ≤ 0 marcado como ``None``."""
    out = {}
    for dPth in dPth_range_mmHg:
        dPth = float(dPth)
        out[dPth] = None if dPth <= 0 else K_crit(dPth, dV_uL)
    return out


def escala_C_out(K_mmHg_per_uL: float, dV_uL: float, dPth_mmHg: float,
                 C_out_range_uL_min_mmHg) -> dict:
    """Consequência 3 em tabela: I(C_out) no mesmo (K, ΔV, dPth)."""
    return {
        float(C): dose_fechada_H6(K_mmHg_per_uL, dV_uL, C, dPth_mmHg)
        for C in C_out_range_uL_min_mmHg
    }


def verificar_escala_linear_C_out(
    K_mmHg_per_uL: float,
    dV_uL: float,
    dPth_mmHg: float,
    C_ref_uL_min_mmHg: float,
    fator: float = 0.5,
) -> dict:
    """Verificação direta da Consequência 3: I(C_ref·fator) = I(C_ref)/fator
    EXATAMENTE (ex.: fator=0,5 → C_out pela metade, "glaucomatoso", dobra I).
    Não há aproximação numérica — é a mesma fórmula avaliada duas vezes."""
    C_teste = C_ref_uL_min_mmHg * fator
    I_ref = dose_fechada_H6(K_mmHg_per_uL, dV_uL, C_ref_uL_min_mmHg, dPth_mmHg)
    I_teste = dose_fechada_H6(K_mmHg_per_uL, dV_uL, C_teste, dPth_mmHg)
    razao_obs = I_teste / I_ref if I_ref > 0 else float("nan")
    return {
        "C_ref": C_ref_uL_min_mmHg,
        "C_teste": C_teste,
        "I_ref_mmHg_min": I_ref,
        "I_teste_mmHg_min": I_teste,
        "razao_observada": razao_obs,
        "razao_esperada": 1.0 / fator,
    }


if __name__ == "__main__":
    # Cenário do plano: dPth=15 mmHg, ΔV=50 µL, C=0,28 µL/min/mmHg.
    dV, C, dPth = 50.0, 0.28, 15.0

    print("=== Consequência 1: limite superior ΔV/C (independente de K) ===")
    print(f"  dV/C = {limite_superior_dV_sobre_C(dV, C):.2f} mmHg.min")

    print(f"\n=== Consequência 2: I(K), dPth={dPth} (exemplo do plano) ===")
    print(f"  K_crit = {K_crit(dPth, dV):.4f} mmHg/uL (plano cita 0,30 — confere)")
    for K, I in curva_I_vs_K([0.05, 0.10, 0.20, 0.30, 0.31, 0.40, 0.60, 1.00, 3.00],
                             dV, C, dPth).items():
        print(f"  K={K:5.3f}  I={I:8.3f} mmHg.min")

    print("\n=== Consequência 3: escala linear em C_out ===")
    v = verificar_escala_linear_C_out(0.5, dV, dPth, C_ref_uL_min_mmHg=C, fator=0.5)
    print(f"  I(C=0,28) = {v['I_ref_mmHg_min']:.3f} ; I(C=0,14) = {v['I_teste_mmHg_min']:.3f}")
    print(f"  razão observada = {v['razao_observada']:.6f} (esperada = {v['razao_esperada']:.6f})")

    print("\n=== Alerta metodológico: I e K_crit como função de dPth ===")
    faixa = [5, 10, 15, 20, 25, 30]
    print("  I(dPth), K=0,5 mmHg/uL:")
    for d, I in curva_I_vs_dPth(faixa, 0.5, dV, C).items():
        print(f"    dPth={d:5.1f}  I={I}")
    print("  K_crit(dPth):")
    for d, kc in K_crit_vs_dPth(faixa, dV).items():
        print(f"    dPth={d:5.1f}  K_crit={kc}")
