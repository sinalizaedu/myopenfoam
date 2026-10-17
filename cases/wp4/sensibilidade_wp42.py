#!/usr/bin/env python3
"""Sensibilidade univariada da dose isquêmica (WP4.2).

Protocolo numérico = ``run_wp41.protocolo_referencia()`` (refluxo instantâneo WP0, sem paracentese).
"""
from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

import numpy as np

WP4 = Path(__file__).resolve().parent
WP0 = WP4.parent / "wp0"
for p in (str(WP4), str(WP0)):
    if p not in sys.path:
        sys.path.insert(0, p)

from dose_isquemica import dose_isquemica  # noqa: E402
from goldmann_iop_solver import FriedenwaldPV, simulate  # noqa: E402
from opp_perfusion import mopp  # noqa: E402
from run_wp41 import ConstantKPV, protocolo_referencia  # noqa: E402

P0 = 16.9
T_END = 40.0


def run_case(proto, pv, pas, pad, opp_crit: float) -> dict:
    t, _v, iop = simulate(proto, pv)
    mopp_t = np.asarray(mopp(iop, pas, pad), float)
    mopp_basal = float(mopp_t[0])
    i_tot = dose_isquemica(t, mopp_t, opp_crit)
    i_basal = max(0.0, opp_crit - mopp_basal) * T_END
    i_evt = i_tot - i_basal
    return {
        "iop_peak": float(iop.max()),
        "mopp_min": float(mopp_t.min()),
        "mopp_basal": mopp_basal,
        "I_total": i_tot,
        "I_evento": i_evt,
    }


def main() -> int:
    opp40 = 40.0
    opp35 = 35.0
    rows = []

    # BP
    for pas, pad, label in ((110, 70, "110/70"), (120, 80, "120/80"), (140, 90, "140/90")):
        proto = dataclasses.replace(protocolo_referencia(), SBP_mmHg=float(pas), DBP_mmHg=float(pad))
        pv = FriedenwaldPV(Kf_per_uL=0.00581, P0_mmHg=P0)
        r = run_case(proto, pv, pas, pad, opp40)
        rows.append(("PA " + label, opp40, r["I_total"], r["I_evento"]))

    # K_f band (WP0 sensitivity text)
    proto = protocolo_referencia()
    for kf, label in ((0.00352, "Kf baixo (P0=22)"), (0.00581, "Kf ref"), (0.00745, "Kf alto (P0=14)")):
        pv = FriedenwaldPV(Kf_per_uL=kf, P0_mmHg=P0)
        r = run_case(proto, pv, 120, 80, opp40)
        r35 = run_case(proto, pv, 120, 80, opp35)
        rows.append((label, opp40, r["I_total"], r["I_evento"]))
        rows.append((label + " @35", opp35, r35["I_total"], r35["I_evento"]))

    # P(V) forms — peaks at 50 uL for reference
    proto = protocolo_referencia()
    forms = [
        ("Friedenwald ref", FriedenwaldPV(0.00581, P0)),
        ("Linear K=0,325 secante", ConstantKPV(0.325)),
        ("Linear K=0,298 WP1.2", ConstantKPV(0.298)),
        ("Linear K=0,393 Pallikaris*", ConstantKPV(0.393)),
        ("Linear K=0,635 Silver*", ConstantKPV(0.635)),
    ]
    for name, pv in forms:
        p50 = pv.P(50.0)
        r40 = run_case(proto, pv, 120, 80, opp40)
        r35 = run_case(proto, pv, 120, 80, opp35)
        print(f"{name:28s}  P@50={p50:5.1f}  I@40={r40['I_total']:6.1f} (evt {r40['I_evento']:5.1f})  I@35={r35['I_total']:5.1f}")

    print("\n=== PA (Friedenwald, OPP_crit=40) ===")
    for label, oc, it, ie in rows[:3]:
        print(f"  {label:20s}  I_total={it:7.1f}  I_evento={ie:7.1f}")

    print("\n=== K_f (120/80) ===")
    for label, oc, it, ie in rows[3:]:
        print(f"  {label:22s}  crit={oc:.0f}  I_total={it:7.1f}  I_evento={ie:7.1f}")

    # Papazoglou scaling: if 31.15 is ~2 min not peak, scale delta
    ratio = 16.0 / 12.4  # WP0 recalibrated peak delta / 2 min delta
    iop_2min = 13.98 + 17.2
    iop_peak_est = 13.98 + 17.2 * ratio
    print(f"\nPapazoglou: IOP@~2min={iop_2min:.2f}  ratio peak/2min={ratio:.3f}  IOP_pico_est={iop_peak_est:.1f}")
    for pas, pad in ((110, 70), (120, 80), (140, 90)):
        m = 2 / 3 * (pad + (pas - pad) / 3) - iop_peak_est
        print(f"  PA {pas}/{pad}  MOPP_min_est~{m:.1f}  OPP_crit max~{m:.1f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
