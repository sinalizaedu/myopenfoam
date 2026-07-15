#!/usr/bin/env python3
"""Figura compacta do Caso 3F com rampa Dz = -1.0 mm.
(A) curvas F_z(Dz) sobrepostas (todas limpas ate lambda=1.0)
(B) kink_dura e fechamento do SAS vs P_contact, com marcadores de
    independencia de malha em Pc9034 (radpia2/3/4).
"""
import importlib.util
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
OFF = REPO / "cases/_mi/on-caso-3__radpia2dura3/ccx"

src = (HERE / "analyze_on-caso-3_pcontact_sweep.py").read_text()
ns: dict = {}
exec(compile(src[:src.index("# 3) loop pelos runs")], "f", "exec"), ns)  # noqa: S102
parse_dat = ns["parse_dat"]

SWEEP = [("Pc0", 0, "0 Pa"), ("Pc4517", 4517, "4.5 kPa"),
         ("Pc9034", 9034, "9.0 kPa (baseline)"), ("Pc13551", 13551, "13.6 kPa"),
         ("Pc18068", 18068, "18.1 kPa (sistolico)")]
COLORS = plt.cm.plasma(np.linspace(0.05, 0.85, len(SWEEP)))

data = json.loads((HERE / "caso_3f_dz1.json").read_text())
sweep = data["sweep"]
mi = data["mesh_indep"]

fig, (axA, axB) = plt.subplots(1, 2, figsize=(12.5, 4.8))

# (A) F-Dz
for i, (tag, pc, lab) in enumerate(SWEEP):
    p = OFF / f"on-caso-3_{tag}.dat"
    if not p.exists():
        continue
    t, Dz, Fd, Fp, Fo, Fg = parse_dat(p)
    Feng = -(Fd + Fp + Fo) * 1e3
    axA.plot(np.abs(Dz) * 1e3, np.abs(Feng), "o-", color=COLORS[i],
             label=lab, lw=1.8, ms=3)
axA.set_xlabel(r"$|\Delta z|$ do globo [mm]")
axA.set_ylabel(r"$|F_z|$ no engaste posterior [mN]")
axA.set_title(u"(A) Curva $F_z(\\Delta z)$ — rampa $\\Delta z=-1.0$ mm\n"
              u"todas as cargas atingem $\\lambda=1.0$ (sem ponto-limite)")
axA.legend(fontsize=8, loc="upper left")
axA.grid(alpha=0.3)

# (B) kink_dura + gap reduction vs Pc
pcs = np.array([r["pc"] for r in sweep])
kink = np.array([r.get("dura", 0) * 1e3 for r in sweep])
gapr = np.array([r.get("gap_reduc_pct", 0) for r in sweep])
axB.plot(pcs / 1e3, kink, "o-", color="firebrick", lw=2, ms=8,
         label=u"kink lateral da dura")
# marcadores de independencia de malha em Pc9034
mk = {"radpia2dura3": ("D", "k"), "radpia3dura4": ("s", "navy"),
      "radpia4dura5": ("^", "teal")}
for r in mi:
    m, c = mk.get(r["mesh"], ("x", "gray"))
    axB.plot(9.034, r.get("dura", 0) * 1e3, m, color=c, ms=9, mfc="none",
             mew=1.8, label=f"malha {r['mesh']}")
axB.set_xlabel(r"$p_c$ da arteria oftalmica [kPa]")
axB.set_ylabel(u"kink lateral da dura [mm]", color="firebrick")
axB.tick_params(axis="y", labelcolor="firebrick")
axB.grid(alpha=0.3)

axB2 = axB.twinx()
axB2.plot(pcs / 1e3, gapr, "s--", color="steelblue", lw=1.6, ms=6,
          label=u"fechamento do SAS")
axB2.set_ylabel(u"fechamento do SAS local [%]", color="steelblue")
axB2.tick_params(axis="y", labelcolor="steelblue")
axB2.set_ylim(-5, 105)
axB.set_title(u"(B) Resposta monotonica vs $p_c$\n"
              u"kink da dura (independente de malha em $p_c=9$ kPa) e fechamento do SAS")
h1, l1 = axB.get_legend_handles_labels()
axB.legend(h1, l1, fontsize=7.5, loc="upper left")

plt.tight_layout()
out = REPO / "brunaStuff/figs/on-caso-3f-dz1.png"
plt.savefig(out, dpi=140, bbox_inches="tight")
print("salvo:", out)
