#!/usr/bin/env python3
"""Single Yeoh-2 NLGEOM forward run (octant spherical shell)."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WP1 = HERE.parents[1] / "wp1.1" / "scripts"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(WP1))

from ccx_utils import run_ccx  # noqa: E402
from extract_pv_curve import extract_pv  # noqa: E402
from gen_sphere_shell_mesh import write_mesh  # noqa: E402
from write_deck import write_deck  # noqa: E402
from yeoh_material import P0_MMHG, load_yeoh_params, p_targets  # noqa: E402


def run_yeoh_forward(
    R_mm: float,
    t_mm: float,
    work: Path,
    tag: str,
    *,
    ne: int = 8,
    p_final: float = 50.0,
    n_steps: int = 16,
    fit_path: Path | None = None,
) -> tuple[list[dict], dict]:
    """Return (pv_rows, meta). Raises on CCX failure."""
    work.mkdir(parents=True, exist_ok=True)
    params = load_yeoh_params(fit_path)
    mesh = work / f"{tag}_mesh.inp"
    write_mesh(
        mesh,
        R_mm,
        t_mm,
        ne,
        2,
        tag,
        bc_mode="symmetry_octant",
        mesh_kind="spherical",
        theta_min_deg=3.0,
        reduced=True,
    )
    deck = work / f"{tag}.inp"
    write_deck(
        deck,
        mesh.name,
        t_mm,
        "yeoh2",
        params,
        p_targets(p_final, n_steps),
        label=f"yeoh {tag}",
        bc_mode="symmetry_octant",
        p0_mmhg=P0_MMHG,
    )
    frd = run_ccx(deck, clean=True)
    rows = extract_pv(deck, frd, R_mm, p0_mmhg=P0_MMHG)
    meta = {
        "R_mm": R_mm,
        "t_mm": t_mm,
        "ne": ne,
        "p_final_mmHg": p_final,
        "params": params,
        "status": "OK",
    }
    return rows, meta
