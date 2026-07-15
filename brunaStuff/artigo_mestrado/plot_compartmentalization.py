"""Plota a compartimentalizacao Darcy-driven do on-caso-1.2.

Gera duas figuras:
  1. Q_drenagem vs d em escala log-log (mostra escalamento Q ~ 1/d)
  2. Perfil de pressao p ao longo do eixo z para os 3 valores de d

Output:
  brunaStuff/figs/on-caso-1.2-compartmentalization.png
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

case = Path("cases/on-caso-1.2")
zones = parse_cellzones(case / "fluid/constant/polyMesh/cellZones")

R_PIA_OUT = 1.55e-3
R_SCLERA_IN = 2.35e-3
A_OUTLET = math.pi * (R_SCLERA_IN ** 2 - R_PIA_OUT ** 2)


def parse_cell_centers(path: Path) -> list[tuple[float, float, float]]:
    """Le os centroides de celula (gerados via writeCellCentres)."""
    import re

    text = path.read_text()
    m = re.search(
        r"internalField\s+nonuniform\s+List<vector>\s*\n\s*(\d+)\s*\(\s*([\s\S]+?)\)\s*;",
        text,
    )
    n = int(m.group(1))
    triples = re.findall(r"\(([-+0-9.eE\s]+)\)", m.group(2))
    out = []
    for t in triples:
        parts = t.split()
        out.append((float(parts[0]), float(parts[1]), float(parts[2])))
    assert len(out) == n
    return out


d_values = [1e13, 1e15, 1e17]
labels = ["d = 1e13 (open)", "d = 1e15 (healthy)", "d = 1e17 (IIH/SANS)"]
colors = ["C2", "C0", "C3"]
sweep = case / "_sweep"

Q_list = []
ICP_list = []
all_p = []
all_U = []
labels_short = ["1e13", "1e15", "1e17"]
for label_short in labels_short:
    p = parse_internal_field(sweep / f"d{label_short}/1/p")
    U = parse_vector_field(sweep / f"d{label_short}/1/U")
    all_p.append(p)
    all_U.append(U)

    pp_ids = zones["peri_porous"]
    sas_ids = zones["sas"]

    Uz_pp_mean = sum(U[i][2] for i in pp_ids) / len(pp_ids)
    Q_list.append(Uz_pp_mean * A_OUTLET)
    ICP_list.append(sum(p[i] for i in sas_ids) / len(sas_ids))

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Panel 1: Q vs d (log-log)
ax = axes[0]
ax.loglog(d_values, np.abs(Q_list), "o-", color="C0", markersize=10, lw=2)
for i, (d, q) in enumerate(zip(d_values, Q_list)):
    ax.annotate(
        f"  {labels[i].split('(')[1].rstrip(')')}\n  Q = {q:.2e}",
        xy=(d, abs(q)),
        fontsize=9,
        ha="left",
        va="center",
    )

ax.axhline(3e-11, ls="--", color="grey", alpha=0.6,
           label="Q_fisiologico ~ 3e-11 m³/s")
ax.set_xlabel("Coeficiente de Darcy d (m$^{-2}$)", fontsize=11)
ax.set_ylabel("|Vazao de drenagem| Q (m³/s)", fontsize=11)
ax.set_title("Compartimentalizacao Darcy-driven\n(on-caso-1.2)", fontsize=12)
ax.grid(True, which="both", alpha=0.3)
ax.legend(loc="upper right", fontsize=9)
ax.set_xlim(3e12, 3e17)

# Panel 2: perfil de p ao longo de z
ax = axes[1]
# Usa o campo Cz gerado por writeCellCentres
Cz = parse_internal_field(case / "fluid/0/Cz")
z_all = np.array(Cz)

for label_short, color, label in zip(labels_short, colors, labels):
    p = all_p[labels_short.index(label_short)]
    p = np.array(p)

    z_bins = np.linspace(z_all.min(), z_all.max(), 60)
    z_mid = 0.5 * (z_bins[1:] + z_bins[:-1])
    p_avg = np.array([
        p[(z_all >= z_bins[i]) & (z_all < z_bins[i + 1])].mean()
        if ((z_all >= z_bins[i]) & (z_all < z_bins[i + 1])).any()
        else np.nan
        for i in range(len(z_bins) - 1)
    ])
    ax.plot(z_mid * 1000, p_avg * 1000, "o-", color=color, label=label, ms=4, alpha=0.85)

ax.axvspan(30, 30.5, alpha=0.15, color="orange", label="peri_porous (lid)")
ax.axhline(1333, ls=":", color="grey", alpha=0.6, label="p_inlet")
ax.axhline(0, ls=":", color="grey", alpha=0.6)
ax.set_xlabel("z (mm)", fontsize=11)
ax.set_ylabel("Pressao cinematica p · ρ (Pa)", fontsize=11)
ax.set_title("Distribuicao de pressao ao longo do eixo z\n(BCs fixedValue: queda total ancorada)", fontsize=12)
ax.legend(loc="lower left", fontsize=9)
ax.grid(True, alpha=0.3)

plt.tight_layout()
out = Path("brunaStuff/figs")
out.mkdir(parents=True, exist_ok=True)
fig.savefig(out / "on-caso-1.2-compartmentalization.png", dpi=130, bbox_inches="tight")
print(f"Figure saved: {out / 'on-caso-1.2-compartmentalization.png'}")
