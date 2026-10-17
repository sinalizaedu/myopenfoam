#!/usr/bin/env python3
"""Write a multi-step hyperelastic spherical-shell CalculiX deck (wp1.2)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ccx_utils import bulk_compliance_mpa, d1_from_ogden_mu1, mmhg_to_mpa

P0_MMHG = 15.0


def material_block(model: str, params: dict, nu: float, E_mpa: float) -> str:
    if params.get("d1_tied_mu1") and model.startswith("ogden"):
        d1 = d1_from_ogden_mu1(params["mu1_MPa"])
    elif "D1" in params:
        d1 = params["D1"]
    else:
        d1 = bulk_compliance_mpa(model, nu, E_mpa)
    if model == "yeoh2":
        c10 = params["C10_MPa"]
        c20 = params["C20_MPa"]
        return f"""*MATERIAL, NAME=SHELL_MAT
*HYPERELASTIC, YEOH
{c10:.12e}, {c20:.12e}, 0.0, {d1:.12e}, 0.0, 0.0"""
    if model == "yeoh3":
        return f"""*MATERIAL, NAME=SHELL_MAT
*HYPERELASTIC, YEOH
{params['C10_MPa']:.12e}, {params['C20_MPa']:.12e}, {params['C30_MPa']:.12e}, {d1:.12e}, 0.0, 0.0"""
    if model == "ogden1":
        return f"""*MATERIAL, NAME=SHELL_MAT
*HYPERELASTIC, OGDEN, N=1
{params['mu1_MPa']:.12e}, {params['alpha1']:.12e}, {d1:.12e}"""
    if model == "ogden2":
        d2 = params.get("D2", d1)
        return f"""*MATERIAL, NAME=SHELL_MAT
*HYPERELASTIC, OGDEN, N=2
{params['mu1_MPa']:.12e}, {params['alpha1']:.12e}, {params['mu2_MPa']:.12e}, {params['alpha2']:.12e}, {d1:.12e}, {d2:.12e}"""
    raise ValueError(f"Unknown model {model}")


def _read_mesh_bc_mode(mesh_path: Path) -> str:
    meta = mesh_path.with_suffix(".meta.json")
    if meta.is_file():
        return str(json.loads(meta.read_text()).get("bc_mode", "pins"))
    for line in mesh_path.read_text().splitlines():
        if "bc_mode=" in line:
            return line.split("bc_mode=")[1].split()[0]
    return "pins"


def static_line(model: str) -> str:
    if model.startswith("ogden"):
        return "0.005, 1.0, 1e-6, 0.02"
    return "0.01, 1.0, 1e-6, 0.04"


def boundary_block(bc_mode: str) -> list[str]:
    if bc_mode == "symmetry_octant":
        return [
            "** Symmetry planes on x=0, y=0, z=0 (1/8 sphere — stable NLGEOM)",
            "*BOUNDARY",
            "SYM_X, 1, 1, 0.0",
            "SYM_Y, 2, 2, 0.0",
            "SYM_Z, 3, 3, 0.0",
        ]
    return [
        "** Rigid-body removal (wp1.1 linear only — not recommended for NLGEOM)",
        "*BOUNDARY",
        "PIN1, 1, 3, 0.0",
        "PIN2, 2, 3, 0.0",
        "PIN3, 3, 3, 0.0",
    ]


def write_deck(
    out: Path,
    mesh_name: str,
    t_mm: float,
    model: str,
    params: dict,
    p_targets_mmhg: list[float],
    label: str = "wp1.2",
    nu: float = 0.47,
    E_mpa: float = 3.0,
    bc_mode: str = "",
    p0_mmhg: float | None = None,
) -> dict:
    """Write .inp with one NLGEOM step and a tabular pressure amplitude."""
    mesh_path = out.parent / mesh_name
    if not bc_mode:
        bc_mode = _read_mesh_bc_mode(mesh_path) if mesh_path.is_file() else "symmetry_octant"

    p0 = float(p0_mmhg if p0_mmhg is not None else P0_MMHG)
    p_targets = sorted({p0, *[float(p) for p in p_targets_mmhg]})
    if p_targets[0] > p0 + 1e-9:
        p_targets.insert(0, p0)

    n_pts = len(p_targets)
    amp_lines = ["*AMPLITUDE, NAME=P_LOAD"]
    step_meta: list[dict] = []
    for i, p_mmhg in enumerate(p_targets):
        t = 0.0 if n_pts == 1 else i / (n_pts - 1)
        amp_lines.append(f"{t:.6f}, {mmhg_to_mpa(p_mmhg):.12e}")
        step_meta.append(
            {
                "name": f"P_{i:02d}",
                "p_mmhg": p_mmhg,
                "pseudo_time": t,
            }
        )

    step_inc = max(120, 8 * n_pts)
    lines = [
        "*HEADING",
        f"{label} — hyperelastic spherical shell inflation",
        "** Units: mm, N, MPa. Single NLGEOM step + tabular pressure amplitude.",
        f"** bc_mode={bc_mode}",
        f"*INCLUDE, INPUT={mesh_name}",
        material_block(model, params, nu, E_mpa),
        "*SHELL SECTION, ELSET=SHELL, MATERIAL=SHELL_MAT",
        f"{t_mm:.6f}",
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
        "p_targets_mmhg": p_targets,
        "steps": step_meta,
        "P0_mmHg": p0,
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
    ap.add_argument("--p-max", type=float, default=60.0)
    ap.add_argument("--n-steps", type=int, default=12)
    ap.add_argument("--bc-mode", default="", choices=["", "pins", "symmetry_octant"])
    args = ap.parse_args()

    p_targets = list(
        P0_MMHG
        + (args.p_max - P0_MMHG) * i / args.n_steps
        for i in range(1, args.n_steps + 1)
    )
    params = {"C10_MPa": args.C10, "C20_MPa": args.C20}
    meta = write_deck(
        args.out,
        args.mesh.name,
        args.t,
        args.model,
        params,
        p_targets,
        bc_mode=args.bc_mode,
    )
    print(json.dumps(meta, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
