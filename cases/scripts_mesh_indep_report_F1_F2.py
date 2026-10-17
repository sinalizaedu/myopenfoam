#!/usr/bin/env python3
"""Compare F1/F2 baseline mesh-independence metrics (F1 volume only; F2 patch+volume)."""
from __future__ import annotations

import re
from pathlib import Path

CASES = Path(__file__).resolve().parent
MMHG = 133.322  # Pa

LEVELS_BY_KIND = {
    "patch": ("F2",),
    "volume": ("F1", "F2"),
}
KINDS = ("patch", "volume")


def case_dir(level: str, kind: str) -> Path:
    return CASES / f"doc-baseline-{level.lower()}-{kind}-fluid"


def n_cells(cdir: Path) -> int | None:
    for log in (
        cdir / "fluid/log.checkMesh",
        cdir / "fluid/log.fluent3DMeshToFoam",
        cdir / "fluid/log.blockMesh",
    ):
        if not log.exists():
            continue
        text = log.read_text(errors="ignore")
        m = re.search(r"cells:\s+(\d+)", text)
        if m:
            return int(m.group(1))
        m = re.search(r"nCells:\s+(\d+)", text)
        if m:
            return int(m.group(1))
    return None


def final_iop_mmhg(cdir: Path) -> float | None:
    pfile = cdir / "fluid/postProcessing/iop_probe/0/p"
    if not pfile.exists():
        return None
    last = None
    for line in pfile.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            try:
                last = float(parts[1])
            except ValueError:
                continue
    if last is None:
        return None
    return last / MMHG


def max_speed(cdir: Path) -> float | None:
    fluid = cdir / "fluid"
    times = []
    for p in fluid.iterdir():
        if p.is_dir() and re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", p.name):
            try:
                times.append((float(p.name), p))
            except ValueError:
                pass
    if not times:
        return None
    times.sort()
    ufile = times[-1][1] / "U"
    if not ufile.exists():
        return None
    text = ufile.read_text(errors="ignore")
    vecs = re.findall(
        r"\(\s*([-+eE0-9.]+)\s+([-+eE0-9.]+)\s+([-+eE0-9.]+)\s*\)",
        text,
    )
    if not vecs:
        return None
    import math

    return max(math.sqrt(float(x) ** 2 + float(y) ** 2 + float(z) ** 2) for x, y, z in vecs)


def iterations(cdir: Path) -> int | None:
    log = cdir / "fluid/log.simpleFoam"
    if not log.exists():
        return None
    text = log.read_text(errors="ignore")
    times = [int(m.group(1)) for m in re.finditer(r"^Time = (\d+)\s*$", text, re.M)]
    return times[-1] if times else None


def converged(cdir: Path) -> bool:
    log = cdir / "fluid/log.simpleFoam"
    if not log.exists():
        return False
    text = log.read_text(errors="ignore")
    return "SIMPLE solution converged" in text or (
        re.search(r"^End$", text, re.M) is not None and "FOAM FATAL" not in text
    )


def main() -> None:
    rows = []
    for kind in KINDS:
        prev_iop = None
        for level in LEVELS_BY_KIND[kind]:
            c = case_dir(level, kind)
            iop = final_iop_mmhg(c) if c.exists() else None
            err = None
            if iop is not None and prev_iop is not None and prev_iop != 0:
                err = 100.0 * (iop - prev_iop) / abs(prev_iop)
            rows.append(
                {
                    "kind": kind,
                    "mesh": level,
                    "cells": n_cells(c) if c.exists() else None,
                    "iop": iop,
                    "umax": max_speed(c) if c.exists() and converged(c) else None,
                    "iters": iterations(c) if c.exists() else None,
                    "err": err,
                    "ok": converged(c) if c.exists() else False,
                }
            )
            if iop is not None:
                prev_iop = iop

    out = CASES / "mesh_independence_F1_F2_report.md"
    lines = [
        "# Mesh independence — baseline F1 / F2 (Fluent)",
        "",
        "F1 = `meshfile2.msh` (855k tets). F2 = finer 3D fluid export at",
        "`doc-g2-sim1/geometry/eye_g2_fluid_fluent_F2.msh` (not imported yet).",
        "",
    ]
    for kind in KINDS:
        lines += [
            f"## {kind}",
            "",
            "| Malha | Células | IOP (mmHg) | Umax (m/s) | Iters | Erro % IOP vs ant. |",
            "|---|---:|---:|---:|---:|---:|",
        ]
        for r in rows:
            if r["kind"] != kind:
                continue

            def fmt(v, nd=4):
                if v is None:
                    return "—"
                if isinstance(v, float):
                    return f"{v:.{nd}g}"
                return str(v)

            lines.append(
                f"| {r['mesh']} | {fmt(r['cells'], 0)} | {fmt(r['iop'], 4)} | "
                f"{fmt(r['umax'], 4)} | {fmt(r['iters'], 0)} | {fmt(r['err'], 3)} |"
            )
        lines.append("")

    out.write_text("\n".join(lines) + "\n")
    print(out.read_text())
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
