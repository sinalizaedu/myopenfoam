#!/usr/bin/env python3
"""Isolated forward repro: fresh .inp from scratch, outside optimizer loop."""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from ccx_utils import ccx_bin, run_ccx  # noqa: E402
from fit_pallikaris import DP_FEA_FINAL, Geometry, PallikarisForward  # noqa: E402


def try_run(
    mu1: float,
    alpha1: float,
    dp_final: float,
    trial: int,
    out: Path,
) -> str:
    work = out / f"trial_{trial:02d}"
    if work.is_dir():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    forward = PallikarisForward(
        Geometry(R_mm=12.0, t_mm=0.5),
        work,
        ne=6,
        dp_fea_final=dp_final,
    )
    deck = work / "isolated.inp"
    try:
        forward.run(mu1, alpha1, tag="isolated")
    except Exception as exc:
        log = work / "log_isolated.txt"
        tail = log.read_text().splitlines()[-10:] if log.is_file() else []
        return f"FAIL: {exc} | log_tail={tail}"
    log = work / "log_isolated.txt"
    text = log.read_text() if log.is_file() else ""
    if "Job finished" not in text:
        return f"FAIL: no Job finished | log_tail={text.splitlines()[-8:]}"
    if "*ERROR" in text:
        return f"FAIL: CCX error in log"
    return "OK"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mu1", type=float, default=7.1585)
    ap.add_argument("--alpha1", type=float, default=0.5)
    ap.add_argument("--dp-final", type=float, default=DP_FEA_FINAL)
    ap.add_argument("--trials", type=int, default=5)
    ap.add_argument(
        "--out",
        type=Path,
        default=HERE.parent / "output_octant" / "isolated_repro",
    )
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    print(f"ccx={ccx_bin()}")
    print(
        f"isolated point: mu1={args.mu1} alpha1={args.alpha1} "
        f"dp_final={args.dp_final} mmHg (abs)"
    )
    results: list[tuple[int, str]] = []
    for i in range(1, args.trials + 1):
        status = try_run(args.mu1, args.alpha1, args.dp_final, i, args.out)
        print(f"  trial {i}/{args.trials}: {status}")
        results.append((i, status))

    summary = args.out / "RESULTS.md"
    lines = [
        "# Isolated forward reproducibility\n",
        f"- **ccx**: `{ccx_bin()}`",
        f"- **μ₁**: {args.mu1}",
        f"- **α₁**: {args.alpha1}",
        f"- **P_final**: {args.dp_final} mmHg (abs)",
        f"- **trials**: {args.trials} (fresh deck each)",
        "",
        "| trial | result |",
        "|---|---|",
    ]
    for i, status in results:
        lines.append(f"| {i} | {status} |")
    ok = sum(1 for _, s in results if s == "OK")
    lines.append("")
    lines.append(f"**Summary**: {ok}/{args.trials} OK")
    summary.write_text("\n".join(lines) + "\n")
    print(f"\nWrote {summary}")
    return 0 if ok == args.trials else 1


if __name__ == "__main__":
    raise SystemExit(main())
