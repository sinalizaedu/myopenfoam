#!/usr/bin/env python3
"""CalculiX deck with one shell section per thickness band."""
from __future__ import annotations

import json
from pathlib import Path

import sys

HERE = Path(__file__).resolve().parent
WP12 = HERE.parents[2] / "wp1.2" / "scripts"
sys.path.insert(0, str(WP12))

from ccx_utils import d1_from_ogden_mu1, mmhg_to_mpa  # noqa: E402
from write_deck import boundary_block, material_block, static_line  # noqa: E402


def write_deck_variable_t(
    out: Path,
    mesh_name: str,
    band_thickness_mm: list[float],
    model: str,
    params: dict,
    p_targets_mmhg: list[float],
    *,
    label: str = "wp1.4 sweep",
    bc_mode: str = "symmetry_octant",
    p0_mmhg: float = 16.9,
    nu: float = 0.47,
    E_mpa: float = 3.0,
) -> dict:
    mesh_path = out.parent / mesh_name
    meta_mesh = json.loads(mesh_path.with_suffix(".meta.json").read_text())
    n_bands = len(band_thickness_mm)
    if meta_mesh.get("band_thickness_mm"):
        band_thickness_mm = list(meta_mesh["band_thickness_mm"])

    p0 = float(p0_mmhg)
    p_targets = sorted({p0, *[float(p) for p in p_targets_mmhg]})
    if p_targets[0] > p0 + 1e-9:
        p_targets.insert(0, p0)

    n_pts = len(p_targets)
    amp_lines = ["*AMPLITUDE, NAME=P_LOAD"]
    step_meta: list[dict] = []
    for i, p_mmhg in enumerate(p_targets):
        t = 0.0 if n_pts == 1 else i / (n_pts - 1)
        amp_lines.append(f"{t:.6f}, {mmhg_to_mpa(p_mmhg):.12e}")
        step_meta.append({"name": f"P_{i:02d}", "p_mmhg": p_mmhg, "pseudo_time": t})

    section_lines: list[str] = []
    for b in range(n_bands):
        section_lines.append(f"*SHELL SECTION, ELSET=T_BAND_{b:02d}, MATERIAL=SHELL_MAT")
        section_lines.append(f"{band_thickness_mm[b]:.6f}")

    step_inc = max(120, 8 * n_pts)
    lines = [
        "*HEADING",
        f"{label} — variable-thickness hyperelastic shell",
        "** Units: mm, N, MPa. NLGEOM + tabular pressure.",
        f"** bc_mode={bc_mode}",
        f"*INCLUDE, INPUT={mesh_name}",
        material_block(model, params, nu, E_mpa),
        *section_lines,
        *amp_lines,
        f"*STEP, NLGEOM, INC={step_inc}",
        "*STATIC",
        static_line(model),
        *boundary_block(bc_mode),
        "*DSLOAD, AMPLITUDE=P_LOAD",
        "INNER_SURF, P, 1.0",
        "*NODE FILE",
        "U",
        "*END STEP",
    ]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n")
    meta = {
        "deck": str(out),
        "model": model,
        "params": params,
        "bc_mode": bc_mode,
        "single_step": True,
        "variable_thickness": True,
        "band_thickness_mm": band_thickness_mm,
        "p_targets_mmhg": p_targets,
        "steps": step_meta,
        "P0_mmHg": p0,
    }
    out.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2))
    return meta
