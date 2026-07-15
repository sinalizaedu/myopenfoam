"""Analisa o sweep ICP-driven do on-caso-1.2-fluidonly.

Para cada valor de d em [1e12, 1e13, 1e14, 1e15, 1e16] calcula:
  - p_inlet (ICP do SAS proximal, kinematic)
  - p_SAS_bulk (mean da zona sas)
  - p_pp (mean do peri_porous)
  - Δp_lid = p_SAS - p_pp
  - U_inlet (deve ser ~constante = Q_prescrito / A_inlet)
  - Re

Gera tabela e figura: brunaStuff/figs/on-caso-1.2-icp-driven.png
"""
from __future__ import annotations
import math
import sys
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, "brunaStuff")
from check_compartmentalization import parse_cellzones, parse_internal_field
from check_velocity import parse_vector_field

case = Path("cases/on-caso-1.2-fluidonly")
if not case.exists():
    case = Path("cases/artigo_mestrado/on-caso-1.2-fluidonly")
zones = parse_cellzones(case / "constant/polyMesh/cellZones")

R_PIA_OUT = 1.55e-3
R_SCLERA_IN = 2.35e-3
A_OUTLET = math.pi * (R_SCLERA_IN ** 2 - R_PIA_OUT ** 2)

d_values = [1e12, 1e13, 1e14, 1e15, 1e16]
labels_short = ["1e12", "1e13", "1e14", "1e15", "1e16"]

results = []
for ds in labels_short:
    p_path = case / f"_sweep_fluidonly/d{ds}/1/p"
    U_path = case / f"_sweep_fluidonly/d{ds}/1/U"
    if not p_path.exists():
        # try alternative paths
        candidates = list((case / f"_sweep_fluidonly/d{ds}").rglob("p"))
        if candidates:
            p_path = candidates[0]
            U_path = p_path.parent / "U"
        else:
            print(f"WARN no p for {ds}")
            continue
    p = parse_internal_field(p_path)
    U = parse_vector_field(U_path)
    sas_p = [p[i] for i in zones["sas"]]
    pp_p = [p[i] for i in zones["peri_porous"]]
    sas_U = [U[i] for i in zones["sas"]]
    pp_U = [U[i] for i in zones["peri_porous"]]

    p_max = max(p)
    sas_mean = sum(sas_p) / len(sas_p)
    pp_mean = sum(pp_p) / len(pp_p)
    sas_U_max = max((u[0]**2+u[1]**2+u[2]**2)**0.5 for u in sas_U)
    pp_U_max = max((u[0]**2+u[1]**2+u[2]**2)**0.5 for u in pp_U)
    pp_Uz_mean = sum(u[2] for u in pp_U) / len(pp_U)

    results.append(dict(
        d_label=ds, p_max=p_max,
        sas_mean=sas_mean, pp_mean=pp_mean,
        delta=sas_mean - pp_mean,
        sas_U_max=sas_U_max, pp_U_max=pp_U_max,
        Q=pp_Uz_mean * A_OUTLET,
    ))

print(f"{'d (m^-2)':<10s} | {'p_inlet (Pa)':>13s} {'ICP_bulk (Pa)':>14s} {'Δp_lid (Pa)':>13s} | "
      f"{'U_SAS (m/s)':>13s} {'Q (m³/s)':>15s}")
print("-" * 95)
for r in results:
    print(f"d={r['d_label']:<7s} | "
          f"{r['p_max']*1000:>13.1f} {r['sas_mean']*1000:>14.1f} {r['delta']*1000:>13.1f} | "
          f"{r['sas_U_max']:>13.3e} {r['Q']:>15.3e}")

# ----- Figure -----
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
ds = [float(r['d_label']) for r in results]
icp_pa = [r['sas_mean']*1000 for r in results]
delta_pa = [r['delta']*1000 for r in results]

ax = axes[0]
ax.semilogx(ds, icp_pa, "o-", color="C3", lw=2, ms=10, label="ICP_bulk (mean p in SAS)")
ax.semilogx(ds, delta_pa, "s--", color="C0", lw=2, ms=8, label="Δp_lid")
ax.axhline(1333, ls=":", color="grey", alpha=0.7, label="P_CSF normal (1333 Pa)")
ax.axhline(3800, ls=":", color="firebrick", alpha=0.7, label="P_CSF SANS (3800 Pa)")
for d, p in zip(ds, icp_pa):
    ax.annotate(f"{p:.1f} Pa", xy=(d, p), xytext=(0, 6), textcoords="offset points",
                ha="center", fontsize=8, color="C3")
ax.set_xlabel("Coeficiente de Darcy d (m$^{-2}$)", fontsize=11)
ax.set_ylabel("Pressao cinematica · ρ (Pa)", fontsize=11)
ax.set_title("ICP elevada por compartimentalizacao\n"
             "(BCs ICP-driven: Q=3e-11 m³/s prescrito no inlet)", fontsize=12)
ax.legend(loc="upper left", fontsize=9)
ax.grid(True, alpha=0.3, which="both")

# Panel 2: pressao perfil ao longo de z
ax = axes[1]
Cz_path = case / "0/Cz"
Cz = parse_internal_field(Cz_path)
z_all = np.array(Cz)
colors = ["C2", "C1", "C0", "C9", "C3"]
for i, r in enumerate(results):
    p_path = case / f"_sweep_fluidonly/d{r['d_label']}/1/p"
    p = np.array(parse_internal_field(p_path))
    z_bins = np.linspace(z_all.min(), z_all.max(), 60)
    z_mid = 0.5 * (z_bins[1:] + z_bins[:-1])
    p_avg = np.array([
        p[(z_all >= z_bins[k]) & (z_all < z_bins[k+1])].mean()
        if ((z_all >= z_bins[k]) & (z_all < z_bins[k+1])).any() else np.nan
        for k in range(len(z_bins)-1)
    ])
    ax.plot(z_mid * 1000, p_avg * 1000, "o-", color=colors[i],
            label=f"d = {r['d_label']} (ICP={r['sas_mean']*1000:.0f} Pa)",
            ms=4, alpha=0.85)
ax.axvspan(30, 30.5, alpha=0.15, color="orange", label="peri_porous (lid)")
ax.axhline(0, ls=":", color="grey", alpha=0.6)
ax.set_xlabel("z (mm)", fontsize=11)
ax.set_ylabel("Pressao cinematica · ρ (Pa)", fontsize=11)
ax.set_title("Perfil de pressao - sweep d\n(ICP sobe com d, lid concentra a queda)", fontsize=12)
ax.legend(loc="upper right", fontsize=8)
ax.grid(True, alpha=0.3)

plt.tight_layout()
out = Path("brunaStuff/figs")
out.mkdir(parents=True, exist_ok=True)
fig.savefig(out / "on-caso-1.2-icp-driven.png", dpi=130, bbox_inches="tight")
# nome esperado pelo artigo (PIC = ICP em portugues)
fig.savefig(out / "on-caso-1.2-pic-driven.png", dpi=130, bbox_inches="tight")
print(f"\nFigure saved: {out / 'on-caso-1.2-icp-driven.png'}")
print(f"Figure saved: {out / 'on-caso-1.2-pic-driven.png'}")
