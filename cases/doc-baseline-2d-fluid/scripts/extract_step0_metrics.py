#!/usr/bin/env python3
"""Extract Step 0 metrics from a completed run."""

from __future__ import annotations

import pathlib
import sys

RHO = 995  # kg/m³ — Lamminsalo Tabela I ᵈ @ 37 °C
PA_TO_MMHG = 0.0075006
# Legacy absolute-Q target (pre velocity-inlet). Balance now vs measured inlet flux.
Q_TARGET_LEGACY = 3.0e-9 / 60.0  # m³/s (3 µL/min) — unused for balance after U-inlet


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
    probes = read_probe(fluid / "postProcessing" / "iop_probe" / "0" / "p")
    if len(probes) < 4:
        print("ERROR: iop_probe data missing", file=sys.stderr)
        sys.exit(1)

    iop_ac_r, iop_ac_l, iop_vit_r, iop_vit_l = [pkin_to_mmhg(p) for p in probes]
    delta_ac_vit = abs(((iop_ac_r + iop_ac_l) / 2) - ((iop_vit_r + iop_vit_l) / 2))

    log = fluid / "log.simpleFoam"
    q_tm = q_tm_l = q_in = q_in_l = None
    for line in reversed(log.read_text().splitlines()):
        if q_tm is None and "sum(outlet_tm) of phi" in line:
            q_tm = float(line.split("=")[-1].strip())
        if q_tm_l is None and "sum(outlet_tm_left) of phi" in line:
            q_tm_l = float(line.split("=")[-1].strip())
        if q_in is None and "sum(ac_inlet) of phi" in line:
            q_in = float(line.split("=")[-1].strip())
        if q_in_l is None and "sum(ac_inlet_left) of phi" in line:
            q_in_l = float(line.split("=")[-1].strip())
        if None not in (q_tm, q_tm_l, q_in, q_in_l):
            break

    q_out = (q_tm or 0.0) + (q_tm_l or 0.0)
    # Inlet phi is negative (into domain); use magnitude as Q_in
    q_in_total = abs(q_in or 0.0) + abs(q_in_l or 0.0)
    q_target = q_in_total if q_in_total > 0 else Q_TARGET_LEGACY
    q_err = abs(q_out - q_target) / q_target * 100.0 if q_target else float("nan")

    ncells = None
    owner = fluid / "constant" / "polyMesh" / "owner"
    if owner.exists():
        for line in owner.read_text().splitlines():
            if "nCells:" in line:
                import re
                m = re.search(r"nCells:(\d+)", line)
                if m:
                    ncells = int(m.group(1))
                break
    if ncells is None:
        for name in ("log.checkMesh.refined2", "log.checkMesh.refined", "log.checkMesh", "log.blockMesh"):
            p = fluid / name
            if p.exists():
                for line in p.read_text().splitlines():
                    if "nCells:" in line:
                        ncells = int(line.split()[-1])
                        break
            if ncells:
                break

    import re
    d_tm = None
    fv = fluid / "system" / "fvOptions"
    m = re.search(r"d\s+d\s+\[0 -2 0 0 0 0 0\]\s+\(([0-9.eE+-]+)", fv.read_text())
    if m:
        d_tm = float(m.group(1))

    print(f"nCells={ncells}")
    print(f"d_TM={d_tm:.4e}" if d_tm else "d_TM=N/A")
    print(f"IOP_AC_right={iop_ac_r:.3f} mmHg")
    print(f"IOP_AC_left={iop_ac_l:.3f} mmHg")
    print(f"IOP_AC_mean={(iop_ac_r+iop_ac_l)/2:.3f} mmHg")
    print(f"IOP_vitreous_mean={(iop_vit_r+iop_vit_l)/2:.3f} mmHg")
    print(f"delta_AC_vitreous={delta_ac_vit:.3f} mmHg")
    print(f"Q_in_total={q_in_total:.4e} m³/s")
    print(f"Q_TM_total={q_out:.4e} m³/s (target = Q_in)")
    print(f"Q_balance_error={q_err:.2f} %")


if __name__ == "__main__":
    main()
