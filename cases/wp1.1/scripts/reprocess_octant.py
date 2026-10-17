#!/usr/bin/env python3
"""Repost-process wp1.1 octant from existing .frd files (no CCX unless linearity missing).

Regenerates output_octant/summary.json, RESULTS_{human,rabbit}.md, and
theta_min_sensitivity.json (from claude-wp1.1 sweep at ne=6, 288 elem equiv).
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WP1_1 = HERE.parent
CCX_DIR = WP1_1 / "ccx"
OUT = WP1_1 / "output_octant"
CLAUDE_WP11 = WP1_1.parent / "claude-wp1.1" / "output" / "results.json"

sys.path.insert(0, str(HERE))
from extract_K import K_analytic_mmHg_per_uL, extract  # noqa: E402
from run_verification_octant import (  # noqa: E402
    CASES,
    CONVERGENCE_LEVELS,
    DP_MMHG,
    E_MPA,
    NE_RECOMMENDED,
    NU,
    mesh_independence_epsilon,
    publish_report_decks,
    run_ccx,
    write_combined_results,
    write_deck,
)

LINEARITY_TAG = f"oct_ne{NE_RECOMMENDED}"


def find_mesh_convergence_frd(case: str, ne: int) -> tuple[Path, Path]:
    tag = f"oct_ne{ne}"
    deck = CCX_DIR / f"{case}_{tag}.inp"
    frd = CCX_DIR / f"{case}_{tag}.frd"
    if deck.is_file() and frd.is_file():
        return deck, frd
    raise FileNotFoundError(f"Missing {case} {tag}: {deck} / {frd}")


def find_linearity_frd(case: str, load: str) -> tuple[Path, Path]:
    """load: 'Phalf' (0.5 mmHg) or 'Pfull' (1.0 mmHg)."""
    if load == "Pfull":
        return find_mesh_convergence_frd(case, NE_RECOMMENDED)
    tag = f"{LINEARITY_TAG}_{load}"
    deck = CCX_DIR / f"{case}_{tag}.inp"
    frd = CCX_DIR / f"{case}_{tag}.frd"
    if deck.is_file() and frd.is_file():
        return deck, frd
    raise FileNotFoundError(f"Missing linearity {case} {load}: {deck} / {frd}")


def reprocess_mesh_row(case: str, ne: int) -> dict:
    geom = CASES[case]
    deck, frd = find_mesh_convergence_frd(case, ne)
    res = extract(deck, frd, geom["R"], geom["t"], E_MPA, NU)
    res.update(
        {
            "case": case,
            "mesh_tag": f"oct_ne{ne}",
            "ne": ne,
            "full_sphere_equiv_elements": ne * ne * 8,
            "dP_mmHg": DP_MMHG,
            "deck": str(deck),
        }
    )
    return res


def run_linearity_ccx(case: str, dP_mmHg: float, load: str) -> dict:
    tag = LINEARITY_TAG if load == "Pfull" else f"{LINEARITY_TAG}_{load}"
    geom = CASES[case]
    mesh = CCX_DIR / f"{case}_{LINEARITY_TAG}_mesh.inp"
    if not mesh.is_file():
        from gen_sphere_shell_mesh import write_mesh  # noqa: E402

        write_mesh(
            mesh,
            geom["R"],
            geom["t"],
            NE_RECOMMENDED,
            2,
            label=f"{case} spherical octant ne={NE_RECOMMENDED}",
            bc_mode="symmetry_octant",
            mesh_kind="spherical",
            theta_min_deg=3.0,
            reduced=True,
        )
    deck = CCX_DIR / f"{case}_{tag}.inp"
    write_deck(deck, mesh.name, geom["R"], geom["t"], dP_mmHg, f"{case} ({tag})")
    for ext in (".frd", ".sta", ".cvg", ".dat", ".12d"):
        p = CCX_DIR / f"{case}_{tag}{ext}"
        if p.exists():
            p.unlink()
    frd = run_ccx(deck)
    return extract(deck, frd, geom["R"], geom["t"], E_MPA, NU)


def linearity_row(case: str, *, run_missing: bool) -> dict:
    deck_half = CCX_DIR / f"{case}_{LINEARITY_TAG}_Phalf.inp"
    try:
        deck_h, frd_h = find_linearity_frd(case, "Phalf")
        r_half = extract(deck_h, frd_h, *CASES[case].values(), E_MPA, NU)
        deck_half = deck_h
    except FileNotFoundError:
        if not run_missing:
            raise
        print(f"  {case}: running Phalf (0.5 mmHg)...")
        r_half = run_linearity_ccx(case, 0.5 * DP_MMHG, "Phalf")

    deck_f, frd_f = find_linearity_frd(case, "Pfull")
    r_full = extract(deck_f, frd_f, *CASES[case].values(), E_MPA, NU)

    ratio = r_full["dV_uL"] / r_half["dV_uL"] if abs(r_half["dV_uL"]) > 1e-20 else float("nan")
    return {
        "case": case,
        "ne": NE_RECOMMENDED,
        "full_sphere_equiv_elements": NE_RECOMMENDED * NE_RECOMMENDED * 8,
        "dV_half_uL": r_half["dV_uL"],
        "dV_full_uL": r_full["dV_uL"],
        "volume_ratio": ratio,
        "linear_ok": abs(ratio - 2.0) < 0.02,
        "deck_half": str(deck_half),
        "deck_full": str(deck_f),
    }


def load_theta_min_sensitivity() -> dict:
    src = CLAUDE_WP11
    if not src.is_file():
        return {"source": str(src), "note": "claude-wp1.1 theta_min sweep not found", "results": []}
    rows = json.loads(src.read_text())
    return {
        "source": str(src),
        "note": "ne=6 (288 full-sphere equiv), S8R, NLGEOM=NO, theta_min sweep 1/3/5 deg",
        "results": rows,
    }


def format_results_md(case: str, rows: list[dict], lin: dict) -> str:
    geom = CASES[case]
    lines = [
        f"# wp1.1 octant — K verification ({case})\n",
        f"Geometria: R={geom['R']} mm, t={geom['t']} mm. "
        f"Malha esférica (θ,φ), S8R, θ_min=3°, simetria nos 3 planos.\n",
        "| elem (full eq.) | K_FEA | ε_i (%) | erro vs analítico (%) |",
        "|---:|---:|---:|---:|",
    ]
    for r in rows:
        eps = r.get("epsilon_i_pct", float("nan"))
        eps_s = "—" if eps != eps else f"{eps:.4f}"
        lines.append(
            f"| {r['full_sphere_equiv_elements']} | {r['K_FEA_mmHg_per_uL']:.6f} | "
            f"{eps_s} | {r['error_pct']:.2f} |"
        )
    final = next((r for r in rows if r["ne"] == NE_RECOMMENDED), rows[-1])
    lines.extend(
        [
            f"\nK_analítico: {final['K_analytic_mmHg_per_uL']:.6f} mmHg/µL\n",
            f"Erro @ ne={final['ne']} (≈{final['full_sphere_equiv_elements']} elem): "
            f"**{final['error_pct']:+.2f}%**\n",
            f"\n## Linearidade (ne={NE_RECOMMENDED}, ≈{lin['full_sphere_equiv_elements']} elem)\n",
            "| ΔV @0.5 mmHg | ΔV @1.0 mmHg | razão |",
            "|---:|---:|---:|",
            f"| {lin['dV_half_uL']:.6f} | {lin['dV_full_uL']:.6f} | {lin['volume_ratio']:.4f} |",
        ]
    )
    return "\n".join(lines) + "\n"


def build_summary(
    all_rows: list[dict],
    linearity: list[dict],
    theta_min: dict,
) -> dict:
    return {
        "mesh_kind": "spherical_octant",
        "bc_mode": "symmetry_octant",
        "theta_min_deg": 3.0,
        "gauss_order": 3,
        "convergence_levels": list(CONVERGENCE_LEVELS),
        "ne_recommended": NE_RECOMMENDED,
        "results": all_rows,
        "linearity": linearity,
        "theta_min_sensitivity": theta_min,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--run-missing-linearity",
        action="store_true",
        help="Run CCX for Phalf decks if .frd missing",
    )
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    all_rows: list[dict] = []
    linearity: list[dict] = []

    for case in ("human", "rabbit"):
        print(f"\n=== {case} mesh reprocess ===")
        rows = [reprocess_mesh_row(case, ne) for ne in CONVERGENCE_LEVELS]
        rows = mesh_independence_epsilon(rows)
        all_rows.extend(rows)
        for r in rows:
            eps = r.get("epsilon_i_pct", float("nan"))
            eps_s = "—" if eps != eps else f"{eps:.4f}"
            print(
                f"  ne={r['ne']} ({r['full_sphere_equiv_elements']} elem): "
                f"K={r['K_FEA_mmHg_per_uL']:.6f} eps_i={eps_s}"
            )

        print(f"=== {case} linearity ===")
        lin = linearity_row(case, run_missing=args.run_missing_linearity)
        linearity.append(lin)
        print(f"  ratio={lin['volume_ratio']:.4f} linear={'OK' if lin['linear_ok'] else 'FAIL'}")

        (OUT / f"RESULTS_{case}.md").write_text(format_results_md(case, rows, lin))

    theta_min = load_theta_min_sensitivity()
    (OUT / "theta_min_sensitivity.json").write_text(json.dumps(theta_min, indent=2))

    summary = build_summary(all_rows, linearity, theta_min)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))

    case_rows = {
        "human": [r for r in all_rows if r["case"] == "human"],
        "rabbit": [r for r in all_rows if r["case"] == "rabbit"],
    }
    publish_report_decks(("human", "rabbit"), ne=NE_RECOMMENDED)
    write_combined_results(case_rows, linearity)

    print(f"\nwrote {OUT / 'summary.json'}")
    print(f"wrote {OUT / 'theta_min_sensitivity.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
