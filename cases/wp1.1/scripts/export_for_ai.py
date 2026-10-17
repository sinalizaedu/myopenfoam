#!/usr/bin/env python3
"""Bundle wp1.1 results into one markdown file for copy-paste to another AI."""
from __future__ import annotations

import json
from pathlib import Path

WP1_1 = Path(__file__).resolve().parent.parent
OUT = WP1_1 / "output_wp1.1"
MESH = OUT / "mesh_independence"


def read(path: Path) -> str:
    return path.read_text() if path.is_file() else f"*(missing: {path.name})*"


def summary_table() -> str:
    sj = OUT / "summary.json"
    if not sj.is_file():
        return "*(summary.json missing)*"
    data = json.loads(sj.read_text())
    lines = [
        "| espécie | elem | K_FEA | K_analítico | erro (%) | ΔV (µL) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in data.get("cases", []):
        lines.append(
            f"| {r['case']} | {r['n_elements']} | {r['K_FEA_mmHg_per_uL']:.6f} | "
            f"{r['K_analytic_mmHg_per_uL']:.6f} | {r['error_pct']:.2f} | {r['dV_uL']:.6f} |"
        )
    return "\n".join(lines)


def main() -> int:
    parts = [
        "# wp1.1 — pacote de resultados (CalculiX S8)\n",
        "Copiar este arquivo inteiro para a outra IA.\n",
        "---\n",
        "## Parâmetros comuns\n",
        "| parâmetro | valor |",
        "|---|---|",
        "| elemento | S8 (casca 2ª ordem) |",
        "| E | 3.0 MPa |",
        "| ν | 0.47 |",
        "| ΔP | 1.0 mmHg |",
        "| QoI | K = ΔP/ΔV via ∫ u·n dA (Gauss) |",
        "| malha recomendada | ne/face = 24 → 3456 elementos/esfera |",
        "| critério independência | ε_i < 1% por dois refinamentos consecutivos |",
        "| critério verificação | |K_FEA − K_analítico|/K_analítico < 2% |",
        "\n---\n",
        "## HUMANO — independência de malha\n",
        read(MESH / "human" / "MESH_INDEPENDENCE.md"),
        "\n---\n",
        "## HUMANO — verificação vs analítico (ne=24)\n",
        read(OUT / "RESULTS_human.md"),
        "\n---\n",
        "## COELHO — independência de malha\n",
        read(MESH / "rabbit" / "MESH_INDEPENDENCE.md"),
        "\n---\n",
        "## COELHO — verificação vs analítico (ne=24)\n",
        read(OUT / "RESULTS_rabbit.md"),
        "\n---\n",
        "## Tabela resumo (malha final ne=24, 3456 elem)\n",
        summary_table(),
    ]
    export = OUT / "EXPORT_FOR_AI.md"
    export.write_text("\n".join(parts))
    print(export.read_text())
    print(f"\nWrote {export}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
