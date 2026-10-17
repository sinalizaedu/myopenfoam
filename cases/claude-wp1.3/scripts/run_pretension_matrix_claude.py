#!/usr/bin/env python3
"""claude-wp1.3 — pré-tensão (MULF Gee et al. 2010) para os 8 casos do WP1.2.

Terceiro braço independente (Sonnet), em paralelo a cases/wp1.3/ (Composer/
Cursor). NÃO edita nada lá — só CHAMA (subprocess) o script já validado
`run_wp13_mulf_gee.py` para cada uma das 8 combinações (4 alvos x 2
materiais) da matriz oficial do WP1.2 (cases/wp1.2/output_literature_p50_v2/).

Até agora (2026-09-25) o WP1.3 só tinha testado a divergência de
pré-tensão (Ogden endurece, Yeoh amolece) para o alvo Friedenwald
(wp1.3-ogden-new / wp1.3-yeoh-new, P_final=50). Este script estende a
MESMA checagem para os outros 3 alvos (Pallikaris, Silver, Agra), usando
os parâmetros finais e corretos do fechamento do WP1.2 (Agra já com a
correção do bound de alfa; Pallikaris na versão "sintética" que é a que
está na matriz oficial de 8 casos -- ver CROSS_VALIDATION_PALLIKARIS.md
para a versão digitalizada, fora do escopo desta matriz).

Pergunta que isso responde: a divergência Ogden-endurece/Yeoh-amolece
observada no Friedenwald é uma característica GERAL dos dois materiais
(aparece com qualquer calibração), ou é específica de como o Friedenwald
foi calibrado?

Uso:
    python3 scripts/run_pretension_matrix_claude.py                # todos os 8
    python3 scripts/run_pretension_matrix_claude.py --targets pallikaris,silver
    python3 scripts/run_pretension_matrix_claude.py --materials ogden
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent            # cases/claude-wp1.3/scripts
CLAUDE_WP13 = HERE.parent                          # cases/claude-wp1.3
WP12 = CLAUDE_WP13.parent / "wp1.2"                # cases/wp1.2 (leitura apenas)
WP13 = CLAUDE_WP13.parent / "wp1.3"                # cases/wp1.3 (leitura apenas)
MULF_SCRIPT = WP13 / "scripts" / "run_wp13_mulf_gee.py"

TARGETS = ("pallikaris", "silver", "agra", "friedenwald")
MATERIALS = ("ogden", "yeoh")

P_FINAL_DEFAULT = 50.0  # alinhado à decisão do WP1.2 (não 80)


def fit_path_for(target: str, material: str) -> Path:
    return WP12 / "output_literature_p50_v2" / f"{target}_{material}" / "fit_results.json"


def run_one(target: str, material: str, out_root: Path, p_final: float, ne: int) -> dict:
    fit = fit_path_for(target, material)
    if not fit.is_file():
        raise FileNotFoundError(f"fit_results.json não encontrado: {fit}")

    out = out_root / f"{target}_{material}"
    out.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        str(MULF_SCRIPT),
        "--fit", str(fit),
        "--material", material,
        "--ne", str(ne),
        "--p-final", str(p_final),
        "--out", str(out),
    ]
    print(f"\n{'='*70}\n{target}_{material}  (fit={fit})\n{'='*70}")
    proc = subprocess.run(cmd, capture_output=False)
    result_path = out / "pretension_mulf_gee.json"
    if not result_path.is_file():
        return {
            "target": target,
            "material": material,
            "status": "FAILED",
            "returncode": proc.returncode,
        }
    data = json.loads(result_path.read_text())
    return {
        "target": target,
        "material": material,
        "status": "OK" if proc.returncode == 0 else "MULF_NOT_CLEAN",
        "returncode": proc.returncode,
        "mulf_converged": data.get("mulf", {}).get("converged"),
        "verify_error_mm": data.get("verify_error_mm"),
        "K_at_V0": data.get("K_local_at_V0_mmHg_per_uL"),
        "K_at_Vref": data.get("K_local_at_ref_mmHg_per_uL"),
        "V_ref_uL": data.get("V_ref_default_uL"),
        "relative_change_pct": data.get("relative_change_pct"),
    }


def write_summary(out_root: Path, results: list[dict]) -> None:
    lines = [
        "# claude-wp1.3 — pré-tensão (MULF Gee 2010), 8 casos do WP1.2\n",
        "Terceiro braço independente (Sonnet). P_final=50 mmHg, mesma matriz",
        "de fits do WP1.2 (`cases/wp1.2/output_literature_p50_v2/`).\n",
        "| alvo | material | MULF | K(V≈0) | K(V_ref) | V_ref [µL] | Δ% |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for r in results:
        if r["status"] == "FAILED":
            lines.append(f"| {r['target']} | {r['material']} | **FALHOU** | — | — | — | — |")
            continue
        conv = "OK" if r["mulf_converged"] else "NÃO CONVERGIU"
        lines.append(
            f"| {r['target']} | {r['material']} | {conv} | "
            f"{r['K_at_V0']:.4f} | {r['K_at_Vref']:.4f} | {r['V_ref_uL']:.1f} | "
            f"{r['relative_change_pct']:+.2f}% |"
        )
    lines.append("")
    (out_root / "PRETENSION_MATRIX_SUMMARY_CLAUDE.md").write_text("\n".join(lines))
    (out_root / "pretension_matrix_results.json").write_text(json.dumps(results, indent=2))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--targets", default=",".join(TARGETS))
    ap.add_argument("--materials", default=",".join(MATERIALS))
    ap.add_argument("--p-final", type=float, default=P_FINAL_DEFAULT)
    ap.add_argument("--ne", type=int, default=8)
    ap.add_argument("--out", type=Path, default=CLAUDE_WP13 / "output_pretension_8cases")
    args = ap.parse_args()

    targets = [t.strip() for t in args.targets.split(",") if t.strip()]
    materials = [m.strip() for m in args.materials.split(",") if m.strip()]
    args.out.mkdir(parents=True, exist_ok=True)

    results = []
    for target in targets:
        for material in materials:
            results.append(run_one(target, material, args.out, args.p_final, args.ne))

    write_summary(args.out, results)
    print(f"\nDone — see {args.out / 'PRETENSION_MATRIX_SUMMARY_CLAUDE.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
