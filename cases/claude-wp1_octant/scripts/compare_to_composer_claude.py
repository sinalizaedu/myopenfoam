#!/usr/bin/env python3
"""claude-wp1_octant -- compara a trilha Yeoh (claude, multi-start) com o Composer.

Le output/wp1.{1,2,3}-yeoh/*.json deste caso e compara com os numeros de
referencia do Composer (cases/wp1_octant/output/MATERIAL_MATRIX_SUMMARY.md,
lidos diretamente por mim em 22/09/2026 -- hardcoded aqui, nao editados no
arquivo original). Gera output/COMPARE_TO_COMPOSER.md com a resposta direta
"bateu ou nao bateu" dentro de uma tolerancia, para a Bruna nao precisar
esperar uma rodada de chat so pra saber se os numeros conferem.

NAO EDITA nada existente -- so LE (json.loads) os outputs deste caso
(claude-wp1_octant/output/), que sao arquivos novos gerados por scripts
proprios, e usa constantes hardcoded como referencia do Composer.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "output"

# Referencia: cases/wp1_octant/output/MATERIAL_MATRIX_SUMMARY.md (lido em 22/09/2026)
COMPOSER_REF = {
    "wp1.2": {
        "C10_MPa": 4.363931624633122,
        "C20_MPa": 4.994979920594,
        "R2": 0.938273,
        "max_residual_mmHg": 7.90,
    },
    "wp1.3": {
        "K_local_at_V0": 1.1930,
        "K_local_at_Vref": 1.3789,
        "relative_change_pct": 15.59,
    },
}

# Tolerancias -- "bate" se dentro disso. Yeoh e um ajuste bem-condicionado
# (poucos minimos esperados), entao uso tolerancia apertada para o fit em si
# e mais frouxa para grandezas derivadas (K, pretensao) que amplificam erro.
TOL_PCT_FIT = 2.0       # C10, C20, R2
TOL_PCT_DERIVED = 8.0   # K_FEA, dP/dV (mais sensivel a ne, malha, etc.)


def pct_diff(a: float, b: float) -> float:
    if b == 0:
        return float("nan")
    return 100.0 * (a - b) / b


def verdict(diff_pct: float, tol: float) -> str:
    if diff_pct != diff_pct:  # nan
        return "N/A"
    return "BATE" if abs(diff_pct) <= tol else "DIVERGE"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out-dir", type=Path, default=OUT)
    args = ap.parse_args()

    lines = [
        "# claude-wp1_octant -- comparacao Yeoh (claude, multi-start) vs Composer (single-start)\n",
        "Gerado automaticamente lendo os JSONs deste caso e comparando com os",
        "numeros do Composer (`cases/wp1_octant/output/MATERIAL_MATRIX_SUMMARY.md`).",
        "",
    ]

    any_missing = False

    # WP1.2 -- fit
    fit_path = args.out_dir / "wp1.2-yeoh" / "fit_results.json"
    if fit_path.is_file():
        data = json.loads(fit_path.read_text())
        sel = data.get("selected")
        p = sel["params"]
        q = sel["quality"]
        ref = COMPOSER_REF["wp1.2"]
        rows = [
            ("C10_MPa", p["C10_MPa"], ref["C10_MPa"], TOL_PCT_FIT),
            ("C20_MPa", p["C20_MPa"], ref["C20_MPa"], TOL_PCT_FIT),
            ("R2", q["R2"], ref["R2"], TOL_PCT_FIT),
            ("max_residual_mmHg", q["max_residual_mmHg"], ref["max_residual_mmHg"], TOL_PCT_DERIVED),
        ]
        lines += ["## WP1.2 -- ajuste Yeoh vs Pallikaris\n", "| grandeza | claude (multi-start, melhor) | composer (single-start) | diff % | veredito |",
                  "|---|---:|---:|---:|---|"]
        for name, mine, comp, tol in rows:
            d = pct_diff(mine, comp)
            lines.append(f"| {name} | {mine:.4f} | {comp:.4f} | {d:+.2f}% | {verdict(d, tol)} |")
        ranked = data.get("ranked_by_cost", [])
        if ranked:
            lines.append("")
            lines.append(f"- {len(ranked)} starts validos rodados; menor custo = {ranked[0]['cost']:.2f}.")
            close_to_composer = [
                r for r in ranked
                if abs(pct_diff(r["C10_final"], ref["C10_MPa"])) < 15 and abs(pct_diff(r["C20_final"], ref["C20_MPa"])) < 15
            ]
            lines.append(
                f"- {len(close_to_composer)}/{len(ranked)} starts convergiram para perto do "
                f"resultado do Composer (C10~{ref['C10_MPa']:.2f}, C20~{ref['C20_MPa']:.2f})."
            )
        lines.append("")
    else:
        any_missing = True
        lines += ["## WP1.2 -- ainda nao rodado (fit_results.json ausente)\n"]

    # WP1.3 -- pretensao
    p3_path = args.out_dir / "wp1.3-yeoh" / "pretension_study.json"
    if p3_path.is_file():
        data = json.loads(p3_path.read_text())
        fc = data["fit_curve_method"]
        ref = COMPOSER_REF["wp1.3"]
        rows = [
            ("K_local_at_V0", fc["K_local_at_V0"], ref["K_local_at_V0"]),
            ("K_local_at_Vref", fc["K_local_at_Vref"], ref["K_local_at_Vref"]),
            ("relative_change_pct", fc["relative_change_pct"], ref["relative_change_pct"]),
        ]
        lines += ["## WP1.3 -- pretensao (metodo curva-do-ajuste, comparavel ao Composer)\n",
                  "| grandeza | claude | composer | diff % | veredito |",
                  "|---|---:|---:|---:|---|"]
        for name, mine, comp in rows:
            d = pct_diff(mine, comp)
            lines.append(f"| {name} | {mine:.4f} | {comp:.4f} | {d:+.2f}% | {verdict(d, TOL_PCT_DERIVED)} |")
        dfm = data["dense_forward_method"]
        lines.append("")
        lines.append(
            f"- Curva densa forward (novo, so aqui): dP/dV@V0={dfm['K_local_at_V0']:.4f}, "
            f"variacao={dfm['relative_change_pct']:+.2f}% -- comparar com o -41,4% "
            "\"artefato de incremento\" que o Composer/Cursor reportou no E5 dele."
        )
        lines.append("")
    else:
        any_missing = True
        lines += ["## WP1.3 -- ainda nao rodado (pretension_study.json ausente)\n"]

    lines.append("---")
    if any_missing:
        lines.append("**Rode `./Allrun --only yeoh` primeiro para preencher as secoes faltando.**")
    else:
        lines.append(
            "Leitura: `BATE` = dentro da tolerancia (2% para C10/C20/R2, 8% para grandezas "
            "derivadas como K e dP/dV, que amplificam qualquer diferenca de malha/ne ou "
            "escolha de cluster no multi-start). `DIVERGE` fora disso merece olhar de perto "
            "-- pode ser malha (ne diferente), escolha de cluster, ou um bug real."
        )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "COMPARE_TO_COMPOSER.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
