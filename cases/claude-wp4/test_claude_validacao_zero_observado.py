"""
test_claude_validacao_zero_observado.py
==========================================

Testes do modulo claude_validacao_zero_observado.py (item 4.4 do WP4).

    cd cases/claude-wp4
    ../wp0/.venv/bin/python -m pytest -v test_claude_validacao_zero_observado.py
"""
import os
import sys

import pytest

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS_DIR)

from claude_validacao_zero_observado import (  # noqa: E402
    K_implicito_do_pico_observado,
    opp_crit_maximo_consistente_com_zero,
    tabela_consistencia_zero_oct_a,
    dPth_com_reserva_vascular,
    subgrupo_risco_damasceno,
    controle_negativo_afinamento_mecanico,
    MOPP_MIN_OBSERVADO_OCT_A_MMHG,
)


def test_K_implicito_do_pico_observado_oct_a():
    """(31-14)/50 = 0.34 mmHg/uL."""
    assert K_implicito_do_pico_observado() == pytest.approx(0.34, abs=1e-9)


def test_opp_crit_maximo_consistente_com_zero_e_o_proprio_mopp_min():
    assert opp_crit_maximo_consistente_com_zero(31.0) == 31.0
    assert opp_crit_maximo_consistente_com_zero(20.0) == 20.0


def test_tabela_consistencia_zero_oct_a_veredito_correto():
    tab = tabela_consistencia_zero_oct_a(OPP_crit_range=(20, 30, 31, 32, 50),
                                          MOPP_min_observado_mmHg=31.0)
    assert "zero" in tab[20.0]
    assert "zero" in tab[30.0]
    assert "zero" in tab[31.0]  # fronteira: OPP_crit == MOPP_min ainda conta como zero
    assert "deficit" in tab[32.0]
    assert "deficit" in tab[50.0]


def test_dPth_com_reserva_vascular_identidade_phi_1():
    assert dPth_com_reserva_vascular(20.0, 25.0, phi_vasc=1.0) == pytest.approx(20.0)


def test_dPth_com_reserva_vascular_diminui_com_phi_maior():
    d1 = dPth_com_reserva_vascular(20.0, 25.0, phi_vasc=1.0)
    d2 = dPth_com_reserva_vascular(20.0, 25.0, phi_vasc=1.3)
    assert d2 < d1
    assert d2 == pytest.approx(20.0 - 25.0 * 0.3)


def test_dPth_com_reserva_vascular_rejeita_phi_menor_que_1():
    with pytest.raises(ValueError):
        dPth_com_reserva_vascular(20.0, 25.0, phi_vasc=0.9)


def test_subgrupo_risco_damasceno_tipico_e_zero_risco_e_positivo():
    """O caso central do 4.4: no MESMO cenario basal, paciente tipico
    deve dar I=0 (consistente com OCT-A) e o subgrupo de risco de
    Damasceno deve dar I>0 (consistente com a associacao observada
    entre obstrucao carotidea e CRAO transitoria)."""
    r = subgrupo_risco_damasceno(
        K_tipico_mmHg_per_uL=0.34, K_alto_mmHg_per_uL=1.0,
        dV_uL=50.0, C_out_uL_min_mmHg=0.28,
        dPth_basal_mmHg=20.0, OPP_crit_ref_mmHg=25.0, phi_vasc_risco=1.3,
    )
    assert r["status_tipico"] == "OK"
    assert r["I_tipico_mmHg_min"] == 0.0
    assert r["status_risco"] == "OK"
    assert r["I_risco_mmHg_min"] > 0.0


def test_subgrupo_risco_damasceno_marca_regime_cronico_quando_dPth_risco_negativo():
    """phi_vasc muito alto pode empurrar dPth_risco para <=0 -- deve
    marcar como fora de dominio (regime cronico), nao devolver NaN."""
    r = subgrupo_risco_damasceno(
        K_tipico_mmHg_per_uL=0.34, K_alto_mmHg_per_uL=1.0,
        dV_uL=50.0, C_out_uL_min_mmHg=0.28,
        dPth_basal_mmHg=20.0, OPP_crit_ref_mmHg=25.0, phi_vasc_risco=2.0,
    )
    assert r["I_risco_mmHg_min"] is None
    assert "cronico" in r["status_risco"]


def test_controle_negativo_estrutura_e_valores_do_plano():
    c = controle_negativo_afinamento_mecanico()
    assert c["afinamento_percentual"] == pytest.approx(0.25)
    assert c["tempo_pico_min"] == 15
    assert c["tempo_resolucao_h"] == 48
    assert c["compativel_com_dose_isquemica_do_modelo"] is False


def test_MOPP_min_observado_constante_bate_com_o_plano():
    assert MOPP_MIN_OBSERVADO_OCT_A_MMHG == pytest.approx(31.0)
