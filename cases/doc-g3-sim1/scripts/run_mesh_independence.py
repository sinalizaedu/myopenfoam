#!/usr/bin/env python3
"""G3 FSI mesh-independence: M1/M2/M3 fluid baseline + one-step FSI snapshot."""

from __future__ import annotations

import csv
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
LEVELS = ("M1", "M2", "M3")
N_THETA = {"M1": 6, "M2": 10, "M3": 16}
FSI_MAX_TIME = os.environ.get("FSI_MAX_TIME", "0.01")
GEN = REPO / ".venv-geom" / "bin" / "python"
GEN_SCRIPT = REPO / "brunaStuff" / "gen_lamminsalo_g2.py"


def ensure_meshes() -> None:
    for level in LEVELS:
        for kind in ("fluid", "solid"):
            suffix = "fluid" if kind == "fluid" else "solid"
            path = CASE / "geometry" / f"eye_g2_{suffix}_lamminsalo_{level}.msh"
            if path.exists():
                continue
            if not GEN.exists():
                raise RuntimeError(f"missing {path} and no .venv-geom on host")
            flags = ["--mesh"] if kind == "fluid" else ["--mesh-solid"]
            print(f"Generating {path.name} on host...", flush=True)
            subprocess.run(
                [
                    str(GEN),
                    str(GEN_SCRIPT),
                    "--case",
                    "doc-g3-sim1",
                    *flags,
                    "--mesh-level",
                    level,
                ],
                cwd=str(REPO),
                check=True,
            )


def docker_run(inner: str, log_path: pathlib.Path) -> None:
    cmd = ["docker", "compose", "run", "--rm", "fsi", "bash", "-lc", inner]
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w") as logf:
        proc = subprocess.run(cmd, cwd=str(REPO), stdout=logf, stderr=subprocess.STDOUT, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"failed — see {log_path}")


def parse_metrics(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def run_level(level: str) -> dict:
    dest = OUT / level
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    print(f"\n===== {level}: fluid baseline =====", flush=True)
    inner_fluid = f"cd /simulation/doc-g3-sim1 && ./Allclean && MESH_LEVEL={level} MODE=fluid ./Allrun"
    docker_run(inner_fluid, dest / "log.fluid.Allrun.txt")

    shutil.copy2(CASE / "fluid" / "log.simpleFoam", dest / "log.simpleFoam")
    shutil.copy2(CASE / "fluid" / "log.checkMesh", dest / "log.fluid.checkMesh")
    fluid_metrics = subprocess.run(
        ["python3", "scripts/extract_step0_metrics.py"],
        cwd=str(CASE),
        capture_output=True,
        text=True,
        env={**os.environ, "MESH_LEVEL": level},
    )
    (dest / "metrics_fluid.txt").write_text(fluid_metrics.stdout)
    mf = parse_metrics(fluid_metrics.stdout)

    print(f"===== {level}: FSI snapshot (t={FSI_MAX_TIME}s) =====", flush=True)
    inner_fsi = (
        f"cd /simulation/doc-g3-sim1 && "
        f"MESH_LEVEL={level} MODE=fsi SKIP_MESH_IMPORT=1 FLUID_PREWARM=0 "
        f"FSI_MAX_TIME={FSI_MAX_TIME} ./Allrun"
    )
    docker_run(inner_fsi, dest / "log.fsi.Allrun.txt")

    for name in ("log.pimpleFoam", "log.solids4Foam"):
        p = CASE / ("fluid" if "pimple" in name else "solid") / name
        if p.exists():
            shutil.copy2(p, dest / name)
    if (CASE / "solid" / "log.checkMesh").exists():
        shutil.copy2(CASE / "solid" / "log.checkMesh", dest / "log.solid.checkMesh")

    fsi_metrics = subprocess.run(
        ["python3", "scripts/extract_fsi_metrics.py"],
        cwd=str(CASE),
        capture_output=True,
        text=True,
        env={**os.environ, "MESH_LEVEL": level},
    )
    (dest / "metrics_fsi.txt").write_text(fsi_metrics.stdout)
    ms = parse_metrics(fsi_metrics.stdout)

    row = {
        "level": level,
        "n_theta": N_THETA[level],
        "nCells_fluid": mf.get("nCells", ms.get("nCells_fluid", "")),
        "nCells_solid": ms.get("nCells_solid", ""),
        "IOP_AC_mmHg": mf.get("IOP_AC", "").split()[0],
        "Q_TM": mf.get("Q_TM", "").split()[0],
        "D_max_um": ms.get("D_max_um", "N/A").split()[0],
        "mapping_max_m": ms.get("mapping_max_m", "N/A").split()[0],
        "fsi_active_faces": ms.get("fsi_active_faces_solid", ""),
        "wall_faces": ms.get("wall_faces", ""),
        "fsi_ok": ms.get("fsi_coupling_ok", "False"),
    }
    return row


def pct(a: float, b: float) -> float:
    return abs(a - b) / abs(b) * 100.0 if b else float("nan")


def write_report(rows: list[dict]) -> None:
    def f(key: str, i: int) -> float:
        try:
            return float(rows[i][key])
        except (KeyError, ValueError):
            return float("nan")

    iops = [f("IOP_AC_mmHg", i) for i in range(3)]
    dmax = [f("D_max_um", i) for i in range(3)]

    lines = [
        "# Mesh-independence — G3 Sim 1 (G2-fluid + G2-solid FSI)",
        "",
        "## Setup",
        "",
        "Structured OCC revolve (`n_θ` = 6 / 10 / 16), same porous coeffs as G2 Sim 1",
        "(`d_TM = 7.779×10¹⁴`, IOP₀ target ≈ 15 mmHg).",
        "",
        "Per level:",
        "1. `MODE=fluid` — rigid-wall steady IOP₀",
        f"2. `MODE=fsi` — one-way Force, `FSI_MAX_TIME={FSI_MAX_TIME}` s (after fluid warm state)",
        "",
        "| Level | n_θ | nCells fluid | nCells solid | IOP [mmHg] | Q_TM [m³/s] | |D|_max fsi [µm] | map max [m] | FSI ok |",
        "|-------|----:|-------------:|-------------:|-----------:|------------:|----------------:|------------:|:------:|",
    ]
    for r in rows:
        lines.append(
            f"| {r['level']} | {r['n_theta']} | {r['nCells_fluid']} | {r['nCells_solid']} | "
            f"{r['IOP_AC_mmHg']} | {r['Q_TM']} | {r['D_max_um']} | {r['mapping_max_m']} | {r['fsi_ok']} |"
        )

    lines += [
        "",
        "## Grid convergence (fluid IOP)",
        "",
        f"- M1 → M2: **{pct(iops[1], iops[0]):.2f}%**",
        f"- M2 → M3: **{pct(iops[2], iops[1]):.2f}%**",
        f"- M1 → M3: **{pct(iops[2], iops[0]):.2f}%**",
        "",
        "## FSI snapshot (|D|_max on solid after coupled step)",
        "",
    ]
    if all(math.isfinite(x) and x > 0 for x in dmax[:2]):
        lines.append(f"- M1 → M2: **{pct(dmax[1], dmax[0]):.2f}%**")
    elif all(x == 0 for x in dmax):
        lines.append("- All levels: |D|_max ≈ 0 µm (one 0.01 s step; solid still at rest).")
    if all(math.isfinite(x) and x > 0 for x in dmax[1:]):
        lines.append(f"- M2 → M3: **{pct(dmax[2], dmax[1]):.2f}%**")
    lines += [
        "",
        "## Decision",
        "",
    ]

    d_iop23 = pct(iops[2], iops[1]) if all(math.isfinite(x) for x in iops[1:3]) else float("nan")
    if d_iop23 < 1.0:
        rec = "**M2** for production (fluid IOP within 1% of M3; matches G2-fluid study)."
    elif d_iop23 < 2.0:
        rec = "**M2** engineering default; **M3** if reporting sub-percent IOP."
    else:
        rec = "**M3** for fluid IOP; re-check FSI |D| before long coupled runs."

    lines.append(rec)
    lines += [
        "",
        "Solid mesh remains **7 disconnected regions** — |D|_max is a patch-local smoke metric,",
        "not a converged structural solution.",
        "",
        "## Reproduce",
        "",
        "```bash",
        ".venv-geom/bin/python brunaStuff/gen_lamminsalo_g2.py \\",
        "  --case doc-g3-sim1 --mesh --mesh-solid --mesh-level M1  # repeat M2,M3",
        "python3 cases/doc-g3-sim1/scripts/run_mesh_independence.py",
        "```",
    ]

    (OUT / "REPORT.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ensure_meshes()
    rows = []
    for level in LEVELS:
        rows.append(run_level(level))
        print(rows[-1], flush=True)

    csv_path = OUT / "results.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    write_report(rows)
    print(f"\nWrote {csv_path}")
    print(f"Wrote {OUT / 'REPORT.md'}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
