"""
claude_opp_perfusion.py
========================

Extensao do item 4.1 do WP4 (cadeia IOP(t) -> OPP(t) -> metrica de
isquemia), construida sobre o solver 0D existente em
cases/wp0/goldmann_iop_solver.py (Protocol, simulate, perfusion_metrics,
ischemic_dose_curve). NAO MODIFICA esse arquivo -- so importa dele.

O WP0 ja implementa: MOPP(t), dose isquemica I(OPP_crit), T_>30/40/50,
e ischemic_dose_curve() varrendo OPP_crit. Este modulo adiciona so o que
faltava, conforme a proposta revisada do WP4
(ver cases/claude-wp4/claude-wp4-proposta-teorica.md):

1. OPP_diast(t) = PAD_oftalmica - IOP(t)
   A outra definicao padrao de pressao de perfusao ocular, complementar
   a MOPP.

2. Fator de reserva vascular paciente-especifico phi_vasc >= 1, que
   modula o limiar efetivo:
       OPP_crit_efetivo = OPP_crit_ref * phi_vasc
   Motivado por Damasceno et al. (2022): 66.6% dos casos de CRAO
   transitoria pos-IVI (18/4069 injecoes, 0.44%) tinham obstrucao
   carotidea >=70%, sugerindo que o limiar isquemico efetivo nao e
   universal -- e paciente-dependente via reserva vascular.
   phi_vasc e um PARAMETRO DE SENSIBILIDADE, nao um valor medido/calibrado.

3. cadeia_completa(): chama perfusion_metrics() do WP0 com o OPP_crit ja
   ajustado por phi_vasc, e acrescenta OPP_diast(t) ao resultado.

4. sensibilidade_fator_braquial(): varre o fator 2/3 (convencao de MOPP,
   nunca medida direta) na faixa 0.5-0.8 exigida pelo plano de tese.

Ver cases/claude-wp4/README.md para as formulas, convencoes e ressalvas.
"""

from __future__ import annotations

import os
import sys
from typing import Optional

import numpy as np

_WP0_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "wp0")
if _WP0_DIR not in sys.path:
    sys.path.insert(0, _WP0_DIR)

from goldmann_iop_solver import (  # noqa: E402
    Protocol,
    perfusion_metrics,
)


def opp_diastolica(IOP_mmHg: np.ndarray, PAD_oftalmica_mmHg: float) -> np.ndarray:
    """
    OPP_diast(t) = PAD_oftalmica - IOP(t)   [mmHg]

    Definicao alternativa a MOPP, usada em parte da literatura de
    glaucoma/perfusao ocular. PAD_oftalmica (pressao arterial diastolica
    NA ARTERIA OFTALMICA) nao e o mesmo que PAD braquial -- se so tiver
    a PAD braquial (a que sai do protocolo, proto.DBP_mmHg), use como
    aproximacao de ordem zero e declare isso explicitamente na tese, do
    mesmo jeito que o fator 2/3 de MOPP ja e declarado como convencao.
    """
    IOP_mmHg = np.asarray(IOP_mmHg, dtype=float)
    return PAD_oftalmica_mmHg - IOP_mmHg


def opp_crit_efetivo(OPP_crit_ref_mmHg: float, phi_vasc: float = 1.0) -> float:
    """
    OPP_crit_efetivo = OPP_crit_ref * phi_vasc

    phi_vasc >= 1: fator de reserva vascular paciente-especifico.
      phi_vasc = 1.0  -> sem comorbidade vascular conhecida (padrao)
      phi_vasc > 1.0  -> reserva vascular reduzida (ex.: obstrucao
                         carotidea significativa, diabetes avancada) --
                         eleva o limiar efetivo, logo o MESMO OPP(t) fica
                         mais perto (ou abaixo) do limiar de dano.

    Nao ha calibracao direta na literatura para phi_vasc -- trate como
    parametro de sensibilidade / estratificacao de risco relativo, nunca
    como numero calibrado.

    Levanta ValueError se phi_vasc < 1.0 (nao ha racional fisiologico
    para reserva vascular reduzir o limiar efetivo abaixo do valor de
    referencia).
    """
    if phi_vasc < 1.0:
        raise ValueError(f"phi_vasc deve ser >= 1.0, recebido {phi_vasc}")
    return OPP_crit_ref_mmHg * phi_vasc


def pad_oftalmica_from_braquial(PAD_mmHg: float, fator_braquial_oftalmica: float = 2.0 / 3.0) -> float:
    """
    Estimativa de PAD na arteria oftalmica a partir da PAD braquial,
    reaproveitando o MESMO fator de escala ja usado para MAP -> MOPP.

    CONVENCAO RECONCILIADA com a implementacao paralela feita no Composer
    (cases/wp4/opp_perfusion.py): quando nao ha PAD oftalmica medida
    diretamente, escala-se a PAD braquial pelo mesmo fator
    braquial->oftalmica de MOPP, em vez de usar a PAD braquial sem
    escalar. Nenhuma das duas convencoes tem calibracao direta na
    literatura -- mas usar o MESMO fator do resto da cadeia e mais
    consistente internamente do que introduzir uma segunda convencao
    (escala 1.0) sem justificativa propria. Declarar isso na tese.
    """
    return fator_braquial_oftalmica * PAD_mmHg


def cadeia_completa(t_min: np.ndarray, IOP_mmHg: np.ndarray, proto: Protocol,
                     OPP_crit_ref_mmHg: float = 50.0,
                     mopp_factor: float = 2.0 / 3.0,
                     phi_vasc: float = 1.0,
                     PAD_oftalmica_mmHg: Optional[float] = None,
                     estimar_PAD_oftalmica: bool = False) -> dict:
    """
    Cadeia IOP(t) -> {MOPP(t), OPP_diast(t)} -> metrica de isquemia,
    item 4.1 do WP4 (versao revisada).

    Reusa perfusion_metrics() do WP0 (MOPP, I, T_>30/40/50) com o
    OPP_crit ja ajustado por phi_vasc, e adiciona OPP_diast(t).

    PAD_oftalmica_mmHg: PAD na arteria oftalmica, se medida.

    estimar_PAD_oftalmica (padrao False): se True e PAD_oftalmica_mmHg for
    None, estima PAD_oft = mopp_factor * proto.DBP_mmHg -- a convencao do
    modulo do Composer (cases/wp4/opp_perfusion.py).

    POR QUE O PADRAO E False (decisao de 03/10, ver claude-AUDITORIA-WP4-5-6.md):
    o fator 2/3 e convencao da literatura para a queda da pressao MEDIA da
    braquial ate a oftalmica. Aplica-lo a DIASTOLICA e uma suposicao
    ADICIONAL, sem fonte, e a OPP diastolica alimenta a dose isquemica do
    item 4.2. Pela regra do plano ("se nao houver fonte, o parametro nao
    entra"), o padrao e NAO estimar: OPP_diast fica None e quem quiser a
    convencao do Composer pede explicitamente com estimar_PAD_oftalmica=True.
    Isso tambem mantem test_opp_diast_none_sem_pad_oftalmica valido.

    Retorna um dict com todas as chaves de perfusion_metrics() do WP0,
    mais:
      - "OPP_crit_ref_mmHg", "phi_vasc", "OPP_crit_efetivo_mmHg"
      - "OPP_diast" (array) e "OPP_diast_min_mmHg" (float)
      - "PAD_oftalmica_mmHg" (a estimativa/valor usado, para auditoria)
    """
    opp_crit_eff = opp_crit_efetivo(OPP_crit_ref_mmHg, phi_vasc)

    base = perfusion_metrics(t_min, IOP_mmHg, proto,
                              OPP_crit_mmHg=opp_crit_eff,
                              mopp_factor=mopp_factor)

    base["OPP_crit_ref_mmHg"] = OPP_crit_ref_mmHg
    base["phi_vasc"] = phi_vasc
    base["OPP_crit_efetivo_mmHg"] = opp_crit_eff

    if PAD_oftalmica_mmHg is not None:
        pad_oft = PAD_oftalmica_mmHg
        origem_pad = "medida/informada"
    elif estimar_PAD_oftalmica:
        pad_oft = pad_oftalmica_from_braquial(proto.DBP_mmHg, mopp_factor)
        origem_pad = f"ESTIMADA como {mopp_factor:.4f} x PAD braquial (suposicao sem fonte)"
    else:
        pad_oft = None
        origem_pad = ("nao informada e nao estimada -- OPP_diast indisponivel "
                      "(use estimar_PAD_oftalmica=True para a convencao do Composer)")

    base["PAD_oftalmica_mmHg"] = pad_oft
    base["PAD_oftalmica_origem"] = origem_pad
    if pad_oft is None:
        base["OPP_diast"] = None
        base["OPP_diast_min_mmHg"] = None
    else:
        opp_diast = opp_diastolica(IOP_mmHg, pad_oft)
        base["OPP_diast"] = opp_diast
        base["OPP_diast_min_mmHg"] = float(opp_diast.min())

    return base


def sensibilidade_fator_braquial(t_min: np.ndarray, IOP_mmHg: np.ndarray,
                                  proto: Protocol,
                                  OPP_crit_mmHg: float = 50.0,
                                  fatores=(0.5, 0.6, 2.0 / 3.0, 0.7, 0.8)) -> dict:
    """
    Varre o fator braquial->oftalmica (convencao 2/3, faixa de
    sensibilidade 0.5-0.8 exigida pelo plano de tese, WP4.1) e retorna I
    e MOPP_min para cada valor. Nunca reporte um unico fator como se
    fosse medido.
    """
    out = {}
    for f in fatores:
        m = perfusion_metrics(t_min, IOP_mmHg, proto, OPP_crit_mmHg=OPP_crit_mmHg,
                               mopp_factor=f)
        out[f] = {"I_mmHg_min": m["I_mmHg_min"], "MOPP_min_mmHg": m["MOPP_min_mmHg"]}
    return out


if __name__ == "__main__":
    from goldmann_iop_solver import ThinShellPV, simulate

    proto = Protocol()
    pv = ThinShellPV(R_m=0.012, t_m=0.6e-3, E_Pa=3e6, P0_mmHg=proto.P0_mmHg)
    t, V, P = simulate(proto, pv)

    print("=== Paciente de referencia (phi_vasc=1.0) ===")
    r1 = cadeia_completa(t, P, proto, OPP_crit_ref_mmHg=50.0, phi_vasc=1.0,
                          PAD_oftalmica_mmHg=proto.DBP_mmHg)
    print(f"  I (OPP_crit=50, phi=1.0) = {r1['I_mmHg_min']:.2f} mmHg.min")
    print(f"  MOPP minima              = {r1['MOPP_min_mmHg']:.1f} mmHg")
    print(f"  OPP_diast minima         = {r1['OPP_diast_min_mmHg']:.1f} mmHg")

    print("\n=== Paciente com reserva vascular reduzida (phi_vasc=1.4) ===")
    r2 = cadeia_completa(t, P, proto, OPP_crit_ref_mmHg=50.0, phi_vasc=1.4,
                          PAD_oftalmica_mmHg=proto.DBP_mmHg)
    print(f"  OPP_crit efetivo         = {r2['OPP_crit_efetivo_mmHg']:.1f} mmHg")
    print(f"  I (OPP_crit efetivo)     = {r2['I_mmHg_min']:.2f} mmHg.min")

    print("\n=== Sensibilidade ao fator braquial->oftalmica ===")
    sens = sensibilidade_fator_braquial(t, P, proto, OPP_crit_mmHg=50.0)
    for f, vals in sens.items():
        print(f"  fator={f:.3f}  I={vals['I_mmHg_min']:.2f} mmHg.min  MOPP_min={vals['MOPP_min_mmHg']:.1f}")
