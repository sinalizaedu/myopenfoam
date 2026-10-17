#!/usr/bin/env python3
"""WP4 — correcoes dos defeitos apontados em claude-REVISAO-WP4.md.

Modulo autocontido (so numpy). Cada funcao aqui substitui uma do pipeline oficial
em cases/wp4/, que NAO foi alterado. As referencias completas estao em
claude-REFERENCES-WP4.md.

O que esta corrigido:

  1. tempo_acima_interpolado        <- substitui opp_perfusion._tempo_iop_acima
     O original integra um indicador binario por trapezio, o que devolve
     (nº de amostras acima) x dt em vez do tempo real acima. Inofensivo no grid
     do solver (dt=0,01 min), mas erra por minutos no grid clinico do WP3
     (6 pontos: imediato, 2, 5, 10, 15, 30 min). Aqui os cruzamentos sao
     interpolados linearmente — exato para dado linear por partes.

  2. dose_isquemica_exata           <- substitui dose_isquemica.dose_isquemica
     Mesmo problema: trapezio sobre o deficit recortado subestima quando o
     cruzamento cai dentro de um intervalo. Aqui a parte positiva de cada
     segmento e integrada analiticamente.

  3. dano_acumulado_com_estado      <- substitui dose_cumulativa.dose_cumulativa
     O original desconta cada evento pelo intervalo imediatamente anterior, sem
     variavel de estado: cresce linearmente em N e NUNCA satura, o que nao e o
     que "recuperacao parcial" significa. Aqui o dano e um estado que decai entre
     eventos e satura em I/(1-exp(-a.dt)).

  4. curva_sensibilidade_fator_braquial  <- NAO EXISTIA
     O plano exige: "O fator 2/3 aproxima a queda de pressao da braquial ate a
     arteria oftalmica. Declare como suposicao e faca analise de sensibilidade em
     0,5-0,8." Havia varredura para OPP_crit, nenhuma para este fator.

  5. PARAMS_LITERATURA_V2           <- substitui dose_isquemica._PARAMS_LITERATURA
     Provenancia por parametro: fonte, condicao experimental (consciente /
     anestesiado / nao confirmada) e etiqueta de confianca, como o plano exige.
     Corrige a atribuicao "Fourman & Garner" (nao existe Garner) e marca como
     SEM FONTE o Q_prod=3,06 do coelho e o C_out=0,57 do plano.

  6. REGIMES_ANTIVEGF               <- substitui dose_cumulativa.REGIMES_PLANO
     Os regimes nao vem do plano (que nao tem Secao 4.5). Fontes primarias reais,
     e o treat-and-extend corrigido de "12 a cada 10 semanas" para a faixa medida.

Uso:
    docker compose run --rm fsi bash -lc \
      'pip install numpy --break-system-packages && \
       cd /simulation/claude-wp4 && python3 claude_wp4_fixes.py'
"""
from __future__ import annotations

import math

import numpy as np

# numpy 1.26 (container) nao tem np.trapezoid, que e 2.0+
_trapz = getattr(np, "trapezoid", None) or np.trapz

# =============================================================================
# 1 e 2 — estimadores exatos para dado linear por partes
# =============================================================================


def tempo_acima_interpolado(
    t_min: np.ndarray, y: np.ndarray, limiar: float
) -> float:
    """Tempo com y(t) > limiar, interpolando os cruzamentos [min].

    Exato quando y e linear por partes entre as amostras (que e a hipotese
    implicita de qualquer integracao trapezoidal). O original
    (``trapz`` de um indicador binario) devolve dt x (nº de amostras acima),
    com vies de ate um intervalo de amostragem.
    """
    t = np.asarray(t_min, dtype=float)
    v = np.asarray(y, dtype=float)
    if t.shape != v.shape:
        raise ValueError("t_min e y precisam ter o mesmo formato")
    if t.size < 2:
        return 0.0

    total = 0.0
    for i in range(len(t) - 1):
        t0, t1 = t[i], t[i + 1]
        y0, y1 = v[i] - limiar, v[i + 1] - limiar
        dt = t1 - t0
        if dt <= 0:
            continue
        if y0 > 0 and y1 > 0:
            total += dt
        elif y0 <= 0 and y1 <= 0:
            continue
        elif y0 <= 0 < y1:
            frac = (-y0) / (y1 - y0)       # fracao do segmento abaixo do limiar
            total += (1.0 - frac) * dt
        else:                               # y0 > 0 >= y1
            frac = y0 / (y0 - y1)          # fracao do segmento acima do limiar
            total += frac * dt
    return float(total)


def dose_isquemica_exata(
    t_min: np.ndarray, OPP_t: np.ndarray, OPP_crit_mmHg: float
) -> float:
    """I = integral de max(0, OPP_crit - OPP(t)) dt [mmHg.min], exata para
    OPP linear por partes — integra analiticamente a parte positiva de cada
    segmento, inclusive quando o cruzamento cai no meio do intervalo."""
    t = np.asarray(t_min, dtype=float)
    opp = np.asarray(OPP_t, dtype=float)
    if t.shape != opp.shape:
        raise ValueError("t_min e OPP_t precisam ter o mesmo formato")
    if t.size < 2:
        return 0.0

    total = 0.0
    for i in range(len(t) - 1):
        dt = t[i + 1] - t[i]
        if dt <= 0:
            continue
        d0 = OPP_crit_mmHg - opp[i]
        d1 = OPP_crit_mmHg - opp[i + 1]
        if d0 >= 0 and d1 >= 0:
            total += 0.5 * (d0 + d1) * dt
        elif d0 <= 0 and d1 <= 0:
            continue
        elif d0 > 0 > d1:
            frac = d0 / (d0 - d1)
            total += 0.5 * d0 * frac * dt
        else:                               # d0 < 0 < d1
            frac = (-d0) / (d1 - d0)
            total += 0.5 * d1 * (1.0 - frac) * dt
    return float(total)


def diagnostico_resolucao(t_min: np.ndarray, tau_min: float | None = None) -> dict:
    """Reporta a resolucao do grid, sem limiar arbitrario de aprovacao.

    Serve para o usuario julgar se o grid resolve o transiente: num grid
    clinico de 6 pontos em 30 min, dt_max = 15 min contra tau de poucos
    minutos, e qualquer integral temporal fica dominada pela interpolacao.
    """
    t = np.asarray(t_min, dtype=float)
    dts = np.diff(t)
    out = {
        "n_pontos": int(t.size),
        "dt_min_min": float(dts.min()) if dts.size else None,
        "dt_max_min": float(dts.max()) if dts.size else None,
        "janela_min": float(t[-1] - t[0]) if t.size > 1 else 0.0,
    }
    if tau_min:
        out["tau_min"] = float(tau_min)
        out["dt_max_sobre_tau"] = float(dts.max() / tau_min) if dts.size else None
    return out


# =============================================================================
# 3 — modelo de dano com estado (satura), em vez de desconto por evento
# =============================================================================


def dano_acumulado_com_estado(
    I_por_evento_mmHg_min,
    intervalos_min,
    a_per_min: float | None = None,
) -> dict:
    """Dano como variavel de estado: D_j = D_{j-1}.exp(-a.dt_j) + I_j.

    Diferenca em relacao ao original: o original calcula
    sum_j I_j.w(dt_j), em que cada evento e descontado apenas pelo intervalo
    anterior. Sem estado, I_cum = I.[1 + (N-1).w] cresce LINEARMENTE em N e nunca
    satura. Com estado, o dano satura em

        D_inf = I / (1 - exp(-a.dt))     (I e dt constantes)

    que e o que "recuperacao parcial" significa fisicamente. Para o regime mensal
    com meia-vida de 4 semanas (exp(-a.dt)=0,5), D_inf = 2.I — e nao 12,5.I.

    a_per_min=None e acumulacao perfeita (nenhuma recuperacao): D_N = N.I.
    """
    I_arr = np.asarray(I_por_evento_mmHg_min, dtype=float)
    N = len(I_arr)
    if N == 0:
        raise ValueError("I_por_evento_mmHg_min nao pode ser vazio")
    intervalos = list(intervalos_min)
    if len(intervalos) != N - 1:
        raise ValueError(f"intervalos_min deve ter N-1={N - 1} elementos")
    if a_per_min is not None and a_per_min <= 0:
        raise ValueError(f"a_per_min deve ser > 0, recebido {a_per_min}")

    D = 0.0
    estados = []
    for j in range(N):
        if j > 0:
            decaimento = 1.0 if a_per_min is None else math.exp(-a_per_min * intervalos[j - 1])
            D = D * decaimento
        D = D + I_arr[j]
        estados.append(D)

    out = {
        "D_apos_cada_evento_mmHg_min": [float(d) for d in estados],
        "D_final_mmHg_min": float(estados[-1]),
        "D_maximo_mmHg_min": float(max(estados)),
        "N": N,
    }
    # estado estacionario analitico, quando I e dt sao constantes
    if a_per_min is not None and N > 1:
        dts = np.asarray(intervalos, dtype=float)
        if np.allclose(dts, dts[0]) and np.allclose(I_arr, I_arr[0]):
            r = math.exp(-a_per_min * float(dts[0]))
            out["D_infinito_mmHg_min"] = float(I_arr[0] / (1.0 - r)) if r < 1 else None
            out["fracao_do_estacionario"] = (
                float(estados[-1] / out["D_infinito_mmHg_min"])
                if out.get("D_infinito_mmHg_min")
                else None
            )
    return out


# =============================================================================
# 4 — sensibilidade ao fator braquial-oftalmica (exigida pelo plano)
# =============================================================================


def curva_sensibilidade_fator_braquial(
    t_min: np.ndarray,
    iop_mmHg: np.ndarray,
    pas: float,
    pad: float,
    OPP_crit_mmHg: float,
    fatores=(0.50, 0.55, 0.60, 2.0 / 3.0, 0.70, 0.75, 0.80),
) -> dict:
    """I(fator braquial-oftalmica) na faixa 0,5-0,8 que o plano manda varrer.

    MOPP = fator.MAP - IOP, com MAP = PAD + (PAS - PAD)/3. O fator e convencao
    da literatura de glaucoma, nao medida por paciente — e a dose isquemica e
    muito sensivel a ele, porque desloca a MOPP inteira verticalmente.
    """
    t = np.asarray(t_min, dtype=float)
    iop = np.asarray(iop_mmHg, dtype=float)
    MAP = pad + (pas - pad) / 3.0
    out = {}
    for f in fatores:
        mopp = f * MAP - iop
        out[round(float(f), 4)] = {
            "MOPP_min_mmHg": float(np.min(mopp)),
            "I_mmHg_min": dose_isquemica_exata(t, mopp, OPP_crit_mmHg),
        }
    return out


# =============================================================================
# 5 — parametros de vazao com provenancia por parametro
# =============================================================================

# Etiquetas de confianca exigidas pelo plano (Secao 2.3):
#   "V"  verificado na fonte primaria
#   "V2" verificado em fonte secundaria, confirmar no primario
#   "NF" nao encontrado / sem fonte publicada
PARAMS_LITERATURA_V2 = {
    "humano": {
        "Q_prod_uL_min": {"valor": 2.4, "conf": "V2", "condicao": "acordado",
                          "fonte": "plano de tese (lista de hedges); confirmar primario"},
        "C_out_uL_min_mmHg": {"valor": 0.28, "conf": "V2", "condicao": "acordado",
                              "fonte": "plano de tese (hedges): C_out humano ~0,28"},
        "Pev_mmHg": {"valor": 10.0, "conf": "V2", "condicao": "acordado",
                     "fonte": "plano de tese; Ruffini et al. 2024 usa P_epv=8"},
        "frac_uveoscleral": {"valor": 0.20, "conf": "V2", "condicao": "acordado",
                             "fonte": "Goel et al. 2010 (citado no plano)"},
    },
    "coelho": {
        # Fourman S, Fourman MB. Curr Eye Res. 1989;8(9):963-969.
        # DOI 10.3109/02713688909082658. PMID 2791636.
        # Tonografia 0,26 +- 0,07 e perfusao a pressao constante 0,26 — os dois
        # metodos CONCORDAM (r=0,914). O codigo oficial cita "Fourman & Garner":
        # nao existe Garner. Condicao anestesica NAO confirmada no resumo.
        "C_out_uL_min_mmHg": {"valor": 0.26, "conf": "V", "condicao": "nao confirmada",
                              "fonte": "Fourman S, Fourman MB 1989, Curr Eye Res 8(9):963-969"},
        # Kiel JW, Kopczynski CC. J Ocul Pharmacol Ther. 2015;31(3):146-151.
        # DOI 10.1089/jop.2014.0146. EVP 16 +- 1 mmHg em coelho anestesiado.
        "Pev_mmHg": {"valor": 15.5, "conf": "V", "condicao": "anestesiado",
                     "fonte": "Kiel & Kopczynski 2015 (EVP 16+-1 mmHg)"},
        # SEM FONTE. O fluxo publicado que foi possivel verificar e 1,46-2,53
        # uL/min em coelho CONSCIENTE (Zhao et al. 2010, IOVS 51(6):3145-3151,
        # DOI 10.1167/iovs.09-4415). 3,06 esta ACIMA dessa faixa.
        "Q_prod_uL_min": {"valor": 3.06, "conf": "NF", "condicao": "nao confirmada",
                          "fonte": "SEM FONTE — faixa medida (consciente): 1,46-2,53 (Zhao 2010)"},
        "frac_uveoscleral": {"valor": 0.05, "conf": "V2", "condicao": "nao confirmada",
                             "fonte": "plano de tese: 3-8% em coelho (Toris & Pederson)"},
    },
}

# Valor do plano que NAO tem fonte publicada (ver claude-REFERENCES-WP4.md):
# C_out coelho = 0,57 uL/min/mmHg. E reproduzivel do balanco de Goldmann com
# Q=3,06 e (IOP-Pev)~5,4 mmHg, ou seja, parece derivado e nao medido.
C_OUT_COELHO_DO_PLANO_SEM_FONTE = 0.57

# Facilidade em coelho CONSCIENTE, para contraste (Zhao et al. 2010):
# 0,14 +- 0,02 (adulto dia), 0,10 +- 0,02 (noite), 0,20 +- 0,03 (juvenil dia).
# Ou seja: consciente e MAIS BAIXO que 0,26, entao anestesia nao explica 0,57.
C_OUT_COELHO_CONSCIENTE_ZHAO2010 = (0.10, 0.20)


def derivar_P0_equilibrio(
    Pev_mmHg: float, Q_prod_uL_min: float, C_out_uL_min_mmHg: float, frac_uveoscleral: float
) -> float:
    """P0 = Pev + Q_prod.(1 - frac_uv)/C_out — equilibrio de Goldmann (dV/dt=0)."""
    return Pev_mmHg + Q_prod_uL_min * (1.0 - frac_uveoscleral) / C_out_uL_min_mmHg


def P0_com_provenancia(especie: str) -> dict:
    """P0 derivado + a provenancia de cada parametro que entrou nele, e um aviso
    explicito quando ha parametro sem fonte ou mistura de condicoes experimentais."""
    if especie not in PARAMS_LITERATURA_V2:
        raise ValueError(f"especie desconhecida: {especie!r}")
    p = PARAMS_LITERATURA_V2[especie]
    P0 = derivar_P0_equilibrio(
        p["Pev_mmHg"]["valor"], p["Q_prod_uL_min"]["valor"],
        p["C_out_uL_min_mmHg"]["valor"], p["frac_uveoscleral"]["valor"],
    )
    sem_fonte = [k for k, v in p.items() if v["conf"] == "NF"]
    condicoes = {v["condicao"] for v in p.values()}
    return {
        "especie": especie,
        "P0_mmHg": P0,
        "parametros": p,
        "parametros_sem_fonte": sem_fonte,
        "condicoes_misturadas": sorted(condicoes) if len(condicoes) > 1 else None,
        "confiavel": not sem_fonte and len(condicoes) == 1,
    }


# =============================================================================
# 6 — regimes de anti-VEGF com fonte primaria
# =============================================================================

MIN_POR_SEMANA = 7 * 24 * 60

# ATENCAO: estes regimes NAO vem do plano de tese (que nao tem Secao 4.5 nem
# menciona brolucizumabe/faricimabe/treat-and-extend). Fontes primarias:
#
#  Dugel PU et al. HAWK e HARRIER. Ophthalmology 2020;127(1):72-84.
#    DOI 10.1016/j.ophtha.2019.04.017  (+ 96 sem: 2021;128(1):89-99,
#    DOI 10.1016/j.ophtha.2020.06.028, PMID 32574761)
#  Heier JS et al. TENAYA e LUCERNE. Lancet 2022;399(10326):729-740.
#    DOI 10.1016/S0140-6736(22)00010-1
#  Gemenetzi M, Patel PJ. Ophthalmol Ther 2017;6(1):79-92.
#    DOI 10.1007/s40123-017-0087-5
#
# RESSALVA ESTRUTURAL: q12s e q16s nos ensaios sao a PROPORCAO de pacientes que
# conseguiu manter o intervalo (brolucizumabe q12s: 56% HAWK / 51% HARRIER na
# semana 48; faricimabe q16s: 45,7% TENAYA / 44,9% LUCERNE), nao o intervalo de
# toda a coorte. Modelar o regime como se 100% mantivesse o intervalo maximo
# subestima a dose acumulada media da populacao.
REGIMES_ANTIVEGF = {
    "mensal_fixo": {
        "N_2anos": 24, "intervalo_semanas": 4.0,
        "fonte": "regime de referencia q4s (dosagem mensal continua)",
        "conf": "V2",
    },
    "treat_and_extend": {
        # CORRIGIDO: o codigo oficial usa 12 injecoes a cada 10 semanas.
        # Gemenetzi & Patel 2017 reportam 13,0-14,3 injecoes em 2 anos
        # (Abedi 8,6+5,7 = 14,3; Arnold/FRB 7,5+5,5 = 13,0) e Mrejen 8,3/ano,
        # equivalente a intervalo medio de ~6,3 semanas.
        "N_2anos": 13, "intervalo_semanas": 6.3,
        "fonte": "Gemenetzi & Patel 2017 (revisao sistematica de T&E)",
        "conf": "V",
    },
    "brolucizumabe_q12s": {
        "N_2anos": 8, "intervalo_semanas": 12.0,
        "fonte": "Dugel et al. HAWK/HARRIER 2020-2021 (q12s em 51-56% na sem. 48)",
        "conf": "V",
    },
    "faricimabe_q16s": {
        "N_2anos": 6, "intervalo_semanas": 16.0,
        "fonte": "Heier et al. TENAYA/LUCERNE 2022 (q16s em ~45% na sem. 48)",
        "conf": "V",
    },
}


def comparar_regimes_com_estado(
    I_por_evento_mmHg_min: float,
    meia_vida_semanas: float,
    regimes: dict | None = None,
) -> dict:
    """Compara os regimes nos DOIS limites, agora com o modelo de estado:
    acumulacao perfeita (D_N = N.I) vs recuperacao com estado (satura).

    meia_vida_semanas NAO e calibrada — e parametro de sensibilidade (nao ha
    fonte para a recuperacao perfusional ocular; ver claude-REFERENCES-WP4.md).
    """
    regimes = regimes if regimes is not None else REGIMES_ANTIVEGF
    a = math.log(2.0) / (meia_vida_semanas * MIN_POR_SEMANA)
    out = {"meia_vida_semanas": meia_vida_semanas, "a_per_min": a, "regimes": {}}
    for nome, r in regimes.items():
        N, dt_sem = r["N_2anos"], r["intervalo_semanas"]
        dt = dt_sem * MIN_POR_SEMANA
        perfeita = dano_acumulado_com_estado([I_por_evento_mmHg_min] * N, [dt] * (N - 1), None)
        parcial = dano_acumulado_com_estado([I_por_evento_mmHg_min] * N, [dt] * (N - 1), a)
        out["regimes"][nome] = {
            "N_2anos": N,
            "intervalo_semanas": dt_sem,
            "D_perfeita_mmHg_min": perfeita["D_final_mmHg_min"],
            "D_com_recuperacao_mmHg_min": parcial["D_final_mmHg_min"],
            "D_infinito_mmHg_min": parcial.get("D_infinito_mmHg_min"),
            "fracao_do_estacionario": parcial.get("fracao_do_estacionario"),
            "fonte": r["fonte"],
            "conf": r["conf"],
        }
    return out


# =============================================================================
# demonstracao
# =============================================================================

if __name__ == "__main__":
    print("=" * 74)
    print("WP4 — correcoes (ver claude-REVISAO-WP4.md e claude-REFERENCES-WP4.md)")
    print("=" * 74)

    # --- 1/2: estimador de tempo acima e dose, em grid fino vs grid clinico ---
    print("\n[1/2] Estimadores temporais: grid do solver vs grid clinico do WP3")
    # decaimento exponencial sintetico: IOP = P0 + dP0.exp(-t/tau)
    P0, dP0, tau = 16.9, 33.0, 3.18       # tau de Ruffini et al. 2024 (3,18 min)
    def iop_de(t):
        return P0 + dP0 * np.exp(-t / tau)

    t_fino = np.linspace(0, 30, 3001)      # dt = 0,01 min, como o solver
    t_clin = np.array([0.0, 2.0, 5.0, 10.0, 15.0, 30.0])   # protocolo do WP3

    # valor analitico do tempo acima: t = tau.ln(dP0/(limiar-P0))
    for limiar in (30.0, 40.0):
        exato = tau * math.log(dP0 / (limiar - P0)) if (limiar - P0) < dP0 else 0.0
        trap_fino = float(_trapz((iop_de(t_fino) > limiar).astype(float), t_fino))
        trap_clin = float(_trapz((iop_de(t_clin) > limiar).astype(float), t_clin))
        novo_fino = tempo_acima_interpolado(t_fino, iop_de(t_fino), limiar)
        novo_clin = tempo_acima_interpolado(t_clin, iop_de(t_clin), limiar)
        print(f"  T_acima_{limiar:.0f}  analitico={exato:6.3f} min")
        print(f"     indicador/trapz  fino={trap_fino:6.3f}  CLINICO={trap_clin:7.3f}")
        print(f"     interpolado      fino={novo_fino:6.3f}  CLINICO={novo_clin:7.3f}")

    print("\n  Dose isquemica (MOPP, PAS=120 PAD=70):")
    MAP = 70 + (120 - 70) / 3.0
    # Com OPP_crit=50 a MOPP fica abaixo do limiar na janela inteira (nao ha
    # cruzamento), e trapezio == exata. A diferenca aparece quando o limiar e
    # cruzado DENTRO de um intervalo — e e esse o caso de interesse clinico,
    # porque e onde o deficit comeca e termina.
    for crit in (50.0, 25.0):
        print(f"    OPP_crit={crit:.0f} mmHg:")
        for nome, t in (("fino", t_fino), ("CLINICO", t_clin)):
            mopp = (2.0 / 3.0) * MAP - iop_de(t)
            antigo = float(_trapz(np.clip(crit - mopp, 0, None), t))
            novo = dose_isquemica_exata(t, mopp, crit)
            dif = (novo - antigo) / novo * 100.0 if novo else 0.0
            print(f"      {nome:8s} trapz={antigo:8.3f}   exata={novo:8.3f}"
                  f"   dif={dif:+5.1f}%")
    print(f"  resolucao do grid clinico: {diagnostico_resolucao(t_clin, tau)}")

    # --- 3: modelo de estado vs desconto por evento ---
    print("\n[3] Dano acumulado: desconto por evento (original) vs estado (satura)")
    I_ev, mv = 20.0, 4.0
    a = math.log(2.0) / (mv * MIN_POR_SEMANA)
    for nome, r in REGIMES_ANTIVEGF.items():
        N, dt_sem = r["N_2anos"], r["intervalo_semanas"]
        dt = dt_sem * MIN_POR_SEMANA
        w = math.exp(-a * dt)
        antigo = I_ev * (1 + (N - 1) * w)          # formula do pipeline oficial
        est = dano_acumulado_com_estado([I_ev] * N, [dt] * (N - 1), a)
        print(f"  {nome:22s} N={N:2d} dt={dt_sem:4.1f}sem  "
              f"original={antigo:7.2f}  com estado={est['D_final_mmHg_min']:6.2f}  "
              f"D_inf={est.get('D_infinito_mmHg_min', float('nan')):6.2f}")
    print("  (o original cresce linear em N; com estado satura em I/(1-exp(-a.dt)))")

    # --- 4: sensibilidade ao fator braquial-oftalmica ---
    print("\n[4] Sensibilidade ao fator braquial-oftalmica (0,5-0,8), OPP_crit=50:")
    for f, v in curva_sensibilidade_fator_braquial(
        t_fino, iop_de(t_fino), 120, 70, 50.0
    ).items():
        print(f"  fator={f:.4f}  MOPP_min={v['MOPP_min_mmHg']:6.2f}  "
              f"I={v['I_mmHg_min']:8.2f} mmHg.min")

    # --- 5: P0 com provenancia ---
    print("\n[5] P0 derivado, com provenancia por parametro:")
    for esp in ("humano", "coelho"):
        r = P0_com_provenancia(esp)
        print(f"  {esp:8s} P0={r['P0_mmHg']:6.2f} mmHg  confiavel={r['confiavel']}")
        if r["parametros_sem_fonte"]:
            print(f"     SEM FONTE: {r['parametros_sem_fonte']}")
        if r["condicoes_misturadas"]:
            print(f"     condicoes misturadas: {r['condicoes_misturadas']}")
    print("\n  Sensibilidade de P0 do coelho ao Q_prod (3,06 nao tem fonte;")
    print("  faixa medida consciente 1,46-2,53 uL/min, Zhao et al. 2010):")
    for q in (1.46, 2.0, 2.53, 3.06):
        p0 = derivar_P0_equilibrio(15.5, q, 0.26, 0.05)
        flag = "  <- SEM FONTE" if q == 3.06 else ""
        print(f"    Q_prod={q:4.2f} -> P0={p0:5.2f} mmHg{flag}")
    print(f"\n  C_out coelho: 0,26 medido (Fourman & Fourman 1989) vs "
          f"{C_OUT_COELHO_DO_PLANO_SEM_FONTE} do plano (SEM FONTE).")
    print(f"  Consciente e ainda MAIS BAIXO: {C_OUT_COELHO_CONSCIENTE_ZHAO2010} (Zhao 2010)")
    print("  => anestesia nao explica a diferenca; 0,57 parece derivado, nao medido.")
