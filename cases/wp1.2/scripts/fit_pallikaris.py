#!/usr/bin/env python3
"""WP1.2 — fit Ogden N=1 to Pallikaris synthetic P(V) on spherical octant."""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

HERE = Path(__file__).resolve().parent
WP1 = HERE.parents[1] / "wp1.1"
WP12 = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(WP1 / "scripts"))

from ccx_utils import d1_from_ogden_mu1, run_ccx  # noqa: E402
from extract_pv_curve import extract_pv  # noqa: E402
from fit_hyperelastic import ExpPoint, dp_dv_local, fit_quality  # noqa: E402
from gen_sphere_shell_mesh import write_mesh  # noqa: E402
from write_deck import write_deck  # noqa: E402

P0_MMHG = 16.9
P0_PALLIKARIS_MMHG = 10.0  # basal do artigo Pallikaris et al. (2005)
KF_PER_UL = 0.0126
# Absolute pressure at end of FEA ramp [mmHg] (compat *DSLOAD* final value).
DP_FEA_FINAL = 50.0


@dataclass
class Geometry:
    R_mm: float
    t_mm: float
    source: str = "human_wp1.1"
    nu: float = 0.47
    E_mpa: float = 3.0


def pallikaris_pressure(
    v_uL: float,
    p0_user: float = P0_MMHG,
    kf: float = KF_PER_UL,
    p0_pallikaris: float = P0_PALLIKARIS_MMHG,
) -> float:
    """Re-anchored Pallikaris formula: article increment from P₀=10, on user basal."""
    dp_pallikaris = p0_pallikaris * (10.0 ** (kf * v_uL)) - p0_pallikaris
    return p0_user + dp_pallikaris


# Fig. 2 Pallikaris et al. (2005) — leitura visual, 79 olhos (claude-wp1_analysis)
V_PALLIKARIS_DIGIT = np.array(
    [0.0, 4.5, 9.0, 13.5, 17.5, 22.0, 26.5, 31.0, 35.5, 40.0, 44.5], dtype=float
)
P_PALLIKARIS_DIGIT = np.array(
    [10.0, 10.3, 15.5, 20.0, 23.0, 25.5, 28.5, 31.5, 35.0, 37.5, 41.5], dtype=float
)
V_MAX_PALLIKARIS_DIGIT = 44.5


def pallikaris_digitized_points(
    v_max: float = V_MAX_PALLIKARIS_DIGIT,
    p0_pallikaris: float = P0_PALLIKARIS_MMHG,
) -> list[ExpPoint]:
    """Digitized Pallikaris re-anchored: ΔP = P_artigo − 10, on user P₀=16.9."""
    rows: list[ExpPoint] = []
    for v, p_art in zip(V_PALLIKARIS_DIGIT, P_PALLIKARIS_DIGIT):
        if float(v) <= float(v_max) + 1e-9:
            rows.append(
                ExpPoint(V_uL=float(v), P_mmHg=float(p_art - p0_pallikaris))
            )
    return rows


def generate_pallikaris_csv(
    path: Path,
    v_max: float = V_MAX_PALLIKARIS_DIGIT,
    p0: float = P0_MMHG,
    use_delta_p: bool = True,
    **_ignored,
) -> list[ExpPoint]:
    """Build target from digitized Fig. 2 points (ΔP above user P₀)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = pallikaris_digitized_points(v_max=min(v_max, V_MAX_PALLIKARIS_DIGIT))
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["V_uL", "P_mmHg", "eye_id"])
        for row in rows:
            p_store = row.P_mmHg if use_delta_p else row.P_mmHg + p0
            w.writerow([f"{row.V_uL:.4f}", f"{p_store:.4f}", "pallikaris_digitized"])
    return rows


class PallikarisForward:
    def __init__(
        self,
        geom: Geometry,
        work_dir: Path,
        ne: int = 6,
        p_max_mmhg: float | None = None,
        n_load_steps: int = 16,
        p0_mmhg: float = P0_MMHG,
        dp_fea_final: float = DP_FEA_FINAL,
    ):
        self.geom = geom
        self.work_dir = work_dir
        self.ne = ne
        self.p0_mmhg = p0_mmhg
        self.dp_fea_final = float(dp_fea_final)
        self.p_max_mmhg = (
            float(p_max_mmhg) if p_max_mmhg is not None else self.dp_fea_final
        )
        self.n_load_steps = n_load_steps
        self.mesh_path = work_dir / "mesh.inp"
        work_dir.mkdir(parents=True, exist_ok=True)
        write_mesh(
            self.mesh_path,
            geom.R_mm,
            geom.t_mm,
            ne,
            2,
            label=f"pallikaris ne={ne}",
            bc_mode="symmetry_octant",
            mesh_kind="spherical",
            theta_min_deg=3.0,
            reduced=True,
        )

    def _p_targets(self) -> list[float]:
        return [
            self.p0_mmhg + (self.p_max_mmhg - self.p0_mmhg) * i / self.n_load_steps
            for i in range(1, self.n_load_steps + 1)
        ]

    def run(self, mu1: float, alpha1: float, tag: str = "run") -> tuple[np.ndarray, np.ndarray]:
        params = {
            "mu1_MPa": float(mu1),
            "alpha1": float(alpha1),
            "d1_tied_mu1": True,
            "D1": d1_from_ogden_mu1(mu1),
        }
        deck = self.work_dir / f"{tag}.inp"
        write_deck(
            deck,
            self.mesh_path.name,
            self.geom.t_mm,
            "ogden1",
            params,
            self._p_targets(),
            label=f"wp1.2 pallikaris {tag}",
            nu=self.geom.nu,
            E_mpa=self.geom.E_mpa,
            bc_mode="symmetry_octant",
            p0_mmhg=self.p0_mmhg,
        )

        frd = run_ccx(deck, clean=True)
        rows = extract_pv(deck, frd, self.geom.R_mm, p0_mmhg=self.p0_mmhg)
        v = np.array([r["dV_uL"] for r in rows], dtype=float)
        p = np.array([r["p_mmhg"] for r in rows], dtype=float)
        return v, p


def fit_ogden1(
    forward: PallikarisForward,
    exp: list[ExpPoint],
    max_nfev: int = 25,
) -> dict:
    v_exp = np.array([e.V_uL for e in exp])
    p_exp = np.array([e.P_mmHg for e in exp])
    x0 = np.array([2.14, 1.77])
    lo = np.array([0.05, 0.5])
    hi = np.array([15.0, 100.0])
    n_eval = {"n": 0}

    def residuals(x: np.ndarray) -> np.ndarray:
        n_eval["n"] += 1
        tag = f"opt_{n_eval['n']:03d}"
        v_fea, p_fea = forward.run(float(x[0]), float(x[1]), tag=tag)
        order = np.argsort(v_fea)
        v_fea, p_fea = v_fea[order], p_fea[order]
        if v_fea.max() < v_exp.max() * 0.9:
            return np.ones_like(p_exp) * 50.0
        # FEA absolute P → ΔP above P₀ (matches handoff CSV/residual convention)
        dp_fea = p_fea - forward.p0_mmhg
        dp_pred = np.interp(v_exp, v_fea, dp_fea)
        return dp_pred - p_exp

    t0 = time.time()
    res = least_squares(
        residuals,
        x0,
        bounds=(lo, hi),
        max_nfev=max_nfev,
        ftol=1e-8,
        xtol=1e-8,
        diff_step=0.02,
        x_scale="jac",
        verbose=2,
    )
    fit_time = time.time() - t0
    mu1, alpha1 = float(res.x[0]), float(res.x[1])
    v_fea, p_fea = forward.run(mu1, alpha1, tag="final")
    order = np.argsort(v_fea)
    v_fea, p_fea = v_fea[order], p_fea[order]
    dp_fea = p_fea - forward.p0_mmhg
    dp_at_exp = np.interp(v_exp, v_fea, dp_fea)
    quality = fit_quality(p_exp, dp_at_exp)

    return {
        "model": "ogden1",
        "params": {
            "mu1_MPa": mu1,
            "alpha1": alpha1,
            "D1": d1_from_ogden_mu1(mu1),
            "d1_tied_mu1": True,
        },
        "quality": quality,
        "optimizer": {
            "success": bool(res.success),
            "message": res.message,
            "nfev": int(res.nfev),
            "cost": float(res.cost),
            "fit_time_s": fit_time,
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
    ap.add_argument("--max-nfev", type=int, default=25)
    ap.add_argument(
        "--dp-fea-final",
        type=float,
        default=DP_FEA_FINAL,
        help="Absolute P at end of FEA ramp [mmHg] (default: %(default)s)",
    )
    ap.add_argument("--out", type=Path, default=WP12 / "output_octant")
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    csv_path = args.out / "pallikaris_synthetic.csv"
    exp = generate_pallikaris_csv(csv_path)

    geom = Geometry(R_mm=args.R, t_mm=args.t)
    work = args.out / "ccx_runs" / "ogden1"
    forward = PallikarisForward(
        geom, work, ne=args.ne, dp_fea_final=args.dp_fea_final
    )
    result = fit_ogden1(forward, exp, max_nfev=args.max_nfev)

    out = {
        "geometry": asdict(geom),
        "pallikaris": {"P0_mmHg": P0_MMHG, "Kf_per_uL": KF_PER_UL},
        "fea_ramp": {"P_final_mmHg_abs": args.dp_fea_final, "p_max_mmHg": forward.p_max_mmhg},
        "mesh": {"kind": "spherical", "ne": args.ne, "bc_mode": "symmetry_octant"},
        "selected": result,
    }
    (args.out / "fit_results.json").write_text(json.dumps(out, indent=2))

    q = result["quality"]
    lines = [
        "# wp1.2 — Ogden N=1 vs Pallikaris (spherical octant)\n",
        f"- **Geometry**: R={geom.R_mm} mm, t={geom.t_mm} mm",
        f"- **Pallikaris**: P₀={P0_MMHG} mmHg, Kf={KF_PER_UL} /µL",
        f"- **FEA ramp**: P_final={args.dp_fea_final} mmHg (abs, amplitude endpoint)",
        f"- **μ₁**: {result['params']['mu1_MPa']:.4f} MPa",
        f"- **α₁**: {result['params']['alpha1']:.4f}",
        f"- **D₁** (tied): {result['params']['D1']:.6f}",
        f"- **R²**: {q['R2']:.4f}",
        f"- **Max residual**: {q['max_residual_mmHg']:.2f} mmHg",
        f"- **Optimizer nfev**: {result['optimizer']['nfev']}",
        "",
    ]
    (args.out / "RESULTS.md").write_text("\n".join(lines))
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
