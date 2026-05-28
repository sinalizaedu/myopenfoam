"""TESTE A+B versao TRANSIENTE da bateria 'compartimentalizacao FSI':

Aplica os Testes A (uniformidade de p) e B (|U| residual) a cada snapshot
dos casos transientes:

  - fsi-transiente-2 : 1g, PIC_mean=1333 Pa, com oscilacao cardiaca+respiratoria
  - fsi-transiente-3 : SANS,  PIC_mean=3800 Pa, idem

Hipotese H0 (compartimentalizacao Pascal-uniforme TAMBEM no transiente):
  Como o solver pimpleFoam usa formulacao INCOMPRESSIVEL, a propagacao de
  pressao no LCR e' instantanea (c -> oo). Logo, em CADA tempo t, o campo
  p deve ser quase uniforme = p_inlet(t).

H1 (Pascal quebra em regime dinamico):
  Inertia local (rho*dU/dt) e termo viscoso (mu*Laplacian(U)) podem gerar
  gradientes nao-triviais de p, especialmente quando a aceleracao do
  inlet e' alta (dp_inlet/dt grande).

Metricas vs tempo:
  1) p_avg(t)        : deve seguir p_inlet(t)
  2) p_std(t)/p_avg  : uniformidade relativa  (H0: << 1%)
  3) |U|_max(t)      : esperado oscilar com dp_inlet/dt
  4) Re_max(t)       : esperado <= 1 (Stokes)
  5) ratio |U|/U_Stokes : referencia adimensional

Saidas:
  sans_outputs/diag_testAB_transient_<case>.csv
  sans_outputs/diag_testAB_transient.png  (4 paineis 2x4 mostrando -2 e -3)
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from diag_fsi_compartmentalization_A import (
    parse_scalar_field, parse_vector_field, RHO_LCR,
)

ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = ROOT / "cases"
OUT_DIR = Path(__file__).resolve().parent / "sans_outputs"
OUT_DIR.mkdir(exist_ok=True)

R_INNER_M = 0.00155
R_OUTER_M = 0.00235
L_CHAR_M  = R_OUTER_M - R_INNER_M
NU_LCR    = 1.0e-6
MU_LCR    = NU_LCR * RHO_LCR

# referencia de PIC media para cada caso (Pa)
P_MEAN = {
    "fsi-transiente-2": 1333.0,
    "fsi-transiente-3": 3800.0,
}


def list_time_dirs(fluid_dir: Path) -> list[float]:
    """Lista subdirs numericos > 0 (os snapshots)."""
    times = []
    for d in fluid_dir.iterdir():
        if not d.is_dir():
            continue
        try:
            t = float(d.name)
        except ValueError:
            continue
        if t > 0:
            times.append(t)
    return sorted(times)


def snapshot_stats(p_path: Path, U_path: Path) -> dict:
    """Le p e U de UM snapshot, devolve estatisticas Pascal/Stokes."""
    p_kin = parse_scalar_field(p_path.read_text())
    U     = parse_vector_field(U_path.read_text())
    p_Pa  = p_kin * RHO_LCR
    Umag  = np.linalg.norm(U, axis=1)

    p_avg = float(p_Pa.mean())
    p_std = float(p_Pa.std())
    p_max = float(p_Pa.max())
    p_min = float(p_Pa.min())
    span_rel = (p_max - p_min) / abs(p_avg) if abs(p_avg) > 0 else float("inf")

    Umag_max = float(Umag.max())
    Umag_avg = float(Umag.mean())
    Re_max   = Umag_max * L_CHAR_M / NU_LCR
    return {
        "p_avg": p_avg, "p_std": p_std, "p_min": p_min, "p_max": p_max,
        "span_rel_pct": span_rel * 100.0,
        "Umag_max": Umag_max, "Umag_avg": Umag_avg,
        "Re_max": Re_max,
    }


def analyze_case(case_name: str) -> dict:
    fluid_dir = CASES_DIR / case_name / "fluid"
    times = list_time_dirs(fluid_dir)
    print(f"\n  {case_name}: {len(times)} snapshots (t={times[0]:.2f}..{times[-1]:.2f})")
    rows = []
    for t in times:
        td = fluid_dir / (f"{t:g}")
        p_path = td / "p"
        U_path = td / "U"
        if not (p_path.exists() and U_path.exists()):
            continue
        try:
            stats = snapshot_stats(p_path, U_path)
        except Exception as e:
            print(f"    [SKIP] t={t}: {e}")
            continue
        stats["t"] = t
        rows.append(stats)
    return {"case": case_name, "rows": rows}


def print_summary(res: dict):
    rows = res["rows"]
    t = np.array([r["t"] for r in rows])
    p_avg = np.array([r["p_avg"] for r in rows])
    span = np.array([r["span_rel_pct"] for r in rows])
    Umax = np.array([r["Umag_max"] for r in rows])
    Re = np.array([r["Re_max"] for r in rows])
    p_ref = P_MEAN.get(res["case"], np.nan)

    print(f"\n  ==== {res['case']} ====")
    print(f"  p_avg range      : {p_avg.min():.2f} .. {p_avg.max():.2f} Pa")
    print(f"  p_avg mean       : {p_avg.mean():.2f} Pa  (vs PIC_mean {p_ref})")
    print(f"  span_rel max     : {span.max():.4f} %   ({'OK' if span.max() < 1 else 'NON-UNIFORM'})")
    print(f"  span_rel mean    : {span.mean():.4f} %")
    print(f"  |U|_max range    : {Umax.min():.3e} .. {Umax.max():.3e} m/s")
    print(f"  Re_max range     : {Re.min():.3e} .. {Re.max():.3e}")

    if span.max() < 0.1:
        verdict = "PASCAL UNIFORME PRESERVADO no regime transiente"
    elif span.max() < 1.0:
        verdict = "PASCAL APROXIMADO (uniformidade < 1% em todos os snapshots)"
    else:
        verdict = "PASCAL QUEBRADO em algum snapshot (gradientes >1%)"
    print(f"  >>> VEREDITO: {verdict}")


def plot_combined(results: list[dict], outpath: Path):
    fig, axes = plt.subplots(2, 4, figsize=(18, 8))
    for irow, res in enumerate(results):
        rows = res["rows"]
        t = np.array([r["t"] for r in rows])
        p_avg = np.array([r["p_avg"] for r in rows])
        span = np.array([r["span_rel_pct"] for r in rows])
        Umax = np.array([r["Umag_max"] for r in rows])
        Re = np.array([r["Re_max"] for r in rows])
        p_ref = P_MEAN.get(res["case"], np.nan)

        # (a) p_avg(t) - deve seguir o inlet
        ax = axes[irow, 0]
        ax.plot(t, p_avg, marker=".", color="#2980b9", lw=1.2)
        ax.axhline(p_ref, color="red", ls="--", lw=1.0, label=f"PIC_mean={p_ref}")
        ax.set_xlabel("t [s]"); ax.set_ylabel("p_avg [Pa]")
        ax.set_title(f"{res['case']} - p_avg(t)")
        ax.legend(fontsize=8); ax.grid(alpha=0.3)

        # (b) span relativo - uniformidade
        ax = axes[irow, 1]
        ax.plot(t, span, marker=".", color="#27ae60", lw=1.2)
        ax.axhline(1.0, color="red", ls="--", lw=1.0, label="1% threshold")
        ax.axhline(0.01, color="orange", ls=":", lw=1.0, label="0.01% threshold (estatico)")
        ax.set_yscale("log")
        ax.set_xlabel("t [s]"); ax.set_ylabel("(p_max-p_min)/p_avg [%]")
        ax.set_title(f"{res['case']} - uniformidade de p")
        ax.legend(fontsize=8); ax.grid(alpha=0.3, which="both")

        # (c) |U|_max(t)
        ax = axes[irow, 2]
        ax.plot(t, Umax, marker=".", color="#e67e22", lw=1.2)
        ax.set_xlabel("t [s]"); ax.set_ylabel("|U|_max [m/s]")
        ax.set_title(f"{res['case']} - velocidade pico")
        ax.grid(alpha=0.3)

        # (d) Re_max(t)
        ax = axes[irow, 3]
        ax.plot(t, Re, marker=".", color="#c0392b", lw=1.2)
        ax.axhline(1.0, color="red", ls="--", lw=1.0, label="Re=1 (Stokes limit)")
        ax.set_yscale("log")
        ax.set_xlabel("t [s]"); ax.set_ylabel("Re_max = |U|_max * L/nu")
        ax.set_title(f"{res['case']} - Reynolds local")
        ax.legend(fontsize=8); ax.grid(alpha=0.3, which="both")

    fig.suptitle("Testes A+B TRANSIENTES - compartimentalizacao do LCR sob oscilacao cardiaca+respiratoria",
                  fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(outpath, dpi=140)
    plt.close(fig)
    print(f"\n  figura: {outpath}")


def write_csv(res: dict):
    case = res["case"]
    path = OUT_DIR / f"diag_testAB_transient_{case}.csv"
    with open(path, "w") as f:
        f.write("t,p_avg_Pa,p_std_Pa,p_min_Pa,p_max_Pa,span_rel_pct,Umag_max_m_s,Umag_avg_m_s,Re_max\n")
        for r in res["rows"]:
            f.write(f"{r['t']:.4f},{r['p_avg']:.6f},{r['p_std']:.6e},"
                    f"{r['p_min']:.6f},{r['p_max']:.6f},{r['span_rel_pct']:.6e},"
                    f"{r['Umag_max']:.6e},{r['Umag_avg']:.6e},{r['Re_max']:.6e}\n")
    print(f"  CSV: {path}")


def main():
    cases = ["fsi-transiente-2", "fsi-transiente-3"]
    results = []
    for c in cases:
        if not (CASES_DIR / c).exists():
            print(f"  [SKIP] {c}: caso nao encontrado")
            continue
        res = analyze_case(c)
        results.append(res)
        print_summary(res)
        write_csv(res)

    if results:
        plot_combined(results, OUT_DIR / "diag_testAB_transient.png")


if __name__ == "__main__":
    main()
