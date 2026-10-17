#!/usr/bin/env python3
"""Two-step NLGEOM deck with V re-referenced at P0 (NOT Gee et al. 2010 MULF).

This is a legacy shortcut: step 1 loads to P0, step 2 continues to P_final, and
post-processing sets V=0 at the end of step 1. It does NOT iterate on reference
geometry. For true MULF use mulf_gee.py / run_wp13_mulf_gee.py.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ccx_utils import mmhg_to_mpa
from write_deck import (
    P0_MMHG,
    _read_mesh_bc_mode,
    boundary_block,
    material_block,
    static_line,
)


def write_deck_mulf(
    out: Path,
    mesh_name: str,
    t_mm: float,
    model: str,
    params: dict,
    p0_mmhg: float,
    p_final_mmhg: float,
    n_load_steps: int = 24,
    label: str = "wp1.3 MULF",
    nu: float = 0.47,
    E_mpa: float = 3.0,
    bc_mode: str = "",
    p_init_mmhg: float = 0.1,
) -> dict:
    """Write a two-step hyperelastic inflation deck (prestress + loading)."""
    mesh_path = out.parent / mesh_name
    if not bc_mode:
        bc_mode = _read_mesh_bc_mode(mesh_path) if mesh_path.is_file() else "symmetry_octant"

    p0 = float(p0_mmhg)
    p_final = float(p_final_mmhg)
    if p_final <= p0 + 1e-9:
        raise ValueError(f"p_final ({p_final}) must exceed P0 ({p0})")

    n2 = max(4, int(n_load_steps))
    step2_pressures = [
        p0 + (p_final - p0) * i / n2 for i in range(n2 + 1)
    ]

    # Step 1: ramp to P0 from unstressed state (constant target P0 — same as single-step
    # deck t=0). Avoid low-pressure Ogden ramp (p_init→P0) which diverges for α₁≪1.
    step1_inc = max(120, 8 * 24) if model.startswith("ogden") else max(60, 4 * 20)
    step2_inc = max(120, 8 * n2)

    lines = [
        "*HEADING",
        f"{label} — MULF two-step hyperelastic inflation",
        "** Units: mm, N, MPa. Step 1 prestress to P0; step 2 incremental load.",
        f"** bc_mode={bc_mode} mulf=true",
        f"*INCLUDE, INPUT={mesh_name}",
        material_block(model, params, nu, E_mpa),
        "*SHELL SECTION, ELSET=SHELL, MATERIAL=SHELL_MAT",
        f"{t_mm:.6f}",
        "*AMPLITUDE, NAME=PRESTRESS",
        f"0.000000, {mmhg_to_mpa(p0):.12e}",
        f"1.000000, {mmhg_to_mpa(p0):.12e}",
        f"*STEP, NLGEOM, INC={step1_inc}",
        "*STATIC",
        static_line(model),
        *boundary_block(bc_mode),
        "*DSLOAD, AMPLITUDE=PRESTRESS",
        "INNER_SURF, P, 1.0",
        "*NODE FILE",
        "U",
        "*END STEP",
        "*AMPLITUDE, NAME=LOAD_ABS",
        f"0.000000, {mmhg_to_mpa(p0):.12e}",
        f"1.000000, {mmhg_to_mpa(p_final):.12e}",
        f"*STEP, NLGEOM, INC={step2_inc}",
        "*STATIC",
        static_line(model),
        *boundary_block(bc_mode),
        "** Step 2: absolute pressure P0→P_final (ccx 2.20 has no OP=MOD on *DSLOAD)",
        "*DSLOAD, AMPLITUDE=LOAD_ABS",
        "INNER_SURF, P, 1.0",
        "*NODE FILE",
        "U",
        "*END STEP",
    ]

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n")

    step2_meta = [
        {
            "name": f"S2_{i:02d}",
            "p_mmhg": p,
            "pseudo_time": i / n2 if n2 else 0.0,
            "step_id": 2,
            "role": "loading",
        }
        for i, p in enumerate(step2_pressures)
    ]

    meta = {
        "deck": str(out),
        "model": model,
        "params": params,
        "bc_mode": bc_mode,
        "mulf": True,
        "single_step": False,
        "P0_mmHg": p0,
        "prestress_mode": "constant_P0_ramp",
        "p_final_mmHg": p_final,
        "n_load_steps": n2,
        "step1": {"role": "prestress", "p_end_mmhg": p0},
        "step2_pressures_mmhg": step2_pressures,
        "steps": [
            {
                "name": "S1_PRESTRESS",
                "p_mmhg": p0,
                "pseudo_time": 1.0,
                "step_id": 1,
                "role": "prestress",
            },
            *step2_meta,
        ],
    }
    meta_path = out.with_suffix(".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2))
    return meta


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mesh", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--t", type=float, required=True)
    ap.add_argument("--model", default="yeoh2")
    ap.add_argument("--C10", type=float, default=0.5)
    ap.add_argument("--C20", type=float, default=0.05)
    ap.add_argument("--p0", type=float, default=P0_MMHG)
    ap.add_argument("--p-final", type=float, default=50.0)
    ap.add_argument("--n-steps", type=int, default=24)
    ap.add_argument("--bc-mode", default="", choices=["", "pins", "symmetry_octant"])
    args = ap.parse_args()

    params = {"C10_MPa": args.C10, "C20_MPa": args.C20}
    meta = write_deck_mulf(
        args.out,
        args.mesh.name,
        args.t,
        args.model,
        params,
        p0_mmhg=args.p0,
        p_final_mmhg=args.p_final,
        n_load_steps=args.n_steps,
        bc_mode=args.bc_mode,
    )
    print(json.dumps(meta, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
