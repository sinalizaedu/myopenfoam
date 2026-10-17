#!/usr/bin/env python3
"""WP1.5 — forward CCX (octant spherical shell) com P0 e p_final explícitos.

Corrige o achado do piloto de espécie: os runners do wp1.2
(``ogden_forward_run.py`` / ``yeoh_forward_run.py``) fixam P0=16,9 mmHg
(basal humano) tanto na rampa de pressão quanto no V=0 de ``extract_pv`` —
valor errado para o coelho anestesiado, cujo basal é 26,7 mmHg
(equilíbrio de Goldmann: Q_prod=3,06 µL/min, C_out=0,26 µL/min/mmHg,
Pev=15,5 mmHg, frac_uv=0,05 — Kiel et al. 2011/2015; Fourman & Garner 1989).

Aqui ``p0_mmhg`` e ``p_final_mmhg`` entram por fora (por espécie).
Reusa apenas os *loaders* de material do wp1.2 (não dependem de P0);
rampa e extração são locais. Nenhum módulo do wp1.2 é editado.
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
from ogden_forward_run import load_ogden_params  # noqa: E402
from write_deck import write_deck  # noqa: E402
from yeoh_material import load_yeoh_params  # noqa: E402

MODELS = {"ogden": "ogden1", "yeoh": "yeoh2"}


def pressure_ramp(p0_mmhg: float, p_final_mmhg: float, n_steps: int) -> list[float]:
    """Alvos absolutos de pressão: n_steps valores de P0+ΔP/n até p_final."""
    return [p0_mmhg + (p_final_mmhg - p0_mmhg) * i / n_steps for i in range(1, n_steps + 1)]


def run_forward(
    material: str,
    R_mm: float,
    t_mm: float,
    work: Path,
    tag: str,
    *,
    fit_path: Path,
    p0_mmhg: float,
    p_final_mmhg: float,
    ne: int = 8,
    n_steps: int = 16,
) -> tuple[list[dict], dict]:
    """Forward NLGEOM com basal P0 da espécie. Levanta exceção se o CCX falhar."""
    if material not in MODELS:
        raise ValueError(f"material desconhecido: {material}")
    work.mkdir(parents=True, exist_ok=True)
    params = (
        load_ogden_params(fit_path) if material == "ogden" else load_yeoh_params(fit_path)
    )
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
        MODELS[material],
        params,
        pressure_ramp(p0_mmhg, p_final_mmhg, n_steps),
        label=f"{material} {tag} (P0={p0_mmhg} por espécie)",
        bc_mode="symmetry_octant",
        p0_mmhg=p0_mmhg,
    )
    frd = run_ccx(deck, clean=True)
    rows = extract_pv(deck, frd, R_mm, p0_mmhg=p0_mmhg)
    meta = {
        "R_mm": R_mm,
        "t_mm": t_mm,
        "ne": ne,
        "p0_mmHg": p0_mmhg,
        "p_final_mmHg": p_final_mmhg,
        "params": params,
        "status": "OK",
    }
    return rows, meta
