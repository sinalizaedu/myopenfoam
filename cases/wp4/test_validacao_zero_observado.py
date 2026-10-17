"""Testes WP4.4 — validação teórica contra o zero observado."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

WP4 = Path(__file__).resolve().parent
sys.path.insert(0, str(WP4))

from validacao_zero_observado import (  # noqa: E402
    K_implicito_do_pico_observado,
    controle_negativo_afinamento_mecanico,
    dPth_com_reserva_vascular,
    opp_crit_maximo_consistente_com_zero,
    subgrupo_risco_damasceno,
    tabela_consistencia_zero_oct_a,
)


def test_K_implicito_do_pico_observado_oct_a():
    """(31 − 14)/50 = 0,34 mmHg/µL."""
    assert K_implicito_do_pico_observado() == pytest.approx(0.34)
    assert K_implicito_do_pico_observado(14.0, 31.0, 50.0) == pytest.approx(0.34)


def test_opp_crit_maximo_consistente_com_zero_e_o_proprio_mopp_min():
    assert opp_crit_maximo_consistente_com_zero(31.0) == 31.0


def test_tabela_consistencia_zero_oct_a_veredito_correto():
    tab = tabela_consistencia_zero_oct_a(OPP_crit_range=(25, 30, 31, 35, 50))
    assert "zero" in tab[25.0]
    assert "zero" in tab[30.0]
    # fronteira: OPP_crit == MOPP_min observado → déficit máximo = 0 → zero
    assert "zero" in tab[31.0]
    assert "deficit>0" in tab[35.0]
    assert "deficit>0" in tab[50.0]


def test_tabela_consistencia_fronteira_exata():
    """Teste dedicado à fronteira OPP_crit == MOPP_min (déficit = 0 exato)."""
    tab = tabela_consistencia_zero_oct_a(OPP_crit_range=(31.0,), MOPP_min_observado_mmHg=31.0)
    assert tab[31.0].startswith("zero")


def test_dPth_com_reserva_vascular_identidade_phi_1():
    assert dPth_com_reserva_vascular(20.0, 25.0, 1.0) == 20.0


def test_dPth_com_reserva_vascular_diminui_com_phi_maior():
    """dPth(1,3) = 20 − 25·0,3 = 12,5."""
    assert dPth_com_reserva_vascular(20.0, 25.0, 1.3) == pytest.approx(12.5)


def test_dPth_com_reserva_vascular_rejeita_phi_menor_que_1():
    with pytest.raises(ValueError):
        dPth_com_reserva_vascular(20.0, 25.0, 0.9)


def test_subgrupo_risco_damasceno_cenario_ilustrativo_do_plano():
    """Cenário do plano: K_tip=0,34, K_alto=1,0, ΔV=50, C=0,28, dPth_basal=20,
    OPP_crit_ref=25, phi_risco=1,3 → típico I=0, risco I≈72,0 mmHg·min."""
    r = subgrupo_risco_damasceno(
        K_tipico_mmHg_per_uL=0.34, K_alto_mmHg_per_uL=1.0,
        dV_uL=50.0, C_out_uL_min_mmHg=0.28,
        dPth_basal_mmHg=20.0, OPP_crit_ref_mmHg=25.0, phi_vasc_risco=1.3,
    )
    assert r["status_tipico"] == "OK"
    assert r["I_tipico_mmHg_min"] == 0.0          # K·ΔV = 17 ≤ dPth = 20
    assert r["status_risco"] == "OK"
    assert r["dPth_risco_mmHg"] == pytest.approx(12.5)
    assert r["I_risco_mmHg_min"] == pytest.approx(72.0, abs=0.1)


def test_subgrupo_risco_damasceno_marca_regime_cronico_quando_dPth_risco_negativo():
    """phi alto demais → dPth_risco ≤ 0 → marca 'regime cronico', NÃO ValueError."""
    r = subgrupo_risco_damasceno(
        K_tipico_mmHg_per_uL=0.34, K_alto_mmHg_per_uL=1.0,
        dV_uL=50.0, C_out_uL_min_mmHg=0.28,
        dPth_basal_mmHg=20.0, OPP_crit_ref_mmHg=25.0, phi_vasc_risco=2.0,
    )
    assert r["dPth_risco_mmHg"] <= 0
    assert r["I_risco_mmHg_min"] is None
    assert "regime cronico" in r["status_risco"]


def test_controle_negativo_estrutura_e_valores_do_plano():
    c = controle_negativo_afinamento_mecanico()
    assert c["afinamento_percentual"] == 0.25
    assert c["tempo_pico_min"] == 15
    assert c["tempo_resolucao_h"] == 48
    assert c["fonte"] == "PMC13307848"
    assert c["compativel_com_dose_isquemica_do_modelo"] is False
    assert "mecanica" in c["mecanismo_atribuido"]


def test_MOPP_min_observado_constante_bate_com_o_plano():
    """Constantes do estudo OCT-A conforme citadas no plano (14→31, MOPP~31)."""
    from validacao_zero_observado import (
        IOP_BASAL_OCT_A_MMHG,
        IOP_PICO_OCT_A_MMHG,
        MOPP_MIN_OBSERVADO_OCT_A_MMHG,
        N_OLHOS_OCT_A,
    )
    assert (IOP_BASAL_OCT_A_MMHG, IOP_PICO_OCT_A_MMHG) == (14.0, 31.0)
    assert MOPP_MIN_OBSERVADO_OCT_A_MMHG == 31.0
    assert N_OLHOS_OCT_A == 54
