#!/usr/bin/env python3
"""Archive experiment logs, probes and postProcessing under results/."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", type=Path, default=Path(__file__).resolve().parents[1])
    args = ap.parse_args()
    case = args.case
    fluid = case / "fluid"
    dest = case / "results"
    dest.mkdir(parents=True, exist_ok=True)

    log = fluid / "log.pimpleFoam"
    if log.is_file():
        shutil.copy2(log, dest / "log.experiment_run.txt")
    else:
        print(f"WARNING: missing {log}", file=sys.stderr)

    probe = fluid / "postProcessing" / "iop_probe" / "0" / "p"
    if probe.is_file():
        shutil.copy2(probe, dest / "iop_probe_p.txt")
    else:
        print(f"WARNING: missing {probe}", file=sys.stderr)

    pp_src = fluid / "postProcessing"
    if pp_src.is_dir():
        pp_dst = dest / "postProcessing"
        if pp_dst.exists():
            shutil.rmtree(pp_dst)
        shutil.copytree(pp_src, pp_dst)
    else:
        print(f"WARNING: missing {pp_src}", file=sys.stderr)

    print(f"Archived experiment → {dest}")


if __name__ == "__main__":
    sys.exit(main() or 0)
