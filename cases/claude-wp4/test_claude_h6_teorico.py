"""
test_claude_h6_teorico.py
===========================

Testes do modulo claude_h6_teorico.py (item 4.3 do WP4).

    cd cases/claude-wp4
    ../wp0/.venv/bin/python -m pytest -v test_claude_h6_teorico.py
"""
import os
import sys

import numpy as np
import pytest

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_WP0_DIR = os.path.join(_THIS_DIR, "..", "wp0")
sys.path.insert(0, _THIS_DIR)
sys.path.insert(0, _WP0_DIR)

from claude_h6_teorico import (  # noqa: E402
    dose_fechada_H6,
    K_crit,
    limite_superior_dV_sobre_C,
    curva_I_vs_K,
    curva_I_vs_dPth,
    K_crit_vs_dPth,
    escala_C_out,
    verificar_escala_linear_C_out,
)
from claude_dose_isquemica import (  # noqa: E402
    protocolo_com_P0_literatura,
    validacao_fechada_H6,
)
from goldmann_iop_solver import ThinShellPV  # noqa: E402


def test_K_crit_exemplo_do_plano():
    """Plano de tese (Secao 4.3): dPth=15 mmHg, dV=50 uL -> K_crit=0.30 mmHg/uL."""
    assert K_crit(dPth_mmHg=15.0, dV_uL=50.0) == pytest.approx(0.30, abs=1e-9)


def test_K_crit_rejeita_dPth_nao_positivo():
    with pytest.raises(ValueError):
        K_crit(dPth_mmHg=0.0, dV_uL=50.0)
    with pytest.raises(ValueError):
        K_crit(dPth_mmHg=-5.0, dV_uL=50.0)


def test_dose_zero_exatamente_abaixo_de_K_crit():
    """Consequencia 2: K < K_crit -> I EXATAMENTE zero (nao so pequeno)."""
    dPth, dV, C = 15.0, 50.0, 0.28
    kc = K_crit(dPth, dV)
    assert dose_fechada_H6(kc * 0.5, dV, C, dPth) == 0.0
    assert dose_fechada_H6(kc * 0.999, dV, C, dPth) == 0.0


def test_dose_positiva_exatamente_acima_de_K_crit():
    dPth, dV, C = 15.0, 50.0, 0.28
    kc = K_crit(dPth, dV)
    assert dose_fechada_H6(kc * 1.5, dV, C, dPth) > 0.0


def test_dose_continua_em_K_crit():
    """dose_fechada_H6 deve ser continua em K=K_crit (dP0=dPth -> ln(1)=0 -> I=0),
    nao ter um salto na fronteira."""
    dPth, dV, C = 15.0, 50.0, 0.28
    kc = K_crit(dPth, dV)
    I_um_pouco_abaixo = dose_fechada_H6(kc * 0.9999, dV, C, dPth)
    I_um_pouco_acima = dose_fechada_H6(kc * 1.0001, dV, C, dPth)
    assert I_um_pouco_abaixo == 0.0
    assert I_um_pouco_acima == pytest.approx(0.0, abs=1e-3)


def test_dose_fechada_rejeita_dPth_nao_positivo():
    with pytest.raises(ValueError):
        dose_fechada_H6(0.5, 50.0, 0.28, dPth_mmHg=0.0)
    with pytest.raises(ValueError):
        dose_fechada_H6(0.5, 50.0, 0.28, dPth_mmHg=-1.0)


def test_consequencia_1_satura_em_dV_sobre_C_para_K_grande():
    """Sem limiar (K->infinito), I -> dV/C (limite superior assintotico)."""
    dPth, dV, C = 15.0, 50.0, 0.28
    limite = limite_superior_dV_sobre_C(dV, C)
    I_K_grande = dose_fechada_H6(1e6, dV, C, dPth)
    assert I_K_grande == pytest.approx(limite, rel=1e-4)
    # e deve ser MENOR que o limite para qualquer K finito (a formula nunca ultrapassa)
    for K in (0.31, 0.5, 1.0, 10.0, 100.0):
        assert dose_fechada_H6(K, dV, C, dPth) < limite


def test_curva_I_vs_K_monotonica_crescente():
    dPth, dV, C = 15.0, 50.0, 0.28
    curva = curva_I_vs_K([0.1, 0.2, 0.30, 0.31, 0.5, 1.0, 5.0], dV, C, dPth)
    vals = list(curva.values())
    assert all(vals[i] <= vals[i + 1] + 1e-9 for i in range(len(vals) - 1))


def test_curva_I_vs_dPth_marca_None_fora_de_dominio():
    curva = curva_I_vs_dPth([-5.0, 0.0, 5.0, 15.0], K_mmHg_per_uL=0.5, dV_uL=50.0,
                             C_out_uL_min_mmHg=0.28)
    assert curva[-5.0] is None
    assert curva[0.0] is None
    assert curva[5.0] is not None
    assert curva[15.0] is not None


def test_K_crit_vs_dPth_marca_None_fora_de_dominio():
    curva = K_crit_vs_dPth([-5.0, 0.0, 10.0, 20.0], dV_uL=50.0)
    assert curva[-5.0] is None
    assert curva[0.0] is None
    assert curva[10.0] == pytest.approx(0.20)
    assert curva[20.0] == pytest.approx(0.40)


def test_consequencia_3_escala_linear_em_C_out():
    """C_out escala I linearmente -- I(C/2) deve ser EXATAMENTE 2x I(C)."""
    v = verificar_escala_linear_C_out(K_mmHg_per_uL=0.5, dV_uL=50.0, dPth_mmHg=15.0,
                                       C_ref_uL_min_mmHg=0.28, fator=0.5)
    assert v["razao_observada"] == pytest.approx(v["razao_esperada"], rel=1e-9)
    assert v["razao_observada"] == pytest.approx(2.0, rel=1e-9)


def test_escala_C_out_tabela_consistente_com_verificacao():
    tab = escala_C_out(K_mmHg_per_uL=0.5, dV_uL=50.0, dPth_mmHg=15.0,
                        C_out_range_uL_min_mmHg=[0.14, 0.28, 0.56])
    assert tab[0.14] == pytest.approx(2.0 * tab[0.28], rel=1e-9)
    assert tab[0.56] == pytest.approx(0.5 * tab[0.28], rel=1e-9)


def test_dose_fechada_H6_bate_com_validacao_fechada_H6_do_4_2():
    """Consistencia entre 4.2 e 4.3: dose_fechada_H6 (parametros primitivos)
    deve dar o MESMO I_fechado que validacao_fechada_H6 (Protocol/PV
    concretos) calcula internamente, no mesmo cenario -- duas
    implementacoes da mesma formula, caminhos de codigo diferentes."""
    proto = protocolo_com_P0_literatura("humano")
    pv = ThinShellPV(R_m=0.012, t_m=0.6e-3, E_Pa=3e6, P0_mmHg=proto.P0_mmHg)
    v = validacao_fechada_H6(proto, pv, OPP_crit_ref_mmHg=38.0)

    I_via_4_3 = dose_fechada_H6(
        K_mmHg_per_uL=v["K_mmHg_per_uL"],
        dV_uL=proto.V_inj_uL,
        C_out_uL_min_mmHg=proto.C_out_uL_min_mmHg,
        dPth_mmHg=v["dP_th_mmHg"],
    )
    assert I_via_4_3 == pytest.approx(v["I_fechado_mmHg_min"], rel=1e-9)
