#!/usr/bin/env python3
"""Summarise A1–E1 and A2–E2 solid meshes: checkMesh + conformal map vs O1 fluid wall."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

SM = Path(__file__).resolve().parent
CASE = SM.parent
FLUID = CASE / "fluid" / "constant" / "polyMesh"
PROD = CASE / "solid" / "constant" / "polyMesh"


def _bruna() -> Path:
    for cand in (CASE.parents[1] / "brunaStuff", Path("/opt/brunaStuff")):
        if (cand / "verify_o1_fsi_conformal.py").exists():
            return cand
    return CASE.parents[1] / "brunaStuff"


BRUNA = _bruna()
VERIFY = BRUNA / "verify_o1_fsi_conformal.py"
PLOT = BRUNA / "plot_o1_solid_mesh.py"
V1 = ("A1", "B1", "C1", "D1", "E1")
V2 = ("A2", "B2", "C2", "D2", "E2")


def parse_checkmesh(log: Path) -> dict:
    text = log.read_text() if log.exists() else ""
    cells = re.search(r"^\s*cells:\s+(\d+)", text, re.M)
    neg = re.search(r"Number of negative volume cells:\s+(\d+)", text)
    if not neg:
        okvol = "Cell volumes OK" in text
        nneg = 0 if okvol else -1
    else:
        nneg = int(neg.group(1))
    nonortho = re.search(r"non-orthogonality Max:\s+([\d.]+)", text)
    failed = "Failed" in text and "Mesh OK" not in text
    fsi = re.search(r"fsi_active\s+(\d+)", text)
    open_c = re.search(r"number of open cells\s+(\d+)", text, re.I)
    tets = re.search(r"tetrahedra:\s+(\d+)", text)
    pyramids = re.search(r"pyramids:\s+(\d+)", text)
    prisms = re.search(r"prisms:\s+(\d+)", text)
    hexes = re.search(r"hexahedra:\s+(\d+)", text)
    return {
        "cells": int(cells.group(1)) if cells else 0,
        "neg_vol": nneg,
        "max_nonortho": float(nonortho.group(1)) if nonortho else None,
        "failed": failed,
        "fsi_faces": int(fsi.group(1)) if fsi else 0,
        "open_cells": int(open_c.group(1)) if open_c else 0,
        "tets": int(tets.group(1)) if tets else 0,
        "pyramids": int(pyramids.group(1)) if pyramids else 0,
        "prisms": int(prisms.group(1)) if prisms else 0,
        "hexes": int(hexes.group(1)) if hexes else 0,
        "ok": (not failed) and nneg == 0,
    }


def conformal(solid: Path) -> str:
    if not VERIFY.exists() or not (solid / "boundary").exists():
        return "n/a"
    if "fsi_active" not in (solid / "boundary").read_text():
        return "no fsi_active"
    try:
        out = subprocess.check_output(
            [sys.executable, str(VERIFY), str(FLUID), str(solid), "--centroid-tol", "1e-6"],
            text=True,
            stderr=subprocess.STDOUT,
        )
        m = re.search(r"max centroid error ([\d.eE+-]+) m", out)
        flag = "PASS" if "[PASS]" in out else "FAIL"
        err = m.group(1) if m else "?"
        return f"{flag} {err}"
    except subprocess.CalledProcessError as exc:
        tail = (exc.output or "")[-200:].replace("\n", " ")
        return f"ERR {tail}"


def prod_cells() -> int:
    if not (PROD / "owner").exists():
        return 33408
    info = parse_checkmesh(CASE / "solid" / "log.checkMesh")
    return info["cells"] or 33408


def summarize(names: tuple[str, ...], title: str) -> list[tuple[str, dict, str]]:
    rows = []
    figdir = SM / "figures"
    figdir.mkdir(exist_ok=True)
    print(f"\n{title}")
    print(f"{'mesh':4s}  {'cells':>8s}  {'negVol':>6s}  {'open':>5s}  {'nonOrtho':>8s}  {'fsi':>5s}  {'mix':>12s}  conformal")
    print("-" * 95)
    ref = prod_cells()
    for name in names:
        log = SM / name / "log.checkMesh"
        poly = SM / name / "constant" / "polyMesh"
        info = parse_checkmesh(log)
        conf = conformal(poly) if poly.exists() else "no mesh"
        rows.append((name, info, conf))
        no = f"{info['max_nonortho']:.1f}" if info["max_nonortho"] is not None else "-"
        mix_parts = []
        if info["hexes"]:
            mix_parts.append(f"{info['hexes']} hex")
        if info["prisms"]:
            mix_parts.append(f"{info['prisms']} prism")
        if info["tets"]:
            mix_parts.append(f"{info['tets']} tet")
        if info["pyramids"]:
            mix_parts.append(f"{info['pyramids']} pyr")
        mix = ", ".join(mix_parts) if mix_parts else "hex"
        ge = ">=" if info["cells"] >= ref else "<"
        print(
            f"{name:4s}  {info['cells']:8d}{ge}  {info['neg_vol']:6d}  {info['open_cells']:5d}  "
            f"{no:>8s}  {info['fsi_faces']:5d}  {mix:>12s}  {conf}"
        )
        if poly.exists() and PLOT.exists() and (poly / "points").exists():
            out = figdir / f"{name}_solid_mesh.png"
            try:
                subprocess.check_call(
                    [sys.executable, str(PLOT), "--polymesh", str(poly),
                     "--out", str(out), "--case-label", name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except subprocess.CalledProcessError:
                pass
    return rows


def write_report(v1_rows, v2_rows) -> None:
    report = SM / "REPORT.md"
    ref = prod_cells()
    lines = [
        "# O1 solid mesh study (A1–E1, A2–E2)",
        "",
        f"Production reference `solid/`: **{ref}** cells.",
        "",
        "## v1 (baseline)",
        "",
        "| mesh | cells | neg. vol | open | max non-ortho | fsi_active | conformal vs wall |",
        "|------|------:|---------:|-----:|--------------:|-----------:|-------------------|",
    ]
    for name, info, conf in v1_rows:
        no = f"{info['max_nonortho']:.1f}" if info["max_nonortho"] is not None else "-"
        lines.append(
            f"| {name} | {info['cells']} | {info['neg_vol']} | {info['open_cells']} | {no} | "
            f"{info['fsi_faces']} | {conf} |"
        )
    lines += [
        "",
        "## v2 (dense + mixed elements, geometry ≥ production)",
        "",
        "| mesh | cells | neg. vol | open | max non-ortho | fsi_active | cell mix | conformal |",
        "|------|------:|---------:|-----:|--------------:|-----------:|----------|-----------|",
    ]
    for name, info, conf in v2_rows:
        no = f"{info['max_nonortho']:.1f}" if info["max_nonortho"] is not None else "-"
        mix_parts = []
        if info["tets"]:
            mix_parts.append(f"{info['tets']} tet")
        if info["prisms"]:
            mix_parts.append(f"{info['prisms']} prism")
        if info["pyramids"]:
            mix_parts.append(f"{info['pyramids']} pyr")
        mix = ", ".join(mix_parts) if mix_parts else "hex"
        lines.append(
            f"| {name} | {info['cells']} | {info['neg_vol']} | {info['open_cells']} | {no} | "
            f"{info['fsi_faces']} | {mix} | {conf} |"
        )
    lines += [
        "",
        "### v2 pipelines",
        "",
        "- **A2** Full Lamminsalo Gmsh 3D (H1 limbus): 2× radial, θ=12, limbus quads→prisms. "
        "**Not** coat extrusion.",
        "- **B2** H1 structured `blockMesh`, layers 5/5/5/5 (hex wedge).",
        "- **C2** Aggressive `snappyHexMesh` level (3 4), 6 prism-like wedge layers.",
        "- **D2** Fine Gmsh revolve (H1, 2× radial, limbus prisms).",
        "- **E2** `mergeMeshes` + `splitMeshRegions` of fluid + B2.",
        "",
        "Build: `MESH=B2 ./Allmesh` or `MESH=v2 ./Allmesh` for all v2 meshes.",
        "FSI hook: `MESH=B2 MODE=fsi ./Allrun` copies `solid_meshes/$MESH`.",
        "",
    ]
    report.write_text("\n".join(lines))
    print(f"Wrote {report}")


def main() -> None:
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    v1_rows: list[tuple[str, dict, str]] = []
    v2_rows: list[tuple[str, dict, str]] = []
    if which in ("all", "v1"):
        v1_rows = summarize(V1, "=== v1 (A1–E1) ===")
    if which in ("all", "v2"):
        v2_rows = summarize(V2, "=== v2 (A2–E2) ===")
    if which == "all":
        write_report(v1_rows, v2_rows)
    elif which == "v1":
        write_report(v1_rows, [])
    else:
        write_report([], v2_rows)


if __name__ == "__main__":
    main()
