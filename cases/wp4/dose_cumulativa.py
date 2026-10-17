"""WP4.5 — dose isquêmica acumulada em regime terapêutico de injeções
repetidas (contribuição original — não existia em nenhum item anterior).

    I_cum(N) = Σ_{j=1..N} I_j · w(t_j − t_{j−1})

Dois limites de w(Δt), AMBOS implementados (nunca reportar só um):

  - Acumulação perfeita: w = 1 sempre → I_cum = N·I.
  - Recuperação parcial (inspirado no modelo SF do rato,
    SF = 1 − b·(1 − e^{−a·t}), reinterpretado como a FRAÇÃO de dano que
    persiste após um intervalo Δt):

        w(Δt) = (1−b) + b·e^{−a·Δt}

    Δt curto → w → 1 (quase todo dano acumula); Δt ≫ 1/a → w → (1−b)
    (recuperação quase completa se b=1; piso residual se b<1). Com b=1
    (padrão) vira decaimento exponencial puro w=e^{−a·Δt} — SIMPLIFICAÇÃO
    do modelo do rato (que tem assíntota b<1, dano residual permanente);
    se a tese precisar de dano residual mesmo com intervalo infinito,
    usar b<1 explicitamente (já suportado).

**a e b NÃO têm calibração direta na literatura** para recuperação
perfusional ocular — são PARÂMETROS DE SENSIBILIDADE, exatamente como
phi_vasc (4.1) e OPP_crit (4.2/4.3). Nunca reportar I_cum para um único
(a,b) — sempre ao lado do limite de acumulação perfeita e, se possível,
de uma faixa de a (via meia-vida).

Regimes terapêuticos do plano (Seção 4.5), N em 2 anos:
  mensal_fixo (24, 4 sem), treat_and_extend (10, 10 sem — ALTAIR ~10,4/96 sem),
  brolucizumabe (~8, 12 sem), faricimabe (~6, 16 sem).
"""
from __future__ import annotations

import math

import numpy as np

MIN_POR_SEMANA = 7 * 24 * 60

REGIMES_PLANO = {
    "mensal_fixo": {"N_2anos": 24, "intervalo_semanas": 4.0},
    "treat_and_extend": {"N_2anos": 10, "intervalo_semanas": 10.0},
    "brolucizumabe": {"N_2anos": 8, "intervalo_semanas": 12.0},
    "faricimabe": {"N_2anos": 6, "intervalo_semanas": 16.0},
}

# Meia-vida de referência ILUSTRATIVA (não calibrada — parâmetro de
# sensibilidade). 4 semanas por estar na ordem do intervalo terapêutico
# mais curto (mensal), regime onde a diferença entre os dois limites de
# w(Δt) mais importa.
MEIA_VIDA_ILUSTRATIVA_SEMANAS = 4.0
A_ILUSTRATIVO_PER_MIN = math.log(2.0) / (MEIA_VIDA_ILUSTRATIVA_SEMANAS * MIN_POR_SEMANA)


def peso_geral(dt_min: float, a_per_min: float | None = None, b: float = 1.0) -> float:
    """w(Δt): a_per_min=None é atalho para acumulação perfeita (w=1 sempre);
    caso contrário w = (1−b) + b·exp(−a·Δt). ValueError se a ≤ 0 ou b ∉ [0,1]."""
    if a_per_min is None:
        return 1.0
    if not (0.0 <= b <= 1.0):
        raise ValueError(f"b deve estar em [0,1], recebido {b}")
    if a_per_min <= 0:
        raise ValueError(f"a_per_min deve ser > 0, recebido {a_per_min}")
    return (1.0 - b) + b * math.exp(-a_per_min * dt_min)


def dose_cumulativa(
    I_por_evento_mmHg_min,
    intervalos_min,
    a_per_min: float | None = None,
    b: float = 1.0,
) -> dict:
    """I_cum = Σ_j I_j·w(Δt_j), com w do PRIMEIRO evento sempre 1.0 (não há
    intervalo anterior nem dano prévio antes do primeiro evento).

    ``I_por_evento_mmHg_min``: N doses (constante se K fixo; pode variar por
    evento, ex.: K progredindo com miopia/glaucoma).
    ``intervalos_min``: N−1 intervalos entre eventos consecutivos.
    """
    I_arr = np.asarray(I_por_evento_mmHg_min, dtype=float)
    N = len(I_arr)
    if N == 0:
        raise ValueError("I_por_evento_mmHg_min não pode ser vazio")
    intervalos = list(intervalos_min)
    if len(intervalos) != N - 1:
        raise ValueError(
            f"intervalos_min deve ter N-1={N - 1} elementos (um entre cada "
            f"par de eventos consecutivos), recebido {len(intervalos)}"
        )
    pesos = [1.0] + [peso_geral(dt, a_per_min, b) for dt in intervalos]
    pesos_arr = np.asarray(pesos, dtype=float)
    contribuicoes = I_arr * pesos_arr
    return {
        "I_cum_mmHg_min": float(contribuicoes.sum()),
        "pesos": pesos_arr.tolist(),
        "contribuicoes_mmHg_min": contribuicoes.tolist(),
        "N": N,
    }


def regime_terapeutico(
    N: int,
    intervalo_semanas: float,
    I_por_evento_mmHg_min: float,
    a_per_min: float | None = None,
    b: float = 1.0,
) -> dict:
    """N injeções igualmente espaçadas, mesmo I por evento (K constante).
    Para N=1 não há intervalos; I_cum = I_por_evento trivialmente."""
    if N < 1:
        raise ValueError(f"N deve ser >= 1, recebido {N}")
    intervalo_min = intervalo_semanas * MIN_POR_SEMANA
    out = dose_cumulativa(
        [I_por_evento_mmHg_min] * N,
        [intervalo_min] * (N - 1),
        a_per_min=a_per_min,
        b=b,
    )
    out["intervalo_semanas"] = intervalo_semanas
    return out


def comparar_regimes(
    I_por_evento_mmHg_min: float,
    a_per_min: float | None = A_ILUSTRATIVO_PER_MIN,
    b: float = 1.0,
    regimes: dict | None = None,
) -> dict:
    """Para cada regime (os 4 do plano, ou dict custom no formato de
    REGIMES_PLANO), calcula I_cum nos DOIS limites — acumulação perfeita
    (N·I) e recuperação parcial (a,b dados). Nunca reportar só um."""
    regimes = regimes if regimes is not None else REGIMES_PLANO
    out = {}
    for nome, r in regimes.items():
        perfeita = regime_terapeutico(r["N_2anos"], r["intervalo_semanas"],
                                      I_por_evento_mmHg_min, a_per_min=None)
        parcial = regime_terapeutico(r["N_2anos"], r["intervalo_semanas"],
                                     I_por_evento_mmHg_min, a_per_min=a_per_min, b=b)
        out[nome] = {
            "N_2anos": r["N_2anos"],
            "intervalo_semanas": r["intervalo_semanas"],
            "I_cum_perfeita_mmHg_min": perfeita["I_cum_mmHg_min"],
            "I_cum_parcial_mmHg_min": parcial["I_cum_mmHg_min"],
        }
    return out


if __name__ == "__main__":
    I_evento = 20.0  # mmHg.min por evento (exemplo, K constante)

    print("=== 4 regimes do plano, I por evento = 20 mmHg.min ===")
    print(f"  meia-vida ilustrativa = {MEIA_VIDA_ILUSTRATIVA_SEMANAS:.0f} semanas "
          f"(a={A_ILUSTRATIVO_PER_MIN:.3e} /min) — PARÂMETRO DE SENSIBILIDADE, não calibrado")
    tab = comparar_regimes(I_evento)
    print(f"  {'regime':<18} {'N':>3} {'intervalo':>10} {'I_cum perfeita':>15} {'I_cum parcial':>14}")
    for nome, v in tab.items():
        print(f"  {nome:<18} {v['N_2anos']:>3} {v['intervalo_semanas']:>8.0f} sem "
              f"{v['I_cum_perfeita_mmHg_min']:>13.1f}  {v['I_cum_parcial_mmHg_min']:>12.2f}")

    print("\n=== Sensibilidade à meia-vida (mensal_fixo, N=24) ===")
    for mv in (2.0, 4.0, 8.0, 12.0):
        a = math.log(2.0) / (mv * MIN_POR_SEMANA)
        r = regime_terapeutico(24, 4.0, I_evento, a_per_min=a)
        print(f"  meia-vida={mv:5.1f} sem  I_cum_parcial={r['I_cum_mmHg_min']:8.2f} mmHg.min")
