#!/usr/bin/env python3
"""WP1.4 — Gera amostras por hipercubo latino para a varredura paramétrica.

Espaço de parâmetros (7 variáveis, conforme plano de tese):
  Contínuas:
    1. comprimento_axial_mm  : 20–30 mm
    2. t_equatorial_mm       : 0.3–0.8 mm
    3. t_posterior_mm         : 0.6–1.2 mm
    4. mu1_factor             : 0.5–1.5 (fator multiplicativo sobre mu1 nominal, ±2 SD)
    5. alpha1_factor          : 0.5–1.5 (idem para alpha1)
    6. ACD_mm                 : 2.0–4.5 mm (profundidade da câmara anterior)
  Categóricas:
    7. lens_status            : phakic / pseudophakic / aphakic
    8. vitrectomy             : sim / não

Saída: CSV com N_SAMPLES linhas + JSON com metadados.

Uso:
    python3 generate_lhs_samples.py --n 300 --out sweep_samples.csv
    python3 generate_lhs_samples.py --n 300 --seed 42 --out sweep_samples.csv
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np


# ---------- parâmetros nominais do fit Ogden (Friedenwald, WP1.2) ----------
MU1_NOMINAL = 2.2708230587169704   # MPa
ALPHA1_NOMINAL = 1.05617628707085

# ---------- faixas contínuas ----------
BOUNDS = {
    "comprimento_axial_mm": (20.0, 30.0),
    "t_equatorial_mm":      (0.3,  0.8),
    "t_posterior_mm":        (0.6,  1.2),
    "mu1_factor":            (0.5,  1.5),   # ±~2 SD (conservador)
    "alpha1_factor":         (0.5,  1.5),
    "ACD_mm":                (2.0,  4.5),
}
CONTINUOUS_KEYS = list(BOUNDS.keys())
N_CONTINUOUS = len(CONTINUOUS_KEYS)

# ---------- variáveis categóricas ----------
LENS_OPTIONS = ["phakic", "pseudophakic", "aphakic"]
VITRECTOMY_OPTIONS = [False, True]


def latin_hypercube(n: int, d: int, rng: np.random.Generator) -> np.ndarray:
    """Gera hipercubo latino normalizado [0,1]^d com n amostras."""
    result = np.zeros((n, d))
    for j in range(d):
        perm = rng.permutation(n)
        result[:, j] = (perm + rng.uniform(size=n)) / n
    return result


def scale_samples(lhs_01: np.ndarray) -> np.ndarray:
    """Escala de [0,1] para as faixas reais."""
    scaled = np.zeros_like(lhs_01)
    for j, key in enumerate(CONTINUOUS_KEYS):
        lo, hi = BOUNDS[key]
        scaled[:, j] = lo + (hi - lo) * lhs_01[:, j]
    return scaled


def assign_categorical(n: int, rng: np.random.Generator) -> tuple[list[str], list[bool]]:
    """Atribui variáveis categóricas com distribuição uniforme."""
    lens = [LENS_OPTIONS[i % len(LENS_OPTIONS)] for i in rng.permutation(n)]
    vitr = [VITRECTOMY_OPTIONS[i % len(VITRECTOMY_OPTIONS)] for i in rng.permutation(n)]
    return list(lens), list(vitr)


def derived_geometry(row: dict) -> dict:
    """Calcula geometria derivada para a simulação.

    Para o modelo de casca esférica atual, mapeia:
      - comprimento_axial → R_mm (raio médio ≈ AL/2)
      - t_equatorial como espessura principal da casca

    Quando o mesh generator suportar elipsoide ou espessura variável,
    expandir esta função.
    """
    al = row["comprimento_axial_mm"]
    R_mm = al / 2.0
    t_eq = float(row["t_equatorial_mm"])
    t_post = float(row["t_posterior_mm"])
    # Espessura efetiva para malha uniforme: mistura equatorial/posterior
    # (posterior mais espesso → peso maior no polo; evita ignorar t_posterior_mm)
    t_mm = 0.55 * t_eq + 0.45 * t_post
    # Material absoluto
    mu1_MPa = MU1_NOMINAL * row["mu1_factor"]
    alpha1 = ALPHA1_NOMINAL * row["alpha1_factor"]
    return {
        "R_mm": round(R_mm, 2),
        "t_mm": round(t_mm, 3),
        "mu1_MPa": mu1_MPa,
        "alpha1": alpha1,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, default=300, help="Número de amostras (padrão: 300)")
    ap.add_argument("--seed", type=int, default=42, help="Semente do RNG")
    ap.add_argument("--out", type=Path, default=Path("sweep_samples.csv"))
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    lhs_01 = latin_hypercube(args.n, N_CONTINUOUS, rng)
    scaled = scale_samples(lhs_01)
    lens_list, vitr_list = assign_categorical(args.n, rng)

    # Montar registros
    fieldnames = [
        "case_id",
        *CONTINUOUS_KEYS,
        "lens_status", "vitrectomy",
        "R_mm", "t_mm", "mu1_MPa", "alpha1",
    ]
    rows = []
    for i in range(args.n):
        row = {"case_id": f"S{i+1:04d}"}
        for j, key in enumerate(CONTINUOUS_KEYS):
            row[key] = round(float(scaled[i, j]), 4)
        row["lens_status"] = lens_list[i]
        row["vitrectomy"] = vitr_list[i]
        # Derivados
        derived = derived_geometry(row)
        row.update(derived)
        rows.append(row)

    # Escrever CSV
    with open(args.out, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Metadados
    meta = {
        "n_samples": args.n,
        "seed": args.seed,
        "bounds": BOUNDS,
        "categorical": {
            "lens_status": LENS_OPTIONS,
            "vitrectomy": VITRECTOMY_OPTIONS,
        },
        "nominal_material": {
            "mu1_MPa": MU1_NOMINAL,
            "alpha1": ALPHA1_NOMINAL,
        },
        "notes": [
            "mu1_factor e alpha1_factor multiplicam os valores nominais do fit Ogden/Friedenwald",
            "R_mm = comprimento_axial_mm / 2 (aproximação esférica)",
            "t_mm = 0.55*t_equatorial + 0.45*t_posterior (espessura efetiva, malha uniforme)",
            "Malha ainda esférica; elipsoide / t(θ) ficam para iteração seguinte",
            "ACD_mm armazenada para uso futuro com geometria que inclua câmara anterior",
        ],
    }
    meta_path = args.out.with_suffix(".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False))

    print(f"Geradas {args.n} amostras LHS → {args.out}")
    print(f"Metadados → {meta_path}")


if __name__ == "__main__":
    main()
