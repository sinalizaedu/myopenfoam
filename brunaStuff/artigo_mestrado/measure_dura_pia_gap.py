#!/usr/bin/env python3
"""Para cada run do sweep on-caso-3 (P_contact 0..18068 Pa), mede a folga
radial entre a dura INNER (r0~2.35 mm) e a pia OUTER (r0~1.55 mm) na MESMA
secao axial do patch de contato (z em [20.9, 24.1] mm, lado +X).

Saidas:
  brunaStuff/dura_pia_gap_summary.txt
  brunaStuff/dura_pia_gap.png   (barras: gap inicial vs deformado, % reduzido)
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CASE = Path("cases/on-caso-3/ccx")
OUT  = Path("brunaStuff")


def _parse_line(L: str, n: int):
    if len(L) < 3 + 10 + 12: return None
    try: nid = int(L[3:13])
    except ValueError: return None
    try: return nid, [float(L[13 + 12*k : 13 + 12*(k + 1)]) for k in range(n)]
    except ValueError: return None


def parse_frd(path: Path):
    nodes = {}; in_n = False
    lines = path.read_text(errors="ignore").splitlines()
    for L in lines:
        s = L.strip()
        if not in_n:
            if s.startswith("2C "): in_n = True
            continue
        if s.startswith("-3"): break
        if L.lstrip().startswith("-1"):
            r = _parse_line(L, 3)
            if r: nodes[r[0]] = tuple(r[1])
    disp_blocks = []; in_d = False; cur = {}
    for L in lines:
        s = L.strip()
        if s.startswith("-4"):
            parts = s.split()
            in_d = (len(parts) >= 2 and parts[1] == "DISP")
            if in_d: cur = {}
            continue
        if not in_d: continue
        if s.startswith("-3"):
            if cur: disp_blocks.append(cur)
            in_d = False; cur = {}
            continue
        if s.startswith("-5"): continue
        if L.lstrip().startswith("-1"):
            r = _parse_line(L, 3)
            if r: cur[r[0]] = tuple(r[1])
    return nodes, (disp_blocks[-1] if disp_blocks else {})


SWEEP = [("Pc0",0),("Pc4517",4517),("Pc9034",9034),
         ("Pc13551",13551),("Pc18068",18068)]

rows = []
for tag, pc in SWEEP:
    f = CASE / f"on-caso-3_{tag}.frd"
    if not f.exists():
        print(f"SKIP {tag}")
        continue
    nodes, disp = parse_frd(f)
    nids = np.array(sorted(nodes.keys()))
    P = np.array([nodes[n] for n in nids])
    U = np.zeros_like(P)
    for i, n in enumerate(nids):
        if n in disp: U[i] = disp[n]
    r0 = np.sqrt(P[:, 0]**2 + P[:, 1]**2)

    mask_z = (P[:, 2] > 20.9e-3) & (P[:, 2] < 24.1e-3)
    md = (np.abs(r0 - 2.35e-3) < 0.05e-3) & mask_z & (P[:, 0] > 2.0e-3)
    if md.sum() == 0:
        md = (r0 > 2.20e-3) & (r0 < 2.45e-3) & mask_z & (P[:, 0] > 2.0e-3)
    mp = (np.abs(r0 - 1.55e-3) < 0.06e-3) & mask_z & (P[:, 0] > 1.0e-3)

    Px = P[:, 0] + U[:, 0]; Py = P[:, 1] + U[:, 1]
    r_def = np.sqrt(Px**2 + Py**2)

    r_dura_min = r_def[md].min() * 1e3
    r_pia_max  = r_def[mp].max() * 1e3
    gap_def    = r_dura_min - r_pia_max
    gap0       = (r0[md].min() - r0[mp].max()) * 1e3
    rows.append((tag, pc, r_dura_min, r_pia_max, gap_def, gap0))

# tabela
lines = []
lines.append(f"{'tag':<8} {'Pc[Pa]':>7} | "
             f"{'dura_in r_min[mm]':>17} {'pia_out r_max[mm]':>17} "
             f"{'gap_def[mm]':>11} {'gap0[mm]':>9} {'reduziu[%]':>10}")
lines.append("-" * 100)
for tag, pc, rd, rp, gd, g0 in rows:
    red = (1 - gd/g0) * 100
    lines.append(f"{tag:<8} {pc:>7} | {rd:>17.4f} {rp:>17.4f} "
                 f"{gd:>11.4f} {g0:>9.4f} {red:>10.1f}")
table = "\n".join(lines)
print(table)
(OUT / "dura_pia_gap_summary.txt").write_text(table + "\n")

# Plot: barras gap_def vs gap0
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
pcs = [r[1] for r in rows]
gaps_def = [r[4] for r in rows]
gaps0 = [r[5] for r in rows]
reductions = [(1 - r[4]/r[5]) * 100 for r in rows]

x = np.arange(len(pcs))
w = 0.36
ax1.bar(x - w/2, gaps0, w, color="lightgray", label="gap inicial (SAS = 0.80 mm)")
ax1.bar(x + w/2, gaps_def, w, color="steelblue", label="gap apos compressao")
ax1.axhline(0, color="red", lw=1.5, ls="--", label="contato dura-pia")
ax1.set_xticks(x)
ax1.set_xticklabels([f"Pc={p}\nPa" for p in pcs])
ax1.set_ylabel("folga radial dura-pia no patch de contato [mm]")
ax1.set_title("(A) Folga local do SAS sob a arteria oftalmica\n"
              "0.8 mm vira ate 0.17 mm em Pc sistolico")
ax1.legend(loc="upper right", fontsize=9)
ax1.grid(alpha=0.3, axis="y")

ax2.bar(x, reductions, color=["#e5f5e0" if r < 30 else "#fdae6b" if r < 70 else "#a63603"
                              for r in reductions])
for i, r in enumerate(reductions):
    ax2.text(i, r + 1.5, f"{r:.0f}%", ha="center", fontsize=11, fontweight="bold")
ax2.axhline(100, color="red", lw=1.5, ls="--", label="100% = encosta")
ax2.set_xticks(x)
ax2.set_xticklabels([f"Pc={p}\nPa" for p in pcs])
ax2.set_ylabel("% de reducao do gap SAS local")
ax2.set_title("(B) % do SAS local esmagado em z=22.5 mm, lado +X")
ax2.set_ylim(-10, 110)
ax2.legend(loc="upper left", fontsize=9)
ax2.grid(alpha=0.3, axis="y")

plt.suptitle("on-caso-3 - SANS + arteria oftalmica: o SAS local nao chega a fechar, "
             "mas em Pc sistolico esta a 0.17 mm do contato dura-pia (~79% esmagado)",
             fontsize=11, y=1.02)
plt.tight_layout()
plt.savefig(OUT / "dura_pia_gap.png", dpi=140, bbox_inches="tight")
print(f"\nplot: {OUT/'dura_pia_gap.png'}")
print(f"table: {OUT/'dura_pia_gap_summary.txt'}")
