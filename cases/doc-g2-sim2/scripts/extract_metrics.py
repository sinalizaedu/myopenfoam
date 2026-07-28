#!/usr/bin/env python3
"""Extract experiment metrics (IOP peaks, recovery) for doc-g2-sim2."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RHO = 995.0
PA_TO_MMHG = 0.0075006


def mmhg(p: float) -> float:
    return p * RHO * PA_TO_MMHG


def read_iop(path: Path) -> list[tuple[float, float, float]]:
    rows = []
    for line in path.read_text().splitlines():
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split()
        if len(parts) < 5:
            continue
        t = float(parts[0])
        vals = [float(x) for x in parts[1:5]]
        ac = 0.5 * (mmhg(vals[0]) + mmhg(vals[1]))
        vit = 0.5 * (mmhg(vals[2]) + mmhg(vals[3]))
        rows.append((t, ac, vit))
    return rows


def nearest(rows, t_target: float) -> tuple[float, float, float]:
    return min(rows, key=lambda r: abs(r[0] - t_target))


def read_d_tm(case: Path) -> str:
    fv = case / "fluid/system/fvOptions"
    m = re.search(r"d\s+d\s+\[0 -2 0 0 0 0 0\]\s+\(([0-9.eE+-]+)", fv.read_text())
    return f"{float(m.group(1)):.3e}" if m else "N/A"


def in_phase(rows, t0: float, t1: float) -> list[tuple[float, float, float]]:
    return [r for r in rows if t0 <= r[0] <= t1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument(
        "--wall",
        choices=("robin", "rigid"),
        default="robin",
        help="wall BC label in metrics output",
    )
    args = ap.parse_args()
    case = args.case
    probe = case / "fluid/postProcessing/iop_probe/0/p"
    if not probe.is_file():
        print(f"ERROR: {probe} missing", file=sys.stderr)
        sys.exit(1)
    rows = read_iop(probe)
    if not rows:
        sys.exit(1)

    peak_ac = peak_vit = None
    ivi = in_phase(rows, 5.0, 11.0)
    if ivi:
        peak_ac = max(ivi, key=lambda r: r[1])
        peak_vit = max(ivi, key=lambda r: r[2])
    else:
        peak_ac = max(rows, key=lambda r: r[1])
        peak_vit = max(rows, key=lambda r: r[2])
    t0 = rows[0]
    t11 = nearest(rows, 11.0)
    t20 = nearest(rows, 20.0)

    lines = [
        f"d_TM={read_d_tm(case)}",
        f"IOP0_AC={t0[1]:.3f} mmHg",
        f"IOP0_vit={t0[2]:.3f} mmHg",
        f"peak_AC={peak_ac[1]:.2f} mmHg @ t={peak_ac[0]:.2f}s",
        f"peak_vit={peak_vit[2]:.2f} mmHg @ t={peak_vit[0]:.2f}s",
        f"IOP_t11_AC={t11[1]:.2f}",
        f"IOP_t20_AC={t20[1]:.3f} mmHg",
        f"IOP_t20_vit={t20[2]:.3f} mmHg",
        f"wall={'volume_matched_robin' if args.wall == 'robin' else 'noSlip_rigid'}",
        "Q_ivi=2.08325e-9",
    ]
    text = "\n".join(lines) + "\n"
    default_out = case / "results" / f"{args.wall}_onaxis" / "metrics.txt"
    out = args.out or default_out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(text)


if __name__ == "__main__":
    main()
