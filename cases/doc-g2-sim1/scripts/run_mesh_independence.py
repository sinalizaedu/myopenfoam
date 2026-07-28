#!/usr/bin/env python3
"""Run G2-fluid mesh independence (M1/M2/M3) via Docker Allrun and write REPORT."""

from __future__ import annotations

import csv
import math
import os
import pathlib
import re
import shutil
import subprocess
import sys

CASE = pathlib.Path(__file__).resolve().parent.parent
REPO = CASE.parents[1]
OUT = CASE / "mesh_independence"
LEVELS = ("M1", "M2", "M3")
RHO = 995.0
PA_TO_MMHG = 0.0075006


def pkin_to_mmhg(p: float) -> float:
    return p * RHO * PA_TO_MMHG


def read_iop(fluid: pathlib.Path) -> float:
    path = fluid / "postProcessing" / "iop_probe" / "0" / "p"
    vals = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith("#") or not line:
            continue
        parts = line.split()
        if len(parts) >= 5:
            vals = [float(x) for x in parts[1:5]]
    if len(vals) < 2:
        raise RuntimeError(f"no IOP probes in {path}")
    # mean of AC probes (first two)
    return 0.5 * (pkin_to_mmhg(vals[0]) + pkin_to_mmhg(vals[1]))


def read_ncells(fluid: pathlib.Path) -> int:
    for line in (fluid / "log.checkMesh").read_text().splitlines():
        if "nCells:" in line:
            return int(line.split()[-1])
    raise RuntimeError("nCells not found")


def read_q(fluid: pathlib.Path) -> float:
    for line in reversed((fluid / "log.simpleFoam").read_text().splitlines()):
        if "sum(outlet_tm) of phi" in line:
            return float(line.split("=")[-1].strip())
    return float("nan")


def run_level(level: str, d_tm: str | None) -> dict:
    env = os.environ.copy()
    env["MESH_LEVEL"] = level
    if d_tm:
        env["D_TM"] = d_tm
    cmd = [
        "docker",
        "compose",
        "run",
        "--rm",
        "fsi",
        "bash",
        "-lc",
        f"cd /simulation/doc-g2-sim1 && ./Allclean && ./Allrun",
    ]
    print(f"\n===== {level} =====", flush=True)
    # Set env vars inside the container command
    inner = f"cd /simulation/doc-g2-sim1 && ./Allclean && MESH_LEVEL={level}"
    if d_tm:
        inner += f" D_TM={d_tm}"
    inner += " ./Allrun"
    cmd = ["docker", "compose", "run", "--rm", "fsi", "bash", "-lc", inner]
    log_path = OUT / f"{level}_run.log"
    with log_path.open("w") as logf:
        proc = subprocess.run(
            cmd,
            cwd=str(REPO),
            stdout=logf,
            stderr=subprocess.STDOUT,
            text=True,
        )
    if proc.returncode != 0:
        raise RuntimeError(f"{level} failed — see {log_path}")

    fluid = CASE / "fluid"
    # archive
    dest = OUT / level
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    for name in ("log.simpleFoam", "log.checkMesh"):
        shutil.copy2(fluid / name, dest / name)
    pp = fluid / "postProcessing" / "iop_probe" / "0" / "p"
    if pp.exists():
        (dest / "iop_probe_p.txt").write_text(pp.read_text())

    return {
        "level": level,
        "nCells": read_ncells(fluid),
        "IOP_mmHg": read_iop(fluid),
        "Q_TM": read_q(fluid),
    }


def gci_analysis(rows: list[dict]) -> str:
    # Assume r ≈ N^{1/3} ratio between successive meshes
    iops = [r["IOP_mmHg"] for r in rows]
    ns = [r["nCells"] for r in rows]
    # coarsest → finest: M1, M2, M3
    f1, f2, f3 = iops[2], iops[1], iops[0]  # fine, mid, coarse (standard GCI naming)
    # Actually standard: h1 fine. So f1=M3, f2=M2, f3=M1
    n1, n2, n3 = ns[2], ns[1], ns[0]
    r21 = (n1 / n2) ** (1.0 / 3.0)
    r32 = (n2 / n3) ** (1.0 / 3.0)
    eps21 = f2 - f1
    eps32 = f3 - f2
    lines = []
    lines.append(f"r21 (M2→M3) ≈ {r21:.3f}, r32 (M1→M2) ≈ {r32:.3f}")
    if abs(eps21) < 1e-12 or abs(eps32) < 1e-12:
        lines.append("IOP differences too small for order estimate.")
        return "\n".join(lines)
    # observed order
    p = abs(math.log(abs(eps32 / eps21)) / math.log(r21))
    # Richardson
    f_ext = f1 + eps21 / (r21**p - 1.0)
    # GCI fine
    Fs = 1.25
    gci_fine = Fs * abs(eps21) / (r21**p - 1.0) / abs(f1) * 100.0
    gci_mid = Fs * abs(eps32) / (r32**p - 1.0) / abs(f2) * 100.0
    # asymptotic check
    asym = abs(r21**p * eps21 / eps32) if abs(eps32) > 0 else float("nan")
    d_m2_m3 = abs(iops[1] - iops[2]) / abs(iops[2]) * 100.0
    lines += [
        f"Observed order p ≈ {p:.3f}",
        f"Richardson-extrapolated IOP ≈ {f_ext:.3f} mmHg",
        f"Fine-grid GCI (M3) ≈ {gci_fine:.3f}%",
        f"Medium-grid GCI (M2) ≈ {gci_mid:.3f}%",
        f"Asymptotic-range check ≈ {asym:.3f} (ideal ≈ 1)",
        f"M2 → M3 IOP change: {d_m2_m3:.3f}%",
    ]
    return "\n".join(lines)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d_tm = os.environ.get("D_TM")  # optional fixed
    rows = []
    for level in LEVELS:
        rows.append(run_level(level, d_tm))
        print(rows[-1], flush=True)

    csv_path = OUT / "results.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["level", "nCells", "IOP_mmHg", "Q_TM"])
        w.writeheader()
        w.writerows(rows)

    analysis = gci_analysis(rows)
    # Decision
    d23 = abs(rows[1]["IOP_mmHg"] - rows[2]["IOP_mmHg"]) / abs(rows[2]["IOP_mmHg"]) * 100.0
    if d23 < 1.0:
        decision = (
            f"M2 differs from M3 by {d23:.2f}% (<1%). "
            "**M2 is recommended** for production 3D G2-fluid."
        )
        recommended = "M2"
    elif d23 < 2.0:
        decision = (
            f"M2 differs from M3 by {d23:.2f}% (1–2%). "
            "Prefer **M2** for engineering; use **M3** if reporting sub-percent uncertainty."
        )
        recommended = "M2"
    else:
        decision = (
            f"M2→M3 change is {d23:.2f}% (>2%). Prefer **M3** (or refine further)."
        )
        recommended = "M3"

    report = f"""# Mesh-independence study — G2-fluid Sim 1 (90° calotte)

## Setup

Gmsh fluid mesh with **local 30G tip refinement** (box fields at IVI/ACP sites,
`lc_tip ≈ 28 µm`, lumen r = 0.07 mm). Unstructured angular revolve when tip
refinement is active. Geometry, BCs (Q = 1.25×10⁻¹¹ m³/s = ¼ of 3 µL/min),
porous coefficients, schemes and residual tolerances were held fixed.

| Level | Cells | IOP [mmHg] | Q_TM [m³/s] |
|-------|------:|-----------:|------------:|
| M1 | {rows[0]['nCells']:,} | {rows[0]['IOP_mmHg']:.3f} | {rows[0]['Q_TM']:.4e} |
| M2 | {rows[1]['nCells']:,} | {rows[1]['IOP_mmHg']:.3f} | {rows[1]['Q_TM']:.4e} |
| M3 | {rows[2]['nCells']:,} | {rows[2]['IOP_mmHg']:.3f} | {rows[2]['Q_TM']:.4e} |

d_TM = {d_tm or 'fvOptions default (7.779e14)'}
Needle patch: 30G lumen r = 0.07 mm (`brunaStuff/g2_needle.py`)

## Grid-convergence

{analysis}

## Decision

{decision}

**Recommended mesh for 3D G2-fluid: {recommended}**
"""
    (OUT / "REPORT.md").write_text(report)
    print(report)
    print(f"Wrote {csv_path}")
    print(f"Wrote {OUT / 'REPORT.md'}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
