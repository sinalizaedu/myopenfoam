#!/usr/bin/env python3
"""
Step 0 calibration + mesh study driver.
Runs Allclean.step0 / Allrun.step0 in Docker, sweeps d_TM, computes GCI.
"""

from __future__ import annotations

import math
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

CASE = Path(__file__).resolve().parent.parent
REPO = CASE.parent.parent
RHO = 995.0
PA_TO_MMHG = 0.0075006
Q_TARGET = 3.0e-9 / 60.0


def run_docker(cmd: str) -> subprocess.CompletedProcess:
    full = (
        f"cd /simulation/eye-fsi-tc0 && {cmd}"
    )
    return subprocess.run(
        [
            "docker", "compose", "run", "--rm", "fsi",
            "bash", "-lc", full,
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
    )


def read_iop_mmhg() -> float | None:
    probe = CASE / "fluid" / "postProcessing" / "iop_probe" / "0" / "p"
    if not probe.exists():
        return None
    last = None
    for line in probe.read_text().splitlines():
        line = line.strip()
        if line.startswith("#") or not line:
            continue
        parts = line.split()
        if len(parts) >= 2:
            try:
                last = float(parts[1])
            except ValueError:
                pass
    if last is None:
        return None
    return last * RHO * PA_TO_MMHG


def read_ncells() -> int | None:
    fluid = CASE / "fluid"
    for name in (
        "log.checkMesh.refined2",
        "log.checkMesh.refined",
        "log.checkMesh",
        "log.blockMesh",
    ):
        log = fluid / name
        if not log.exists():
            continue
        for line in log.read_text().splitlines():
            if "nCells:" in line:
                return int(line.split()[-1])
    return None


def read_q_tm() -> float | None:
    log = CASE / "fluid" / "log.simpleFoam"
    if not log.exists():
        return None
    for line in reversed(log.read_text().splitlines()):
        if "flowRateTM =" in line:
            try:
                return float(line.split()[-1])
            except ValueError:
                return None
    return None


def gci(phi1: float, phi2: float, phi3: float, r: float = 2.0) -> tuple[float, float]:
    """ASME V&V 20 style GCI from three mesh levels (fine→coarse: phi3, phi2, phi1)."""
    eps21 = phi2 - phi3
    eps32 = phi1 - phi2
    if abs(eps21) < 1e-12 or abs(eps32) < 1e-12:
        return float("nan"), float("nan")
    r21 = r
    r32 = r
    p = abs(math.log(abs(eps32 / eps21)) / math.log(r21))
    if p < 0.01:
        p = 1.0
    fs = abs((r21**p - 1.0) / (2.0 * p * eps21)) if abs(eps21) > 1e-12 else float("nan")
    gci_fine = 1.25 * fs * abs(eps32) / (phi3 if abs(phi3) > 1e-12 else 1.0) * 100.0
    return gci_fine, p


def log_run(msg: str) -> None:
    path = CASE / "run_log_step0.txt"
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with path.open("a") as fh:
        fh.write(f"{ts}  {msg}\n")
    print(msg)


def calibrate(mesh_level: str = "M1", d_start: float = 3.08e14) -> float:
    """Binary search d_TM to hit IOP ~ 15 mmHg."""
    lo, hi = d_start * 0.3, d_start * 3.0
    best_d, best_iop, best_err = d_start, 0.0, 1e9

    for i in range(12):
        d_mid = math.sqrt(lo * hi)
        d_str = f"{d_mid:.6e}"
        proc = run_docker(
            f"./Allclean.step0 && MESH_LEVEL={mesh_level} D_TM={d_str} ./Allrun.step0"
        )
        if proc.returncode != 0:
            # simpleFoam may complete but post-summary grep can fail on older Allrun; verify probe
            iop_check = read_iop_mmhg()
            if iop_check is not None:
                log_run(f"CALIB warn iter={i} d_TM={d_str} rc={proc.returncode} IOP={iop_check:.3f} (probe OK)")
            else:
                tail = (proc.stdout + proc.stderr)[-800:]
                log_run(f"CALIB FAIL iter={i} d_TM={d_str} tail={tail}")
                raise RuntimeError(f"Allrun.step0 failed at d_TM={d_str}")

        iop = read_iop_mmhg()
        if iop is None:
            raise RuntimeError("Could not read IOP probe")

        err = abs(iop - 15.0)
        log_run(f"CALIB iter={i} d_TM={d_mid:.4e} IOP={iop:.3f} mmHg mesh={mesh_level}")
        calib = CASE / "calibration_step0.log"
        with calib.open("a") as fh:
            fh.write(f"{mesh_level}\t{d_mid:.6e}\t{iop:.4f}\t{read_ncells()}\n")

        if err < best_err:
            best_d, best_iop, best_err = d_mid, iop, err

        if abs(iop - 15.0) < 0.25:
            return d_mid

        # IOP low → increase d_TM (more TM resistance → higher AC pressure)
        if iop < 15.0:
            lo = d_mid
        else:
            hi = d_mid

    log_run(f"CALIB best d_TM={best_d:.4e} IOP={best_iop:.3f} (err={best_err:.2f})")
    return best_d


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"

    if mode == "run":
        mesh = sys.argv[2] if len(sys.argv) > 2 else "M1"
        d_tm = sys.argv[3] if len(sys.argv) > 3 else ""
        extra = f" D_TM={d_tm}" if d_tm else ""
        proc = run_docker(f"./Allclean.step0 && MESH_LEVEL={mesh} {extra} ./Allrun.step0".strip())
        print(proc.stdout)
        if proc.returncode != 0:
            print(proc.stderr, file=sys.stderr)
            sys.exit(proc.returncode)
        iop = read_iop_mmhg()
        print(f"IOP={iop:.3f} mmHg  nCells={read_ncells()}  Q_TM={read_q_tm()}")
        return

    if mode == "mesh-study":
        results = []
        d_tm = 3.08e14
        for level in ("M1", "M2", "M3"):
            d_tm = calibrate(level, d_tm)
            iop = read_iop_mmhg()
            n = read_ncells()
            results.append((level, n, iop, d_tm))
            log_run(f"MESH {level}: nCells={n} IOP={iop:.3f} d_TM={d_tm:.4e}")

        if len(results) == 3:
            iops = [r[2] for r in reversed(results)]  # fine M3, medium M2, coarse M1
            gci_val, p_obs = gci(iops[0], iops[1], iops[2])
            log_run(f"GCI(IOP,fine)={gci_val:.2f}%  p={p_obs:.2f}")
        return

    # full: calibrate M1 then mesh study
    calibrate("M1")
    subprocess.check_call([sys.executable, __file__, "mesh-study"])


if __name__ == "__main__":
    main()
