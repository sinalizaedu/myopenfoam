#!/usr/bin/env python3
"""WP1.5 — species pilot: human + rabbit octant, Ogden + Yeoh.

.. deprecated:: SUPERSEDED por ``run_pilot_species_p0corr.py``.
   BUG conhecido: este piloto usa P0=16,9 mmHg (basal humano) para as DUAS
   espécies — o basal do coelho anestesiado é 26,7 mmHg. Os números de coelho
   em ``output_pilot_species_p50/`` têm o V=0 fora do basal fisiológico.
   Mantido apenas para reproduzir o histórico; não use para conclusões.

Uses official WP1.2 closure fits (Friedenwald, P_final=50 mmHg):
  wp1.2/output_literature_p50_v2/friedenwald_{ogden,yeoh}/fit_results.json

Compares V_max and early effective stiffness K_eff between materials per species.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WP15 = HERE.parent
WP12 = WP15.parent / "wp1.2"
sys.path.insert(0, str(WP12 / "scripts"))

from ogden_forward_run import load_ogden_params, run_ogden_forward  # noqa: E402
from yeoh_forward_run import run_yeoh_forward  # noqa: E402
from yeoh_material import P0_MMHG, load_yeoh_params  # noqa: E402

SPECIES = {
    "human": {"R_mm": 12.0, "t_mm": 0.5},
    "rabbit": {"R_mm": 7.6, "t_mm": 0.33},
}

FIT_OGDEN = WP12 / "output_literature_p50_v2" / "friedenwald_ogden" / "fit_results.json"
FIT_YEOH = WP12 / "output_literature_p50_v2" / "friedenwald_yeoh" / "fit_results.json"
P_FINAL_DEFAULT = 50.0


def k_eff_early(pv: list[dict]) -> float:
    v = [r["dV_uL"] for r in pv if r["dV_uL"] > 0]
    p = [r["p_mmhg"] for r in pv if r["dV_uL"] > 0]
    if v and v[0] > 1e-9:
        return (p[0] - P0_MMHG) / v[0]
    return float("nan")


def run_one(material: str, species: str, geom: dict, work: Path, ne: int, p_final: float) -> dict:
    R, t = geom["R_mm"], geom["t_mm"]
    tag = f"{species}_{material}"
    try:
        if material == "yeoh":
            pv, _ = run_yeoh_forward(
                R, t, work, tag, ne=ne, p_final=p_final, fit_path=FIT_YEOH,
            )
        else:
            pv, _ = run_ogden_forward(
                R, t, work, tag, ne=ne, p_final=p_final, fit_path=FIT_OGDEN,
            )
        return {
            "species": species,
            "material": material,
            **geom,
            "status": "OK",
            "V_max_uL": max(r["dV_uL"] for r in pv),
            "K_eff_early_mmHg_per_uL": k_eff_early(pv),
            "n_pv_points": len(pv),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "species": species,
            "material": material,
            **geom,
            "status": f"FAIL: {exc}",
        }


def write_results_md(out: Path, results: list[dict], meta: dict) -> None:
    by_species: dict[str, dict] = {}
    for r in results:
        d = by_species.setdefault(r["species"], {"R_mm": r["R_mm"], "t_mm": r["t_mm"]})
        mat = r["material"]
        if r["status"] == "OK":
            d[f"{mat}_vmax"] = r["V_max_uL"]
            d[f"{mat}_keff"] = r["K_eff_early_mmHg_per_uL"]
        else:
            d[f"{mat}_status"] = r["status"]

    lines = [
        "# WP1.5 — species pilot (Ogden + Yeoh, Friedenwald P_final=50)\n",
        f"- **Ogden**: μ₁={meta['ogden']['mu1_MPa']:.4f} MPa, α₁={meta['ogden']['alpha1']:.4f}",
        f"- **Yeoh**: C10={meta['yeoh']['C10_MPa']:.4f}, C20={meta['yeoh']['C20_MPa']:.4f} MPa",
        f"- **Mesh**: octant spherical, ne={meta['ne']}",
        f"- **Convergence**: {meta['n_ok']}/{meta['n_total']} OK",
        "",
        "| species | R [mm] | t [mm] | V_max Ogden [µL] | K_eff Ogden | V_max Yeoh [µL] | K_eff Yeoh | ΔV Yeoh−Ogden | ΔK Yeoh−Ogden |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for sp, d in by_species.items():
        vo, vy = d.get("ogden_vmax"), d.get("yeoh_vmax")
        ko, ky = d.get("ogden_keff"), d.get("yeoh_keff")
        vo_s = f"{vo:.1f}" if vo is not None else "—"
        vy_s = f"{vy:.1f}" if vy is not None else "—"
        ko_s = f"{ko:.3f}" if ko is not None else "—"
        ky_s = f"{ky:.3f}" if ky is not None else "—"
        dv = f"{vy - vo:+.1f}" if vo is not None and vy is not None else "—"
        dk = f"{ky - ko:+.3f}" if ko is not None and ky is not None else "—"
        lines.append(
            f"| {sp} | {d['R_mm']} | {d['t_mm']} | {vo_s} | {ko_s} | {vy_s} | {ky_s} | {dv} | {dk} |"
        )
    lines.append("")
    lines.append(
        "Simplified spherical octant only; full globe + cornea + AC pending. "
        "Cross-check: `cases/claude-wp1.5/`."
    )
    lines.append("")
    (out / "RESULTS.md").write_text("\n".join(lines) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--materials", default="ogden,yeoh")
    ap.add_argument("--species", default="human,rabbit")
    ap.add_argument("--ne", type=int, default=8)
    ap.add_argument("--p-final", type=float, default=P_FINAL_DEFAULT)
    ap.add_argument("--out", type=Path, default=WP15 / "output_pilot_species_p50")
    args = ap.parse_args()

    for p in (FIT_OGDEN, FIT_YEOH):
        if not p.is_file():
            raise FileNotFoundError(f"Missing fit: {p}")

    materials = [m.strip() for m in args.materials.split(",") if m.strip()]
    species_list = [s.strip() for s in args.species.split(",") if s.strip()]
    args.out.mkdir(parents=True, exist_ok=True)
    work = args.out / "ccx_runs"

    ogden_p = load_ogden_params(FIT_OGDEN)
    yeoh_p = load_yeoh_params(FIT_YEOH)

    results: list[dict] = []
    for material in materials:
        for sp in species_list:
            if sp not in SPECIES:
                raise ValueError(f"Unknown species: {sp}")
            print(f"=== {sp} {material} R={SPECIES[sp]['R_mm']} t={SPECIES[sp]['t_mm']} ===")
            entry = run_one(material, sp, SPECIES[sp], work, args.ne, args.p_final)
            print(f"  -> {entry['status']}")
            results.append(entry)

    n_ok = sum(1 for r in results if r["status"] == "OK")
    payload = {
        "fits": {"ogden": str(FIT_OGDEN), "yeoh": str(FIT_YEOH)},
        "materials": {"ogden": ogden_p, "yeoh": yeoh_p},
        "p_final_mmHg": args.p_final,
        "ne": args.ne,
        "note": "Simplified WP1.5: 2-species spherical octant. Full globe+cornea+AC pending port.",
        "results": results,
    }
    (args.out / "pilot_results.json").write_text(json.dumps(payload, indent=2))
    write_results_md(
        args.out,
        results,
        {
            "ogden": ogden_p,
            "yeoh": yeoh_p,
            "ne": args.ne,
            "n_ok": n_ok,
            "n_total": len(results),
        },
    )
    print(f"\nWrote {args.out / 'RESULTS.md'} ({n_ok}/{len(results)} OK)")
    return 0 if n_ok == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
