#!/usr/bin/env python3
"""Gee et al. (2010) MULF fixed-point iteration for hyperelastic pre-tension.

Find relaxed reference coordinates X_ref such that applying P0 on X_ref reproduces
observed geometry X_obs (in vivo shape at physiological pressure).
"""
from __future__ import annotations

import json
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
WP1 = HERE.parents[1] / "wp1.1" / "scripts"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(WP1))

from ccx_utils import run_ccx  # noqa: E402
from extract_K import _map_frd_disp_to_mesh, parse_nsets, parse_nodes  # noqa: E402
from mesh_node_io import (  # noqa: E402
    deformed_coords,
    enforce_symmetry,
    max_coord_delta,
    save_coords_json,
    update_mesh_node_coords,
)
from write_deck_p0 import write_deck_p0  # noqa: E402


def _frd_module():
    for _cand in (
        Path("/opt/brunaStuff/artigo_mestrado"),
        WP1.parents[2] / "brunaStuff" / "artigo_mestrado",
    ):
        if (_cand / "frd_stress.py").is_file():
            sys.path.insert(0, str(_cand))
            break
    from frd_stress import parse_frd  # noqa: E402

    return parse_frd


def extract_nodal_disp_at_p0(
    mesh_path: Path,
    frd_path: Path,
    t_mm: float,
) -> dict[int, tuple[float, float, float]]:
    parse_frd = _frd_module()
    mesh_nodes = parse_nodes(mesh_path)
    frd_nodes, _, steps = parse_frd(frd_path)
    if not steps:
        raise ValueError(f"No steps in {frd_path}")
    disp_raw = steps[-1]["disp"]
    disp = _map_frd_disp_to_mesh(mesh_nodes, frd_nodes, disp_raw, t_mm)
    if len(disp) < len(mesh_nodes):
        raise ValueError(
            f"Mapped {len(disp)}/{len(mesh_nodes)} nodal displacements from {frd_path}"
        )
    return disp


def verify_ccx_ok(log_path: Path) -> tuple[bool, str]:
    if not log_path.is_file():
        return False, f"missing {log_path}"
    text = log_path.read_text(errors="replace")
    if "***ERROR" in text or "SOLUTION IS NOT CONVERGED" in text.upper():
        return False, "CalculiX error or no convergence"
    if not any(m in text.upper() for m in ("JOB FINISHED", "THE ANALYSIS HAS BEEN COMPLETED")):
        return False, "analysis incomplete"
    return True, "OK"


@dataclass
class MULFIteration:
    k: int
    ccx_status: str
    delta_x_ref_mm: float
    max_u_mm: float
    beta: float


@dataclass
class MULFResult:
    converged: bool
    n_iter: int
    x_ref_delta_mm: float
    verify_error_mm: float
    iterations: list[MULFIteration]
    x_ref_path: str
    mesh_work: str


def run_p0_solve(
    work: Path,
    mesh_name: str,
    t_mm: float,
    model: str,
    params: dict,
    p0_mmhg: float,
    tag: str,
) -> tuple[Path, dict[int, tuple[float, float, float]], str]:
    deck = work / f"p0_{tag}.inp"
    write_deck_p0(
        deck,
        mesh_name,
        t_mm,
        model,
        params,
        p0_mmhg=p0_mmhg,
        label=f"MULF P0 {tag}",
        bc_mode="symmetry_octant",
    )
    frd = run_ccx(deck, clean=True)
    log = work / f"log_p0_{tag}.txt"
    ok, msg = verify_ccx_ok(log)
    if not ok:
        raise RuntimeError(f"P0 solve failed ({tag}): {msg}")
    disp = extract_nodal_disp_at_p0(work / mesh_name, frd, t_mm)
    return frd, disp, msg


def mulf_iterate(
    x_obs: dict[int, np.ndarray],
    work: Path,
    mesh_name: str,
    nsets: dict[str, list[int]],
    *,
    t_mm: float,
    model: str,
    params: dict,
    p0_mmhg: float,
    max_iter: int = 12,
    tol_mm: float = 1e-3,
    beta: float = 0.7,
    beta_min: float = 0.35,
) -> MULFResult:
    """Fixed-point MULF (Gee et al. 2010): Picard on g(X)=X_obs - u(X).

    X_ref^(k+1) = (1-beta)*X_ref^(k) + beta*(X_obs - u(X_ref^(k))).
    """
    mesh_path = work / mesh_name
    x_ref = {nid: np.array(x, dtype=float) for nid, x in x_obs.items()}
    save_coords_json(work / "x_obs_mm.json", x_obs)
    history: list[MULFIteration] = []
    converged = False
    b = float(beta)

    for k in range(max_iter):
        x_before = {nid: np.array(x, dtype=float) for nid, x in x_ref.items()}
        update_mesh_node_coords(mesh_path, x_ref)

        tag = f"iter{k:02d}"
        try:
            _, disp, status = run_p0_solve(
                work,
                mesh_name,
                t_mm,
                model,
                params,
                p0_mmhg,
                tag,
            )
        except RuntimeError:
            if b > beta_min + 1e-9:
                b = max(beta_min, 0.5 * b)
                continue
            raise

        u_max = max(float(np.linalg.norm(np.asarray(u))) for u in disp.values())
        x_next = {}
        for nid, xb in x_before.items():
            xo = x_obs[nid]
            du = np.asarray(disp.get(nid, (0.0, 0.0, 0.0)), dtype=float)
            x_next[nid] = (1.0 - b) * xb + b * (xo - du)
        x_next = enforce_symmetry(x_next, nsets)
        delta = max_coord_delta(x_before, x_next)

        history.append(
            MULFIteration(k=k, ccx_status=status, delta_x_ref_mm=delta, max_u_mm=u_max, beta=b)
        )

        x_ref = x_next
        if delta < tol_mm:
            converged = True
            break

    x_ref_path = work / "x_ref_converged.json"
    save_coords_json(x_ref_path, x_ref)
    update_mesh_node_coords(mesh_path, x_ref)

    _, disp_v, _ = run_p0_solve(
        work,
        mesh_name,
        t_mm,
        model,
        params,
        p0_mmhg,
        "verify",
    )
    x_pred = enforce_symmetry(deformed_coords(x_ref, disp_v), nsets)
    verify_err = max_coord_delta(x_pred, x_obs)

    return MULFResult(
        converged=converged,
        n_iter=len(history),
        x_ref_delta_mm=history[-1].delta_x_ref_mm if history else float("nan"),
        verify_error_mm=verify_err,
        iterations=history,
        x_ref_path=str(x_ref_path),
        mesh_work=str(work),
    )


def prepare_observed_mesh(
    R_mm: float,
    t_mm: float,
    ne: int,
    work: Path,
    label: str,
) -> tuple[Path, str, dict[int, np.ndarray], dict[str, list[int]]]:
    """Create observed mesh X_obs (in vivo geometry at P0) and working copy."""
    from gen_sphere_shell_mesh import write_mesh  # noqa: E402

    work.mkdir(parents=True, exist_ok=True)
    mesh_obs = work / "mesh_obs.inp"
    mesh_work = work / "mesh.inp"
    write_mesh(
        mesh_obs,
        R_mm,
        t_mm,
        ne,
        2,
        label,
        bc_mode="symmetry_octant",
        mesh_kind="spherical",
        theta_min_deg=3.0,
        reduced=True,
    )
    shutil.copy2(mesh_obs, mesh_work)
    x_obs = parse_nodes(mesh_obs)
    nsets = parse_nsets(mesh_obs)
    return work, "mesh.inp", x_obs, nsets
