#!/usr/bin/env python3
"""
view_on-caso-3J.py
==================
Visualizacao rapida do Caso 3J (geometria em "J" + cargas 3F):
  - le os nos de REFERENCIA da malja varrida (on-caso-3J_mesh.inp)
  - le o deslocamento U do ULTIMO passo de carga (lam max) do .frd
  - plota o plano XY (plano do "J"): referencia (cinza) vs deformado
    (colorido por |U_lat| = sqrt(Ux^2+Uy^2)) -> mostra o kink/dobramento.

Uso: brunaStuff/.venv/bin/python brunaStuff/view_on-caso-3J.py
"""
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from frd_stress import parse_frd
from inp_to_vtk import parse_inp

CCX = HERE.parent / "cases" / "on-caso-3J" / "ccx"
MESH = CCX / "on-caso-3J_mesh.inp"
FRD = CCX / "on-caso-3J.frd"
OUT = HERE / "on-caso-3J_view.png"

# zonas estruturais a desenhar (ignora SAS p/ nao poluir; mantem meninges+nervo)
DRAW_ZONES = {"ON", "PIA", "DURA", "LC", "SCLERA_PERI", "SCLERA_RING", "GLOBO"}

nodes, elems = parse_inp(MESH)
ref = {nid: np.array(xyz) for nid, xyz in nodes.items()}

# nos que pertencem as zonas desenhadas
draw_nids = sorted({n for (_eid, conn, z) in elems if z in DRAW_ZONES for n in conn})
R = np.array([ref[n] for n in draw_nids])  # (N,3) em metros

# deslocamento do ultimo passo (lam max)
_, _n2zone, steps = parse_frd(FRD)
steps = [s for s in steps if s.get("disp")]
last = max(steps, key=lambda d: (d["lam"] if d["lam"] is not None else 0.0))
lam = last["lam"]
disp = last["disp"]
U = np.array([disp.get(n, (0.0, 0.0, 0.0)) for n in draw_nids])  # (N,3)

D = R + U
ulat = np.hypot(U[:, 0], U[:, 1]) * 1e3  # mm, no plano do J (XY)

mm = 1e3
fig, axes = plt.subplots(1, 2, figsize=(12, 7))
fig.suptitle(f"Caso 3J - geometria em \"J\" (Caso 2J) + cargas 3F "
             f"(Dy=-1.0 mm, p_c=9034 Pa, PIC) | lambda={lam:.3f}", fontsize=12)

# Painel A: referencia vs deformado no plano XY (plano do J)
ax = axes[0]
ax.scatter(R[:, 0] * mm, R[:, 1] * mm, s=3, c="0.75",
           label="referencia (J inicial)", zorder=1)
sc = ax.scatter(D[:, 0] * mm, D[:, 1] * mm, s=4, c=ulat, cmap="viridis",
                label="deformado", zorder=2)
ax.scatter([0], [0], marker="*", s=180, c="red", zorder=3, label="globo (origem)")
cb = fig.colorbar(sc, ax=ax, shrink=0.8)
cb.set_label("|U_lat| = sqrt(Ux^2+Uy^2) [mm]")
ax.set_xlabel("X [mm]"); ax.set_ylabel("Y [mm]")
ax.set_title("(A) Plano do \"J\" (XY): referencia vs deformado")
ax.set_aspect("equal"); ax.grid(alpha=0.3); ax.legend(loc="best", fontsize=8)

# Painel B: vista lateral XZ (espessura em Z) -> mostra excursao fora do plano
ax = axes[1]
uoop = np.abs(U[:, 2]) * 1e3
sc2 = ax.scatter(D[:, 0] * mm, D[:, 2] * mm, s=4, c=uoop, cmap="magma", zorder=2)
ax.scatter(R[:, 0] * mm, R[:, 2] * mm, s=3, c="0.8", zorder=1)
cb2 = fig.colorbar(sc2, ax=ax, shrink=0.8)
cb2.set_label("|Uz| fora do plano [mm]")
ax.set_xlabel("X [mm]"); ax.set_ylabel("Z [mm] (espessura)")
ax.set_title("(B) Vista XZ: excursao fora do plano (lado da arteria)")
ax.set_aspect("equal"); ax.grid(alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig(OUT, dpi=140, bbox_inches="tight")
print(f"[view] lam={lam}, N nos desenhados={len(draw_nids)}, "
      f"|U_lat|max={ulat.max():.3f} mm, |Uz|max={uoop.max():.3f} mm")
print(f"[view] figura: {OUT}")
