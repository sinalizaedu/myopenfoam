#!/usr/bin/env python3
"""
Gera as tabelas de pressão pulsátil para o caso artoph-fsi-curva-mestrado.

Produz:
  cases/artoph-fsi-curva-mestrado/fluid/constant/inlet_pressure.dat
  cases/artoph-fsi-curva-mestrado/fluid/constant/outlet_pressure.dat

Cada arquivo é uma tabela OpenFOAM (time  value) com pressão CINEMÁTICA
(p/ρ, [m²/s²]) — pimpleFoam é incompressível e trabalha sempre com p/ρ.

Forma de onda fisiológica para artéria sistêmica de pequeno calibre (AO):
  - Frequência cardíaca padrão: 75 bpm  → período T = 0,8 s
  - Pico sistólico: ~16 kPa (~120 mmHg) em t ≈ 0,15 s
  - Dicrotic notch: ~12,5 kPa em t ≈ 0,33 s
  - Vale diastólico: ~10,7 kPa (~80 mmHg) em t ≈ 0,55 s
  - PAM (∫p dt / T) ≈ 13,3 kPa (~100 mmHg)

O escoamento é induzido por um pequeno gradiente de pressão entre inlet e
outlet (Δp_mean ≈ 500 Pa, ~3,8 mmHg), compatível com a faixa fisiológica
de queda pressórica em um segmento de ~30 mm da AO. A onda em si é
idêntica nas duas extremidades; apenas a média é deslocada.

Acoplamento: one-way (Force fluido→sólido via preCICE). A malha fluida é
estática (staticFvMesh) — a deformação da parede NÃO realimenta o fluido.
"""
from __future__ import annotations

import math
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "cases" / "artoph-fsi-curva-mestrado" / "fluid" / "constant"

RHO = 1050.0
T_CYCLE = 0.8
N_CYCLES = 2
N_PER_CYCLE = 200
DT = T_CYCLE / N_PER_CYCLE

P_MEAN_PA = 13_300.0
P_SYS_PA = 16_000.0
P_DIA_PA = 10_700.0
# Δp_drive = 10 Pa (~0.075 mmHg): hidrodinamicamente despreziv\u00e9l perto da
# faixa puls\u00e1til (5300 Pa), mas necess\u00e1rio para evitar SINGULARIDADE no
# sistema linear de press\u00e3o (sem gradiente, qualquer p constante \u00e9 solu\u00e7\u00e3o).
# Para hemodinâmica realista (futuro): subir para 200-500 Pa e reduzir Δt < 5e-5.
DELTA_P_DRIVE_PA = 10.0

# Rampa suave de inicializacao para evitar water-hammer / choque hidrostatico
# na partida. Durante t in [0, T_RAMP), as oscilacoes da onda sao atenuadas
# multiplicativamente por um cosseno levantado (Hann window) que cresce de 0 a 1,
# preservando a PAM. Isso simula uma "rampa fisiologica" sem quebrar a media.
T_RAMP = 0.10


def waveform_pa(t: float) -> float:
    """Pressão sistêmica arterial fisiológica (Pa).

    Aproximação Fourier-truncada calibrada para reproduzir pico sistólico,
    vale diastólico, dicrotic notch e PAM ~ 13,3 kPa em T = 0,8 s.
    """
    phi = 2.0 * math.pi * (t % T_CYCLE) / T_CYCLE
    a1, p1 = 1.20, 0.62
    a2, p2 = 0.45, 1.10
    a3, p3 = 0.18, 1.85
    a4, p4 = 0.08, 2.40
    osc = (
        a1 * math.sin(phi - p1)
        + a2 * math.sin(2 * phi - p2)
        + a3 * math.sin(3 * phi - p3)
        + a4 * math.sin(4 * phi - p4)
    )
    p_raw = P_MEAN_PA + (P_SYS_PA - P_DIA_PA) * 0.5 * osc / 1.30
    return p_raw


def calibrate_offsets() -> tuple[float, float]:
    """Garante PAM = 13 300 Pa e range [10 700, 16 000] Pa."""
    ts = [i * DT for i in range(N_PER_CYCLE)]
    raw = [waveform_pa(t) for t in ts]
    mean = sum(raw) / len(raw)
    pmin = min(raw)
    pmax = max(raw)
    span_raw = pmax - pmin
    span_target = P_SYS_PA - P_DIA_PA
    scale = span_target / span_raw
    shift = P_MEAN_PA - mean * scale
    return scale, shift


def write_table(path: Path, time_press_pa: list[tuple[float, float]]) -> None:
    """Escreve no formato OpenFOAM Function1 'table' (time value)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write("// Tabela de pressao cinematica p/rho [m^2/s^2] vs tempo [s].\n")
        f.write(f"// Gerada por brunaStuff/gen_artoph_pressure_waveform.py\n")
        f.write(f"// rho = {RHO:g} kg/m^3, T = {T_CYCLE:g} s, N_ciclos = {N_CYCLES}\n")
        f.write("(\n")
        for t, p_pa in time_press_pa:
            p_kin = p_pa / RHO
            f.write(f"    ({t:.6f}  {p_kin:.6f})\n")
        f.write(")\n")


def main() -> None:
    scale, shift = calibrate_offsets()

    inlet_rows: list[tuple[float, float]] = []
    outlet_rows: list[tuple[float, float]] = []

    n_total = N_CYCLES * N_PER_CYCLE + 1
    for i in range(n_total):
        t = i * DT
        p_base_unr = waveform_pa(t) * scale + shift
        # Suaviza a oscilacao em torno da PAM durante a rampa inicial
        if t < T_RAMP:
            w = 0.5 * (1.0 - math.cos(math.pi * t / T_RAMP))  # Hann ramp 0 -> 1
        else:
            w = 1.0
        p_base = P_MEAN_PA + w * (p_base_unr - P_MEAN_PA)
        # Driver gradiente tambem com rampa (evita acelerar fluido bruscamente)
        drive = w * DELTA_P_DRIVE_PA
        inlet_rows.append((t, p_base + 0.5 * drive))
        outlet_rows.append((t, p_base - 0.5 * drive))

    write_table(OUT_DIR / "inlet_pressure.dat", inlet_rows)
    write_table(OUT_DIR / "outlet_pressure.dat", outlet_rows)

    diag_pa = [r[1] - 0.5 * DELTA_P_DRIVE_PA for r in inlet_rows[:N_PER_CYCLE]]
    mean_pa = sum(diag_pa) / len(diag_pa)
    pmin_pa = min(diag_pa)
    pmax_pa = max(diag_pa)
    print(f"OK - tabelas escritas em {OUT_DIR}")
    print(f"  ciclos: {N_CYCLES}, T = {T_CYCLE} s, pontos/ciclo = {N_PER_CYCLE}")
    print(f"  range total (s): [0, {(n_total - 1) * DT:.3f}]")
    print(f"  base (Pa)    PAM = {mean_pa:.1f}, min = {pmin_pa:.1f}, max = {pmax_pa:.1f}")
    print(f"  drive Δp     = {DELTA_P_DRIVE_PA:.1f} Pa entre inlet e outlet")
    print(f"  p_kin range  inlet:  [{(pmin_pa + 0.5*DELTA_P_DRIVE_PA)/RHO:.4f}, "
          f"{(pmax_pa + 0.5*DELTA_P_DRIVE_PA)/RHO:.4f}] m²/s²")
    print(f"  p_kin range  outlet: [{(pmin_pa - 0.5*DELTA_P_DRIVE_PA)/RHO:.4f}, "
          f"{(pmax_pa - 0.5*DELTA_P_DRIVE_PA)/RHO:.4f}] m²/s²")


if __name__ == "__main__":
    main()
