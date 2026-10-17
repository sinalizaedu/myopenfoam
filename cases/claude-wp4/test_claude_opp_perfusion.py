"""
test_claude_opp_perfusion.py
==============================

Testes do modulo claude_opp_perfusion.py (item 4.1 do WP4, versao
revisada). Rodar com pytest a partir do venv de cases/wp0:

    cd cases/claude-wp4
    ../wp0/.venv/bin/python -m pytest -v test_claude_opp_perfusion.py
"""

import os
import sys

import numpy as np
import pytest

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_WP0_DIR = os.path.join(_THIS_DIR, "..", "wp0")
sys.path.insert(0, _THIS_DIR)
sys.path.insert(0, _WP0_DIR)

from claude_opp_perfusion import (  # noqa: E402
    opp_diastolica,
    opp_crit_efetivo,
    cadeia_completa,
    sensibilidade_fator_braquial,
)
from goldmann_iop_solver import Protocol, ThinShellPV, simulate, perfusion_metrics  # noqa: E402


def test_opp_diastolica_iop_constante():
    """IOP constante em 15 mmHg, PAD_oftalmica=70 -> OPP_diast=55 em todo t."""
    iop = np.full(10, 15.0)
    opp = opp_diastolica(iop, PAD_oftalmica_mmHg=70.0)
    assert np.allclose(opp, 55.0)


def test_opp_crit_efetivo_identidade_phi_1():
    assert opp_crit_efetivo(50.0, phi_vasc=1.0) == pytest.approx(50.0)


def test_opp_crit_efetivo_escala_com_phi():
    assert opp_crit_efetivo(50.0, phi_vasc=1.4) == pytest.approx(70.0)


def test_opp_crit_efetivo_rejeita_phi_menor_que_1():
    with pytest.raises(ValueError):
        opp_crit_efetivo(50.0, phi_vasc=0.9)


@pytest.fixture(scope="module")
def cenario_wp0():
    """Roda o solver do WP0 com os parametros padrao (cenario de pico
    real do proprio pipeline da tese, nao um exemplo sintetico) e
    devolve (t, IOP, proto)."""
    proto = Protocol()
    pv = ThinShellPV(R_m=0.012, t_m=0.6e-3, E_Pa=3e6, P0_mmHg=proto.P0_mmHg)
    t, V, P = simulate(proto, pv)
    return t, P, proto


def test_cadeia_completa_reproduz_perfusion_metrics_quando_phi_1(cenario_wp0):
    """Com phi_vasc=1.0, a cadeia revisada deve reproduzir exatamente os
    campos ja existentes de perfusion_metrics() do WP0 -- nao pode haver
    divergencia por reimplementacao paralela da mesma formula."""
    t, IOP, proto = cenario_wp0
    base = perfusion_metrics(t, IOP, proto, OPP_crit_mmHg=50.0, mopp_factor=2.0 / 3.0)
    revisada = cadeia_completa(t, IOP, proto, OPP_crit_ref_mmHg=50.0, phi_vasc=1.0)

    assert revisada["I_mmHg_min"] == pytest.approx(base["I_mmHg_min"])
    assert revisada["MOPP_min_mmHg"] == pytest.approx(base["MOPP_min_mmHg"])
    assert revisada["T_above_30_min"] == pytest.approx(base["T_above_30_min"])
    assert revisada["T_above_40_min"] == pytest.approx(base["T_above_40_min"])
    assert revisada["T_above_50_min"] == pytest.approx(base["T_above_50_min"])


def test_ordem_dos_tempos_acima_de_limiar(cenario_wp0):
    t, IOP, proto = cenario_wp0
    r = cadeia_completa(t, IOP, proto, OPP_crit_ref_mmHg=50.0)
    assert r["T_above_50_min"] <= r["T_above_40_min"] <= r["T_above_30_min"]
    assert r["T_above_30_min"] >= 0.0


def test_phi_vasc_maior_aumenta_ou_mantem_dose_isquemica(cenario_wp0):
    """Paciente com reserva vascular reduzida (phi_vasc>1) tem limiar
    efetivo mais alto -> deve acumular dose isquemica igual ou MAIOR,
    nunca menor, para o mesmo IOP(t)."""
    t, IOP, proto = cenario_wp0
    r_ref = cadeia_completa(t, IOP, proto, OPP_crit_ref_mmHg=50.0, phi_vasc=1.0)
    r_risco = cadeia_completa(t, IOP, proto, OPP_crit_ref_mmHg=50.0, phi_vasc=1.4)
    assert r_risco["I_mmHg_min"] >= r_ref["I_mmHg_min"]


def test_opp_diast_none_sem_pad_oftalmica(cenario_wp0):
    t, IOP, proto = cenario_wp0
    r = cadeia_completa(t, IOP, proto, OPP_crit_ref_mmHg=50.0)
    assert r["OPP_diast"] is None
    assert r["OPP_diast_min_mmHg"] is None


def test_sensibilidade_fator_braquial_cobre_faixa_padrao(cenario_wp0):
    t, IOP, proto = cenario_wp0
    sens = sensibilidade_fator_braquial(t, IOP, proto, OPP_crit_mmHg=50.0)
    assert len(sens) == 5

    # fator maior -> MOPP maior -> dose isquemica menor ou igual (monotonico)
    fatores_ordenados = sorted(sens.keys())
    doses = [sens[f]["I_mmHg_min"] for f in fatores_ordenados]
    assert all(doses[i] >= doses[i + 1] - 1e-9 for i in range(len(doses) - 1))
