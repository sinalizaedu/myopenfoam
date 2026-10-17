#!/usr/bin/env python3
"""claude-wp1_octant -- WP1.3: pretensao, reconciliando curva-do-ajuste vs curva-densa-forward.

A Bruna sinalizou uma discrepancia real: o WP1.3 do Composer (pretension_from_fit.py)
usa a curva do PROPRIO ajuste do otimizador (poucos pontos, os mesmos 16 steps usados
para calibrar mu1/alpha1 ou C10/C20) para estimar dP/dV por diferenca finita local.
O E5 (do relatorio do outro Claude) usava uma curva forward DENSA (muitos pontos,
rodada a parte, nao os pontos de calibracao) e achou -19.7%, bem diferente do
+0.78% (Ogden) / +15.6% (Yeoh) do Composer.

Isso pode ser so ruido de diferenciacao numerica: poucos pontos → derivada local
mal condicionada, especialmente perto de V=0 onde a curva e mais "achatada".

Aqui, para CADA material (usa o fit_results.json do multistart deste caso):
  1. Repete o calculo "curva do ajuste" (dp_dv_local nos mesmos pontos de calibracao)
     -- comparavel direto ao numero do Composer.
  2. Roda uma curva FORWARD DENSA nova (30 steps, nao os pontos de calibracao,
     malha fresca) e calcula a mesma derivada local em V≈0 e V=V_ref.
  3. Reporta os dois lado a lado + a diferenca relativa entre os dois metodos.

Isso decide se a discrepancia com o E5 e real (sensibilidade de metodo) ou some
quando se usa curva densa em ambos os lados.

NAO EDITA nada existente -- so importa (read-only) de wp1.1/wp1.2 scripts.
Nenhum dos dois resultados (curva-ajuste ou curva-densa) deve ir pro relatorio
como quantificacao final -- MULF continua nao implementado (mesma ressalva do
Composer e do handoff original).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
WP11_SCRIPTS = HERE.parents[1] / "wp1.1" / "scripts"
WP12_SCRIPTS = HERE.parents[1] / "wp1.2" / "scripts"
sys.path.insert(0, str(WP11_SCRIPTS))
sys.path.insert(0, str(WP12_SCRIPTS))

from ccx_utils import d1_from_ogden_mu1, run_ccx  # noqa: E402
from extract_pv_curve import extract_pv  # noqa: E402
from fit_hyperelastic import dp_dv_local  # noqa: E402
from gen_sphere_shell_mesh import write_mesh  # noqa: E402
from write_deck import write_deck  # noqa: E402

R_MM, T_MM = 12.0, 0.5
P0_DEFAULT = 16.9


def load_fit_curve(fit: Path) -> tuple[np.ndarray, np.ndarray, dict, str]:
    data = json.loads(fit.read_text())
    sel = data.get("selected") or data.get("fit")
    model = sel.get("model", "unknown")
    params = sel.get("params", {})
    curve = sel["fea_curve"]
    v = np.array([r["V_uL"] for r in curve], dtype=float)
    p_key = "P_abs_mmHg" if "P_abs_mmHg" in curve[0] else "P_mmHg"
    p_abs = np.array([r[p_key] for r in curve], dtype=float)
    p0 = float(data.get("pallikaris", {}).get("P0_mmHg", P0_DEFAULT))
    return v, p_abs - p0, params, model


def model_params_for_deck(model: str, params: dict) -> dict:
    if model.startswith("ogden"):
        return {
            "mu1_MPa": params["mu1_MPa"], "alpha1": params["alpha1"],
            "D1": params.get("D1", d1_from_ogden_mu1(params["mu1_MPa"])),
        }
    return {"C10_MPa": params["C10_MPa"], "C20_MPa": params["C20_MPa"]}


def dense_forward_curve(model: str, params: dict, ne: int, p0: float, p_final: float, n_steps: int, work: Path) -> tuple[np.ndarray, np.ndarray]:
    work.mkdir(parents=True, exist_ok=True)
    mesh = work / "mesh.inp"
    write_mesh(
        mesh, R_MM, T_MM, ne, 2, "wp1.3-dense-forward",
        bc_mode="symmetry_octant", mesh_kind="spherical", theta_min_deg=3.0, reduced=True,
    )
    p_targets = [p0 + (p_final - p0) * i / n_steps for i in range(1, n_steps + 1)]
    deck = work / "dense.inp"
    write_deck(
        deck, mesh.name, T_MM, model, params, p_targets,
        label="wp1.3 dense forward", bc_mode="symmetry_octant", p0_mmhg=p0,
    )
    frd = run_ccx(deck, clean=True)
    rows = extract_pv(deck, frd, R_MM, p0_mmhg=p0)
    v = np.array([r["dV_uL"] for r in rows], dtype=float)
    p = np.array([r["p_mmhg"] for r in rows], dtype=float)
    order = np.argsort(v)
    return v[order], (p[order] - p0)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fit", type=Path, required=True)
    ap.add_argument("--material", required=True)
    ap.add_argument("--ne", type=int, default=8)
    ap.add_argument("--p-final", type=float, default=80.0)
    ap.add_argument("--n-steps-dense", type=int, default=30)
    ap.add_argument("--p0", type=float, default=P0_DEFAULT)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)

    v_fit, dp_fit, params, model = load_fit_curve(args.fit)
    v_ref = min(10.0, float(v_fit.max()) * 0.2) if v_fit.max() > 1e-6 else 2.0

    k_v0_fitcurve = dp_dv_local(v_fit, dp_fit, 0.0)
    k_ref_fitcurve = dp_dv_local(v_fit, dp_fit, v_ref)
    rel_fitcurve = 100.0 * (k_ref_fitcurve - k_v0_fitcurve) / k_v0_fitcurve if abs(k_v0_fitcurve) > 1e-12 else float("nan")

    deck_params = model_params_for_deck(model, params)
    v_dense, dp_dense = dense_forward_curve(
        model, deck_params, args.ne, args.p0, args.p_final, args.n_steps_dense, args.out / "ccx_dense"
    )
    k_v0_dense = dp_dv_local(v_dense, dp_dense, 0.0)
    k_ref_dense = dp_dv_local(v_dense, dp_dense, v_ref)
    rel_dense = 100.0 * (k_ref_dense - k_v0_dense) / k_v0_dense if abs(k_v0_dense) > 1e-12 else float("nan")

    method_diff_pct_v0 = 100.0 * (k_v0_dense - k_v0_fitcurve) / k_v0_fitcurve if abs(k_v0_fitcurve) > 1e-12 else float("nan")
    method_diff_pct_ref = 100.0 * (k_ref_dense - k_ref_fitcurve) / k_ref_fitcurve if abs(k_ref_fitcurve) > 1e-12 else float("nan")

    result = {
        "material": args.material, "model": model, "params": params, "P0_mmHg": args.p0,
        "V_ref_uL": v_ref,
        "fit_curve_method": {
            "n_points": int(len(v_fit)),
            "K_local_at_V0": k_v0_fitcurve, "K_local_at_Vref": k_ref_fitcurve, "relative_change_pct": rel_fitcurve,
        },
        "dense_forward_method": {
            "n_points": args.n_steps_dense,
            "K_local_at_V0": k_v0_dense, "K_local_at_Vref": k_ref_dense, "relative_change_pct": rel_dense,
        },
        "method_agreement": {
            "diff_pct_at_V0": method_diff_pct_v0, "diff_pct_at_Vref": method_diff_pct_ref,
        },
        "source_fit": str(args.fit),
        "note": "MULF nao implementado -- nenhum dos dois numeros vai pro relatorio como quantificacao final.",
    }
    (args.out / "pretension_study.json").write_text(json.dumps(result, indent=2))

    lines = [
        f"# claude-wp1_octant -- WP1.3-{args.material} pretensao, dois metodos lado a lado\n",
        f"- **Modelo**: {model}",
        f"- **P0**: {args.p0} mmHg, V_ref={v_ref:.3f} uL",
        "",
        "| metodo | n pontos | dP/dV @ V=0 | dP/dV @ V_ref | variacao relativa |",
        "|---|---:|---:|---:|---:|",
        f"| curva do ajuste (Composer-like) | {len(v_fit)} | {k_v0_fitcurve:.4f} | {k_ref_fitcurve:.4f} | {rel_fitcurve:+.2f}% |",
        f"| curva densa forward (novo) | {args.n_steps_dense} | {k_v0_dense:.4f} | {k_ref_dense:.4f} | {rel_dense:+.2f}% |",
        "",
        f"**Concordancia entre metodos**: {method_diff_pct_v0:+.1f}% (@V=0), {method_diff_pct_ref:+.1f}% (@V_ref).",
        "",
        "Se os dois metodos derem sinais/ordens de grandeza diferentes, a inclinacao de "
        "pretensao e sensivel ao metodo de diferenciacao numerica (poucos pontos da curva "
        "de calibracao vs curva densa dedicada) -- ai nenhum dos dois numeros e confiavel "
        "isoladamente e o proximo passo tem que ser MULF real, nao mais pos-processamento "
        "de curva P(V).",
        "",
        result["note"],
    ]
    (args.out / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
