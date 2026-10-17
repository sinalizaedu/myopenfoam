"""
claude_h6_teorico.py
======================

Item 4.3 do WP4: o resultado teorico H6 (versao corrigida, Secao 1/4.3
do plano de tese) e suas tres consequencias. Construido sobre o 4.2
(claude_dose_isquemica.py), que ja implementa e valida numericamente a
formula fechada (validacao_fechada_H6, erro ~0.17% no cenario humano).
Este modulo NAO reimplementa a validacao -- adiciona o que 4.3 pede que
4.2 ainda nao cobria:

    I = dV/C - dPth/(C*K) * [1 + ln(K*dV/dPth)]           (dPth < K*dV)
    I = 0                                                   (dPth >= K*dV)
    K_crit = dPth / dV

Tres consequencias (Secao 4.3 do plano):
  1. Sem limiar, K cancela -- I = dV/C e o limite superior assintotico
     (K->infinito).
  2. Com limiar, existe K_crit abaixo do qual a dose e EXATAMENTE zero
     -- quase binario.
  3. C_out escala tudo linearmente -- glaucomatoso (C baixo) tem I
     proporcionalmente maior em QUALQUER K.

ALERTA METODOLOGICO do plano (citado literalmente): "todo o resultado
depende do valor de dPth, que e justamente o parametro mais mal
conhecido do modelo. Apresente I e K_crit como funcao de dPth, nunca
com um valor fixo." Este modulo faz isso por construcao -- toda funcao
publica aqui aceita dPth (ou uma faixa dele) como parametro, nenhuma
tem um dPth hardcoded.
"""

from __future__ import annotations

import numpy as np

_trapz = getattr(np, "trapezoid", None) or np.trapz


def dose_fechada_H6(K_mmHg_per_uL: float, dV_uL: float, C_out_uL_min_mmHg: float,
                     dPth_mmHg: float) -> float:
    """
    Formula fechada de H6 (Secao 1/4.3), ja generalizada para dPth<=0
    (perfusao basal ja abaixo do limiar mesmo sem injecao -- I diverge
    nesse regime porque o modelo 0D assume decaimento exponencial
    infinito sem nenhum outro mecanismo de recuperacao; ver ressalva no
    docstring de curva_I_vs_dPth). Para dPth>0 e o resultado normal:

        I = dV/C - dPth/(C*K) * [1 + ln(K*dV/dPth)]   se K*dV > dPth
        I = 0                                          se K*dV <= dPth

    Note: esta e a MESMA formula que validacao_fechada_H6() (4.2) ja
    valida numericamente contra o solver 0D (erro ~0.17% no cenario
    humano) -- aqui ela e reescrita em termos dos parametros primitivos
    (K, dV, C, dPth), nao de um Protocol/PV concretos, para poder
    varrer dPth livremente (o que o plano exige) sem precisar rodar o
    solver 0D a cada ponto.
    """
    if dPth_mmHg <= 0:
        raise ValueError(
            f"dPth={dPth_mmHg:.3f} <= 0: perfusao basal ja abaixo do "
            "limiar mesmo sem injecao -- fora do dominio de H6 (ver "
            "validacao_fechada_H6 em claude_dose_isquemica.py, mesma "
            "checagem)."
        )
    dP0 = K_mmHg_per_uL * dV_uL
    if dP0 <= dPth_mmHg:
        return 0.0
    tau = 1.0 / (C_out_uL_min_mmHg * K_mmHg_per_uL)
    return tau * (dP0 - dPth_mmHg - dPth_mmHg * np.log(dP0 / dPth_mmHg))


def K_crit(dPth_mmHg: float, dV_uL: float) -> float:
    """
    K_crit = dPth / dV  [mmHg/uL]

    Abaixo de K_crit, I=0 EXATAMENTE (regime "sem dano" -- a elevacao de
    pico dP0=K*dV nunca ultrapassa o limiar dPth). Acima, I>0 e cresce
    (ver dose_fechada_H6). Requer dPth>0 (ver dose_fechada_H6).
    """
    if dPth_mmHg <= 0:
        raise ValueError(f"dPth={dPth_mmHg:.3f} <= 0: K_crit indefinido nesse regime (ver dose_fechada_H6).")
    if dV_uL <= 0:
        raise ValueError(f"dV_uL={dV_uL} deve ser > 0.")
    return dPth_mmHg / dV_uL


def limite_superior_dV_sobre_C(dV_uL: float, C_out_uL_min_mmHg: float) -> float:
    """
    Consequencia 1: SEM limiar (ou K->infinito), I -> dV/C -- o limite
    superior assintotico de dose_fechada_H6, independente de K. Serve
    de referencia de escala para julgar o quao perto de "pior caso" um
    K observado esta.
    """
    return dV_uL / C_out_uL_min_mmHg


def curva_I_vs_K(K_range_mmHg_per_uL, dV_uL: float, C_out_uL_min_mmHg: float,
                  dPth_mmHg: float) -> dict:
    """
    Consequencia 1+2 juntas: I(K) para uma faixa de K, no mesmo (dV, C,
    dPth). Mostra a transicao quase-binaria em K_crit e a saturacao
    assintotica em dV/C para K grande. Nunca reporte um I(K) isolado --
    plote/tabule esta curva.
    """
    out = {}
    for K in K_range_mmHg_per_uL:
        out[float(K)] = dose_fechada_H6(K, dV_uL, C_out_uL_min_mmHg, dPth_mmHg)
    return out


def curva_I_vs_dPth(dPth_range_mmHg, K_mmHg_per_uL: float, dV_uL: float,
                     C_out_uL_min_mmHg: float) -> dict:
    """
    ALERTA METODOLOGICO do plano (Secao 4.3): dPth e o parametro mais
    mal conhecido do modelo -- NUNCA reporte I ou K_crit com um dPth
    fixo. Esta funcao varre dPth (que depende de MAP, P0 e
    OPP_crit_efetivo, todos incertos) e devolve I(dPth) para o MESMO
    (K, dV, C). dPth<=0 e pulado (fora do dominio -- ver dose_fechada_H6)
    e marcado como None no dict de saida, para nao quebrar a varredura
    inteira por causa de um unico ponto fora de dominio.
    """
    out = {}
    for dPth in dPth_range_mmHg:
        dPth = float(dPth)
        if dPth <= 0:
            out[dPth] = None
        else:
            out[dPth] = dose_fechada_H6(K_mmHg_per_uL, dV_uL, C_out_uL_min_mmHg, dPth)
    return out


def K_crit_vs_dPth(dPth_range_mmHg, dV_uL: float) -> dict:
    """
    K_crit como funcao de dPth (mesma exigencia do plano: nunca um
    K_crit fixo). dPth<=0 marcado como None (K_crit indefinido).
    """
    out = {}
    for dPth in dPth_range_mmHg:
        dPth = float(dPth)
        out[dPth] = None if dPth <= 0 else K_crit(dPth, dV_uL)
    return out


def escala_C_out(K_mmHg_per_uL: float, dV_uL: float, dPth_mmHg: float,
                  C_out_range_uL_min_mmHg) -> dict:
    """
    Consequencia 3: C_out escala I linearmente -- ver verificacao
    analitica em verificar_escala_linear_C_out(). Esta funcao apenas
    tabula I(C_out) no mesmo (K, dV, dPth), para reportar ao lado da
    verificacao.
    """
    out = {}
    for C in C_out_range_uL_min_mmHg:
        out[float(C)] = dose_fechada_H6(K_mmHg_per_uL, dV_uL, C, dPth_mmHg)
    return out


def verificar_escala_linear_C_out(K_mmHg_per_uL: float, dV_uL: float, dPth_mmHg: float,
                                   C_ref_uL_min_mmHg: float, fator: float = 0.5) -> dict:
    """
    Verifica a Consequencia 3 diretamente na formula: I(C) = I(C_ref) *
    (C_ref/C) EXATAMENTE, para qualquer K -- porque tau=1/(C*K) e o
    UNICO lugar em que C aparece em dose_fechada_H6, e tau entra
    multiplicando toda a expressao (dP0, dPth, K nao dependem de C).

    fator: C_teste = C_ref * fator (ex.: 0.5 -> C_out pela metade,
    "glaucomatoso" -- C_out tipicamente reduzido).

    Retorna dict com I_ref, I_teste, razao_observada (I_teste/I_ref) e
    razao_esperada (1/fator), para conferencia direta -- devem ser
    identicas a menos de erro de ponto flutuante (nao ha aproximacao
    numerica aqui, e a mesma formula fechada avaliada duas vezes).
    """
    C_teste = C_ref_uL_min_mmHg * fator
    I_ref = dose_fechada_H6(K_mmHg_per_uL, dV_uL, C_ref_uL_min_mmHg, dPth_mmHg)
    I_teste = dose_fechada_H6(K_mmHg_per_uL, dV_uL, C_teste, dPth_mmHg)
    razao_obs = I_teste / I_ref if I_ref > 0 else float("nan")
    return {
        "C_ref": C_ref_uL_min_mmHg, "C_teste": C_teste,
        "I_ref_mmHg_min": I_ref, "I_teste_mmHg_min": I_teste,
        "razao_observada": razao_obs, "razao_esperada": 1.0 / fator,
    }


if __name__ == "__main__":
    # Cenario ilustrativo humano: dV=50 uL, C_out=0.28 (literatura,
    # Goel et al. 2010), MAP/P0/OPP_crit tipicos -> dPth de referencia
    # (mesmo cenario de validacao_fechada_H6 em claude_dose_isquemica.py)
    dV = 50.0
    C = 0.28

    print("=== Consequencia 1: limite superior dV/C (independente de K) ===")
    print(f"  dV/C = {limite_superior_dV_sobre_C(dV, C):.2f} mmHg.min")

    print("\n=== Consequencia 2: I(K) e K_crit, dPth=15 mmHg (exemplo do plano) ===")
    dPth_exemplo = 15.0
    print(f"  K_crit = {K_crit(dPth_exemplo, dV):.4f} mmHg/uL "
          f"(plano cita 0.30 para dPth=15, dV=50 -- confere)")
    curva_K = curva_I_vs_K([0.05, 0.10, 0.20, 0.30, 0.31, 0.40, 0.60, 1.00, 3.00],
                           dV, C, dPth_exemplo)
    for K, I in curva_K.items():
        print(f"  K={K:5.3f}  I={I:8.3f} mmHg.min")

    print("\n=== Consequencia 3: escala linear em C_out ===")
    v = verificar_escala_linear_C_out(K_mmHg_per_uL=0.5, dV_uL=dV, dPth_mmHg=dPth_exemplo,
                                       C_ref_uL_min_mmHg=0.28, fator=0.5)
    print(f"  I(C=0.28)      = {v['I_ref_mmHg_min']:.3f}")
    print(f"  I(C=0.14, 'glaucomatoso') = {v['I_teste_mmHg_min']:.3f}")
    print(f"  razao observada = {v['razao_observada']:.4f}  (esperada = {v['razao_esperada']:.4f})")

    print("\n=== Alerta metodologico: I e K_crit como funcao de dPth (nunca fixo) ===")
    faixa_dPth = [5, 10, 15, 20, 25, 30]
    print("  I(dPth), K=0.5 mmHg/uL:")
    for dPth, I in curva_I_vs_dPth(faixa_dPth, 0.5, dV, C).items():
        print(f"    dPth={dPth:5.1f}  I={I}")
    print("  K_crit(dPth):")
    for dPth, kc in K_crit_vs_dPth(faixa_dPth, dV).items():
        print(f"    dPth={dPth:5.1f}  K_crit={kc}")
