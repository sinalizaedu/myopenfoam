#!/usr/bin/env python3
"""WP1.4 — Treina emulador GP (processo gaussiano) sobre os resultados da varredura.

Lê sweep_results.json e treina um GP para prever V_max e K_eff
a partir dos parâmetros de entrada.

Critério de aceitação: erro de validação cruzada (LOO ou k-fold) < 5%.

Saída:
  - emulator_report.json — métricas de validação cruzada
  - emulator_model.pkl   — modelo treinado (para uso no WP6)

Uso:
    python3 train_emulator_claude.py
    python3 train_emulator_claude.py --results output_sweep_claude/sweep_results.json
    python3 train_emulator_claude.py --cv-folds 10
"""
from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path

import numpy as np

try:
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import Matern, ConstantKernel, WhiteKernel
    from sklearn.model_selection import cross_val_score, LeaveOneOut
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    print("AVISO: scikit-learn não instalado. Instale com: pip install scikit-learn")
    print("       pip install scikit-learn --break-system-packages  (no container)")

HERE = Path(__file__).resolve().parent

# Colunas de entrada para o emulador
INPUT_COLS = [
    "comprimento_axial_mm",
    "t_equatorial_mm",
    "t_posterior_mm",
    "mu1_factor",
    "alpha1_factor",
    "ACD_mm",
    # lens_status e vitrectomy são codificados separadamente
]

# Alvos
TARGET_COLS = ["V_max_uL", "K_eff_mmHg_per_uL"]


def load_data(path: Path) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Carrega e prepara os dados da varredura.

    Returns:
        X: array (n, d) de features
        Y: array (n, 2) de targets [V_max, K_eff]
        case_ids: lista de IDs
    """
    data = json.loads(path.read_text())
    ok = [r for r in data if r.get("status") == "OK"]
    if not ok:
        raise ValueError("Nenhum caso com status OK encontrado")

    n = len(ok)
    print(f"Carregados {n} casos OK de {len(data)} total")

    # Features contínuas
    X_cont = np.zeros((n, len(INPUT_COLS)))
    for i, row in enumerate(ok):
        for j, col in enumerate(INPUT_COLS):
            X_cont[i, j] = float(row[col])

    # Features categóricas → one-hot
    lens_map = {"phakic": [1, 0, 0], "pseudophakic": [0, 1, 0], "aphakic": [0, 0, 1]}
    X_lens = np.array([lens_map.get(r.get("lens_status", "phakic"), [1, 0, 0]) for r in ok])
    X_vitr = np.array([[1.0 if r.get("vitrectomy") in (True, "True", "true") else 0.0] for r in ok])

    X = np.hstack([X_cont, X_lens, X_vitr])

    # Targets
    Y = np.zeros((n, len(TARGET_COLS)))
    for i, row in enumerate(ok):
        Y[i, 0] = float(row["V_max_uL"])
        k_eff = row.get("K_eff_mmHg_per_uL")
        Y[i, 1] = float(k_eff) if k_eff is not None else np.nan

    case_ids = [r["case_id"] for r in ok]
    return X, Y, case_ids


def train_gp(X: np.ndarray, y: np.ndarray, cv_folds: int = 5) -> dict:
    """Treina GP com kernel Matérn e avalia por validação cruzada."""
    if not HAS_SKLEARN:
        raise ImportError("scikit-learn necessário")

    # Escalar features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Kernel: Matérn 5/2 é uma boa escolha padrão para dados físicos
    kernel = (
        ConstantKernel(1.0, (1e-3, 1e3))
        * Matern(length_scale=np.ones(X.shape[1]), nu=2.5)
        + WhiteKernel(noise_level=1e-5, noise_level_bounds=(1e-10, 1e1))
    )

    gp = GaussianProcessRegressor(
        kernel=kernel,
        n_restarts_optimizer=10,
        normalize_y=True,
        random_state=42,
    )

    # Validação cruzada
    # Métrica: R² (sklearn default para regressão)
    if cv_folds == -1:
        # Leave-One-Out (mais preciso, mais lento)
        cv = LeaveOneOut()
        scores = cross_val_score(gp, X_scaled, y, cv=cv, scoring="r2")
    else:
        scores = cross_val_score(gp, X_scaled, y, cv=cv_folds, scoring="r2")

    r2_mean = float(np.mean(scores))
    r2_std = float(np.std(scores))

    # Erro relativo médio via CV
    if cv_folds == -1:
        cv = LeaveOneOut()
    from sklearn.model_selection import cross_val_predict
    y_pred = cross_val_predict(gp, X_scaled, y, cv=cv_folds if cv_folds != -1 else LeaveOneOut())
    rel_errors = np.abs(y_pred - y) / np.abs(y) * 100
    mean_rel_error = float(np.mean(rel_errors))
    max_rel_error = float(np.max(rel_errors))

    # Treinar modelo final (em todos os dados)
    gp.fit(X_scaled, y)

    return {
        "model": gp,
        "scaler": scaler,
        "metrics": {
            "R2_cv_mean": round(r2_mean, 4),
            "R2_cv_std": round(r2_std, 4),
            "mean_relative_error_pct": round(mean_rel_error, 2),
            "max_relative_error_pct": round(max_rel_error, 2),
            "cv_folds": cv_folds,
            "n_samples": len(y),
            "passes_5pct_criterion": mean_rel_error < 5.0,
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", type=Path,
                    default=HERE.parent / "output_sweep_claude" / "sweep_results.json")
    ap.add_argument("--out", type=Path, default=HERE.parent / "output_emulator_claude")
    ap.add_argument("--cv-folds", type=int, default=5,
                    help="Número de folds para CV (-1 = LOO)")
    args = ap.parse_args()

    if not HAS_SKLEARN:
        print("Instale scikit-learn antes de rodar este script.")
        print("  pip install scikit-learn --break-system-packages")
        raise SystemExit(1)

    X, Y, case_ids = load_data(args.results)
    args.out.mkdir(parents=True, exist_ok=True)

    report = {}
    for t_idx, target_name in enumerate(TARGET_COLS):
        # Filtrar NaN
        mask = ~np.isnan(Y[:, t_idx])
        X_t = X[mask]
        y_t = Y[mask, t_idx]

        if len(y_t) < 10:
            print(f"  {target_name}: poucos dados ({len(y_t)}), pulando")
            continue

        print(f"\nTreinando emulador para {target_name} ({len(y_t)} amostras)...")
        result = train_gp(X_t, y_t, cv_folds=args.cv_folds)

        m = result["metrics"]
        print(f"  R² CV = {m['R2_cv_mean']:.4f} ± {m['R2_cv_std']:.4f}")
        print(f"  Erro relativo médio = {m['mean_relative_error_pct']:.2f}%")
        print(f"  Erro relativo máximo = {m['max_relative_error_pct']:.2f}%")
        criterion = "PASSA" if m["passes_5pct_criterion"] else "FALHA"
        print(f"  Critério <5%: {criterion}")

        report[target_name] = m

        # Salvar modelo
        model_path = args.out / f"emulator_{target_name}.pkl"
        with open(model_path, "wb") as fh:
            pickle.dump({
                "model": result["model"],
                "scaler": result["scaler"],
                "input_cols": INPUT_COLS,
                "target": target_name,
            }, fh)
        print(f"  Modelo salvo: {model_path}")

    # Relatório
    report_path = args.out / "emulator_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nRelatório: {report_path}")

    # Verificar critério global
    all_pass = all(m.get("passes_5pct_criterion", False) for m in report.values())
    if all_pass:
        print("\n*** TODOS os emuladores passam no critério de <5% ***")
    else:
        print("\n*** ATENÇÃO: nem todos os emuladores passam no critério de <5% ***")
        print("    Considere aumentar o número de amostras ou revisar o espaço paramétrico.")


if __name__ == "__main__":
    main()
