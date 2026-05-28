#!/usr/bin/env python3
"""gen_teste_2d_fsi_omvs_pressure.py

Gera a onda de pressao arterial sistemica para o caso cases/teste-2d-fsi-oa-on
usando a reconstrucao trigonometrica em 6 partes do OMVS (Ocular
Mathematical Virtual Simulator, Sala 2019 / Guidoboni et al.), parametrizada
por:

    SP = 120 mmHg  (pressao sistolica)
    DP =  80 mmHg  (pressao diastolica)
    HR =  69 bpm   (frequencia cardiaca, T = 60/HR = 0.8696 s)

Identico ao gen_ao_mestrado_omvs_pressure.py (mesma fisiologia), mas escreve
em cases/teste-2d-fsi-oa-on/fluid/constant/{inlet,outlet}_pressure.dat.

Saidas (pressao cinematica p/rho, [m^2/s^2]):
    cases/teste-2d-fsi-oa-on/fluid/constant/inlet_pressure.dat
    cases/teste-2d-fsi-oa-on/fluid/constant/outlet_pressure.dat
"""
from __future__ import annotations

import math
from pathlib import Path

# Detecta automaticamente o local: copia em cases/<x>/scripts/ ou brunaStuff/.
SCRIPT_DIR = Path(__file__).resolve().parent
if SCRIPT_DIR.name == "scripts":
    CASE = SCRIPT_DIR.parent
else:
    REPO = SCRIPT_DIR.parent
    CASE = REPO / "cases" / "teste-2d-fsi-oa-on"

OUT_DIR = CASE / "fluid" / "constant"

# Parametros fisiologicos (OMVS, Sala 2019)
SP_MMHG = 120.0
DP_MMHG = 80.0
HR_BPM = 69.0

MMHG_TO_PA = 133.322387415
SP_PA = SP_MMHG * MMHG_TO_PA
DP_PA = DP_MMHG * MMHG_TO_PA
PP_PA = SP_PA - DP_PA

T_CYCLE = 60.0 / HR_BPM
RHO = 1050.0

N_CYCLES = 3
N_PER_CYCLE = 200
DT_TABLE = T_CYCLE / N_PER_CYCLE

DELTA_P_DRIVE_PA = 10.0
T_RAMP = 0.10
T_OUTLET_SHIFT = 0.005  # outlet defasado em 5ms

# Marcos da onda (fracoes de T e fracoes de PP acima de DP) — OMVS 6 pieces
MARKERS = [
    (0.00, 0.00),
    (0.10, 0.40),
    (0.18, 1.00),
    (0.30, 0.55),
    (0.40, 0.65),
    (0.55, 0.40),
    (1.00, 0.00),
]


def pressure_pa(tau: float) -> float:
    """Pressao P em Pa para tau in [0,1] (fracao do ciclo)."""
    tau = tau % 1.0
    for i in range(len(MARKERS) - 1):
        t0, f0 = MARKERS[i]
        t1, f1 = MARKERS[i + 1]
        if t0 <= tau < t1:
            theta = math.pi * (tau - t0) / (t1 - t0)
            P0 = DP_PA + f0 * PP_PA
            P1 = DP_PA + f1 * PP_PA
            return (P0 + P1) / 2.0 - (P1 - P0) / 2.0 * math.cos(theta)
    return DP_PA


def hann_ramp(t: float) -> float:
    """Fator multiplicativo Hann [0,1] em t in [0, T_RAMP]."""
    if t <= 0.0:
        return 0.0
    if t >= T_RAMP:
        return 1.0
    return 0.5 * (1.0 - math.cos(math.pi * t / T_RAMP))


def write_table(path: Path, offset_pa: float, time_shift: float) -> None:
    """Escreve tabela OpenFOAM Function1 (time, value)."""
    n_total = N_CYCLES * N_PER_CYCLE + 1
    with path.open("w") as fh:
        fh.write("// Gerado por brunaStuff/gen_teste_2d_fsi_omvs_pressure.py\n")
        fh.write(f"// SP={SP_MMHG} DP={DP_MMHG} mmHg, HR={HR_BPM} bpm, T={T_CYCLE:.4f}s\n")
        fh.write(f"// rho={RHO} kg/m^3, offset={offset_pa:.1f} Pa, shift={time_shift*1000:.1f} ms\n")
        fh.write(f"// Coluna 1: t [s];  Coluna 2: p/rho [m^2/s^2]\n")
        fh.write("(\n")
        for i in range(n_total):
            t = i * DT_TABLE
            tau = (t - time_shift) / T_CYCLE
            P_raw = pressure_pa(tau)
            P = (P_raw + offset_pa) * hann_ramp(t)
            kin = P / RHO
            fh.write(f"    ({t:.6f}  {kin:.6f})\n")
        fh.write(")\n")
    print(f"Escrito: {path}  ({n_total} amostras)")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # inlet: pressao OMVS sem offset
    write_table(OUT_DIR / "inlet_pressure.dat", offset_pa=0.0, time_shift=0.0)
    # outlet: -DELTA_P_DRIVE para conduzir fluxo, atrasado 5ms vs inlet
    write_table(
        OUT_DIR / "outlet_pressure.dat",
        offset_pa=-DELTA_P_DRIVE_PA,
        time_shift=T_OUTLET_SHIFT,
    )
    print(f"\nOndas: 80-120 mmHg, HR=69 bpm, 3 ciclos ({N_CYCLES*T_CYCLE:.3f}s)")
    print(f"Rampa Hann TOTAL nos primeiros {T_RAMP*1000:.0f} ms")
    print(f"Outlet defasado {T_OUTLET_SHIFT*1000:.0f}ms vs inlet -> Δp pulsatil ~30 Pa")


if __name__ == "__main__":
    main()
