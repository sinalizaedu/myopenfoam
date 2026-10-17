#!/usr/bin/env python3
"""claude-wp1.3 — pré-tensão, 6 casos, com relaxação MULF CORRIGIDA.

Roda run_wp13_mulf_gee_fixed_claude.py (relaxação corrigida, ver seu
docstring e o de mulf_gee_fixed_relax_claude.py) nos mesmos 6 casos
(3 alvos x 2 materiais) já rodados com a fórmula original, para comparar
Δ% de rigidez antes/depois da correção.

Uso:
    python3 scripts/run_pretension_matrix_fixed_claude.py
    # so recalcular Pallikaris com o ajuste digitalizado (Fig.2), sem
    # tocar nos outros 2 alvos nem sobrescrever o resultado antigo
    # (formula) que fica em output_pretension_8cases_fixed_relax/:
    python3 scripts/run_pretension_matrix_fixed_claude.py --targets pallikaris \
        --out output_pretension_8cases_fixed_relax_digitized

ACHADO/CORREÇÃO (sessão de 27/09): a Bruna removeu o alvo "Pallikaris
(fórmula analítica)" da Tabela wp1.2 — o único "Pallikaris" que resta é o
ajuste dos pontos digitalizados da Fig. 2 do artigo
(`cases/wp1.2/output_literature_p50_digitized/pallikaris_*`,
μ1=5,367/α1=0,535), não mais o ajuste da fórmula
(`output_literature_p50_v2/pallikaris_*`, μ1=4,243/α1=0,5, que ERA o
usado aqui até esta correção). fit_path_for() agora aponta "pallikaris"
para o dataset digitalizado -- os outros 2 alvos (silver/friedenwald)
não têm variante digitalizada, continuam em output_literature_p50_v2.
Os números de pré-tensão para Pallikaris PRECISAM ser recalculados (não
reaproveite os antigos, calculados com os parâmetros da fórmula) -- ver
--out abaixo, que por padrão grava numa pasta nova para não sobrescrever
o resultado antigo (histórico, baseado na fórmula, mantido para registro).
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
FIXED_SCRIPT = HERE / "run_wp13_mulf_gee_fixed_claude.py"
ORIGINAL_SUMMARY = CLAUDE_WP13 / "output_pretension_8cases" / "pretension_matrix_results.json"

# Agra foi excluído da tese (sessão de 28/09): não entra na Tabela wp1.2 nem
# na de pré-tensão. Os diretórios agra_* antigos em output_pretension_8cases*/
# ficam como histórico e não devem ser citados.
TARGETS = ("pallikaris", "silver", "friedenwald")
MATERIALS = ("ogden", "yeoh")
P_FINAL_DEFAULT = 50.0


# Alvos que têm uma variante "digitalizado" (pontos da figura original,
# em vez da fórmula analítica do artigo) -- ver docstring do módulo.
# Único caso hoje: Pallikaris. Se a Bruna digitalizar outra figura no
# futuro, adicione o alvo aqui.
_ALVOS_COM_VARIANTE_DIGITALIZADA = {"pallikaris": "output_literature_p50_digitized"}


def fit_path_for(target: str, material: str) -> Path:
    dataset = _ALVOS_COM_VARIANTE_DIGITALIZADA.get(target, "output_literature_p50_v2")
    return WP12 / dataset / f"{target}_{material}" / "fit_results.json"


def run_one(target: str, material: str, out_root: Path, p_final: float, ne: int) -> dict:
    fit = fit_path_for(target, material)
    if not fit.is_file():
        raise FileNotFoundError(f"fit_results.json não encontrado: {fit}")

    out = out_root / f"{target}_{material}"
    out.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, str(FIXED_SCRIPT),
        "--fit", str(fit), "--material", material,
        "--ne", str(ne), "--p-final", str(p_final), "--out", str(out),
    ]
    print(f"\n{'='*70}\n{target}_{material} (RELAXAÇÃO CORRIGIDA)  (fit={fit})\n{'='*70}")
    proc = subprocess.run(cmd, capture_output=False)
    result_path = out / "pretension_mulf_gee_fixed.json"
    if not result_path.is_file():
        return {"target": target, "material": material, "status": "FAILED", "returncode": proc.returncode}
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
    original = {}
    if ORIGINAL_SUMMARY.is_file():
        for r in json.loads(ORIGINAL_SUMMARY.read_text()):
            original[(r["target"], r["material"])] = r.get("relative_change_pct")

    lines = [
        "# claude-wp1.3 — pré-tensão, 6 casos, RELAXAÇÃO CORRIGIDA vs. original\n",
        "Compara Δ% de rigidez local (mesma métrica) entre a fórmula de",
        "relaxação original de `mulf_gee.py` (bug: mistura com X_obs fixo) e a",
        "corrigida (mistura com X_ref da iteração anterior). Ver",
        "`MULF_RELAXATION_BUG_NOTE_CLAUDE.md` para a derivação do bug.\n",
        "| alvo | material | Δ% original | Δ% corrigido | diferença (pp) | MULF (corrigido) | verify_err [mm] |",
        "|---|---|---:|---:|---:|---|---:|",
    ]
    tem_pallikaris = any(r["target"] == "pallikaris" for r in results)
    for r in results:
        if r["status"] == "FAILED":
            lines.append(f"| {r['target']} | {r['material']} | — | **FALHOU** | — | — | — |")
            continue
        orig = original.get((r["target"], r["material"]))
        orig_s = f"{orig:+.2f}%" if orig is not None else "n/d"
        diff = (r["relative_change_pct"] - orig) if orig is not None else float("nan")
        conv = "OK" if r["mulf_converged"] else "NÃO CONVERGIU"
        alvo_label = r["target"] + ("*" if r["target"] == "pallikaris" else "")
        lines.append(
            f"| {alvo_label} | {r['material']} | {orig_s} | "
            f"{r['relative_change_pct']:+.2f}% | {diff:+.2f} | {conv} | {r['verify_error_mm']:.4e} |"
        )
    if tem_pallikaris:
        lines.append("")
        lines.append(
            "*Pallikaris: a coluna \"Δ% original\" veio do ajuste da FÓRMULA "
            "(μ1=4,24), que não é mais o alvo \"Pallikaris\" na Tabela wp1.2 "
            "(agora é o ajuste dos pontos digitalizados da Fig. 2, μ1=5,37). "
            "A diferença aqui mistura DOIS efeitos -- a correção da relaxação "
            "MULF e a troca do dataset de ajuste -- não isole a segunda sem "
            "rodar também a versão antiga (fórmula) com a relaxação já "
            "corrigida (já existe em output_pretension_8cases_fixed_relax/)."
        )
    lines.append("")
    (out_root / "PRETENSION_MATRIX_SUMMARY_FIXED_CLAUDE.md").write_text("\n".join(lines))
    (out_root / "pretension_matrix_results_fixed.json").write_text(json.dumps(results, indent=2))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--targets", default=",".join(TARGETS))
    ap.add_argument("--materials", default=",".join(MATERIALS))
    ap.add_argument("--p-final", type=float, default=P_FINAL_DEFAULT)
    ap.add_argument("--ne", type=int, default=8)
    ap.add_argument("--out", type=Path, default=CLAUDE_WP13 / "output_pretension_8cases_fixed_relax")
    args = ap.parse_args()

    targets = [t.strip() for t in args.targets.split(",") if t.strip()]
    materials = [m.strip() for m in args.materials.split(",") if m.strip()]
    args.out.mkdir(parents=True, exist_ok=True)

    results = []
    for target in targets:
        for material in materials:
            results.append(run_one(target, material, args.out, args.p_final, args.ne))

    write_summary(args.out, results)
    print(f"\nDone — see {args.out / 'PRETENSION_MATRIX_SUMMARY_FIXED_CLAUDE.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
