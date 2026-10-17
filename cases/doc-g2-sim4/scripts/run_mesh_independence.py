#!/usr/bin/env python3
"""Mesh independence for doc-g2-sim4 (IVI + ACP, Robin wall, M1 reference).

Levels (coarse → fine): M5, M4, M1 (production ref), M2, M3.
Each level: baseline (simpleFoam) → experiment (pimpleFoam, IVI+ACP).
Experiment retries with smaller deltaT / Courant limit on numerical blow-up.
"""

from __future__ import annotations

import csv
import json
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
# coarse → fine
LEVELS = ("M5", "M4", "M1", "M2", "M3")
RHO = 995.0
PA_TO_MMHG = 0.0075006
IVI_T0, IVI_T1 = 5.0, 11.0
ACP_T0, ACP_T1 = 15.0, 21.0

# Fixed dt first; then adaptive Courant; then smaller fixed steps.
EXPERIMENT_ATTEMPTS: tuple[dict[str, str], ...] = (
    {"DELTA_T": "0.05", "ADJUST_TIME_STEP": "no", "MAX_CO": "100"},
    {"DELTA_T": "0.05", "ADJUST_TIME_STEP": "yes", "MAX_CO": "1.0", "MAX_DELTA_T": "0.05"},
    {"DELTA_T": "0.02", "ADJUST_TIME_STEP": "yes", "MAX_CO": "0.8", "MAX_DELTA_T": "0.02"},
    {"DELTA_T": "0.01", "ADJUST_TIME_STEP": "yes", "MAX_CO": "0.5", "MAX_DELTA_T": "0.01"},
    {"DELTA_T": "0.005", "ADJUST_TIME_STEP": "no", "MAX_CO": "50"},
    {"DELTA_T": "0.001", "ADJUST_TIME_STEP": "no", "MAX_CO": "50"},
)


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
    log = fluid / "log.checkMesh"
    for line in log.read_text().splitlines():
        if re.search(r"^\s*cells:\s+\d+", line):
            return int(line.split()[-1])
    raise RuntimeError("cells: not found in log.checkMesh")


def read_tip_cells(fluid: pathlib.Path, name: str) -> int:
    log = fluid / f"log.topoSet.{name}"
    if not log.is_file():
        return -1
    pat = rf"cellSet {name}_cells now size (\d+)"
    for line in reversed(log.read_text().splitlines()):
        m = re.search(pat, line)
        if m:
            return int(m.group(1))
    return -1


def read_d_tm(fluid: pathlib.Path) -> str:
    fv = fluid / "system/fvOptions"
    m = re.search(r"d\s+d\s+\[0 -2 0 0 0 0 0\]\s+\(([0-9.eE+-]+)", fv.read_text())
    return f"{float(m.group(1)):.3e}" if m else "N/A"


def docker_run(inner: str, log_path: pathlib.Path) -> int:
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
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w") as logf:
        proc = subprocess.run(
            cmd,
            cwd=str(REPO),
            stdout=logf,
            stderr=subprocess.STDOUT,
            text=True,
        )
    return proc.returncode


def baseline_converged(log_path: pathlib.Path) -> bool:
    if not log_path.is_file():
        return False
    text = log_path.read_text()
    return "SIMPLE solution converged" in text and "FOAM FATAL" not in text


def experiment_converged(log_path: pathlib.Path) -> bool:
    if not log_path.is_file():
        return False
    text = log_path.read_text()
    if "FOAM FATAL" in text or re.search(r"\bnan\b", text, re.I):
        return False
    if re.search(r"continuity errors.*e\+[0-9]{2,}", text):
        return False
    return bool(re.search(r"^Time = 30\s*$", text, re.M))


def attempt_label(cfg: dict[str, str]) -> str:
    parts = [f"dt={cfg.get('DELTA_T', 'default')}"]
    if cfg.get("ADJUST_TIME_STEP") == "yes":
        parts.append(f"Co≤{cfg.get('MAX_CO', '?')}")
    return ", ".join(parts)


def build_experiment_script(level: str, cfg: dict[str, str]) -> str:
    env_parts = [
        f"MESH_LEVEL={level}",
        "MODE=experiment",
        "REUSE_MESH=1",
    ]
    for key in ("DELTA_T", "ADJUST_TIME_STEP", "MAX_CO", "MAX_DELTA_T"):
        if key in cfg:
            env_parts.append(f"{key}={cfg[key]}")
    env = " ".join(env_parts)
    return f"cd /simulation/doc-g2-sim4 && {env} ./Allrun"


def run_experiment_with_retries(level: str, log_path: pathlib.Path) -> dict[str, str]:
    last_cfg: dict[str, str] = {}
    for i, cfg in enumerate(EXPERIMENT_ATTEMPTS, start=1):
        last_cfg = cfg
        label = attempt_label(cfg)
        print(f"  attempt {i}/{len(EXPERIMENT_ATTEMPTS)}: {label}", flush=True)
        attempt_log = OUT / f"{level}_experiment_attempt{i}.log"
        rc = docker_run(build_experiment_script(level, cfg), attempt_log)
        shutil.copy2(attempt_log, log_path)
        if rc == 0 and experiment_converged(attempt_log):
            print(f"  experiment OK ({label})", flush=True)
            return {"experiment_deltaT": cfg.get("DELTA_T", "0.05"), "experiment_config": label}
        print(f"  experiment failed ({label}) — retrying", flush=True)
    raise RuntimeError(
        f"{level} experiment failed after {len(EXPERIMENT_ATTEMPTS)} attempts "
        f"(last: {attempt_label(last_cfg)}) — see {log_path}"
    )


def metrics_from_probe(fluid: pathlib.Path) -> dict[str, float]:
    rows = read_iop_probe(fluid / "postProcessing" / "iop_probe" / "0" / "p")
    if not rows:
        raise RuntimeError("empty iop_probe")
    t0 = rows[0]
    t30 = min(rows, key=lambda r: abs(r[0] - 30.0))
    ivi = [r for r in rows if IVI_T0 <= r[0] <= IVI_T1]
    acp = [r for r in rows if ACP_T0 <= r[0] <= ACP_T1]
    if not ivi or not acp:
        raise RuntimeError("missing IVI or ACP phase samples")
    peak_ac = max(ivi, key=lambda r: abs(r[1] - t0[1]))
    peak_vit = max(ivi, key=lambda r: abs(r[2] - t0[2]))
    min_ac = max(acp, key=lambda r: abs(r[1] - t0[1]))
    min_vit = max(acp, key=lambda r: abs(r[2] - t0[2]))
    return {
        "IOP0_AC_mmHg": t0[1],
        "IOP0_vit_mmHg": t0[2],
        "peak_IVI_AC_mmHg": peak_ac[1],
        "peak_IVI_vit_mmHg": peak_vit[2],
        "min_ACP_AC_mmHg": min_ac[1],
        "min_ACP_vit_mmHg": min_vit[2],
        "IOP_t30_AC_mmHg": t30[1],
        "IOP_t30_vit_mmHg": t30[2],
    }


def archive_level(level: str) -> None:
    fluid = CASE / "fluid"
    dest = OUT / level
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    for name in (
        "log.checkMesh",
        "log.topoSet.iviTip",
        "log.topoSet.acpTip",
        "log.simpleFoam",
        "log.pimpleFoam",
    ):
        src = fluid / name
        if src.is_file():
            shutil.copy2(src, dest / name)
    pp = fluid / "postProcessing" / "iop_probe" / "0" / "p"
    if pp.is_file():
        shutil.copy2(pp, dest / "iop_probe_p.txt")
    metrics_path = CASE / "results" / "metrics.txt"
    if metrics_path.is_file():
        shutil.copy2(metrics_path, dest / "metrics.txt")


def run_level(level: str) -> dict:
    fluid = CASE / "fluid"
    log_base = OUT / f"{level}_baseline.log"
    log_exp = OUT / f"{level}_experiment.log"

    print(f"\n===== {level} baseline =====", flush=True)
    rc = docker_run(
        f"cd /simulation/doc-g2-sim4 && ./Allclean && "
        f"MESH_LEVEL={level} MODE=baseline ./Allrun",
        log_base,
    )
    if rc != 0:
        raise RuntimeError(f"{level} baseline failed — see {log_base}")
    if not baseline_converged(log_base):
        raise RuntimeError(f"{level} baseline did not converge — see {log_base}")

    print(f"===== {level} experiment (IVI+ACP) =====", flush=True)
    exp_meta = run_experiment_with_retries(level, log_exp)
    archive_level(level)

    row = {
        "level": level,
        "nCells": read_ncells(fluid),
        "ivi_tip_cells": read_tip_cells(fluid, "iviTip"),
        "acp_tip_cells": read_tip_cells(fluid, "acpTip"),
        "d_TM": read_d_tm(fluid),
        "baseline_converged": True,
        "experiment_converged": True,
        **exp_meta,
    }
    row.update(metrics_from_probe(fluid))
    return row


def pct_change(a: float, b: float) -> float:
    if abs(b) < 1e-12:
        return float("nan")
    return abs(a - b) / abs(b) * 100.0


def gci_triplet(
    rows: list[dict],
    key: str,
    *,
    fine: str,
    mid: str,
    coarse: str,
) -> str:
    by = {r["level"]: r for r in rows}
    f1, f2, f3 = by[fine][key], by[mid][key], by[coarse][key]
    n1, n2, n3 = by[fine]["nCells"], by[mid]["nCells"], by[coarse]["nCells"]
    r21 = (n1 / n2) ** (1.0 / 3.0)
    r32 = (n2 / n3) ** (1.0 / 3.0)
    eps21 = f2 - f1
    eps32 = f3 - f2
    lines = [
        f"{coarse} → {mid} → {fine}: "
        f"{f3:.4f} → {f2:.4f} → {f1:.4f}  "
        f"(N {n3:,} → {n2:,} → {n1:,})",
        f"r21 ≈ {r21:.3f}, r32 ≈ {r32:.3f}",
    ]
    if abs(eps21) < 1e-9 or abs(eps32) < 1e-9:
        lines.append("differences too small for GCI.")
        return "\n".join(lines)
    p = abs(math.log(abs(eps32 / eps21)) / math.log(r21))
    Fs = 1.25
    gci_fine = Fs * abs(eps21) / (r21**p - 1.0) / abs(f1) * 100.0
    lines += [
        f"Observed order p ≈ {p:.3f}",
        f"Fine-grid GCI ({fine}) ≈ {gci_fine:.3f}%",
        f"{mid} → {fine} change: {pct_change(f1, f2):.3f}%",
    ]
    return "\n".join(lines)


def write_report(levels: tuple[str, ...], rows: list[dict]) -> None:
    fields = [
        "level",
        "nCells",
        "ivi_tip_cells",
        "acp_tip_cells",
        "d_TM",
        "experiment_deltaT",
        "experiment_config",
        "IOP0_AC_mmHg",
        "IOP0_vit_mmHg",
        "peak_IVI_AC_mmHg",
        "peak_IVI_vit_mmHg",
        "min_ACP_AC_mmHg",
        "min_ACP_vit_mmHg",
        "IOP_t30_AC_mmHg",
        "IOP_t30_vit_mmHg",
        "baseline_converged",
        "experiment_converged",
    ]
    csv_path = OUT / "results.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    by = {r["level"]: r for r in rows}
    m1 = by.get("M1")
    m2 = by.get("M2")
    m3 = by.get("M3")
    fine_decision = "N/A"
    if m1 and m2 and m3:
        d23 = pct_change(m3["peak_IVI_AC_mmHg"], m2["peak_IVI_AC_mmHg"])
        if d23 < 1.0:
            fine_decision = (
                f"M2 vs M3 peak IVI AC differs by {d23:.2f}% (<1%). **M2 sufficient**."
            )
        elif d23 < 2.0:
            fine_decision = (
                f"M2 vs M3 peak IVI AC differs by {d23:.2f}% (1–2%). Prefer **M2**."
            )
        else:
            fine_decision = f"M2→M3 peak IVI AC change {d23:.2f}% (>2%). Prefer **M3**."

    coarse_decision = "N/A"
    m4 = by.get("M4")
    m5 = by.get("M5")
    if m1 and m4 and m5:
        d54 = pct_change(m4["peak_IVI_AC_mmHg"], m5["peak_IVI_AC_mmHg"])
        d41 = pct_change(m1["peak_IVI_AC_mmHg"], m4["peak_IVI_AC_mmHg"])
        coarse_decision = (
            f"M5→M4 peak IVI AC change {d54:.2f}%; "
            f"M4→M1 change {d41:.2f}%. "
            f"Coarse meshes {'acceptable' if d41 < 3.0 else 'may bias IVI peak'} vs M1."
        )

    def row_line(r: dict) -> str:
        return (
            f"| {r['level']} | {r['nCells']:,} | {r['ivi_tip_cells']} | {r['acp_tip_cells']} | "
            f"{r.get('experiment_deltaT', '?')} | {r['IOP0_AC_mmHg']:.3f} | "
            f"{r['peak_IVI_AC_mmHg']:.2f} | {r['peak_IVI_vit_mmHg']:.2f} | "
            f"{r['min_ACP_AC_mmHg']:.2f} | {r['min_ACP_vit_mmHg']:.2f} |"
        )

    report = f"""# Mesh-independence — G2 Sim 4 (IVI + ACP, Robin wall)

## Setup

Bulk G2-fluid meshes from doc-g2-sim1. **M1 = production reference**.
Each level: `MODE=baseline` (simpleFoam) → `MODE=experiment` (pimpleFoam, t = 30 s).
Experiment retries smaller `deltaT` / Courant limit on blow-up.

| Level | Cells | ivi_tip | acp_tip | exp Δt | IOP₀ AC | Peak IVI AC | Peak IVI vit | Min ACP AC | Min ACP vit |
|-------|------:|--------:|--------:|-------:|--------:|------------:|-------------:|-----------:|------------:|
"""
    for level in levels:
        report += row_line(by[level]) + "\n"

    if {"M1", "M2", "M3"}.issubset(by):
        report += f"""
## Grid convergence — M1 → M2 → M3

### Peak IVI AC [mmHg]

{gci_triplet(rows, "peak_IVI_AC_mmHg", fine="M3", mid="M2", coarse="M1")}

### Min ACP AC [mmHg]

{gci_triplet(rows, "min_ACP_AC_mmHg", fine="M3", mid="M2", coarse="M1")}

**Decision:** {fine_decision}
"""

    if {"M5", "M4", "M1"}.issubset(by):
        report += f"""
## Grid convergence — coarse side (M5 → M4 → M1)

### Peak IVI AC [mmHg]

{gci_triplet(rows, "peak_IVI_AC_mmHg", fine="M1", mid="M4", coarse="M5")}

**Coarse-side decision:** {coarse_decision}
"""

    report += """
## Recommended mesh

**Production reference: M1.** Confirm M2/M3 changes are <1–2% on peak IVI and min ACP.
"""
    (OUT / "REPORT.md").write_text(report)
    print(report)
    print(f"Wrote {OUT / 'results.csv'}")
    print(f"Wrote {OUT / 'REPORT.md'}")


def main() -> None:
    only = os.environ.get("LEVELS")
    levels = tuple(x.strip() for x in only.split(",") if x.strip()) if only else LEVELS

    OUT.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    for level in levels:
        sim1_msh = REPO / "cases" / "doc-g2-sim1" / "geometry" / f"eye_g2_fluid_lamminsalo_{level}.msh"
        if not sim1_msh.is_file():
            raise RuntimeError(
                f"missing {sim1_msh}\n"
                f"Generate: cases/doc-g2-sim1/scripts/gen_mesh_g2_fluid.sh {level}"
            )
        row = run_level(level)
        rows.append(row)
        print(row, flush=True)
        write_report(levels=tuple(r["level"] for r in rows), rows=rows)
        (OUT / "progress.json").write_text(json.dumps(rows, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
