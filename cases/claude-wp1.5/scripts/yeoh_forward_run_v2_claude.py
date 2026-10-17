#!/usr/bin/env python3
"""Yeoh-2 forward run com P0 e p_final parametrizados por especie.

Mesma correcao que ogden_forward_run_v2_claude.py, para o material Yeoh.
Reusa load_yeoh_params() de cases/wp1.2/scripts/yeoh_material.py (nao
depende de P0), mas NAO reusa o p_targets() de la (que tem P0=16.9
fixo) nem yeoh_forward_run.py (que tambem fixa P0_MMHG=16.9 e nao
expoe p0/p_final por fora).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WP12 = HERE.parents[1] / "wp1.2" / "scripts"
sys.path.insert(0, str(WP12))

from ccx_utils import run_ccx  # noqa: E402
from extract_pv_curve import extract_pv  # noqa: E402
from gen_sphere_shell_mesh import write_mesh  # noqa: E402
from write_deck import write_deck  # noqa: E402
from yeoh_material import load_yeoh_params  # noqa: E402


def p_targets(p0: float, p_final: float, n_steps: int) -> list[float]:
    return [p0 + (p_final - p0) * i / n_steps for i in range(1, n_steps + 1)]


def run_yeoh_forward_v2(
    R_mm: float,
    t_mm: float,
    work: Path,
    tag: str,
    *,
    fit_path: Path | None,
    p0_mmhg: float,
    p_final_mmhg: float,
    ne: int = 8,
    n_steps: int = 16,
) -> tuple[list[dict], dict]:
    work.mkdir(parents=True, exist_ok=True)
    params = load_yeoh_params(fit_path)
    mesh = work / f"{tag}_mesh.inp"
    write_mesh(
        mesh, R_mm, t_mm, ne, 2, tag,
        bc_mode="symmetry_octant", mesh_kind="spherical",
        theta_min_deg=3.0, reduced=True,
    )
    deck = work / f"{tag}.inp"
    write_deck(
        deck, mesh.name, t_mm, "yeoh2", params,
        p_targets(p0_mmhg, p_final_mmhg, n_steps),
        label=f"yeoh {tag} (P0={p0_mmhg} especifico da especie)",
        bc_mode="symmetry_octant", p0_mmhg=p0_mmhg,
    )
    frd = run_ccx(deck, clean=True)
    rows = extract_pv(deck, frd, R_mm, p0_mmhg=p0_mmhg)
    meta = {
        "R_mm": R_mm, "t_mm": t_mm, "ne": ne,
        "p0_mmHg": p0_mmhg, "p_final_mmHg": p_final_mmhg,
        "params": params, "status": "OK",
    }
    return rows, meta
