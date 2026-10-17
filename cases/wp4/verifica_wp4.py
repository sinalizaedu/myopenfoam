#!/usr/bin/env python3
"""Verificação independente dos números do WP4.1 e WP4.2 com o solver 0D do WP0.

Parâmetros da Tabela de escoamento humana, Q_prod=2.415 uL/min
(equilíbrio em $P_0=16{,}9$ mmHg), protocolo WP4 ($50$ µL em $6$ s, refluxo instantâneo WP0,
sem paracentese, $40$ min). Tempos abaixo de limiar usam a mesma regra do
``run_wp41.py`` (interpolação nos cruzamentos).

Uso (repo):
  cases/wp0/.venv/bin/python cases/wp4/verifica_wp4.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

WP4 = Path(__file__).resolve().parent
WP0 = WP4.parent / "wp0"
for p in (str(WP4), str(WP0)):
    if p not in sys.path:
        sys.path.insert(0, p)

from goldmann_iop_solver import FriedenwaldPV, _reflux_mode  # noqa: E402
from dose_isquemica import delta_V_bolus_fechada, dose_isquemica, validacao_fechada_H6  # noqa: E402
from h6_teorico import dose_fechada_H6  # noqa: E402
from opp_perfusion import map_mmhg, mopp  # noqa: E402
from run_wp41 import ConstantKPV, protocolo_referencia, tempo_abaixo_interpolado  # noqa: E402

PAM = map_mmhg(120.0, 80.0)
P0 = 16.9
MOPP_BASAL = 2 / 3 * PAM - P0


def _print_proto() -> None:
    proto = protocolo_referencia()
    print("=== Protocolo WP4.1 (run_wp41.protocolo_referencia) ===")
    print(f"  Q_prod={proto.Q_prod_uL_min} uL/min  C_out={proto.C_out_uL_min_mmHg}")
    print(f"  Pev={proto.Pev_mmHg} mmHg  f_uv={proto.frac_uveoscleral}  P0={proto.P0_mmHg}")
    print(f"  reflux_mode={proto.reflux_mode!r}  effective={_reflux_mode(proto)!r}")
    print(f"  t_inj_dur={proto.t_inj_dur_min} min  t_end={proto.t_end_min} min")
    print(f"  MOPP_basal={MOPP_BASAL:.2f} mmHg\n")


def main() -> int:
    _print_proto()
    proto = protocolo_referencia()
    formas = {
        "linear K=0,325": ConstantKPV(0.325),
        "Friedenwald Kf=0,00581": FriedenwaldPV(Kf_per_uL=0.00581, P0_mmHg=P0),
    }
    from goldmann_iop_solver import simulate

    res = {}
    for nome, pv in formas.items():
        t, _v, iop = simulate(proto, pv)
        mopp_t = np.asarray(mopp(iop, 120.0, 80.0, fator_braquial_oftalmica=2 / 3), float)
        res[nome] = (t, mopp_t)
        print(nome)
        print(f"   pico IOP        {iop.max():.2f} mmHg")
        print(f"   MOPP minima     {mopp_t.min():.2f} mmHg")
        for th in (30, 40, 50):
            print(f"   tempo MOPP<{th}   {tempo_abaixo_interpolado(t, mopp_t, th):.2f} min")

    t_f, m_f = res["Friedenwald Kf=0,00581"]
    print("\nDose numerica, Friedenwald (mmHg·min)")
    for c in (25, 30, 31, 35, 40, 45, 50):
        print(f"   OPP_crit {c:2d}   {dose_isquemica(t_f, m_f, c):7.2f}")

    t_l, m_l = res["linear K=0,325"]
    v = validacao_fechada_H6(proto, ConstantKPV(0.325), OPP_crit_ref_mmHg=40.0)
    print(
        f"\nLinear K=0,325, OPP_crit=40: numerica {v['I_numerico_mmHg_min']:.1f}  "
        f"fechada H6 {v['I_fechado_mmHg_min']:.1f}  "
        f"(erro rel {v['erro_relativo'] * 100:.1f}%)"
    )
    d_pth = MOPP_BASAL - 40.0
    dV_net = delta_V_bolus_fechada(proto)
    tau = 1.0 / (0.28 * 0.325)
    t_fech_40 = tau * np.log(0.325 * dV_net / d_pth) if 0.325 * dV_net > d_pth else 0.0
    print(
        f"   H6 bolus: tempo abaixo 40 mmHg (nao = Goldmann ODE) = {t_fech_40:.2f} min  "
        f"| simulado T<40 = {tempo_abaixo_interpolado(t_l, m_l, 40):.2f} min"
    )
    print(
        "Forma fechada dPth=15:",
        [
            round(dose_fechada_H6(k, dV_net, 0.28, 15), 2)
            for k in (0.30, 0.31, 0.325, 0.40, 0.60, 1.00)
        ],
    )
    print(
        "Dose acumulada com recuperacao:",
        [round(20 * (1 + (n - 1) * 2 ** (-d / 4)), 1) for n, d in ((24, 4), (10, 10), (8, 12), (6, 16))],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
