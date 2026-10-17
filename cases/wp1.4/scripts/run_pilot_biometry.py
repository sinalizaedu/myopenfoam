#!/usr/bin/env python3
"""WP1.4 — 14-case biometry pilot: Ogden + Yeoh (Friedenwald, P_final=50 mmHg).

Uses official WP1.2 closure fits:
  output_literature_p50_v2/friedenwald_{ogden,yeoh}/fit_results.json

Replaces the 22/Sep pilot (Yeoh-only, E3 params, P_final=80).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WP14 = HERE.parent
WP12 = WP14.parent / "wp1.2"
sys.path.insert(0, str(WP12 / "scripts"))

from ogden_forward_run import load_ogden_params, run_ogden_forward  # noqa: E402
from yeoh_forward_run import run_yeoh_forward  # noqa: E402
from yeoh_material import load_yeoh_params  # noqa: E402

FIT_OGDEN = WP12 / "output_literature_p50_v2" / "friedenwald_ogden" / "fit_results.json"
FIT_YEOH = WP12 / "output_literature_p50_v2" / "friedenwald_yeoh" / "fit_results.json"
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
            pv, _ = run_yeoh_forward(
                R, t, work, tag, ne=ne, p_final=p_final, fit_path=FIT_YEOH,
            )
        else:
            pv, _ = run_ogden_forward(
                R, t, work, tag, ne=ne, p_final=p_final, fit_path=FIT_OGDEN,
            )
        v_max = max(r["dV_uL"] for r in pv)
        p_max = max(r["p_mmhg"] for r in pv)
        return {
            **row,
            "material": material,
            "status": "OK",
            "V_max_uL": v_max,
            "P_max_mmHg": p_max,
            "n_pv_points": len(pv),
        }
    except Exception as exc:  # noqa: BLE001
        return {**row, "material": material, "status": f"FAIL: {exc}"}


def write_results_md(out: Path, results: list[dict], meta: dict) -> None:
    by_case: dict[str, dict] = {}
    for r in results:
        d = by_case.setdefault(
            r["case_id"],
            {"R_mm": r["R_mm"], "t_mm": r["t_mm"], "note": r.get("note", "")},
        )
        if r["status"] == "OK":
            d[r["material"]] = r["V_max_uL"]
        else:
            d[r["material"]] = None
            d[f"{r['material']}_status"] = r["status"]

    lines = [
        "# WP1.4 — 14-case biometry pilot (Ogden + Yeoh, Friedenwald P_final=50)\n",
        f"- **Ogden**: μ₁={meta['ogden']['mu1_MPa']:.4f}, α₁={meta['ogden']['alpha1']:.4f} MPa",
        f"- **Yeoh**: C10={meta['yeoh']['C10_MPa']:.4f}, C20={meta['yeoh']['C20_MPa']:.4f} MPa",
        f"- **Mesh**: octant spherical, ne={meta['ne']}",
        f"- **Convergence**: {meta['n_ok']}/{meta['n_total']} OK",
        "",
        "| case | R | t | V_max Ogden µL | V_max Yeoh µL | Δ Yeoh−Ogden µL |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for cid, d in by_case.items():
        vo, vy = d.get("ogden"), d.get("yeoh")
        vo_s = f"{vo:.1f}" if vo is not None else "—"
        vy_s = f"{vy:.1f}" if vy is not None else "—"
        delta = f"{vy - vo:+.1f}" if vo is not None and vy is not None else "—"
        lines.append(f"| {cid} | {d['R_mm']} | {d['t_mm']} | {vo_s} | {vy_s} | {delta} |")
    lines.append("")
    (out / "RESULTS.md").write_text("\n".join(lines) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", type=Path, default=WP14 / "data" / "biometry_14.csv")
    ap.add_argument("--materials", default="ogden,yeoh")
    ap.add_argument("--ne", type=int, default=8)
    ap.add_argument("--p-final", type=float, default=P_FINAL_DEFAULT)
    ap.add_argument("--out", type=Path, default=WP14 / "output_pilot_biometry_p50")
    args = ap.parse_args()

    for p in (FIT_OGDEN, FIT_YEOH):
        if not p.is_file():
            raise FileNotFoundError(f"Missing fit: {p}")

    materials = [m.strip() for m in args.materials.split(",") if m.strip()]
    args.out.mkdir(parents=True, exist_ok=True)
    work = args.out / "ccx_runs"
    cases = load_biometry(args.data)

    ogden_p = load_ogden_params(FIT_OGDEN)
    yeoh_p = load_yeoh_params(FIT_YEOH)

    results: list[dict] = []
    for material in materials:
        for row in cases:
            print(f"=== {row['case_id']} {material} R={row['R_mm']} t={row['t_mm']} ===")
            entry = run_one(material, row, work, args.ne, args.p_final)
            print(f"  -> {entry['status']}")
            results.append(entry)

    n_ok = sum(1 for r in results if r["status"] == "OK")
    payload = {
        "fits": {
            "ogden": str(FIT_OGDEN),
            "yeoh": str(FIT_YEOH),
        },
        "materials": {
            "ogden": ogden_p,
            "yeoh": yeoh_p,
        },
        "p_final_mmHg": args.p_final,
        "ne": args.ne,
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
