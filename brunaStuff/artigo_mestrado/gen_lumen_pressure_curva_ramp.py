"""Generate a *ramped* expanding lumen pressure table for artoph-curva-mestrado.

Diagnostic step: a divergent solver run with the full -10700 Pa load suggests
either a material/BC pathology or numerical fragility. To isolate this we
ramp the pressure linearly from 0 to -P_diast over the first half of the
simulation (0 to 0.5 s), then apply the second cardiac cycle's pulsatile
profile normally between 0.5 and 1.0 s.

If the solver converges with the ramped load, the issue was the abrupt step
load at t=0 (which the segregated solver can't handle in one shot). If it
still diverges, the issue is the material/BC setup.
"""
import math
from pathlib import Path

T_sist = 0.218
T_cycle = 0.500
P_diast = 10700.0
P_amp = 5300.0
dt = 0.01
t_end = 1.0

def P_pulse(t_local: float) -> float:
    if t_local <= T_sist:
        return P_amp * math.sin(math.pi * t_local / T_sist) + P_diast
    return P_diast

out = Path(__file__).resolve().parents[1] / (
    "cases/artoph-curva-mestrado/solid/constant/lumen_pressure.dat"
)
out.parent.mkdir(parents=True, exist_ok=True)

entries = []
t = 0.0
while t <= t_end + 1e-9:
    if t < 0.5:
        # Linear ramp from 0 to -P_diast over first cycle
        P = -P_diast * (t / 0.5)
    else:
        # Pulsatile waveform applied during second cycle, negative sign
        t_local = (t - 0.5) % T_cycle
        P = -P_pulse(t_local)
    entries.append((round(t, 4), round(P, 1)))
    t = round(t + dt, 4)

header = """\
// artoph-curva-mestrado — tabela de pressao com rampa
// Gerado por brunaStuff/gen_lumen_pressure_curva_ramp.py
//
// t  in [0, 0.5] s:  rampa linear de 0 a -10700 Pa  (sem pulsacao)
// t  in [0.5, 1.0] s: pulsacao cardiaca normal (-10700 a -16000 Pa)
//
// Versao com rampa para diagnostico de convergencia: evita step load
// brusco no t=0 que pode causar divergencia no segregated solver.
(
"""
footer = ");\n"

with out.open("w") as f:
    f.write(header)
    for t_val, P_val in entries:
        f.write(f"  ( {t_val:<7.3f}   {P_val:.1f} )\n")
    f.write(footer)

print(f"[write] {out}")
print(f"        ramp 0 -> -{P_diast} Pa over t in [0, 0.5]")
print(f"        pulsatile cycle in t in [0.5, 1.0]")
