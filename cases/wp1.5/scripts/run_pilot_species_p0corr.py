#!/usr/bin/env python3
"""WP1.5 — species pilot CORRIGIDO: P0 basal específico por espécie.

Bug do piloto anterior (``run_pilot_species.py`` → ``output_pilot_species_p50/``):
os runners do wp1.2 fixam P0=16,9 mmHg (basal HUMANO) para as duas espécies —
tanto na geometria de referência sem tensão (a rampa começa em 16,9) quanto
no V=0 de ``extract_pv``. O basal do coelho anestesiado é 26,7 mmHg.

Basais (equilíbrio de Goldmann, mesmos parâmetros do relatório WP0, seção
"Produção trabecular e uveoescleral"):

    P0 = Pev + Q_prod·(1 − frac_uv) / C_out

| espécie            | Q_prod | C_out | Pev  | frac_uv | P0     |
|--------------------|--------|-------|------|---------|--------|
| humano             | 2,4    | 0,28  | 10,0 | 0,20    | 16,9   |
| coelho anestesiado | 3,06   | 0,26  | 15,5 | 0,05    | 26,7   |

Janela de pressão: MESMA amplitude ΔP = 33,1 mmHg a partir do basal de cada
espécie (humano 16,9→50,0; coelho 26,7→59,8), para não confundir diferença de
complacência real com diferença de janela absoluta de pressão. Decisão de
desenho (a alternativa é p_final=50 fixo para as duas) — ver
``cases/claude-wp1.5/CORRECAO_P0_ESPECIE_CLAUDE.md``.

CAVEAT que PERMANECE: o material (fit Ogden/Yeoh Friedenwald) é calibrado em
dados HUMANOS e aplicado à geometria do coelho sem recalibração.

Cross-validação independente: ``cases/claude-wp1.5/output_pilot_species_corrected_claude/``.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WP15 = HERE.parent
WP12 = WP15.parent / "wp1.2"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(WP12 / "scripts"))

from forward_run_v2 import run_forward  # noqa: E402
from ogden_forward_run import load_ogden_params  # noqa: E402
from yeoh_material import load_yeoh_params  # noqa: E402

SPECIES = {
    "human": {"R_mm": 12.0, "t_mm": 0.5},
    "rabbit": {"R_mm": 7.6, "t_mm": 0.33},
}

P0_MMHG_BY_SPECIES = {
    "human": 16.9,
    "rabbit": 26.7,
}

# Mesma amplitude do piloto original (50,0 − 16,9), a partir do basal de cada espécie.
DELTA_P_MMHG = 50.0 - 16.9

FIT_OGDEN = WP12 / "output_literature_p50_v2" / "friedenwald_ogden" / "fit_results.json"
FIT_YEOH = WP12 / "output_literature_p50_v2" / "friedenwald_yeoh" / "fit_results.json"

# Resultados anteriores (com o bug de P0) e cross-check independente (somente leitura).
PREV_RESULTS_JSON = WP15 / "output_pilot_species_p50" / "pilot_results.json"
CLAUDE_RESULTS_JSON = (
    WP15.parent / "claude-wp1.5" / "output_pilot_species_corrected_claude"
    / "pilot_species_corrected_results.json"
)


def k_eff_early(pv: list[dict], p0: float) -> float:
    v = [r["dV_uL"] for r in pv if r["dV_uL"] > 0]
    p = [r["p_mmhg"] for r in pv if r["dV_uL"] > 0]
    if v and v[0] > 1e-9:
        return (p[0] - p0) / v[0]
    return float("nan")


def run_one(material: str, species: str, geom: dict, work: Path, ne: int) -> dict:
    R, t = geom["R_mm"], geom["t_mm"]
    tag = f"{species}_{material}_p0corr"
    p0 = P0_MMHG_BY_SPECIES[species]
    p_final = p0 + DELTA_P_MMHG
    fit = FIT_YEOH if material == "yeoh" else FIT_OGDEN
    try:
        pv, _ = run_forward(
            material, R, t, work, tag,
            fit_path=fit, p0_mmhg=p0, p_final_mmhg=p_final, ne=ne,
        )
        return {
            "species": species,
            "material": material,
            **geom,
            "status": "OK",
            "P0_mmHg": p0,
            "p_final_mmHg": p_final,
            "V_max_uL": max(r["dV_uL"] for r in pv),
            "K_eff_early_mmHg_per_uL": k_eff_early(pv, p0),
            "n_pv_points": len(pv),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "species": species,
            "material": material,
            **geom,
            "status": f"FAIL: {exc}",
            "P0_mmHg": p0,
            "p_final_mmHg": p_final,
        }


def _load_buggy() -> dict:
    """Valores do piloto anterior (P0=16,9 p/ as duas espécies), se existirem."""
    if not PREV_RESULTS_JSON.is_file():
        return {}
    data = json.loads(PREV_RESULTS_JSON.read_text())
    return {
        (r["species"], r["material"]): r
        for r in data.get("results", [])
        if r.get("status") == "OK"
    }


def _load_claude() -> dict:
    """Cross-check independente (claude-wp1.5 corrigido), se existir."""
    if not CLAUDE_RESULTS_JSON.is_file():
        return {}
    data = json.loads(CLAUDE_RESULTS_JSON.read_text())
    return {
        (r["species"], r["material"]): r
        for r in data
        if r.get("status") == "OK"
    }


def write_results_md(out: Path, results: list[dict], meta: dict) -> None:
    buggy = _load_buggy()
    claude = _load_claude()
    lines = [
        "# WP1.5 — species pilot CORRIGIDO (P0 por espécie, ΔP=33,1 mmHg)\n",
        f"- **Ogden**: μ₁={meta['ogden']['mu1_MPa']:.4f} MPa, α₁={meta['ogden']['alpha1']:.4f}",
        f"- **Yeoh**: C10={meta['yeoh']['C10_MPa']:.4f}, C20={meta['yeoh']['C20_MPa']:.4f} MPa",
        "- **P0**: humano 16,9 mmHg / coelho 26,7 mmHg (Goldmann, ver docstring do script)",
        "- **Rampa**: P0 → P0+33,1 mmHg (humano 16,9→50,0; coelho 26,7→59,8)",
        f"- **Mesh**: octant spherical, ne={meta['ne']}",
        f"- **Convergence**: {meta['n_ok']}/{meta['n_total']} OK",
        "",
        "| species | material | P0 | p_final | V_max [µL] | K_eff early | V_max (bug P0=16,9) | K_eff (bug) |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in results:
        if r["status"] != "OK":
            lines.append(
                f"| {r['species']} | {r['material']} | {r['P0_mmHg']:.1f} | "
                f"{r['p_final_mmHg']:.1f} | FALHOU | — | — | — |"
            )
            continue
        old = buggy.get((r["species"], r["material"]), {})
        vo = f"{old['V_max_uL']:.2f}" if old else "—"
        ko = f"{old['K_eff_early_mmHg_per_uL']:.4f}" if old else "—"
        lines.append(
            f"| {r['species']} | {r['material']} | {r['P0_mmHg']:.1f} | {r['p_final_mmHg']:.1f} | "
            f"{r['V_max_uL']:.2f} | {r['K_eff_early_mmHg_per_uL']:.4f} | {vo} | {ko} |"
        )
    lines.append("")

    if claude:
        lines.extend([
            "## Cross-check vs claude-wp1.5 (implementação independente)",
            "",
            "| species | material | V_max aqui | V_max claude | ΔV% | K_eff aqui | K_eff claude | ΔK% |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ])
        for r in results:
            if r["status"] != "OK":
                continue
            c = claude.get((r["species"], r["material"]))
            if not c:
                continue
            dv = 100.0 * (r["V_max_uL"] - c["V_max_uL"]) / c["V_max_uL"]
            dk = 100.0 * (
                r["K_eff_early_mmHg_per_uL"] - c["K_eff_early_mmHg_per_uL"]
            ) / c["K_eff_early_mmHg_per_uL"]
            lines.append(
                f"| {r['species']} | {r['material']} | {r['V_max_uL']:.2f} | {c['V_max_uL']:.2f} | "
                f"{dv:+.3f}% | {r['K_eff_early_mmHg_per_uL']:.4f} | "
                f"{c['K_eff_early_mmHg_per_uL']:.4f} | {dk:+.3f}% |"
            )
        lines.append("")

    lines.extend([
        "## Notas",
        "",
        "- Controle interno: a rampa do **humano** é idêntica à do piloto anterior "
        "(16,9→50,0) — V_max/K_eff humanos devem reproduzir `output_pilot_species_p50/`.",
        "- O bug inflava o K_eff do coelho em ~1% (V=0 caía no 1º passo da rampa, "
        "~19 mmHg, não no basal real); a correção também estende a janela do coelho "
        "para a faixa fisiológica dele.",
        "- **Caveat que permanece**: material calibrado em dados humanos, aplicado ao "
        "coelho sem recalibração.",
        "- Simplified spherical octant only; full globe + cornea + AC pending.",
        "",
    ])
    (out / "RESULTS.md").write_text("\n".join(lines) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--materials", default="ogden,yeoh")
    ap.add_argument("--species", default="human,rabbit")
    ap.add_argument("--ne", type=int, default=8)
    ap.add_argument("--out", type=Path, default=WP15 / "output_pilot_species_p0corr")
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
            p0 = P0_MMHG_BY_SPECIES[sp]
            print(
                f"=== {sp} {material} R={SPECIES[sp]['R_mm']} t={SPECIES[sp]['t_mm']} "
                f"P0={p0} p_final={p0 + DELTA_P_MMHG:.1f} ==="
            )
            entry = run_one(material, sp, SPECIES[sp], work, args.ne)
            print(f"  -> {entry['status']}")
            results.append(entry)

    n_ok = sum(1 for r in results if r["status"] == "OK")
    payload = {
        "fits": {"ogden": str(FIT_OGDEN), "yeoh": str(FIT_YEOH)},
        "materials": {"ogden": ogden_p, "yeoh": yeoh_p},
        "P0_mmHg_by_species": P0_MMHG_BY_SPECIES,
        "delta_P_mmHg": DELTA_P_MMHG,
        "ne": args.ne,
        "note": "P0 corrigido por espécie (coelho 26,7 mmHg). Material segue calibrado em humano.",
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
