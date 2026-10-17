#!/usr/bin/env python3
"""claude-wp1_octant — K efetivo @ pequeno ΔP com material hiperelástico (octante, NLGEOM).

Roda ne=6 e ne=8 (default) para checar sensibilidade de malha — gap que o Composer
nao cobriu. Importa read-only de wp1.1/scripts e wp1.2/scripts.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WP11_SCRIPTS = HERE.parents[1] / "wp1.1" / "scripts"
WP12_SCRIPTS = HERE.parents[1] / "wp1.2" / "scripts"
sys.path.insert(0, str(WP11_SCRIPTS))
sys.path.insert(0, str(WP12_SCRIPTS))

from ccx_utils import d1_from_ogden_mu1, run_ccx  # noqa: E402
from extract_K import K_analytic_mmHg_per_uL  # noqa: E402
from extract_pv_curve import extract_pv  # noqa: E402
from gen_sphere_shell_mesh import write_mesh  # noqa: E402
from write_deck import write_deck  # noqa: E402

R_MM, T_MM = 12.0, 0.5
P0, DP = 16.9, 1.0
E_MPA, NU = 3.0, 0.47


def load_params(fit: Path, material: str) -> tuple[str, dict]:
    data = json.loads(fit.read_text())
    sel = data.get("selected") or data.get("fit")
    model = sel.get("model", material)
    params = dict(sel["params"])
    if model.startswith("ogden") or material == "ogden":
        return "ogden1", {
            "mu1_MPa": params["mu1_MPa"],
            "alpha1": params["alpha1"],
            "D1": params.get("D1", d1_from_ogden_mu1(params["mu1_MPa"])),
        }
    return "yeoh2", {
        "C10_MPa": params["C10_MPa"],
        "C20_MPa": params["C20_MPa"],
    }


def run_ne(model: str, params: dict, material: str, ne: int, out: Path) -> dict:
    work = out / f"ccx_ne{ne}"
    work.mkdir(parents=True, exist_ok=True)
    mesh = work / "mesh.inp"
    write_mesh(
        mesh,
        R_MM,
        T_MM,
        ne,
        2,
        f"wp1.1-{material}",
        bc_mode="symmetry_octant",
        mesh_kind="spherical",
        theta_min_deg=3.0,
        reduced=True,
    )
    deck = work / "run.inp"
    write_deck(
        deck,
        mesh.name,
        T_MM,
        model,
        params,
        [P0 + DP],
        label=f"wp1.1-{material} small dP ne={ne}",
        bc_mode="symmetry_octant",
        p0_mmhg=P0,
    )
    frd = run_ccx(deck, clean=True)
    rows = extract_pv(deck, frd, R_MM, p0_mmhg=P0)
    dV = max((r["dV_uL"] for r in rows), default=float("nan"))
    k_fea = DP / dV if dV > 1e-12 else float("nan")
    k_lin = K_analytic_mmHg_per_uL(R_MM, T_MM, E_MPA, NU)
    return {
        "ne": ne,
        "dP_mmHg": DP,
        "dV_uL": dV,
        "K_FEA_small_strain": k_fea,
        "K_analytic_linear": k_lin,
        "error_vs_linear_pct": 100.0 * (k_fea - k_lin) / k_lin if k_lin else float("nan"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--material", choices=["ogden", "yeoh"], required=True)
    ap.add_argument("--fit", type=Path, required=True)
    ap.add_argument("--ne-levels", type=int, nargs="+", default=[6, 8])
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    model, params = load_params(args.fit, args.material)
    by_ne = [run_ne(model, params, args.material, ne, args.out) for ne in args.ne_levels]

    mesh_delta_pct = float("nan")
    if len(by_ne) >= 2 and all(r["K_FEA_small_strain"] > 0 for r in by_ne):
        k0, k1 = by_ne[0]["K_FEA_small_strain"], by_ne[1]["K_FEA_small_strain"]
        mesh_delta_pct = 100.0 * (k1 - k0) / k0

    result = {
        "material": args.material,
        "model": model,
        "params": params,
        "runs": by_ne,
        "mesh_sensitivity_pct": mesh_delta_pct,
        "source_fit": str(args.fit),
    }
    (args.out / "summary.json").write_text(json.dumps(result, indent=2))

    lines = [
        f"# claude-wp1_octant — wp1.1-{args.material} K hiperelástico @ pequeno ΔP\n",
        f"- **Modelo**: {model}",
        f"- **Params**: {json.dumps(params)}",
        f"- **Geometria**: R={R_MM} mm, t={T_MM} mm, octante",
        f"- **Carga**: ΔP={DP} mmHg acima de P₀={P0}",
        "",
        "| ne | K_FEA | K linear analítico | erro vs linear (%) |",
        "|---:|---:|---:|---:|",
    ]
    for r in by_ne:
        lines.append(
            f"| {r['ne']} | {r['K_FEA_small_strain']:.6f} | {r['K_analytic_linear']:.6f} "
            f"| {r['error_vs_linear_pct']:+.2f} |"
        )
    if len(by_ne) >= 2:
        lines += [
            "",
            f"**Sensibilidade de malha (ne={by_ne[0]['ne']} vs {by_ne[1]['ne']})**: "
            f"{mesh_delta_pct:+.2f}% em K_FEA.",
        ]
    lines += [
        "",
        "Nota: WP1.1 linear (E=3 MPa) é independente de material; este run mede K efetivo",
        "com a lei hiperelástica ajustada no WP1.2 — K >> linear é esperado.",
    ]
    (args.out / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
