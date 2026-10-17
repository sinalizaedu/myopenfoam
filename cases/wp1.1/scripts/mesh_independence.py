#!/usr/bin/env python3
"""Formal mesh-independence study for wp1.1 (CalculiX S8 sphere).

QoI: K = ΔP/ΔV from Gauss cavity integral (extract_K.cavity_dV_mm3).
Refinement: ne/face ∈ {6, 12, 24, 48} → 6·ne² elements (216 … 13824).

Stop criterion (pre-defined): ε_i = |K_i − K_{i−1}|/|K_i| < 1% for two
consecutive refinements.  Recommend coarsest level that satisfies this for WP1.4/1.5.
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
WP1_1 = HERE.parent
OUT = WP1_1 / "output_wp1.1" / "mesh_independence"

sys.path.insert(0, str(HERE))
from extract_K import K_analytic_mmHg_per_uL  # noqa: E402
from run_verification import (  # noqa: E402
    CASES,
    E_MPA,
    NU,
    ccx_bin,
    run_case,
)

NE_LEVELS = (6, 12, 24, 48)
REFINE_RATIO = 2.0
EPS_TARGET = 0.01
CASES_TO_RUN = ("human", "rabbit")


def n_elements(ne: int) -> int:
    return 6 * ne * ne


def h_char_mm(R_mm: float, ne: int) -> float:
    return math.pi * R_mm / (2.0 * ne)


def richardson_p(k: tuple[float, float, float], r: float = REFINE_RATIO) -> float:
    k2, k1, k0 = k
    num = k2 - k1
    den = k1 - k0
    if abs(den) < 1e-15 or num * den <= 0:
        return float("nan")
    return math.log(abs(num / den)) / math.log(r)


def richardson_K_inf(k_fine: float, k_coarser: float, p: float, r: float = REFINE_RATIO) -> float:
    if abs(r**p - 1.0) < 1e-12:
        return float("nan")
    return k_fine + (k_fine - k_coarser) / (r**p - 1.0)


def recommend_level(rows: list[dict]) -> dict:
    for i in range(1, len(rows) - 1):
        e1, e2 = rows[i].get("eps_pct"), rows[i + 1].get("eps_pct")
        if e1 is None or e2 is None:
            continue
        if e1 < EPS_TARGET * 100 and e2 < EPS_TARGET * 100:
            ne = rows[i]["ne_per_face"]
            return {
                "ne_per_face": ne,
                "n_elements": n_elements(ne),
                "reason": (
                    f"ε({rows[i-1]['ne_per_face']}→{ne})={e1:.3f}% and "
                    f"ε({ne}→{rows[i+1]['ne_per_face']})={e2:.3f}% both < {EPS_TARGET*100:.0f}%"
                ),
            }
    return {
        "ne_per_face": None,
        "n_elements": None,
        "reason": "criterion not met on any pair of consecutive refinements",
    }


def write_plot(rows: list[dict], case: str, R: float, K_an: float, out_dir: Path) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not available — skipping plots", file=sys.stderr)
        return

    nes = np.array([r["ne_per_face"] for r in rows], dtype=float)
    Ks = np.array([r["K_FEA_mmHg_per_uL"] for r in rows])
    hs = np.array([r["h_char_mm"] for r in rows])
    inv_h2 = 1.0 / hs**2
    k_inf = rows[-1].get("K_richardson", float("nan"))

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    ax = axes[0]
    ax.plot(nes, Ks, "o-", label="K_FEA")
    ax.axhline(K_an, color="C1", ls="--", label=f"K_analytic={K_an:.5f}")
    if not math.isnan(k_inf):
        ax.axhline(k_inf, color="C2", ls=":", label="K_∞ Richardson")
    ax.set_xlabel("ne per cube face")
    ax.set_ylabel("K (mmHg/µL)")
    ax.set_title(f"{case}: K vs mesh density")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    ax.plot(inv_h2, Ks, "s-", color="C0")
    ax.axhline(K_an, color="C1", ls="--")
    ax.set_xlabel(r"$1/h^2$ (1/mm²)")
    ax.set_ylabel("K (mmHg/µL)")
    ax.set_title("K vs $1/h²$ (plateau check)")
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(out_dir / "K_convergence.png", dpi=150)
    plt.close(fig)


def write_case_report(study: dict, case_dir: Path) -> str:
    """Standalone markdown report for one species."""
    lines = [
        f"# wp1.1 — independência de malha ({study['case']})\n",
        f"QoI: **K = ΔP/ΔV** via ∫ u·n dA (Gauss).  Critério: ε_i < {EPS_TARGET*100:.0f}% "
        f"em **dois** refinamentos consecutivos.\n",
    ]
    lines.extend(format_case_section(study))
    md = "\n".join(lines)
    (case_dir / "MESH_INDEPENDENCE.md").write_text(md)
    (case_dir / "results.json").write_text(
        json.dumps({k: v for k, v in study.items() if k != "rows"} | {"rows": study["rows"]}, indent=2)
    )
    return md


def run_study(case: str) -> dict:
    geom = CASES[case]
    R, t = geom["R"], geom["t"]
    K_an = K_analytic_mmHg_per_uL(R, t, E_MPA, NU)
    case_dir = OUT / case
    case_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}\nCase: {case}  R={R} mm  t={t} mm  ne levels: {NE_LEVELS}\n{'='*60}")

    rows: list[dict] = []
    for ne in NE_LEVELS:
        t0 = time.perf_counter()
        print(f"=== {case} ne={ne}  (n_elem={n_elements(ne)}) ===")
        res = run_case(case, ne, tag=f"meshind_{case}_ne{ne}")
        elapsed = time.perf_counter() - t0
        row = {
            "case": case,
            "ne_per_face": ne,
            "n_elements": res["n_elements"],
            "n_nodes": res["n_nodes"],
            "h_char_mm": h_char_mm(R, ne),
            "K_FEA_mmHg_per_uL": res["K_FEA_mmHg_per_uL"],
            "K_analytic_mmHg_per_uL": K_an,
            "err_vs_analytic_pct": res["error_pct"],
            "dV_uL": res["dV_uL"],
            "time_s": elapsed,
        }
        rows.append(row)
        print(f"  K={row['K_FEA_mmHg_per_uL']:.6f}  time={elapsed:.1f}s\n")

    for i, row in enumerate(rows):
        if i == 0:
            row["eps_pct"] = None
            row["eps_label"] = "—"
        else:
            ki = row["K_FEA_mmHg_per_uL"]
            kp = rows[i - 1]["K_FEA_mmHg_per_uL"]
            eps = 100.0 * abs(ki - kp) / abs(ki)
            row["eps_pct"] = eps
            row["eps_label"] = f"{eps:.3f}"

    Ks = [r["K_FEA_mmHg_per_uL"] for r in rows]
    diffs = [Ks[i] - Ks[i + 1] for i in range(len(Ks) - 1)]
    monotonic = all(d >= 0 for d in diffs) or all(d <= 0 for d in diffs)

    p = float("nan")
    p_mid = float("nan")
    k_inf = float("nan")
    if len(rows) >= 3:
        k3 = tuple(r["K_FEA_mmHg_per_uL"] for r in rows[-3:])
        p = richardson_p(k3, REFINE_RATIO)
        k_inf = richardson_K_inf(k3[2], k3[1], p, REFINE_RATIO)
        rows[-1]["p_richardson"] = p
        rows[-1]["K_richardson"] = k_inf
        if len(rows) >= 4:
            km = tuple(r["K_FEA_mmHg_per_uL"] for r in rows[:3])
            p_mid = richardson_p(km, REFINE_RATIO)

    rec = recommend_level(rows)

    study = {
        "case": case,
        "R_mm": R,
        "t_mm": t,
        "K_analytic": K_an,
        "rows": rows,
        "p": p,
        "p_mid": p_mid,
        "K_inf": k_inf,
        "monotonic": monotonic,
        "recommend": rec,
    }
    write_case_report(study, case_dir)

    with open(case_dir / "K_vs_mesh.csv", "w") as fh:
        fh.write("ne_per_face,n_elements,h_char_mm,K_FEA,eps_pct,time_s,inv_h2\n")
        for r in rows:
            inv = 1.0 / r["h_char_mm"] ** 2
            eps = "" if r["eps_pct"] is None else f"{r['eps_pct']:.6f}"
            fh.write(
                f"{r['ne_per_face']},{r['n_elements']},{r['h_char_mm']:.6f},"
                f"{r['K_FEA_mmHg_per_uL']:.8f},{eps},{r['time_s']:.2f},{inv:.6e}\n"
            )

    write_plot(rows, case, R, K_an, case_dir)

    return study


def format_case_section(study: dict) -> list[str]:
    case = study["case"]
    rows = study["rows"]
    p, p_mid, k_inf = study["p"], study["p_mid"], study["K_inf"]
    rec = study["recommend"]
    K_an = study["K_analytic"]
    monotonic = study["monotonic"]

    lines = [
        f"## {case} (R={study['R_mm']} mm, t={study['t_mm']} mm)\n",
        f"K_analytic = {K_an:.6f} mmHg/µL (checagem extra; não critério de parada).\n",
        "| ne/face | elementos | h_char (mm) | K_FEA | ε_i vs anterior (%) | t (s) | err vs analítico (%) |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        lines.append(
            f"| {r['ne_per_face']} | {r['n_elements']} | {r['h_char_mm']:.4f} | "
            f"{r['K_FEA_mmHg_per_uL']:.6f} | {r['eps_label']} | {r['time_s']:.1f} | "
            f"{r['err_vs_analytic_pct']:.3f} |"
        )

    lines.append("\n**Convergência:**")
    lines.append(f"- Monotônica: **{'sim' if monotonic else 'NÃO — investigar'}**")
    lines.append(f"- p (Richardson, últimos 3 níveis): **{p:.3f}** (esperado ~2 para S8)")
    if not math.isnan(p_mid):
        lines.append(f"- p (6→12→24): **{p_mid:.3f}**")
    if not math.isnan(k_inf):
        err_inf = 100.0 * (k_inf - K_an) / K_an
        lines.append(f"- K_∞ ≈ **{k_inf:.6f}** mmHg/µL (vs analítico {err_inf:+.3f}%)")

    lines.append("\n**Recomendação:**")
    if rec["ne_per_face"]:
        lines.append(
            f"ne/face = **{rec['ne_per_face']}** ({rec['n_elements']} elementos): {rec['reason']}."
        )
    else:
        lines.append(f"Critério **não atingido**: {rec['reason']}.")

    if not monotonic:
        lines.append(
            "\n⚠ K não monotônico — revisar malha antes de aceitar convergência."
        )
    if not math.isnan(p) and (p < 0.8 or p > 3.0):
        hint = ""
        if not math.isnan(p_mid) and 1.2 <= p_mid <= 3.0 and rows[-1].get("eps_pct", 99) < 0.1:
            hint = f" p alto no trio fino com p(6,12,24)={p_mid:.2f} sugere plateau."
        lines.append(f"\n⚠ p={p:.2f} fora da banda ~2.{hint}")

    lines.append(f"\nGráfico: `{case}/K_convergence.png`\n")
    return lines


def parse_args() -> argparse.Namespace:
    import argparse

    p = argparse.ArgumentParser(description="wp1.1 mesh-independence study")
    p.add_argument(
        "case",
        nargs="?",
        choices=("human", "rabbit", "all"),
        default="all",
        help="species to run (default: all)",
    )
    return p.parse_args()


def main() -> int:
    import argparse  # noqa: F401 — used by parse_args

    args = parse_args()
    cases = CASES_TO_RUN if args.case == "all" else (args.case,)

    OUT.mkdir(parents=True, exist_ok=True)

    print(f"CalculiX: {ccx_bin()}")
    print(f"Stop criterion: ε_i < {EPS_TARGET*100:.0f}% for two consecutive refinements")
    print(f"Cases: {', '.join(cases)}")

    studies = [run_study(case) for case in cases]

    if len(studies) > 1:
        lines = [
            "# wp1.1 — estudo de independência de malha (índice)\n",
            f"Relatórios separados: `human/MESH_INDEPENDENCE.md`, `rabbit/MESH_INDEPENDENCE.md`.\n",
        ]
        for study in studies:
            lines.extend(format_case_section(study))
        recs = {s["case"]: s["recommend"]["ne_per_face"] for s in studies}
        lines.append("## Recomendação comum WP1.4 / 1.5\n")
        if all(recs.values()):
            ne_common = max(recs.values())
            lines.append(
                f"Usar **ne/face = {ne_common}** ({n_elements(ne_common)} elementos/esfera): {recs}."
            )
        (OUT / "MESH_INDEPENDENCE.md").write_text("\n".join(lines))
        (OUT / "results.json").write_text(
            json.dumps(
                {s["case"]: {k: v for k, v in s.items() if k != "rows"} | {"rows": s["rows"]} for s in studies},
                indent=2,
            )
        )
        print("\n" + "\n".join(lines))
    else:
        md = (OUT / studies[0]["case"] / "MESH_INDEPENDENCE.md").read_text()
        print("\n" + md)

    print(f"\nWrote {OUT}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
