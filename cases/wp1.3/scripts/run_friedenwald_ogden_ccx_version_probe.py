#!/usr/bin/env python3
"""Run Friedenwald–Ogden P0 probe deck with ccx_preCICE 2.20 vs vanilla ccx 2.21 (same .inp)."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WP12 = HERE.parents[1] / "wp1.2" / "scripts"
WP1 = HERE.parents[1] / "wp1.1" / "scripts"
sys.path.insert(0, str(WP12))
sys.path.insert(0, str(WP1))

from ccx_utils import ccx_diagnostics  # noqa: E402
from extract_pv_curve import extract_pv  # noqa: E402


def run_ccx_bin(deck: Path, ccx: Path) -> Path:
    work = deck.parent
    base = deck.stem
    for ext in (".frd", ".sta", ".cvg", ".12d"):
        p = work / f"{base}{ext}"
        if p.is_file():
            p.unlink()
    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = env.get("OMP_NUM_THREADS", "1")
    subprocess.run([str(ccx), "-i", base], cwd=work, check=True, env=env)
    return work / f"{base}.frd"


def dV_p0_uL(deck: Path, frd: Path, r_mm: float, p0: float) -> float:
    rows = extract_pv(deck, frd, r_mm, p0_mmhg=p0)
    if not rows:
        return float("nan")
    return float(rows[-1].get("v_abs_uL", rows[-1]["dV_uL"]))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--deck-dir",
        type=Path,
        default=HERE.parent
        / "output_backward_displacement_6/friedenwald_ogden/fixed_point/fp_03",
        help="Directory containing p0_probe.inp (+ mesh include)",
    )
    ap.add_argument("--ccx-220", type=Path, default=Path("/opt/calculix/bin/ccx_preCICE"))
    ccx221_default = os.environ.get("CCX221_BIN", "/opt/calculix/bin/ccx_2.21")
    ap.add_argument("--ccx-221", type=Path, default=Path(ccx221_default))
    ap.add_argument("--out", type=Path, default=HERE.parent / "output_backward_displacement_6" / "friedenwald_ogden_ccx_version_probe.json")
    args = ap.parse_args()

    deck = args.deck_dir / "p0_probe.inp"
    if not deck.is_file():
        raise SystemExit(f"Missing {deck}")
    meta = json.loads(deck.with_suffix(".meta.json").read_text())
    p0 = float(meta.get("P0_mmHg", 16.9))
    r_mm = 12.0

    results: dict = {"deck": str(deck), "P0_mmHg": p0, "ccx_env": ccx_diagnostics(), "runs": {}}

    for tag, ccx in (("ccx_preCICE_2.20", args.ccx_220), ("ccx_2.21", args.ccx_221)):
        if not ccx.is_file():
            results["runs"][tag] = {"status": "missing_binary", "path": str(ccx)}
            continue
        try:
            ver = subprocess.run([str(ccx), "-v"], capture_output=True, text=True, check=False)
            frd = run_ccx_bin(deck, ccx)
            dv = dV_p0_uL(deck, frd, r_mm, p0)
            results["runs"][tag] = {
                "status": "ok",
                "binary": str(ccx),
                "version_output": (ver.stdout or ver.stderr).strip()[:500],
                "dV_P0_uL": dv,
            }
        except subprocess.CalledProcessError as exc:
            results["runs"][tag] = {"status": "failed", "binary": str(ccx), "error": str(exc)}

    if results["runs"].get("ccx_preCICE_2.20", {}).get("status") == "ok" and results["runs"].get("ccx_2.21", {}).get("status") == "ok":
        d20 = results["runs"]["ccx_preCICE_2.20"]["dV_P0_uL"]
        d21 = results["runs"]["ccx_2.21"]["dV_P0_uL"]
        results["comparison"] = {
            "delta_dV_uL": d20 - d21,
            "rel_pct": 100.0 * (d20 - d21) / d21 if d21 else None,
        }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
