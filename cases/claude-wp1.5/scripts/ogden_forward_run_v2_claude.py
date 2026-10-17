#!/usr/bin/env python3
"""Ogden-N1 forward run com P0 e p_final parametrizados por especie.

Correcao do achado do WP1.5: `ogden_forward_run.py` (usado pelo piloto
original) tem P0_MMHG=16.9 fixo no modulo, aplicado tanto ao humano
quanto ao coelho. Fisiologicamente o basal do coelho anestesiado e
26.7 mmHg (ver relatorio WP0, LaTeX, secao "Producao trabecular e
uveoescleral"; mesmos valores usados em claude_dose_isquemica.py do
WP4.2). Este modulo generaliza run_ogden_forward para receber p0_mmhg
e p_final_mmhg explicitos, para que cada especie use sua propria
rampa de pressao.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WP12 = HERE.parents[1] / "wp1.2" / "scripts"
sys.path.insert(0, str(WP12))

from ccx_utils import d1_from_ogden_mu1, run_ccx  # noqa: E402
from extract_pv_curve import extract_pv  # noqa: E402
from gen_sphere_shell_mesh import write_mesh  # noqa: E402
from write_deck import write_deck  # noqa: E402


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


def p_targets(p0: float, p_final: float, n_steps: int) -> list[float]:
    return [p0 + (p_final - p0) * i / n_steps for i in range(1, n_steps + 1)]


def run_ogden_forward_v2(
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
    """Igual a run_ogden_forward, mas p0/p_final vem de fora (por especie)."""
    work.mkdir(parents=True, exist_ok=True)
    params = load_ogden_params(fit_path)
    mesh = work / f"{tag}_mesh.inp"
    write_mesh(
        mesh, R_mm, t_mm, ne, 2, tag,
        bc_mode="symmetry_octant", mesh_kind="spherical",
        theta_min_deg=3.0, reduced=True,
    )
    deck = work / f"{tag}.inp"
    write_deck(
        deck, mesh.name, t_mm, "ogden1", params,
        p_targets(p0_mmhg, p_final_mmhg, n_steps),
        label=f"ogden {tag} (P0={p0_mmhg} especifico da especie)",
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
