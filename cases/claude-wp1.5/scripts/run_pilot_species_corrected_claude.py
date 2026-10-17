#!/usr/bin/env python3
"""claude-wp1.5 CORRIGIDO — piloto de especie (humano + coelho), Ogden + Yeoh,
com P0 (basal fisiologico) especifico por especie.

BUG no script original (run_pilot_species_claude.py, e nos modulos que ele
chama: ogden_forward_run.py / cases/wp1.2/scripts/yeoh_forward_run.py):
P0_MMHG=16.9 (basal HUMANO) e usado tambem para o coelho -- tanto para
definir a geometria de referencia sem tensao (rampa de pressao comeca em
16.9, nao no basal real do coelho) quanto para o V=0 de extract_pv().

Basais corretos, derivados do equilibrio de Goldmann com parametros
ancorados na literatura (relatorio WP0 em LaTeX, secao "Producao
trabecular e uveoescleral"; ver tambem cases/claude-wp4/claude_dose_isquemica.py):

    humano:            P0 = 16.9 mmHg  (Goel et al. 2010)
    coelho anestesiado: P0 = 26.7 mmHg  (Kiel et al. 2011/2015; Fourman & Garner 1989)

Janela de pressao: o piloto original usa p_final=50 mmHg fixo (delta_P=
50-16.9=33.1 mmHg a partir do basal humano). Para manter a MESMA amplitude
de estimulo (delta_P) nas duas especies -- e nao amplificar ainda mais a
diferenca de complacencia so por causa da janela de pressao absoluta --
este script usa o MESMO delta_P=33.1 mmHg a partir do basal de cada
especie:

    humano: 16.9 -> 50.0 mmHg   (igual ao original)
    coelho: 26.7 -> 59.8 mmHg   (novo)

Isso e uma escolha de desenho, nao uma verdade unica -- ver
CORRECAO_P0_ESPECIE_CLAUDE.md para a discussao e alternativas.

CAVEAT que PERMANECE (ja estava no fechamento original, nao e resolvido
aqui): o material (fit Ogden/Yeoh do Friedenwald) continua calibrado em
DADOS HUMANOS -- nao ha recalibracao para coelho. Este script corrige
APENAS o P0/janela de pressao por especie, nao a lacuna de material.

Requer CalculiX (nao roda no ambiente do Claude) -- ver Allrun_corrected.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent            # cases/claude-wp1.5/scripts
CLAUDE_WP15 = HERE.parent                          # cases/claude-wp1.5
WP12 = CLAUDE_WP15.parent / "wp1.2"                 # leitura apenas (Composer)

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(WP12 / "scripts"))

from yeoh_forward_run_v2_claude import run_yeoh_forward_v2  # noqa: E402
from ogden_forward_run_v2_claude import run_ogden_forward_v2  # noqa: E402

SPECIES = {
    "human": {"R_mm": 12.0, "t_mm": 0.5},
    "rabbit": {"R_mm": 7.6, "t_mm": 0.33},
}

# P0 especifico por especie (ver docstring acima / relatorio WP0)
P0_MMHG_BY_SPECIES = {
    "human": 16.9,
    "rabbit": 26.7,
}

# Mesmo delta_P (33.1 mmHg) do piloto original (50.0 - 16.9), aplicado a
# partir do P0 de cada especie -- ver docstring.
DELTA_P_MMHG = 50.0 - 16.9

FIT_PATHS = {
    "ogden": WP12 / "output_literature_p50_v2" / "friedenwald_ogden" / "fit_results.json",
    "yeoh": WP12 / "output_literature_p50_v2" / "friedenwald_yeoh" / "fit_results.json",
}

# Resultados do piloto ORIGINAL (com o bug), para comparacao direta no
# relatorio de saida -- copiados de output_pilot_species_claude/pilot_species_results.json
RESULTADOS_ORIGINAIS_COM_BUG = {
    ("human", "ogden"): {"V_max_uL": 115.27191867182454, "K_eff_early_mmHg_per_uL": 0.2998562140220139},
    ("rabbit", "ogden"): {"V_max_uL": 28.03752453622102, "K_eff_early_mmHg_per_uL": 1.2317839035142257},
    ("human", "yeoh"): {"V_max_uL": 111.49469110343625, "K_eff_early_mmHg_per_uL": 0.39246187442797514},
    ("rabbit", "yeoh"): {"V_max_uL": 27.13567903508978, "K_eff_early_mmHg_per_uL": 1.6119198225172953},
}


def run_one(material: str, species: str, geom: dict, work: Path, ne: int) -> dict:
    R, t = geom["R_mm"], geom["t_mm"]
    tag = f"{species}_{material}_v2"
    p0 = P0_MMHG_BY_SPECIES[species]
    p_final = p0 + DELTA_P_MMHG
    try:
        if material == "yeoh":
            pv, meta = run_yeoh_forward_v2(
                R, t, work, tag, fit_path=FIT_PATHS["yeoh"],
                p0_mmhg=p0, p_final_mmhg=p_final, ne=ne,
            )
        else:
            pv, meta = run_ogden_forward_v2(
                R, t, work, tag, fit_path=FIT_PATHS["ogden"],
                p0_mmhg=p0, p_final_mmhg=p_final, ne=ne,
            )
        v = [r["dV_uL"] for r in pv if r["dV_uL"] > 0]
        p = [r["p_mmhg"] for r in pv if r["dV_uL"] > 0]
        k_eff = (p[0] - p0) / v[0] if v and v[0] > 1e-9 else float("nan")
        entry = {
            "species": species, "material": material, **geom, "status": "OK",
            "P0_mmHg": p0, "p_final_mmHg": p_final,
            "V_max_uL": max(r["dV_uL"] for r in pv),
            "K_eff_early_mmHg_per_uL": k_eff,
        }
    except Exception as exc:  # noqa: BLE001
        entry = {"species": species, "material": material, **geom, "status": f"FAIL: {exc}",
                  "P0_mmHg": p0, "p_final_mmHg": p_final}

    old = RESULTADOS_ORIGINAIS_COM_BUG.get((species, material))
    if old:
        entry["V_max_uL_ORIGINAL_COM_BUG"] = old["V_max_uL"]
        entry["K_eff_ORIGINAL_COM_BUG"] = old["K_eff_early_mmHg_per_uL"]
    return entry


def write_summary(out: Path, results: list[dict]) -> None:
    lines = [
        "# claude-wp1.5 CORRIGIDO -- P0 especifico por especie",
        "",
        "| especie | material | P0 usado | p_final | V_max [uL] | K_eff | "
        "V_max ORIGINAL (bug) | K_eff ORIGINAL (bug) |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in results:
        if r["status"] != "OK":
            lines.append(f"| {r['species']} | {r['material']} | {r.get('P0_mmHg','—')} | "
                         f"{r.get('p_final_mmHg','—')} | FALHOU | — | — | — |")
            continue
        lines.append(
            f"| {r['species']} | {r['material']} | {r['P0_mmHg']:.1f} | {r['p_final_mmHg']:.1f} | "
            f"{r['V_max_uL']:.2f} | {r['K_eff_early_mmHg_per_uL']:.4f} | "
            f"{r.get('V_max_uL_ORIGINAL_COM_BUG', float('nan')):.2f} | "
            f"{r.get('K_eff_ORIGINAL_COM_BUG', float('nan')):.4f} |"
        )
    lines.append("")
    (out / "RESULTS_CORRIGIDO_CLAUDE.md").write_text("\n".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--materials", default="ogden,yeoh")
    ap.add_argument("--species", default="human,rabbit")
    ap.add_argument("--ne", type=int, default=8)
    ap.add_argument("--out", type=Path, default=CLAUDE_WP15 / "output_pilot_species_corrected_claude")
    args = ap.parse_args()

    materials = [m.strip() for m in args.materials.split(",") if m.strip()]
    species = [s.strip() for s in args.species.split(",") if s.strip()]
    args.out.mkdir(parents=True, exist_ok=True)
    work = args.out / "ccx_runs"

    results = []
    for material in materials:
        for sp in species:
            p0 = P0_MMHG_BY_SPECIES[sp]
            p_final = p0 + DELTA_P_MMHG
            print(f"=== {sp} {material} R={SPECIES[sp]['R_mm']} t={SPECIES[sp]['t_mm']} "
                  f"P0={p0} p_final={p_final:.1f} ===")
            entry = run_one(material, sp, SPECIES[sp], work, args.ne)
            print(f"  -> {entry['status']}")
            results.append(entry)

    (args.out / "pilot_species_corrected_results.json").write_text(json.dumps(results, indent=2))
    write_summary(args.out, results)
    n_ok = sum(1 for r in results if r["status"] == "OK")
    print(f"\nDone: {n_ok}/{len(results)} OK -- see {args.out / 'RESULTS_CORRIGIDO_CLAUDE.md'}")
    return 0 if n_ok == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
