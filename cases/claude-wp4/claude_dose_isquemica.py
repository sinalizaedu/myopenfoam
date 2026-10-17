"""
claude_dose_isquemica.py
==========================

Item 4.2 do WP4: metrica de dose isquemica por evento unico (𝓘),
construida sobre o item 4.1 (claude_opp_perfusion.py) e sobre o solver 0D
do WP0 (goldmann_iop_solver.py). NAO edita nenhum dos dois.

O WP0 ja calcula uma dose isquemica (I_mmHg_min) via perfusion_metrics(),
usando SEMPRE MOPP como definicao de perfusao. Este modulo generaliza e
valida isso:

1. dose_isquemica(t, OPP_t, OPP_crit): integral generalizada, aplicavel a
   MOPP(t) OU OPP_diast(t) (ou qualquer serie de pressao de perfusao) --
   nao amarrada a MOPP como o WP0.

2. dose_isquemica_da_cadeia(): a partir do dict devolvido por
   cadeia_completa() do 4.1, calcula 𝓘 para as DUAS definicoes de
   perfusao (MOPP e OPP_diast) no mesmo OPP_crit_efetivo (ja ajustado por
   phi_vasc), e confere contra o I_mmHg_min que o WP0 ja devolve (devem
   ser identicos para a via MOPP -- checagem de consistencia).

3. curva_sensibilidade_opp_crit(): 𝓘 como funcao de uma faixa de
   OPP_crit_ref -- nunca reportar um numero so (exigencia do plano de
   tese, Secao 4.2/4.3).

4. validacao_fechada_H6(): compara o 𝓘 numerico (trapz sobre a saida do
   solver 0D, via MOPP) contra a formula fechada de H6 (Secao 1/4.3 do
   plano de tese):

       I = tau*[dP0 - dPth - dPth*ln(dP0/dPth)],  tau = 1/(C*K)

   valida para K CONSTANTE (ThinShellPV) e sem paracentese/refluxo --
   checagem de consistencia interna do proprio modelo, nao contra dado
   externo. Espera-se um erro pequeno e nao nulo por causa da duracao
   finita da injecao (a formula fechada assume bolus instantaneo; o
   solver usa uma rampa de 6 s) -- ver README para a magnitude medida.

Ancoras de literatura para escolher a faixa de OPP_crit (documentadas
aqui, NAO usadas como valor fixo no codigo):
  - Baltimore Eye Survey: DOPP < 30 mmHg -> risco ~6x (CRONICO)
    [Tielsch JM et al. Arch Ophthalmol 1995;113(2):216-221,
     PMID 7864755 -- estudo TRANSVERSAL de glaucoma cronico]
  - Barbados Eye Study:   MOPP < 40 mmHg -> RR 2,6 (CRONICO)
    [CORRIGIDO de "MOPP < 42 -> 3,1x": Leske et al. Ophthalmology
     2008;115(1):85-93 (PMID 17629563) reportam MOPP<40 com RR 2,6 e
     DOPP<53 com RR 2,2; o limiar de 42 nao foi confirmado]
  - CRAO completa humana: dano irreversivel em 12-15 min (revisao
    contestando Hayreh) -- este e um limiar de TEMPO, nao de OPP; nao
    entra diretamente na curva de sensibilidade de OPP_crit, mas
    contextualiza a escala de tempo em que a dose se acumula.
Nenhuma dessas ancoras foi medida no regime agudo transitorio pos-IVI --
sao pontos de referencia da literatura cronica/de oclusao completa, nao
uma calibracao direta.
"""

from __future__ import annotations

import os
import sys
from typing import Optional

import numpy as np

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_WP0_DIR = os.path.join(_THIS_DIR, "..", "wp0")
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)
if _WP0_DIR not in sys.path:
    sys.path.insert(0, _WP0_DIR)

import dataclasses

from goldmann_iop_solver import Protocol, simulate  # noqa: E402
from claude_opp_perfusion import cadeia_completa, opp_crit_efetivo  # noqa: E402

_trapz = getattr(np, "trapezoid", None) or np.trapz


def dose_isquemica(t_min: np.ndarray, OPP_t: np.ndarray, OPP_crit_mmHg: float) -> float:
    """
    𝓘 = integral( max(0, OPP_crit - OPP(t)) dt )   [mmHg.min]

    Generalizada: OPP_t pode ser MOPP(t) OU OPP_diast(t) (ou qualquer
    outra serie de pressao de perfusao) -- a formula nao depende de qual
    definicao foi usada para gerar OPP_t.
    """
    t = np.asarray(t_min, dtype=float)
    opp = np.asarray(OPP_t, dtype=float)
    if t.shape != opp.shape:
        raise ValueError("t_min e OPP_t precisam ter o mesmo formato")
    deficit = np.clip(OPP_crit_mmHg - opp, 0.0, None)
    return float(_trapz(deficit, t))


def dose_isquemica_da_cadeia(t_min: np.ndarray, chain: dict) -> dict:
    """
    A partir do dict devolvido por cadeia_completa() (item 4.1), calcula
    𝓘 para MOPP e para OPP_diast, no mesmo OPP_crit_efetivo (ja ajustado
    por phi_vasc).

    Inclui uma checagem de consistencia: I_MOPP deve ser identico ao
    I_mmHg_min que o proprio WP0 ja calculou dentro de cadeia_completa
    (mesma formula, mesmos dados -- nao pode divergir).
    """
    opp_crit_eff = chain["OPP_crit_efetivo_mmHg"]

    I_mopp = dose_isquemica(t_min, chain["MOPP"], opp_crit_eff)
    out = {
        "OPP_crit_efetivo_mmHg": opp_crit_eff,
        "I_MOPP_mmHg_min": I_mopp,
    }

    if chain.get("OPP_diast") is not None:
        out["I_OPP_diast_mmHg_min"] = dose_isquemica(t_min, chain["OPP_diast"], opp_crit_eff)
    else:
        out["I_OPP_diast_mmHg_min"] = None

    if "I_mmHg_min" in chain:
        out["I_MOPP_ja_no_WP0"] = chain["I_mmHg_min"]

    return out


def curva_sensibilidade_opp_crit(t_min: np.ndarray, OPP_t: np.ndarray,
                                  opp_crit_range=(20, 25, 30, 35, 40, 45, 50, 55, 60)) -> dict:
    """
    𝓘 como funcao de OPP_crit_ref -- generaliza ischemic_dose_curve() do
    WP0 (que so aceita IOP/MOPP) para qualquer serie de perfusao.

    Nunca reporte um unico valor de 𝓘 sem esta curva ao lado -- ver
    Secao 4.2/4.3 do plano de tese.
    """
    return {th: dose_isquemica(t_min, OPP_t, th) for th in opp_crit_range}


def derivar_P0_equilibrio(Pev_mmHg: float, Q_prod_uL_min: float,
                          C_out_uL_min_mmHg: float, frac_uveoscleral: float) -> float:
    """
    P0 = Pev + Q_prod*(1-frac_uveoscleral)/C_out

    Ponto de equilibrio de Goldmann (dV/dt=0, sem injecao) dado os
    QUATRO parametros de vazao, cada um com base na literatura.

    Esta e a forma CORRETA de obter um P0 fisicamente consistente:
    ancorar Q_prod, C_out, Pev e frac_uveoscleral em valores medidos
    independentemente (ex.: Goel et al. 2010 para humano: Q_prod=2.4,
    C_out=0.28, Pev=10, frac=0.20 -> P0=16.9 mmHg) e DERIVAR P0 --
    em vez de fixar um P0 "de literatura geral" (os 15 mmHg comumente
    citados) e forcar algum dos quatro parametros a se ajustar sem base
    propria (o que uma versao anterior deste modulo fazia, recalculando
    Q_prod=1.75 sem nenhuma citacao -- ver historico do arquivo).
    """
    return Pev_mmHg + Q_prod_uL_min * (1.0 - frac_uveoscleral) / C_out_uL_min_mmHg


# Parametros de literatura por especie, citados no relatorio WP0 (Tabela
# "Parametros de escoamento fisiologico por especie"). Fonte primaria:
# Goel et al. 2010 (humano); Fourman S & Fourman MB 1989 e Kiel &
# Kopczynski 2015 (coelho). CORRIGIDO: nao existe "Garner"; e o rotulo
# "anestesiado" so e verificado para a Pev (Kiel 2015), nao para a
# facilidade (Fourman 1989). Detalhe por parametro logo abaixo.
_PARAMS_LITERATURA = {
    "humano": dict(Q_prod_uL_min=2.4, C_out_uL_min_mmHg=0.28, Pev_mmHg=10.0, frac_uveoscleral=0.20),
    # PROVENANCIA (ver claude-REFERENCES-WP4.md):
    #  C_out=0.26  [VERIFICADO] Fourman S, Fourman MB. Curr Eye Res.
    #              1989;8(9):963-969. DOI 10.3109/02713688909082658.
    #              Tonografia 0,26+-0,07 E perfusao a pressao constante 0,26
    #              (os dois metodos concordam, r=0,914). NAO existe "Garner".
    #              Condicao anestesica NAO confirmada no resumo.
    #              O C_out=0,57 da lista de hedges do plano NAO TEM FONTE
    #              publicada e e reproduzivel do balanco de Goldmann -- parece
    #              derivado, nao medido. Coelho consciente e mais BAIXO ainda:
    #              0,10-0,20 (Zhao et al. IOVS 2010;51(6):3145-3151).
    #  Pev=15.5    [VERIFICADO] Kiel JW, Kopczynski CC. J Ocul Pharmacol Ther.
    #              2015;31(3):146-151. EVP 16+-1 mmHg, coelho anestesiado.
    #  Q_prod=3.06 [SEM FONTE] nenhuma fonte localizada. Fluxo publicado
    #              verificavel: 1,46-2,53 uL/min, coelho consciente (Zhao 2010).
    #              3,06 esta ACIMA da faixa medida. P0 derivado varia de 20,8
    #              (Q=1,46) a 26,7 mmHg (Q=3,06) -- ~6 mmHg de amplitude.
    #  frac_uv=0.05 [SECUNDARIO] plano de tese: 3-8% em coelho.
    #  ALERTA: mistura condicoes experimentais (Pev anestesiado + faixa de
    #  fluxo consciente + Fourman nao confirmado) num unico P0.
    "coelho_anestesiado": dict(Q_prod_uL_min=3.06, C_out_uL_min_mmHg=0.26, Pev_mmHg=15.5, frac_uveoscleral=0.05),
}


def protocolo_com_P0_literatura(especie: str = "humano", **overrides) -> Protocol:
    """
    Gera um Protocol cujo P0_mmHg e DERIVADO dos parametros de vazao com
    base na literatura (ver _PARAMS_LITERATURA e derivar_P0_equilibrio()),
    em vez de usar um P0 fixo desancorado desses parametros.

    Para especie="humano": Q_prod=2.4, C_out=0.28, Pev=10, frac=0.20
    -> P0=16.86 mmHg (~16.9, valor usado no relatorio WP0 em LaTeX).
    Para especie="coelho_anestesiado": -> P0=26.68 mmHg (~26.7).

    ACHADO desta sessao: o Protocol() padrao de goldmann_iop_solver.py
    usa P0_mmHg=15.0 com Q_prod=3.0 uL/min -- nem o P0 nem o Q_prod
    batem com os valores de literatura usados no relatorio WP0 (P0=16.9,
    Q_prod=2.4). Com os parametros DEFAULT do codigo (nao os desta
    funcao), o equilibrio real da ODE fica em ~18.57 mmHg, um vies de
    +3.57 mmHg que se manifesta com a MESMA constante de tempo (~18 min)
    da propria dinamica pos-injecao que o WP4 mede. Verificado por
    simulacao direta (Protocol(V_inj_uL=0, t_end_min=100)): IOP diverge
    de 15 para 18.57 mmHg mesmo sem nenhuma injecao.

    Isto NAO e um erro deste modulo -- e uma inconsistencia dos
    PARAMETROS PADRAO de goldmann_iop_solver.Protocol(), que este modulo
    nao edita (restricao do projeto). Recomendacao: reconciliar
    Protocol() com os valores do relatorio WP0 (Q_prod=2.4 em vez de
    3.0, P0=16.9 em vez de 15.0) diretamente no arquivo oficial --
    decisao de quem mantem esse arquivo, nao deste modulo.

    overrides substitui qualquer parametro de _PARAMS_LITERATURA ou
    qualquer outro kwarg de Protocol antes de derivar P0 (ex.: passe
    V_inj_uL=100.0 para replicar Chang&Chung 2007).
    """
    if especie not in _PARAMS_LITERATURA:
        raise ValueError(f"especie desconhecida: {especie!r}. Use uma de {list(_PARAMS_LITERATURA)}")

    params = dict(_PARAMS_LITERATURA[especie])
    # overrides podem mudar Q_prod/C_out/Pev/frac (recalcula P0) ou so
    # passar adiante outros kwargs de Protocol (ex.: V_inj_uL, t_end_min)
    fluxo_keys = ("Q_prod_uL_min", "C_out_uL_min_mmHg", "Pev_mmHg", "frac_uveoscleral")
    outros_kwargs = {}
    for k, v in overrides.items():
        if k in fluxo_keys:
            params[k] = v
        else:
            outros_kwargs[k] = v

    P0 = derivar_P0_equilibrio(params["Pev_mmHg"], params["Q_prod_uL_min"],
                               params["C_out_uL_min_mmHg"], params["frac_uveoscleral"])

    return Protocol(
        P0_mmHg=P0,
        Pev_mmHg=params["Pev_mmHg"],
        Q_prod_uL_min=params["Q_prod_uL_min"],
        C_out_uL_min_mmHg=params["C_out_uL_min_mmHg"],
        frac_uveoscleral=params["frac_uveoscleral"],
        **outros_kwargs,
    )


def validacao_fechada_H6(proto: Protocol, pv, OPP_crit_ref_mmHg: float,
                          mopp_factor: float = 2.0 / 3.0,
                          phi_vasc: float = 1.0) -> dict:
    """
    Compara o 𝓘 numerico (via MOPP, saida do solver 0D) contra a formula
    fechada de H6 (Secao 1/4.3 do plano de tese):

        dP0 = K * dV                          (pico de elevacao de IOP)
        tau = 1 / (C_out * K)                 (constante de tempo)
        dPth = mopp_factor*MAP - P0 - OPP_crit_efetivo
        I_fechado = 0                                     se dP0 <= dPth
                  = tau*(dP0 - dPth - dPth*ln(dP0/dPth))   se dP0 >  dPth

    So valida para K CONSTANTE (requer pv.K_mmHg_per_uL, ou seja,
    ThinShellPV) e com refluxo/paracentese desligados -- a formula
    fechada assume um unico compartimento linear.

    IMPORTANTE: so valida para dP_th > 0, isto e, quando a MOPP basal
    (sem injecao) ja esta ACIMA de OPP_crit_efetivo -- a formula fechada
    de H6 assume threshold acima do basal (ver Secao 1 do plano de
    tese). Se a MOPP basal ja estiver abaixo de OPP_crit_efetivo (dP_th
    <= 0), a formula fechada nao se aplica (levanta ValueError em vez de
    devolver NaN silenciosamente, que e o que acontecia numa versao
    anterior deste modulo).

    Use protocolo_com_P0_literatura() para gerar um proto cujo P0 seja
    de fato o equilibrio da ODE, derivado de parametros de vazao com
    base na literatura -- ver o docstring dessa funcao para o porque
    isso e necessario com os parametros default do WP0.

    Retorna dict com I_numerico, I_fechado, erro_relativo (ou erro
    absoluto se I_fechado==0), e os parametros intermediarios (dP0, dPth,
    tau) para auditoria.
    """
    if not hasattr(pv, "K_mmHg_per_uL"):
        raise ValueError(
            "validacao_fechada_H6 requer uma PV com K constante "
            "(ThinShellPV) -- a formula fechada de H6 nao vale para "
            "P(V) nao-linear (ex.: FriedenwaldPV)."
        )
    if proto.reflux_enabled or proto.par_enabled:
        raise ValueError(
            "validacao_fechada_H6 requer refluxo e paracentese "
            "desligados (proto.reflux_enabled=False, proto.par_enabled=False) "
            "-- a formula fechada de H6 nao inclui esses termos."
        )

    K = pv.K_mmHg_per_uL
    C = proto.C_out_uL_min_mmHg
    dV = proto.V_inj_uL
    tau = 1.0 / (C * K)

    MAP = proto.DBP_mmHg + (proto.SBP_mmHg - proto.DBP_mmHg) / 3.0
    opp_crit_eff = opp_crit_efetivo(OPP_crit_ref_mmHg, phi_vasc)
    dP_th = mopp_factor * MAP - proto.P0_mmHg - opp_crit_eff
    dP_0 = K * dV

    if dP_th <= 0:
        raise ValueError(
            f"dP_th={dP_th:.2f} <= 0: a MOPP basal ja esta abaixo de "
            f"OPP_crit_efetivo ({opp_crit_eff:.1f} mmHg) mesmo sem "
            "injecao -- a formula fechada de H6 nao se aplica neste "
            "regime. Verifique se proto.P0_mmHg e de fato o equilibrio "
            "da ODE (ver protocolo_com_P0_literatura()) e/ou reduza "
            "OPP_crit_ref_mmHg."
        )

    if dP_0 <= dP_th:
        I_fechado = 0.0
    else:
        I_fechado = tau * (dP_0 - dP_th - dP_th * np.log(dP_0 / dP_th))

    t, V, P = simulate(proto, pv)
    chain = cadeia_completa(t, P, proto, OPP_crit_ref_mmHg=OPP_crit_ref_mmHg,
                             mopp_factor=mopp_factor, phi_vasc=phi_vasc)
    I_numerico = chain["I_mmHg_min"]

    if I_fechado > 0:
        erro_rel = abs(I_numerico - I_fechado) / I_fechado
    else:
        erro_rel = abs(I_numerico - I_fechado)

    return {
        "I_numerico_mmHg_min": I_numerico,
        "I_fechado_mmHg_min": I_fechado,
        "erro_relativo": erro_rel,
        "dP_0_mmHg": dP_0,
        "dP_th_mmHg": dP_th,
        "tau_min": tau,
        "K_mmHg_per_uL": K,
    }


if __name__ == "__main__":
    from goldmann_iop_solver import ThinShellPV

    proto = Protocol()
    pv = ThinShellPV(R_m=0.012, t_m=0.6e-3, E_Pa=3e6, P0_mmHg=proto.P0_mmHg)
    t, V, P = simulate(proto, pv)

    # OPP_crit = 50 mmHg vem da epidemiologia de glaucoma CRONICO (Leske 2009).
    # Com a MOPP basal destas condicoes (~41 mmHg), esse limiar classifica o
    # repouso como ja deficitario — ver claude-AUDITORIA-WP4-5-6.md, Parte 1.
    # A literatura aguda aponta ~30 mmHg. As duas sao mostradas abaixo.
    chain = cadeia_completa(t, P, proto, OPP_crit_ref_mmHg=50.0, phi_vasc=1.0)
    chain30 = cadeia_completa(t, P, proto, OPP_crit_ref_mmHg=30.0, phi_vasc=1.0)
    MAP_ref = proto.DBP_mmHg + (proto.SBP_mmHg - proto.DBP_mmHg) / 3.0
    print(f"MOPP basal = (2/3)x{MAP_ref:.1f} - {proto.P0_mmHg:.2f} = "
          f"{(2/3)*MAP_ref - proto.P0_mmHg:.2f} mmHg")

    print("=== 4.2: dose isquemica por evento (MOPP vs OPP_diast) ===")
    d = dose_isquemica_da_cadeia(t, chain)
    print(f"  I via MOPP        = {d['I_MOPP_mmHg_min']:.2f} mmHg.min")
    print(f"  I via MOPP (WP0)  = {d['I_MOPP_ja_no_WP0']:.2f} mmHg.min  (deve ser igual acima)")
    I_diast = d["I_OPP_diast_mmHg_min"]
    if I_diast is None:
        print("  I via OPP_diast   = indisponivel "
              "(PAD oftalmica nao informada; ver estimar_PAD_oftalmica em "
              "claude_opp_perfusion.cadeia_completa)")
    else:
        print(f"  I via OPP_diast   = {I_diast:.2f} mmHg.min")

    d30 = dose_isquemica_da_cadeia(t, chain30)
    print(f"  I via MOPP, OPP_crit=30   = {d30['I_MOPP_mmHg_min']:.2f} mmHg.min "
          f"(limiar do regime AGUDO)")

    print("\n=== Curva de sensibilidade a OPP_crit (via MOPP) ===")
    print("  ATENCAO: Protocol() default usa P0=15,0 com Q_prod=3,0, cujo")
    print("  equilibrio real e 18,57 mmHg -- a IOP DERIVA para cima sem injecao")
    print("  nenhuma, e a MOPP cai ~3,6 mmHg na janela. Qualquer limiar acima de")
    print("  ~39 mmHg captura essa deriva em vez do pico. Por isso as duas curvas:")
    proto_der = protocolo_com_P0_literatura("humano", t_end_min=proto.t_end_min)
    pv_der = ThinShellPV(R_m=0.012, t_m=0.6e-3, E_Pa=3e6, P0_mmHg=proto_der.P0_mmHg)
    t_der, _Vd, P_der = simulate(proto_der, pv_der)
    chain_der = cadeia_completa(t_der, P_der, proto_der, OPP_crit_ref_mmHg=50.0)
    c_def = curva_sensibilidade_opp_crit(t, chain["MOPP"])
    c_der = curva_sensibilidade_opp_crit(t_der, chain_der["MOPP"])
    MAPd = proto_der.DBP_mmHg + (proto_der.SBP_mmHg - proto_der.DBP_mmHg) / 3.0
    print(f"\n  P0 default={proto.P0_mmHg:.2f} (MOPP basal "
          f"{(2/3)*MAP_ref - proto.P0_mmHg:.2f}, IOP deriva p/ 18,57)")
    print(f"  P0 derivado={proto_der.P0_mmHg:.2f} (MOPP basal "
          f"{(2/3)*MAPd - proto_der.P0_mmHg:.2f}, sem deriva)")
    print(f"\n  {'OPP_crit':>9} {'I (P0 default)':>15} {'I (P0 derivado)':>16} {'dI/dOPP_crit':>13}")
    ths = sorted(c_der)
    for i, th in enumerate(ths):
        slope = ""
        if i > 0:
            dI = c_der[th] - c_der[ths[i-1]]
            slope = f"{dI/(th-ths[i-1]):.1f}"
        print(f"  {th:9.1f} {c_def[th]:15.2f} {c_der[th]:16.2f} {slope:>13}")
    print(f"\n  Janela de integracao T = {proto_der.t_end_min:.0f} min. Quando a")
    print("  inclinacao dI/dOPP_crit se aproxima de T, o limiar passou do maximo")
    print("  da MOPP e a dose mede a janela, nao o evento -- regime degenerado.")

    print("\n=== Validacao fechada contra H6 (P0 derivado da literatura, humano) ===")
    proto_ok = protocolo_com_P0_literatura("humano")
    print(f"  Q_prod (Goel et al. 2010) = {proto_ok.Q_prod_uL_min} uL/min "
          f"(vs {Protocol().Q_prod_uL_min} no Protocol() default)")
    print(f"  P0 derivado = {proto_ok.P0_mmHg:.2f} mmHg "
          f"(vs {Protocol().P0_mmHg} no Protocol() default -- relatorio WP0 usa 16.9)")
    pv_ok = ThinShellPV(R_m=0.012, t_m=0.6e-3, E_Pa=3e6, P0_mmHg=proto_ok.P0_mmHg)
    v = validacao_fechada_H6(proto_ok, pv_ok, OPP_crit_ref_mmHg=38.0)
    print(f"  I numerico   = {v['I_numerico_mmHg_min']:.3f} mmHg.min")
    print(f"  I fechado    = {v['I_fechado_mmHg_min']:.3f} mmHg.min")
    print(f"  erro relativo= {v['erro_relativo']*100:.2f} %  (residual esperado: rampa de injecao de 6s vs bolus instantaneo)")
