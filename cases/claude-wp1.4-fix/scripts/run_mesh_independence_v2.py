#!/usr/bin/env python3
"""WP1.4 — independencia de malha, versao 2 (com a espessura corrigida).

O que mudou em relacao a run_mesh_independence_fixed.py:

  O estudo anterior pediu 8, 16 e 32 faixas de espessura com ne=8, mas o
  octante tem apenas 8 aneis de elementos — entao as tres rodadas tinham 8
  faixas efetivas e o que variou foi so ONDE t(theta) era amostrada dentro de
  cada anel. Mediu 1,3-2,6% de dispersao em K vinda de uma escolha arbitraria.

  Agora gen_mesh_bands usa uma faixa por anel com espessura = media de
  t(theta) ponderada pela area do anel. Nao sobra escolha arbitraria.

Dois estudos:

  A — CONVERGENCIA ESPACIAL (a que importa): ne em {8,10,12,14}, uma faixa por
      anel, espessura por media de area. Criterio: variacao relativa <1% em
      dois refinamentos seguidos (Roache 1997; ASME V&V 10).

  B — A CORRECAO FUNCIONOU? ne fixo, comparando:
        modo "point"     com n_bands = 8, 16, 32  -> deve dispersar (defeito antigo)
        modo "area_mean" com uma faixa por anel   -> valor unico, sem escolha
      Reporta a amplitude de cada modo.

Uso no Docker:
    docker compose run --rm fsi bash -lc 'pip install numpy --break-system-packages && cd /simulation/claude-wp1.4-fix/scripts && python3 run_mesh_independence_v2.py'
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

CONFIGS = [
    ("C_AL20_tfino",  {"comprimento_axial_mm": 20.0, "t_equatorial_mm": 0.30, "t_posterior_mm": 0.60}),
    ("C_AL20_tgrosso",{"comprimento_axial_mm": 20.0, "t_equatorial_mm": 0.80, "t_posterior_mm": 1.20}),
    ("C_AL30_tfino",  {"comprimento_axial_mm": 30.0, "t_equatorial_mm": 0.30, "t_posterior_mm": 0.60}),
    ("C_NOMINAL",     {"comprimento_axial_mm": 25.0, "t_equatorial_mm": 0.55, "t_posterior_mm": 0.90}),
]
BASE_ROW = {"mu1_factor": 1.0, "alpha1_factor": 1.0, "ACD_mm": 3.25,
            "lens_status": "phakic", "vitrectomy": False}


def run_case(cid, row, work, ne, n_bands, modo):
    resolved = resolve_case(row, n_bands=n_bands)
    t0 = time.time()
    mesh_path = work / f"{cid}_mesh.inp"
    mm = write_mesh_banded(
        mesh_path, resolved["R_mm"], resolved["t_equatorial_mm"],
        resolved["t_posterior_mm"], ne, 2, cid,
        theta_min_deg=resolved["theta_min_deg"], reduced=True,
        n_bands=n_bands, thickness_mode=modo,
    )
    mu1 = resolved["mu1_MPa"]
    deck = work / f"{cid}.inp"
    write_deck_variable_t(
        deck, mesh_path.name, mm["band_thickness_mm"], "ogden1",
        {"mu1_MPa": mu1, "alpha1": resolved["alpha1"],
         "D1": d1_from_ogden_mu1(mu1), "d1_tied_mu1": True},
        p_targets(p0=P0_MMHG), label=f"malha v2 {cid}", p0_mmhg=P0_MMHG,
    )
    frd = run_ccx(deck, clean=False)
    pv = sorted(extract_pv(deck, frd, resolved["R_mm"], p0_mmhg=P0_MMHG),
                key=lambda r: r["p_mmhg"])
    p = np.array([r["p_mmhg"] for r in pv], float)
    v = np.array([r["dV_uL"] for r in pv], float); v -= v[0]
    return {
        "ne": ne, "n_rings": mm["n_rings"], "n_bands": mm["n_bands_effective"],
        "modo": modo, "n_elements": mm["n_elements"],
        "t_over_R": round(mm["t_mean_mm"] / resolved["R_mm"], 5),
        "K": float((p[1] - p[0]) / (v[1] - v[0])) if v[1] > 0 else float("nan"),
        "V_max": float(v[-1]), "s": round(time.time() - t0, 1),
    }


def eps(serie, key):
    out = []
    for i, r in enumerate(serie):
        e = None
        if i > 0 and serie[i - 1][key]:
            e = abs(r[key] - serie[i - 1][key]) / abs(serie[i - 1][key]) * 100.0
        out.append({"ne": r["ne"], "n_bands": r["n_bands"], "n_elements": r["n_elements"],
                    key: r[key], "epsilon_pct": round(e, 4) if e is not None else None})
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=ROOT / "output_mesh_independence_v2")
    ap.add_argument("--ne-list", type=int, nargs="+", default=[8, 10, 12, 14])
    ap.add_argument("--ne-fixed", type=int, default=8)
    ap.add_argument("--bands-point", type=int, nargs="+", default=[8, 16, 32])
    args = ap.parse_args()

    work = args.out / "ccx_runs"; work.mkdir(parents=True, exist_ok=True)
    rep = {
        "criterio_A": "variacao relativa <1% em dois refinamentos seguidos (Roache 1997; ASME V&V 10)",
        "estudo_A_convergencia_espacial": {"modo": "area_mean, uma faixa por anel", "configs": {}},
        "estudo_B_a_correcao_funcionou": {"ne_fixo": args.ne_fixed, "configs": {}},
    }

    for name, geom in CONFIGS:
        row = {**BASE_ROW, **geom, "case_id": name}

        print(f"\n=== {name} — ESTUDO A (ne varia, media por area) ===")
        serie = []
        for ne in args.ne_list:
            r = run_case(f"{name}_A{ne}", row, work, ne, None, "area_mean")
            serie.append(r)
            print(f"  ne={ne:3d} aneis={r['n_rings']:3d} elems={r['n_elements']:5d} "
                  f"K={r['K']:.6f} V={r['V_max']:7.3f} ({r['s']:.0f}s)")
        rep["estudo_A_convergencia_espacial"]["configs"][name] = {
            "t_over_R": serie[0]["t_over_R"],
            "K": eps(serie, "K"), "V_max": eps(serie, "V_max"),
        }

        print(f"=== {name} — ESTUDO B (a correcao funcionou?) ===")
        pontual = []
        for nb in args.bands_point:
            r = run_case(f"{name}_Bp{nb}", row, work, args.ne_fixed, nb, "point")
            pontual.append(r)
            print(f"  point    n_bands pedido={nb:3d} efetivo={r['n_bands']:3d} K={r['K']:.6f}")
        r_area = run_case(f"{name}_Ba", row, work, args.ne_fixed, None, "area_mean")
        print(f"  area_mean uma faixa por anel ({r_area['n_bands']:3d})      K={r_area['K']:.6f}")

        Ks = [r["K"] for r in pontual]
        amp = (max(Ks) - min(Ks)) / np.mean(Ks) * 100.0
        rep["estudo_B_a_correcao_funcionou"]["configs"][name] = {
            "point": [{"n_bands_pedido": nb, "n_bands_efetivo": r["n_bands"], "K": r["K"]}
                      for nb, r in zip(args.bands_point, pontual)],
            "amplitude_point_pct": round(float(amp), 4),
            "area_mean": {"n_bands": r_area["n_bands"], "K": r_area["K"]},
            "amplitude_area_mean_pct": 0.0,
            "nota": "area_mean nao tem parametro livre: uma faixa por anel, "
                    "espessura = media de t(theta) ponderada pela area do anel",
        }
        print(f"  -> amplitude do modo pontual: {amp:.2f}%  | area_mean: valor unico")

        (args.out / "mesh_independence_v2.json").write_text(
            json.dumps(rep, indent=2, ensure_ascii=False))

    print(f"\nRelatorio: {args.out / 'mesh_independence_v2.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
