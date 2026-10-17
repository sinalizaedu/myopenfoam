#!/usr/bin/env python3
"""WP1.4 corrigido — independencia de malha nos cantos da caixa de projeto.

Por que isto nao existia: a convergencia do WP1.2 foi estabelecida com espessura
uniforme, R=12 mm e t=0,5 mm. A varredura do WP1.4 roda R em [10;15] e t em
[0,3;1,2] — t/R varia ~4x, e o termo de 2a ordem identificado no WP1.1 escala com
(t/R)^2. Nenhum caso da varredura tinha checagem de malha.

E por que precisa do gen_mesh_bands: no pipeline original o numero de faixas de
espessura e igual a `ne`, entao refinar a malha refinava tambem a discretizacao de
t(theta) e os dois efeitos ficavam confundidos. Aqui sao separados:

  Estudo A — ne em {8, 10, 12} com n_bands FIXO  -> erro de discretizacao espacial
  Estudo B — n_bands em {8, 16, 32} com ne FIXO  -> erro de representacao de t(theta)

Criterio (WP1.1/WP1.2, Roache 1997 / ASME V&V 10): variacao relativa <1% em dois
refinamentos seguidos.

Uso no Docker:
    docker compose run --rm fsi bash -lc \
      'pip install numpy --break-system-packages && \
       cd /simulation/claude-wp1.4-fix/scripts && python3 run_mesh_independence_fixed.py'
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CASES = ROOT.parent
sys.path.insert(0, str(CASES / "wp1.2" / "scripts"))
sys.path.insert(0, str(HERE))

from ccx_utils import d1_from_ogden_mu1, run_ccx  # noqa: E402
from extract_pv_curve import extract_pv  # noqa: E402

from case_model_fixed import P0_MMHG, p_targets, resolve_case  # noqa: E402
from gen_mesh_bands import write_mesh_banded  # noqa: E402

sys.path.append(str(CASES / "wp1.4" / "sweep_full" / "scripts"))
from write_deck_vt import write_deck_variable_t  # noqa: E402

# Cantos da caixa de projeto do plano (AL 20-30, t_eq 0,3-0,8, t_post 0,6-1,2),
# escolhidos para maximizar a variacao de t/R, mais o caso nominal.
CONFIGS = [
    ("C_AL20_tfino", {"comprimento_axial_mm": 20.0, "t_equatorial_mm": 0.30, "t_posterior_mm": 0.60}),
    ("C_AL20_tgrosso", {"comprimento_axial_mm": 20.0, "t_equatorial_mm": 0.80, "t_posterior_mm": 1.20}),
    ("C_AL30_tfino", {"comprimento_axial_mm": 30.0, "t_equatorial_mm": 0.30, "t_posterior_mm": 0.60}),
    ("C_AL30_tgrosso", {"comprimento_axial_mm": 30.0, "t_equatorial_mm": 0.80, "t_posterior_mm": 1.20}),
    ("C_NOMINAL", {"comprimento_axial_mm": 25.0, "t_equatorial_mm": 0.55, "t_posterior_mm": 0.90}),
]

BASE_ROW = {
    "mu1_factor": 1.0,
    "alpha1_factor": 1.0,
    "ACD_mm": 3.25,
    "lens_status": "phakic",
    "vitrectomy": False,
}


def run_case(cid: str, row: dict, work: Path, ne: int, n_bands: int) -> dict:
    resolved = resolve_case(row, n_bands=n_bands)
    t0 = time.time()
    mesh_path = work / f"{cid}_mesh.inp"
    mesh_meta = write_mesh_banded(
        mesh_path,
        resolved["R_mm"],
        resolved["t_equatorial_mm"],
        resolved["t_posterior_mm"],
        ne,
        2,
        cid,
        theta_min_deg=resolved["theta_min_deg"],
        reduced=True,
        n_bands=n_bands,
    )
    mu1 = resolved["mu1_MPa"]
    deck_path = work / f"{cid}.inp"
    write_deck_variable_t(
        deck_path,
        mesh_path.name,
        mesh_meta["band_thickness_mm"],
        "ogden1",
        {
            "mu1_MPa": mu1,
            "alpha1": resolved["alpha1"],
            "D1": d1_from_ogden_mu1(mu1),
            "d1_tied_mu1": True,
        },
        p_targets(p0=P0_MMHG),
        label=f"wp1.4 malha {cid}",
        p0_mmhg=P0_MMHG,
    )
    frd = run_ccx(deck_path, clean=False)
    pv = extract_pv(deck_path, frd, resolved["R_mm"], p0_mmhg=P0_MMHG)
    rows = sorted(pv, key=lambda r: r["p_mmhg"])
    p = np.array([r["p_mmhg"] for r in rows], dtype=float)
    v = np.array([r["dV_uL"] for r in rows], dtype=float)
    v = v - v[0]
    k = float((p[1] - p[0]) / (v[1] - v[0])) if v[1] > 0 else float("nan")
    return {
        "case_id": cid,
        "ne": ne,
        "n_bands": mesh_meta["n_bands_effective"],
        "n_elements": mesh_meta["n_elements"],
        "R_mm": resolved["R_mm"],
        "t_over_R": round(resolved["t_mean_mm"] / resolved["R_mm"], 5),
        "K_basal_mmHg_per_uL": k,
        "V_max_uL": float(v[-1]),
        "elapsed_s": round(time.time() - t0, 1),
    }


def epsilon_table(series: list[dict], key: str, varying: str) -> list[dict]:
    """Variacao relativa entre refinamentos sucessivos, em %."""
    out = []
    for i, r in enumerate(series):
        eps = None
        if i > 0:
            prev = series[i - 1][key]
            if prev:
                eps = abs(r[key] - prev) / abs(prev) * 100.0
        out.append(
            {
                varying: r[varying],
                "n_elements": r["n_elements"],
                key: round(r[key], 6),
                "epsilon_pct": round(eps, 4) if eps is not None else None,
            }
        )
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=ROOT / "output_mesh_independence")
    ap.add_argument("--ne-list", type=int, nargs="+", default=[8, 10, 12])
    ap.add_argument("--bands-list", type=int, nargs="+", default=[8, 16, 32])
    ap.add_argument("--ne-fixed", type=int, default=8)
    ap.add_argument("--bands-fixed", type=int, default=16)
    args = ap.parse_args()

    work = args.out / "ccx_runs"
    work.mkdir(parents=True, exist_ok=True)
    report: dict = {
        "criterion": "variacao relativa <1% em dois refinamentos seguidos (Roache 1997; ASME V&V 10)",
        "estudo_A_malha_espacial": {"n_bands_fixo": args.bands_fixed, "configs": {}},
        "estudo_B_faixas_espessura": {"ne_fixo": args.ne_fixed, "configs": {}},
    }

    for name, geom in CONFIGS:
        row = {**BASE_ROW, **geom, "case_id": name}

        print(f"\n=== {name} — Estudo A (ne varia, n_bands={args.bands_fixed}) ===")
        serie_a = []
        for ne in args.ne_list:
            r = run_case(f"{name}_neA{ne}", row, work, ne, args.bands_fixed)
            serie_a.append(r)
            print(f"  ne={ne:3d}  elems={r['n_elements']:5d}  K={r['K_basal_mmHg_per_uL']:.6f}")
        report["estudo_A_malha_espacial"]["configs"][name] = {
            "t_over_R": serie_a[0]["t_over_R"],
            "K": epsilon_table(serie_a, "K_basal_mmHg_per_uL", "ne"),
            "V_max": epsilon_table(serie_a, "V_max_uL", "ne"),
        }

        print(f"=== {name} — Estudo B (n_bands varia, ne={args.ne_fixed}) ===")
        serie_b = []
        for nb in args.bands_list:
            r = run_case(f"{name}_nbB{nb}", row, work, args.ne_fixed, nb)
            serie_b.append(r)
            print(f"  n_bands={nb:3d} (efetivo {r['n_bands']:3d})  K={r['K_basal_mmHg_per_uL']:.6f}")
        report["estudo_B_faixas_espessura"]["configs"][name] = {
            "K": epsilon_table(serie_b, "K_basal_mmHg_per_uL", "n_bands"),
            "V_max": epsilon_table(serie_b, "V_max_uL", "n_bands"),
        }

        (args.out / "mesh_independence.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False)
        )

    print(f"\nRelatorio: {args.out / 'mesh_independence.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
