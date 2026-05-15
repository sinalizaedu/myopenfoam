"""Generate the *expanding* lumen pressure table for artoph-curva-mestrado.

In the curved case the artery is modelled as a *filled* solid (no hollow
wall), so the patch `lumen` is the lateral OUTER surface of the artery
tube. To simulate the pulsatile blood pressure acting from the *inside* of
the artery wall (which expands the artery outward), we apply a negative
`pressure` in solidTraction: in solids4Foam the BC computes traction as
sigma·n = -p·n + tau, so a negative p flips the sign and gives traction
pointing along the outward normal -- i.e. expansion.

This script writes the negated version of the pulsatile waveform that
gen_lumen_pressure_table.py produces for the straight case.
"""
import math
from pathlib import Path

T_sist = 0.218
T_cycle = 0.500
P_diast = 10700.0
P_amp = 5300.0
dt = 0.01
t_end = 1.0

def P_at(t_local: float) -> float:
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
    t_local = t % T_cycle
    # Negative sign: in the filled-solid case, negative pressure ≡ outward
    # traction ≡ expansion (see header comment above).
    P = -P_at(t_local)
    entries.append((round(t, 4), round(P, 1)))
    t = round(t + dt, 4)

header = """\
// artoph-curva-mestrado — tabela de pressao pulsatil (artéria como sólido cheio)
// Gerado por brunaStuff/gen_lumen_pressure_curva.py
//
// IMPORTANTE: valores negativos.
//   No modelo de art\u00e9ria solida cheia (sem casca), o patch `lumen` \u00e9 a
//   superficie LATERAL EXTERNA do tubo. Para simular press\u00e3o sangu\u00ednea
//   *interna* (que empurra a parede para fora), aplicamos `solidTraction`
//   com `pressure` NEGATIVO: sigma\u00b7n = -p\u00b7n, ou seja, com p<0 a tra\u00e7\u00e3o
//   aponta na dire\u00e7\u00e3o da normal externa = expans\u00e3o.
//
// Magnitude segue o ciclo card\u00edaco padr\u00e3o (igual ao caso reto):
//   |P_sist|  = 16000 Pa \u2248 120 mmHg
//   |P_diast| = 10700 Pa \u2248  80 mmHg
//   T_sist  = 0.218 s, T_ciclo = 0.5 s  (HR \u2248 120 bpm)
(
"""
footer = ");\n"

with out.open("w") as f:
    f.write(header)
    for t_val, P_val in entries:
        f.write(f"  ( {t_val:<7.3f}   {P_val:.1f} )\n")
    f.write(footer)

print(f"[write] {out}")
print(f"        {len(entries)} entries, t in [0, {entries[-1][0]}] s")
print(f"        P_min = {min(p for _, p in entries):.1f} Pa")
print(f"        P_max = {max(p for _, p in entries):.1f} Pa")
