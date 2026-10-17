#!/usr/bin/env python3
"""Single NLGEOM step: load internal pressure to P0 (MULF inner solve)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ccx_utils import mmhg_to_mpa
from write_deck import (
    _read_mesh_bc_mode,
    boundary_block,
    material_block,
    static_line,
)


def write_deck_p0(
    out: Path,
    mesh_name: str,
    t_mm: float,
    model: str,
    params: dict,
    p0_mmhg: float,
    label: str = "MULF P0 solve",
    nu: float = 0.47,
    E_mpa: float = 3.0,
    bc_mode: str = "",
) -> dict:
    mesh_path = out.parent / mesh_name
    if not bc_mode:
        bc_mode = _read_mesh_bc_mode(mesh_path) if mesh_path.is_file() else "symmetry_octant"

    p0 = float(p0_mmhg)
    p_mpa = mmhg_to_mpa(p0)
    step_inc = max(120, 8 * 24) if model.startswith("ogden") else max(80, 4 * 16)

    lines = [
        "*HEADING",
        f"{label} — NLGEOM inflation to P0={p0} mmHg",
        f"** bc_mode={bc_mode}",
        f"*INCLUDE, INPUT={mesh_name}",
        material_block(model, params, nu, E_mpa),
        "*SHELL SECTION, ELSET=SHELL, MATERIAL=SHELL_MAT",
        f"{t_mm:.6f}",
        "*AMPLITUDE, NAME=P0_LOAD",
        f"0.000000, {p_mpa:.12e}",
        f"1.000000, {p_mpa:.12e}",
        f"*STEP, NLGEOM, INC={step_inc}",
        "*STATIC",
        static_line(model),
        *boundary_block(bc_mode),
        "*DSLOAD, AMPLITUDE=P0_LOAD",
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
        "mulf_p0_solve": True,
        "P0_mmHg": p0,
        "p_targets_mmhg": [p0],
        "steps": [{"name": "P0", "p_mmhg": p0, "pseudo_time": 1.0}],
    }
    out.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2))
    return meta


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mesh", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--t", type=float, required=True)
    ap.add_argument("--model", default="yeoh2")
    ap.add_argument("--p0", type=float, default=16.9)
    args = ap.parse_args()
    params = {"C10_MPa": 0.5, "C20_MPa": 0.05}
    meta = write_deck_p0(
        args.out, args.mesh.name, args.t, args.model, params, p0_mmhg=args.p0
    )
    print(json.dumps(meta, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
