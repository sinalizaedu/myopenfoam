#!/usr/bin/env python3
"""WP1.4 corrigido — emulador GP com metadados consistentes e critério na cauda.

Corrige dois defeitos de cases/wp1.4/sweep_full/scripts/train_emulator.py:

  1. METADADOS DO PICKLE INCONSISTENTES. O original treinava com 10 colunas
     (6 continuas + 3 one-hot de cristalino + 1 de vitrectomia) mas gravava apenas
     os 6 nomes de `INPUT_COLS`, e a ordem do one-hot nao ficava registrada em
     lugar nenhum. Quem carregasse o emulador seguindo `input_cols` passaria 6
     colunas a um modelo que exige 10 — quebra, ou devolve numero errado em
     silencio. Aqui `input_cols` descreve exatamente a matriz de treino.

  2. CRITERIO AVALIADO NA MEDIA. O original marcava `passes_5pct_criterion` com
     `mean(rel) < 5`, e o emulador de V_max passava com erro MAXIMO de 5,96%.
     Aqui o criterio do plano (<5%) e avaliado no MAXIMO, e media/p95/maximo sao
     todos reportados.

Alem disso:
  - ACD, estado do cristalino e vitrectomia NAO entram como preditores, porque no
    modelo corrigido nao tem via mecanica (ver case_model_fixed). Entram na
    calculadora clinica por outras vias (ACD pelo WP5/Ensaio D; vitrectomia pelo
    R_ref no WP0, conforme a H4 do plano).
  - O dominio de treino e gravado no pickle, para que o consumidor (WP5/WP6)
    detecte extrapolacao em vez de confiar cegamente no GP.
  - As metricas sao reportadas tambem no subconjunto clinicamente plausivel,
    definido pela faixa de validacao do proprio plano (pico precoce de 30-36 mmHg
    apos 50 uL; Knecht et al. 2009, tratada pelo plano como faixa unica).

Uso no Docker:
    docker compose run --rm fsi bash -lc \
      'pip install numpy scikit-learn --break-system-packages && \
       cd /simulation/claude-wp1.4-fix/scripts && python3 train_emulator_fixed.py'
"""
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
    from sklearn.model_selection import KFold, cross_val_predict
    from sklearn.preprocessing import StandardScaler
except ImportError:
    raise SystemExit(
        "Instale no container: pip install scikit-learn --break-system-packages"
    )

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

# Preditores com via mecanica no modelo de casca (os unicos que afetam K e V).
INPUT_COLS = [
    "comprimento_axial_mm",
    "t_equatorial_mm",
    "t_posterior_mm",
    "mu1_factor",
    "alpha1_factor",
]

TARGETS = {
    "K_basal_first_mmHg_per_uL": "mmHg/uL",
    "V_max_uL": "uL",
    "dIOP_at_50uL_mmHg": "mmHg",
}

# Faixa de validacao clinica do plano de tese (Knecht et al. 2009, Retina
# 29:1175-81): pico precoce pos-injecao de 0,05 mL entre ~30 e ~36 mmHg,
# tratado pelo plano como faixa unica (a diferenca entre tecnicas nao foi
# estatisticamente significativa).
PEAK_BAND_MMHG = (30.0, 36.0)
P0_MMHG = 16.9


def load_xy(path: Path, target: str) -> tuple[np.ndarray, np.ndarray, list[dict]]:
    data = json.loads(path.read_text())
    ok = [
        r
        for r in data
        if r.get("status") == "OK" and r.get(target) is not None
    ]
    X = np.array([[float(r[c]) for c in INPUT_COLS] for r in ok], dtype=float)
    y = np.array([float(r[target]) for r in ok], dtype=float)
    return X, y, ok


def train_gp(X: np.ndarray, y: np.ndarray, cv_folds: int, seed: int = 42) -> dict:
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    kernel = (
        ConstantKernel(1.0, (1e-4, 1e5))
        * Matern(
            length_scale=np.ones(X.shape[1]),
            length_scale_bounds=(1e-3, 1e6),
            nu=2.5,
        )
        + WhiteKernel(noise_level=1e-4, noise_level_bounds=(1e-12, 1e2))
    )
    gp = GaussianProcessRegressor(
        kernel=kernel,
        n_restarts_optimizer=12,
        normalize_y=True,
        random_state=seed,
    )
    # KFold explicito com shuffle: o original usava cv=5 sem shuffle, o que depende
    # da ordem das linhas do CSV.
    cv = KFold(n_splits=cv_folds, shuffle=True, random_state=seed)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        y_pred = cross_val_predict(gp, Xs, y, cv=cv)
        gp.fit(Xs, y)
    return {"model": gp, "scaler": scaler, "y_pred_cv": y_pred}


def metrics(y: np.ndarray, y_pred: np.ndarray, mask: np.ndarray | None = None) -> dict:
    if mask is not None:
        y, y_pred = y[mask], y_pred[mask]
    if len(y) == 0:
        return {"n": 0}
    rel = np.abs(y_pred - y) / np.maximum(np.abs(y), 1e-12) * 100.0
    ss_res = float(np.sum((y - y_pred) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    return {
        "n": int(len(y)),
        "R2_cv": round(1.0 - ss_res / ss_tot, 6) if ss_tot > 0 else None,
        "rel_err_mean_pct": round(float(np.mean(rel)), 3),
        "rel_err_p95_pct": round(float(np.percentile(rel, 95)), 3),
        "rel_err_max_pct": round(float(np.max(rel)), 3),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--results", type=Path, default=ROOT / "output_sweep_fixed" / "sweep_results_fixed.json"
    )
    ap.add_argument("--out", type=Path, default=ROOT / "output_emulator_fixed")
    ap.add_argument("--cv-folds", type=int, default=5)
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    report: dict = {
        "criterion": "erro relativo MAXIMO de validacao cruzada < 5% (plano, WP1.4)",
        "predictors": INPUT_COLS,
        "excluded_predictors": {
            "ACD_mm": "sem via mecanica na casca de uma camada (ver case_model_fixed)",
            "lens_status": "sem via mecanica na casca de uma camada",
            "vitrectomy": "sem via mecanica; entra em R_ref no WP0 (H4 do plano)",
        },
        "clinical_band_source": (
            "Knecht et al. 2009 (Retina 29:1175-81), pico precoce 30-36 mmHg "
            "apos 50 uL, tratado como faixa unica pelo plano de tese"
        ),
        "targets": {},
    }

    for target, unit in TARGETS.items():
        X, y, rows = load_xy(args.results, target)
        if len(y) < 20:
            print(f"{target}: apenas {len(y)} casos, pulando")
            continue
        res = train_gp(X, y, args.cv_folds)
        y_pred = res["y_pred_cv"]

        # subconjunto clinicamente plausivel: pico = P0 + dIOP@50uL dentro da faixa
        peak = np.array(
            [
                (P0_MMHG + r["dIOP_at_50uL_mmHg"])
                if r.get("dIOP_at_50uL_mmHg") is not None
                else np.nan
                for r in rows
            ],
            dtype=float,
        )
        plausible = (peak >= PEAK_BAND_MMHG[0]) & (peak <= PEAK_BAND_MMHG[1])

        m_all = metrics(y, y_pred)
        m_plaus = metrics(y, y_pred, plausible)
        entry = {
            "unit": unit,
            "all_cases": m_all,
            "clinically_plausible_subset": m_plaus,
            "passes_max_5pct": bool(m_all["rel_err_max_pct"] < 5.0),
            "passes_mean_5pct": bool(m_all["rel_err_mean_pct"] < 5.0),
            "training_domain": {
                c: [float(X[:, j].min()), float(X[:, j].max())]
                for j, c in enumerate(INPUT_COLS)
            },
        }
        report["targets"][target] = entry

        with open(args.out / f"emulator_{target}.pkl", "wb") as fh:
            pickle.dump(
                {
                    "model": res["model"],
                    "scaler": res["scaler"],
                    # descreve EXATAMENTE a matriz de treino, nesta ordem:
                    "input_cols": list(INPUT_COLS),
                    "n_features": len(INPUT_COLS),
                    "target": target,
                    "target_unit": unit,
                    "training_domain": entry["training_domain"],
                    "usage": (
                        "X = np.array([[<"
                        + ">, <".join(INPUT_COLS)
                        + ">]]); y = model.predict(scaler.transform(X)). "
                        "Checar training_domain antes de confiar: fora dele o GP extrapola."
                    ),
                },
                fh,
            )
        print(
            f"{target}: media {m_all['rel_err_mean_pct']}%  "
            f"p95 {m_all['rel_err_p95_pct']}%  max {m_all['rel_err_max_pct']}%  "
            f"-> criterio(max<5%) {'PASS' if entry['passes_max_5pct'] else 'FAIL'}"
        )

    (args.out / "emulator_report_fixed.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False)
    )
    print(f"\nRelatorio: {args.out / 'emulator_report_fixed.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
