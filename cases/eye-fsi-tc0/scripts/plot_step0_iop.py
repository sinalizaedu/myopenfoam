#!/usr/bin/env python3
"""Plot steady IOP vs simpleFoam iteration (Step 0)."""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RHO = 995  # kg/m³ — Lamminsalo Tabela I ᵈ @ 37 °C
PA_TO_MMHG = 0.0075006

case = Path(__file__).resolve().parent.parent
probe = case / "fluid" / "postProcessing" / "iop_probe" / "0" / "p"
out = case / "figures" / "iop_step0_steady.png"
out.parent.mkdir(exist_ok=True)

times, ac_r = [], []
for line in probe.read_text().splitlines():
    line = line.strip()
    if line.startswith("#") or not line:
        continue
    parts = line.split()
    if len(parts) >= 2:
        times.append(float(parts[0]))
        ac_r.append(float(parts[1]) * RHO * PA_TO_MMHG)

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(times, ac_r, label="IOP AC (right probe)")
ax.axhline(15.0, color="k", ls="--", lw=0.8, label="Target 15 mmHg")
ax.set_xlabel("Iteration")
ax.set_ylabel("IOP (mmHg)")
ax.set_title("Sim 1 Step 0 — steady convergence")
ax.legend()
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(out, dpi=150)
print(f"Wrote {out}")
