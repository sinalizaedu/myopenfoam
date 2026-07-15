#!/usr/bin/env python3
"""
gen_contact_pressure_table.py - gera a tabela de pressao pulsatil para o
                                 patch contact_artoph do on-mestrado.

Origem fisica:
  A pressao de contato entre a arteria oftalmica dilatada e a bainha do
  nervo optico (ONS) deriva da pressao luminal arterial via:

      p_contact(t) = (p_contact_micro / P_lumen_micro) * P_lumen(t)
                   = 0.6767 * P_lumen(t)

  com:
      P_lumen_micro = 13300 Pa  (100 mmHg, pressao media em microgravidade)
      p_contact_micro = 9000 Pa  (derivado em cases/artoph-mestrado/solid/0/D)

  Hipotese: relacao linear entre pressao luminal e forca de contato
  transmitida ao ONS (regime elastico linear, sem perda de contato
  durante o ciclo cardiaco - apropriado para microgravidade onde existe
  contato base sustentado).

Perfil pulsatil herdado de gen_lumen_pressure_table.py:
  P_lumen(t') = 5300 * sin(pi t'/0.218) + 10700   Pa   para t' <= 0.218 s
  P_lumen(t') = 10700                              Pa   para t'  > 0.218 s
  T_ciclo = 0.500 s  (HR ~ 120 bpm)

Saida: cases/on-mestrado/solid/constant/contact_pressure.dat
"""

import math
import os

# Parametros do ciclo cardiaco
T_sist  = 0.218   # s - duracao da sistole
T_ciclo = 0.500   # s - periodo cardiaco
P_diast = 10700.0 # Pa - 80 mmHg
P_amp   = 5300.0  # Pa - amplitude sistole-diastole

# Fator de transferencia lumen -> contato (derivado do artoph-mestrado)
ALPHA = 9000.0 / 13300.0  # ~ 0.6767

# Discretizacao temporal
dt    = 0.01     # s - passo da tabela (1/50 do ciclo)
t_end = 25.0     # s - cinquenta ciclos cardiacos completos


def P_lumen(t_local):
    if t_local <= T_sist:
        return P_amp * math.sin(math.pi * t_local / T_sist) + P_diast
    return P_diast


# Geracao da tabela
entries = []
t = 0.0
while t <= t_end + 1e-9:
    t_local = t % T_ciclo
    P_contact = ALPHA * P_lumen(t_local)
    entries.append((round(t, 4), round(P_contact, 1)))
    t = round(t + dt, 4)

# Escrita do arquivo
out_path = os.path.join(
    os.path.dirname(__file__),
    "../cases/on-mestrado/solid/constant/contact_pressure.dat",
)
out_path = os.path.normpath(out_path)

P_contact_sist = ALPHA * (P_amp + P_diast)
P_contact_diast = ALPHA * P_diast

n_ciclos = int(round(t_end / T_ciclo))
picos_t = [round(T_sist/2 + k*T_ciclo, 2) for k in range(n_ciclos)]

header = f"""\
// on-mestrado - tabela de pressao pulsatil no contato arteria-bainha
// Gerado por brunaStuff/gen_contact_pressure_table.py
//
// Derivacao:
//   p_contact(t) = ALPHA * P_lumen(t),   ALPHA = 9000/13300 = {ALPHA:.4f}
//   onde P_lumen(t) e o ciclo cardiaco do artoph-mestrado
//
// {n_ciclos} ciclos cardiacos completos (HR ~ 120 bpm, T_ciclo = {T_ciclo} s):
//   p_contact_sist  ~ {P_contact_sist:.0f} Pa   (picos em t = {picos_t} s)
//   p_contact_diast ~ {P_contact_diast:.0f} Pa   (linha de base diastolica)
//
// Hipotese: forca de contato proporcional a pressao luminal
//   (regime linear, contato sustentado em microgravidade)
//
// Formato: ( tempo[s]   pressao[Pa] )
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
print(f"ALPHA = {ALPHA:.4f}  (= 9000/13300)")
print(f"p_contact_diast = {P_contact_diast:.1f} Pa")
print(f"p_contact_sist  = {P_contact_sist:.1f} Pa")
print(f"p_contact_max em tabela = {max(P for _, P in entries):.1f} Pa")
print(f"p_contact_min em tabela = {min(P for _, P in entries):.1f} Pa")
