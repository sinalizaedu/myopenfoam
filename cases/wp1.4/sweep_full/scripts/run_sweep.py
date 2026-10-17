#!/usr/bin/env python3
"""WP1.4 sweep_full — 300-case LHS runner (variable t(θ), Ogden N=1)."""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SWEEP = HERE.parent
CASES = SWEEP.parents[1]
WP12 = CASES / "wp1.2"

sys.path.insert(0, str(WP12 / "scripts"))
sys.path.insert(0, str(HERE))

from ccx_utils import d1_from_ogden_mu1, run_ccx  # noqa: E402
from extract_pv_curve import extract_pv  # noqa: E402

from case_model import P0_MMHG, p_targets, resolve_case  # noqa: E402
from gen_mesh_variable_t import write_mesh_variable_thickness  # noqa: E402
from write_deck_vt import write_deck_variable_t  # noqa: E402

NE_DEFAULT = 8


def run_one_case(row: dict, work: Path, ne: int, p_final: float) -> dict:
    cid = row["case_id"]
    resolved = resolve_case(row)
    tag = cid
    t0 = time.time()
    try:
        mesh_path = work / f"{tag}_mesh.inp"
        mesh_meta = write_mesh_variable_thickness(
            mesh_path,
            resolved["R_mm"],
            resolved["t_equatorial_mm"],
            resolved["t_posterior_mm"],
            ne,
            2,
            tag,
            theta_min_deg=resolved["theta_min_deg"],
            reduced=True,
        )
        mu1 = resolved["mu1_MPa"]
        alpha1 = resolved["alpha1"]
        params = {
            "mu1_MPa": mu1,
            "alpha1": alpha1,
            "D1": d1_from_ogden_mu1(mu1),
            "d1_tied_mu1": True,
        }
        deck_path = work / f"{tag}.inp"
        write_deck_variable_t(
            deck_path,
            mesh_path.name,
            mesh_meta["band_thickness_mm"],
            "ogden1",
            params,
            p_targets(p_final, p0=P0_MMHG),
            label=f"wp1.4 sweep {tag}",
            p0_mmhg=P0_MMHG,
        )
        frd = run_ccx(deck_path, clean=True)
        pv_rows = extract_pv(deck_path, frd, resolved["R_mm"], p0_mmhg=P0_MMHG)
        scale = resolved["vit_dv_scale"]
        for r in pv_rows:
            r["dV_uL"] = r["dV_uL"] * scale

        v_max = max(r["dV_uL"] for r in pv_rows)
        p_max = max(r["p_mmhg"] for r in pv_rows)
        k_eff = None
        if len(pv_rows) >= 2:
            dv = pv_rows[1]["dV_uL"] - pv_rows[0]["dV_uL"]
            dp = pv_rows[1]["p_mmhg"] - pv_rows[0]["p_mmhg"]
            if dv > 0:
                k_eff = dp / dv

        elapsed = time.time() - t0
        return {
            **{k: row.get(k) for k in row},
            **resolved,
            "status": "OK",
            "V_max_uL": round(v_max, 2),
            "P_max_mmHg": round(p_max, 2),
            "K_eff_mmHg_per_uL": round(k_eff, 6) if k_eff else None,
            "elapsed_s": round(elapsed, 1),
            "pv_curve": pv_rows,
        }
    except Exception as exc:
        return {
            **row,
            **resolve_case(row),
            "status": f"FAIL: {exc}",
            "elapsed_s": round(time.time() - t0, 1),
        }


def load_existing(path: Path) -> dict[str, dict]:
    if not path.is_file():
        return {}
    data = json.loads(path.read_text())
    return {r["case_id"]: r for r in data if r.get("status") == "OK"}


def save_results(path: Path, results: list[dict]) -> None:
    slim = [{k: v for k, v in r.items() if k != "pv_curve"} for r in results]
    path.write_text(json.dumps(slim, indent=2, ensure_ascii=False))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--samples", type=Path, default=SWEEP / "sweep_samples.csv")
    ap.add_argument("--out", type=Path, default=SWEEP / "output_sweep")
    ap.add_argument("--ne", type=int, default=NE_DEFAULT)
    ap.add_argument("--p-final", type=float, default=50.0)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--end", type=int, default=None)
    args = ap.parse_args()

    with open(args.samples, newline="") as fh:
        samples = list(csv.DictReader(fh))
    end = args.end if args.end is not None else len(samples)
    samples = samples[args.start:end]

    args.out.mkdir(parents=True, exist_ok=True)
    work = args.out / "ccx_runs"
    work.mkdir(parents=True, exist_ok=True)
    results_path = args.out / "sweep_results.json"

    existing = load_existing(results_path) if args.resume else {}
    if existing:
        print(f"Resume: {len(existing)} OK cases skipped")

    results = list(existing.values())
    n_new = n_fail = 0
    for i, row in enumerate(samples):
        cid = row["case_id"]
        if cid in existing:
            continue
        idx = args.start + i + 1
        total = args.start + len(samples)
        print(f"[{idx}/{total}] {cid}")
        result = run_one_case(row, work, args.ne, args.p_final)
        results.append(result)
        n_new += 1
        if result["status"] == "OK":
            print(
                f"  OK V_max={result['V_max_uL']:.1f} µL  "
                f"K={result.get('K_eff_mmHg_per_uL')}  ({result['elapsed_s']:.0f}s)"
            )
        else:
            n_fail += 1
            print(f"  {result['status']} ({result['elapsed_s']:.0f}s)")
        if n_new % 10 == 0:
            save_results(results_path, results)

    save_results(results_path, results)
    n_ok = sum(1 for r in results if r.get("status") == "OK")
    print(f"\nDone: {n_ok}/{len(results)} OK, {n_fail} new failures")
    print(f"Results: {results_path}")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
