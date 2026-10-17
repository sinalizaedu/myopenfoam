"""Testes WP4.5 — dose isquêmica acumulada em regime de injeções repetidas."""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

WP4 = Path(__file__).resolve().parent
sys.path.insert(0, str(WP4))

from dose_cumulativa import (  # noqa: E402
    A_ILUSTRATIVO_PER_MIN,
    MEIA_VIDA_ILUSTRATIVA_SEMANAS,
    MIN_POR_SEMANA,
    REGIMES_PLANO,
    comparar_regimes,
    dose_cumulativa,
    peso_geral,
    regime_terapeutico,
)


def test_peso_geral_a_none_e_acumulacao_perfeita():
    assert peso_geral(0.0, a_per_min=None) == 1.0
    assert peso_geral(1e6, a_per_min=None) == 1.0


def test_peso_zero_em_dt_zero():
    """w(0) = (1−b) + b·1 = 1 para qualquer b."""
    for b in (0.0, 0.3, 1.0):
        assert peso_geral(0.0, a_per_min=1e-4, b=b) == pytest.approx(1.0)


def test_peso_monotonico_decrescente_em_dt():
    ws = [peso_geral(dt, a_per_min=A_ILUSTRATIVO_PER_MIN) for dt in
          (0.0, 1e3, 1e4, 4e4, 1e5, 1e6)]
    assert all(ws[i] >= ws[i + 1] for i in range(len(ws) - 1))


def test_peso_assintota_piso_1_menos_b():
    w = peso_geral(1e12, a_per_min=A_ILUSTRATIVO_PER_MIN, b=0.7)
    assert w == pytest.approx(0.3, abs=1e-9)


def test_meia_vida_definicao_exata():
    """Com b=1, w(meia-vida) = 0,5 EXATAMENTE (e^{-ln2} = 1/2)."""
    t_half = MEIA_VIDA_ILUSTRATIVA_SEMANAS * MIN_POR_SEMANA
    assert peso_geral(t_half, a_per_min=A_ILUSTRATIVO_PER_MIN, b=1.0) == pytest.approx(0.5)


def test_peso_geral_rejeita_parametros_invalidos():
    with pytest.raises(ValueError):
        peso_geral(10.0, a_per_min=0.0)
    with pytest.raises(ValueError):
        peso_geral(10.0, a_per_min=-1e-5)
    with pytest.raises(ValueError):
        peso_geral(10.0, a_per_min=1e-4, b=1.5)
    with pytest.raises(ValueError):
        peso_geral(10.0, a_per_min=1e-4, b=-0.1)


def test_acumulacao_perfeita_e_N_vezes_I_exato():
    r = regime_terapeutico(24, 4.0, 20.0, a_per_min=None)
    assert r["I_cum_mmHg_min"] == pytest.approx(24 * 20.0)


def test_peso_do_primeiro_evento_sempre_um():
    r = dose_cumulativa([20.0, 20.0, 20.0], [100.0, 100.0],
                        a_per_min=A_ILUSTRATIVO_PER_MIN)
    assert r["pesos"][0] == 1.0


def test_dose_cumulativa_rejeita_tamanhos_incompativeis():
    with pytest.raises(ValueError):
        dose_cumulativa([20.0, 20.0, 20.0], [100.0])  # N=3 pede 2 intervalos
    with pytest.raises(ValueError):
        dose_cumulativa([], [])


def test_recuperacao_parcial_menor_ou_igual_a_perfeita():
    I = 20.0
    for nome, reg in REGIMES_PLANO.items():
        perfeita = regime_terapeutico(reg["N_2anos"], reg["intervalo_semanas"], I,
                                      a_per_min=None)
        parcial = regime_terapeutico(reg["N_2anos"], reg["intervalo_semanas"], I,
                                     a_per_min=A_ILUSTRATIVO_PER_MIN)
        assert parcial["I_cum_mmHg_min"] <= perfeita["I_cum_mmHg_min"] + 1e-9


def test_ordem_preservada_entre_os_4_regimes_nos_dois_limites():
    """mensal > T&E > brolucizumabe > faricimabe (N domina) nos dois limites."""
    tab = comparar_regimes(20.0)
    ordem = ["mensal_fixo", "treat_and_extend", "brolucizumabe", "faricimabe"]
    perf = [tab[n]["I_cum_perfeita_mmHg_min"] for n in ordem]
    parc = [tab[n]["I_cum_parcial_mmHg_min"] for n in ordem]
    assert all(perf[i] > perf[i + 1] for i in range(3))
    assert all(parc[i] > parc[i + 1] for i in range(3))


def test_comparar_regimes_cobre_os_4_do_plano():
    tab = comparar_regimes(20.0)
    assert set(tab.keys()) == {"mensal_fixo", "treat_and_extend",
                               "brolucizumabe", "faricimabe"}
    for nome, v in tab.items():
        assert v["N_2anos"] == REGIMES_PLANO[nome]["N_2anos"]
        assert v["I_cum_perfeita_mmHg_min"] == pytest.approx(
            v["N_2anos"] * 20.0)


def test_regime_terapeutico_N_1_trivial():
    r = regime_terapeutico(1, 4.0, 20.0, a_per_min=A_ILUSTRATIVO_PER_MIN)
    assert r["I_cum_mmHg_min"] == 20.0
    assert r["pesos"] == [1.0]


def test_valores_de_referencia_meia_vida_4_semanas():
    """Com meia-vida = intervalo (4 sem), w=0,5: mensal I_cum = 20·(1+23·0,5) = 250."""
    r = regime_terapeutico(24, 4.0, 20.0, a_per_min=A_ILUSTRATIVO_PER_MIN)
    assert r["I_cum_mmHg_min"] == pytest.approx(250.0)
