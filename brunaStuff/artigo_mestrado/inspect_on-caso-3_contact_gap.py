#!/usr/bin/env python3
"""
Inspecao fisica extra sobre o sweep de P_contact em on-caso-3:

  1) Gap radial DURA_INTERNA - PIA_EXTERNA no patch de contato (z~22.5, +X)
     -> Verifica se em algum Pc a dura "encosta" na pia (gap = 0).
  2) Planificacao do globo (Dz e protrusao da lamina cribrosa)
     -> SANS classico: 'posterior globe flattening' + 'optic disc edema'.
  3) Padrao axial do kink (U_lat ao longo do eixo +X em r~1.55, pia outer)
     -> Identifica modo de flambagem (1 lobulo, 2 lobulos, etc.).

Saidas:
  brunaStuff/on-caso-3_inspect_gap_globe.png  (3 paineis)
  print no stdout com tabela
"""
import re
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CASE = Path("cases/on-caso-3/ccx")
OUT = Path("brunaStuff")

SWEEP = [
    ("Pc0",         0),
    ("Pc4517",   4517),
    ("Pc9034",   9034),
    ("Pc13551", 13551),
    ("Pc18068", 18068),
]
COLORS = plt.cm.plasma(np.linspace(0.05, 0.85, len(SWEEP)))

R_DURA_OUT = 2.50e-3
R_DURA_IN  = 2.35e-3
R_PIA_OUT  = 1.55e-3
R_PIA_IN   = 1.45e-3
TOL_R = 0.06e-3
Z_CONT_MIN, Z_CONT_MAX = 20.9e-3, 24.1e-3
INITIAL_GAP_DURA_PIA = R_DURA_IN - R_PIA_OUT     # 0.80 mm


def _parse_data_line(L, n_floats):
    if len(L) < 3 + 10 + 12: return None
    try: nid = int(L[3:13])
    except ValueError: return None
    vals = []
    for k in range(n_floats):
        s = L[13 + 12*k : 13 + 12*(k+1)]
        if not s: return None
        try: vals.append(float(s))
        except ValueError: return None
    return nid, vals


def parse_frd(path):
    """Retorna (nodes_dict {nid:(x,y,z)}, last_disp {nid:(ux,uy,uz)})."""
    nodes = {}
    text = path.read_text(errors="ignore")
    lines = text.splitlines()
    in_nodes = False
    for L in lines:
        s = L.strip()
        if not in_nodes:
            if s.startswith("2C ") or s == "2C": in_nodes = True
            continue
        if s.startswith("-3"): in_nodes = False; break
        if L.lstrip().startswith("-1"):
            r = _parse_data_line(L, 3)
            if r: nodes[r[0]] = tuple(r[1])
    disp_blocks, in_disp, cur = [], False, {}
    for L in lines:
        s = L.strip()
        if s.startswith("-4"):
            p = s.split(); v = p[1] if len(p) >= 2 else ""
            in_disp = (v == "DISP")
            if in_disp: cur = {}
            continue
        if not in_disp: continue
        if s.startswith("-3"):
            if cur: disp_blocks.append(cur)
            in_disp = False; cur = {}; continue
        if s.startswith("-5"): continue
        if L.lstrip().startswith("-1"):
            r = _parse_data_line(L, 3)
            if r: cur[r[0]] = tuple(r[1])
    # Filtra blocos com |U| absurdo (pos-divergencia do Riks)
    MAX_U = 0.1  # 100 mm
    for blk in reversed(disp_blocks):
        umax = max((max(abs(v) for v in u) for u in blk.values()), default=0)
        if umax < MAX_U:
            return nodes, blk
    return nodes, {}


def analyze(tag):
    frd = CASE / f"on-caso-3_{tag}.frd"
    if not frd.exists():
        return None
    nodes, disp = parse_frd(frd)
    nids = np.array(sorted(nodes.keys()))
    P = np.array([nodes[n] for n in nids])
    U = np.zeros_like(P)
    for i, n in enumerate(nids):
        if n in disp: U[i] = disp[n]
    P_def = P + U
    r0  = np.sqrt(P[:, 0]**2 + P[:, 1]**2)
    r_new = np.sqrt(P_def[:, 0]**2 + P_def[:, 1]**2)

    res = {}

    # 1) Gap DURA INNER vs PIA OUTER no patch de contato (lado +X, z~22.5)
    m_dura_in_local = (np.abs(r0 - R_DURA_IN) < TOL_R) & \
                      (P[:, 2] > Z_CONT_MIN) & (P[:, 2] < Z_CONT_MAX) & \
                      (P[:, 0] > 0)
    m_pia_out_local = (np.abs(r0 - R_PIA_OUT) < TOL_R) & \
                      (P[:, 2] > Z_CONT_MIN) & (P[:, 2] < Z_CONT_MAX) & \
                      (P[:, 0] > 0)
    if m_dura_in_local.sum() and m_pia_out_local.sum():
        r_dura_in_min = r_new[m_dura_in_local].min()
        r_pia_out_max = r_new[m_pia_out_local].max()
        res["r_dura_in_min_mm"] = r_dura_in_min * 1e3
        res["r_pia_out_max_mm"] = r_pia_out_max * 1e3
        res["gap_local_mm"] = (r_dura_in_min - r_pia_out_max) * 1e3
        res["gap_initial_mm"] = INITIAL_GAP_DURA_PIA * 1e3
        res["gap_close_pct"] = 100.0 * (1.0 - res["gap_local_mm"]
                                              / res["gap_initial_mm"])
    else:
        res["gap_local_mm"] = np.nan
        res["gap_close_pct"] = np.nan

    # 2) Planificacao do globo: media Uz nos nos da globo anterior z>=30.8
    m_globe = P[:, 2] >= 30.6e-3
    if m_globe.sum():
        res["uz_globe_mean_mm"] = U[m_globe, 2].mean() * 1e3
        # Globo lateral (z=30.3-30.8, esclera) protrusao radial
        m_eq = (P[:, 2] > 30.3e-3) & (P[:, 2] < 30.8e-3)
        if m_eq.sum():
            r_eq = np.sqrt(P_def[m_eq, 0]**2 + P_def[m_eq, 1]**2)
            r_eq_0 = np.sqrt(P[m_eq, 0]**2 + P[m_eq, 1]**2)
            res["globe_equator_dr_mm"] = (r_eq.max() - r_eq_0.max()) * 1e3

    # 3) Padrao axial do kink na pia outer (r~1.55) ao longo de z
    m_pia_out = np.abs(r0 - R_PIA_OUT) < TOL_R
    z_pia = P[m_pia_out, 2]
    Ulat_pia = np.sqrt(U[m_pia_out, 0]**2 + U[m_pia_out, 1]**2)
    # bin por z (cells centradas em 1.5, 4.5, ..., 28.5 mm)
    z_bins = np.linspace(0, 30e-3, 11)
    z_centers = 0.5 * (z_bins[1:] + z_bins[:-1])
    Ulat_z = np.zeros_like(z_centers)
    for k in range(len(z_centers)):
        mz = (z_pia >= z_bins[k]) & (z_pia < z_bins[k+1])
        if mz.sum():
            Ulat_z[k] = Ulat_pia[mz].max()
    res["z_centers_mm"] = z_centers * 1e3
    res["Ulat_pia_axial_mm"] = Ulat_z * 1e3
    return res


runs = []
for tag, pc in SWEEP:
    r = analyze(tag)
    if r is None:
        print(f"[SKIP] {tag}: sem .frd"); continue
    r["tag"] = tag; r["pc"] = pc
    runs.append(r)
    print(f"{tag:8s} Pc={pc:6d} Pa  "
          f"gap_dura-pia={r['gap_local_mm']:.4f} mm  "
          f"({r['gap_close_pct']:5.1f}% fechado)  "
          f"Uz_globe={r.get('uz_globe_mean_mm', 0):.3f} mm  "
          f"protrusao_eq={r.get('globe_equator_dr_mm', 0):.4f} mm")

# Plot
fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
fig.suptitle("on-caso-3 - Inspecao fisica do sweep P_contact "
             "(Caso 2 + P_contact: Winkler k=200 kPa/m baseline, Dz=-1.5 mm)",
             fontsize=11)

# Painel 1: gap dura-pia no contato vs Pc
ax = axes[0]
pcs   = [r["pc"] for r in runs]
gaps  = [r["gap_local_mm"] for r in runs]
g0    = INITIAL_GAP_DURA_PIA * 1e3
ax.plot(pcs, gaps, "o-", lw=2, markersize=12, color="darkred",
        label="gap simulado (dura_in min vs pia_out max no contato)")
ax.axhline(g0, color="gray", ls="--", lw=1.5,
           label=f"gap inicial ({g0:.2f} mm)")
ax.axhline(0, color="red", ls=":", lw=1.5, label="contato (gap=0)")
ax.set_xlabel("P_contact [Pa]")
ax.set_ylabel("Gap radial dura_interna - pia_externa [mm]")
ax.set_title("(1) Encosto dura -> pia no patch de contato\n"
             "(o quanto a dura afunda em direcao ao nervo)", fontsize=10)
ax.legend(loc="best", fontsize=9)
ax.grid(alpha=0.3)
for p, g in zip(pcs, gaps):
    pct = 100 * (1 - g / g0)
    ax.annotate(f"{pct:.0f}%\nfechado", (p, g), xytext=(6, 8),
                textcoords="offset points", fontsize=8)

# Painel 2: planificacao do globo (Uz_globe) + protrusao equador
ax = axes[1]
uz_glob = [r.get("uz_globe_mean_mm", 0) for r in runs]
dr_eq   = [r.get("globe_equator_dr_mm", 0) for r in runs]
ax2 = ax.twinx()
l1 = ax.plot(pcs, uz_glob, "o-", lw=2, markersize=12, color="navy",
             label="Uz medio do globo posterior (Dz prescrito = -1.5)")
l2 = ax2.plot(pcs, dr_eq, "s-", lw=2, markersize=10, color="orange",
              label="dR no equador (protrusao lateral)")
ax.set_xlabel("P_contact [Pa]")
ax.set_ylabel("Uz globo posterior [mm] (Dz)", color="navy")
ax2.set_ylabel("dR equador globo [mm] (protrusao)", color="orange")
ax.tick_params(axis='y', labelcolor='navy')
ax2.tick_params(axis='y', labelcolor='orange')
ax.set_title("(2) Marcadores SANS classicos\n"
             "Uz~planificacao posterior, dR_eq~choroidal stretching",
             fontsize=10)
ax.grid(alpha=0.3)
lns = l1 + l2
ax.legend(lns, [l.get_label() for l in lns], loc="best", fontsize=8)

# Painel 3: kink axial da pia outer ao longo de z, sobreposto por Pc
ax = axes[2]
for i, r in enumerate(runs):
    z = r["z_centers_mm"]
    u = r["Ulat_pia_axial_mm"]
    ax.plot(z, u, "o-", color=COLORS[i], lw=2, markersize=6,
            label=f"Pc={r['pc']} Pa")
ax.axvline(22.5, color="gray", ls="--", lw=1.5, alpha=0.7,
           label="z patch de contato (22.5 mm)")
ax.axvline(15.0, color="gray", ls=":", lw=1.5, alpha=0.7,
           label="z perturbacao (15 mm)")
ax.set_xlabel("z [mm] (do canal otico ate o globo)")
ax.set_ylabel("|U_lat| max na pia outer (r=1.55 mm) [mm]")
ax.set_title("(3) Padrao axial do kink no nervo\n"
             "1 lobulo central = modo 1 (Euler); 2 lobulos = modo 2",
             fontsize=10)
ax.legend(loc="best", fontsize=8)
ax.grid(alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.94])
out_png = OUT / "on-caso-3_inspect_gap_globe.png"
plt.savefig(out_png, dpi=140, bbox_inches="tight")
print(f"\nFigura salva: {out_png}")
