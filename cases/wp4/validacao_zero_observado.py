"""WP4.4 — validação teórica contra o zero observado na literatura.

Construído sobre o 4.3 (``h6_teorico.dose_fechada_H6``) e o 4.1
(``opp_perfusion.opp_crit_efetivo``). Objetivo (citação do plano):
"mostrar que o modelo reproduz corretamente a ausência de déficit
perfusional relatada na literatura para injeção única, e delimitar a
região paramétrica onde essa previsão deixaria de valer."

Etapa INTEIRAMENTE COMPUTACIONAL — literatura publicada vs modelo 0D,
sem dado próprio e sem rodar o solver (tudo em primitivos dPth/K/ΔV).

Três peças:
  1. OCT-A 2026 (n=54): pico de IOP 14→31 mmHg, MOPP≈31 mmHg relatado
     durante o evento, SEM déficit de perfusão mensurável → para que faixa
     de OPP_crit o modelo também prediz zero?
  2. Damasceno et al. 2022: CRAO transitória pós-IVI em 0,44% das injeções
     (18/4069); destes, 66,6% com obstrução carotídea ≥70% → o modelo deve
     prever 𝓘>0 nesse subgrupo (K alto + phi_vasc>1) mesmo quando o
     paciente típico tem 𝓘=0 no MESMO cenário basal.
  3. Controle negativo: afinamento retiniano de 25% aos 15 min pós-IVI
     (PMC13307848), resolvido em 48 h, atribuído a compressão mecânica —
     o modelo não pode confundir isso com isquemia (vive no espaço de
     pressão de perfusão, não de espessura retiniana).
"""
from __future__ import annotations

import sys
from pathlib import Path

WP4 = Path(__file__).resolve().parent
if str(WP4) not in sys.path:
    sys.path.insert(0, str(WP4))

from h6_teorico import dose_fechada_H6  # noqa: E402
from opp_perfusion import opp_crit_efetivo  # noqa: E402

# --- Peça 1: OCT-A 2026 (n=54) ---------------------------------------------
IOP_BASAL_OCT_A_MMHG = 14.0
IOP_PICO_OCT_A_MMHG = 31.0
# MOPP mínima RELATADA DIRETAMENTE pelo estudo durante o evento — não
# recalculada de MAP populacional (o estudo tem seu próprio MAP de coorte).
MOPP_MIN_OBSERVADO_OCT_A_MMHG = 31.0
N_OLHOS_OCT_A = 54
DV_TIPICO_UL = 50.0


def K_implicito_do_pico_observado(
    iop_basal_mmHg: float = IOP_BASAL_OCT_A_MMHG,
    iop_pico_mmHg: float = IOP_PICO_OCT_A_MMHG,
    dV_uL: float = DV_TIPICO_UL,
) -> float:
    """K implícito = (pico − basal)/ΔV [mmHg/µL].

    NÃO é um K medido independentemente — é uma leitura do próprio dado do
    OCT-A assumindo ΔV=50 µL típico. Âncora de ordem de grandeza para
    "K típico de população", não substituto do emulador do WP1.4 (que usa
    biometria real).
    """
    return (iop_pico_mmHg - iop_basal_mmHg) / dV_uL


def opp_crit_maximo_consistente_com_zero(
    MOPP_min_observado_mmHg: float = MOPP_MIN_OBSERVADO_OCT_A_MMHG,
) -> float:
    """O modelo prediz 𝓘=0 sse OPP_crit ≤ MOPP_min observado (nenhum instante
    cruza o limiar). Devolve explicitamente esse teto (= o próprio MOPP_min)
    para não deixar a conclusão implícita no meio de uma tabela."""
    return MOPP_min_observado_mmHg


def tabela_consistencia_zero_oct_a(
    OPP_crit_range=(15, 20, 25, 30, 31, 35, 40, 45, 50),
    MOPP_min_observado_mmHg: float = MOPP_MIN_OBSERVADO_OCT_A_MMHG,
) -> dict:
    """Para cada OPP_crit candidato (parâmetro incerto — alerta metodológico
    do plano), diz se o modelo prediz "zero" (consistente com o OCT-A) ou
    "deficit>0" (inconsistente — exigiria revisar a hipótese de que o limiar
    crônico ~50 mmHg vale para eventos transitórios).

    A comparação é contra o MOPP_min OBSERVADO (dado da literatura), não
    contra um MOPP_min recalculado de MAP populacional.
    """
    out = {}
    for opp in OPP_crit_range:
        opp = float(opp)
        out[opp] = (
            "zero (consistente com OCT-A)"
            if opp <= MOPP_min_observado_mmHg
            else "deficit>0 (inconsistente com OCT-A)"
        )
    return out


# --- Peça 2: subgrupo de risco de Damasceno et al. 2022 ---------------------
FRACAO_CRAO_TRANSITORIA = 18 / 4069          # 0,44% das injeções
FRACAO_COM_OBSTRUCAO_CAROTIDEA = 0.666       # dos casos de CRAO transitória


def dPth_com_reserva_vascular(
    dPth_basal_mmHg: float,
    OPP_crit_ref_mmHg: float,
    phi_vasc: float,
) -> float:
    """dPth(phi) = dPth_basal − OPP_crit_ref·(phi − 1).

    Consequência direta de OPP_crit_efetivo = OPP_crit_ref·phi_vasc (4.1)
    dentro de dPth = f·MAP − P0 − OPP_crit_efetivo: elevar phi eleva o
    limiar efetivo e reduz dPth na mesma proporção.
    """
    if phi_vasc < 1.0:
        raise ValueError(f"phi_vasc deve ser >= 1.0, recebido {phi_vasc}")
    return dPth_basal_mmHg - OPP_crit_ref_mmHg * (phi_vasc - 1.0)


def subgrupo_risco_damasceno(
    K_tipico_mmHg_per_uL: float,
    K_alto_mmHg_per_uL: float,
    dV_uL: float,
    C_out_uL_min_mmHg: float,
    dPth_basal_mmHg: float,
    OPP_crit_ref_mmHg: float,
    phi_vasc_risco: float,
) -> dict:
    """Paciente TÍPICO (K típico, phi=1) vs subgrupo de risco de Damasceno
    (K alto = olho curto/rígido, phi>1 = obstrução carotídea), no MESMO
    cenário basal — isola o efeito de K e phi_vasc.

    Se dPth do subgrupo cair ≤ 0, marca "regime cronico" (a fórmula de H6
    não se aplica — basal já abaixo do limiar sem injeção) em vez de
    levantar ValueError.
    """
    dPth_tipico = dPth_basal_mmHg  # phi_vasc=1 por definição
    dPth_risco = dPth_com_reserva_vascular(dPth_basal_mmHg, OPP_crit_ref_mmHg, phi_vasc_risco)

    if dPth_tipico <= 0:
        I_tipico, status_tipico = None, "fora de dominio (dPth_basal<=0 — cenario basal mal escolhido)"
    else:
        I_tipico = dose_fechada_H6(K_tipico_mmHg_per_uL, dV_uL, C_out_uL_min_mmHg, dPth_tipico)
        status_tipico = "OK"

    if dPth_risco <= 0:
        I_risco = None
        status_risco = "regime cronico (basal ja abaixo do limiar mesmo sem injecao)"
    else:
        I_risco = dose_fechada_H6(K_alto_mmHg_per_uL, dV_uL, C_out_uL_min_mmHg, dPth_risco)
        status_risco = "OK"

    return {
        "dPth_tipico_mmHg": dPth_tipico,
        "I_tipico_mmHg_min": I_tipico,
        "status_tipico": status_tipico,
        "dPth_risco_mmHg": dPth_risco,
        "I_risco_mmHg_min": I_risco,
        "status_risco": status_risco,
        "K_tipico_mmHg_per_uL": K_tipico_mmHg_per_uL,
        "K_alto_mmHg_per_uL": K_alto_mmHg_per_uL,
        "phi_vasc_risco": phi_vasc_risco,
    }


# --- Peça 3: controle negativo (OCT ultra-precoce) --------------------------
def controle_negativo_afinamento_mecanico() -> dict:
    """Afinamento retiniano de 25% aos 15 min pós-IVI, resolvido em 48 h,
    atribuído a compressão mecânica direta (PMC13307848) — NÃO isquemia.

    Verificação conceitual documentada em código (citável/testável): o
    modelo (𝓘, MOPP, OPP_diast) vive no espaço de PRESSÃO DE PERFUSÃO ao
    longo do tempo; não tem variável de espessura retiniana nem de
    deformação mecânica — portanto estruturalmente NÃO PODE atribuir esse
    afinamento a isquemia, que no modelo só existe como déficit de OPP(t)
    abaixo de um limiar.
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
            "variavel (espessura estrutural, nao pressao de perfusao) sao "
            "incompativeis com 𝓘 (integral de deficit de OPP), que so mede "
            "o que acontece na janela aguda de pressao, nao deformacao "
            "residual do tecido apos a pressao normalizar."
        ),
    }


if __name__ == "__main__":
    print("=== Peça 1: consistência com o zero do OCT-A 2026 (n=54) ===")
    K_impl = K_implicito_do_pico_observado()
    print(f"  K implícito do pico observado (14→31 mmHg, ΔV=50 µL) = {K_impl:.3f} mmHg/uL")
    print(f"  OPP_crit máximo consistente com zero = {opp_crit_maximo_consistente_com_zero():.1f} mmHg")
    for opp, veredito in tabela_consistencia_zero_oct_a().items():
        print(f"    OPP_crit={opp:5.1f}  {veredito}")

    print("\n=== Peça 2: subgrupo de risco de Damasceno et al. 2022 ===")
    print(f"  CRAO transitória pós-IVI: {FRACAO_CRAO_TRANSITORIA * 100:.2f}% das injeções (18/4069)")
    print(f"  dos quais {FRACAO_COM_OBSTRUCAO_CAROTIDEA * 100:.1f}% com obstrução carotídea ≥70%")
    r = subgrupo_risco_damasceno(
        K_tipico_mmHg_per_uL=K_impl, K_alto_mmHg_per_uL=1.0,
        dV_uL=50.0, C_out_uL_min_mmHg=0.28,
        dPth_basal_mmHg=20.0, OPP_crit_ref_mmHg=25.0, phi_vasc_risco=1.3,
    )
    print(f"  Típico: dPth={r['dPth_tipico_mmHg']:.1f}  I={r['I_tipico_mmHg_min']}")
    print(f"  Risco:  dPth={r['dPth_risco_mmHg']:.1f}  I={r['I_risco_mmHg_min']:.1f} mmHg.min")

    print("\n=== Peça 3: controle negativo (OCT ultra-precoce) ===")
    c = controle_negativo_afinamento_mecanico()
    print(f"  Afinamento {c['afinamento_percentual'] * 100:.0f}% aos {c['tempo_pico_min']} min, "
          f"resolvido em {c['tempo_resolucao_h']}h ({c['fonte']})")
    print(f"  Compatível com dose isquêmica do modelo? {c['compativel_com_dose_isquemica_do_modelo']}")
