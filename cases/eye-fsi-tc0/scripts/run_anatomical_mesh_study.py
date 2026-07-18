#!/usr/bin/env python3
"""Anatomical G1 mesh independence (M1/M2/M3) with fixed d_TM.

Meshes are generated on the host; solves run in Docker (cases/ mount only).
"""

from __future__ import annotations

import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

CASE = Path(__file__).resolve().parent.parent
REPO = CASE.parent.parent
PY = REPO / ".venv-geom" / "bin" / "python"
GEN = REPO / "brunaStuff" / "gen_lamminsalo_2d.py"
D_TM = "1.257839e+14"
LEVELS = ("M1", "M2", "M3")


def rebuild_mesh(level: str) -> None:
    print(f"+ rebuild {level}", flush=True)
    subprocess.check_call(
        [str(PY), str(GEN), "--mesh", "--mesh-level", level],
        cwd=REPO,
    )


def run_docker(cmd: str) -> None:
    full = f"cd /simulation/eye-fsi-tc0 && {cmd}"
    print("+", full, flush=True)
    proc = subprocess.run(
        ["docker", "compose", "run", "--rm", "fsi", "bash", "-lc", full],
        cwd=REPO,
        text=True,
    )
    if proc.returncode != 0:
        raise SystemExit(f"command failed: {cmd}")


def metrics() -> dict:
    out = subprocess.check_output(
        [sys.executable, str(CASE / "scripts" / "extract_step0_metrics.py")],
        text=True,
    )
    d: dict = {"raw": out}
    for line in out.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip()
    log = (CASE / "fluid" / "log.simpleFoam").read_text()
    qr = ql = None
    for line in reversed(log.splitlines()):
        if qr is None and "sum(outlet_tm) of phi" in line and "left" not in line:
            qr = float(line.split("=")[-1])
        if ql is None and "sum(outlet_tm_left) of phi" in line:
            ql = float(line.split("=")[-1])
        if qr is not None and ql is not None:
            break
    d["Q_R"] = qr
    d["Q_L"] = ql
    cm = (CASE / "fluid" / "log.checkMesh").read_text()
    for z in ("tm_zone", "tm_zone_left"):
        m = re.search(rf"{z}\s+(\d+)", cm)
        d[z] = int(m.group(1)) if m else None
    return d


def main() -> None:
    rows = []
    log_path = CASE / "mesh_study_anatomical.log"
    with log_path.open("w") as log:
        log.write(f"# anatomical mesh study {datetime.now(timezone.utc).isoformat()}\n")
        log.write(f"# fixed d_TM={D_TM}\n")
        for level in LEVELS:
            rebuild_mesh(level)
            run_docker(
                f"./Allclean.anatomical && MESH_LEVEL={level} D_TM={D_TM} ./Allrun.anatomical"
            )
            m = metrics()
            iop = float(m.get("IOP_AC_mean", "nan").split()[0])
            qerr = float(m.get("Q_balance_error", "nan").split()[0])
            ncells = int(m.get("nCells", "0"))
            qr, ql = m["Q_R"], m["Q_L"]
            split = 100.0 * qr / (qr + ql) if qr and ql else float("nan")
            row = {
                "level": level,
                "nCells": ncells,
                "tm_R": m["tm_zone"],
                "tm_L": m["tm_zone_left"],
                "IOP": iop,
                "Qerr": qerr,
                "Q_R_pct": split,
            }
            rows.append(row)
            line = (
                f"{level} nCells={ncells} tm={m['tm_zone']}/{m['tm_zone_left']} "
                f"IOP={iop:.3f} Qerr={qerr:.2f}% Q_R%={split:.1f}\n"
            )
            print(line, end="", flush=True)
            log.write(line)

        spread = max(r["IOP"] for r in rows) - min(r["IOP"] for r in rows)
        log.write(f"IOP_spread_mmHg={spread:.3f} ({100 * spread / 15:.1f}% of 15)\n")
        print(f"IOP spread = {spread:.3f} mmHg ({100 * spread / 15:.1f}% of target)")

    md = CASE / "mesh_study_anatomical.md"
    lines = [
        "# Anatomical G1 — mesh independence (Sim 1)",
        "",
        f"Fixed `d_TM = {D_TM}` m⁻² (calibrated on prior M1 baseline).",
        "",
        "| Level | nCells | TM R/L cells | IOP₀ [mmHg] | Q err [%] | Q_right [%] |",
        "|-------|--------|--------------|-------------|-----------|-------------|",
    ]
    for r in rows:
        lines.append(
            f"| {r['level']} | {r['nCells']} | {r['tm_R']}/{r['tm_L']} | "
            f"{r['IOP']:.3f} | {r['Qerr']:.2f} | {r['Q_R_pct']:.1f} |"
        )
    spread = max(r["IOP"] for r in rows) - min(r["IOP"] for r in rows)
    lines += [
        "",
        f"**IOP spread** (fixed d_TM): **{spread:.3f} mmHg** ({100 * spread / 15:.1f}% of 15).",
        "",
        "Acceptance (legacy Sim1): spread ≲ 5%. Recalibrate `d_TM` per level if needed.",
        "",
    ]
    md.write_text("\n".join(lines))
    print(f"Wrote {md}")


if __name__ == "__main__":
    main()
