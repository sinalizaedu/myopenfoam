#!/usr/bin/env python3
"""Record passive pimpleFoam baseline IOP and d_TM after equilibration."""

from __future__ import annotations

import re
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


def read_d_tm(case: Path) -> float | None:
    fv = case / "fluid/system/fvOptions"
    if not fv.is_file():
        return None
    m = re.search(r"d\s+d\s+\[0 -2 0 0 0 0 0\]\s+\(([0-9.eE+-]+)", fv.read_text())
    return float(m.group(1)) if m else None


def main() -> None:
    case = Path(__file__).resolve().parents[1]
    fluid = case / "fluid"
    files = list(fluid.glob("postProcessing/iop_probe/*/p"))
    if not files:
        print("WARNING: no baseline IOP data — skip")
        return

    def _tkey(p: Path) -> float:
        try:
            return float(p.parent.name)
        except ValueError:
            return -1.0

    t, vals = read_last_probe_row(max(files, key=_tkey))
    iop_ac = 0.5 * (vals[0] + vals[1]) * RHO * PA_TO_MMHG
    iop_vit = 0.5 * (vals[2] + vals[3]) * RHO * PA_TO_MMHG
    d_tm = read_d_tm(case)
    d_tm_str = f"{d_tm:.6e}" if d_tm is not None else "null"
    cal = case / "calibration"
    cal.mkdir(exist_ok=True)
    out = cal / "baseline_iop.yaml"
    out.write_text(
        f"""# Verified after MODE=baseline pimpleFoam — IOP set by d_TM in fvOptions
case: {case.name}
time: {t}
d_TM: {d_tm_str}
P_TM_Torr: {P_TM_TORR}
iop_ac_mmHg: {iop_ac:.4f}
iop_vit_mmHg: {iop_vit:.4f}
solver: pimpleFoam
deltaT: 0.05
# Recalibrate IOP: change d_TM (D_TM= env or scripts/set_d_tm.py) and re-run baseline
"""
    )
    print(f"Wrote {out}  d_TM={d_tm_str}  IOP_AC={iop_ac:.3f} mmHg")


if __name__ == "__main__":
    main()
