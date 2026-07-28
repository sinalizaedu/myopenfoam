#!/usr/bin/env python3
"""Record steady baseline IOP and d_TM after simpleFoam (verify calibration)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

RHO = 995.0
PA_TO_MMHG = 0.0075006
P_TM_TORR = 10.0


def read_last_probe_row(path: Path) -> tuple[float, list[float]]:
    last = None
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith("#") or not line:
            continue
        parts = line.split()
        if len(parts) >= 5:
            last = (float(parts[0]), [float(x) for x in parts[1:5]])
    if last is None:
        raise SystemExit(f"ERROR: no probe data in {path}")
    return last


def iop_from_logs(case: Path) -> tuple[float, float] | None:
    for rel in (
        "fluid/log.simpleFoam",
        "results/log.baseline_run.txt",
        "log.baseline_run.txt",
    ):
        path = case / rel
        if not path.is_file():
            continue
        iop_ac = iop_vit = None
        for line in reversed(path.read_text().splitlines()):
            if iop_ac is None and line.startswith("IOP_AC="):
                m = re.search(r"IOP_AC=([\d.]+)", line)
                if m:
                    iop_ac = float(m.group(1))
            if iop_vit is None and line.startswith("IOP_vitreous="):
                m = re.search(r"IOP_vitreous=([\d.]+)", line)
                if m:
                    iop_vit = float(m.group(1))
            if iop_ac is not None and iop_vit is not None:
                return iop_ac, iop_vit
    return None


def read_d_tm(case: Path) -> float | None:
    fv = case / "fluid/system/fvOptions"
    if not fv.is_file():
        return None
    m = re.search(r"d\s+d\s+\[0 -2 0 0 0 0 0\]\s+\(([0-9.eE+-]+)", fv.read_text())
    return float(m.group(1)) if m else None


def main() -> None:
    case = Path(__file__).resolve().parents[1]
    fluid = case / "fluid"
    iop_ac = iop_vit = None
    t = 0.0

    probe = fluid / "postProcessing" / "iop_probe" / "0" / "p"
    if not probe.is_file():
        files = sorted(fluid.glob("postProcessing/iop_probe/*/p"))
        if files:
            probe = files[-1]
    if probe.is_file():
        t, vals = read_last_probe_row(probe)
        ac = 0.5 * (vals[0] + vals[1])
        vit = 0.5 * (vals[2] + vals[3])
        iop_ac = ac * RHO * PA_TO_MMHG
        iop_vit = vit * RHO * PA_TO_MMHG

    if iop_ac is None:
        parsed = iop_from_logs(case)
        if not parsed:
            print("WARNING: no baseline IOP data — skip", file=sys.stderr)
            return
        iop_ac, iop_vit = parsed

    d_tm = read_d_tm(case)
    d_tm_str = f"{d_tm:.6e}" if d_tm is not None else "null"
    cal = case / "calibration"
    cal.mkdir(exist_ok=True)
    out = cal / "baseline_iop.yaml"
    text = f"""# Verified after MODE=baseline simpleFoam — IOP set by d_TM in fvOptions
case: {case.name}
time: {t}
d_TM: {d_tm_str}
P_TM_Torr: {P_TM_TORR}
iop_ac_mmHg: {iop_ac:.4f}
iop_vit_mmHg: {iop_vit:.4f}
# Recalibrate IOP: change d_TM (D_TM= env or scripts/set_d_tm.py) and re-run baseline
"""
    out.write_text(text)
    print(f"Wrote {out}  d_TM={d_tm_str}  IOP_AC={iop_ac:.3f} mmHg")


if __name__ == "__main__":
    main()
