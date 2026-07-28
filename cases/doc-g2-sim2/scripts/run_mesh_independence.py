#!/usr/bin/env python3
"""Mesh independence for doc-g2-sim2 IVI (30G lumen, IVI-only tip refinement)."""

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


def read_iop_probe(path: pathlib.Path) -> list[tuple[float, float, float]]:
    rows: list[tuple[float, float, float]] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith("#") or not line:
            continue
        parts = line.split()
        if len(parts) < 5:
            continue
        t = float(parts[0])
        vals = [float(x) for x in parts[1:5]]
        ac = 0.5 * (pkin_to_mmhg(vals[0]) + pkin_to_mmhg(vals[1]))
        vit = 0.5 * (pkin_to_mmhg(vals[2]) + pkin_to_mmhg(vals[3]))
        rows.append((t, ac, vit))
    return rows


def read_ncells(fluid: pathlib.Path) -> int:
    for line in (fluid / "log.checkMesh").read_text().splitlines():
        if "nCells:" in line:
            return int(line.split()[-1])
    raise RuntimeError("nCells not found")


def read_tip_cells(fluid: pathlib.Path) -> int:
    log = fluid / "log.topoSet.iviTip"
    if not log.is_file():
        return -1
    for line in reversed(log.read_text().splitlines()):
        m = re.search(r"cellSet ivi_tip_cells now size (\d+)", line)
        if m:
            return int(m.group(1))
    return -1


def read_baseline_iop(fluid: pathlib.Path) -> float:
    path = fluid / "postProcessing" / "iop_probe" / "0" / "p"
    rows = read_iop_probe(path)
    if not rows:
        raise RuntimeError(f"no IOP in {path}")
    return rows[-1][1]


def read_peak_iop(fluid: pathlib.Path) -> tuple[float, float]:
    path = fluid / "postProcessing" / "iop_probe" / "0" / "p"
    rows = read_iop_probe(path)
    ivi = [r for r in rows if 5.0 <= r[0] <= 11.0]
    if not ivi:
        ivi = rows
    peak_ac = max(ivi, key=lambda r: r[1])
    peak_vit = max(ivi, key=lambda r: r[2])
    return peak_ac[1], peak_vit[2]


def docker_run(inner: str, log_path: pathlib.Path) -> None:
    cmd = [
        "docker",
        "compose",
        "-f",
        str(REPO / "docker-compose.yaml"),
        "run",
        "--rm",
        "fsi",
        "bash",
        "-lc",
        inner,
    ]
    with log_path.open("w") as logf:
        proc = subprocess.run(
            cmd,
            cwd=str(REPO),
            stdout=logf,
            stderr=subprocess.STDOUT,
            text=True,
        )
    if proc.returncode != 0:
        raise RuntimeError(f"failed — see {log_path}")


def run_level(level: str) -> dict:
    fluid = CASE / "fluid"
    dest = OUT / level
    log_base = OUT / f"{level}_baseline.log"
    log_exp = OUT / f"{level}_experiment.log"

    print(f"\n===== {level} baseline =====", flush=True)
    docker_run(
        f"cd /simulation/doc-g2-sim2 && ./Allclean && "
        f"MESH_LEVEL={level} MODE=baseline ./Allrun",
        log_base,
    )

    print(f"===== {level} experiment (IVI) =====", flush=True)
    docker_run(
        f"cd /simulation/doc-g2-sim2 && "
        f"MESH_LEVEL={level} MODE=experiment REUSE_MESH=1 ./Allrun",
        log_exp,
    )

    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    for name in (
        "log.checkMesh",
        "log.topoSet.iviTip",
        "log.simpleFoam",
        "log.pimpleFoam",
    ):
        src = fluid / name
        if src.is_file():
            shutil.copy2(src, dest / name)
    pp = fluid / "postProcessing" / "iop_probe" / "0" / "p"
    if pp.is_file():
        shutil.copy2(pp, dest / "iop_probe_p.txt")

    peak_ac, peak_vit = read_peak_iop(fluid)
    return {
        "level": level,
        "nCells": read_ncells(fluid),
        "ivi_tip_cells": read_tip_cells(fluid),
        "IOP0_mmHg": read_baseline_iop(fluid),
        "peak_AC_mmHg": peak_ac,
        "peak_vit_mmHg": peak_vit,
    }


def gci_peak(rows: list[dict], key: str) -> str:
    vals = [r[key] for r in rows]
    ns = [r["nCells"] for r in rows]
    f1, f2, f3 = vals[2], vals[1], vals[0]
    n1, n2, n3 = ns[2], ns[1], ns[0]
    r21 = (n1 / n2) ** (1.0 / 3.0)
    r32 = (n2 / n3) ** (1.0 / 3.0)
    eps21 = f2 - f1
    eps32 = f3 - f2
    lines = [f"r21 ≈ {r21:.3f}, r32 ≈ {r32:.3f}"]
    if abs(eps21) < 1e-9 or abs(eps32) < 1e-9:
        lines.append("differences too small for GCI.")
        return "\n".join(lines)
    p = abs(math.log(abs(eps32 / eps21)) / math.log(r21))
    Fs = 1.25
    gci_fine = Fs * abs(eps21) / (r21**p - 1.0) / abs(f1) * 100.0
    d_m2_m3 = abs(vals[1] - vals[2]) / abs(vals[2]) * 100.0
    lines += [
        f"Observed order p ≈ {p:.3f}",
        f"Fine-grid GCI ≈ {gci_fine:.3f}%",
        f"M2 → M3 change: {d_m2_m3:.3f}%",
    ]
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for level in LEVELS:
        msh = CASE / "geometry" / f"eye_g2_fluid_lamminsalo_{level}.msh"
        if not msh.is_file():
            raise RuntimeError(
                f"missing {msh} — generate with:\n"
                f"  .venv-geom/bin/python brunaStuff/gen_lamminsalo_g2.py "
                f"--case doc-g2-sim2 --mesh --mesh-level {level} --tip-refine ivi"
            )
        rows.append(run_level(level))
        print(rows[-1], flush=True)

    csv_path = OUT / "results.csv"
    fields = [
        "level",
        "nCells",
        "ivi_tip_cells",
        "IOP0_mmHg",
        "peak_AC_mmHg",
        "peak_vit_mmHg",
    ]
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    d_peak = (
        abs(rows[1]["peak_AC_mmHg"] - rows[2]["peak_AC_mmHg"])
        / abs(rows[2]["peak_AC_mmHg"])
        * 100.0
    )
    if d_peak < 1.0:
        decision = f"M2 vs M3 peak AC differs by {d_peak:.2f}% (<1%). **Recommend M2** for IVI production."
        recommended = "M2"
    elif d_peak < 2.0:
        decision = f"M2 vs M3 peak AC differs by {d_peak:.2f}% (1–2%). Prefer **M2**; use **M3** if sub-percent needed."
        recommended = "M2"
    else:
        decision = f"M2→M3 peak AC change {d_peak:.2f}% (>2%). Prefer **M3**."
        recommended = "M3"

    report = f"""# Mesh-independence — G2 Sim 2 IVI (30G lumen, IVI-only refinement)

## Setup

Gmsh fluid mesh with **local IVI tip refinement only** (`--tip-refine ivi`).
30G nominal lumen r = 0.07 mm. Robin wall, Q_ivi = 2.08325×10⁻⁹ m³/s (sector ¼).
Each level: baseline (`simpleFoam`) → IVI experiment (`pimpleFoam`, t = 0–20 s).

| Level | Cells | ivi_tip cells | IOP₀ [mmHg] | Peak AC [mmHg] | Peak vitreous [mmHg] |
|-------|------:|--------------:|--------------:|---------------:|---------------------:|
| M1 | {rows[0]['nCells']:,} | {rows[0]['ivi_tip_cells']} | {rows[0]['IOP0_mmHg']:.3f} | {rows[0]['peak_AC_mmHg']:.2f} | {rows[0]['peak_vit_mmHg']:.2f} |
| M2 | {rows[1]['nCells']:,} | {rows[1]['ivi_tip_cells']} | {rows[1]['IOP0_mmHg']:.3f} | {rows[1]['peak_AC_mmHg']:.2f} | {rows[1]['peak_vit_mmHg']:.2f} |
| M3 | {rows[2]['nCells']:,} | {rows[2]['ivi_tip_cells']} | {rows[2]['IOP0_mmHg']:.3f} | {rows[2]['peak_AC_mmHg']:.2f} | {rows[2]['peak_vit_mmHg']:.2f} |

## Grid convergence (peak AC during IVI)

{gci_peak(rows, "peak_AC_mmHg")}

## Grid convergence (peak vitreous during IVI)

{gci_peak(rows, "peak_vit_mmHg")}

## Decision

{decision}

**Recommended mesh for G2 Sim 2 IVI: {recommended}**
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
