"""
Plot IOP vs time from eye-fsi-tc0 simulation.

IOP is computed from the TM outflow rate via Darcy's law:
  IOP [m²/s²] = RTM × Q_TM / A_TM
  IOP [mmHg]  = IOP [m²/s²] × ρ / 133.322
where RTM = ν × d_eff × L_mesh = 9.64e4 m/s (kinematic TM resistance),
      A_TM = 2.4e-3 m × 1e-3 m = 2.4e-6 m².

Simulation phases:
  t =  0 –  5 s : baseline (ac_inlet only)
  t =  5 – 11 s : IVI injection (needle_inlet + ac_inlet)
  t = 11 – 15 s : post-injection recovery
  t = 15 – 21 s : paracentesis (needle_outlet + ac_inlet)
  t = 21 – 25 s : post-paracentesis recovery
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Data paths ────────────────────────────────────────────────────────────────
BASE = '/Users/brunaenne/Documents/repos/myopenfoam/cases/eye-fsi-tc0'
TM_FILE = f'{BASE}/fluid/postProcessing/flowRateTM/0/surfaceFieldValue.dat'

# ── Physical constants ────────────────────────────────────────────────────────
NU    = 6.97e-7       # m²/s (kinematic viscosity, aqueous humor at 37°C, from transportProperties)
D_TM  = 2.57e14       # m⁻²  (Darcy resistance coefficient, fvOptions)
L_TM  = 5.0e-4        # m    (TM cell block width, x=[19.5,20mm])
RTM   = NU * D_TM * L_TM   # m/s  = 8.96e4 (kinematic TM resistance)
A_TM  = 2.4e-6        # m²   (outlet_tm face area, y=[0,2.4mm] × z=[0,1mm])
RHO   = 993           # kg/m³ (density, aqueous humor at 37°C)
MMHG  = 133.322       # Pa/mmHg

# ── Load data ─────────────────────────────────────────────────────────────────
data = np.loadtxt(TM_FILE, comments='#')
t_raw, Q_raw = data[:, 0], data[:, 1]

# Keep one value per unique timestep (multiple FSI iterations write same t)
t_unique, idx = np.unique(t_raw, return_index=True)
Q_tm = Q_raw[idx]

# ── Compute IOP ───────────────────────────────────────────────────────────────
IOP_m2s2 = RTM * Q_tm / A_TM          # kinematic pressure [m²/s²]
IOP_mmHg = IOP_m2s2 * RHO / MMHG     # IOP [mmHg]

# ── Smooth for display (rolling mean, window=15 timesteps) ───────────────────
from numpy.lib.stride_tricks import sliding_window_view
def smooth(x, w=15):
    pad = w // 2
    xp  = np.pad(x, pad, mode='edge')
    return sliding_window_view(xp, w).mean(axis=-1)

t_sm  = t_unique
iop_sm = smooth(IOP_mmHg, w=15)

# ── Phase annotation ──────────────────────────────────────────────────────────
phases = [
    (0,  5,  '#e8f4f8', 'Baseline'),
    (5,  11, '#ffeeba', 'IVI Injection'),
    (11, 15, '#e8f4f8', 'Recovery'),
    (15, 21, '#ffe0e0', 'Paracentesis'),
    (21, 25, '#e8f4f8', 'Recovery'),
]

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 5))

# Phase bands
for t0, t1, color, label in phases:
    ax.axvspan(t0, t1, alpha=0.35, color=color, zorder=0)

# Phase dividers
for t_div in [5, 11, 15, 21]:
    ax.axvline(t_div, color='gray', lw=0.8, ls='--', zorder=1)

# IOP data (raw, semi-transparent) and smoothed
ax.plot(t_unique, IOP_mmHg, color='steelblue', alpha=0.25, lw=0.7, label='IOP (per timestep)')
ax.plot(t_sm, iop_sm, color='steelblue', lw=2.2, label='IOP (smoothed)')

# Phase labels (in axes coordinates: x normalised, y near top)
phase_centers_norm = [(t0 + t1) / 2 / 25 for t0, t1, *_ in phases]
phase_names   = ['Baseline', 'IVI\nInjection', 'Recovery', 'Paracentesis', 'Recovery']
for xc, name in zip(phase_centers_norm, phase_names):
    ax.text(xc, 0.97, name,
            ha='center', va='top', fontsize=8, color='dimgray',
            transform=ax.transAxes)

# Reference line (normal IOP range)
ax.axhline(10, color='green', lw=0.8, ls=':', alpha=0.7)
ax.axhline(21, color='green', lw=0.8, ls=':', alpha=0.7)
ax.text(0.5, 10.3, 'Normal IOP lower (10 mmHg)', fontsize=7, color='green', alpha=0.7)
ax.text(0.5, 21.3, 'Normal IOP upper (21 mmHg)', fontsize=7, color='green', alpha=0.7)

# Labels
ax.set_xlabel('Time [s]', fontsize=12)
ax.set_ylabel('IOP [mmHg]', fontsize=12)
ax.set_title('Intraocular Pressure — IVI + Paracentesis (eye-fsi-tc0 FSI simulation)', fontsize=12)
ax.set_xlim(0, 25)
ax.set_ylim(0, 25)
ax.legend(loc='lower right', fontsize=9)
ax.grid(True, alpha=0.3)

# Phase legend patches
legend_patches = [
    mpatches.Patch(color='#e8f4f8', alpha=0.7, label='Baseline / Recovery'),
    mpatches.Patch(color='#ffeeba', alpha=0.7, label='IVI Injection (t=5–11 s)'),
    mpatches.Patch(color='#ffe0e0', alpha=0.7, label='Paracentesis (t=15–21 s)'),
]
ax.legend(handles=legend_patches + [
    plt.Line2D([0], [0], color='steelblue', lw=2.2, label='IOP (smoothed)'),
    plt.Line2D([0], [0], color='steelblue', lw=0.7, alpha=0.4, label='IOP (per step)'),
], loc='lower right', fontsize=8)

plt.tight_layout()
out = '/Users/brunaenne/Documents/repos/myopenfoam/brunaStuff/iop_curve.png'
plt.savefig(out, dpi=150, bbox_inches='tight')
print(f'Saved: {out}')

# ── Summary statistics ────────────────────────────────────────────────────────
mask_base  = (t_unique >= 3)    & (t_unique <= 5)
mask_inj   = (t_unique >= 7)    & (t_unique <= 10)
mask_para  = (t_unique >= 17)   & (t_unique <= 20)

def m(arr, mask): return np.mean(arr[mask]) if mask.any() else float('nan')

print('\n=== IOP statistics ===')
print(f'  Baseline  (t=3–5 s)     : {m(IOP_mmHg, mask_base):.1f} mmHg')
print(f'  Injection (t=7–10 s)    : {m(IOP_mmHg, mask_inj):.1f} mmHg')
print(f'  Paracentesis (t=17–20s) : {m(IOP_mmHg, mask_para):.1f} mmHg')
print(f'  ΔP injection             : {m(IOP_mmHg, mask_inj) - m(IOP_mmHg, mask_base):+.1f} mmHg')
print(f'  ΔP paracentesis          : {m(IOP_mmHg, mask_para) - m(IOP_mmHg, mask_base):+.1f} mmHg')
