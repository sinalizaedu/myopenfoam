"""Testes WP4.2 — dose isquêmica por evento (𝓘)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

WP4 = Path(__file__).resolve().parent
WP0 = WP4.parent / "wp0"
sys.path.insert(0, str(WP4))
sys.path.insert(0, str(WP0))

from dose_isquemica import (  # noqa: E402
    curva_sensibilidade_opp_crit,
    derivar_P0_equilibrio,
    dose_isquemica,
    dose_isquemica_da_cadeia,
    protocolo_com_P0_literatura,
    validacao_fechada_H6,
)
from goldmann_iop_solver import (  # noqa: E402
    FriedenwaldPV,
    Protocol,
    ThinShellPV,
    perfusion_metrics,
    simulate,
)
from opp_perfusion import aplicar_cadeia  # noqa: E402


def test_dose_isquemica_zero_quando_sempre_acima_do_limiar():
    t = np.linspace(0, 10, 50)
    opp = np.full_like(t, 60.0)
    assert dose_isquemica(t, opp, OPP_crit_mmHg=50.0) == 0.0


def test_dose_isquemica_caso_analitico_trivial():
    """Déficit constante de 10 mmHg por 5 min → I = 50 mmHg·min (trapézio exato)."""
    t = np.array([0.0, 5.0])
    opp = np.array([40.0, 40.0])
    assert dose_isquemica(t, opp, OPP_crit_mmHg=50.0) == pytest.approx(50.0)


def test_dose_isquemica_bate_com_wp0_perfusion_metrics():
    """Mesma fórmula do WP0 (phi=1): I via aplicar_cadeia(4.1)+dose_isquemica
    deve ser idêntico ao I_mmHg_min de perfusion_metrics."""
    proto = Protocol()
    pv = ThinShellPV(R_m=0.012, t_m=0.6e-3, E_Pa=3e6, P0_mmHg=proto.P0_mmHg)
    t, _V, P = simulate(proto, pv)
    ref = perfusion_metrics(t, P, proto, OPP_crit_mmHg=50.0)["I_mmHg_min"]
    chain = aplicar_cadeia(t, P, pas=proto.SBP_mmHg, pad=proto.DBP_mmHg,
                           opp_crit_ref=50.0)
    assert dose_isquemica(t, chain["mopp"], 50.0) == pytest.approx(ref, rel=1e-12)


def test_dose_isquemica_da_cadeia_duas_vias():
    proto = Protocol()
    pv = ThinShellPV(R_m=0.012, t_m=0.6e-3, E_Pa=3e6, P0_mmHg=proto.P0_mmHg)
    t, _V, P = simulate(proto, pv)
    chain = aplicar_cadeia(t, P, pas=proto.SBP_mmHg, pad=proto.DBP_mmHg,
                           opp_crit_ref=50.0)
    d = dose_isquemica_da_cadeia(t, chain)
    assert d["I_MOPP_mmHg_min"] >= 0.0
    assert d["I_OPP_diast_mmHg_min"] >= d["I_MOPP_mmHg_min"]  # OPP_diast <= MOPP ponto a ponto


def test_curva_sensibilidade_monotonica_nao_decrescente():
    t = np.linspace(0, 10, 100)
    opp = 40.0 + 5.0 * np.sin(t)
    curva = curva_sensibilidade_opp_crit(t, opp)
    limiares = sorted(curva.keys())
    doses = [curva[th] for th in limiares]
    assert all(doses[i] <= doses[i + 1] + 1e-9 for i in range(len(doses) - 1))


def test_derivar_P0_equilibrio_valores_literatura():
    """Humano 16,86 e coelho 26,68 mmHg — mesmos valores do relatório WP0."""
    assert derivar_P0_equilibrio(10.0, 2.4, 0.28, 0.20) == pytest.approx(16.857, abs=1e-3)
    assert derivar_P0_equilibrio(15.5, 3.06, 0.26, 0.05) == pytest.approx(26.681, abs=1e-3)


def test_protocolo_com_P0_literatura_remove_deriva_basal():
    """Com P0 derivado, IOP não deriva sem injeção; combo legado P0=15/Q=3 deriva."""
    proto_bug = Protocol(
        P0_mmHg=15.0,
        Q_prod_uL_min=3.0,
        reflux_mode="none",
        V_inj_uL=0.0,
        t_end_min=100.0,
    )
    pv = ThinShellPV(R_m=0.012, t_m=0.6e-3, E_Pa=3e6, P0_mmHg=proto_bug.P0_mmHg)
    _, _, P_bug = simulate(proto_bug, pv, n_points=500)
    assert abs(P_bug[-1] - proto_bug.P0_mmHg) > 3.0

    proto_ok = protocolo_com_P0_literatura("humano", V_inj_uL=0.0, t_end_min=100.0)
    pv_ok = ThinShellPV(R_m=0.012, t_m=0.6e-3, E_Pa=3e6, P0_mmHg=proto_ok.P0_mmHg)
    _, _, P_ok = simulate(proto_ok, pv_ok, n_points=500)
    assert P_ok[-1] == pytest.approx(proto_ok.P0_mmHg, abs=0.05)


def test_validacao_fechada_H6_bate_dentro_de_5_porcento():
    """K constante, sem paracentese/refluxo: 𝓘 numérico vs fórmula fechada.
    Residual esperado: rampa de injeção de 6 s vs bólus instantâneo."""
    proto = protocolo_com_P0_literatura("humano")
    pv = ThinShellPV(R_m=0.012, t_m=0.6e-3, E_Pa=3e6, P0_mmHg=proto.P0_mmHg)
    v = validacao_fechada_H6(proto, pv, OPP_crit_ref_mmHg=38.0)
    assert v["erro_relativo"] < 0.05


def test_validacao_fechada_H6_rejeita_K_nao_constante():
    proto = protocolo_com_P0_literatura("humano")
    pv_f = FriedenwaldPV(Kf_per_uL=0.0126, P0_mmHg=proto.P0_mmHg)
    with pytest.raises(ValueError):
        validacao_fechada_H6(proto, pv_f, OPP_crit_ref_mmHg=38.0)


def test_validacao_fechada_H6_rejeita_paracentese_ligada():
    proto = protocolo_com_P0_literatura("humano", par_enabled=True)
    pv = ThinShellPV(R_m=0.012, t_m=0.6e-3, E_Pa=3e6, P0_mmHg=proto.P0_mmHg)
    with pytest.raises(ValueError):
        validacao_fechada_H6(proto, pv, OPP_crit_ref_mmHg=38.0)


def test_validacao_fechada_H6_rejeita_limiar_abaixo_do_basal():
    """dP_th ≤ 0 (limiar já abaixo da MOPP basal) → ValueError, não NaN."""
    proto = protocolo_com_P0_literatura("humano")
    pv = ThinShellPV(R_m=0.012, t_m=0.6e-3, E_Pa=3e6, P0_mmHg=proto.P0_mmHg)
    with pytest.raises(ValueError):
        validacao_fechada_H6(proto, pv, OPP_crit_ref_mmHg=50.0)
