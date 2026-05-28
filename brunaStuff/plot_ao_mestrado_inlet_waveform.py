#!/usr/bin/env python3
"""Plota a tabela inlet_pressure.dat de cases/ao-mestrado para conferencia
visual da onda OMVS 6-piece (SP=120, DP=80, HR=69 bpm)."""
from pathlib import Path
import re
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[1]
INLET = REPO / "cases" / "ao-mestrado" / "fluid" / "constant" / "inlet_pressure.dat"
OUTLET = REPO / "cases" / "ao-mestrado" / "fluid" / "constant" / "outlet_pressure.dat"
OUT = REPO / "brunaStuff" / "plot_ao_mestrado_inlet_waveform.png"

RHO = 1050.0
MMHG = 133.322387415

PAT = re.compile(r"\(\s*([\d.eE+-]+)\s+([\d.eE+-]+)\s*\)")


def load(path: Path):
    ts, ps = [], []
    for line in path.read_text().splitlines():
        m = PAT.search(line)
        if m:
            ts.append(float(m.group(1)))
            ps.append(float(m.group(2)) * RHO / MMHG)  # m^2/s^2 -> Pa -> mmHg
    return ts, ps


t1, p1 = load(INLET)
t2, p2 = load(OUTLET)

fig, axes = plt.subplots(1, 3, figsize=(18, 4.2))

ax = axes[0]
ax.plot(t1, p1, "tab:red", lw=1.4, label="inlet")
ax.plot(t2, p2, "tab:blue", lw=1.0, ls="--", label="outlet", alpha=0.7)
ax.axhline(120, ls=":", c="k", lw=0.8, alpha=0.5)
ax.axhline(80, ls=":", c="k", lw=0.8, alpha=0.5)
ax.axvspan(0.0, 0.10, alpha=0.15, color="orange", label="rampa Hann (100ms)")
ax.text(0.05, 121, "SP=120", fontsize=8, color="gray")
ax.text(0.05, 81, "DP=80", fontsize=8, color="gray")
ax.set_xlabel("tempo (s)"); ax.set_ylabel("pressao (mmHg)")
ax.set_title("Onda completa: 3 ciclos com rampa total")
ax.grid(alpha=0.3); ax.legend(loc="lower right", fontsize=8)

ax = axes[1]
ax.plot(t1, [a-b for a,b in zip(p1,p2)], "tab:purple", lw=1.0, label="Δp = p_in − p_out")
ax.axhline(0, ls=":", c="k", lw=0.6)
ax.axvspan(0.0, 0.10, alpha=0.15, color="orange")
ax.set_xlabel("tempo (s)"); ax.set_ylabel("Δp (mmHg)")
ax.set_title("Gradiente longitudinal pulsatil\n(criado pelo shift de 5ms no outlet)")
ax.grid(alpha=0.3); ax.legend(loc="best", fontsize=8)

ax = axes[2]
T_cycle = 0.8696
n_one = sum(1 for t in t1 if T_cycle*2 <= t <= T_cycle*3 + 1e-3)
i0 = next(i for i,t in enumerate(t1) if t >= T_cycle*2)
i1 = i0 + n_one
t3 = [t-T_cycle*2 for t in t1[i0:i1]]
ax.plot(t3, p1[i0:i1], "tab:red", lw=1.6, label="inlet, ciclo 3")
ax.plot(t3, p2[i0:i1], "tab:blue", lw=1.0, ls="--", label="outlet, ciclo 3", alpha=0.7)
ax.axhline(120, ls=":", c="k", lw=0.8); ax.axhline(80, ls=":", c="k", lw=0.8)
markers = [
    (0.000, 80, "DP"),
    (0.1565, 120, "SP"),
    (0.2609, 80 + 0.55*40, "incisura"),
    (0.3478, 80 + 0.65*40, "dicrotico"),
    (0.4783, 80 + 0.40*40, "meio diast."),
]
for tt, pp, lbl in markers:
    ax.plot(tt, pp, "ko", ms=4)
    ax.annotate(lbl, (tt, pp), xytext=(5, 5), textcoords="offset points", fontsize=8)
ax.set_xlabel("tempo no ciclo (s)"); ax.set_ylabel("pressao (mmHg)")
ax.set_title(f"3o ciclo (regime): T={T_cycle:.3f} s, HR=69 bpm")
ax.grid(alpha=0.3); ax.legend(loc="lower right", fontsize=8)

plt.tight_layout()
plt.savefig(OUT, dpi=130)
print(f"[write] {OUT}")
print(f"  Δp range: [{min(a-b for a,b in zip(p1,p2)):.4f}, {max(a-b for a,b in zip(p1,p2)):.4f}] mmHg")
print(f"  Δp range: [{min(a-b for a,b in zip(p1,p2))*MMHG:.2f}, {max(a-b for a,b in zip(p1,p2))*MMHG:.2f}] Pa")
