#!/usr/bin/env python3
"""claude-wp1_octant — Ogden N=1 vs Pallikaris, MULTI-START, D1 livre.

Independente do Composer (wp1_octant/scripts/run_material_matrix.py), que reusa
fit_pallikaris.py com UM UNICO start em x0=(2.14,1.77), D1 amarrado a mu1, e
bounds alpha1 em [0.5,6.0] -- o resultado (mu1=7.16, alpha1=0.500000071...)
fica colado no limite inferior da caixa, ou seja, nao sabemos se e um minimo
genuino ou se o otimizador so parou porque bateu na parede.

Aqui: (a) D1 livre (log10), (b) 7 pontos de partida cobrindo a regiao,
incluindo alpha1 abaixo de 0.3 para testar diretamente, NESTE ambiente
(ccx_preCICE 2.20 deste repo), se a hipotese de cancelamento catastrofico
em alpha1 baixo (relatorio do "outro Claude") se manifesta aqui, (c)
ne=8 por padrao para ficar comparavel ao Composer (que usou ne=8 no
wp1.2-ogden do material matrix), (d) clustering dos resultados finais.

NAO EDITA nenhum arquivo existente -- so importa (read-only) de wp1.2/scripts.
Nao roda sozinho: escreve o deck e delega pro usuario rodar dentro do
container Docker (mesmo padrao dos outros claude-*).
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

from ccx_utils import d1_from_ogden_mu1  # noqa: E402
from fit_hyperelastic import fit_quality  # noqa: E402
from fit_pallikaris import (  # noqa: E402
    DP_FEA_FINAL,
    KF_PER_UL,
    P0_MMHG,
    Geometry,
    PallikarisForward,
    generate_pallikaris_csv,
)

# x0 = (mu1, alpha1, log10(D1))
X0_CANDIDATES = [
    (2.14, 1.77, np.log10(0.238446)),      # otimo historico "bom" (handoff) -- reproduz?
    (7.16, 0.50, np.log10(0.0713)),        # resultado atual do Composer (colado no bound)
    (5.44, 0.49, np.log10(2.26e-4)),       # meu fit D1-livre anterior (claude-wp1.2, ne=6)
    (3.00, 0.90, np.log10(0.05)),          # cobertura intermediaria
    (1.50, 0.20, -6.0),                    # alpha1 BEM baixo -- teste direto da hipotese
    (0.80, 0.15, -6.0),                    # alpha1 ainda mais baixo, mu1 pequeno
    (9.00, 1.50, np.log10(0.02)),          # extremo oposto
]

LO = np.array([0.15, 0.15, -8.0])
HI = np.array([12.0, 3.5, 0.0])

TOL_MU1 = 0.5
TOL_ALPHA1 = 0.08
TOL_LOGD1 = 1.0


def residuals_factory(forward: PallikarisForward, v_exp: np.ndarray, p_exp: np.ndarray):
    n_eval = {"n": 0}

    def residuals(x: np.ndarray) -> np.ndarray:
        n_eval["n"] += 1
        mu1, alpha1, log_d1 = float(x[0]), float(x[1]), float(x[2])
        d1 = 10.0 ** log_d1
        tag = f"opt_{n_eval['n']:03d}"
        try:
            v_fea, p_fea = forward_run_with_d1(forward, mu1, alpha1, d1, tag)
        except Exception:
            return np.ones_like(p_exp) * 200.0
        order = np.argsort(v_fea)
        v_fea, p_fea = v_fea[order], p_fea[order]
        if v_fea.size == 0 or v_fea.max() < v_exp.max() * 0.9:
            return np.ones_like(p_exp) * 50.0
        dp_fea = p_fea - forward.p0_mmhg
        dp_pred = np.interp(v_exp, v_fea, dp_fea)
        return dp_pred - p_exp

    return residuals, n_eval


def forward_run_with_d1(forward: PallikarisForward, mu1: float, alpha1: float, d1: float, tag: str):
    """Same as PallikarisForward.run() but with D1 free instead of tied to mu1."""
    from write_deck import write_deck
    from ccx_utils import run_ccx
    from extract_pv_curve import extract_pv

    params = {"mu1_MPa": mu1, "alpha1": alpha1, "d1_tied_mu1": False, "D1": d1}
    deck = forward.work_dir / f"{tag}.inp"
    write_deck(
        deck,
        forward.mesh_path.name,
        forward.geom.t_mm,
        "ogden1",
        params,
        forward._p_targets(),
        label=f"claude multistart {tag}",
        nu=forward.geom.nu,
        E_mpa=forward.geom.E_mpa,
        bc_mode="symmetry_octant",
        p0_mmhg=forward.p0_mmhg,
    )
    frd = run_ccx(deck, clean=True)
    rows = extract_pv(deck, frd, forward.geom.R_mm, p0_mmhg=forward.p0_mmhg)
    v = np.array([r["dV_uL"] for r in rows], dtype=float)
    p = np.array([r["p_mmhg"] for r in rows], dtype=float)
    return v, p


def cluster(results: list[dict]) -> list[list[int]]:
    clusters: list[list[int]] = []
    for i, r in enumerate(results):
        placed = False
        for c in clusters:
            j = c[0]
            rj = results[j]
            if (
                abs(r["mu1_final"] - rj["mu1_final"]) < TOL_MU1
                and abs(r["alpha1_final"] - rj["alpha1_final"]) < TOL_ALPHA1
                and abs(np.log10(max(r["D1_final"], 1e-12)) - np.log10(max(rj["D1_final"], 1e-12))) < TOL_LOGD1
            ):
                c.append(i)
                placed = True
                break
        if not placed:
            clusters.append([i])
    return clusters


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ne", type=int, default=8, help="malha (Composer usou 8 no wp1.2-ogden)")
    ap.add_argument("--max-nfev", type=int, default=40)
    ap.add_argument("--out", type=Path, default=HERE.parent / "output" / "wp1.2-ogden")
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    csv_path = args.out / "pallikaris_synthetic.csv"
    exp = generate_pallikaris_csv(csv_path)
    v_exp = np.array([e.V_uL for e in exp])
    p_exp = np.array([e.P_mmHg for e in exp])

    geom = Geometry(R_mm=12.0, t_mm=0.5)

    all_results = []
    for i, x0 in enumerate(X0_CANDIDATES, start=1):
        work = args.out / "ccx_runs" / f"start_{i:02d}"
        forward = PallikarisForward(geom, work, ne=args.ne, dp_fea_final=DP_FEA_FINAL)
        residuals, n_eval = residuals_factory(forward, v_exp, p_exp)

        x0_arr = np.array(x0)
        t0 = time.time()
        try:
            res = least_squares(
                residuals,
                x0_arr,
                bounds=(LO, HI),
                max_nfev=args.max_nfev,
                ftol=1e-9,
                xtol=1e-9,
                diff_step=0.01,
                x_scale=[3.0, 0.5, 2.0],
                verbose=2,
            )
            fit_time = time.time() - t0
            mu1, alpha1, log_d1 = float(res.x[0]), float(res.x[1]), float(res.x[2])
            d1 = 10.0 ** log_d1
            v_fea, p_fea = forward_run_with_d1(forward, mu1, alpha1, d1, "final")
            order = np.argsort(v_fea)
            v_fea, p_fea = v_fea[order], p_fea[order]
            dp_fea = p_fea - forward.p0_mmhg
            dp_at_exp = np.interp(v_exp, v_fea, dp_fea)
            q = fit_quality(p_exp, dp_at_exp)
            at_lo_bound = bool(alpha1 < LO[1] + 0.02)
            all_results.append(
                {
                    "start": i,
                    "x0": list(x0),
                    "mu1_final": mu1,
                    "alpha1_final": alpha1,
                    "D1_final": d1,
                    "R2": q["R2"],
                    "max_residual_mmHg": q["max_residual_mmHg"],
                    "cost": float(res.cost),
                    "nfev": int(res.nfev),
                    "success": bool(res.success),
                    "message": res.message,
                    "alpha1_pinned_at_bound": at_lo_bound,
                    "fit_time_s": fit_time,
                    "fea_curve": [{"V_uL": float(v), "P_mmHg": float(p)} for v, p in zip(v_fea, p_fea)],
                }
            )
        except Exception as exc:
            all_results.append(
                {
                    "start": i,
                    "x0": list(x0),
                    "error": str(exc),
                    "mu1_final": float("nan"),
                    "alpha1_final": float("nan"),
                    "D1_final": float("nan"),
                    "R2": float("nan"),
                    "cost": float("inf"),
                    "nfev": 0,
                }
            )

    valid = [r for r in all_results if np.isfinite(r.get("cost", np.inf))]
    valid_sorted = sorted(valid, key=lambda r: r["cost"])
    idx_map = {id(r): i for i, r in enumerate(all_results)}
    clusters = cluster(all_results) if valid else []

    out_json = {
        "geometry": {"R_mm": geom.R_mm, "t_mm": geom.t_mm},
        "pallikaris": {"P0_mmHg": P0_MMHG, "Kf_per_uL": KF_PER_UL},
        "mesh": {"ne": args.ne, "bc_mode": "symmetry_octant"},
        "all_results": all_results,
        "ranked_by_cost": valid_sorted,
    }
    if valid_sorted:
        best = valid_sorted[0]
        out_json["selected"] = {
            "model": "ogden1",
            "params": {
                "mu1_MPa": best["mu1_final"],
                "alpha1": best["alpha1_final"],
                "D1": best["D1_final"],
                "d1_tied_mu1": False,
            },
            "quality": {"R2": best["R2"], "max_residual_mmHg": best["max_residual_mmHg"]},
            "optimizer": {"nfev": best["nfev"], "cost": best["cost"], "success": best.get("success")},
            "fea_curve": best["fea_curve"],
            "fit_convention": "delta_P_above_P0",
            "note": "menor custo entre os multi-starts; ver clusters no RESULTS.md antes de aceitar como unico.",
        }
    (args.out / "fit_results.json").write_text(json.dumps(out_json, indent=2))

    lines = [
        "# claude-wp1_octant -- WP1.2 Ogden N=1 vs Pallikaris, MULTI-START (ne=%d)\n" % args.ne,
        "Alvo: Pallikaris P0=16.9 mmHg, Kf=0.0126 /uL.",
        f"Geometria: R=12.0 mm, t=0.5 mm, octante ne={args.ne}.",
        "Rampa FEA: 0..80.0 mmHg (abs). D1 livre (log10).",
        "",
        "## Todos os fits, ordenados por custo",
        "",
        "| rank | x0 (mu1,alpha1,log10D1) | mu1 | alpha1 | D1 | R2 | resid_max | cost | nfev | no bound? |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in valid_sorted:
        lines.append(
            f"| {r['start']} | ({r['x0'][0]:.2f},{r['x0'][1]:.2f},{r['x0'][2]:.1f}) "
            f"| {r['mu1_final']:.3f} | {r['alpha1_final']:.3f} | {r['D1_final']:.3e} "
            f"| {r['R2']:.4f} | {r['max_residual_mmHg']:.2f} | {r['cost']:.2f} | {r['nfev']} "
            f"| {'SIM (colado!)' if r['alpha1_pinned_at_bound'] else 'nao'} |"
        )
    failed = [r for r in all_results if not np.isfinite(r.get("cost", np.inf))]
    if failed:
        lines.append("")
        lines.append("## Starts que falharam (CCX/otimizador)")
        for r in failed:
            lines.append(f"- start {r['start']} x0={r['x0']}: {r.get('error','?')}")

    lines.append("")
    lines.append(f"## {len(clusters)} cluster(s) distintos encontrados")
    lines.append("")
    for ci, members in enumerate(clusters, start=1):
        rs = [all_results[m] for m in members if np.isfinite(all_results[m].get("cost", np.inf))]
        if not rs:
            continue
        best_c = min(rs, key=lambda r: r["cost"])
        lines.append(
            f"- **C{ci}** ({len(rs)} fit(s)): mu1~{best_c['mu1_final']:.2f}, "
            f"alpha1~{best_c['alpha1_final']:.2f}, D1~{best_c['D1_final']:.2e}, "
            f"melhor R2={best_c['R2']:.4f}, cost={best_c['cost']:.2f}"
        )

    if valid_sorted:
        b = valid_sorted[0]
        lines.append("")
        lines.append("## Global (menor custo)")
        lines.append(f"- mu1 = {b['mu1_final']:.4f} MPa")
        lines.append(f"- alpha1 = {b['alpha1_final']:.4f}")
        lines.append(f"- D1 = {b['D1_final']:.4e}")
        lines.append(f"- R2 = {b['R2']:.4f}, resid max = {b['max_residual_mmHg']:.2f} mmHg")
        lines.append(f"- Veio de x0 = {tuple(round(v,3) for v in b['x0'])}")
        lines.append("")
        lines.append(
            "**Pergunta central**: algum start com alpha1 baixo (0.15-0.30) reduz o custo "
            "abaixo dos starts com alpha1~0.5? Se sim, o R2~0.93 fica ainda mais alto e a regiao "
            "de baixo alpha1 NAO falha neste ambiente (reforca achado do Composer/E1). Se os "
            "starts de alpha1 baixo divergirem ou falharem no CCX, e evidencia a favor da "
            "hipotese de cancelamento catastrofico do outro Claude, agora tambem observada aqui."
        )

    (args.out / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
