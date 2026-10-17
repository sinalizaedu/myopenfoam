"""
test_claude_dose_isquemica.py
================================

Testes do modulo claude_dose_isquemica.py (item 4.2 do WP4).

    cd cases/claude-wp4
    ../wp0/.venv/bin/python -m pytest -v test_claude_dose_isquemica.py
"""

import os
import sys

import numpy as np
import pytest

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_WP0_DIR = os.path.join(_THIS_DIR, "..", "wp0")
sys.path.insert(0, _THIS_DIR)
sys.path.insert(0, _WP0_DIR)

from claude_dose_isquemica import (  # noqa: E402
    dose_isquemica,
    dose_isquemica_da_cadeia,
    curva_sensibilidade_opp_crit,
    validacao_fechada_H6,
    protocolo_com_P0_literatura,
)
from claude_opp_perfusion import cadeia_completa  # noqa: E402
from goldmann_iop_solver import Protocol, ThinShellPV, FriedenwaldPV, simulate  # noqa: E402


def test_dose_isquemica_zero_quando_sempre_acima_do_limiar():
    t = np.linspace(0, 10, 50)
    opp = np.full_like(t, 60.0)
    assert dose_isquemica(t, opp, OPP_crit_mmHg=50.0) == 0.0


def test_dose_isquemica_caso_analitico_trivial():
    """Deficit constante de 10 mmHg por 5 min -> I = 50 mmHg.min (regra do trapezio exata p/ deficit constante)."""
    t = np.array([0.0, 5.0])
    opp = np.array([40.0, 40.0])
    assert dose_isquemica(t, opp, OPP_crit_mmHg=50.0) == pytest.approx(50.0)


@pytest.fixture(scope="module")
def cenario_wp0():
    proto = Protocol()
    pv = ThinShellPV(R_m=0.012, t_m=0.6e-3, E_Pa=3e6, P0_mmHg=proto.P0_mmHg)
    t, V, P = simulate(proto, pv)
    return t, P, proto


def test_dose_isquemica_da_cadeia_bate_com_wp0(cenario_wp0):
    """I via MOPP calculado por este modulo tem que ser identico ao
    I_mmHg_min que cadeia_completa() (4.1) ja devolve -- mesma formula,
    mesmos dados, dois caminhos de codigo."""
    t, P, proto = cenario_wp0
    chain = cadeia_completa(t, P, proto, OPP_crit_ref_mmHg=50.0)
    d = dose_isquemica_da_cadeia(t, chain)
    assert d["I_MOPP_mmHg_min"] == pytest.approx(d["I_MOPP_ja_no_WP0"])
    assert d["I_MOPP_mmHg_min"] == pytest.approx(chain["I_mmHg_min"])


def test_dose_isquemica_da_cadeia_opp_diast_none_quando_cadeia_sem_ela():
    # cadeia_completa (versao atual) sempre calcula OPP_diast (auto-estimado);
    # este teste garante que, se um dia voltar a ser None, o modulo lida bem.
    fake_chain = {
        "MOPP": np.array([10.0, 20.0]),
        "OPP_diast": None,
        "OPP_crit_efetivo_mmHg": 50.0,
    }
    d = dose_isquemica_da_cadeia(np.array([0.0, 1.0]), fake_chain)
    assert d["I_OPP_diast_mmHg_min"] is None
    assert d["I_MOPP_mmHg_min"] > 0


def test_curva_sensibilidade_monotonica_decrescente_no_limiar(cenario_wp0):
    """Dose isquemica deve ser nao-decrescente conforme OPP_crit aumenta
    (limiar mais alto -> mais tempo abaixo dele)."""
    t, P, proto = cenario_wp0
    chain = cadeia_completa(t, P, proto, OPP_crit_ref_mmHg=50.0)
    curva = curva_sensibilidade_opp_crit(t, chain["MOPP"])
    limiares = sorted(curva.keys())
    doses = [curva[th] for th in limiares]
    assert all(doses[i] <= doses[i + 1] + 1e-9 for i in range(len(doses) - 1))


def test_protocolo_com_P0_literatura_remove_deriva_basal():
    """ACHADO desta sessao: Protocol() padrao do WP0 diverge de P0 mesmo
    sem injecao. protocolo_com_P0_literatura() deve corrigir isso."""
    proto_bug = Protocol(V_inj_uL=0.0, t_end_min=100.0)
    pv = ThinShellPV(R_m=0.012, t_m=0.6e-3, E_Pa=3e6, P0_mmHg=proto_bug.P0_mmHg)
    _, _, P_bug = simulate(proto_bug, pv, n_points=500)
    # confirma que o bug existe nos parametros default (documentado, nao corrigido aqui)
    assert abs(P_bug[-1] - proto_bug.P0_mmHg) > 3.0

    proto_ok = protocolo_com_P0_literatura(V_inj_uL=0.0, t_end_min=100.0)
    pv_ok = ThinShellPV(R_m=0.012, t_m=0.6e-3, E_Pa=3e6, P0_mmHg=proto_ok.P0_mmHg)
    _, _, P_ok = simulate(proto_ok, pv_ok, n_points=500)
    assert P_ok[-1] == pytest.approx(proto_ok.P0_mmHg, abs=0.05)


def test_validacao_fechada_H6_bate_dentro_de_5_porcento():
    """Com o protocolo Goldmann-consistente, K constante (ThinShellPV) e
    sem paracentese/refluxo, o 𝓘 numerico deve bater com a formula
    fechada de H6 dentro de ~5% (residual esperado: rampa de injecao de
    6s vs bolus instantaneo assumido na formula fechada)."""
    proto = protocolo_com_P0_literatura()
    pv = ThinShellPV(R_m=0.012, t_m=0.6e-3, E_Pa=3e6, P0_mmHg=proto.P0_mmHg)
    v = validacao_fechada_H6(proto, pv, OPP_crit_ref_mmHg=38.0)
    assert v["erro_relativo"] < 0.05


def test_validacao_fechada_H6_rejeita_K_nao_constante():
    proto = protocolo_com_P0_literatura()
    pv_friedenwald = FriedenwaldPV(Kf_per_uL=0.0126, P0_mmHg=proto.P0_mmHg)
    with pytest.raises(ValueError):
        validacao_fechada_H6(proto, pv_friedenwald, OPP_crit_ref_mmHg=38.0)


def test_validacao_fechada_H6_rejeita_paracentese_ligada():
    proto = protocolo_com_P0_literatura(par_enabled=True)
    pv = ThinShellPV(R_m=0.012, t_m=0.6e-3, E_Pa=3e6, P0_mmHg=proto.P0_mmHg)
    with pytest.raises(ValueError):
        validacao_fechada_H6(proto, pv, OPP_crit_ref_mmHg=38.0)


def test_validacao_fechada_H6_rejeita_limiar_abaixo_do_basal():
    """dP_th <= 0 (limiar ja abaixo da MOPP basal) deve levantar
    ValueError, nao devolver NaN."""
    proto = protocolo_com_P0_literatura()
    pv = ThinShellPV(R_m=0.012, t_m=0.6e-3, E_Pa=3e6, P0_mmHg=proto.P0_mmHg)
    with pytest.raises(ValueError):
        validacao_fechada_H6(proto, pv, OPP_crit_ref_mmHg=50.0)
