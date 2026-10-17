#!/usr/bin/env python3
"""claude-wp1_octant -- orquestrador (equivalente independente ao run_material_matrix.py).

Roda, para cada material (ogden, yeoh):
  1. fit_ogden_multistart_claude.py / fit_yeoh_multistart_claude.py  (WP1.2, multi-start)
  2. wp11_hyperelastic_k_claude.py   (WP1.1, K hiperelastico + checagem de malha ne=6 vs 8)
  3. wp13_pretension_claude.py       (WP1.3, curva-do-ajuste vs curva-densa-forward)

Custo estimado: bem mais caro que o Composer (multi-start = varios fits em vez
de um), ordem de 2-3h total no Docker dependendo da maquina. Rode em background
se possivel (nohup / tmux) -- nao precisa terminar de uma vez, cada etapa grava
seu proprio fit_results.json/RESULTS.md incrementalmente.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "output"


def run(cmd: list[str], label: str) -> None:
    print(f"\n{'='*60}\n{label}\n{'='*60}")
    subprocess.run(cmd, check=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ne-fit", type=int, default=8, help="malha do ajuste WP1.2 (Composer usou 8)")
    ap.add_argument("--wp11-ne-levels", type=int, nargs="+", default=[6, 8])
    ap.add_argument("--only", choices=["ogden", "yeoh", ""], default="")
    ap.add_argument("--skip-wp12", action="store_true")
    ap.add_argument("--skip-wp11", action="store_true")
    ap.add_argument("--skip-wp13", action="store_true")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    materials = [args.only] if args.only else ["ogden", "yeoh"]

    for mat in materials:
        o12 = OUT / f"wp1.2-{mat}"
        o11 = OUT / f"wp1.1-{mat}"
        o13 = OUT / f"wp1.3-{mat}"

        if not args.skip_wp12:
            if mat == "ogden":
                run(
                    [sys.executable, str(HERE / "fit_ogden_multistart_claude.py"), "--ne", str(args.ne_fit), "--out", str(o12)],
                    f"WP1.2 {mat} multi-start",
                )
            else:
                run(
                    [sys.executable, str(HERE / "fit_yeoh_multistart_claude.py"), "--ne", str(args.ne_fit), "--out", str(o12)],
                    f"WP1.2 {mat} multi-start",
                )

        fit_json = o12 / "fit_results.json"
        if not fit_json.is_file():
            print(f"Faltando {fit_json}, abortando este material.")
            continue

        if not args.skip_wp11:
            run(
                [
                    sys.executable, str(HERE / "wp11_hyperelastic_k_claude.py"),
                    "--material", mat, "--fit", str(fit_json),
                    "--ne-levels", *[str(n) for n in args.wp11_ne_levels],
                    "--out", str(o11),
                ],
                f"WP1.1 {mat} K hiperelastico (malha checada)",
            )

        if not args.skip_wp13:
            run(
                [
                    sys.executable, str(HERE / "wp13_pretension_claude.py"),
                    "--fit", str(fit_json), "--material", mat, "--out", str(o13),
                ],
                f"WP1.3 {mat} pretensao (2 metodos)",
            )

    if "yeoh" in materials:
        run(
            [sys.executable, str(HERE / "compare_to_composer_claude.py"), "--out-dir", str(OUT)],
            "Comparacao automatica Yeoh (claude) vs Composer",
        )

    summary = OUT / "PIPELINE_DONE_claude.txt"
    summary.write_text(
        "claude-wp1_octant pipeline concluido.\n"
        + "\n".join(f"  {mat}: {OUT}/wp1.{{1,2,3}}-{mat}/" for mat in materials)
        + ("\n  comparacao: " + str(OUT / "COMPARE_TO_COMPOSER.md") if "yeoh" in materials else "")
    )
    print(f"\nConcluido. Ver {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
