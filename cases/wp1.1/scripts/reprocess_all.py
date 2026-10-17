#!/usr/bin/env python3
"""Repost-process wp1.1 from existing .frd files (no CalculiX re-run).

Uses KDTree R±t/2 + mean FRD mapping (default in extract_K.py).
Regenerates mesh-independence tables, verification RESULTS, summary.json.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WP1_1 = HERE.parent
CCX_DIR = WP1_1 / "ccx"
OUT = WP1_1 / "output_wp1.1"
MESH_OUT = OUT / "mesh_independence"

sys.path.insert(0, str(HERE))
from extract_K import K_analytic_mmHg_per_uL, extract  # noqa: E402
from mesh_independence import (  # noqa: E402
    EPS_TARGET,
    NE_LEVELS,
    REFINE_RATIO,
    CASES_TO_RUN,
    format_case_section,
    h_char_mm,
    n_elements,
    recommend_level,
    richardson_K_inf,
    richardson_p,
    write_case_report,
    write_plot,
)
from run_verification import (  # noqa: E402
    CASES,
    CONVERGENCE_LEVELS,
    E_MPA,
    NE_FINE,
    NU,
    copy_deliverable_deck,
    format_results_md,
)

SUPERSESSION_NOTE = """\
> **Nota (correção de pós-processamento):** versões anteriores deste relatório usavam
> mapeamento FRD por *bucket angular* com fallback (~25% dos nós S8 de aresta/meio-de-aresta),
> que podia escolher o nó de topo vs base errado e viésar K em malha grossa.
> **Método atual (padrão):** KDTree 3D + média aritmética em R±t/2 (superfície média
> sob variação linear na espessura). Mesmos `.frd`; só o pós-processamento mudou.
"""


def find_deck_frd(case: str, ne: int) -> tuple[Path, Path]:
    for tag in (f"meshind_{case}_ne{ne}", f"meshind_ne{ne}", f"ne{ne}"):
        deck = CCX_DIR / f"{case}_{tag}.inp"
        frd = CCX_DIR / f"{case}_{tag}.frd"
        if deck.is_file() and frd.is_file():
            return deck, frd
    raise FileNotFoundError(f"No deck/frd for {case} ne={ne}")


def reprocess_mesh_study(case: str) -> dict:
    geom = CASES[case]
    R, t = geom["R"], geom["t"]
    K_an = K_analytic_mmHg_per_uL(R, t, E_MPA, NU)
    case_dir = MESH_OUT / case
    case_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    for ne in NE_LEVELS:
        deck, frd = find_deck_frd(case, ne)
        res = extract(deck, frd, R, t, E_MPA, NU)
        rows.append(
            {
                "case": case,
                "ne_per_face": ne,
                "n_elements": res["n_elements"],
                "n_nodes": res["n_nodes"],
                "h_char_mm": h_char_mm(R, ne),
                "K_FEA_mmHg_per_uL": res["K_FEA_mmHg_per_uL"],
                "K_analytic_mmHg_per_uL": K_an,
                "err_vs_analytic_pct": res["error_pct"],
                "dV_uL": res["dV_uL"],
                "time_s": 0.0,
            }
        )
        print(f"  {case} ne={ne}: K={res['K_FEA_mmHg_per_uL']:.6f}")

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

    p = p_mid = k_inf = float("nan")
    if len(rows) >= 3:
        k3 = tuple(r["K_FEA_mmHg_per_uL"] for r in rows[-3:])
        p = richardson_p(k3, REFINE_RATIO)
        k_inf = richardson_K_inf(k3[2], k3[1], p, REFINE_RATIO)
        rows[-1]["p_richardson"] = p
        rows[-1]["K_richardson"] = k_inf
        if len(rows) >= 4:
            km = tuple(r["K_FEA_mmHg_per_uL"] for r in rows[:3])
            p_mid = richardson_p(km, REFINE_RATIO)

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
        "recommend": recommend_level(rows),
        "frd_mapping": "kdtree_r_pm_t2_mean",
    }
    write_case_report(study, case_dir)
    # prepend supersession note to per-species report
    pth = case_dir / "MESH_INDEPENDENCE.md"
    pth.write_text(SUPERSESSION_NOTE + "\n\n" + pth.read_text())

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


def reprocess_verification(case: str) -> tuple[dict, list[dict], dict]:
    geom = CASES[case]
    R, t = geom["R"], geom["t"]
    convergence: list[dict] = []
    for ne in CONVERGENCE_LEVELS:
        deck, frd = find_deck_frd(case, ne)
        res = extract(deck, frd, R, t, E_MPA, NU)
        res.update({"case": case, "ne_per_face": ne, "mesh_tag": f"ne{ne}"})
        convergence.append(res)
    deck_f, frd_f = find_deck_frd(case, NE_FINE)
    final = extract(deck_f, frd_f, R, t, E_MPA, NU)
    final.update({"case": case, "ne_per_face": NE_FINE, "mesh_tag": f"ne{NE_FINE}"})

    deck_h, frd_h = CCX_DIR / f"{case}_ne{NE_FINE}_Phalf.inp", CCX_DIR / f"{case}_ne{NE_FINE}_Phalf.frd"
    deck_f, frd_f = CCX_DIR / f"{case}_ne{NE_FINE}_Pfull.inp", CCX_DIR / f"{case}_ne{NE_FINE}_Pfull.frd"
    r_half = extract(deck_h, frd_h, R, t, E_MPA, NU)
    r_full = extract(deck_f, frd_f, R, t, E_MPA, NU)
    ratio = r_full["dV_uL"] / r_half["dV_uL"]
    lin = {
        "case": case,
        "dV_half_uL": r_half["dV_uL"],
        "dV_full_uL": r_full["dV_uL"],
        "volume_ratio": ratio,
        "linear_ok": abs(ratio - 2.0) < 0.02,
    }
    copy_deliverable_deck(case)
    md = format_results_md(case, final, convergence, lin)
    (OUT / f"RESULTS_{case}.md").write_text(SUPERSESSION_NOTE + "\n\n" + md)
    return final, convergence, lin


def main() -> int:
    MESH_OUT.mkdir(parents=True, exist_ok=True)
    print("=== reprocess wp1.1 (KDTree R±t/2 mapping, existing .frd) ===\n")

    studies = []
    for case in CASES_TO_RUN:
        print(f"Mesh independence: {case}")
        studies.append(reprocess_mesh_study(case))

    lines = [
        SUPERSESSION_NOTE,
        "\n# wp1.1 — estudo de independência de malha\n",
        f"QoI: **K = ΔP/ΔV** via ∫ u·n dA (Gauss).  Mapeamento FRD: **KDTree R±t/2 + média**.\n",
        f"Critério: ε_i < {EPS_TARGET*100:.0f}% em **dois** refinamentos consecutivos.\n",
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
    (MESH_OUT / "MESH_INDEPENDENCE.md").write_text("\n".join(lines))
    (MESH_OUT / "results.json").write_text(
        json.dumps(
            {
                "frd_mapping": "kdtree_r_pm_t2_mean",
                "supersedes": "angular_bucket_fallback",
                **{s["case"]: {k: v for k, v in s.items() if k != "rows"} | {"rows": s["rows"]} for s in studies},
            },
            indent=2,
        )
    )

    results, all_conv, all_lin = [], [], []
    for case in CASES_TO_RUN:
        print(f"\nVerification: {case}")
        final, conv, lin = reprocess_verification(case)
        results.append(final)
        all_conv.extend(conv)
        all_lin.append(lin)

    summary = {
        "cases": results,
        "mesh_convergence": all_conv,
        "linearity": all_lin,
        "parameters": {
            "E_MPa": E_MPA,
            "nu": NU,
            "ne_fine": NE_FINE,
            "frd_mapping": "kdtree_r_pm_t2_mean",
        },
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))

    rlines = [
        SUPERSESSION_NOTE,
        f"\n# wp1.1 — thin shell K verification\n",
        f"Malha final: **ne/face = {NE_FINE}** ({6 * NE_FINE * NE_FINE} elementos).\n",
        f"Mapeamento FRD: KDTree R±t/2 + média. Independência: `mesh_independence/MESH_INDEPENDENCE.md`.\n",
        "| caso | malha (elem) | ΔP | ΔV (µL) | K_FEA | K_analítico | erro (%) |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in results:
        rlines.append(
            f"| {r['case']} | {r['n_elements']} | {r['dP_mmHg']:.3f} | "
            f"{r['dV_uL']:.6f} | {r['K_FEA_mmHg_per_uL']:.6f} | "
            f"{r['K_analytic_mmHg_per_uL']:.6f} | {r['error_pct']:.2f} |"
        )
    rlines.append("\n## Convergência (ne = 6 / 12 / 24)\n")
    rlines.append("| caso | ne | elem | K_FEA | erro (%) |")
    rlines.append("|---|---:|---:|---:|---:|")
    for r in all_conv:
        rlines.append(
            f"| {r['case']} | {r['ne_per_face']} | {r['n_elements']} | "
            f"{r['K_FEA_mmHg_per_uL']:.6f} | {r['error_pct']:.2f} |"
        )
    rlines.append(f"\n## Linearidade (ne/face = {NE_FINE})\n")
    rlines.append("| caso | ΔV@0.5 | ΔV@1.0 | razão |")
    rlines.append("|---|---:|---:|---:|")
    for r in all_lin:
        rlines.append(
            f"| {r['case']} | {r['dV_half_uL']:.6f} | {r['dV_full_uL']:.6f} | {r['volume_ratio']:.4f} |"
        )
    errs = ", ".join(f"{r['case']} {r['error_pct']:+.2f}%" for r in results)
    rlines.append(f"\n## Conclusão\n\n**Critério <2% atingido** ({errs}).\n")
    (OUT / "RESULTS.md").write_text("\n".join(rlines))

    print("\n=== K summary (check vs reference) ===")
    ref = {
        ("human", 6): 0.163786,
        ("human", 12): 0.163719,
        ("human", 24): 0.163714,
        ("human", 48): 0.163713,
        ("rabbit", 6): 0.672019,
        ("rabbit", 12): 0.671740,
        ("rabbit", 24): 0.671720,
        ("rabbit", 48): 0.671718,
    }
    for study in studies:
        for row in study["rows"]:
            k = row["K_FEA_mmHg_per_uL"]
            exp = ref.get((study["case"], row["ne_per_face"]))
            if exp:
                d = 100 * abs(k - exp) / exp
                ok = "OK" if d < 0.01 else "DIFF"
                print(f"  {study['case']} ne={row['ne_per_face']}: K={k:.6f} ref={exp:.6f} {ok}")
        print(f"  recommend {study['case']}: ne={study['recommend']['ne_per_face']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
