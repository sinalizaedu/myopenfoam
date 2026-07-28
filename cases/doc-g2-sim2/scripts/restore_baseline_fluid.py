#!/usr/bin/env python3
"""Restore fluid/ to post-baseline state (drop experiment times and postProcessing)."""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path


def latest_baseline_time(fluid: Path) -> Path:
    ints: list[tuple[float, Path]] = []
    for p in fluid.iterdir():
        if not p.is_dir() or not p.name.isdigit():
            continue
        t = float(p.name)
        if t > 0:
            ints.append((t, p))
    if not ints:
        raise SystemExit("ERROR: no integer baseline time directory under fluid/")
    return max(ints, key=lambda x: x[0])[1]


def main() -> None:
    case = Path(__file__).resolve().parents[1]
    fluid = case / "fluid"
    if not (fluid / "constant" / "polyMesh").is_dir():
        raise SystemExit("ERROR: missing polyMesh — run baseline first")

    src = latest_baseline_time(fluid)
    print(f"=== restore baseline fluid from time {src.name} ===")

    for p in list(fluid.iterdir()):
        if not p.is_dir():
            continue
        name = p.name
        if name == "0" or name == "constant":
            continue
        if name.isdigit() or "." in name:
            if p != src:
                shutil.rmtree(p)

    shutil.rmtree(fluid / "postProcessing", ignore_errors=True)
    shutil.rmtree(fluid / "dynamicCode", ignore_errors=True)
    for log_name in ("log.pimpleFoam",):
        p = fluid / log_name
        if p.is_file():
            p.unlink()
            print(f"  removed {log_name}")

    zero = fluid / "0"
    zero.mkdir(exist_ok=True)
    for f in ("U", "p"):
        shutil.copy2(src / f, zero / f)
    for extra in ("phi", "uniform"):
        p = zero / extra
        if p.exists():
            shutil.rmtree(p) if p.is_dir() else p.unlink()

    for pair in (
        ("controlDict.baseline", "controlDict"),
        ("fvSchemes.baseline", "fvSchemes"),
        ("fvSolution.baseline", "fvSolution"),
        ("U.baseline", "U"),
        ("p.baseline", "p"),
    ):
        src_f = fluid / "initial" / pair[0]
        dst_f = fluid / "initial" / pair[1]
        if src_f.is_file():
            shutil.copy2(src_f, dst_f)
        tpl = fluid / "system" / pair[0]
        if tpl.is_file():
            shutil.copy2(tpl, fluid / "system" / pair[1])

    if (fluid / "initial" / "U.experiment.robin").is_file():
        shutil.copy2(fluid / "initial" / "U.experiment.robin", fluid / "initial" / "U.experiment")

    print(f"  kept baseline time {src.name}; fluid/0 reset; postProcessing cleared")
    print("  active templates → baseline (controlDict, initial/U,p)")


if __name__ == "__main__":
    main()
