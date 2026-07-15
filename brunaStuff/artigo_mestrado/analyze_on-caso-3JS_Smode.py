#!/usr/bin/env python3
"""
analyze_on-caso-3JS_Smode.py
============================
O Caso 3JS PARTE de uma geometria em "S" IMPOSTA (offset lateral ~sin(2pi s/L),
troca de sinal em s=L/2). Pergunta: sob a compressao axial + arteria, o complexo
ASSUME e AMPLIFICA esse "S" (a deflexao da linha de centro deformada, medida vs a
corda das extremidades, troca de sinal -> n>=2) -- ao contrario de 2J/3J (arco
unico, n=1)?

Metodo identico ao analyze_on-caso-3J_Smode.py, porem a linha de centro de
referencia e' o "S" (th(s)=th0+A*cos(2pi s/L)) do warp_centerline_S.py.
"""
from pathlib import Path
import math
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from frd_stress import parse_frd
from inp_to_vtk import parse_inp

CCX = HERE.parent / "cases" / "on-caso-3JS" / "ccx"
MESH = CCX / "on-caso-3JS_mesh.inp"
FRD = CCX / "on-caso-3JS.frd"
OUT = HERE / "on-caso-3JS_Smode.png"

THETA0 = -90.0
SWING = 25.0
L = 0.0308


def centerline_grid(theta0_deg, swing_deg, L, ngrid=2000):
    th0 = math.radians(theta0_deg)
    A = math.radians(swing_deg)
    s = np.linspace(0.0, L, ngrid)
    th = th0 + A * np.cos(2.0 * math.pi * s / L)
    tx, ty = np.cos(th), np.sin(th)
    cx = np.concatenate([[0.0], np.cumsum(0.5 * (tx[1:] + tx[:-1]) * np.diff(s))])
    cy = np.concatenate([[0.0], np.cumsum(0.5 * (ty[1:] + ty[:-1]) * np.diff(s))])
    return s, np.stack([cx, cy], axis=-1)


nodes, elems = parse_inp(MESH)
ref = {nid: np.array(xyz) for nid, xyz in nodes.items()}
on_nids = sorted({n for (_e, conn, z) in elems if z == "ON" for n in conn})

R3 = np.array([ref[n] for n in on_nids])

# estacao de arco s* por no ('on'): argmin |XY - C(s)| na curva S de referencia
s_grid, C_grid = centerline_grid(THETA0, SWING, L)
XY = R3[:, :2]
d2 = ((XY[:, None, :] - C_grid[None, :, :]) ** 2).sum(-1)
s_star = s_grid[d2.argmin(1)]

_, _n2zone, steps = parse_frd(FRD)
steps = [s for s in steps if s.get("disp")]
last = max(steps, key=lambda d: (d["lam"] if d["lam"] is not None else 0.0))
lam = last["lam"]
disp = last["disp"]
U = np.array([disp.get(n, (0.0, 0.0, 0.0)) for n in on_nids])
DEF = R3 + U

nbins = 24
edges = np.linspace(0.0, L, nbins + 1)
sb = 0.5 * (edges[:-1] + edges[1:])
cl_ref = np.full((nbins, 3), np.nan)
cl_def = np.full((nbins, 3), np.nan)
for i in range(nbins):
    m = (s_star >= edges[i]) & (s_star < edges[i + 1])
    if m.sum() >= 3:
        cl_ref[i] = R3[m].mean(0)
        cl_def[i] = DEF[m].mean(0)
ok = ~np.isnan(cl_def[:, 0])
sb, cl_ref, cl_def = sb[ok], cl_ref[ok], cl_def[ok]

# deflexao residual da linha de centro (DEFORMADA e REF) vs corda das extremidades
def signed_defl(cl):
    chord0, chord1 = cl[0], cl[-1]
    axis = chord1 - chord0
    axis = axis / np.linalg.norm(axis)
    rel = cl - chord0
    along = rel @ axis
    perp = rel - np.outer(along, axis)
    perp_mag = np.linalg.norm(perp, axis=1)
    principal = perp[np.argmax(perp_mag), :2]
    principal = principal / (np.linalg.norm(principal) + 1e-30)
    return (perp[:, :2] @ principal) * 1e3, perp_mag

signed_mm, _ = signed_defl(cl_def)
signed_ref_mm, _ = signed_defl(cl_ref)

thr = 0.02  # mm
sig = signed_mm.copy()
sig[np.abs(sig) < thr] = 0.0
nz_signs = np.sign(sig[sig != 0.0])
n_sign_changes = int((np.diff(nz_signs) != 0).sum()) if nz_signs.size > 1 else 0
is_S = n_sign_changes >= 1
uoop = np.abs(U[:, 2]).max() * 1e3

fig, axes = plt.subplots(1, 2, figsize=(12, 6))
verdict = "ONDULACAO EM 'S' (antissimetrica, n>=2)" if is_S else "ARCO UNICO (n=1, sem 'S')"
fig.suptitle(f"Caso 3JS (S imposto) | lambda={lam:.3f} | veredito: {verdict}", fontsize=12)

ax = axes[0]
ax.plot(cl_ref[:, 0] * 1e3, cl_ref[:, 1] * 1e3, "o-", color="0.7", label="centro REF (S imposto)")
ax.plot(cl_def[:, 0] * 1e3, cl_def[:, 1] * 1e3, "o-", color="C0", label="centro DEFORMADO")
ax.plot([cl_def[0, 0] * 1e3, cl_def[-1, 0] * 1e3],
        [cl_def[0, 1] * 1e3, cl_def[-1, 1] * 1e3], "r--", lw=1, label="corda (extremidades)")
ax.scatter([0], [0], marker="*", s=160, c="red", zorder=5, label="globo")
ax.set_aspect("equal"); ax.grid(alpha=0.3); ax.legend(fontsize=8)
ax.set_xlabel("X [mm]"); ax.set_ylabel("Y [mm]")
ax.set_title("(A) Linha de centro do nervo no plano do S")

ax = axes[1]
ax.axhline(0, color="k", lw=0.8)
ax.plot(sb * 1e3, signed_ref_mm, "s--", color="0.6", label="REF (S imposto)")
ax.plot(sb * 1e3, signed_mm, "o-", color="C3", label="DEFORMADO")
ax.fill_between(sb * 1e3, signed_mm, 0, alpha=0.2, color="C3")
ax.set_xlabel("s [mm] (arco a partir do globo)")
ax.set_ylabel("deflexao residual vs corda [mm]")
ax.set_title(f"(B) {n_sign_changes} troca(s) de sinal -> {'S' if is_S else 'arco unico'}")
ax.legend(fontsize=8); ax.grid(alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(OUT, dpi=140, bbox_inches="tight")
print(f"[Smode-3JS] lam={lam}")
print(f"[Smode-3JS] trocas de sinal (DEFORMADO) = {n_sign_changes}  -> "
      f"{'S (antissimetrico, n>=2)' if is_S else 'arco unico (n=1)'}")
print(f"[Smode-3JS] deflexao residual max (deformado) = {np.abs(signed_mm).max():.3f} mm")
print(f"[Smode-3JS] deflexao residual max (ref S)      = {np.abs(signed_ref_mm).max():.3f} mm")
print(f"[Smode-3JS] |Uz| max (fora do plano) = {uoop:.3f} mm")
print(f"[Smode-3JS] figura: {OUT}")
