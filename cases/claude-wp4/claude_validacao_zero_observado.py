"""
claude_validacao_zero_observado.py
=====================================

Item 4.4 do WP4: validacao teorica contra o zero observado. Construido
sobre o 4.3 (claude_h6_teorico.py) e o 4.1 (claude_opp_perfusion.py --
phi_vasc).

ATENCAO -- ESCOPO E RASTREABILIDADE (corrigido):
Este item 4.4 NAO existe no plano de tese. O plano tem apenas 4.1, 4.2 e
4.3 na secao WP4. Uma versao anterior deste arquivo abria com uma frase
entre aspas atribuida ao plano ("mostrar que o modelo reproduz
corretamente a ausencia de deficit perfusional...") -- essa frase NAO
consta do plano e foi removida. O item e uma extensao proposta, nao um
item planejado, e deve ser apresentado como tal.

Objetivo (formulacao propria, sem atribuicao): verificar se o modelo
reproduz a ausencia de deficit perfusional relatada na literatura para
injecao unica, e delimitar a regiao parametrica onde essa previsao
deixaria de valer.

Esta etapa e inteiramente computacional (literatura publicada vs
simulacao 0D) -- nenhum dado proprio, nenhuma chamada ao solver 0D
concreto necessaria (tudo em termos de dPth/K/dV primitivos, igual ao
4.3).

Tres pecas, na ordem do plano:

1. Confrontar o zero do OCT-A 2026 (n=54, pico de IOP 14->31 mmHg,
   MOPP~31 mmHg relatado durante o evento) com a previsao do modelo:
   para que faixa de OPP_crit o modelo tambem prediz zero?
2. Simular o subgrupo de risco de Damasceno et al. 2022 (K alto = olho
   curto + phi_vasc elevado = obstrucao carotidea) e verificar que o
   modelo prediz 𝓘>0 nesse subgrupo, mesmo quando o paciente tipico (K
   tipico, phi_vasc=1) tem 𝓘=0 no MESMO cenario basal.
3. Controle negativo: o achado de afinamento retiniano de 25% aos 15
   min pos-IVI (resolvido em 48h, atribuido a compressao mecanica, nao
   isquemia) NAO deve ser confundido pelo modelo com dose isquemica --
   e um efeito estrutural/mecanico transitorio, fora do espaco de
   variaveis deste modelo (MOPP/OPP_diast, nao espessura retiniana).
"""

from __future__ import annotations

import numpy as np

from claude_h6_teorico import dose_fechada_H6
from claude_opp_perfusion import opp_crit_efetivo

# --- Peca 1: OCT-A 2026 (n=54) ---------------------------------------------

IOP_BASAL_OCT_A_MMHG = 14.0
IOP_PICO_OCT_A_MMHG = 31.0
MOPP_MIN_OBSERVADO_OCT_A_MMHG = 31.0  # relatado diretamente no estudo (nao recalculado a partir de MAP populacional -- ver README)
N_OLHOS_OCT_A = 54
DV_TIPICO_UL = 50.0


def K_implicito_do_pico_observado(iop_basal_mmHg: float = IOP_BASAL_OCT_A_MMHG,
                                   iop_pico_mmHg: float = IOP_PICO_OCT_A_MMHG,
                                   dV_uL: float = DV_TIPICO_UL) -> float:
    """
    K implicito = (pico - basal) / dV  [mmHg/uL]

    NAO e um K medido independentemente -- e uma LEITURA do proprio dado
    do OCT-A (o pico de IOP relatado), assumindo dV=50 uL tipico. Serve
    de ancora de ordem de grandeza para "K tipico de populacao", nao
    como substituto do emulador do WP1.4 (que usa biometria real).
    """
    return (iop_pico_mmHg - iop_basal_mmHg) / dV_uL


def opp_crit_maximo_consistente_com_zero(MOPP_min_observado_mmHg: float = MOPP_MIN_OBSERVADO_OCT_A_MMHG) -> float:
    """
    O modelo prediz 𝓘=0 sse OPP_crit <= MOPP_min observado durante o
    evento (nenhum instante cruza o limiar). Esta funcao so devolve o
    proprio MOPP_min observado -- e o teto de OPP_crit consistente com
    o zero relatado, dado explicitamente para nao deixar essa conclusao
    implicita no meio de uma tabela.
    """
    return MOPP_min_observado_mmHg


def tabela_consistencia_zero_oct_a(
    OPP_crit_range=(15, 20, 25, 30, 31, 35, 40, 45, 50),
    MOPP_min_observado_mmHg: float = MOPP_MIN_OBSERVADO_OCT_A_MMHG,
) -> dict:
    """
    Para cada OPP_crit candidato (parametro incerto -- ver alerta
    metodologico do plano, Secao 4.2/4.3), diz se o modelo prediz "zero"
    (consistente com o OCT-A) ou "deficit>0" (inconsistente -- exigiria
    revisar a hipotese de que o limiar cronico ~50 mmHg vale para
    eventos transitorios).

    Nao depende de K/dV/C_out: a comparacao e feita diretamente contra o
    MOPP_min OBSERVADO (dado da literatura), nao contra um MOPP_min
    recalculado a partir de MAP populacional -- ver README para o porque
    (o estudo tem seu proprio MAP de coorte, que nao reproduzimos aqui).
    """
    out = {}
    for opp in OPP_crit_range:
        opp = float(opp)
        out[opp] = "zero (consistente com OCT-A)" if opp <= MOPP_min_observado_mmHg else "deficit>0 (inconsistente com OCT-A)"
    return out


# --- Peca 2: subgrupo de risco de Damasceno et al. 2022 --------------------

# Fracao de casos de CRAO transitoria pos-IVI com obstrucao carotidea
# significativa (Damasceno et al. 2022): 18/4069 injecoes (0.44%) foram
# CRAO transitoria; destes, 66.6% tinham obstrucao carotidea >=70%.
FRACAO_CRAO_TRANSITORIA = 18 / 4069
FRACAO_COM_OBSTRUCAO_CAROTIDEA = 0.666


def dPth_com_reserva_vascular(dPth_basal_mmHg: float, OPP_crit_ref_mmHg: float,
                               phi_vasc: float) -> float:
    """
    dPth(phi_vasc) = dPth_basal - OPP_crit_ref*(phi_vasc - 1)

    Consequencia direta de OPP_crit_efetivo = OPP_crit_ref*phi_vasc (4.1)
    dentro de dPth = mopp_factor*MAP - P0 - OPP_crit_efetivo: dPth_basal
    e o valor com phi_vasc=1 (sem reserva vascular reduzida); elevar
    phi_vasc eleva o limiar efetivo e reduz dPth na mesma proporcao.
    """
    if phi_vasc < 1.0:
        raise ValueError(f"phi_vasc deve ser >= 1.0, recebido {phi_vasc}")
    return dPth_basal_mmHg - OPP_crit_ref_mmHg * (phi_vasc - 1.0)


def subgrupo_risco_damasceno(
    K_tipico_mmHg_per_uL: float, K_alto_mmHg_per_uL: float,
    dV_uL: float, C_out_uL_min_mmHg: float,
    dPth_basal_mmHg: float, OPP_crit_ref_mmHg: float,
    phi_vasc_risco: float,
) -> dict:
    """
    Compara paciente TIPICO (K tipico, phi_vasc=1 -- sem comorbidade
    vascular) contra o subgrupo de risco de Damasceno et al. 2022 (K
    alto = olho curto/rigido, phi_vasc>1 = obstrucao carotidea
    significativa), no MESMO cenario basal (dPth_basal, OPP_crit_ref) --
    isola o efeito de K e phi_vasc, nao muda nenhum outro parametro.

    Espera-se (e e o que valida o modelo contra a observacao): tipico
    -> 𝓘=0 (consistente com OCT-A); subgrupo de risco -> 𝓘>0
    (consistente com a associacao observada entre obstrucao carotidea e
    CRAO transitoria pos-IVI).
    """
    dPth_tipico = dPth_basal_mmHg  # phi_vasc=1 por definicao
    dPth_risco = dPth_com_reserva_vascular(dPth_basal_mmHg, OPP_crit_ref_mmHg, phi_vasc_risco)

    if dPth_tipico <= 0:
        I_tipico = None
        status_tipico = "fora de dominio (dPth_basal<=0 -- cenario basal mal escolhido)"
    else:
        I_tipico = dose_fechada_H6(K_tipico_mmHg_per_uL, dV_uL, C_out_uL_min_mmHg, dPth_tipico)
        status_tipico = "OK"

    if dPth_risco <= 0:
        I_risco = None
        status_risco = "basal ja abaixo do limiar mesmo sem injecao (regime cronico, nao mais transitorio)"
    else:
        I_risco = dose_fechada_H6(K_alto_mmHg_per_uL, dV_uL, C_out_uL_min_mmHg, dPth_risco)
        status_risco = "OK"

    return {
        "dPth_tipico_mmHg": dPth_tipico, "I_tipico_mmHg_min": I_tipico, "status_tipico": status_tipico,
        "dPth_risco_mmHg": dPth_risco, "I_risco_mmHg_min": I_risco, "status_risco": status_risco,
        "K_tipico_mmHg_per_uL": K_tipico_mmHg_per_uL, "K_alto_mmHg_per_uL": K_alto_mmHg_per_uL,
        "phi_vasc_risco": phi_vasc_risco,
    }


# --- Peca 3: controle negativo (OCT ultra-precoce) -------------------------

def controle_negativo_afinamento_mecanico() -> dict:
    """
    Achado do OCT ultra-precoce (PMC13307848): afinamento retiniano de
    25% aos 15 min pos-IVI, resolvido em 48h, atribuido a compressao
    mecanica direta (nao isquemia).

    Este NAO e um calculo do modelo -- e uma verificacao conceitual,
    documentada em codigo para poder ser citada/testada como qualquer
    outro achado deste modulo. O modelo aqui (𝓘, MOPP, OPP_diast) vive
    inteiramente no espaco de PRESSAO DE PERFUSAO ao longo do tempo; ele
    nao tem nenhuma variavel de espessura retiniana ou deformacao
    mecanica direta do tecido -- entao ele estruturalmente NAO PODE
    atribuir esse afinamento a isquemia, porque isquemia (no modelo) so
    existe como deficit de OPP(t) abaixo de um limiar, e esse achado nao
    e reportado em termos de OPP. A funcao serve para deixar essa
    distincao explicita e citavel, nao para "calcular" nada nela.
    """
    return {
        "afinamento_percentual": 0.25,
        "tempo_pico_min": 15,
        "tempo_resolucao_h": 48,
        "mecanismo_atribuido": "compressao mecanica direta (nao isquemia)",
        "fonte": "PMC13307848",
        "compativel_com_dose_isquemica_do_modelo": False,
        "motivo": (
            "escala de tempo (15 min -> resolucao em 48h) e o tipo de "
            "variavel (espessura estrutural, nao pressao de perfusao) "
            "sao incompativeis com 𝓘 (integral de deficit de OPP), que "
            "so mede o que acontece na janela aguda de pressao, nao "
            "deformacao residual do tecido apos a pressao normalizar."
        ),
    }


if __name__ == "__main__":
    print("=== Peca 1: consistencia com o zero do OCT-A 2026 (n=54) ===")
    K_impl = K_implicito_do_pico_observado()
    print(f"  K implicito do pico observado (14->31 mmHg, dV=50uL) = {K_impl:.3f} mmHg/uL")
    print(f"  OPP_crit maximo consistente com zero = {opp_crit_maximo_consistente_com_zero():.1f} mmHg")
    print("  Tabela de consistencia:")
    for opp, veredito in tabela_consistencia_zero_oct_a().items():
        print(f"    OPP_crit={opp:5.1f}  {veredito}")

    print("\n=== Peca 2: subgrupo de risco de Damasceno et al. 2022 ===")
    print(f"  CRAO transitoria pos-IVI: {FRACAO_CRAO_TRANSITORIA*100:.2f}% das injecoes (18/4069)")
    print(f"  dos quais {FRACAO_COM_OBSTRUCAO_CAROTIDEA*100:.1f}% com obstrucao carotidea >=70%")
    r = subgrupo_risco_damasceno(
        K_tipico_mmHg_per_uL=K_impl, K_alto_mmHg_per_uL=1.0,
        dV_uL=50.0, C_out_uL_min_mmHg=0.28,
        dPth_basal_mmHg=20.0, OPP_crit_ref_mmHg=25.0, phi_vasc_risco=1.3,
    )
    print(f"  Tipico:  dPth={r['dPth_tipico_mmHg']:.1f}  I={r['I_tipico_mmHg_min']}")
    print(f"  Risco:   dPth={r['dPth_risco_mmHg']:.1f}  I={r['I_risco_mmHg_min']:.1f} mmHg.min")

    print("\n=== Peca 3: controle negativo (OCT ultra-precoce) ===")
    c = controle_negativo_afinamento_mecanico()
    print(f"  Afinamento {c['afinamento_percentual']*100:.0f}% aos {c['tempo_pico_min']} min, "
          f"resolvido em {c['tempo_resolucao_h']}h ({c['fonte']})")
    print(f"  Compativel com dose isquemica do modelo? {c['compativel_com_dose_isquemica_do_modelo']}")
