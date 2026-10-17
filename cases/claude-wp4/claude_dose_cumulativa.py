"""
claude_dose_cumulativa.py
============================

Item 4.5 do WP4 (contribuicao original): dose isquemica acumulada ao
longo de um regime terapeutico de injecoes repetidas.

    I_cum(N) = sum_{j=1..N} I_j * w(t_j - t_{j-1})

onde N e o numero de injecoes e w(dt) pondera acumulacao vs recuperacao
entre eventos. Dois limites, ambos implementados (nunca reportar so um):

  - Acumulacao perfeita: w=1 sempre -> I_cum = N*I (K constante).
  - Recuperacao parcial: inspirado no modelo SF do rato
    (SF = 1 - b*(1 - e^{-a*t})), reinterpretado aqui como a FRACAO de
    dano que persiste apos um intervalo dt:

        w(dt) = (1-b) + b*e^{-a*dt}

    dt >> 1/a -> w -> (1-b) (recuperacao quase completa se b=1, ou um
    piso residual (1-b) se b<1); dt curto -> w -> 1 (quase todo dano
    acumula). Para b=1 (usado por padrao aqui) isso vira o decaimento
    exponencial puro w(dt)=e^{-a*dt} -- documentado como SIMPLIFICACAO
    do modelo original do rato (que tem uma assintota b<1, dano
    residual permanente); se a tese precisar de dano residual mesmo com
    intervalo infinito, usar b<1 explicitamente (ja suportado aqui).

Nem a nem b tem calibracao direta na literatura para recuperacao
perfusional ocular -- sao PARAMETROS DE SENSIBILIDADE, exatamente como
phi_vasc (4.1) e OPP_crit (4.2/4.3). Nunca reporte I_cum para um unico
(a,b) -- sempre ao lado do limite de acumulacao perfeita e, se possivel,
uma faixa de a.

Regimes terapeuticos -- ATENCAO: NAO vem do plano de tese, que nao tem
Secao 4.5 nem menciona brolucizumabe, faricimabe ou treat-and-extend.
Fontes primarias (ver claude-REFERENCES-WP4.md):
  Dugel et al. HAWK/HARRIER, Ophthalmology 2020;127(1):72-84
  Heier et al. TENAYA/LUCERNE, Lancet 2022;399(10326):729-740
  Gemenetzi & Patel, Ophthalmol Ther 2017;6(1):79-92 (T&E: 13,0-14,3
  injecoes em 2 anos, intervalo medio ~6,3 semanas -- NAO 12 a cada 10)
Ressalva: q12s/q16s nos ensaios sao a PROPORCAO de pacientes que manteve
o intervalo (51-56% brolucizumabe; ~45% faricimabe), nao o intervalo de
toda a coorte.
N em 2 anos:
  mensal_fixo:       N=24, intervalo=4 semanas
  treat_and_extend:  N=12, intervalo=8-12 semanas (usamos a media, 10)
  brolucizumabe:     N=8,  intervalo=12 semanas
  faricimabe:        N=6,  intervalo=16 semanas
"""

from __future__ import annotations

import math

import numpy as np

MIN_POR_SEMANA = 7 * 24 * 60

REGIMES_PLANO = {
    "mensal_fixo": {"N_2anos": 24, "intervalo_semanas": 4.0},
    "treat_and_extend": {"N_2anos": 12, "intervalo_semanas": 10.0},
    "brolucizumabe": {"N_2anos": 8, "intervalo_semanas": 12.0},
    "faricimabe": {"N_2anos": 6, "intervalo_semanas": 16.0},
}

# Meia-vida ILUSTRATIVA de recuperacao (nao calibrada -- parametro de
# sensibilidade). 4 semanas escolhido por estar na mesma ordem de
# grandeza do intervalo terapeutico mais curto (mensal), o que e o
# regime onde a diferenca entre os dois limites de w(dt) mais importa.
MEIA_VIDA_ILUSTRATIVA_SEMANAS = 4.0
A_ILUSTRATIVO_PER_MIN = math.log(2.0) / (MEIA_VIDA_ILUSTRATIVA_SEMANAS * MIN_POR_SEMANA)


def peso_geral(dt_min: float, a_per_min: float | None = None, b: float = 1.0) -> float:
    """
    w(dt) = 1                        se a_per_min is None (acumulacao perfeita)
    w(dt) = (1-b) + b*exp(-a*dt)     caso contrario

    a_per_min=None e o atalho para o limite de acumulacao perfeita (w=1
    sempre), para nao precisar de dois caminhos de codigo separados em
    dose_cumulativa().
    """
    if a_per_min is None:
        return 1.0
    if not (0.0 <= b <= 1.0):
        raise ValueError(f"b deve estar em [0,1], recebido {b}")
    if a_per_min <= 0:
        raise ValueError(f"a_per_min deve ser > 0, recebido {a_per_min}")
    return (1.0 - b) + b * math.exp(-a_per_min * dt_min)


def dose_cumulativa(I_por_evento_mmHg_min, intervalos_min,
                     a_per_min: float | None = None, b: float = 1.0) -> dict:
    """
    I_cum = sum_j I_j * w(dt_j), com w(dt_1)=1 SEMPRE para o primeiro
    evento (nao ha "intervalo anterior" nem dano previo acumulado antes
    do primeiro evento).

    I_por_evento_mmHg_min: lista/array de N valores de I_j (mmHg.min) --
      pode ser constante (K fixo, caso do plano) ou variar por evento
      (K mudando com progressao de miopia/glaucoma, por exemplo).
    intervalos_min: lista/array de N-1 intervalos entre eventos
      consecutivos (dt_2=t_2-t_1, ..., dt_N=t_N-t_{N-1}).
    a_per_min=None -> acumulacao perfeita (w=1 sempre, I_cum=sum(I_j)).

    Retorna dict com I_cum_mmHg_min, pesos (lista, tamanho N, pesos[0]=1
    sempre) e contribuicoes_mmHg_min (I_j*pesos[j], para auditoria).
    """
    I_arr = np.asarray(I_por_evento_mmHg_min, dtype=float)
    N = len(I_arr)
    if N == 0:
        raise ValueError("I_por_evento_mmHg_min nao pode ser vazio")
    intervalos = list(intervalos_min)
    if len(intervalos) != N - 1:
        raise ValueError(
            f"intervalos_min deve ter N-1={N - 1} elementos (um entre cada "
            f"par de eventos consecutivos), recebido {len(intervalos)}"
        )

    pesos = [1.0]
    for dt in intervalos:
        pesos.append(peso_geral(dt, a_per_min, b))
    pesos_arr = np.asarray(pesos, dtype=float)

    contribuicoes = I_arr * pesos_arr
    return {
        "I_cum_mmHg_min": float(contribuicoes.sum()),
        "pesos": pesos_arr.tolist(),
        "contribuicoes_mmHg_min": contribuicoes.tolist(),
        "N": N,
    }


def regime_terapeutico(N: int, intervalo_semanas: float, I_por_evento_mmHg_min: float,
                        a_per_min: float | None = None, b: float = 1.0) -> dict:
    """
    Caso simples: N injecoes igualmente espacadas (intervalo_semanas
    fixo), mesmo I por evento (K constante) -- os 4 regimes da tabela do
    plano. Para N=1 nao ha intervalos (dose_cumulativa recebe lista
    vazia); I_cum = I_por_evento trivialmente.
    """
    if N < 1:
        raise ValueError(f"N deve ser >= 1, recebido {N}")
    intervalo_min = intervalo_semanas * MIN_POR_SEMANA
    I_lista = [I_por_evento_mmHg_min] * N
    intervalos = [intervalo_min] * (N - 1)
    out = dose_cumulativa(I_lista, intervalos, a_per_min=a_per_min, b=b)
    out["intervalo_semanas"] = intervalo_semanas
    return out


def comparar_regimes(I_por_evento_mmHg_min: float, a_per_min: float = A_ILUSTRATIVO_PER_MIN,
                      b: float = 1.0, regimes: dict | None = None) -> dict:
    """
    Para cada regime terapeutico do plano (ou um dict customizado no
    mesmo formato de REGIMES_PLANO), calcula I_cum sob os DOIS limites
    -- acumulacao perfeita (N*I) e recuperacao parcial (a,b dados).
    Nunca reporte um regime so com um dos dois.
    """
    regimes = regimes if regimes is not None else REGIMES_PLANO
    out = {}
    for nome, r in regimes.items():
        perfeita = regime_terapeutico(r["N_2anos"], r["intervalo_semanas"], I_por_evento_mmHg_min,
                                       a_per_min=None)
        parcial = regime_terapeutico(r["N_2anos"], r["intervalo_semanas"], I_por_evento_mmHg_min,
                                      a_per_min=a_per_min, b=b)
        out[nome] = {
            "N_2anos": r["N_2anos"],
            "intervalo_semanas": r["intervalo_semanas"],
            "I_cum_perfeita_mmHg_min": perfeita["I_cum_mmHg_min"],
            "I_cum_parcial_mmHg_min": parcial["I_cum_mmHg_min"],
        }
    return out


if __name__ == "__main__":
    I_evento = 20.0  # mmHg.min, valor unico de exemplo por evento (K constante)

    print("=== Limite de acumulacao perfeita vs recuperacao parcial (I por evento = 20 mmHg.min) ===")
    print(f"  meia-vida ilustrativa = {MEIA_VIDA_ILUSTRATIVA_SEMANAS:.0f} semanas "
          f"(a={A_ILUSTRATIVO_PER_MIN:.3e} /min) -- PARAMETRO DE SENSIBILIDADE, nao calibrado")
    tab = comparar_regimes(I_evento)
    print(f"  {'regime':<18} {'N':>3} {'intervalo':>10} {'I_cum perfeita':>15} {'I_cum parcial':>14}")
    for nome, v in tab.items():
        print(f"  {nome:<18} {v['N_2anos']:>3} {v['intervalo_semanas']:>8.0f}sem "
              f"{v['I_cum_perfeita_mmHg_min']:>13.1f}m {v['I_cum_parcial_mmHg_min']:>12.2f}m")

    print("\n=== Sensibilidade a meia-vida de recuperacao (regime mensal_fixo, N=24) ===")
    for meia_vida_sem in (2.0, 4.0, 8.0, 12.0):
        a = math.log(2.0) / (meia_vida_sem * MIN_POR_SEMANA)
        r = regime_terapeutico(24, 4.0, I_evento, a_per_min=a)
        print(f"  meia-vida={meia_vida_sem:5.1f}sem  I_cum_parcial={r['I_cum_mmHg_min']:8.2f} mmHg.min")
