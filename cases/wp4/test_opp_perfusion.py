"""Testes WP4.1 — cadeia IOP → OPP."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

WP4 = Path(__file__).resolve().parent
WP0 = WP4.parent / "wp0"
sys.path.insert(0, str(WP4))
sys.path.insert(0, str(WP0))

from goldmann_iop_solver import FriedenwaldPV, Protocol, simulate  # noqa: E402
from opp_perfusion import (  # noqa: E402
    aplicar_cadeia,
    mopp,
    opp_crit_efetivo,
    opp_diastolica,
)


def test_mopp_caso_trivial_constante():
    """IOP=15, PAS=120, PAD=80 → MOPP manual."""
    pas, pad = 120.0, 80.0
    iop = 15.0
    map_esperado = pad + (pas - pad) / 3.0  # 93.333...
    esperado = (2.0 / 3.0) * map_esperado - iop
    obtido = mopp(iop, pas, pad)
    assert obtido == pytest.approx(esperado, rel=1e-12)
    assert esperado == pytest.approx(47.22222222222222, rel=1e-9)


def test_mopp_vetorizado():
    iop = np.array([15.0, 20.0, 25.0])
    out = mopp(iop, 120.0, 80.0)
    assert out.shape == (3,)
    assert out[0] == pytest.approx(mopp(15.0, 120.0, 80.0))


def test_opp_diastolica():
    pad_oft = (2.0 / 3.0) * 80.0
    assert opp_diastolica(15.0, pad_oft) == pytest.approx(pad_oft - 15.0)


def test_opp_crit_efetivo_identidade():
    assert opp_crit_efetivo(50.0, phi_vasc=1.0) == 50.0
    assert opp_crit_efetivo(40.0, phi_vasc=1.25) == pytest.approx(50.0)


def test_opp_crit_efetivo_rejeita_phi_menor_que_um():
    with pytest.raises(ValueError, match="phi_vasc"):
        opp_crit_efetivo(50.0, phi_vasc=0.9)


def test_cadeia_cenario_wp0_pico():
    """IVI 50 uL, Friedenwald Kf conservador — pico ~40–50 mmHg, tempos coerentes."""
    pv = FriedenwaldPV(Kf_per_uL=0.0126, P0_mmHg=15.0, V0_uL=0.0)
    proto = Protocol(t_end_min=30.0, frac_uveoscleral=0.20, SBP_mmHg=120.0, DBP_mmHg=70.0)
    t, _v, iop = simulate(proto, pv, n_points=4000)

    chain = aplicar_cadeia(
        t,
        iop,
        pas=proto.SBP_mmHg,
        pad=proto.DBP_mmHg,
        opp_crit_ref=50.0,
        fator_braquial=2.0 / 3.0,
        phi_vasc=1.0,
    )

    t30, t40, t50 = chain["T_acima_30"], chain["T_acima_40"], chain["T_acima_50"]
    assert t30 >= 0.0 and t40 >= 0.0 and t50 >= 0.0
    assert t50 <= t40 + 1e-9
    assert t40 <= t30 + 1e-9
    assert float(iop.max()) > 40.0
    assert chain["opp_crit_efetivo"] == 50.0
    assert chain["opp_minima_atingida"] == pytest.approx(chain["mopp_min_mmHg"])
    assert chain["opp_minima_atingida"] < chain["MAP_mmHg"] * (2.0 / 3.0) - 15.0 + 1.0


def test_aplicar_cadeia_shapes():
    t = np.linspace(0, 10, 50)
    iop = np.full_like(t, 15.0)
    out = aplicar_cadeia(t, iop, pas=120, pad=80, opp_crit_ref=45.0)
    assert out["mopp"].shape == t.shape
    assert out["opp_diast"].shape == t.shape
    assert out["T_acima_30"] == 0.0
