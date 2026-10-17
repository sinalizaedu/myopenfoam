#!/usr/bin/env python3
"""Extract experiment metrics for sim3 (ACP-only) and sim4/sim5 (IVI+ACP)."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RHO = 995.0
PA_TO_MMHG = 0.0075006

# Full windows including 1.0 s ramps at each edge (see U.experiment tables).
IVI_T0, IVI_T1 = 5.0, 12.0
ACP_T0, ACP_T1 = 15.0, 22.0


def mmhg(p: float) -> float:
    return p * RHO * PA_TO_MMHG


def uses_ivi_acp_protocol(case_name: str) -> bool:
    return case_name in ("doc-g2-sim4", "doc-g2-sim5") or case_name.startswith(
        "doc-run-"
    )


def read_iop(path: Path) -> list[tuple[float, float, float]]:
    rows: list[tuple[float, float, float]] = []
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


def nearest(rows: list[tuple[float, float, float]], t_target: float) -> tuple[float, float, float]:
    return min(rows, key=lambda r: abs(r[0] - t_target))


def in_phase(rows: list[tuple[float, float, float]], t0: float, t1: float) -> list[tuple[float, float, float]]:
    return [r for r in rows if t0 <= r[0] <= t1]


def read_d_tm(case: Path) -> str:
    fv = case / "fluid/system/fvOptions"
    m = re.search(r"d\s+d\s+\[0 -2 0 0 0 0 0\]\s+\(([0-9.eE+-]+)", fv.read_text())
    return f"{float(m.group(1)):.3e}" if m else "N/A"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument(
        "--protocol",
        choices=("acp", "ivi_acp", "auto"),
        default="auto",
        help="acp = sim3; ivi_acp = sim4/sim5 and doc-run-*",
    )
    args = ap.parse_args()
    case = args.case
    protocol = args.protocol
    if protocol == "auto":
        protocol = "ivi_acp" if uses_ivi_acp_protocol(case.name) else "acp"

    probe_dir = case / "fluid/postProcessing/iop_probe"
    files = [p for p in probe_dir.glob("*/p") if p.is_file()] if probe_dir.is_dir() else []
    if not files:
        print(f"ERROR: {probe_dir} missing", file=sys.stderr)
        sys.exit(1)
    rows: list[tuple[float, float, float]] = []
    seen: set[float] = set()
    for path in sorted(files, key=lambda p: float(p.parent.name)):
        for row in read_iop(path):
            if row[0] in seen:
                continue
            seen.add(row[0])
            rows.append(row)
    rows.sort(key=lambda r: r[0])
    if not rows:
        sys.exit(1)

    t0 = rows[0]
    t_end = nearest(rows, 30.0)
    lines = [
        f"d_TM={read_d_tm(case)}",
        f"IOP0_AC={t0[1]:.3f} mmHg",
        f"IOP0_vit={t0[2]:.3f} mmHg",
    ]

    if protocol == "ivi_acp":
        ivi = in_phase(rows, IVI_T0, IVI_T1)
        if ivi:
            peak_ac = max(ivi, key=lambda r: r[1])
            peak_vit = max(ivi, key=lambda r: r[2])
            lines.extend(
                [
                    f"peak_IVI_AC={peak_ac[1]:.2f} mmHg @ t={peak_ac[0]:.2f}s",
                    f"peak_IVI_vit={peak_vit[2]:.2f} mmHg @ t={peak_vit[0]:.2f}s",
                ]
            )

    acp = in_phase(rows, ACP_T0, ACP_T1)
    if not acp:
        print(f"ERROR: no probe samples in ACP phase {ACP_T0}–{ACP_T1} s", file=sys.stderr)
        sys.exit(1)
    min_ac = min(acp, key=lambda r: r[1])
    min_vit = min(acp, key=lambda r: r[2])
    lines.extend(
        [
            f"min_ACP_AC={min_ac[1]:.2f} mmHg @ t={min_ac[0]:.2f}s",
            f"min_ACP_vit={min_vit[2]:.2f} mmHg @ t={min_vit[0]:.2f}s",
            f"IOP_t30_AC={t_end[1]:.3f} mmHg",
            f"IOP_t30_vit={t_end[2]:.3f} mmHg",
            "wall=volume_matched_flux",
        ]
    )

    text = "\n".join(lines) + "\n"
    out = args.out or case / "results" / "metrics.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(text)


if __name__ == "__main__":
    main()
