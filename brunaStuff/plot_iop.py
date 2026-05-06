"""
plot_iop.py  —  eye-fsi-tc0  IOP vs time
=========================================
Reads postProcessing data from the FSI case and plots:
  - IOP  : pressure probe inside the AC (upstream of TM porous zone)
           kinematic p [m²/s²] × rho=993 → Pa → mmHg
  - TM flow rate: volumetric flow at outlet_tm [nL/s]
  - Shaded bands for injection and paracentesis phases.

Probe location: (0.010, 0.005, 0.0005) m — centre of AC, row1 col1.
Run from workspace root:
    python3 brunaStuff/plot_iop.py
"""

import pathlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR  = pathlib.Path(__file__).parent
CASE_FLUID  = SCRIPT_DIR.parent / "cases" / "eye-fsi-tc0" / "fluid" / "postProcessing"
PROBE_FILE  = CASE_FLUID / "iop_probe" / "0" / "p"
FLOW_FILE   = CASE_FLUID / "flowRateTM" / "0" / "surfaceFieldValue.dat"
OUT_PNG     = SCRIPT_DIR / "iop_curve.png"

RHO         = 993.0       # kg/m³  (aqueous humor density)
PA_TO_MMHG  = 0.0075006   # 1 Pa = 0.0075006 mmHg


def read_probe(path: pathlib.Path) -> tuple[np.ndarray, np.ndarray]:
    """Parse OpenFOAM probes file.
    Format: comment lines starting with '#', then 'time  val' per row.
    When preCICE writes multiple iterations per timestep the last value
    for each unique time is kept (converged value).
    """
    times, values = [], []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            parts = line.split()
            if len(parts) >= 2:
                try:
                    times.append(float(parts[0]))
                    values.append(float(parts[1]))
                except ValueError:
                    continue

    times  = np.array(times)
    values = np.array(values)

    # keep last entry per unique timestep
    unique_t = np.unique(times)
    last_vals = np.array([values[times == t][-1] for t in unique_t])
    return unique_t, last_vals


def read_dat(path: pathlib.Path) -> tuple[np.ndarray, np.ndarray]:
    """Parse surfaceFieldValue.dat, keeping last value per unique timestep."""
    times, values = [], []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            parts = line.split()
            if len(parts) >= 2:
                try:
                    times.append(float(parts[0]))
                    values.append(float(parts[1]))
                except ValueError:
                    continue

    times  = np.array(times)
    values = np.array(values)
    unique_t = np.unique(times)
    last_vals = np.array([values[times == t][-1] for t in unique_t])
    return unique_t, last_vals


# ── load data ──────────────────────────────────────────────────────────────────
if not PROBE_FILE.exists():
    raise FileNotFoundError(
        f"Probe file not found: {PROBE_FILE}\n"
        "Run the simulation first (blockMesh + Allrun inside Docker)."
    )

t_iop,  p_kin  = read_probe(PROBE_FILE)
t_flow, q_tm   = read_dat(FLOW_FILE)

p_pa   = p_kin * RHO
p_mmhg = p_pa  * PA_TO_MMHG
q_nl_s = np.abs(q_tm) * 1e12   # m³/s → nL/s


# ── figure ─────────────────────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(
    2, 1, figsize=(11, 7), sharex=True,
    gridspec_kw={"hspace": 0.08}
)

phases = [
    (0,  5,  "#e8f4e8", "Baseline"),
    (5,  11, "#fde8e8", "Injection"),
    (11, 15, "#e8f4e8", "Recovery"),
    (15, 21, "#e8e8fd", "Paracentesis"),
    (21, 25, "#e8f4e8", "Recovery"),
]
for ax in (ax1, ax2):
    for x0, x1, col, _ in phases:
        ax.axvspan(x0, x1, color=col, alpha=0.7, zorder=0)

# ── IOP panel ─────────────────────────────────────────────────────────────────
ax1.plot(t_iop, p_mmhg, color="#c0392b", linewidth=1.4, label="IOP — AC probe (mmHg)")
ax1.set_ylabel("Pressure (mmHg)", fontsize=11)
ax1.legend(loc="upper right", fontsize=9)
ax1.grid(True, linestyle="--", linewidth=0.4, alpha=0.5)
ax1.set_title(
    "eye-fsi-tc0  —  IOP with TM + vitreous porous resistance\n"
    r"TM: $\alpha=2.3\times10^{15}\ \mathrm{m}^{-2}$   "
    r"Vitreous: $\alpha=1.72\times10^{13}\ \mathrm{m}^{-2}$",
    fontsize=11, pad=8
)

# secondary y-axis in Pa
ax1b = ax1.twinx()
ax1b.set_ylabel("Pressure (Pa)", fontsize=10, color="#7f8c8d")
ax1b.tick_params(axis="y", labelcolor="#7f8c8d")
lim = ax1.get_ylim()
ax1b.set_ylim(np.array(lim) / PA_TO_MMHG)

# ── Flow rate panel ────────────────────────────────────────────────────────────
ax2.plot(t_flow, q_nl_s, color="#2980b9", linewidth=1.4, label="TM outflow rate (nL/s)")
ax2.set_ylabel("TM flow rate (nL/s)", fontsize=11)
ax2.set_xlabel("Time (s)", fontsize=11)
ax2.legend(loc="upper right", fontsize=9)
ax2.grid(True, linestyle="--", linewidth=0.4, alpha=0.5)

# phase legend
legend_patches = [
    mpatches.Patch(facecolor="#fde8e8", edgecolor="none", label="Injection (t=5–11 s)"),
    mpatches.Patch(facecolor="#e8e8fd", edgecolor="none", label="Paracentesis (t=15–21 s)"),
    mpatches.Patch(facecolor="#e8f4e8", edgecolor="none", label="Baseline / Recovery"),
]
fig.legend(handles=legend_patches, loc="lower center", ncol=3,
           fontsize=9, frameon=True, bbox_to_anchor=(0.5, 0.0))

plt.tight_layout(rect=[0, 0.04, 1, 1])
fig.savefig(OUT_PNG, dpi=150, bbox_inches="tight")
print(f"Saved → {OUT_PNG}")
