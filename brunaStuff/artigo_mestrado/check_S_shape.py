#!/usr/bin/env python3
"""Mede objetivamente se o nervo flambou em "S".

Le o ultimo campo de deslocamento (.frd) e extrai o deslocamento lateral U_x
ao longo do EIXO do nervo (nos do nucleo 'on', r ~ 0) em funcao de z. Um arco
unico (modo 1) mantem U_x do mesmo sinal; um "S" (modo 2) TROCA de sinal.

Compara 3 runs na malha radpia2dura3 (Dz=-1.0 mm, PIC, Winkler intactos):
  - on-caso-3_Pc18068  (baseline da figura: arteria empurra so' de um lado)
  - on-caso-3_Sfix     (variante: apoio lateral no meio)
  - on-caso-3_Sdip     (variante: dois empurroes opostos)

Saida: brunaStuff/check_S_shape.png  + tabela no stdout.
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
REPO = HERE.parent

# reaproveita parse_frd_last_disp do analisador de producao
src = (HERE / "analyze_on-caso-3_pcontact_sweep.py").read_text()
cut = src.index("# 3) loop pelos runs")
ns: dict = {}
exec(compile(src[:cut], "pcontact_funcs", "exec"), ns)  # noqa: S102
parse_frd_last_disp = ns["parse_frd_last_disp"]

CCX = REPO / "cases/_mi/on-caso-3__radpia2dura3/ccx"
RUNS = [
    ("baseline (Pc18068)", CCX / "on-caso-3_Pc18068.frd", "tab:gray"),
    ("Sfix (trava o meio)", CCX / "on-caso-3_Sfix.frd", "tab:blue"),
    ("Sdip (dipolo oposto)", CCX / "on-caso-3_Sdip.frd", "tab:red"),
    ("Shold (arteria segura)", CCX / "on-caso-3_Shold.frd", "tab:green"),
    ("S2ao (AO 2 lados opostos)", CCX / "on-caso-3_S2ao.frd", "tab:purple"),
    ("Sseed (tortuosidade + AO 22.5)", CCX / "on-caso-3_Sseed.frd", "tab:orange"),
]

R_AXIS = 0.4e-3   # nucleo do nervo: nos com r < 0.4 mm = "eixo"
NBINS = 24


def centerline_ux(frd: Path):
    """Retorna (z_bin_mm, Ux_mean_mm) ao longo do eixo do nervo."""
    nodes, disp = parse_frd_last_disp(frd)
    if not nodes or not disp:
        return None
    nids = np.array(sorted(nodes.keys()))
    P = np.array([nodes[n] for n in nids])
    U = np.array([disp.get(n, (0.0, 0.0, 0.0)) for n in nids])
    r0 = np.hypot(P[:, 0], P[:, 1])
    axis = (r0 < R_AXIS) & (P[:, 2] < 30.0e-3)   # so' o trecho do nervo (z<30)
    if axis.sum() < 5:
        return None
    z = P[axis, 2] * 1e3
    # POSICAO lateral deformada = coord_x (inclui eventual semente) + U_x.
    # CCX reporta U relativo a' malha inicial; se a malha ja' parte ondulada
    # (Sseed), e' preciso somar a coordenada para obter a forma real do eixo.
    ux = (P[axis, 0] + U[axis, 0]) * 1e3
    order = np.argsort(z)
    z, ux = z[order], ux[order]
    edges = np.linspace(z.min(), z.max(), NBINS + 1)
    idx = np.clip(np.digitize(z, edges) - 1, 0, NBINS - 1)
    zc, uc = [], []
    for b in range(NBINS):
        m = idx == b
        if m.any():
            zc.append(0.5 * (edges[b] + edges[b + 1]))
            uc.append(ux[m].mean())
    return np.array(zc), np.array(uc)


fig, ax = plt.subplots(figsize=(8, 5))
print(f"{'run':<22} {'Ux_max[mm]':>11} {'Ux_min[mm]':>11} {'troca sinal?':>13} {'=> forma'}")
print("-" * 78)
for label, frd, color in RUNS:
    if not frd.exists():
        print(f"{label:<22} {'(frd ausente)':>11}")
        continue
    out = centerline_ux(frd)
    if out is None:
        print(f"{label:<22} {'(sem dados)':>11}")
        continue
    zc, uc = out
    umax, umin = uc.max(), uc.min()
    # "S" se ha excursao apreciavel dos dois sinais (ignora ruido < 5 um)
    tol = 5e-3
    is_S = (umax > tol) and (umin < -tol)
    forma = "S (modo 2)" if is_S else "arco (modo 1)"
    print(f"{label:<22} {umax:>11.3f} {umin:>11.3f} {('SIM' if is_S else 'nao'):>13} {'=> ' + forma}")
    ax.plot(zc, uc, "-o", ms=3, color=color, label=label)

ax.axhline(0, color="k", lw=0.8, ls="--")
ax.set_xlabel("z ao longo do nervo (mm)")
ax.set_ylabel(r"deslocamento lateral $U_x$ no eixo (mm)")
ax.set_title("Forma da deformada do eixo do nervo  (troca de sinal = S)")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
out_png = HERE / "check_S_shape.png"
fig.savefig(out_png, dpi=130)
print(f"\nSalvo: {out_png}")
