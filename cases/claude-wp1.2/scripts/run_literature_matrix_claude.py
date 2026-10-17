#!/usr/bin/env python3
"""WP1.2 (Claude, independente) — 8 casos: 4 alvos P(V) x 2 materiais.

Terceiro braco independente (Sonnet), em paralelo a cases/wp1.2/ (Composer/
Cursor) e a cases/claude-wp1.2/scripts/fit_pallikaris_multistart_claude.py
(meu proprio trabalho anterior, so-Pallikaris/so-Ogden). NAO edita nada em
cases/wp1.2/ -- so importa (leitura) Geometry, fit_ogden1, PallikarisForward
de fit_pallikaris.py e fit_yeoh2, PallikarisYeohForward de run_e3_e1b.py, ja
validados pelo Composer.

Alvos (ver literature_targets_claude.py para a justificativa de cada v_max):
  1. pallikaris   -- P0=16.9, Kf=0.0126 (exponencial), truncado em V=35 uL
  2. silver       -- Silver & Geyer (2000), coef. exatos, truncado em V=38 uL
  3. agra         -- Agra et al. (2023), bancada hidraulica, V<=40 uL
  4. friedenwald  -- Friedenwald RECALIBRADO do WP0 (Kf=0.00581, contra
                     Knecht 2009) -- o alvo que a propria usuaria ja validou
                     no WP0, V ate 50 uL (padrao clinico de IVI)

Materiais: ogden (Ogden N=1) e yeoh (Yeoh-2). Total 4x2 = 8 casos.

P_final = 50 mmHg (teto da rampa de pressao da FEA), conforme pedido da
usuaria -- e ja o default em fit_pallikaris.DP_FEA_FINAL (o Composer tambem
ja havia migrado para 50 mmHg).

Uso:
    python3 scripts/run_literature_matrix_claude.py                  # todos os 8
    python3 scripts/run_literature_matrix_claude.py --targets pallikaris,friedenwald
    python3 scripts/run_literature_matrix_claude.py --materials ogden
    python3 scripts/run_literature_matrix_claude.py --max-nfev 15    # mais rapido/grosseiro
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

HERE = Path(__file__).resolve().parent          # cases/claude-wp1.2/scripts
CLAUDE_WP12 = HERE.parent                        # cases/claude-wp1.2
WP12 = CLAUDE_WP12.parent / "wp1.2"              # cases/wp1.2  (leitura apenas)

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(WP12 / "scripts"))

from fit_pallikaris import DP_FEA_FINAL, Geometry, P0_MMHG, fit_ogden1, PallikarisForward  # noqa: E402
from run_e3_e1b import fit_yeoh2, PallikarisYeohForward  # noqa: E402

import literature_targets_claude as lt  # noqa: E402
from literature_targets_claude import generate_target, TARGETS, V_MAX_SAFE  # noqa: E402

MATERIALS = ("ogden", "yeoh")


def run_one(
    target: str,
    material: str,
    out: Path,
    *,
    ne: int,
    max_nfev: int,
    p_final: float,
    R: float,
    t: float,
) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    csv_path = out / f"{target}_target.csv"
    exp = generate_target(target, csv_path)

    if material == "ogden":
        geom = Geometry(R_mm=R, t_mm=t, source=f"{target}_claude_wp1.2")
        work = out / "ccx_runs" / "ogden1"
        forward = PallikarisForward(geom, work, ne=ne, dp_fea_final=p_final)
        result = fit_ogden1(forward, exp, max_nfev=max_nfev)
        geom_out = forward.geom
    elif material == "yeoh":
        work = out / "ccx_runs"
        forward = PallikarisYeohForward(work, ne=ne, p_final=p_final)
        forward.geom = Geometry(R_mm=R, t_mm=t, source=f"{target}_claude_wp1.2")
        result = fit_yeoh2(forward, exp, max_nfev=max_nfev)
        geom_out = forward.geom
    else:
        raise ValueError(material)

    payload = {
        "target": target,
        "material": material,
        "geometry": asdict(geom_out),
        "fea_ramp": {"P_final_mmHg_abs": p_final, "P0_mmHg": P0_MMHG},
        "target_v_max_uL": lt.V_MAX_SAFE.get(target, 50.0),
        "pallikaris_mode": lt.PALLIKARIS_TARGET_MODE if target == "pallikaris" else None,
        "mesh": {"ne": ne, "bc_mode": "symmetry_octant"},
        "selected": result,
    }
    (out / "fit_results.json").write_text(json.dumps(payload, indent=2))

    q = result["quality"]
    p = result["params"]
    lines = [
        f"# claude-wp1.2 — {target} x {material} (P_final={p_final} mmHg)\n",
        f"- **Target**: {target} (v_max={V_MAX_SAFE.get(target, 50.0)} uL)",
        f"- **Material**: {material}",
        f"- **Geometry**: R={R} mm, t={t} mm",
        f"- **Parameters**: {json.dumps(p)}",
        f"- **R2**: {q['R2']:.6f}",
        f"- **Max residual**: {q['max_residual_mmHg']:.2f} mmHg",
        f"- **Optimizer nfev**: {result['optimizer']['nfev']}",
        "",
    ]
    (out / "RESULTS.md").write_text("\n".join(lines))
    print("\n".join(lines))
    return payload


def write_summary(out_root: Path, results: list[dict]) -> None:
    lines = [
        "# claude-wp1.2 — matriz literatura x material (P_final=50 mmHg)\n",
        "Terceiro braco independente (Sonnet). Ver README_8CASOS_CLAUDE.md.\n",
        "| target | v_max [uL] | material | R2 | max|resid| [mmHg] | nfev | out |",
        "|---|---:|---|---:|---:|---:|---|",
    ]
    for r in results:
        sel = r["selected"]
        q = sel["quality"]
        opt = sel["optimizer"]
        tag = f"{r['target']}_{r['material']}"
        lines.append(
            f"| {r['target']} | {r['target_v_max_uL']:.1f} | {r['material']} | {q['R2']:.4f} | "
            f"{q['max_residual_mmHg']:.2f} | {opt['nfev']} | `{tag}` |"
        )
    lines.append("")
    (out_root / "LITERATURE_MATRIX_SUMMARY_CLAUDE.md").write_text("\n".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--targets", default=",".join(TARGETS), help="Alvos separados por virgula")
    ap.add_argument("--materials", default=",".join(MATERIALS), help="Materiais separados por virgula")
    ap.add_argument("--p-final", type=float, default=DP_FEA_FINAL, help="Pressao absoluta no fim da rampa FEA [mmHg]")
    ap.add_argument("--ne", type=int, default=8)
    ap.add_argument("--max-nfev", type=int, default=30)
    ap.add_argument("--R", type=float, default=12.0)
    ap.add_argument("--t", type=float, default=0.5)
    ap.add_argument("--out", type=Path, default=CLAUDE_WP12 / "output_literature_p50_claude")
    ap.add_argument(
        "--pallikaris-mode",
        choices=("synthetic", "digitized"),
        default="synthetic",
        help="pallikaris: synthetic re-anchored (matriz 8) ou Fig. 2 digitalizada (validação cruzada)",
    )
    args = ap.parse_args()

    lt.PALLIKARIS_TARGET_MODE = args.pallikaris_mode
    if args.pallikaris_mode == "digitized":
        lt.V_MAX_SAFE["pallikaris"] = lt.V_MAX_PALLIKARIS_DIGIT

    targets = [t.strip() for t in args.targets.split(",") if t.strip()]
    materials = [m.strip() for m in args.materials.split(",") if m.strip()]
    args.out.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []
    for target in targets:
        for material in materials:
            tag = f"{target}_{material}"
            out = args.out / tag
            print(f"\n{'='*60}\n{tag} (P_final={args.p_final} mmHg)\n{'='*60}")
            payload = run_one(
                target,
                material,
                out,
                ne=args.ne,
                max_nfev=args.max_nfev,
                p_final=args.p_final,
                R=args.R,
                t=args.t,
            )
            results.append(payload)

    write_summary(args.out, results)
    print(f"\nDone -- see {args.out / 'LITERATURE_MATRIX_SUMMARY_CLAUDE.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
