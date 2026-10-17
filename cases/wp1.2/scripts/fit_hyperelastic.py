#!/usr/bin/env python3
"""Inverse FEA: fit Yeoh/Ogden hyperelastic params to experimental P(V).

Uses CalculiX spherical shell (wp1.1 mesh) with NLGEOM multi-step inflation.
Minimizes sum of squared pressure residuals at experimental volume points.

Example:
    python3 fit_hyperelastic.py \\
        --data ../data/ensaio_A.csv \\
        --eye-id pig01 \\
        --R 9.0 --t 0.45 \\
        --out ../output_wp1.2
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import least_squares

HERE = Path(__file__).resolve().parent
WP1 = HERE.parents[1] / "wp1.1"
WP12 = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(WP1 / "scripts"))

from ccx_utils import run_ccx  # noqa: E402
from extract_pv_curve import extract_pv  # noqa: E402
from gen_sphere_shell_mesh import write_mesh  # noqa: E402
from write_deck import write_deck  # noqa: E402

P0_MMHG = 15.0
R2_GOOD = 0.98


@dataclass
class Geometry:
    R_mm: float
    t_mm: float
    source: str
    nu: float = 0.47
    E_mpa: float = 3.0


@dataclass
class ExpPoint:
    V_uL: float
    P_mmHg: float


def load_experimental_csv(path: Path, eye_id: str | None) -> list[ExpPoint]:
    rows: list[ExpPoint] = []
    with open(path, newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise ValueError(f"No header in {path}")
        fields = {f.lower().strip(): f for f in reader.fieldnames}
        v_key = fields.get("v_ul") or fields.get("v") or fields.get("dv_ul")
        p_key = fields.get("p_mmhg") or fields.get("p")
        eye_key = fields.get("eye_id") or fields.get("eye")
        if not v_key or not p_key:
            raise ValueError(f"CSV needs V_uL and P_mmHg columns; got {reader.fieldnames}")
        for row in reader:
            if eye_id and eye_key and row.get(eye_key, "").strip() != eye_id:
                continue
            v = float(row[v_key])
            p = float(row[p_key])
            if p >= P0_MMHG - 1e-6 and v >= -1e-6:
                rows.append(ExpPoint(V_uL=v, P_mmHg=p))
    rows.sort(key=lambda r: r.V_uL)
    if len(rows) < 3:
        raise ValueError(f"Need >=3 loading points in {path}")
    return rows


def fit_quality(p_exp: np.ndarray, p_mod: np.ndarray) -> dict:
    resid = p_mod - p_exp
    ss_res = float(np.sum(resid**2))
    ss_tot = float(np.sum((p_exp - np.mean(p_exp)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return {
        "R2": r2,
        "max_residual_mmHg": float(np.max(np.abs(resid))),
        "rmse_mmHg": float(np.sqrt(np.mean(resid**2))),
        "ss_res": ss_res,
    }


def dp_dv_local(v: np.ndarray, p: np.ndarray, v_query: float) -> float:
    """Central difference dP/dV [mmHg/µL] on monotone P(V) branch."""
    order = np.argsort(v)
    v, p = v[order], p[order]
    f = interp1d(v, p, kind="linear", fill_value="extrapolate")
    dv = max(0.5, 0.02 * (v.max() - v.min() + 1e-9))
    v_lo = max(v.min(), v_query - dv)
    v_hi = min(v.max(), v_query + dv)
    if v_hi <= v_lo:
        v_lo, v_hi = v_query - 0.5, v_query + 0.5
    return float((f(v_hi) - f(v_lo)) / (v_hi - v_lo))


class FEAForward:
    """Run CalculiX forward model for a given hyperelastic parameter set."""

    def __init__(
        self,
        geom: Geometry,
        work_dir: Path,
        model: str,
        ne: int = 6,
        n_load_steps: int = 16,
        p_max_mmhg: float = 60.0,
        bc_mode: str = "symmetry_octant",
    ):
        self.geom = geom
        self.work_dir = work_dir
        self.model = model
        self.ne = ne
        self.n_load_steps = n_load_steps
        self.p_max_mmhg = p_max_mmhg
        self.bc_mode = bc_mode
        self.mesh_path = work_dir / "mesh.inp"
        self._ensure_mesh()

    def _ensure_mesh(self) -> None:
        meta_path = self.mesh_path.with_suffix(".meta.json")
        if self.mesh_path.is_file() and meta_path.is_file():
            meta = json.loads(meta_path.read_text())
            if meta.get("bc_mode") == self.bc_mode and meta.get("ne_per_face") == self.ne:
                return
        write_mesh(
            self.mesh_path,
            self.geom.R_mm,
            self.geom.t_mm,
            self.ne,
            2,
            label=f"swine ne{self.ne}",
            bc_mode=self.bc_mode,
        )

    def _p_targets(self) -> list[float]:
        return [
            P0_MMHG + (self.p_max_mmhg - P0_MMHG) * i / self.n_load_steps
            for i in range(1, self.n_load_steps + 1)
        ]

    def run(self, param_vec: np.ndarray, tag: str = "run") -> tuple[np.ndarray, np.ndarray]:
        params = self._vec_to_params(param_vec)
        deck = self.work_dir / f"{tag}.inp"
        meta = write_deck(
            deck,
            self.mesh_path.name,
            self.geom.t_mm,
            self.model,
            params,
            self._p_targets(),
            label=f"wp1.2 {self.model} {tag}",
            nu=self.geom.nu,
            E_mpa=self.geom.E_mpa,
        )
        frd = run_ccx(deck, clean=True)
        rows = extract_pv(deck, frd, self.geom.R_mm)
        v = np.array([r["dV_uL"] for r in rows], dtype=float)
        p = np.array([r["p_mmhg"] for r in rows], dtype=float)
        return v, p

    def _vec_to_params(self, x: np.ndarray) -> dict:
        if self.model == "yeoh2":
            return {"C10_MPa": float(x[0]), "C20_MPa": float(x[1])}
        if self.model == "yeoh3":
            return {"C10_MPa": float(x[0]), "C20_MPa": float(x[1]), "C30_MPa": float(x[2])}
        if self.model == "ogden1":
            return {"mu1_MPa": float(x[0]), "alpha1": float(x[1])}
        if self.model == "ogden2":
            return {
                "mu1_MPa": float(x[0]),
                "alpha1": float(x[1]),
                "mu2_MPa": float(x[2]),
                "alpha2": float(x[3]),
            }
        raise ValueError(self.model)

    def x0_bounds(self) -> tuple[np.ndarray, tuple, tuple]:
        if self.model == "yeoh2":
            return np.array([0.5, 0.05]), (1e-4, -5.0), (5.0, 5.0)
        if self.model == "yeoh3":
            return np.array([0.5, 0.05, 0.001]), (1e-4, -5.0, -1.0), (5.0, 5.0, 1.0)
        if self.model == "ogden1":
            return np.array([0.5, 2.0]), (1e-4, 0.5), (5.0, 6.0)
        if self.model == "ogden2":
            return np.array([0.4, 2.0, 0.05, -2.0]), (1e-4, 0.5, 1e-4, -6.0), (5.0, 6.0, 2.0, -0.5)
        raise ValueError(self.model)


def fit_model(
    forward: FEAForward,
    exp: list[ExpPoint],
    max_nfev: int = 12,
) -> dict:
    v_exp = np.array([e.V_uL for e in exp])
    p_exp = np.array([e.P_mmHg for e in exp])
    x0, lo, hi = forward.x0_bounds()
    n_eval = {"n": 0}

    def residuals(x: np.ndarray) -> np.ndarray:
        n_eval["n"] += 1
        tag = f"opt_{forward.model}_{n_eval['n']:03d}"
        v_fea, p_fea = forward.run(x, tag=tag)
        order = np.argsort(v_fea)
        v_fea, p_fea = v_fea[order], p_fea[order]
        if v_fea.max() < v_exp.max() * 0.95:
            # penalize if FEA does not reach experimental volume range
            return np.ones_like(p_exp) * 50.0
        p_pred = np.interp(v_exp, v_fea, p_fea)
        return p_pred - p_exp

    t0 = time.time()
    res = least_squares(
        residuals,
        x0,
        bounds=(lo, hi),
        max_nfev=max_nfev,
        verbose=2,
    )
    fit_time = time.time() - t0
    params = forward._vec_to_params(res.x)
    v_fea, p_fea = forward.run(res.x, tag="final")
    order = np.argsort(v_fea)
    v_fea, p_fea = v_fea[order], p_fea[order]
    p_at_exp = np.interp(v_exp, v_fea, p_fea)
    quality = fit_quality(p_exp, p_at_exp)
    v_peak = float(v_exp.max())
    return {
        "model": forward.model,
        "params": params,
        "params_vec": res.x.tolist(),
        "quality": quality,
        "optimizer": {
            "success": bool(res.success),
            "message": res.message,
            "nfev": int(res.nfev),
            "cost": float(res.cost),
            "fit_time_s": fit_time,
        },
        "dP_dV_at_V0_mmHg_per_uL": dp_dv_local(v_fea, p_fea, 0.0),
        "dP_dV_at_peak_mmHg_per_uL": dp_dv_local(v_fea, p_fea, v_peak),
        "fea_curve": [{"V_uL": float(v), "P_mmHg": float(p)} for v, p in zip(v_fea, p_fea)],
        "exp_at_fit": [
            {"V_uL": float(v), "P_exp_mmHg": float(pe), "P_fea_mmHg": float(pm)}
            for v, pe, pm in zip(v_exp, p_exp, p_at_exp)
        ],
    }


def select_model(
    geom: Geometry,
    exp: list[ExpPoint],
    work_dir: Path,
    p_max: float,
    ne: int,
    max_nfev: int,
    bc_mode: str = "symmetry_octant",
) -> dict:
    """Try Yeoh-2 first; escalate only if R² < 0.98."""
    chain = ["yeoh2", "yeoh3", "ogden1", "ogden2"]
    best: dict | None = None
    tried: list[dict] = []

    for model in chain:
        print(f"\n=== Trying {model} ===")
        fwd = FEAForward(
            geom,
            work_dir / model,
            model,
            ne=ne,
            p_max_mmhg=p_max,
            bc_mode=bc_mode,
        )
        result = fit_model(fwd, exp, max_nfev=max_nfev)
        tried.append(result)
        r2 = result["quality"]["R2"]
        print(f"  R²={r2:.4f}  max|resid|={result['quality']['max_residual_mmHg']:.2f} mmHg")
        if best is None or r2 > best["quality"]["R2"]:
            best = result
        if r2 >= R2_GOOD:
            best = result
            break

    assert best is not None
    return {"selected": best, "all_models": tried}


def write_overlay_csv(path: Path, result: dict) -> None:
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["V_uL", "P_exp_mmHg", "P_fea_mmHg"])
        for row in result["exp_at_fit"]:
            w.writerow([row["V_uL"], row["P_exp_mmHg"], row["P_fea_mmHg"]])
        w.writerow([])
        w.writerow(["# dense FEA curve"])
        w.writerow(["V_uL", "P_fea_mmHg"])
        for row in result["fea_curve"]:
            w.writerow([row["V_uL"], row["P_mmHg"]])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", type=Path, required=True, help="Experimental CSV (loading branch)")
    ap.add_argument("--eye-id", default="", help="Filter column eye_id if multi-eye file")
    ap.add_argument("--R", type=float, required=True, help="Equivalent radius [mm]")
    ap.add_argument("--t", type=float, required=True, help="Scleral thickness [mm]")
    ap.add_argument("--geom-source", default="user", help="Provenance string for R,t")
    ap.add_argument("--out", type=Path, default=WP12 / "output_wp1.2")
    ap.add_argument("--p-max", type=float, default=60.0)
    ap.add_argument("--ne", type=int, default=6, help="Mesh ne/face (6=fast, 12=verify)")
    ap.add_argument("--max-nfev", type=int, default=10, help="Max FEA evals per model")
    ap.add_argument(
        "--bc-mode",
        default="symmetry_octant",
        choices=["symmetry_octant", "pins"],
        help="BC strategy: symmetry octant (NLGEOM) or 3-node pins (linear wp1.1)",
    )
    ap.add_argument("--model", default="", help="Force model (yeoh2/yeoh3/ogden1/ogden2)")
    args = ap.parse_args()

    exp = load_experimental_csv(args.data, args.eye_id or None)
    p_max = max(args.p_max, max(e.P_mmHg for e in exp))
    geom = Geometry(R_mm=args.R, t_mm=args.t, source=args.geom_source)
    args.out.mkdir(parents=True, exist_ok=True)
    work = args.out / "ccx_runs"
    work.mkdir(parents=True, exist_ok=True)

    if args.model:
        fwd = FEAForward(
            geom,
            work / args.model,
            args.model,
            ne=args.ne,
            p_max_mmhg=p_max,
            bc_mode=args.bc_mode,
        )
        selected = fit_model(fwd, exp, max_nfev=args.max_nfev)
        out = {
            "geometry": asdict(geom),
            "experimental_points": len(exp),
            "bc_mode": args.bc_mode,
            "selected": selected,
        }
    else:
        out = {
            "geometry": asdict(geom),
            "experimental_points": len(exp),
            "bc_mode": args.bc_mode,
            **select_model(geom, exp, work, p_max, args.ne, args.max_nfev, args.bc_mode),
        }

    sel = out["selected"]
    (args.out / "fit_results.json").write_text(json.dumps(out, indent=2))
    write_overlay_csv(args.out / "pv_overlay.csv", sel)

    # human-readable summary
    lines = [
        "# wp1.2 — hyperelastic inverse FEA fit\n",
        f"- **Geometry**: R={geom.R_mm} mm, t={geom.t_mm} mm ({geom.source})",
        f"- **Model selected**: {sel['model']}",
        f"- **Parameters**: {json.dumps(sel['params'])}",
        f"- **R²**: {sel['quality']['R2']:.4f}",
        f"- **Max residual**: {sel['quality']['max_residual_mmHg']:.2f} mmHg",
        f"- **dP/dV @ V=0**: {sel['dP_dV_at_V0_mmHg_per_uL']:.4f} mmHg/µL",
        f"- **dP/dV @ peak**: {sel['dP_dV_at_peak_mmHg_per_uL']:.4f} mmHg/µL",
        "",
    ]
    (args.out / "RESULTS.md").write_text("\n".join(lines))
    print("\n" + "\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
