#!/usr/bin/env python3
"""claude-wp1.5 — piloto de espécie (humano + coelho), Ogden + Yeoh, com
os parâmetros OFICIAIS recalibrados do fechamento do WP1.2
(Friedenwald, P_final=50 mmHg).

O WP1.5 original (cases/wp1.5/, rodado em 22/set, ANTES do fechamento
do WP1.2) só tem Yeoh com params antigos e P_final=80. Este script
atualiza com o fit oficial e adiciona Ogden, reusando as mesmas
geometrias de espécie do original (leitura, não editado).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent            # cases/claude-wp1.5/scripts
CLAUDE_WP15 = HERE.parent                          # cases/claude-wp1.5
WP12 = CLAUDE_WP15.parent / "wp1.2"                 # leitura apenas (Composer)

sys.path.insert(0, str(WP12 / "scripts"))
sys.path.insert(0, str(HERE))

from yeoh_forward_run import run_yeoh_forward  # noqa: E402  (reuso, não editado)
from ogden_forward_run import run_ogden_forward  # noqa: E402  (claude, mesmo do wp1.4)

# Mesmas geometrias de espécie do wp1.5/scripts/run_pilot_yeoh.py original
SPECIES = {
    "human": {"R_mm": 12.0, "t_mm": 0.5},
    "rabbit": {"R_mm": 7.6, "t_mm": 0.33},
}

FIT_PATHS = {
    "ogden": WP12 / "output_literature_p50_v2" / "friedenwald_ogden" / "fit_results.json",
    "yeoh": WP12 / "output_literature_p50_v2" / "friedenwald_yeoh" / "fit_results.json",
}
P0_MMHG = 16.9
P_FINAL_DEFAULT = 50.0


def run_one(material: str, species: str, geom: dict, work: Path, ne: int, p_final: float) -> dict:
    R, t = geom["R_mm"], geom["t_mm"]
    tag = f"{species}_{material}"
    try:
        if material == "yeoh":
            pv, meta = run_yeoh_forward(
                R, t, work, tag, ne=ne, p_final=p_final, fit_path=FIT_PATHS["yeoh"],
            )
        else:
            pv, meta = run_ogden_forward(
                R, t, work, tag, ne=ne, p_final=p_final, fit_path=FIT_PATHS["ogden"],
            )
        v = [r["dV_uL"] for r in pv if r["dV_uL"] > 0]
        p = [r["p_mmhg"] for r in pv if r["dV_uL"] > 0]
        k_eff = (p[0] - P0_MMHG) / v[0] if v and v[0] > 1e-9 else float("nan")
        return {
            "species": species, "material": material, **geom, "status": "OK",
            "V_max_uL": max(r["dV_uL"] for r in pv),
            "K_eff_early_mmHg_per_uL": k_eff,
        }
    except Exception as exc:  # noqa: BLE001
        return {"species": species, "material": material, **geom, "status": f"FAIL: {exc}"}


def write_summary(out: Path, results: list[dict]) -> None:
    by_species: dict[str, dict] = {}
    for r in results:
        d = by_species.setdefault(r["species"], {"R_mm": r["R_mm"], "t_mm": r["t_mm"]})
        vm = r.get("V_max_uL")
        ke = r.get("K_eff_early_mmHg_per_uL")
        d[f"{r['material']}_vmax"] = f"{vm:.1f}" if r["status"] == "OK" else "FALHOU"
        d[f"{r['material']}_keff"] = f"{ke:.3f}" if r["status"] == "OK" else "—"

    lines = [
        "# claude-wp1.5 — piloto de espécie (humano + coelho), Ogden + Yeoh",
        "## (Friedenwald recalibrado, P_final=50 mmHg -- atualiza cases/wp1.5/)\n",
        "| espécie | R [mm] | t [mm] | V_max Ogden [µL] | K_eff Ogden | V_max Yeoh [µL] | K_eff Yeoh |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for sp, d in by_species.items():
        lines.append(
            f"| {sp} | {d['R_mm']} | {d['t_mm']} | {d.get('ogden_vmax', '—')} | "
            f"{d.get('ogden_keff', '—')} | {d.get('yeoh_vmax', '—')} | {d.get('yeoh_keff', '—')} |"
        )
    lines.append("")
    (out / "RESULTS_CLAUDE.md").write_text("\n".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--materials", default="ogden,yeoh")
    ap.add_argument("--species", default="human,rabbit")
    ap.add_argument("--ne", type=int, default=8)
    ap.add_argument("--p-final", type=float, default=P_FINAL_DEFAULT)
    ap.add_argument("--out", type=Path, default=CLAUDE_WP15 / "output_pilot_species_claude")
    args = ap.parse_args()

    materials = [m.strip() for m in args.materials.split(",") if m.strip()]
    species = [s.strip() for s in args.species.split(",") if s.strip()]
    args.out.mkdir(parents=True, exist_ok=True)
    work = args.out / "ccx_runs"

    results = []
    for material in materials:
        for sp in species:
            print(f"=== {sp} {material} R={SPECIES[sp]['R_mm']} t={SPECIES[sp]['t_mm']} ===")
            entry = run_one(material, sp, SPECIES[sp], work, args.ne, args.p_final)
            print(f"  -> {entry['status']}")
            results.append(entry)

    (args.out / "pilot_species_results.json").write_text(json.dumps(results, indent=2))
    write_summary(args.out, results)
    n_ok = sum(1 for r in results if r["status"] == "OK")
    print(f"\nDone: {n_ok}/{len(results)} OK -- see {args.out / 'RESULTS_CLAUDE.md'}")
    return 0 if n_ok == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
