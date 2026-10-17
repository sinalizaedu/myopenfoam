"""
test_claude_dose_cumulativa.py
=================================

Testes do modulo claude_dose_cumulativa.py (item 4.5 do WP4).

    cd cases/claude-wp4
    ../wp0/.venv/bin/python -m pytest -v test_claude_dose_cumulativa.py
"""
import math
import os
import sys

import pytest

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS_DIR)

from claude_dose_cumulativa import (  # noqa: E402
    peso_geral,
    dose_cumulativa,
    regime_terapeutico,
    comparar_regimes,
    REGIMES_PLANO,
    MIN_POR_SEMANA,
)


def test_peso_geral_acumulacao_perfeita_e_sempre_1():
    for dt in (0.0, 100.0, 1e9):
        assert peso_geral(dt, a_per_min=None) == 1.0


def test_peso_geral_recuperacao_parcial_em_dt_zero_e_1():
    assert peso_geral(0.0, a_per_min=0.001, b=1.0) == pytest.approx(1.0)


def test_peso_geral_recuperacao_parcial_tende_a_1_menos_b_no_infinito():
    w = peso_geral(1e8, a_per_min=0.01, b=1.0)
    assert w == pytest.approx(0.0, abs=1e-6)
    w_b = peso_geral(1e8, a_per_min=0.01, b=0.3)
    assert w_b == pytest.approx(0.7, abs=1e-6)


def test_peso_geral_monotonico_decrescente_em_dt():
    a = 0.001
    dts = [0, 10, 50, 100, 500]
    ws = [peso_geral(dt, a_per_min=a) for dt in dts]
    assert all(ws[i] >= ws[i + 1] for i in range(len(ws) - 1))


def test_peso_geral_rejeita_a_nao_positivo():
    with pytest.raises(ValueError):
        peso_geral(10.0, a_per_min=0.0)
    with pytest.raises(ValueError):
        peso_geral(10.0, a_per_min=-1.0)


def test_peso_geral_rejeita_b_fora_de_0_1():
    with pytest.raises(ValueError):
        peso_geral(10.0, a_per_min=0.01, b=1.5)
    with pytest.raises(ValueError):
        peso_geral(10.0, a_per_min=0.01, b=-0.1)


def test_dose_cumulativa_rejeita_tamanho_errado_de_intervalos():
    with pytest.raises(ValueError):
        dose_cumulativa([10.0, 10.0, 10.0], intervalos_min=[100.0])  # precisa de 2, deu 1


def test_dose_cumulativa_rejeita_lista_vazia():
    with pytest.raises(ValueError):
        dose_cumulativa([], intervalos_min=[])


def test_dose_cumulativa_acumulacao_perfeita_e_N_vezes_I():
    """K constante -> I_cum = N*I exatamente, sob acumulacao perfeita (w=1)."""
    N = 24
    I = 20.0
    out = dose_cumulativa([I] * N, intervalos_min=[1000.0] * (N - 1), a_per_min=None)
    assert out["I_cum_mmHg_min"] == pytest.approx(N * I)
    assert all(p == 1.0 for p in out["pesos"])


def test_dose_cumulativa_um_evento_so_e_so_o_proprio_I():
    out = dose_cumulativa([15.0], intervalos_min=[])
    assert out["I_cum_mmHg_min"] == pytest.approx(15.0)
    assert out["pesos"] == [1.0]


def test_dose_cumulativa_recuperacao_parcial_menor_ou_igual_a_perfeita():
    N = 10
    I = 20.0
    intervalos = [500.0] * (N - 1)
    perfeita = dose_cumulativa([I] * N, intervalos, a_per_min=None)
    parcial = dose_cumulativa([I] * N, intervalos, a_per_min=0.01, b=1.0)
    assert parcial["I_cum_mmHg_min"] < perfeita["I_cum_mmHg_min"]


def test_dose_cumulativa_intervalo_muito_longo_tende_a_so_o_primeiro_evento():
    N = 5
    I = 20.0
    out = dose_cumulativa([I] * N, intervalos_min=[1e9] * (N - 1), a_per_min=0.01, b=1.0)
    assert out["I_cum_mmHg_min"] == pytest.approx(I, abs=1e-6)


def test_dose_cumulativa_intervalo_muito_curto_tende_a_acumulacao_perfeita():
    N = 5
    I = 20.0
    out = dose_cumulativa([I] * N, intervalos_min=[1e-6] * (N - 1), a_per_min=0.01, b=1.0)
    assert out["I_cum_mmHg_min"] == pytest.approx(N * I, rel=1e-4)


def test_regime_terapeutico_consistente_com_dose_cumulativa():
    """O wrapper de regime fixo deve dar exatamente o mesmo resultado
    que montar a mesma lista/intervalos na mao e chamar dose_cumulativa."""
    N, sem, I, a = 12, 10.0, 18.0, 5e-5
    r1 = regime_terapeutico(N, sem, I, a_per_min=a)
    intervalo_min = sem * MIN_POR_SEMANA
    r2 = dose_cumulativa([I] * N, [intervalo_min] * (N - 1), a_per_min=a)
    assert r1["I_cum_mmHg_min"] == pytest.approx(r2["I_cum_mmHg_min"])


def test_regime_terapeutico_rejeita_N_menor_que_1():
    with pytest.raises(ValueError):
        regime_terapeutico(0, 4.0, 20.0)


def test_comparar_regimes_ordena_do_maior_acumulo_pro_menor():
    """Regime mensal (N=24, intervalo curto) deve acumular mais que
    treat-and-extend, que deve acumular mais que brolucizumabe, que deve
    acumular mais que faricimabe -- em AMBOS os limites (perfeito e
    parcial), com a meia-vida ilustrativa de 4 semanas do modulo."""
    tab = comparar_regimes(I_por_evento_mmHg_min=20.0)
    ordem = ["mensal_fixo", "treat_and_extend", "brolucizumabe", "faricimabe"]
    for i in range(len(ordem) - 1):
        a, b = ordem[i], ordem[i + 1]
        assert tab[a]["I_cum_perfeita_mmHg_min"] > tab[b]["I_cum_perfeita_mmHg_min"]
        assert tab[a]["I_cum_parcial_mmHg_min"] > tab[b]["I_cum_parcial_mmHg_min"]


def test_comparar_regimes_perfeita_bate_com_N_vezes_I():
    tab = comparar_regimes(I_por_evento_mmHg_min=20.0)
    for nome, v in tab.items():
        esperado = REGIMES_PLANO[nome]["N_2anos"] * 20.0
        assert v["I_cum_perfeita_mmHg_min"] == pytest.approx(esperado)


def test_meia_vida_ilustrativa_reproduz_w_de_meio_em_um_periodo():
    """Por construcao, a_ilustrativo = ln(2)/(4 semanas em min) -> w(4
    semanas) deve ser exatamente 0.5 (definicao de meia-vida)."""
    from claude_dose_cumulativa import A_ILUSTRATIVO_PER_MIN
    dt_4_semanas = 4.0 * MIN_POR_SEMANA
    assert peso_geral(dt_4_semanas, a_per_min=A_ILUSTRATIVO_PER_MIN) == pytest.approx(0.5, abs=1e-6)
