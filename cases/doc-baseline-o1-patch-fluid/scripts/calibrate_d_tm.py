#!/usr/bin/env python3
"""Binary-search d_TM so baseline IOP_AC ≈ 15 mmHg (outlet stays at 10 Torr)."""

from __future__ import annotations

import argparse
import math
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

CASE = Path(__file__).resolve().parent.parent
TARGET = 15.0
TOL = 0.25
D_START = 7.779e14
MESH_LOG = "N1"


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"{ts}  {msg}"
    print(line, flush=True)
    out = CASE / "mesh_independence" / f"calibrate_{MESH_LOG}.log"
    out.parent.mkdir(exist_ok=True)
    with out.open("a") as fh:
        fh.write(line + "\n")


def run_allrun(*, mesh: str, d_tm: float, reuse: bool) -> None:
    env = f"MESH_LEVEL={mesh} MODE=baseline D_TM={d_tm:.6e}"
    if reuse:
        env += " REUSE_MESH=1"
    cmd = f"cd /simulation/doc-baseline-o1-patch-fluid && {env} ./Allrun"
    log(f"RUN {env}")
    proc = subprocess.run(["bash", "-lc", cmd], cwd=CASE)
    if proc.returncode != 0:
        raise SystemExit(f"Allrun failed rc={proc.returncode} d_TM={d_tm:.6e}")


def read_iop() -> tuple[float, float]:
    proc = subprocess.run(
        ["python3", str(CASE / "scripts" / "extract_step0_metrics.py")],
        cwd=CASE,
        capture_output=True,
        text=True,
        check=True,
    )
    print(proc.stdout, end="")
    iop_ac = iop_vit = None
    for line in proc.stdout.splitlines():
        if line.startswith("IOP_AC="):
            iop_ac = float(re.search(r"IOP_AC=([\d.]+)", line).group(1))
        if line.startswith("IOP_vitreous="):
            iop_vit = float(re.search(r"IOP_vitreous=([\d.]+)", line).group(1))
    if iop_ac is None or iop_vit is None:
        raise SystemExit("ERROR: could not parse IOP from extract_step0_metrics")
    return iop_ac, iop_vit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mesh", default="N1")
    parser.add_argument("--d-start", type=float, default=D_START)
    parser.add_argument("--target", type=float, default=TARGET)
    parser.add_argument("--tol", type=float, default=TOL)
    args = parser.parse_args()
    global MESH_LOG
    MESH_LOG = args.mesh

    d_tm = args.d_start
    run_allrun(mesh=args.mesh, d_tm=d_tm, reuse=False)
    iop_ac, iop_vit = read_iop()
    log(f"iter=0 d_TM={d_tm:.4e} IOP_AC={iop_ac:.3f} IOP_vit={iop_vit:.3f}")

    if abs(iop_ac - args.target) <= args.tol:
        log(f"OK already within tol  d_TM={d_tm:.6e}  IOP_AC={iop_ac:.3f} mmHg")
        return 0

    # Low IOP → raise d_TM. If still glued to ~10 mmHg after a 50× jump, patches are wrong.
    if iop_ac < 10.4:
        d_probe = d_tm * 50.0
        run_allrun(mesh=args.mesh, d_tm=d_probe, reuse=True)
        iop_ac, iop_vit = read_iop()
        log(f"bypass-probe d_TM={d_probe:.4e} IOP_AC={iop_ac:.3f}")
        if iop_ac < 10.8:
            raise SystemExit(
                "ERROR: IOP still ~10 mmHg at 50× d_TM — tm_zone is bypassed, not a d_TM scale issue."
            )
        d_tm = d_probe

    lo, hi = min(d_tm, args.d_start) * 0.2, max(d_tm, args.d_start) * 20.0
    if iop_ac < args.target:
        lo = d_tm
    else:
        hi = d_tm

    best_d, best_iop, best_err = d_tm, iop_ac, abs(iop_ac - args.target)
    for i in range(1, 10):
        d_mid = math.sqrt(lo * hi)
        run_allrun(mesh=args.mesh, d_tm=d_mid, reuse=True)
        iop_ac, iop_vit = read_iop()
        err = abs(iop_ac - args.target)
        log(f"iter={i} d_TM={d_mid:.4e} IOP_AC={iop_ac:.3f} IOP_vit={iop_vit:.3f}")
        if err < best_err:
            best_d, best_iop, best_err = d_mid, iop_ac, err
        if err <= args.tol:
            log(f"OK d_TM={d_mid:.6e}  IOP_AC={iop_ac:.3f} mmHg")
            return 0
        if iop_ac < args.target:
            lo = d_mid
        else:
            hi = d_mid

    log(f"BEST d_TM={best_d:.6e} IOP_AC={best_iop:.3f} (err={best_err:.2f})")
    run_allrun(mesh=args.mesh, d_tm=best_d, reuse=True)
    return 0 if best_err <= args.tol else 1


if __name__ == "__main__":
    sys.exit(main())
