#!/usr/bin/env python3
"""Plot do ciclo cardiaco completo (0.8 s) do FSI two-way refeito com a
polyMesh tubular extrudada."""
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

CASE = Path(__file__).resolve().parents[1] / "cases" / "artoph-fsi-curva-mestrado"
OUT = Path(__file__).resolve().parent / "artoph_fsi_final_cycle.png"

# Parse fluid log
flog = (CASE / "fluid" / "log.pimpleFoam").read_text()
t_fluid = [float(m.group(1)) for m in re.finditer(r"^Time = ([\d.eE+-]+)", flog, re.MULTILINE)]
co = [float(m.group(1)) for m in re.finditer(r"Courant Number.*max: ([\d.eE+-]+)", flog)]
# Cada timestep pode ter multiplas linhas Courant; pegar a primeira por timestep
n = min(len(t_fluid), len(co))
t_fluid = t_fluid[:n]
co = co[:n]

# Parse solid log: cada timestep emite "Time = X" -> "Max sigmaEq = Y" -> ...
# Pegar (t, sigma, eps) por timestep
slog = (CASE / "solid" / "log.solids4Foam").read_text()
solid_records: list[tuple[float, float, float]] = []
cur_t = None
cur_eps = None
for line in slog.splitlines():
    m1 = re.match(r"^Time = ([\d.eE+-]+)", line)
    if m1:
        cur_t = float(m1.group(1))
        cur_eps = None
        continue
    m3 = re.search(r"Max epsilonEq = ([\d.eE+-]+)", line)
    if m3 and cur_t is not None:
        cur_eps = float(m3.group(1))
        continue
    m2 = re.search(r"Max sigmaEq.*= ([\d.eE+-]+)", line)
    if m2 and cur_t is not None and cur_eps is not None:
        solid_records.append((cur_t, float(m2.group(1)), cur_eps))
        cur_eps = None
t_solid = np.array([r[0] for r in solid_records])
sigma = np.array([r[1] for r in solid_records])
eps = np.array([r[2] for r in solid_records])

# Parse inlet pressure (kinematic)
p_table = []
for line in (CASE / "fluid" / "constant" / "inlet_pressure.dat").read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("//") or line.startswith("(") and line.endswith(")") and " " not in line:
        continue
    m2 = re.match(r"\(([\d.eE+-]+)\s+([\d.eE+-]+)\)", line)
    if m2:
        p_table.append((float(m2.group(1)), float(m2.group(2))))
t_p = [x[0] for x in p_table]
p_kin = np.array([x[1] for x in p_table])
p_pa = p_kin * 1050.0  # rho_blood

fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)

# Limitar pressao ao intervalo [0, 0.8] (1 ciclo)
t_p_arr = np.array(t_p)
mask = t_p_arr <= 0.8
axes[0].plot(t_p_arr[mask], p_pa[mask] / 1000.0, color="C0", lw=1.5, label="P inlet")
axes[0].axhline(13.3, ls="--", color="gray", alpha=0.6, label="PAM 13.3 kPa")
axes[0].set_ylabel("Pressao [kPa]")
axes[0].set_title("Ciclo cardiaco FSI two-way (polyMesh tubular extrudada, 0.8 s)")
axes[0].legend(loc="upper right")
axes[0].grid(alpha=0.3)

axes[1].plot(t_fluid, co, color="C1", lw=1.5)
axes[1].set_ylabel("Courant max")
axes[1].axhline(1.0, ls="--", color="red", alpha=0.6, label="Co = 1 (estabilidade)")
axes[1].legend(loc="upper right")
axes[1].grid(alpha=0.3)

axes[2].plot(t_solid, sigma / 1000.0, color="C3", lw=1.5, label="von Mises max")
axes[2].set_ylabel(r"$\sigma_{vM,\mathrm{max}}$ [kPa]")
axes[2].set_xlabel("t [s]")
ax2 = axes[2].twinx()
ax2.plot(t_solid, eps * 100, color="C2", lw=1.0, ls="--", alpha=0.7, label="strain max (%)")
ax2.set_ylabel(r"$\varepsilon_{eq,\mathrm{max}}$ [%]", color="C2")
ax2.tick_params(axis="y", labelcolor="C2")
axes[2].legend(loc="upper left")
ax2.legend(loc="upper right")
axes[2].grid(alpha=0.3)

plt.tight_layout()
plt.savefig(OUT, dpi=130, bbox_inches="tight")
print(f"Salvo em {OUT}")
print(f"  Fluid: {len(t_fluid)} timesteps, Co range = [{min(co):.2e}, {max(co):.2e}]")
print(f"  Solid: {len(t_solid)} timesteps")
print(f"    sigmaEq range = [{sigma.min()/1000:.2f}, {sigma.max()/1000:.2f}] kPa")
print(f"    epsilonEq range = [{eps.min()*100:.3f}, {eps.max()*100:.3f}] %")
