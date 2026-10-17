#!/usr/bin/env python3
"""WP4.1 — MOPP(t) e tempos abaixo de limiares de perfusão (pipeline oficial).

Consome IOP(t) do WP0 (goldmann_iop_solver) com duas curvas P(V):
  - WP0: rigidez constante K = 0,325 mmHg/µL
  - WP1.2: Friedenwald recalibrado Kf = 0,00581 µL⁻¹

Protocolo: 50 µL, refluxo instantâneo WP0, sem paracentese; PAS/PAD = 120/80 mmHg; P₀ = 16,9 mmHg.
Sensibilidade: f_bo ∈ [0,50, 0,80].

Saída: cases/wp4/output_wp41/
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

WP4 = Path(__file__).resolve().parent
WP0 = WP4.parent / "wp0"
for p in (str(WP4), str(WP0)):
    if p not in sys.path:
        sys.path.insert(0, p)

from goldmann_iop_solver import (  # noqa: E402
    FriedenwaldPV,
    Protocol,
    Q_PROD_HUMAN_TABELA_UL_MIN,
    protocol_humano_relatorio,
    simulate,
)
from opp_perfusion import map_mmhg, mopp  # noqa: E402

OUT = WP4 / "output_wp41"

# --- metodologia (texto WP4.1) ---
P0_MMHG = 16.9
K_LINEAR_MMHG_PER_UL = 0.325
KF_FRIEDENWALD = 0.00581
PAS_MMHG = 120.0
PAD_MMHG = 80.0
F_BO_REF = 2.0 / 3.0
F_BO_SWEEP = np.linspace(0.50, 0.80, 7)
LIMIARES_MOPP_MMHG = (30.0, 40.0, 50.0)


@dataclass
class ConstantKPV:
    """P(V) linear com K fixo (WP0 rigidez constante)."""

    K_mmHg_per_uL: float
    P0_mmHg: float = P0_MMHG
    V0_uL: float = 0.0

    def P(self, V_uL: float) -> float:
        return self.P0_mmHg + self.K_mmHg_per_uL * (V_uL - self.V0_uL)

    def dPdV(self, V_uL: float) -> float:
        return self.K_mmHg_per_uL

    def V_of_P(self, P_mmHg: float) -> float:
        return self.V0_uL + (P_mmHg - self.P0_mmHg) / self.K_mmHg_per_uL


def tempo_abaixo_interpolado(t_min: np.ndarray, y: np.ndarray, limiar: float) -> float:
    """Minutos com y(t) < limiar; cruzamentos por interpolação linear."""
    t = np.asarray(t_min, dtype=float)
    v = np.asarray(y, dtype=float)
    if t.shape != v.shape or t.size < 2:
        return 0.0
    total = 0.0
    for i in range(len(t) - 1):
        t0, t1 = t[i], t[i + 1]
        y0, y1 = v[i] - limiar, v[i + 1] - limiar
        dt = t1 - t0
        if dt <= 0:
            continue
        if y0 < 0 and y1 < 0:
            total += dt
        elif y0 >= 0 and y1 >= 0:
            continue
        elif y0 >= 0 > y1:
            frac = y0 / (y0 - y1)
            total += frac * dt
        else:
            frac = (-y0) / (y1 - y0)
            total += (1.0 - frac) * dt
    return float(total)


def protocolo_referencia() -> Protocol:
    """WP4: mesmo protocolo humano do WP0 (refluxo instantâneo, IVI sem paracentese)."""
    return protocol_humano_relatorio(
        par_enabled=False,
        t_end_min=40.0,
        SBP_mmHg=PAS_MMHG,
        DBP_mmHg=PAD_MMHG,
    )


def analisar_cenario(nome: str, pv) -> dict:
    proto = protocolo_referencia()
    t, V, iop = simulate(proto, pv)
    map_v = float(map_mmhg(PAS_MMHG, PAD_MMHG))
    mopp_ref = np.asarray(mopp(iop, PAS_MMHG, PAD_MMHG, fator_braquial_oftalmica=F_BO_REF), float)

    tempos_ref = {
        f"T_abaixo_{int(th)}_min": tempo_abaixo_interpolado(t, mopp_ref, th)
        for th in LIMIARES_MOPP_MMHG
    }

    sens_f_bo = {}
    for f in F_BO_SWEEP:
        mopp_t = np.asarray(mopp(iop, PAS_MMHG, PAD_MMHG, fator_braquial_oftalmica=float(f)), float)
        sens_f_bo[f"{float(f):.4f}"] = {
            "MOPP_basal_mmHg": float(f * map_v - P0_MMHG),
            "MOPP_min_mmHg": float(mopp_t.min()),
            **{
                f"T_abaixo_{int(th)}_min": tempo_abaixo_interpolado(t, mopp_t, th)
                for th in LIMIARES_MOPP_MMHG
            },
        }

    return {
        "cenario": nome,
        "protocolo": {
            "V_inj_uL": proto.V_inj_uL,
            "P0_mmHg": proto.P0_mmHg,
            "PAS_mmHg": PAS_MMHG,
            "PAD_mmHg": PAD_MMHG,
            "MAP_mmHg": map_v,
            "refluxo": proto.reflux_mode,
            "reflux_dV_uL": proto.reflux_instant_dV_uL,
            "paracentese": proto.par_enabled,
        },
        "pv": {
            "tipo": type(pv).__name__,
            "K_mmHg_per_uL": getattr(pv, "K_mmHg_per_uL", None),
            "Kf_per_uL": getattr(pv, "Kf", None),
        },
        "referencia_f_bo": F_BO_REF,
        "MOPP_basal_mmHg": float(F_BO_REF * map_v - P0_MMHG),
        "sensibilidade_dMOPP_df_bo_mmHg": map_v,
        "IOP_pico_mmHg": float(iop.max()),
        "t_pico_min": float(t[np.argmax(iop)]),
        "MOPP_min_mmHg": float(mopp_ref.min()),
        **tempos_ref,
        "sensibilidade_f_bo": sens_f_bo,
        "serie": {
            "t_min": t.tolist(),
            "iop_mmHg": iop.tolist(),
            "mopp_mmHg": mopp_ref.tolist(),
        },
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    resultados = [
        analisar_cenario("WP0_K_constante", ConstantKPV(K_LINEAR_MMHG_PER_UL)),
        analisar_cenario(
            "WP1.2_Friedenwald_recalibrado",
            FriedenwaldPV(Kf_per_uL=KF_FRIEDENWALD, P0_mmHg=P0_MMHG),
        ),
    ]
    out_path = OUT / "wp41_resultados.json"
    out_path.write_text(json.dumps(resultados, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    map_v = float(map_mmhg(PAS_MMHG, PAD_MMHG))
    print("WP4.1 — cadeia IOP → MOPP (oficial, cases/wp4)")
    print(f"  MAP = {map_v:.3f} mmHg  (∂MOPP/∂f_bo = MAP)")
    print(f"  MOPP basal (f_bo=2/3) = {F_BO_REF * map_v - P0_MMHG:.2f} mmHg\n")
    for r in resultados:
        print(f"--- {r['cenario']} ---")
        print(f"  IOP pico     : {r['IOP_pico_mmHg']:.1f} mmHg @ t={r['t_pico_min']:.3f} min")
        print(f"  MOPP mínima  : {r['MOPP_min_mmHg']:.1f} mmHg")
        for th in LIMIARES_MOPP_MMHG:
            key = f"T_abaixo_{int(th)}_min"
            print(f"  {key} (f=2/3): {r[key]:.3f} min")
        print("  Sensibilidade f_bo (MOPP_min, min abaixo de 40 mmHg):")
        for f, vals in r["sensibilidade_f_bo"].items():
            print(
                f"    f={f}  MOPP_min={vals['MOPP_min_mmHg']:5.1f}  "
                f"T<40={vals['T_abaixo_40_min']:.3f} min"
            )
        print()
    print(f"JSON completo: {out_path}")


if __name__ == "__main__":
    main()
