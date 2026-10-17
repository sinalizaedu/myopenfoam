#!/usr/bin/env python3
"""claude-wp1.3 — MULF Gee (2010) com relaxação corrigida.

NAO edita cases/wp1.2/scripts/mulf_gee.py (regra do projeto). Reusa dali
tudo que já está certo (run_p0_solve, prepare_observed_mesh,
verify_ccx_ok, os dataclasses) e reimplementa só `mulf_iterate`, com a
fórmula de relaxação corrigida.

## O bug encontrado em mulf_gee.py::mulf_iterate

A atualização original é:

    x_next[nid] = x_obs[nid] - beta * u(x_ref_atual)[nid]

Isso é o ponto fixo do mapa h(x) = x_obs - beta*u(x). Mas o MULF de Gee
et al. (2010) pede o ponto fixo de g(x) = x_obs - u(x) (sem o beta
multiplicando o u). A relaxação de Picard padrão para g deveria misturar
com o x_ref DA ITERAÇÃO ANTERIOR, não com x_obs fixo:

    x_ref^(k+1) = (1-beta)*x_ref^(k) + beta*(x_obs - u(x_ref^(k)))

Como h != g (a menos que beta=1), o algoritmo original converge para um
ponto fixo ERRADO. Confirmado numericamente nos 8 casos já rodados: o
`verify_error_mm` reportado bate EXATAMENTE com (1-beta)*u_max (razão
1.000 em todos os 8) -- ou seja, o "erro de verificação" não é uma
checagem física independente, é a assinatura algébrica do próprio bug.

Este script roda os mesmos 8 casos com a fórmula corrigida acima, para
comparar Δ% de rigidez antes/depois.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent          # cases/claude-wp1.3/scripts
WP12 = HERE.parents[1] / "wp1.2" / "scripts"     # leitura apenas (Composer)
sys.path.insert(0, str(WP12))

from mulf_gee import (  # noqa: E402  (reuso, NAO editado)
    MULFIteration,
    MULFResult,
    prepare_observed_mesh,  # re-exportado p/ quem importar deste módulo
    run_p0_solve,
    verify_ccx_ok,  # re-exportado
)
from mesh_node_io import (  # noqa: E402
    deformed_coords,
    enforce_symmetry,
    max_coord_delta,
    save_coords_json,
    update_mesh_node_coords,
)

__all__ = ["mulf_iterate_fixed", "prepare_observed_mesh", "verify_ccx_ok"]


def mulf_iterate_fixed(
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
    """Fixed-point MULF com relaxação CORRIGIDA:

        X_ref^(k+1) = (1-beta)*X_ref^(k) + beta*(X_obs - u(X_ref^(k)))

    (a versão original de mulf_gee.py faz X_ref^(k+1) = X_obs - beta*u,
    que é o ponto fixo de um mapa diferente -- ver docstring do módulo).
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
                work, mesh_name, t_mm, model, params, p0_mmhg, tag,
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
            # CORREÇÃO: relaxa contra x_ref anterior (xb), não contra x_obs (xo)
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
        work, mesh_name, t_mm, model, params, p0_mmhg, "verify",
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
