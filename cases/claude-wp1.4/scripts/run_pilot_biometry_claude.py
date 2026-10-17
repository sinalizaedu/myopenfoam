#!/usr/bin/env python3
"""claude-wp1.4 — piloto de biometria (14 casos), Ogden + Yeoh, com os
parâmetros OFICIAIS recalibrados do fechamento do WP1.2
(Friedenwald, P_final=50 mmHg).

O WP1.4 original (cases/wp1.4/, rodado em 22/set, ANTES do fechamento
do WP1.2) usa Yeoh com params antigos (C10=4.364 em vez de ~1.02) e
P_final=80 (abandonado em favor de 50). Este script atualiza o piloto
com os valores corretos, reusando a mesma tabela de biometria
(cases/wp1.4/data/biometry_14.csv, leitura apenas) e o helper de Yeoh
já validado (cases/wp1.2/scripts/yeoh_forward_run.py, leitura apenas).
Adiciona também o Ogden (não existia um helper equivalente no repo).

Uso:
    python3 scripts/run_pilot_biometry_claude.py
    python3 scripts/run_pilot_biometry_claude.py --materials yeoh
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent            # cases/claude-wp1.4/scripts
CLAUDE_WP14 = HERE.parent                          # cases/claude-wp1.4
WP12 = CLAUDE_WP14.parent / "wp1.2"                 # leitura apenas (Composer)
WP14_DATA = CLAUDE_WP14.parent / "wp1.4" / "data" / "biometry_14.csv"  # leitura apenas (Composer)

sys.path.insert(0, str(WP12 / "scripts"))
sys.path.insert(0, str(HERE))

from yeoh_forward_run import run_yeoh_forward  # noqa: E402  (reuso, não editado)
from ogden_forward_run import run_ogden_forward  # noqa: E402  (novo, claude)

FIT_PATHS = {
    "ogden": WP12 / "output_literature_p50_v2" / "friedenwald_ogden" / "fit_results.json",
    "yeoh": WP12 / "output_literature_p50_v2" / "friedenwald_yeoh" / "fit_results.json",
}
P_FINAL_DEFAULT = 50.0


def load_biometry(path: Path) -> list[dict]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def run_one(material: str, row: dict, work: Path, ne: int, p_final: float) -> dict:
    cid = row["case_id"]
    R = float(row["R_mm"])
    t = float(row["t_mm"])
    tag = f"{cid}_{material}"
    try:
        if material == "yeoh":
            pv, meta = run_yeoh_forward(
                R, t, work, tag, ne=ne, p_final=p_final, fit_path=FIT_PATHS["yeoh"],
            )
        else:
            pv, meta = run_ogden_forward(
                R, t, work, tag, ne=ne, p_final=p_final, fit_path=FIT_PATHS["ogden"],
            )
        v_max = max(r["dV_uL"] for r in pv)
        p_max = max(r["p_mmhg"] for r in pv)
        return {**row, "material": material, "status": "OK", "V_max_uL": v_max, "P_max_mmHg": p_max}
    except Exception as exc:  # noqa: BLE001
        return {**row, "material": material, "status": f"FAIL: {exc}"}


def write_summary(out: Path, results: list[dict]) -> None:
    by_case: dict[str, dict] = {}
    for r in results:
        d = by_case.setdefault(
            r["case_id"], {"R_mm": r["R_mm"], "t_mm": r["t_mm"], "note": r.get("note", "")}
        )
        vm = r.get("V_max_uL")
        d[r["material"]] = f"{vm:.1f}" if r["status"] == "OK" and vm is not None else "FALHOU"

    lines = [
        "# claude-wp1.4 — piloto de biometria (14 casos), Ogden + Yeoh",
        "## (Friedenwald recalibrado, P_final=50 mmHg -- atualiza cases/wp1.4/)\n",
        "| case | R [mm] | t [mm] | nota | V_max Ogden [µL] | V_max Yeoh [µL] |",
        "|---|---:|---:|---|---:|---:|",
    ]
    for cid, d in by_case.items():
        lines.append(
            f"| {cid} | {d['R_mm']} | {d['t_mm']} | {d.get('note', '')} | "
            f"{d.get('ogden', '—')} | {d.get('yeoh', '—')} |"
        )
    lines.append("")
    (out / "RESULTS_CLAUDE.md").write_text("\n".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", type=Path, default=WP14_DATA)
    ap.add_argument("--materials", default="ogden,yeoh")
    ap.add_argument("--ne", type=int, default=8)
    ap.add_argument("--p-final", type=float, default=P_FINAL_DEFAULT)
    ap.add_argument("--out", type=Path, default=CLAUDE_WP14 / "output_pilot_biometry_claude")
    args = ap.parse_args()

    materials = [m.strip() for m in args.materials.split(",") if m.strip()]
    args.out.mkdir(parents=True, exist_ok=True)
    work = args.out / "ccx_runs"
    cases = load_biometry(args.data)

    results = []
    for material in materials:
        for row in cases:
            print(f"=== {row['case_id']} {material} R={row['R_mm']} t={row['t_mm']} ===")
            entry = run_one(material, row, work, args.ne, args.p_final)
            print(f"  -> {entry['status']}")
            results.append(entry)

    (args.out / "pilot_biometry_results.json").write_text(json.dumps(results, indent=2))
    write_summary(args.out, results)
    n_ok = sum(1 for r in results if r["status"] == "OK")
    print(f"\nDone: {n_ok}/{len(results)} OK -- see {args.out / 'RESULTS_CLAUDE.md'}")
    return 0 if n_ok == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
