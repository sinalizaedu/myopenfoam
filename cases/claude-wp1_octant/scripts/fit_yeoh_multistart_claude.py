#!/usr/bin/env python3
"""claude-wp1_octant -- Yeoh-2 vs Pallikaris, MULTI-START.

O Composer (run_e3_e1b.py, via run_material_matrix.py) rodou UM UNICO start
em x0=(0.612,0.058) e achou C10=4.36/C20=4.99 MPa, R2=0.938 -- bom resultado
e ja reproduzido 2x (5/5 e depois 3/3 isolado). Mas nunca testamos se ha
OUTRO minimo comparavel em outra regiao do espaco (C10,C20), o que mudaria
K_FEA (WP1.1) e a inclinacao de pretensao (WP1.3) usados a jusante.

Aqui: 6 pontos de partida cobrindo regioes distintas de (C10,C20), mesmos
bounds do Composer (C10 em [1e-4,5], C20 em [-5,5]) + um ponto fora dessa
caixa (C10 ate 8) para checar se o teto de 5 MPa estava mordendo.

NAO EDITA nada existente -- so importa (read-only) de wp1.2/scripts.
Nao roda sozinho -- escreve os decks/scripts para o usuario rodar no Docker.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

HERE = Path(__file__).resolve().parent
WP12_SCRIPTS = HERE.parents[1] / "wp1.2" / "scripts"
WP11_SCRIPTS = HERE.parents[1] / "wp1.1" / "scripts"
sys.path.insert(0, str(WP12_SCRIPTS))
sys.path.insert(0, str(WP11_SCRIPTS))

from fit_hyperelastic import fit_quality  # noqa: E402
from fit_pallikaris import DP_FEA_FINAL, KF_PER_UL, P0_MMHG, generate_pallikaris_csv  # noqa: E402
from run_e3_e1b import PallikarisYeohForward  # noqa: E402

X0_CANDIDATES = [
    (0.612, 0.058),   # ponto do Composer/E3 (selftest reference)
    (4.36, 4.99),      # ja no resultado convergido -- checa estabilidade local
    (0.30, 0.02),      # canto baixo (regiao E2 do Composer, testada so p/ estabilidade CCX)
    (1.50, 1.50),      # meio do dominio
    (0.05, 3.0),       # C10 baixo, C20 alto
    (3.0, -2.0),        # C20 negativo (permitido pelos bounds -5..5)
]

LO = np.array([1.0e-4, -5.0])
HI = np.array([8.0, 8.0])  # teto alargado vs Composer (5,5) p/ checar se mordia

TOL_C10 = 0.3
TOL_C20 = 0.3


def cluster(results: list[dict]) -> list[list[int]]:
    clusters: list[list[int]] = []
    for i, r in enumerate(results):
        placed = False
        for c in clusters:
            j = c[0]
            rj = results[j]
            if abs(r["C10_final"] - rj["C10_final"]) < TOL_C10 and abs(r["C20_final"] - rj["C20_final"]) < TOL_C20:
                c.append(i)
                placed = True
                break
        if not placed:
            clusters.append([i])
    return clusters


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ne", type=int, default=8, help="Composer usou 8 no wp1.2-yeoh (via run_e3_e1b default)")
    ap.add_argument("--max-nfev", type=int, default=35)
    ap.add_argument("--repro-trials", type=int, default=3)
    ap.add_argument("--out", type=Path, default=HERE.parent / "output" / "wp1.2-yeoh")
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    csv_path = args.out / "pallikaris_synthetic.csv"
    exp = generate_pallikaris_csv(csv_path)
    v_exp = np.array([e.V_uL for e in exp])
    p_exp = np.array([e.P_mmHg for e in exp])

    all_results = []
    for i, x0 in enumerate(X0_CANDIDATES, start=1):
        work = args.out / "ccx_runs" / f"start_{i:02d}"
        forward = PallikarisYeohForward(work, ne=args.ne, p_final=DP_FEA_FINAL)
        n_eval = {"n": 0}

        def residuals(x: np.ndarray) -> np.ndarray:
            n_eval["n"] += 1
            tag = f"opt_{n_eval['n']:03d}"
            try:
                v_fea, p_fea = forward.run(float(x[0]), float(x[1]), tag=tag)
            except Exception:
                return np.ones_like(p_exp) * 1e3
            order = np.argsort(v_fea)
            v_fea, p_fea = v_fea[order], p_fea[order]
            if v_fea.size == 0 or v_fea.max() < v_exp.max() * 0.9:
                return np.ones_like(p_exp) * 50.0
            dp_fea = p_fea - P0_MMHG
            dp_pred = np.interp(v_exp, v_fea, dp_fea)
            return dp_pred - p_exp

        t0 = time.time()
        try:
            res = least_squares(
                residuals,
                np.array(x0),
                bounds=(LO, HI),
                max_nfev=args.max_nfev,
                ftol=1e-9,
                xtol=1e-9,
                diff_step=0.02,
                verbose=2,
            )
            fit_time = time.time() - t0
            c10, c20 = float(res.x[0]), float(res.x[1])
            v_fea, p_fea = forward.run(c10, c20, tag="final")
            order = np.argsort(v_fea)
            v_fea, p_fea = v_fea[order], p_fea[order]
            dp_fea = p_fea - P0_MMHG
            dp_at_exp = np.interp(v_exp, v_fea, dp_fea)
            q = fit_quality(p_exp, dp_at_exp)
            all_results.append(
                {
                    "start": i,
                    "x0": list(x0),
                    "C10_final": c10,
                    "C20_final": c20,
                    "R2": q["R2"],
                    "max_residual_mmHg": q["max_residual_mmHg"],
                    "cost": float(res.cost),
                    "nfev": int(res.nfev),
                    "success": bool(res.success),
                    "message": res.message,
                    "fit_time_s": fit_time,
                    "fea_curve": [{"V_uL": float(v), "P_abs_mmHg": float(p)} for v, p in zip(v_fea, p_fea)],
                }
            )
        except Exception as exc:
            all_results.append(
                {"start": i, "x0": list(x0), "error": str(exc), "C10_final": float("nan"),
                 "C20_final": float("nan"), "R2": float("nan"), "cost": float("inf"), "nfev": 0}
            )

    valid_sorted = sorted(
        [r for r in all_results if np.isfinite(r.get("cost", np.inf))], key=lambda r: r["cost"]
    )
    clusters = cluster(all_results) if valid_sorted else []

    out_json = {
        "geometry": {"R_mm": 12.0, "t_mm": 0.5},
        "pallikaris": {"P0_mmHg": P0_MMHG, "Kf_per_uL": KF_PER_UL},
        "mesh": {"ne": args.ne, "bc_mode": "symmetry_octant"},
        "all_results": all_results,
        "ranked_by_cost": valid_sorted,
    }
    if valid_sorted:
        best = valid_sorted[0]
        out_json["selected"] = {
            "model": "yeoh2",
            "params": {"C10_MPa": best["C10_final"], "C20_MPa": best["C20_final"]},
            "quality": {"R2": best["R2"], "max_residual_mmHg": best["max_residual_mmHg"]},
            "optimizer": {"nfev": best["nfev"], "cost": best["cost"], "success": best.get("success")},
            "fea_curve": best["fea_curve"],
            "fit_convention": "delta_P_above_P0",
        }
    (args.out / "fit_results.json").write_text(json.dumps(out_json, indent=2))

    lines = [
        "# claude-wp1_octant -- WP1.2 Yeoh-2 vs Pallikaris, MULTI-START (ne=%d)\n" % args.ne,
        "Alvo: Pallikaris P0=16.9 mmHg, Kf=0.0126 /uL.",
        f"Geometria: R=12.0 mm, t=0.5 mm, octante ne={args.ne}.",
        "Bounds C10=[1e-4,8], C20=[-5,8] (alargado vs Composer p/ checar teto).",
        "",
        "## Todos os fits, ordenados por custo",
        "",
        "| rank | x0 (C10,C20) | C10 | C20 | R2 | resid_max | cost | nfev |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in valid_sorted:
        lines.append(
            f"| {r['start']} | ({r['x0'][0]:.3f},{r['x0'][1]:.3f}) | {r['C10_final']:.3f} "
            f"| {r['C20_final']:.3f} | {r['R2']:.4f} | {r['max_residual_mmHg']:.2f} "
            f"| {r['cost']:.2f} | {r['nfev']} |"
        )
    failed = [r for r in all_results if not np.isfinite(r.get("cost", np.inf))]
    if failed:
        lines.append("")
        lines.append("## Starts que falharam")
        for r in failed:
            lines.append(f"- start {r['start']} x0={r['x0']}: {r.get('error','?')}")

    lines.append("")
    lines.append(f"## {len(clusters)} cluster(s) distintos encontrados")
    for ci, members in enumerate(clusters, start=1):
        rs = [all_results[m] for m in members if np.isfinite(all_results[m].get("cost", np.inf))]
        if not rs:
            continue
        b = min(rs, key=lambda r: r["cost"])
        lines.append(
            f"- **C{ci}** ({len(rs)} fit(s)): C10~{b['C10_final']:.3f}, C20~{b['C20_final']:.3f}, "
            f"melhor R2={b['R2']:.4f}, cost={b['cost']:.2f}"
        )

    if valid_sorted:
        b = valid_sorted[0]
        lines.append("")
        lines.append("## Global (menor custo)")
        lines.append(f"- C10 = {b['C10_final']:.4f} MPa")
        lines.append(f"- C20 = {b['C20_final']:.4f} MPa")
        lines.append(f"- R2 = {b['R2']:.4f}, resid max = {b['max_residual_mmHg']:.2f} mmHg")
        lines.append(
            "\n**Referencia (Composer/E3, single-start)**: C10=4.3639, C20=4.9950, R2=0.9383. "
            "Se o global aqui bater com isso (dentro de ~1%), confirma que o minimo do Yeoh e "
            "unico/bem-condicionado -- ao contrario do Ogden, onde meu multi-start (claude-wp1.2) "
            "NAO reproduziu o otimo historico e achou 5 clusters distintos com custo comparavel."
        )

    (args.out / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
