#!/usr/bin/env python3
"""GP emulators for sweep_full (Matérn 5/2, widened kernel bounds)."""
from __future__ import annotations

import argparse
import json
import pickle
import warnings
from pathlib import Path

import numpy as np

try:
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import ConstantKernel, Matern, WhiteKernel
    from sklearn.model_selection import cross_val_predict, cross_val_score
    from sklearn.preprocessing import StandardScaler
except ImportError:
    raise SystemExit("Install scikit-learn in the container: pip install scikit-learn --break-system-packages")

HERE = Path(__file__).resolve().parent
SWEEP = HERE.parent

INPUT_COLS = [
    "comprimento_axial_mm",
    "t_equatorial_mm",
    "t_posterior_mm",
    "mu1_factor",
    "alpha1_factor",
    "ACD_mm",
]
TARGETS = ["V_max_uL", "K_eff_mmHg_per_uL"]


def load_xy(path: Path) -> tuple[np.ndarray, np.ndarray]:
    data = json.loads(path.read_text())
    ok = [r for r in data if r.get("status") == "OK"]
    n = len(ok)
    X = np.zeros((n, len(INPUT_COLS) + 4))
    for i, row in enumerate(ok):
        for j, col in enumerate(INPUT_COLS):
            X[i, j] = float(row[col])
        lens = str(row.get("lens_status", "phakic"))
        lm = {"phakic": [1, 0, 0], "pseudophakic": [0, 1, 0], "aphakic": [0, 0, 1]}.get(
            lens, [1, 0, 0]
        )
        X[i, len(INPUT_COLS) : len(INPUT_COLS) + 3] = lm
        vit = row.get("vitrectomy") in (True, "True", "true")
        X[i, -1] = 1.0 if vit else 0.0
    Y = np.zeros((n, 2))
    for i, row in enumerate(ok):
        Y[i, 0] = float(row["V_max_uL"])
        k = row.get("K_eff_mmHg_per_uL")
        Y[i, 1] = float(k) if k is not None else np.nan
    return X, Y


def train_gp(X: np.ndarray, y: np.ndarray, cv_folds: int) -> dict:
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    kernel = (
        ConstantKernel(1.0, (1e-4, 1e5))
        * Matern(length_scale=np.ones(X.shape[1]), length_scale_bounds=(1e-3, 1e6), nu=2.5)
        + WhiteKernel(noise_level=1e-4, noise_level_bounds=(1e-12, 1e2))
    )
    gp = GaussianProcessRegressor(
        kernel=kernel,
        n_restarts_optimizer=12,
        normalize_y=True,
        random_state=42,
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        scores = cross_val_score(gp, Xs, y, cv=cv_folds, scoring="r2")
        y_pred = cross_val_predict(gp, Xs, y, cv=cv_folds)
    rel = np.abs(y_pred - y) / np.maximum(np.abs(y), 1e-9) * 100.0
    gp.fit(Xs, y)
    return {
        "model": gp,
        "scaler": scaler,
        "metrics": {
            "R2_cv_mean": round(float(np.mean(scores)), 4),
            "R2_cv_std": round(float(np.std(scores)), 4),
            "mean_relative_error_pct": round(float(np.mean(rel)), 2),
            "max_relative_error_pct": round(float(np.max(rel)), 2),
            "cv_folds": cv_folds,
            "n_samples": len(y),
            "passes_5pct_criterion": float(np.mean(rel)) < 5.0,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path, default=SWEEP / "output_sweep" / "sweep_results.json")
    ap.add_argument("--out", type=Path, default=SWEEP / "output_emulator")
    ap.add_argument("--cv-folds", type=int, default=5)
    args = ap.parse_args()

    X, Y = load_xy(args.results)
    args.out.mkdir(parents=True, exist_ok=True)
    report = {}
    for ti, name in enumerate(TARGETS):
        mask = ~np.isnan(Y[:, ti])
        res = train_gp(X[mask], Y[mask, ti], args.cv_folds)
        report[name] = res["metrics"]
        pkl = args.out / f"emulator_{name}.pkl"
        with open(pkl, "wb") as fh:
            pickle.dump(
                {"model": res["model"], "scaler": res["scaler"], "input_cols": INPUT_COLS, "target": name},
                fh,
            )
        print(f"{name}: CV err {res['metrics']['mean_relative_error_pct']}%")
    (args.out / "emulator_report.json").write_text(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
