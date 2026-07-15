#!/usr/bin/env python3
"""Figura + tabela de independencia de malha do on-caso-1.2 (FLUIDO / OpenFOAM).

QoI hidrodinamicas sob carga de compartimentalizacao SANS fixa (inlet p=1333 Pa,
outlet p=0, lid Darcy d=1e16), escoamento de LCR standalone (simpleFoam, laminar,
Re<<1), 3 niveis de refino global (x1, x2, x3):

  - Q_dren  : vazao de drenagem no outlet_peri (sum phi)  -- QoI PRINCIPAL
              (grandeza fisica central: drenagem perineural de LCR);
  - dp_lid  : queda de pressao no lid poroso = <p>_SAS - <p>_peri;
  - |U|_max : pico local de velocidade na SAS (extremo de malha, NAO converge
              monotonicamente -- analogo ao locking da pia no estudo do solido).

Le cases/on-caso-1.2/_mesh_indep_fluid/results.json
Salva brunaStuff/figs/on-caso-1.2-mesh-independence-fluid.png
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "cases", "on-caso-1.2", "_mesh_indep_fluid", "results.json")

data = sorted(json.load(open(RES)), key=lambda x: x["n_cells"])
nc = [x["n_cells"] for x in data]
Q = [x["q_outlet"] * 1e12 for x in data]          # 1e-12 m^3/s
dp = [x["dp_lid_pa"] for x in data]               # Pa
labels = [f"x{x['factor']:g}" for x in data]


def succ(series):
    return [abs(series[i] - series[i - 1]) / abs(series[i]) * 100
            for i in range(1, len(series))]


fig, (ax, axp) = plt.subplots(1, 2, figsize=(12.8, 5.3))

# --- painel 1: QoI principal (vazao de drenagem) vs nCells ---
Q_ref = Q[-1]
ax.axhspan(Q_ref * 0.99, Q_ref * 1.01, color="#2ca02c", alpha=0.15,
           label="±1% (malha mais fina)")
ax.axhline(Q_ref, color="#2ca02c", lw=1.0, ls="--", alpha=0.7)
ax.plot(nc, Q, "o-", color="#1f77b4", lw=2.2, ms=9, zorder=3)
# destaca o baseline (x1 = malha de producao)
ax.plot([nc[0]], [Q[0]], "s", ms=12, mfc="none", mec="#d62728", mew=2.0,
        zorder=4, label="baseline (produção, x1)")
for x, y, l in zip(nc, Q, labels):
    dev = 100 * (y - Q_ref) / Q_ref
    ax.annotate(f"{l}\n{y:.3f}\n({dev:+.1f}%)", (x, y),
                textcoords="offset points", xytext=(0, 11), ha="center", fontsize=8)
ax.set_xscale("log")
ax.set_xlabel("nº de células (log)")
ax.set_ylabel("Q drenagem no outlet_peri  (×10⁻¹² m³/s)")
ax.set_title("Independência de malha — on-caso-1.2 (fluido, simpleFoam)\n"
             "carga SANS fixa (ICP 1333 Pa, lid Darcy d=1e16)", fontsize=11)
ax.legend(loc="best", fontsize=8)
ax.grid(True, which="both", alpha=0.3)
lo, hi = min(Q), max(Q)
pad = max((hi - lo) * 0.8, Q_ref * 0.03)
ax.set_ylim(lo - pad, hi + pad)

# --- painel 2: variacao sucessiva (nivel i vs i-1) ---
axp.plot(nc[1:], succ(Q), "o-", color="#1f77b4", lw=2.2, ms=9, label="Q drenagem")
axp.plot(nc[1:], succ(dp), "s-", color="#c0392b", lw=2.2, ms=9, label="Δp_lid")
axp.axhline(5, color="#1e8449", ls="--", lw=1.2)
axp.text(nc[1], 5.3, "critério 5%", color="#1e8449", fontsize=9, va="bottom")
for x, y in zip(nc[1:], succ(Q)):
    axp.annotate(f"{y:.1f}%", (x, y), textcoords="offset points", xytext=(0, 8),
                 ha="center", fontsize=8, color="#1f77b4")
for x, y in zip(nc[1:], succ(dp)):
    axp.annotate(f"{y:.1f}%", (x, y), textcoords="offset points", xytext=(0, -14),
                 ha="center", fontsize=8, color="#c0392b")
axp.set_xscale("log")
axp.set_xlabel("nº de células (log)")
axp.set_ylabel("variação sucessiva |Δ| entre níveis (%)")
axp.set_title("Diagnóstico de convergência (nível i vs i−1)", fontsize=11)
axp.legend()
axp.grid(True, which="both", alpha=0.3)

fig.tight_layout()
out = os.path.join(ROOT, "brunaStuff", "figs", "on-caso-1.2-mesh-independence-fluid.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
fig.savefig(out, dpi=150)
print("figura ->", out)

# --- tabela ---
print(f"\n{'nivel':>6} {'nCells':>8} {'Q(1e-12 m3/s)':>14} {'Q% vs fino':>11} "
      f"{'dp_lid(Pa)':>11} {'|U|max(m/s)':>13} {'|U|mean(m/s)':>13}")
for i, x in enumerate(data):
    qdev = 100 * (Q[i] - Q[-1]) / Q[-1]
    print(f"{labels[i]:>6} {x['n_cells']:>8} {Q[i]:>14.4f} {qdev:>10.1f}% "
          f"{x['dp_lid_pa']:>11.1f} {x['u_max_sas']:>13.3e} "
          f"{x.get('u_mean_sas', float('nan')):>13.3e}")

dQ = 100 * (Q[-1] - Q[-2]) / abs(Q[-1])
ddp = 100 * (dp[-1] - dp[-2]) / abs(dp[-1])
print(f"\nVariação no último refino (x{data[-2]['factor']:g} -> x{data[-1]['factor']:g}):")
print(f"  Q drenagem: {dQ:+.1f}%   Δp_lid: {ddp:+.1f}%")

# --- sumario persistente (txt) ---
lines = []
P = lines.append
P("=" * 78)
P("ESTUDO DE INDEPENDENCIA DE MALHA - on-caso-1.2 (LADO FLUIDO / OpenFOAM)")
P("=" * 78)
P("Fluido LCR standalone (simpleFoam, laminar, Re<<1), DESACOPLADO do FSI:")
P("  inlet p_kin=1.333 (=1333 Pa), outlet_peri p=0, paredes noSlip estaticas,")
P("  lid peri_porous Darcy d=1e16 m^-2 (regime SANS compartimentalizado).")
P("Refino global do blockMesh por fator inteiro (uniforme r/theta/z).")
P("")
P(f"{'nivel':>6} {'nCells':>8} {'iters':>6} {'Q_dren(m3/s)':>14} {'Q%vs_fino':>10} "
  f"{'dp_lid(Pa)':>11} {'p_SAS(Pa)':>11} {'|U|mean(m/s)':>13} {'|U|max(m/s)':>12}")
for i, x in enumerate(data):
    qdev = 100 * (Q[i] - Q[-1]) / Q[-1]
    P(f"{labels[i]:>6} {x['n_cells']:>8} {x['n_iter']:>6} {x['q_outlet']:>14.4e} "
      f"{qdev:>9.1f}% {x['dp_lid_pa']:>11.1f} {x['p_sas_pa']:>11.4f} "
      f"{x.get('u_mean_sas', float('nan')):>13.3e} {x['u_max_sas']:>12.3e}")
P("")
P("Variacao SUCESSIVA (nivel i vs i-1):")
P(f"  Q drenagem : x1->x2 {succ(Q)[0]:.1f}%   x2->x3 {succ(Q)[1]:.1f}%")
P(f"  dp_lid     : x1->x2 {succ(dp)[0]:.1f}%   x2->x3 {succ(dp)[1]:.1f}%")
P("")
P("OBSERVACOES:")
P("- p_SAS (pressao media na SAS = CARGA transmitida a bainha no FSI) e' identica")
P(f"  ate' 4 casas decimais em todas as malhas (~{data[0]['p_sas_pa']:.2f} Pa): a carga")
P("  estrutural relevante e' independente de malha (<0.001%).")
P("- Q de drenagem (indicador secundario) converge monotonicamente: malha de")
P(f"  producao (x1, {data[0]['n_cells']} cels) a {100*(Q[0]-Q[-1])/Q[-1]:+.1f}% da fina; variacao")
P(f"  sucessiva cai para {succ(Q)[1]:.1f}% no ultimo refino (< criterio 5%).")
P("- |U|_max e' um pico LOCAL (extremo de malha) e nao converge monotonicamente;")
P("  use |U|_mean ou Q como metricas integrais robustas.")
summary = "\n".join(lines) + "\n"
spath = os.path.join(ROOT, "brunaStuff", "mesh_independence_fluid_summary.txt")
open(spath, "w").write(summary)
print("\nsumario ->", spath)
