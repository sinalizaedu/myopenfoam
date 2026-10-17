"""Testes WP4.3 — H6 teórico em primitivos e as três consequências."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

WP4 = Path(__file__).resolve().parent
WP0 = WP4.parent / "wp0"
sys.path.insert(0, str(WP4))
sys.path.insert(0, str(WP0))

from dose_isquemica import protocolo_com_P0_literatura, validacao_fechada_H6  # noqa: E402
from goldmann_iop_solver import ThinShellPV  # noqa: E402
from h6_teorico import (  # noqa: E402
    K_crit,
    K_crit_vs_dPth,
    curva_I_vs_dPth,
    curva_I_vs_K,
    dose_fechada_H6,
    escala_C_out,
    limite_superior_dV_sobre_C,
    verificar_escala_linear_C_out,
)

# Cenário do plano: dPth=15 mmHg, ΔV=50 µL, C=0,28 µL/min/mmHg
DPTH, DV, C = 15.0, 50.0, 0.28


def test_K_crit_reproduz_exemplo_do_plano():
    """dPth=15, ΔV=50 → K_crit = 0,30 mmHg/µL (valor citado no plano)."""
    assert K_crit(DPTH, DV) == pytest.approx(0.30)


def test_dose_zero_abaixo_de_K_crit_positiva_acima():
    K_c = K_crit(DPTH, DV)
    assert dose_fechada_H6(K_c * 0.97, DV, C, DPTH) == 0.0
    assert dose_fechada_H6(K_c, DV, C, DPTH) == 0.0  # fronteira: K·ΔV == dPth
    assert dose_fechada_H6(K_c * 1.03, DV, C, DPTH) > 0.0


def test_dose_continua_na_fronteira_K_crit():
    """I → 0 quando K → K_crit por cima (transição quase-binária, mas contínua)."""
    K_c = K_crit(DPTH, DV)
    I_logo_acima = dose_fechada_H6(K_c * (1.0 + 1e-4), DV, C, DPTH)
    assert I_logo_acima < 1e-4


def test_saturacao_em_dV_sobre_C():
    """Consequência 1: K→∞ ⇒ I → ΔV/C (K cancela)."""
    lim = limite_superior_dV_sobre_C(DV, C)
    assert lim == pytest.approx(178.571, abs=1e-3)
    assert dose_fechada_H6(1e6, DV, C, DPTH) == pytest.approx(lim, rel=1e-3)


def test_curva_I_vs_K_monotonica_nao_decrescente():
    Ks = [0.05, 0.10, 0.20, 0.30, 0.31, 0.40, 0.60, 1.00, 3.00]
    curva = curva_I_vs_K(Ks, DV, C, DPTH)
    Is = [curva[float(K)] for K in Ks]
    assert all(Is[i] <= Is[i + 1] + 1e-12 for i in range(len(Is) - 1))
    assert Is[0] == 0.0 and Is[-1] > 0.0


def test_curvas_marcam_None_fora_de_dominio():
    faixa = [-5.0, 0.0, 5.0, 15.0]
    curva_I = curva_I_vs_dPth(faixa, 0.5, DV, C)
    assert curva_I[-5.0] is None and curva_I[0.0] is None
    assert curva_I[5.0] is not None and curva_I[15.0] is not None
    curva_Kc = K_crit_vs_dPth(faixa, DV)
    assert curva_Kc[-5.0] is None and curva_Kc[0.0] is None
    assert curva_Kc[15.0] == pytest.approx(0.30)


def test_dose_fechada_H6_rejeita_dPth_nao_positivo():
    with pytest.raises(ValueError):
        dose_fechada_H6(0.5, DV, C, 0.0)
    with pytest.raises(ValueError):
        dose_fechada_H6(0.5, DV, C, -3.0)
    with pytest.raises(ValueError):
        K_crit(0.0, DV)
    with pytest.raises(ValueError):
        K_crit(DPTH, 0.0)


def test_escala_linear_C_out_exata():
    """Consequência 3: I(C/2) = 2·I(C) EXATAMENTE, para qualquer K."""
    for K in (0.31, 0.5, 1.0, 3.0):
        v = verificar_escala_linear_C_out(K, DV, DPTH, C_ref_uL_min_mmHg=C, fator=0.5)
        assert v["razao_observada"] == pytest.approx(v["razao_esperada"], rel=1e-9)


def test_escala_C_out_tabela_consistente_com_verificacao():
    tab = escala_C_out(0.5, DV, DPTH, [0.14, 0.28])
    v = verificar_escala_linear_C_out(0.5, DV, DPTH, C_ref_uL_min_mmHg=C, fator=0.5)
    assert tab[0.28] == pytest.approx(v["I_ref_mmHg_min"])
    assert tab[0.14] == pytest.approx(v["I_teste_mmHg_min"])


def test_consistencia_com_validacao_fechada_H6_do_4_2():
    """dose_fechada_H6 (primitivos) deve dar o MESMO I_fechado que
    validacao_fechada_H6 (4.2, Protocol/PV concretos) — mesma fórmula,
    dois caminhos de código. Tolerância 1e-9 (ambas analíticas)."""
    proto = protocolo_com_P0_literatura("humano")
    pv = ThinShellPV(R_m=0.012, t_m=0.6e-3, E_Pa=3e6, P0_mmHg=proto.P0_mmHg)
    v = validacao_fechada_H6(proto, pv, OPP_crit_ref_mmHg=38.0)
    from dose_isquemica import delta_V_bolus_fechada

    I_primitivos = dose_fechada_H6(
        v["K_mmHg_per_uL"],
        delta_V_bolus_fechada(proto),
        proto.C_out_uL_min_mmHg,
        v["dP_th_mmHg"],
    )
    assert I_primitivos == pytest.approx(v["I_fechado_mmHg_min"], rel=1e-9)
