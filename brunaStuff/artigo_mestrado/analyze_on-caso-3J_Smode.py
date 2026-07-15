#!/usr/bin/env python3
"""
analyze_on-caso-3J_Smode.py
===========================
O Caso 3J ja' PARTE de um arco em "J" (modo n=1). Pergunta: sob a compressao
axial + carga arterial, a linha de centro do nervo desenvolve uma ONDULACAO
ANTISSIMETRICA em "S" (inversao de sinal da deflexao ao longo do eixo, modo
n>=2) ou apenas AMPLIFICA o arco unico (sem inversao)?

Metodo:
  1) le os nos de REFERENCIA (malha varrida em J) e o U do ultimo passo (.frd);
  2) para cada no do nervo ('on'), acha a estacao de arco s* = argmin|XY-C(s)|
     na linha de centro analitica C(s) (mesma do warp);
  3) constroi a linha de centro DEFORMADA media por bin de s;
  4) mede a deflexao da linha deformada em relacao a CORDA reta que liga suas
     extremidades (globo <-> engaste) -> deflexao residual d(s);
  5) "S" <=> d(s) troca de sinal (duas meias-ondas). Arco unico <=> sinal unico.
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
OUT = HERE / "on-caso-3J_Smode.png"

# parametros do warp em J (iguais ao Allrun)
THETA0 = np.radians(-90.0)
TURN = np.radians(-53.130102)


def centerline(s, L, R, th0):
    kappa = (TURN) / L
    th = th0 + kappa * s
    cx = (np.sin(th) - np.sin(th0)) * R
    cy = (np.cos(th0) - np.cos(th)) * R
    return np.stack([cx, cy], axis=-1)


nodes, elems = parse_inp(MESH)
ref = {nid: np.array(xyz) for nid, xyz in nodes.items()}
on_nids = sorted({n for (_e, conn, z) in elems if z == "ON" for n in conn})

R3 = np.array([ref[n] for n in on_nids])           # (N,3)
zmax = max(v[2] for v in ref.values())             # nao usado direto; L vem do arco
# L (comprimento de arco) = zmax original; recupera via |R|=L/|turn|, mas usamos
# o mesmo criterio do warp: L = zmax_ref. Aqui zmax_ref foi 0.0308 m.
L = 0.0308
kappa = TURN / L
Rcurv = 1.0 / kappa

# estacao de arco s* por no ('on'): argmin |XY - C(s)|
s_grid = np.linspace(0.0, L, 800)
C_grid = centerline(s_grid, L, Rcurv, THETA0)      # (800,2)
XY = R3[:, :2]
# distancia de cada no a cada ponto do grid
d2 = ((XY[:, None, :] - C_grid[None, :, :]) ** 2).sum(-1)   # (N,800)
s_star = s_grid[d2.argmin(1)]                       # (N,)

# deslocamento do ultimo passo
_, _n2zone, steps = parse_frd(FRD)
steps = [s for s in steps if s.get("disp")]
last = max(steps, key=lambda d: (d["lam"] if d["lam"] is not None else 0.0))
lam = last["lam"]
disp = last["disp"]
U = np.array([disp.get(n, (0.0, 0.0, 0.0)) for n in on_nids])
DEF = R3 + U

# linha de centro DEFORMADA media por bin de s
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

# deflexao residual em relacao a CORDA reta (extremidades da linha deformada)
chord0, chord1 = cl_def[0], cl_def[-1]
axis = chord1 - chord0
axis /= np.linalg.norm(axis)
rel = cl_def - chord0
along = rel @ axis
perp_vec = rel - np.outer(along, axis)            # componente perpendicular (3D)
perp_mag = np.linalg.norm(perp_vec, axis=1)
# sinal: projeta no eixo lateral principal (1a componente PCA do perp em XY)
lat_dir = perp_vec[:, :2]
nz = np.linalg.norm(lat_dir, axis=1) > 0
principal = lat_dir[np.argmax(perp_mag)] / (np.linalg.norm(lat_dir[np.argmax(perp_mag)]) + 1e-30)
signed = (perp_vec[:, :2] @ principal)            # mm depois
signed_mm = signed * 1e3

# deteccao de "S": troca de sinal significativa
thr = 0.02e-3  # 0.02 mm de tolerancia
sig = signed.copy()
sig[np.abs(sig) < thr] = 0.0
nz_signs = np.sign(sig[sig != 0.0])
n_sign_changes = int((np.diff(nz_signs) != 0).sum()) if nz_signs.size > 1 else 0
is_S = n_sign_changes >= 1

# tambem reporta excursao fora do plano
uoop = np.abs(U[:, 2]).max() * 1e3

# -------- plot --------
fig, axes = plt.subplots(1, 2, figsize=(12, 6))
verdict = "ONDULACAO EM 'S' (antissimetrica, n>=2)" if is_S else "ARCO UNICO (n=1, sem 'S')"
fig.suptitle(f"Caso 3J | lambda={lam:.3f} | veredito: {verdict}", fontsize=12)

ax = axes[0]
ax.plot(cl_ref[:, 0] * 1e3, cl_ref[:, 1] * 1e3, "o-", color="0.7", label="centro REF (J)")
ax.plot(cl_def[:, 0] * 1e3, cl_def[:, 1] * 1e3, "o-", color="C0", label="centro DEFORMADO")
ax.plot([chord0[0] * 1e3, chord1[0] * 1e3], [chord0[1] * 1e3, chord1[1] * 1e3],
        "r--", lw=1, label="corda (extremidades)")
ax.scatter([0], [0], marker="*", s=160, c="red", zorder=5, label="globo")
ax.set_aspect("equal"); ax.grid(alpha=0.3); ax.legend(fontsize=8)
ax.set_xlabel("X [mm]"); ax.set_ylabel("Y [mm]")
ax.set_title("(A) Linha de centro do nervo no plano do J")

ax = axes[1]
ax.axhline(0, color="k", lw=0.8)
ax.plot(sb * 1e3, signed_mm, "o-", color="C3")
ax.fill_between(sb * 1e3, signed_mm, 0, alpha=0.2, color="C3")
ax.set_xlabel("s [mm] (arco a partir do globo)")
ax.set_ylabel("deflexao residual vs corda [mm]")
ax.set_title(f"(B) {n_sign_changes} troca(s) de sinal -> "
             f"{'S' if is_S else 'arco unico'}")
ax.grid(alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(OUT, dpi=140, bbox_inches="tight")
print(f"[Smode] lam={lam}")
print(f"[Smode] trocas de sinal da deflexao = {n_sign_changes}  -> "
      f"{'S (antissimetrico)' if is_S else 'arco unico (n=1)'}")
print(f"[Smode] deflexao residual max = {np.abs(signed_mm).max():.3f} mm")
print(f"[Smode] |Uz| max (fora do plano, lado arteria) = {uoop:.3f} mm")
print(f"[Smode] figura: {OUT}")
