#!/usr/bin/env python3
"""gen_fsi_transiente_csf_waveform.py

Gera a tabela OpenFOAM de pressao cinematica p/rho [m^2/s^2] vs tempo [s]
para os casos FSI transientes do nervo optico:

  * fsi-transiente-2 : baseline 1g, PIC = 10 mmHg (1333 Pa)
  * fsi-transiente-3 : SANS / microgravidade, PIC = 28.5 mmHg (3800 Pa)

Modelo de PIC fisiologica
-------------------------
A pressao do LCR no espaco subaracnoideo NAO e' uma constante: e' uma onda
estocastica com componentes deterministicos. Nas escalas de relevancia para
o ONSAS, a literatura (Wagshul et al., 2011, Fluids Barriers CNS; Marmarou
et al., 1978, J Neurosurg; Avezaat & van Eijndhoven, 1986, Acta Neurochir)
identifica DUAS escalas dominantes:

  - pulsacao CARDIACA   : f_HR = 80 bpm  -> T_HR = 0.75 s   amplitude ~1.25 mmHg
  - pulsacao RESPIRATORIA : f_RR = 14 rpm  -> T_RR = 4.286 s amplitude ~3.75 mmHg

A onda total e' a superposicao das duas senoides em torno da PIC media:

    PIC(t) = PIC_mean + A_resp*sin(2*pi*f_RR*t) + A_card*sin(2*pi*f_HR*t)

Em SANS, a hipertensao intracraniana cronica + cephalad fluid shift +
perda de complacencia craniospinal levam a' DISTORCAO das ondas (maior
forca propulsora) -> escalonamos as amplitudes em fsi-transiente-3.

Rampa de inicializacao
----------------------
Hann window TOTAL nos primeiros T_RAMP = 0.20 s (zero -> PIC_mean + osc).
A media tambem rampa para evitar overshoot do solido em t=dt. Os primeiros
~T_RAMP da simulacao DEVEM ser descartados das metricas.

Saida
-----
  cases/<case>/fluid/constant/inlet_pressure.dat

Formato OpenFOAM Function1 'tableFile':
    (
      (t1  p_kin1)
      (t2  p_kin2)
      ...
    )

E referenciada por fluid/0/p como uniformFixedValue + tableFile.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

# ---------------------------------------------------------------------------
# Constantes fisicas e do dominio
# ---------------------------------------------------------------------------
RHO_CSF = 1000.0                   # kg/m^3 (LCR water-like)
MMHG_TO_PA = 133.322387415

# Frequencias fisiologicas
F_HR_BPM = 80.0                    # cardiaca
F_RR_RPM = 14.0                    # respiratoria
T_HR = 60.0 / F_HR_BPM             # 0.75 s
T_RR = 60.0 / F_RR_RPM             # 4.286 s

# Resolucao temporal da TABELA (suficientemente densa para o tableFile
# interpolar linearmente sem perder a senoide cardiaca):
#   T_HR = 0.75 s; queremos >=20 amostras/ciclo cardiaco -> dt_table <= 37.5 ms
DT_TABLE = 0.005                   # 5 ms (150 amostras/ciclo cardiaco)

# Rampa Hann inicial (descartar metricas em t < T_RAMP)
T_RAMP = 0.20

# ---------------------------------------------------------------------------
# Modos: presets por caso
# ---------------------------------------------------------------------------
PRESETS = {
    "fsi-transiente-2": {
        "PIC_mean_mmHg":   10.0,
        "A_resp_mmHg":     3.75,    # respiratoria, baseline 1g
        "A_card_mmHg":     1.25,    # cardiaca, baseline 1g
        "rho":             RHO_CSF,
        "label":           "1g normotenso (PAM=10 mmHg)",
    },
    "fsi-transiente-3": {
        "PIC_mean_mmHg":   28.5,
        # SANS: distorcao das ondas. PIC elevada implica perda de
        # complacencia craniospinal (a curva PV fica mais ingreme),
        # entao a mesma alteracao volumetrica gera oscilacao de
        # pressao maior. Refs: Lawley et al. 2017; Marmarou 1978.
        "A_resp_mmHg":     5.50,    # ~1.47x baseline
        "A_card_mmHg":     2.50,    # ~2.00x baseline (notch sistolico mais visivel)
        "rho":             RHO_CSF,
        "label":           "SANS / microgravidade (PAM=28.5 mmHg, ondas distorcidas)",
    },
}


def csf_waveform_pa(t: float, pic_mean_pa: float,
                    a_resp_pa: float, a_card_pa: float) -> float:
    """Onda PIC (Pa) = PIC_mean + A_resp*sin(2pi f_RR t) + A_card*sin(2pi f_HR t).

    Convencao: pico respiratorio coincide com t=0.25*T_RR; cardiaco com
    t=0.25*T_HR. A pressao em t=0 = PIC_mean (sem rampa).
    """
    omega_resp = 2.0 * math.pi / T_RR
    omega_card = 2.0 * math.pi / T_HR
    return (pic_mean_pa
            + a_resp_pa * math.sin(omega_resp * t)
            + a_card_pa * math.sin(omega_card * t))


def hann_ramp(t: float, t_ramp: float) -> float:
    """Hann window 0 -> 1 em t in [0, t_ramp]."""
    if t <= 0.0:
        return 0.0
    if t >= t_ramp:
        return 1.0
    return 0.5 * (1.0 - math.cos(math.pi * t / t_ramp))


def write_table(path: Path, header_lines: list[str],
                rows: list[tuple[float, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for line in header_lines:
            f.write(f"// {line}\n")
        f.write("(\n")
        for t, p_kin in rows:
            f.write(f"    ({t:.6f}  {p_kin:.6f})\n")
        f.write(")\n")


def diagnostic_metrics(rows_pa: list[tuple[float, float]],
                       window: tuple[float, float]) -> dict:
    """Estatisticas em uma janela [t0, t1]."""
    t0, t1 = window
    sub = [(t, p) for (t, p) in rows_pa if t0 <= t <= t1]
    if not sub:
        return {}
    pmin = min(p for (_, p) in sub)
    pmax = max(p for (_, p) in sub)
    s = 0.0
    for k in range(1, len(sub)):
        s += 0.5 * (sub[k][1] + sub[k-1][1]) * (sub[k][0] - sub[k-1][0])
    pam = s / (sub[-1][0] - sub[0][0])
    return {
        "P_min_Pa":   pmin,
        "P_max_Pa":   pmax,
        "PAM_Pa":     pam,
        "P_min_mmHg": pmin / MMHG_TO_PA,
        "P_max_mmHg": pmax / MMHG_TO_PA,
        "PAM_mmHg":   pam / MMHG_TO_PA,
        "PP_mmHg":    (pmax - pmin) / MMHG_TO_PA,
    }


def gen_for_case(case: str, end_time: float, repo_root: Path) -> None:
    if case not in PRESETS:
        raise ValueError(f"caso desconhecido: {case}. opcoes: {list(PRESETS)}")
    preset = PRESETS[case]
    pic_mean_pa = preset["PIC_mean_mmHg"] * MMHG_TO_PA
    a_resp_pa   = preset["A_resp_mmHg"]   * MMHG_TO_PA
    a_card_pa   = preset["A_card_mmHg"]   * MMHG_TO_PA
    rho         = preset["rho"]

    # Amostragem (inclui t=0 e t=end_time). Pad de 0.5s alem do endTime
    # para outOfBounds clamp nao precisar extrapolar.
    t_max = end_time + 0.5
    n = int(math.ceil(t_max / DT_TABLE)) + 1
    rows_pa: list[tuple[float, float]] = []
    rows_kin: list[tuple[float, float]] = []
    for i in range(n):
        t = i * DT_TABLE
        p_raw = csf_waveform_pa(t, pic_mean_pa, a_resp_pa, a_card_pa)
        w = hann_ramp(t, T_RAMP)
        # Rampa total: comeca em 0 e cresce ate p_raw (a media tambem rampa).
        # Em t=0 a pressao e' 0 (consistente com internalField=0 em fluid/0/p).
        p_pa = w * p_raw
        rows_pa.append((t, p_pa))
        rows_kin.append((t, p_pa / rho))

    target = repo_root / "cases" / case / "fluid" / "constant" / "inlet_pressure.dat"
    header = [
        f"Tabela de pressao cinematica p/rho [m^2/s^2] vs tempo [s].",
        f"Caso: {case}  ({preset['label']})",
        f"Gerado por brunaStuff/gen_fsi_transiente_csf_waveform.py",
        f"",
        f"PIC_mean = {preset['PIC_mean_mmHg']:.3f} mmHg ({pic_mean_pa:.2f} Pa)",
        f"A_resp   = {preset['A_resp_mmHg']:.3f} mmHg ({a_resp_pa:.2f} Pa)  "
        f"f_RR = {F_RR_RPM:.1f} rpm  T_RR = {T_RR:.3f} s",
        f"A_card   = {preset['A_card_mmHg']:.3f} mmHg ({a_card_pa:.2f} Pa)  "
        f"f_HR = {F_HR_BPM:.1f} bpm  T_HR = {T_HR:.3f} s",
        f"rho      = {rho:.1f} kg/m^3   dt_table = {DT_TABLE*1e3:.1f} ms",
        f"endTime  = {end_time:.3f} s   (tabela com pad ate {t_max:.3f} s)",
        f"Hann ramp TOTAL em t < {T_RAMP*1e3:.0f} ms (descartar metricas neste intervalo)",
    ]
    write_table(target, header, rows_kin)
    print(f"OK  -> {target.relative_to(repo_root)}")

    # Diagnostico em uma janela pos-rampa cobrindo 1 ciclo respiratorio
    t0 = max(T_RAMP, 0.5)
    t1 = min(t0 + T_RR, end_time)
    diag = diagnostic_metrics(rows_pa, (t0, t1))
    print(f"      janela diag [{t0:.3f}, {t1:.3f}] s (>=1 ciclo resp):")
    if diag:
        print(f"        PIC mean (PAM)  = {diag['PAM_mmHg']:6.3f} mmHg "
              f"({diag['PAM_Pa']:7.2f} Pa)")
        print(f"        PIC min         = {diag['P_min_mmHg']:6.3f} mmHg "
              f"({diag['P_min_Pa']:7.2f} Pa)")
        print(f"        PIC max         = {diag['P_max_mmHg']:6.3f} mmHg "
              f"({diag['P_max_Pa']:7.2f} Pa)")
        print(f"        PIC range (PP)  = {diag['PP_mmHg']:6.3f} mmHg")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--case", choices=list(PRESETS) + ["all"], default="all",
        help="qual caso gerar (default: all = ambos os transientes)")
    parser.add_argument(
        "--endTime", type=float, default=5.0,
        help="endTime da simulacao em segundos (default: 5.0 = ~1 ciclo resp)")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    targets = list(PRESETS) if args.case == "all" else [args.case]
    print("=== gen_fsi_transiente_csf_waveform ===")
    print(f"  endTime = {args.endTime:.3f} s   dt_table = {DT_TABLE*1e3:.1f} ms")
    print(f"  T_RR = {T_RR:.3f} s   T_HR = {T_HR:.3f} s")
    print(f"  T_RAMP = {T_RAMP*1e3:.0f} ms (Hann window)\n")
    for case in targets:
        print(f"--- {case} ---")
        gen_for_case(case, args.endTime, repo_root)
        print()


if __name__ == "__main__":
    main()
