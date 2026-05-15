#!/usr/bin/env python3
"""
gen_lumen_pressure_table.py — gera a tabela de pressão pulsátil para o
                               patch lumen do artoph-mestrado.

Perfil de velocidade (dado experimental):
  v(t') = (v_sist - v_diast) × sin(π t'/T_sist) + v_diast   para t' ≤ T_sist
  v(t') = v_diast                                             para t' > T_sist

  v_sist  = 16.88 cm/s  (pico sistólico)
  v_diast =  6.32 cm/s  (velocidade diastólica)
  T_sist  = 0.218 s     (duração da sístole)
  T_ciclo = 0.50  s     (período cardíaco, HR ≈ 120 bpm — como no gráfico)

Mapeamento velocidade → pressão (proporcional):
  P(t') = (P_sist - P_diast) × norm(t') + P_diast
  onde norm(t') = (v(t') - v_diast) / (v_sist - v_diast)

  P_sist  = 16000 Pa ≈ 120 mmHg
  P_diast = 10700 Pa ≈  80 mmHg

Saída: constant/lumen_pressure.dat (formato tableFile do OpenFOAM)
"""

import math
import os

# ── Parâmetros ────────────────────────────────────────────────────────────────
T_sist  = 0.218   # s — duração da sístole
T_ciclo = 0.500   # s — período cardíaco
P_diast = 10700.0 # Pa — 80 mmHg
P_amp   = 5300.0  # Pa — (P_sist - P_diast) = 16000 - 10700

dt      = 0.01    # s — passo da tabela
t_end   = 1.0     # s — fim da simulação

def P_at(t_local):
    """Pressão em função do tempo local dentro do ciclo (0 ≤ t_local < T_ciclo)."""
    if t_local <= T_sist:
        return P_amp * math.sin(math.pi * t_local / T_sist) + P_diast
    else:
        return P_diast

# ── Geração da tabela ─────────────────────────────────────────────────────────
entries = []
t = 0.0
while t <= t_end + 1e-9:
    t_local = t % T_ciclo          # tempo dentro do ciclo atual
    P = P_at(t_local)
    entries.append((round(t, 4), round(P, 1)))
    t = round(t + dt, 4)

# ── Escrita do arquivo ────────────────────────────────────────────────────────
out_path = os.path.join(
    os.path.dirname(__file__),
    "../cases/artoph-mestrado/solid/constant/lumen_pressure.dat"
)
out_path = os.path.normpath(out_path)

header = """\
// artoph-mestrado — tabela de pressão pulsátil no lúmen
// Gerado por brunaStuff/gen_lumen_pressure_table.py
//
// Formato: ( tempo[s]   pressao[Pa] )
// Dois ciclos cardíacos completos (HR ≈ 120 bpm, T_ciclo = 0.5 s)
//   P_sist  = 16000 Pa ≈ 120 mmHg   (t = 0.11 s e t = 0.61 s)
//   P_diast = 10700 Pa ≈  80 mmHg   (diastólica baseline)
//   T_sist  = 0.218 s  (duração da sístole — perfil senoidal)
//
// Referência do perfil de velocidade:
//   v(t') = (16.88 - 6.32)×sin(π t'/0.218) + 6.32 cm/s  para t'≤0.218 s
(
"""
footer = ");\n"

with open(out_path, "w") as f:
    f.write(header)
    for t_val, P_val in entries:
        f.write(f"  ( {t_val:<7.3f}   {P_val:.1f} )\n")
    f.write(footer)

print(f"Tabela escrita em: {out_path}")
print(f"Entradas: {len(entries)} pontos, t = 0 a {entries[-1][0]} s")
print(f"P_max = {max(P for _, P in entries):.1f} Pa  (em t ≈ 0.11 s e t ≈ 0.61 s)")
print(f"P_min = {min(P for _, P in entries):.1f} Pa  (diastólica)")
