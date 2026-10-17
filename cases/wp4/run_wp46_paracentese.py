#!/usr/bin/env python3
"""WP4.6 — MOPP e dose isquêmica com paracentese (três estratégias do WP0).

Mesmas métricas do WP4.1/4.2 (Friedenwald recalibrada, PAS/PAD 120/80, f_bo=2/3),
via ``simulate_wp0_timeline`` (par por volume, refluxo instantâneo), alinhado a
``wp0_report.run_par_scenario``.

Cenários:
  - sem_par: IVI padrão WP4.1
  - profilatica: par t=-30 s, janela começa t=-30 s
  - reativa: par t=+30 s
  - tardia: par t=+2 min

Saída: cases/wp4/output_wp46/wp46_paracentese.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

WP4 = Path(__file__).resolve().parent
WP0 = WP4.parent / "wp0"
for p in (str(WP4), str(WP0)):
    if p not in sys.path:
        sys.path.insert(0, p)

from dose_isquemica import dose_isquemica  # noqa: E402
from goldmann_iop_solver import (  # noqa: E402
    FriedenwaldPV,
    Wp0Timeline,
    needle_hydraulic_resistance,
    protocol_humano_relatorio,
    simulate_wp0_timeline,
)
from opp_perfusion import map_mmhg, mopp  # noqa: E402
from run_wp41 import (  # noqa: E402
    F_BO_REF,
    KF_FRIEDENWALD,
    LIMIARES_MOPP_MMHG,
    PAD_MMHG,
    PAS_MMHG,
    P0_MMHG,
    tempo_abaixo_interpolado,
)

OUT = WP4 / "output_wp46"
T_END = 40.0
PAR_VOL = 50.0
REFLUX_DV = 1.19
R_PAR = needle_hydraulic_resistance(0.0795, 13.0, 0.75)
OPP_CRIT_ROWS = (25, 30, 31, 35, 40, 45)

CENARIOS = (
    ("sem_par", None, 0.0, "Sem paracentese (referência WP4.1)"),
    ("profilatica", -0.5, -0.5, "Profilática ($t=-30$ s)"),
    ("reativa", 0.5, 0.0, "Reativa ($t=+30$ s)"),
    ("tardia", 2.0, 0.0, "Tardia ($t=+2$ min)"),
)


def protocolo_wp0_humano():
    return protocol_humano_relatorio(
        SBP_mmHg=PAS_MMHG,
        DBP_mmHg=PAD_MMHG,
        R_par_Pa_s_per_m3=R_PAR,
        par_volume_uL=PAR_VOL,
        reflux_instant_dV_uL=REFLUX_DV,
    )


def simular_par(nome: str, par_start_min: float | None, t_begin: float):
    proto = protocolo_wp0_humano()
    pv = FriedenwaldPV(Kf_per_uL=KF_FRIEDENWALD, P0_mmHg=P0_MMHG)
    tl = Wp0Timeline(
        t_begin_min=t_begin,
        t_end_min=T_END,
        par_start_min=par_start_min,
        par_volume_uL=PAR_VOL,
        instant_reflux_uL=REFLUX_DV,
    )
    t, _v, iop, meta = simulate_wp0_timeline(proto, pv, tl, r_par=R_PAR)
    mopp_t = np.asarray(
        mopp(iop, PAS_MMHG, PAD_MMHG, fator_braquial_oftalmica=F_BO_REF), float
    )
    map_v = float(map_mmhg(PAS_MMHG, PAD_MMHG))
    mopp_basal_ref = float(F_BO_REF * map_v - P0_MMHG)
    dose = {}
    for oc in OPP_CRIT_ROWS:
        i_tot = dose_isquemica(t, mopp_t, float(oc))
        i_basal = max(0.0, float(oc) - mopp_basal_ref) * T_END
        dose[f"I_evt_OPP_{int(oc)}"] = float(i_tot - i_basal)
    tempos = {
        f"T_abaixo_{int(th)}_min": tempo_abaixo_interpolado(t, mopp_t, th)
        for th in LIMIARES_MOPP_MMHG
    }
    return {
        "id": nome,
        "par_start_min": par_start_min,
        "t_begin_min": t_begin,
        "par_duration_s": (
            None if par_start_min is None else float(meta.get("par_duration_min", float("nan")) * 60.0)
        ),
        "IOP_pico_mmHg": float(iop.max()),
        "t_pico_min": float(t[np.argmax(iop)]),
        "MOPP_basal_mmHg": mopp_basal_ref,
        "MOPP_min_mmHg": float(mopp_t.min()),
        **tempos,
        **dose,
        "meta": {k: (float(v) if isinstance(v, (int, float, np.floating)) else v) for k, v in meta.items()},
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [simular_par(n, ps, tb) for n, ps, tb, _ in CENARIOS]
    out_path = OUT / "wp46_paracentese.json"
    out_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("WP4.6 — paracentese × MOPP × dose (Friedenwald, 120/80)\n")
    for r in rows:
        print(f"--- {r['id']} ---")
        print(f"  IOP pico {r['IOP_pico_mmHg']:.2f} mmHg  MOPP min {r['MOPP_min_mmHg']:.2f}")
        print(f"  T<30 {r['T_abaixo_30_min']:.3f} min  T<40 {r['T_abaixo_40_min']:.3f} min")
        print(f"  I_evt@40 {r['I_evt_OPP_40']:.2f} mmHg·min  @35 {r['I_evt_OPP_35']:.2f}")
    print(f"\nJSON: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
