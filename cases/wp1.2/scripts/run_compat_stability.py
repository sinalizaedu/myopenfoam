#!/usr/bin/env python3
"""Run compat deck stability cases with ccx vanilla (or CCX_BIN override)."""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from ccx_utils import ccx_bin  # noqa: E402
from write_octant_ogden_compat import d1_from_mu1, write_octant_ogden_compat  # noqa: E402

CASES = [
    ("handoff_exact", 2.1397, 1.7709, None),
    ("handoff_mu_plus", 2.1397 * (1 + 0.000007), 1.7709, None),
    ("handoff_mu_minus", 2.1397 * (1 - 0.000007), 1.7709, None),
    ("low_alpha", 2.08, 0.55, None),
]


def run_ccx_compat(deck: Path, ccx: str) -> tuple[str, Path | None]:
    work = deck.parent
    stem = deck.stem
    for ext in (".frd", ".sta", ".cvg", ".dat", ".12d", ".stm", ".out"):
        p = work / f"{stem}{ext}"
        if p.exists():
            p.unlink()
    log = work / f"log_{stem}.txt"
    env = os.environ.copy()
    env.setdefault("OMP_NUM_THREADS", str(os.cpu_count() or 4))
    try:
        with log.open("w") as fh:
            subprocess.run(
                [ccx, "-i", stem],
                cwd=work,
                check=True,
                stdout=fh,
                stderr=subprocess.STDOUT,
                env=env,
                timeout=300,
            )
    except subprocess.CalledProcessError:
        tail = log.read_text().splitlines()[-8:] if log.is_file() else []
        return f"FAIL (exit != 0) log_tail={tail}", None
    except subprocess.TimeoutExpired:
        return "FAIL (timeout)", None

    frd = work / f"{stem}.frd"
    text = log.read_text() if log.is_file() else ""
    if not frd.is_file():
        return f"FAIL (no FRD) log_tail={text.splitlines()[-5:]}", None
    if "Job finished" not in text and "*ERROR" in text:
        return f"FAIL (CCX error in log)", frd
    return "OK", frd


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ccx-bin", default=os.environ.get("CCX_BIN", ""))
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--p-mmhg", type=float, default=80.0)
    ap.add_argument("--out", type=Path, default=HERE.parent / "output_octant" / "compat_stability")
    args = ap.parse_args()

    if args.ccx_bin:
        os.environ["CCX_BIN"] = args.ccx_bin
    ccx = ccx_bin()
    args.out.mkdir(parents=True, exist_ok=True)

    print(f"=== Compat stability (ccx={ccx}) ===")
    results: list[tuple[str, str]] = []
    for tag, mu1, alpha1, d1 in CASES:
        if d1 is None:
            d1 = d1_from_mu1(mu1)
        deck = args.out / f"{tag}.inp"
        write_octant_ogden_compat(
            deck,
            args.n,
            args.n,
            12.0,
            0.5,
            mu1,
            alpha1,
            d1,
            args.p_mmhg,
            n_steps=25,
        )
        status, frd = run_ccx_compat(deck, ccx)
        print(f"{tag:18s}  mu={mu1:.6f}  alpha={alpha1:.4f}  D1={d1:.6f}  -> {status}")
        results.append((tag, status))

    summary = args.out / "RESULTS.md"
    lines = [
        "# Compat deck stability\n",
        f"- **ccx**: `{ccx}`",
        f"- **mesh**: n={args.n}, compat octant, S8R, SNEG, INC=500, STATIC 0.04/0.08",
        f"- **P_final**: {args.p_mmhg} mmHg",
        "",
        "| case | result |",
        "|---|---|",
    ]
    for tag, status in results:
        lines.append(f"| {tag} | {status} |")
    summary.write_text("\n".join(lines) + "\n")
    print(f"\nWrote {summary}")
    ok = all(s == "OK" for _, s in results)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
