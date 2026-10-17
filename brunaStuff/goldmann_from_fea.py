#!/usr/bin/env python3
"""Goldmann ODE on an FEA P(V) curve. Rabbit Lamminsalo physiology.

    dV/dt = Q_prod + Q_ivi(t) - C_out (P(V) - P_ev) - Q_uv

P0 = 15 mmHg. Units inside: µL, mmHg, seconds.
Spline covers [V(15), V(15)+50 µL]; bounds_error=False, fill_value=extrapolate.
Uses scipy cubic + solve_ivp when available; otherwise linear interp + RK4.

    python3 brunaStuff/goldmann_from_fea.py \\
        --csv cases/fea-simplf/results/inflation.csv \\
        --out cases/fea-simplf/results/goldmann.csv
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

try:
    from scipy.interpolate import interp1d
    from scipy.integrate import solve_ivp

    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

P0 = 15.0          # mmHg
PEV = 10.0         # mmHg
Q_PROD_UL_MIN = 3.0
FRAC_TM = 0.80
Q_UV_UL_MIN = (1.0 - FRAC_TM) * Q_PROD_UL_MIN          # 0.6
Q_TM0 = FRAC_TM * Q_PROD_UL_MIN                         # 2.4
C_OUT = Q_TM0 / (P0 - PEV)                              # 0.48 µL/min/mmHg
Q_IVI_UL = 50.0
T_IVI = 6.0            # s
T_END = 40.0 * 60.0    # 40 min in seconds


def load_living_branch(csv_path: Path):
    rows = list(csv.DictReader(csv_path.open()))
    living = [r for r in rows if float(r["p_mmhg"]) >= P0 - 0.2]
    if len(living) < 2:
        living = rows
    V = np.array([float(r["v_full_uL"]) for r in living], dtype=np.float64)
    P = np.array([float(r["p_mmhg"]) for r in living], dtype=np.float64)
    order = np.argsort(V)
    V, P = V[order], P[order]
    # drop duplicate V
    _, uniq = np.unique(V, return_index=True)
    return V[uniq], P[uniq]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--json-in", type=Path, default=None)
    args = ap.parse_args()

    V, P = load_living_branch(args.csv)
    V15 = float(V[0])
    # prefer JSON v_at_15 if present
    js = None
    jpath = args.json_in or args.csv.with_suffix(".json")
    if jpath.exists():
        js = json.loads(jpath.read_text())
        if js.get("v_at_15_uL"):
            V15 = float(js["v_at_15_uL"])

    if HAS_SCIPY:
        kind = "cubic" if len(V) >= 4 else "linear"
        p_spline = interp1d(V, P, kind=kind, bounds_error=False, fill_value="extrapolate")

        def p_of_v(vol: float) -> float:
            return float(p_spline(vol))
    else:

        def p_of_v(vol: float) -> float:
            return float(
                np.interp(
                    vol,
                    V,
                    P,
                    left=P[0],
                    right=P[-1]
                    + (P[-1] - P[-2]) / (V[-1] - V[-2] + 1e-15) * (vol - V[-1]),
                )
            )

    q_prod = Q_PROD_UL_MIN / 60.0          # µL/s
    q_uv = Q_UV_UL_MIN / 60.0
    c = C_OUT / 60.0                       # µL/s/mmHg
    q_ivi_rate = Q_IVI_UL / T_IVI

    def rhs(t, vol):
        p = p_of_v(float(np.asarray(vol).reshape(-1)[0]))
        qivi = q_ivi_rate if t < T_IVI else 0.0
        return q_prod + qivi - c * (p - PEV) - q_uv

    if HAS_SCIPY:
        sol = solve_ivp(
            lambda tt, yy: [rhs(tt, yy[0])],
            (0.0, T_END),
            [V15],
            dense_output=True,
            rtol=1e-6,
            atol=1e-8,
            max_step=1.0,
        )
        t_ivi = np.arange(0.0, T_IVI + 1e-12, 0.05)
        t_rest = np.arange(float(int(np.ceil(T_IVI))), T_END + 1e-12, 1.0)
        t = np.unique(np.concatenate([t_ivi, t_rest, [T_END]]))
        vol = sol.sol(t)[0]
    else:
        ts = [0.0]
        vs = [V15]
        t = 0.0
        vol = V15
        while t < T_END - 1e-12:
            dt = 0.05 if t < T_IVI else 1.0
            if t + dt > T_END:
                dt = T_END - t
            k1 = rhs(t, vol)
            k2 = rhs(t + 0.5 * dt, vol + 0.5 * dt * k1)
            k3 = rhs(t + 0.5 * dt, vol + 0.5 * dt * k2)
            k4 = rhs(t + dt, vol + dt * k3)
            vol = vol + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
            t = t + dt
            ts.append(t)
            vs.append(vol)
        t = np.asarray(ts)
        vol = np.asarray(vs)
    p = np.array([p_of_v(v) for v in vol])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["t_s", "t_min", "V_uL", "P_mmHg"])
        for ti, vi, pi in zip(t, vol, p):
            w.writerow([f"{ti:.6e}", f"{ti / 60.0:.6e}", f"{vi:.6e}", f"{pi:.6e}"])

    p_peak = float(np.max(p))
    t_peak = float(t[int(np.argmax(p))])
    # time to P0+1 mmHg after the peak
    after = np.where((t > t_peak) & (p <= P0 + 1.0))[0]
    t_back = float(t[after[0]]) if len(after) else None
    p_inf = float(p[-1])

    tau_s = None
    # linearised tau from FEA K = dP/dV at 15 mmHg
    if len(V) >= 2:
        dpdv = (P[1] - P[0]) / (V[1] - V[0] + 1e-15)   # mmHg / µL
        if dpdv > 0:
            tau_s = 1.0 / ((C_OUT / 60.0) * dpdv)

    summary = {
        "C_out_uL_per_min_per_mmHg": C_OUT,
        "Q_prod_uL_per_min": Q_PROD_UL_MIN,
        "Q_uv_uL_per_min": Q_UV_UL_MIN,
        "P0_mmHg": P0,
        "Pev_mmHg": PEV,
        "P_peak_mmHg": p_peak,
        "t_peak_s": t_peak,
        "dIOP_peak_mmHg": p_peak - P0,
        "t_back_to_16mmHg_min": (None if t_back is None else t_back / 60.0),
        "P_inf_mmHg": p_inf,
        "tau_lin_min": (None if tau_s is None else tau_s / 60.0),
        "csv": str(args.out),
    }
    args.out.with_suffix(".json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    if abs(p_inf - P0) > 0.5:
        print(f"WARNING: P(inf)={p_inf:.2f} mmHg, expected {P0}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
