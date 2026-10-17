#!/usr/bin/env python3
"""claude-wp1.2 -- ajuste Ogden N=1 vs Pallikaris com MULTI-START.

Objetivo: mapear quantos minimos locais existem no espaco (mu1, alpha1, D1)
para o alvo Pallikaris. Ate agora ha evidencia de pelo menos DOIS:

  A. (mu1~2.14, alpha1~1.77, D1~0.24)  R2 ~ 0.97, resid max ~ 2.2 mmHg
     -> reportado no main.pdf (WP1.2 Resultados), otimizador saindo de
        x0=(2.14, 1.77). Fit MUITO melhor.
  B. (mu1~5-7, alpha1~0.5, D1 livre ~1e-4 ou amarrado ~0.07)  R2 ~ 0.93
     -> tanto o fit_pallikaris.py (Cursor, D1 amarrado) quanto o meu
        fit_pallikaris_claude.py (Sonnet, D1 livre) recentes convergem
        para essa vizinhanca. Fit pior.

Este script roda o mesmo otimizador (least_squares, D1 livre em log10,
diff_step=0.005, max_nfev=40) partindo de multiplos x0 deliberadamente
espalhados, e reporta cada minimo alcancado, o custo, e agrupa em
clusters no espaco de parametros. Serve pra:

  1. Confirmar/refutar que existem so dois minimos.
  2. Identificar qual e o global (menor custo).
  3. Dizer se o x0 default do fit_pallikaris.py (2.14, 1.77) esta mesmo
     na bacia do minimo bom -- e se sim, por que o run mais recente
     saiu de la e caiu no ruim (talvez rampa de 80 mmHg em vez de 50
     mudou a curva forward suficiente pra mudar a topologia).

Nao edita nenhum arquivo existente. Reaproveita write_mesh, write_deck,
extract_pv, fit_hyperelastic, ccx_utils do wp1.1/scripts e wp1.2/scripts.

Uso (dentro do container):
    cd /simulation/claude-wp1.2 && python3 scripts/fit_pallikaris_multistart_claude.py

Custo estimado: 6 x0 x ~30 nfev/otimizacao x ~12s/ccx = ~35-45 min.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

HERE = Path(__file__).resolve().parent
CASE_ROOT = HERE.parent          # cases/claude-wp1.2/
CASES_DIR = CASE_ROOT.parent      # cases/
WP1_SCRIPTS = CASES_DIR / "wp1.1" / "scripts"
WP12_SCRIPTS = CASES_DIR / "wp1.2" / "scripts"
sys.path.insert(0, str(WP12_SCRIPTS))
sys.path.insert(0, str(WP1_SCRIPTS))

from ccx_utils import run_ccx  # noqa: E402
from extract_pv_curve import extract_pv  # noqa: E402
from fit_hyperelastic import ExpPoint, fit_quality  # noqa: E402
from gen_sphere_shell_mesh import write_mesh  # noqa: E402
from write_deck import write_deck  # noqa: E402

P0_MMHG = 16.9
KF_PER_UL = 0.0126
DP_FEA_FINAL = 80.0

# x0 candidatos espalhados deliberadamente:
#  - os dois minimos conhecidos + variacoes em torno deles
#  - dois pontos "no meio do mapa" pra checar bacias intermediarias
X0_CANDIDATES = [
    # (mu1, alpha1, log10(D1))       comentario
    (2.14, 1.77, np.log10(0.238)),   # otimo A conhecido (main.pdf)
    (5.44, 0.49, np.log10(2.26e-4)), # meu otimo B recente (D1 livre)
    (7.16, 0.50, np.log10(0.0713)),  # otimo B do Cursor (D1 amarrado)
    (1.0,  2.5,  np.log10(1.0e-2)),  # cobertura: mu1 baixo, alpha1 alto
    (4.0,  1.0,  np.log10(1.0e-3)),  # cobertura: meio-caminho
    (9.0,  0.6,  np.log10(1.0e-6)),  # cobertura: mu1 alto, quase-incompressivel
]

# bounds unificados (mesmos do fit_pallikaris_claude.py, o alpha1 desce ate 0.3)
LO = np.array([0.3,  0.3, np.log10(1.0e-8)])
HI = np.array([12.0, 3.5, np.log10(1.0)])


@dataclass
class Geometry:
    R_mm: float
    t_mm: float
    source: str = "human_wp1.1"
    nu: float = 0.47
    E_mpa: float = 3.0


def pallikaris_pressure(v_uL: float) -> float:
    return P0_MMHG * (10.0 ** (KF_PER_UL * v_uL))


def generate_target(v_max: float = 50.0, n: int = 11) -> list[ExpPoint]:
    vs = np.linspace(0.0, v_max, n)
    return [ExpPoint(V_uL=float(v),
                       P_mmHg=float(pallikaris_pressure(float(v)) - P0_MMHG))
             for v in vs]


class Forward:
    def __init__(self, geom: Geometry, work_dir: Path, ne: int = 6):
        self.geom = geom
        self.work_dir = work_dir
        self.ne = ne
        self.mesh_path = work_dir / "mesh.inp"
        work_dir.mkdir(parents=True, exist_ok=True)
        write_mesh(self.mesh_path, geom.R_mm, geom.t_mm, ne, 2,
                    label=f"multistart ne={ne}", bc_mode="symmetry_octant",
                    mesh_kind="spherical", theta_min_deg=3.0, reduced=True)
        self.p_targets = [P0_MMHG + (DP_FEA_FINAL - P0_MMHG) * i / 16
                            for i in range(1, 17)]

    def run(self, mu1: float, alpha1: float, d1: float, tag: str):
        params = {"mu1_MPa": float(mu1), "alpha1": float(alpha1),
                   "d1_tied_mu1": False, "D1": float(d1)}
        deck = self.work_dir / f"multi_{tag}.inp"
        write_deck(deck, self.mesh_path.name, self.geom.t_mm, "ogden1", params,
                    self.p_targets, label=f"multistart {tag}",
                    nu=self.geom.nu, E_mpa=self.geom.E_mpa,
                    bc_mode="symmetry_octant", p0_mmhg=P0_MMHG)
        frd = run_ccx(deck, clean=True)
        rows = extract_pv(deck, frd, self.geom.R_mm, p0_mmhg=P0_MMHG)
        v = np.array([r["dV_uL"] for r in rows], dtype=float)
        p = np.array([r["p_mmhg"] for r in rows], dtype=float)
        return v, p


def one_fit(forward: Forward, exp: list[ExpPoint],
              x0: tuple[float, float, float], run_prefix: str,
              max_nfev: int = 40) -> dict:
    v_exp = np.array([e.V_uL for e in exp])
    p_exp = np.array([e.P_mmHg for e in exp])
    n_eval = {"n": 0}

    def residuals(x):
        n_eval["n"] += 1
        tag = f"{run_prefix}_e{n_eval['n']:03d}"
        mu1, alpha1, log_d1 = float(x[0]), float(x[1]), float(x[2])
        d1 = 10.0 ** log_d1
        try:
            v_fea, p_fea = forward.run(mu1, alpha1, d1, tag=tag)
        except Exception as exc:
            print(f"  [{tag}] FALHOU mu1={mu1:.3f} a1={alpha1:.3f} "
                   f"D1={d1:.2e}: {exc}", file=sys.stderr)
            return np.ones_like(p_exp) * 100.0
        order = np.argsort(v_fea)
        v_fea, p_fea = v_fea[order], p_fea[order]
        if v_fea.max() < v_exp.max() * 0.9:
            return np.ones_like(p_exp) * 50.0
        dp_fea = p_fea - P0_MMHG
        dp_pred = np.interp(v_exp, v_fea, dp_fea)
        return dp_pred - p_exp

    t0 = time.time()
    res = least_squares(residuals, np.array(x0, dtype=float),
                          bounds=(LO, HI), max_nfev=max_nfev,
                          ftol=1e-10, xtol=1e-10, diff_step=0.005,
                          x_scale="jac", verbose=1)
    dt = time.time() - t0
    mu1, alpha1, log_d1 = (float(v) for v in res.x)
    d1 = 10.0 ** log_d1
    v_fea, p_fea = forward.run(mu1, alpha1, d1, tag=f"{run_prefix}_final")
    order = np.argsort(v_fea)
    v_fea, p_fea = v_fea[order], p_fea[order]
    dp_at_exp = np.interp(v_exp, np.sort(v_fea), (p_fea - P0_MMHG)[order])
    quality = fit_quality(p_exp, dp_at_exp)
    return {
        "x0": {"mu1": x0[0], "alpha1": x0[1], "log10_D1": x0[2]},
        "x_final": {"mu1_MPa": mu1, "alpha1": alpha1, "D1": d1,
                      "log10_D1": log_d1},
        "quality": quality,
        "cost": float(res.cost), "nfev": int(res.nfev),
        "success": bool(res.success), "message": res.message,
        "time_s": dt,
    }


def cluster(fits: list[dict], tol_mu1: float = 0.5, tol_alpha1: float = 0.1,
             tol_log_d1: float = 1.0) -> list[list[int]]:
    """Agrupa fits por proximidade em (mu1, alpha1, log10 D1)."""
    clusters: list[list[int]] = []
    for i, f in enumerate(fits):
        x = f["x_final"]
        placed = False
        for c in clusters:
            ref = fits[c[0]]["x_final"]
            if (abs(x["mu1_MPa"] - ref["mu1_MPa"]) < tol_mu1
                and abs(x["alpha1"] - ref["alpha1"]) < tol_alpha1
                and abs(x["log10_D1"] - ref["log10_D1"]) < tol_log_d1):
                c.append(i)
                placed = True
                break
        if not placed:
            clusters.append([i])
    return clusters


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--R", type=float, default=12.0)
    ap.add_argument("--t", type=float, default=0.5)
    ap.add_argument("--ne", type=int, default=6)
    ap.add_argument("--max-nfev", type=int, default=40)
    ap.add_argument("--out", type=Path, default=CASE_ROOT / "output_multistart")
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    exp = generate_target()
    geom = Geometry(R_mm=args.R, t_mm=args.t)
    work = args.out / "ccx_runs"
    forward = Forward(geom, work, ne=args.ne)

    print(f"Multi-start: {len(X0_CANDIDATES)} pontos iniciais, "
          f"max_nfev={args.max_nfev} cada")
    fits: list[dict] = []
    for i, x0 in enumerate(X0_CANDIDATES):
        print(f"\n=== x0 #{i+1}/{len(X0_CANDIDATES)}: "
              f"mu1={x0[0]}, alpha1={x0[1]}, log10(D1)={x0[2]:.3f} ===")
        f = one_fit(forward, exp, x0, run_prefix=f"x{i+1}",
                     max_nfev=args.max_nfev)
        fits.append(f)
        print(f"  -> mu1={f['x_final']['mu1_MPa']:.4f} "
               f"alpha1={f['x_final']['alpha1']:.4f} "
               f"D1={f['x_final']['D1']:.3e} "
               f"R2={f['quality']['R2']:.4f} cost={f['cost']:.3f}")

    clusters = cluster(fits)
    fits_sorted = sorted(range(len(fits)), key=lambda i: fits[i]["cost"])
    best = fits_sorted[0]

    lines = ["# claude-wp1.2 -- Ogden N=1 vs Pallikaris, MULTI-START\n",
             f"Alvo: Pallikaris P0={P0_MMHG} mmHg, Kf={KF_PER_UL} /uL.",
             f"Geometria: R={geom.R_mm} mm, t={geom.t_mm} mm, octante ne={args.ne}.",
             f"Rampa FEA: 0..{DP_FEA_FINAL} mmHg (abs).",
             f"Otimizador: D1 livre (log10), bounds mu1=[{LO[0]},{HI[0]}] "
             f"alpha1=[{LO[1]},{HI[1]}] log10(D1)=[{LO[2]:.1f},{HI[2]:.1f}].\n",
             "## Todos os fits, ordenados por custo\n",
             "| rank | x0 (mu1, alpha1, log10D1) | mu1_final | alpha1_final | D1_final | R2 | cost | nfev | cluster |",
             "|---:|---|---:|---:|---:|---:|---:|---:|---:|"]
    cluster_of = {i: ci for ci, cs in enumerate(clusters) for i in cs}
    for rank, i in enumerate(fits_sorted, 1):
        f = fits[i]
        x0 = f["x0"]
        xf = f["x_final"]
        lines.append(
            f"| {rank} | ({x0['mu1']:.2f}, {x0['alpha1']:.2f}, {x0['log10_D1']:.1f}) "
            f"| {xf['mu1_MPa']:.3f} | {xf['alpha1']:.3f} | {xf['D1']:.2e} "
            f"| {f['quality']['R2']:.4f} | {f['cost']:.3f} | {f['nfev']} "
            f"| C{cluster_of[i]+1} |"
        )

    lines.append(f"\n## {len(clusters)} cluster(s) distintos encontrados\n")
    for ci, cs in enumerate(clusters):
        ref = fits[cs[0]]["x_final"]
        best_in = min(cs, key=lambda i: fits[i]["cost"])
        lines.append(f"- **C{ci+1}** ({len(cs)} fit{'s' if len(cs)>1 else ''}): "
                      f"mu1~{ref['mu1_MPa']:.2f}, alpha1~{ref['alpha1']:.2f}, "
                      f"D1~{ref['D1']:.2e}, "
                      f"melhor R2={fits[best_in]['quality']['R2']:.4f}, "
                      f"cost={fits[best_in]['cost']:.3f}")

    best_f = fits[best]
    lines.append(f"\n## Global (menor custo)\n"
                  f"- mu1 = {best_f['x_final']['mu1_MPa']:.4f} MPa\n"
                  f"- alpha1 = {best_f['x_final']['alpha1']:.4f}\n"
                  f"- D1 = {best_f['x_final']['D1']:.4e}\n"
                  f"- R2 = {best_f['quality']['R2']:.4f}, "
                  f"resid max = {best_f['quality']['max_residual_mmHg']:.2f} mmHg\n"
                  f"- Veio de x0 = ({best_f['x0']['mu1']}, "
                  f"{best_f['x0']['alpha1']}, log10D1={best_f['x0']['log10_D1']:.2f})\n")

    (args.out / "RESULTS.md").write_text("\n".join(lines))
    (args.out / "multistart_results.json").write_text(json.dumps(
        {"geometry": asdict(geom),
         "pallikaris": {"P0_mmHg": P0_MMHG, "Kf_per_uL": KF_PER_UL},
         "n_x0": len(X0_CANDIDATES), "fits": fits,
         "clusters": [[int(i) for i in c] for c in clusters],
         "best_index": int(best)}, indent=2))
    print("\n" + "\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
