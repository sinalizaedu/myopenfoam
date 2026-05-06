"""
Porous media assessment for eye-fsi-tc0.

Checks whether TM and vitreous porous zones are working physically correctly
by cross-validating three independent criteria:

 1. MASS BALANCE      — Q_TM ≈ Q_inlet at baseline (no leakage)
 2. DARCY LAW         — IOP_probe ≈ ν·d·L·Q_TM/A  (Darcy resistance correct)
 3. PRESSURE COUPLING — p_AC ≈ p_vitreous (both probes equal → zones are connected)
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

BASE = '/Users/brunaenne/Documents/repos/myopenfoam/cases/eye-fsi-tc0'

# ── Physical constants ────────────────────────────────────────────────────────
NU    = 6.97e-7    # m²/s  kinematic viscosity (transportProperties)
D_TM  = 3.08e14    # m⁻²   TM Darcy coeff (fvOptions, calibrated to IOP = 15 Torr)
L_TM  = 5.0e-4     # m     TM width (blockMeshDict col3)
RTM   = NU * D_TM * L_TM   # = 8.96e4 m/s
A_TM  = 2.4e-6     # m²    TM outlet face area
Q_PROD = 4.975e-8 / 993     # m³/s  aqueous production (U/ac_inlet)
RHO, MMHG = 993, 133.322

def to_mmhg(p_kin): return p_kin * RHO / MMHG

# ── Load data ─────────────────────────────────────────────────────────────────
tm_dat = np.loadtxt(f'{BASE}/fluid/postProcessing/flowRateTM/0/surfaceFieldValue.dat',
                    comments='#')
t_q, idx_q = np.unique(tm_dat[:,0], return_index=True)
Q_tm = tm_dat[idx_q, 1]

probe_raw = []
with open(f'{BASE}/fluid/postProcessing/iop_probe/0/p') as f:
    for line in f:
        if line.startswith('#'): continue
        parts = line.split()
        if len(parts) >= 3:
            probe_raw.append((float(parts[0]), float(parts[1]), float(parts[2])))
p_arr = np.array(probe_raw)
t_p, p_AC_kin, p_Vit_kin = p_arr[:,0], p_arr[:,1], p_arr[:,2]
p_AC  = to_mmhg(p_AC_kin)
p_Vit = to_mmhg(p_Vit_kin)

# Average per unique timestep
t_pu, idu = np.unique(t_p, return_index=True)
p_AC_u  = p_AC[idu]
p_Vit_u = p_Vit[idu]

# ── Phase masks ───────────────────────────────────────────────────────────────
mB = (t_q >= 3)  & (t_q <= 5)
mI = (t_q >= 7)  & (t_q <= 10)
mP = (t_q >= 17) & (t_q <= 20)

mBp = (t_pu >= 3)  & (t_pu <= 5)
mIp = (t_pu >= 7)  & (t_pu <= 10)
mPp = (t_pu >= 17) & (t_pu <= 20)

# ── Criterion 1: Mass balance ─────────────────────────────────────────────────
print("=" * 60)
print("CRITERION 1 — MASS BALANCE  (Q_TM = Q_inlet at baseline)")
print("=" * 60)
Q_base  = np.mean(Q_tm[mB])
Q_inj   = np.mean(Q_tm[mI])
Q_para  = np.mean(Q_tm[mP])
err_pct = abs(Q_base - Q_PROD) / Q_PROD * 100

print(f"  Q_inlet (production)  = {Q_PROD:.4e} m³/s")
print(f"  Q_TM baseline         = {Q_base:.4e} m³/s  (error: {err_pct:.2f}%)")
print(f"  Q_TM injection        = {Q_inj:.4e} m³/s  (Δ = {(Q_inj-Q_PROD)/Q_PROD*100:+.1f}%)")
print(f"  Q_TM paracentesis     = {Q_para:.4e} m³/s  (Δ = {(Q_para-Q_PROD)/Q_PROD*100:+.1f}%)")
pass1 = err_pct < 1.0
print(f"  → {'✓ PASS' if pass1 else '✗ FAIL'}  (threshold: error < 1%)")

# ── Criterion 2: Darcy Law ────────────────────────────────────────────────────
print()
print("=" * 60)
print("CRITERION 2 — DARCY LAW  (IOP_probe ≈ ½ × ν·d·L·Q_TM/A)")
print("  Note: single-cell TM → cell-centre reads ~½ of true IOP")
print("=" * 60)
for name, mask_q, mask_p in [("baseline", mB, mBp), ("injection", mI, mIp),
                               ("paracentesis", mP, mPp)]:
    Qm   = np.mean(Q_tm[mask_q])
    IOP_darcy  = RTM * Qm / A_TM * RHO / MMHG   # true IOP
    IOP_expect = 0.5 * IOP_darcy                  # expected cell-centre reading
    IOP_probe  = np.mean(p_AC_u[mask_p])
    err = abs(IOP_probe - IOP_expect) / IOP_expect * 100
    print(f"  {name:14s}: IOP_Darcy = {IOP_darcy:.1f} mmHg  "
          f"expected_probe ≈ {IOP_expect:.1f} mmHg  "
          f"measured = {IOP_probe:.1f} mmHg  (err {err:.0f}%)")

# ── Criterion 3: Pressure coupling ───────────────────────────────────────────
print()
print("=" * 60)
print("CRITERION 3 — PRESSURE COUPLING  (p_AC = p_vitreous)")
print("  Both zones should be in pressure equilibrium via the")
print("  internal face at y=14.4mm, x=[15,20mm].")
print("=" * 60)
diff_B = np.mean(np.abs(p_AC_u[mBp] - p_Vit_u[mBp]))
diff_I = np.mean(np.abs(p_AC_u[mIp] - p_Vit_u[mIp]))
diff_P = np.mean(np.abs(p_AC_u[mPp] - p_Vit_u[mPp]))
for name, diff in [("baseline", diff_B), ("injection", diff_I), ("paracentesis", diff_P)]:
    print(f"  {name:14s}: |p_AC - p_vitreous| = {diff:.4f} mmHg  "
          f"({'✓ coupled' if diff < 0.01 else '✗ decoupled'})")

# ── Plot: IOP curve (corrected RTM) ──────────────────────────────────────────
IOP_mmHg = RTM * Q_tm / A_TM * RHO / MMHG

def smooth(x, w=15):
    xp = np.pad(x, w//2, mode='edge')
    return np.lib.stride_tricks.sliding_window_view(xp, w).mean(-1)

phases = [(0,5,'#e8f4f8','Baseline'),(5,11,'#ffeeba','IVI Injection'),
          (11,15,'#e8f4f8','Recovery'),(15,21,'#ffe0e0','Paracentesis'),(21,25,'#e8f4f8','Recovery')]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
fig.suptitle('Porous Media Assessment — eye-fsi-tc0 FSI', fontsize=13)

# Top: IOP from Darcy (Q_TM-based)
for t0,t1,c,_ in phases: ax1.axvspan(t0,t1,alpha=0.3,color=c,zorder=0)
for td in [5,11,15,21]: ax1.axvline(td,color='gray',lw=0.7,ls='--')
ax1.plot(t_q, IOP_mmHg, color='steelblue', alpha=0.2, lw=0.7)
ax1.plot(t_q, smooth(IOP_mmHg), color='steelblue', lw=2, label='IOP (Darcy = ν·d·L·Q_TM/A)')
ax1.plot(t_pu, p_AC_u, color='coral', alpha=0.2, lw=0.7)
ax1.plot(t_pu, smooth(p_AC_u), color='coral', lw=2, ls='--', label='p_AC probe (≈ ½ IOP, 1-cell TM)')
ax1.plot(t_pu, smooth(p_Vit_u), color='forestgreen', lw=1.5, ls=':', label='p_Vitreous probe')
ax1.axhline(10, color='green', lw=0.6, ls=':', alpha=0.5)
ax1.axhline(21, color='green', lw=0.6, ls=':', alpha=0.5)
ax1.set_ylabel('IOP [mmHg]')
ax1.set_ylim(0, 22)
ax1.legend(fontsize=8, loc='upper right')
ax1.grid(True, alpha=0.3)
ax1.set_title('IOP from Q_TM (Darcy) vs interior probe', fontsize=10)

# Phase labels
for t0,t1,_,lbl in phases:
    ax1.text((t0+t1)/2/25, 0.97, lbl, ha='center', va='top', fontsize=7,
             color='dimgray', transform=ax1.transAxes)

# Bottom: Q_TM flow balance
for t0,t1,c,_ in phases: ax2.axvspan(t0,t1,alpha=0.3,color=c,zorder=0)
for td in [5,11,15,21]: ax2.axvline(td,color='gray',lw=0.7,ls='--')
ax2.axhline(Q_PROD*1e12, color='gray', lw=1.5, ls='--', label=f'Q_inlet = {Q_PROD*1e12:.2f} pL/s')
ax2.plot(t_q, Q_tm*1e12, color='steelblue', alpha=0.25, lw=0.7)
ax2.plot(t_q, smooth(Q_tm*1e12), color='steelblue', lw=2, label='Q_TM outlet (TM drainage)')
ax2.set_ylabel('Flow rate [pL/s]')
ax2.set_xlabel('Time [s]')
ax2.legend(fontsize=8, loc='upper right')
ax2.grid(True, alpha=0.3)
ax2.set_title('TM flow balance — Q_TM ≈ Q_inlet at baseline confirms TM is active', fontsize=10)

for t0,t1,_,lbl in phases:
    ax2.text((t0+t1)/2/25, 0.97, lbl, ha='center', va='top', fontsize=7,
             color='dimgray', transform=ax2.transAxes)

ax2.set_xlim(0, 25)
plt.tight_layout()
out = '/Users/brunaenne/Documents/repos/myopenfoam/brunaStuff/porous_assessment.png'
plt.savefig(out, dpi=150, bbox_inches='tight')
print(f'\nPlot saved: {out}')
