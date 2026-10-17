#!/usr/bin/env python3
"""wp1.2 — fit Ogden N=1 a Pallikaris, versao independente (Claude/Sonnet).

Roda em paralelo ao `fit_pallikaris.py` existente (Cursor/Composer), pra
comparar resultado. NAO edita nenhum arquivo existente -- so importa os
modulos ja validados (malha, deck writer, extracao de curva P-V) e escreve
saida num diretorio proprio (`output_octant_claude/`), sem sobrescrever
`output_octant/`.

Duas escolhas deliberadamente diferentes da versao existente, pra fechar as
perguntas 2 e 3 do handoff:

  1. D1 LIVRE (nao amarrado a mu1 por D1 = 0.5*(1.0204/mu1)). Otimizado em
     escala log (log10 D1) porque o proprio ccx_utils.py deste repo observa
     que o CalculiX-Ogden fica instavel fora de uma faixa quase-incompressivel
     (~1e-6), bem abaixo da faixa que a formula amarrada produz (~0.05-0.5)
     -- vale checar se o ajuste livre migra pra essa regiao ou confirma a
     formula amarrada por conta propria.

  2. Otimizador mais devagar e mais completo: diff_step menor (0.005 em vez
     de 0.02), max_nfev maior (60 em vez de 25), x0 num ponto intermediario
     entre os dois resultados conflitantes ja observados (mu1=5.61/alpha1=0.79
     de um lado, mu1=7.16/alpha1=0.50 do outro), e o limite inferior de
     alpha1 ampliado pra 0.3 (a versao existente trava em 0.5 -- vale
     verificar se o minimo real fica ali ou e cortado pelo bound).

Uso (dentro do container, mesmo ambiente da fit_pallikaris.py existente):
    python3 fit_pallikaris_claude.py

Saida: cases/wp1.2/output_octant_claude/{RESULTS.md,fit_results.json,...}
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

HERE = Path(__file__).resolve().parent  # sera copiado para cases/wp1.2/scripts/
WP1 = HERE.parents[1] / "wp1.1" if (HERE.parents[1] / "wp1.1").is_dir() else HERE.parent.parent / "wp1.1"
WP12 = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(WP1 / "scripts"))

from ccx_utils import run_ccx  # noqa: E402
from extract_pv_curve import extract_pv  # noqa: E402
from fit_hyperelastic import ExpPoint, fit_quality  # noqa: E402
from gen_sphere_shell_mesh import write_mesh  # noqa: E402
from write_deck import write_deck  # noqa: E402

P0_MMHG = 16.9
KF_PER_UL = 0.0126  # Pallikaris et al. 2005, valor real (nao o 0.00581 recalibrado do WP0)
DP_FEA_FINAL = 80.0  # ramp bem acima do alvo, evita a regiao sensivel perto de 20 mmHg


@dataclass
class Geometry:
    R_mm: float
    t_mm: float
    source: str = "human_wp1.1"
    nu: float = 0.47
    E_mpa: float = 3.0


def pallikaris_pressure(v_uL: float, p0: float = P0_MMHG, kf: float = KF_PER_UL) -> float:
    return p0 * (10.0 ** (kf * v_uL))


def generate_pallikaris_target(v_max: float = 50.0, n_pts: int = 11) -> list[ExpPoint]:
    vs = np.linspace(0.0, v_max, n_pts)
    return [ExpPoint(V_uL=float(v), P_mmHg=float(pallikaris_pressure(float(v)) - P0_MMHG)) for v in vs]


class PallikarisForwardClaude:
    """Mesma malha/deck da versao existente -- so o tag muda, pra nao colidir arquivo."""

    def __init__(self, geom: Geometry, work_dir: Path, ne: int = 6,
                 p_max_mmhg: float = DP_FEA_FINAL, n_load_steps: int = 16,
                 p0_mmhg: float = P0_MMHG):
        self.geom = geom
        self.work_dir = work_dir
        self.ne = ne
        self.p0_mmhg = p0_mmhg
        self.p_max_mmhg = p_max_mmhg
        self.n_load_steps = n_load_steps
        self.mesh_path = work_dir / "mesh.inp"
        work_dir.mkdir(parents=True, exist_ok=True)
        write_mesh(
            self.mesh_path, geom.R_mm, geom.t_mm, ne, 2,
            label=f"pallikaris_claude ne={ne}", bc_mode="symmetry_octant",
            mesh_kind="spherical", theta_min_deg=3.0, reduced=True,
        )

    def _p_targets(self) -> list[float]:
        return [self.p0_mmhg + (self.p_max_mmhg - self.p0_mmhg) * i / self.n_load_steps
                for i in range(1, self.n_load_steps + 1)]

    def run(self, mu1: float, alpha1: float, d1: float, tag: str) -> tuple[np.ndarray, np.ndarray]:
        params = {"mu1_MPa": float(mu1), "alpha1": float(alpha1),
                   "d1_tied_mu1": False, "D1": float(d1)}
        deck = self.work_dir / f"claude_{tag}.inp"
        write_deck(
            deck, self.mesh_path.name, self.geom.t_mm, "ogden1", params,
            self._p_targets(), label=f"wp1.2 pallikaris claude {tag}",
            nu=self.geom.nu, E_mpa=self.geom.E_mpa,
            bc_mode="symmetry_octant", p0_mmhg=self.p0_mmhg,
        )
        frd = run_ccx(deck, clean=True)
        rows = extract_pv(deck, frd, self.geom.R_mm, p0_mmhg=self.p0_mmhg)
        v = np.array([r["dV_uL"] for r in rows], dtype=float)
        p = np.array([r["p_mmhg"] for r in rows], dtype=float)
        return v, p


def fit_ogden1_free_d1(forward: PallikarisForwardClaude, exp: list[ExpPoint],
                         max_nfev: int = 60) -> dict:
    v_exp = np.array([e.V_uL for e in exp])
    p_exp = np.array([e.P_mmHg for e in exp])

    # x = [mu1, alpha1, log10(D1)] -- log-D1 pra nao distorcer a escala do
    # otimizador entre 1e-6 (quase-incompressivel) e 1e-1 (formula amarrada).
    x0 = np.array([6.3, 0.65, np.log10(1.0e-4)])  # ponto intermediario deliberado
    lo = np.array([0.5, 0.3, np.log10(1.0e-8)])
    hi = np.array([10.0, 3.0, np.log10(1.0)])
    n_eval = {"n": 0}

    def residuals(x: np.ndarray) -> np.ndarray:
        n_eval["n"] += 1
        tag = f"opt_{n_eval['n']:03d}"
        mu1, alpha1, log_d1 = float(x[0]), float(x[1]), float(x[2])
        d1 = 10.0 ** log_d1
        try:
            v_fea, p_fea = forward.run(mu1, alpha1, d1, tag=tag)
        except Exception as exc:  # CCX divergiu nesse ponto -- penaliza, nao trava o fit
            print(f"  [{tag}] FALHOU mu1={mu1:.4f} alpha1={alpha1:.4f} D1={d1:.2e}: {exc}",
                  file=sys.stderr)
            return np.ones_like(p_exp) * 100.0
        order = np.argsort(v_fea)
        v_fea, p_fea = v_fea[order], p_fea[order]
        if v_fea.max() < v_exp.max() * 0.9:
            return np.ones_like(p_exp) * 50.0
        dp_fea = p_fea - forward.p0_mmhg
        dp_pred = np.interp(v_exp, v_fea, dp_fea)
        return dp_pred - p_exp

    t0 = time.time()
    res = least_squares(
        residuals, x0, bounds=(lo, hi), max_nfev=max_nfev,
        ftol=1e-10, xtol=1e-10, diff_step=0.005, x_scale="jac", verbose=2,
    )
    fit_time = time.time() - t0
    mu1, alpha1, log_d1 = (float(v) for v in res.x)
    d1 = 10.0 ** log_d1
    v_fea, p_fea = forward.run(mu1, alpha1, d1, tag="final")
    order = np.argsort(v_fea)
    v_fea, p_fea = v_fea[order], p_fea[order]
    dp_fea = p_fea - forward.p0_mmhg
    dp_at_exp = np.interp(v_exp, v_fea, dp_fea)
    quality = fit_quality(p_exp, dp_at_exp)

    return {
        "model": "ogden1_D1_free_claude",
        "params": {"mu1_MPa": mu1, "alpha1": alpha1, "D1": d1, "d1_tied_mu1": False},
        "quality": quality,
        "optimizer": {
            "success": bool(res.success), "message": res.message,
            "nfev": int(res.nfev), "cost": float(res.cost), "fit_time_s": fit_time,
            "x0": x0.tolist(), "bounds": {"lo": lo.tolist(), "hi": hi.tolist()},
            "diff_step": 0.005,
        },
        "fea_curve": [{"V_uL": float(v), "P_mmHg": float(p)} for v, p in zip(v_fea, p_fea)],
        "exp_at_fit": [
            {"V_uL": float(v), "P_exp_dP_mmHg": float(pe), "P_fea_dP_mmHg": float(pm)}
            for v, pe, pm in zip(v_exp, p_exp, dp_at_exp)
        ],
        "fit_convention": "delta_P_above_P0",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--R", type=float, default=12.0)
    ap.add_argument("--t", type=float, default=0.5)
    ap.add_argument("--ne", type=int, default=6)
    ap.add_argument("--max-nfev", type=int, default=60)
    ap.add_argument("--dp-fea-final", type=float, default=DP_FEA_FINAL)
    ap.add_argument("--out", type=Path, default=WP12 / "output_octant_claude")
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    exp = generate_pallikaris_target()

    geom = Geometry(R_mm=args.R, t_mm=args.t)
    work = args.out / "ccx_runs" / "ogden1_free_d1"
    forward = PallikarisForwardClaude(geom, work, ne=args.ne, p_max_mmhg=args.dp_fea_final)
    result = fit_ogden1_free_d1(forward, exp, max_nfev=args.max_nfev)

    out = {
        "geometry": asdict(geom),
        "pallikaris": {"P0_mmHg": P0_MMHG, "Kf_per_uL": KF_PER_UL},
        "fea_ramp": {"P_final_mmHg_abs": args.dp_fea_final},
        "mesh": {"kind": "spherical", "ne": args.ne, "bc_mode": "symmetry_octant"},
        "note": "D1 livre (log-parametrizado), max_nfev=60, diff_step=0.005, "
                "x0 intermediario entre os dois resultados conflitantes anteriores. "
                "Comparar contra cases/wp1.2/output_octant/fit_results.json (Cursor/Composer).",
        "selected": result,
    }
    (args.out / "fit_results.json").write_text(json.dumps(out, indent=2))

    q = result["quality"]
    p = result["params"]
    lines = [
        "# wp1.2 -- Ogden N=1 vs Pallikaris (octante, D1 LIVRE, versao Claude)\n",
        f"- **Geometry**: R={geom.R_mm} mm, t={geom.t_mm} mm",
        f"- **Pallikaris**: P0={P0_MMHG} mmHg, Kf={KF_PER_UL} /uL",
        f"- **FEA ramp**: P_final={args.dp_fea_final} mmHg (abs)",
        f"- **mu1**: {p['mu1_MPa']:.4f} MPa",
        f"- **alpha1**: {p['alpha1']:.4f}",
        f"- **D1** (livre, log-fit): {p['D1']:.6e}",
        f"- **R2**: {q['R2']:.4f}",
        f"- **Residuo max**: {q['max_residual_mmHg']:.2f} mmHg",
        f"- **Otimizador**: nfev={result['optimizer']['nfev']}, "
        f"success={result['optimizer']['success']}, diff_step=0.005",
        "",
        "Compare contra `../output_octant/fit_results.json` "
        "(mu1 tied D1, diff_step=0.02, max_nfev=25) e contra o resultado "
        "reportado no README_HANDOFF (mu1=7.16, alpha1=0.50, R2=0.93).",
    ]
    (args.out / "RESULTS.md").write_text("\n".join(lines))
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
