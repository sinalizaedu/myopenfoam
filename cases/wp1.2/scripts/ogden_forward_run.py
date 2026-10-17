#!/usr/bin/env python3
"""Single Ogden-N1 NLGEOM forward run (octant spherical shell)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WP1 = HERE.parents[1] / "wp1.1" / "scripts"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(WP1))

from ccx_utils import d1_from_ogden_mu1, run_ccx  # noqa: E402
from extract_pv_curve import extract_pv  # noqa: E402
from gen_sphere_shell_mesh import write_mesh  # noqa: E402
from write_deck import write_deck  # noqa: E402
from yeoh_material import P0_MMHG, p_targets  # noqa: E402


def load_ogden_params(fit_path: Path) -> dict:
    data = json.loads(fit_path.read_text())
    sel = data.get("selected") or data.get("fit")
    p = dict(sel["params"])
    return {
        "mu1_MPa": p["mu1_MPa"],
        "alpha1": p["alpha1"],
        "D1": p.get("D1", d1_from_ogden_mu1(p["mu1_MPa"])),
        "d1_tied_mu1": p.get("d1_tied_mu1", True),
    }


def run_ogden_forward(
    R_mm: float,
    t_mm: float,
    work: Path,
    tag: str,
    *,
    fit_path: Path,
    ne: int = 8,
    p_final: float = 50.0,
    n_steps: int = 16,
) -> tuple[list[dict], dict]:
    """Return (pv_rows, meta). Raises on CCX failure."""
    work.mkdir(parents=True, exist_ok=True)
    params = load_ogden_params(fit_path)
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
        "ogden1",
        params,
        p_targets(p_final, n_steps),
        label=f"ogden {tag}",
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
