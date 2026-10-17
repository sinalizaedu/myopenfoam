#!/usr/bin/env python3
"""Extract Step 0 metrics from a completed G2-fluid run (1/4 eye)."""

from __future__ import annotations

import pathlib
import re
import sys

RHO = 995  # kg/m³
PA_TO_MMHG = 0.0075006
Q_TARGET_QUARTER = 3.0e-9 / 60.0 / 4.0  # 1.25e-11 m³/s
Q_TARGET_FULL = 3.0e-9 / 60.0


def pkin_to_mmhg(p: float) -> float:
    return p * RHO * PA_TO_MMHG


def read_probe(path: pathlib.Path) -> list[float]:
    vals = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith("#") or not line:
            continue
        parts = line.split()
        if len(parts) >= 5:
            vals = [float(x) for x in parts[1:5]]
        elif len(parts) >= 2:
            vals = [float(parts[1])]
    return vals


def main():
    case = pathlib.Path(__file__).resolve().parent.parent
    fluid = case / "fluid"
    probe_files = list(fluid.glob("postProcessing/iop_probe/*/p"))
    if not probe_files:
        print("ERROR: iop_probe data missing", file=sys.stderr)
        sys.exit(1)

    def _tkey(p: pathlib.Path) -> float:
        try:
            return float(p.parent.name)
        except ValueError:
            return -1.0

    probes = read_probe(max(probe_files, key=_tkey))
    if len(probes) < 4:
        print("ERROR: iop_probe data missing", file=sys.stderr)
        sys.exit(1)

    iop_ac_0, iop_ac_mid, iop_vit_0, iop_vit_mid = [pkin_to_mmhg(p) for p in probes]
    iop_ac = 0.5 * (iop_ac_0 + iop_ac_mid)
    iop_vit = 0.5 * (iop_vit_0 + iop_vit_mid)

    log = fluid / "log.simpleFoam"
    q_tm = None
    for line in reversed(log.read_text().splitlines()):
        if q_tm is None and "sum(outlet_tm) of phi" in line:
            q_tm = float(line.split("=")[-1].strip())
            break
    q_out = q_tm or 0.0
    q_err = abs(q_out - Q_TARGET_QUARTER) / Q_TARGET_QUARTER * 100.0

    ncells = None
    for name in ("log.checkMesh",):
        p = fluid / name
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            if "nCells:" in line:
                ncells = int(line.split()[-1])
                break
            m = re.search(r"^\s*cells:\s+(\d+)", line)
            if m:
                ncells = int(m.group(1))
                break
        if ncells:
            break

    d_tm = None
    fv = fluid / "system" / "fvOptions"
    m = re.search(r"d\s+d\s+\[0 -2 0 0 0 0 0\]\s+\(([0-9.eE+-]+)", fv.read_text())
    if m:
        d_tm = float(m.group(1))

    # Convergence: last residual lines
    converged = False
    last_time = None
    if log.exists():
        text = log.read_text()
        converged = "SIMPLE solution converged" in text or "solution converged" in text.lower()
        for line in reversed(text.splitlines()):
            if line.startswith("Time ="):
                last_time = line.split("=")[-1].strip()
                break

    print(f"nCells={ncells}")
    print(f"d_TM={d_tm:.4e}" if d_tm else "d_TM=N/A")
    print(f"IOP_AC={iop_ac:.3f} mmHg  (sym0={iop_ac_0:.3f}, mid={iop_ac_mid:.3f})")
    print(f"IOP_vitreous={iop_vit:.3f} mmHg  (sym0={iop_vit_0:.3f}, mid={iop_vit_mid:.3f})")
    print(f"delta_AC_vitreous={abs(iop_ac - iop_vit):.3f} mmHg")
    print(f"Q_TM={q_out:.4e} m³/s (quarter target {Q_TARGET_QUARTER:.4e})")
    print(f"Q_full_eye_equiv={4.0 * q_out:.4e} m³/s (full target {Q_TARGET_FULL:.4e})")
    print(f"Q_balance_error={q_err:.2f} %")
    print(f"last_time={last_time}")
    print(f"converged={converged}")


if __name__ == "__main__":
    main()
