#!/usr/bin/env python3
"""gen_ao_mestrado_omvs_pressure.py

Gera a onda de pressao arterial sistemica para o caso cases/ao-mestrado
usando a reconstrucao trigonometrica em 6 partes do OMVS (Ocular
Mathematical Virtual Simulator, Sala 2019 / Guidoboni et al.), parametrizada
por:

    SP = 120 mmHg  (pressao sistolica)
    DP =  80 mmHg  (pressao diastolica)
    HR =  69 bpm   (frequencia cardiaca, T = 60/HR = 0.8696 s)

A onda e definida em 6 sub-intervalos do ciclo cardiaco T, com transicoes
suaves (meia-onda cosseno) entre marcos fisiologicos:

    tau (frac de T) | nome do marco              | P (frac do pulse pressure)
    ---------------+----------------------------+---------------------------
    tau0 = 0.00    | inicio do ciclo (diastole) | P = DP
    tau1 = 0.10    | inicio do upstroke         | P = DP + 0.40*PP
    tau2 = 0.18    | pico sistolico             | P = SP
    tau3 = 0.30    | fim do downstroke (incisura)| P = DP + 0.55*PP
    tau4 = 0.40    | topo do entalhe dicrotico  | P = DP + 0.65*PP
    tau5 = 0.55    | meio da diastole           | P = DP + 0.40*PP
    tau6 = 1.00    | fim do ciclo               | P = DP

onde PP = SP - DP = 40 mmHg. Cada sub-intervalo i->i+1 usa:

    P(tau) = (Pi + Pi+1)/2 - (Pi+1 - Pi)/2 * cos(pi * (tau-taui) / (taui+1-taui))

garantindo C0 e tangente horizontal nos marcos (suave e fisiologico).

Saidas:
    cases/ao-mestrado/fluid/constant/inlet_pressure.dat
    cases/ao-mestrado/fluid/constant/outlet_pressure.dat

Cada arquivo e tabela OpenFOAM Function1 (time value) com pressao
CINEMATICA (p/rho, [m^2/s^2]). pimpleFoam e incompressivel e usa p/rho.

Acoplamento: one-way (pressao no fluido -> tensao na parede via preCICE).
"""
from __future__ import annotations

import math
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "cases" / "ao-mestrado" / "fluid" / "constant"

# Parametros fisiologicos (OMVS, Sala 2019)
SP_MMHG = 120.0
DP_MMHG = 80.0
HR_BPM = 69.0

MMHG_TO_PA = 133.322387415  # 1 mmHg = 133.322 Pa
SP_PA = SP_MMHG * MMHG_TO_PA  # 15998.7 Pa
DP_PA = DP_MMHG * MMHG_TO_PA  # 10665.8 Pa
PP_PA = SP_PA - DP_PA         # 5332.9 Pa

T_CYCLE = 60.0 / HR_BPM       # 0.8696 s
RHO = 1050.0                  # densidade do sangue (kg/m^3)

# Numero de ciclos a gerar e resolucao temporal.
# endTime do controlDict = 0.8 s, T = 0.870 s -> 1 ciclo nao chega ao fim.
# Geramos 3 ciclos com folga (cobre ate 2.6 s) para qualquer extensao futura.
N_CYCLES = 3
N_PER_CYCLE = 200
DT_TABLE = T_CYCLE / N_PER_CYCLE  # ~4.35 ms entre amostras

# Driver de gradiente entre inlet e outlet (necessario para evitar
# singularidade no sistema de pressao incompressivel; nao afeta a
# pulsacao). Pequeno em relacao ao pulse pressure.
DELTA_P_DRIVE_PA = 10.0

# Rampa Hann TOTAL (zero -> PAM): a pressao comeca em zero e cresce ate o
# valor fisiologico em T_RAMP segundos. Rampa total (nao "AC-only") evita
# o overshoot inicial do solido que recebia PAM=12 m²/s² instantaneamente
# em t=1ms na versao anterior. O primeiro ciclo nao deve ser usado
# para extrair metricas (apenas para estabilizacao do sistema).
T_RAMP = 0.10
RAMP_MODE = "total"  # "total" (0 -> PAM) ou "ac_only" (oscila em torno de PAM)

# Shift temporal do outlet (atraso de propagacao da onda):
# o pulso fisiologico leva tempo finito para percorrer a arteria. Sem
# shift, inlet e outlet pulsam em fase e o gradiente longitudinal
# dinamico = 0 (apenas o offset DELTA_P_DRIVE de 10 Pa, insuficiente
# para gerar fluxo fisiologico). Com shift de ~5 ms criamos um Δp
# pulsatil de ate ~PP*shift/T ≈ 30 Pa de pico que conduz a fluxo.
T_OUTLET_SHIFT = 0.005  # 5 ms de atraso na onda do outlet

# Marcos da onda (fracoes de T e fracoes de PP acima de DP) — OMVS 6 pieces
MARKERS = [
    (0.00, 0.00),   # tau0: inicio diastole
    (0.10, 0.40),   # tau1: inicio upstroke (pre-systole)
    (0.18, 1.00),   # tau2: pico sistolico (P = SP)
    (0.30, 0.55),   # tau3: incisura (final do downstroke)
    (0.40, 0.65),   # tau4: topo do entalhe dicrotico
    (0.55, 0.40),   # tau5: meio da diastole
    (1.00, 0.00),   # tau6: fim do ciclo (volta a DP)
]


def omvs_waveform_pa(t: float) -> float:
    """Onda OMVS-6 em Pa, periodica com periodo T_CYCLE."""
    tau = (t % T_CYCLE) / T_CYCLE  # tau em [0, 1)
    for i in range(len(MARKERS) - 1):
        tau_i, frac_i = MARKERS[i]
        tau_j, frac_j = MARKERS[i + 1]
        if tau_i <= tau <= tau_j:
            # cosseno meia-onda de (tau_i, P_i) ate (tau_j, P_j)
            P_i = DP_PA + frac_i * PP_PA
            P_j = DP_PA + frac_j * PP_PA
            phase = math.pi * (tau - tau_i) / (tau_j - tau_i)
            return 0.5 * (P_i + P_j) - 0.5 * (P_j - P_i) * math.cos(phase)
    return DP_PA  # fallback


def diagnostic_metrics(samples: list[tuple[float, float]]) -> dict:
    """Calcula PAM, P_min, P_max ao longo de UM ciclo a partir das amostras."""
    cycle = [(t, p) for (t, p) in samples if t <= T_CYCLE + 1e-9]
    if not cycle:
        return {}
    pmin = min(p for (_, p) in cycle)
    pmax = max(p for (_, p) in cycle)
    # Trapezoidal integration -> PAM
    s = 0.0
    for k in range(1, len(cycle)):
        s += 0.5 * (cycle[k][1] + cycle[k - 1][1]) * (cycle[k][0] - cycle[k - 1][0])
    pam = s / (cycle[-1][0] - cycle[0][0])
    return {
        "P_min_Pa": pmin,
        "P_max_Pa": pmax,
        "P_min_mmHg": pmin / MMHG_TO_PA,
        "P_max_mmHg": pmax / MMHG_TO_PA,
        "PAM_Pa": pam,
        "PAM_mmHg": pam / MMHG_TO_PA,
        "PP_mmHg": (pmax - pmin) / MMHG_TO_PA,
    }


def write_table(path: Path, time_press_pa: list[tuple[float, float]],
                drive_offset_pa: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    side = "inlet" if drive_offset_pa > 0 else "outlet"
    with path.open("w", encoding="utf-8") as f:
        f.write(f"// Tabela de pressao cinematica p/rho [m^2/s^2] vs tempo [s].\n")
        f.write(f"// Onda arterial OMVS 6-piece (Sala 2019 / Guidoboni et al.)\n")
        f.write(f"// SP = {SP_MMHG} mmHg, DP = {DP_MMHG} mmHg, HR = {HR_BPM} bpm\n")
        f.write(f"// T = {T_CYCLE:.4f} s, rho = {RHO} kg/m^3\n")
        f.write(f"// {side}: drive_offset = {drive_offset_pa:+.1f} Pa\n")
        f.write(f"// Gerada por brunaStuff/gen_ao_mestrado_omvs_pressure.py\n")
        f.write("(\n")
        for t, p_pa in time_press_pa:
            p_kin = p_pa / RHO
            f.write(f"    ({t:.6f}  {p_kin:.6f})\n")
        f.write(")\n")


def main() -> None:
    # Gera amostras para N_CYCLES com rampa Hann no primeiro T_RAMP
    n_total = N_CYCLES * N_PER_CYCLE + 1
    inlet_rows: list[tuple[float, float]] = []
    outlet_rows: list[tuple[float, float]] = []
    pure_rows: list[tuple[float, float]] = []  # sem rampa nem drive (para diagnostico)

    for i in range(n_total):
        t = i * DT_TABLE
        p_raw = omvs_waveform_pa(t)
        pure_rows.append((t, p_raw))

        if t < T_RAMP:
            w = 0.5 * (1.0 - math.cos(math.pi * t / T_RAMP))
        else:
            w = 1.0
        # Rampa preserva PAM: oscilacao em torno da media do raw
        # Como p_raw varia em torno de PAM(raw), a rampa atenua a OSCILACAO
        # mas nao a media. Calculamos PAM de 1 ciclo para usar como pivot:
        pass

    # 2) calcula PAM da onda raw (primeiro ciclo) para usar como pivot da rampa
    diag = diagnostic_metrics(pure_rows[: N_PER_CYCLE + 1])
    P_pivot = diag["PAM_Pa"]

    for (t, p_raw_inlet) in pure_rows:
        # outlet le a onda OMVS com atraso T_OUTLET_SHIFT (propagacao da onda
        # arterial pela arteria oftalmica de ~40mm).
        p_raw_outlet = omvs_waveform_pa(t - T_OUTLET_SHIFT) if t >= T_OUTLET_SHIFT else DP_PA

        if t < T_RAMP:
            w = 0.5 * (1.0 - math.cos(math.pi * t / T_RAMP))
        else:
            w = 1.0

        if RAMP_MODE == "total":
            # Rampa total: 0 -> p_raw (a media tambem rampa)
            p_in = w * p_raw_inlet
            p_out = w * p_raw_outlet
        else:  # ac_only
            p_in = P_pivot + w * (p_raw_inlet - P_pivot)
            p_out = P_pivot + w * (p_raw_outlet - P_pivot)

        drive = w * DELTA_P_DRIVE_PA
        inlet_rows.append((t, p_in + 0.5 * drive))
        outlet_rows.append((t, p_out - 0.5 * drive))

    write_table(OUT_DIR / "inlet_pressure.dat", inlet_rows, +0.5 * DELTA_P_DRIVE_PA)
    write_table(OUT_DIR / "outlet_pressure.dat", outlet_rows, -0.5 * DELTA_P_DRIVE_PA)

    # Diagnostico final (usa amostras pos-rampa para garantir SP/DP corretos)
    diag_post_ramp = diagnostic_metrics(
        [r for r in inlet_rows if T_RAMP <= r[0] <= T_RAMP + T_CYCLE]
    )
    print(f"=== gen_ao_mestrado_omvs_pressure ===")
    print(f"  HR = {HR_BPM} bpm  ->  T = {T_CYCLE:.4f} s")
    print(f"  SP = {SP_MMHG} mmHg ({SP_PA:.1f} Pa)")
    print(f"  DP = {DP_MMHG} mmHg ({DP_PA:.1f} Pa)")
    print(f"  PP = {SP_MMHG - DP_MMHG} mmHg ({PP_PA:.1f} Pa)")
    print(f"  N_CYCLES = {N_CYCLES}, N/cycle = {N_PER_CYCLE}, "
          f"DT_table = {DT_TABLE*1e3:.2f} ms")
    print(f"  total time range: [0, {(n_total-1)*DT_TABLE:.4f}] s")
    print(f"  drive Δp inlet-outlet (offset DC) = {DELTA_P_DRIVE_PA:.1f} Pa")
    print(f"  outlet phase shift = {T_OUTLET_SHIFT*1e3:.1f} ms (atraso onda)")
    print(f"  Hann ramp em t<{T_RAMP*1e3:.0f} ms ({RAMP_MODE} mode)")
    print(f"\n  -- ciclo raw (sem rampa, sem drive) --")
    print(f"     PAM = {diag['PAM_mmHg']:.2f} mmHg ({diag['PAM_Pa']:.1f} Pa)")
    print(f"     P_min = {diag['P_min_mmHg']:.2f} mmHg, "
          f"P_max = {diag['P_max_mmHg']:.2f} mmHg")
    print(f"     PP = {diag['PP_mmHg']:.2f} mmHg")
    print(f"\n  -- inlet apos rampa (1 ciclo completo) --")
    if diag_post_ramp:
        print(f"     PAM = {diag_post_ramp['PAM_mmHg']:.2f} mmHg")
        print(f"     P_min = {diag_post_ramp['P_min_mmHg']:.2f} mmHg, "
              f"P_max = {diag_post_ramp['P_max_mmHg']:.2f} mmHg")
        print(f"     PP = {diag_post_ramp['PP_mmHg']:.2f} mmHg")
    print(f"\n  arquivos escritos em {OUT_DIR}")


if __name__ == "__main__":
    main()
