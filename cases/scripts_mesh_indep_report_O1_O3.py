#!/usr/bin/env python3
"""Mesh-independence report for baseline O1/O2/O3 (patch + volume)."""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

CASES = Path(__file__).resolve().parent
RHO = 995.0
PA_TO_MMHG = 0.0075006
Q_TARGET = 1.25e-11  # m³/s quarter eye

LEVELS = ("O2", "O1", "O3")  # coarse → design → fine
KINDS = ("patch", "volume")
FACTOR = {"O2": 0.7, "O1": 1.0, "O3": 1.3}


def case_dir(level: str, kind: str) -> Path:
    return CASES / f"doc-baseline-{level.lower()}-{kind}-fluid"


def n_cells(cdir: Path) -> int | None:
    for log in (cdir / "fluid/log.checkMesh", cdir / "fluid/log.blockMesh"):
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


def typical_div(level: str) -> str:
    return {
        "O1": "(12, 22, 6)",
        "O2": "(8, 15, 4)",
        "O3": "(16, 29, 8)",
    }[level]


def read_calibration(cdir: Path) -> dict:
    for name in ("baseline_iop.yaml", "baseline_O1.yaml", "baseline_O2.yaml", "baseline_O3.yaml"):
        p = cdir / "calibration" / name
        if not p.exists():
            continue
        out = {}
        for line in p.read_text().splitlines():
            if ":" in line and not line.strip().startswith("#"):
                k, _, v = line.partition(":")
                out[k.strip()] = v.strip()
        return out
    return {}


def probe_iop(cdir: Path) -> tuple[float | None, float | None]:
    probes = list((cdir / "fluid").glob("postProcessing/iop_probe/*/p"))
    if not probes:
        return None, None

    def tkey(p: Path) -> float:
        try:
            return float(p.parent.name)
        except ValueError:
            return -1.0

    vals = []
    for line in max(probes, key=tkey).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 5:
            vals = [float(x) for x in parts[1:5]]
        elif len(parts) >= 2:
            vals = [float(parts[1])]
    if len(vals) < 4:
        return None, None
    to_mmhg = lambda p: p * RHO * PA_TO_MMHG
    iop_ac = 0.5 * (to_mmhg(vals[0]) + to_mmhg(vals[1]))
    iop_vit = 0.5 * (to_mmhg(vals[2]) + to_mmhg(vals[3]))
    return iop_ac, iop_vit


def mass_balance(cdir: Path) -> tuple[float | None, float | None]:
    log = cdir / "fluid/log.simpleFoam"
    if not log.exists():
        return None, None
    q = None
    for line in reversed(log.read_text(errors="ignore").splitlines()):
        if "sum(outlet_tm) of phi" in line:
            q = float(line.split("=")[-1].strip())
            break
    if q is None:
        return None, None
    err = abs(q - Q_TARGET) / Q_TARGET * 100.0
    return q, err


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
    vecs = re.findall(
        r"\(\s*([-+eE0-9.]+)\s+([-+eE0-9.]+)\s+([-+eE0-9.]+)\s*\)",
        ufile.read_text(errors="ignore"),
    )
    if not vecs:
        return None
    return max(
        math.sqrt(float(x) ** 2 + float(y) ** 2 + float(z) ** 2) for x, y, z in vecs
    )


def iterations(cdir: Path) -> int | None:
    log = cdir / "fluid/log.simpleFoam"
    if not log.exists():
        return None
    times = [int(m.group(1)) for m in re.finditer(r"^Time = (\d+)\s*$", log.read_text(), re.M)]
    return times[-1] if times else None


def converged(cdir: Path) -> bool:
    log = cdir / "fluid/log.simpleFoam"
    if not log.exists():
        return False
    text = log.read_text(errors="ignore")
    return "SIMPLE solution converged" in text or (
        re.search(r"^End$", text, re.M) is not None and "FOAM FATAL" not in text
    )


def pct_change(new: float, old: float) -> float:
    return 100.0 * (new - old) / abs(old)


def richardson_phi(phi_coarse: float, phi_mid: float, phi_fine: float, r12: float, r23: float) -> float | None:
    e21 = phi_mid - phi_coarse
    e32 = phi_fine - phi_mid
    if abs(e21) < 1e-12 or abs(e32) < 1e-12:
        return None
    r_eff = (r12 + r23) / 2.0
    p = math.log(abs(e32 / e21)) / math.log(r_eff)
    if p < 0.1:
        return None
    return phi_fine + (phi_fine - phi_mid) / (r_eff ** p - 1.0)


def collect_row(level: str, kind: str) -> dict:
    c = case_dir(level, kind)
    cal = read_calibration(c)
    iop_ac, iop_vit = probe_iop(c)
    if iop_ac is None and "iop_ac_mmHg" in cal:
        iop_ac = float(cal["iop_ac_mmHg"])
    if iop_vit is None and "iop_vit_mmHg" in cal:
        iop_vit = float(cal["iop_vit_mmHg"])
    q, qerr = mass_balance(c)
    return {
        "kind": kind,
        "mesh": level,
        "factor": FACTOR[level],
        "div": typical_div(level),
        "cells": n_cells(c),
        "iop_ac": iop_ac,
        "iop_vit": iop_vit,
        "q": q,
        "qerr": qerr,
        "umax": max_speed(c) if converged(c) else None,
        "iters": iterations(c),
        "ok": converged(c),
    }


def fmt(v, nd=4):
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:.{nd}g}"
    return str(v)


def main() -> None:
    rows = [collect_row(level, kind) for kind in KINDS for level in LEVELS]

    out = CASES / "mesh_independence_O1_O2_O3_report.md"
    lines = [
        "# Mesh independence — baseline O1 / O2 / O3",
        "",
        "Structured `blockMesh` G2-fluid quarter eye. Division scaling relative to O1:",
        "**O2 = 0.7×** (coarser), **O1 = 1.0×** (design), **O3 = 1.3×** (finer).",
        "Steady `simpleFoam`, IOP target 15 mmHg via `d_TM` calibration.",
        "",
    ]

    for kind in KINDS:
        sub = [r for r in rows if r["kind"] == kind]
        lines += [
            f"## Model {'B (patch tips)' if kind == 'patch' else 'C (volume tips)'}",
            "",
            "| Mesh | factor | cells | IOP AC (mmHg) | IOP vit (mmHg) | ΔAC–vit | Q_TM (m³/s) | Q err % | Umax (m/s) | iters | status |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
        for r in sub:
            delta = None
            if r["iop_ac"] is not None and r["iop_vit"] is not None:
                delta = abs(r["iop_ac"] - r["iop_vit"])
            status = "OK" if r["ok"] else "INCOMPLETE"
            lines.append(
                f"| {r['mesh']} | {r['factor']} | {fmt(r['cells'],0)} | {fmt(r['iop_ac'],4)} | "
                f"{fmt(r['iop_vit'],4)} | {fmt(delta,3)} | {fmt(r['q'],3)} | {fmt(r['qerr'],3)} | "
                f"{fmt(r['umax'],4)} | {fmt(r['iters'],0)} | {status} |"
            )

        lines += ["", "### IOP change vs previous mesh (O2 → O1 → O3)", ""]
        for i in range(1, len(sub)):
            a, b = sub[i - 1], sub[i]
            if a["iop_ac"] is not None and b["iop_ac"] is not None:
                d = pct_change(b["iop_ac"], a["iop_ac"])
                lines.append(
                    f"- **{a['mesh']} → {b['mesh']}** AC IOP: {fmt(a['iop_ac'],4)} → {fmt(b['iop_ac'],4)} mmHg "
                    f"({fmt(d,3)} %)"
                )
            if a["iop_vit"] is not None and b["iop_vit"] is not None:
                d = pct_change(b["iop_vit"], a["iop_vit"])
                lines.append(
                    f"- **{a['mesh']} → {b['mesh']}** vitreous IOP: {fmt(a['iop_vit'],4)} → {fmt(b['iop_vit'],4)} mmHg "
                    f"({fmt(d,3)} %)"
                )

        vals = [r["iop_ac"] for r in sub if r["iop_ac"] is not None]
        if len(vals) == 3:
            phi_ex = richardson_phi(vals[0], vals[1], vals[2], 1 / 0.7, 1.3)
            if phi_ex is not None:
                lines += [
                    "",
                    f"Richardson extrapolated IOP (AC): **{phi_ex:.4f} mmHg**",
                    f"O3 deviation from extrapolation: **{pct_change(vals[2], phi_ex):.3f} %**",
                ]

        o1 = next(r for r in sub if r["mesh"] == "O1")
        o3 = next(r for r in sub if r["mesh"] == "O3")
        if o1["iop_ac"] and o3["iop_ac"]:
            bracket = pct_change(o3["iop_ac"], o1["iop_ac"])
            verdict = "PASS (<1%)" if abs(bracket) < 1.0 else ("WARN (<3%)" if abs(bracket) < 3.0 else "REVIEW")
            lines += ["", f"**Bracket O1↔O3 (AC IOP):** {fmt(bracket,3)} % — {verdict}"]
        lines.append("")

    missing = [r for r in rows if not r["ok"]]
    if missing:
        lines += [
            "## Incomplete runs",
            "",
            *[f"- `doc-baseline-{r['mesh'].lower()}-{r['kind']}-fluid`" for r in missing],
            "",
        ]

    out.write_text("\n".join(lines) + "\n")
    print(out.read_text())
    print(f"Wrote {out}")
    if missing:
        sys.exit(1)


if __name__ == "__main__":
    main()
