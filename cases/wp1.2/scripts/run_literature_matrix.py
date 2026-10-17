#!/usr/bin/env python3
"""Run WP1.2 fits for literature targets × material models (Ogden / Yeoh).

Default: P_final = 50 mmHg (aligned with WP0 clinical range).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
WP12 = HERE.parent
sys.path.insert(0, str(HERE))

from fit_pallikaris import DP_FEA_FINAL, Geometry, P0_MMHG, fit_ogden1, PallikarisForward  # noqa: E402
from literature_targets import generate_target, MAIN_TARGETS, V_MAX_SAFE  # noqa: E402
from run_e3_e1b import fit_yeoh2, PallikarisYeohForward  # noqa: E402
from yeoh_fit_bounds import yeoh_bounds  # noqa: E402

import numpy as np

MATERIALS = ("ogden", "yeoh")

# Warm starts from prior narrow-box optima (still feasible in log C20 box).
YEOH_WARM_MPA: dict[str, tuple[float, float]] = {
    "silver": (2.949, 4.187),
    "friedenwald": (0.271433, 284.859),
    "pallikaris": (2.904, 1.563),
}


def _yeoh_eval_fixed(forward: PallikarisYeohForward, exp: list, c10: float, c20: float) -> dict:
    from fit_hyperelastic import fit_quality
    from fit_pallikaris import P0_MMHG

    v_fea, p_fea = forward.run(c10, c20, tag="eval_fixed")
    v_exp = np.array([e.V_uL for e in exp])
    p_exp = np.array([e.P_mmHg for e in exp])
    order = np.argsort(v_fea)
    v_fea, p_fea = v_fea[order], p_fea[order]
    dp_fea = p_fea - P0_MMHG
    dp_pred = np.interp(v_exp, v_fea, dp_fea)
    quality = fit_quality(p_exp, dp_pred)
    return {
        "model": "yeoh2",
        "params": {"C10_MPa": c10, "C20_MPa": c20},
        "quality": quality,
        "optimizer": {
            "success": True,
            "message": "fixed parameters (no optimizer)",
            "nfev": 0,
            "cost": float(quality["ss_res"]),
            "fit_time_s": 0.0,
        },
        "fit_convention": "delta_P_above_P0",
    }


def fit_yeoh_multistart_local(
    forward: PallikarisYeohForward,
    exp: list,
    target: str,
    max_nfev: int,
) -> dict:
    x0_def, _, _ = yeoh_bounds()
    starts: list[np.ndarray] = [x0_def.copy()]
    if target in YEOH_WARM_MPA:
        c10, c20 = YEOH_WARM_MPA[target]
        starts.append(np.array([c10, np.log10(c20)]))
    candidates: list[dict] = []
    for si, x0 in enumerate(starts):
        row = fit_yeoh2(forward, exp, max_nfev=max_nfev, x0=x0)
        candidates.append({**row, "warm_start_index": si})
    if target in YEOH_WARM_MPA:
        c10, c20 = YEOH_WARM_MPA[target]
        candidates.append(_yeoh_eval_fixed(forward, exp, c10, c20))
    best = max(candidates, key=lambda r: float(r["quality"]["R2"]))
    return best


def run_one(
    target: str,
    material: str,
    out: Path,
    *,
    ne: int,
    max_nfev: int,
    p_final: float,
    R: float,
    t: float,
) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    csv_path = out / f"{target}_target.csv"
    v_max = V_MAX_SAFE.get(target, 50.0)
    exp = generate_target(target, csv_path, v_max=v_max)

    if material == "ogden":
        geom = Geometry(R_mm=R, t_mm=t, source=f"{target}_wp1.2")
        work = out / "ccx_runs" / "ogden1"
        forward = PallikarisForward(geom, work, ne=ne, dp_fea_final=p_final)
        result = fit_ogden1(forward, exp, max_nfev=max_nfev)
    elif material == "yeoh":
        work = out / "ccx_runs"
        forward = PallikarisYeohForward(work, ne=ne, p_final=p_final)
        forward.geom = Geometry(R_mm=R, t_mm=t, source=f"{target}_wp1.2")
        result = fit_yeoh_multistart_local(
            forward, exp, target, max_nfev=max(max_nfev, 60)
        )
    else:
        raise ValueError(material)

    payload = {
        "target": target,
        "material": material,
        "v_max_uL": v_max,
        "geometry": asdict(forward.geom),
        "fea_ramp": {"P_final_mmHg_abs": p_final, "P0_mmHg": P0_MMHG},
        "mesh": {"ne": ne, "bc_mode": "symmetry_octant"},
        "selected": result,
    }
    (out / "fit_results.json").write_text(json.dumps(payload, indent=2))

    q = result["quality"]
    p = result["params"]
    lines = [
        f"# wp1.2 — {target} × {material} (P_final={p_final} mmHg)\n",
        f"- **Target**: {target}",
        f"- **Material**: {material}",
        f"- **Geometry**: R={R} mm, t={t} mm",
        f"- **Parameters**: {json.dumps(p)}",
        f"- **R²**: {q['R2']:.6f}",
        f"- **Max residual**: {q['max_residual_mmHg']:.2f} mmHg",
        f"- **Optimizer nfev**: {result['optimizer']['nfev']}",
        "",
    ]
    (out / "RESULTS.md").write_text("\n".join(lines))
    print("\n".join(lines))
    return payload


def write_summary(out_root: Path, results: list[dict]) -> None:
    lines = [
        "# WP1.2 literature matrix (P_final=50 mmHg)\n",
        "| target | material | R² | max|resid| [mmHg] | nfev | out |",
        "|---|---|---:|---:|---:|---|",
    ]
    for r in results:
        sel = r["selected"]
        q = sel["quality"]
        opt = sel["optimizer"]
        tag = f"{r['target']}_{r['material']}"
        lines.append(
            f"| {r['target']} | {r['material']} | {q['R2']:.4f} | "
            f"{q['max_residual_mmHg']:.2f} | {opt['nfev']} | `{tag}` |"
        )
    lines.append("")
    (out_root / "LITERATURE_MATRIX_SUMMARY.md").write_text("\n".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    env_targets = os.environ.get("TARGETS", ",".join(MAIN_TARGETS))
    env_materials = os.environ.get("MATERIALS", ",".join(MATERIALS))
    env_out = os.environ.get("OUT", str(WP12 / "output_literature_p50_digitized"))
    ap.add_argument(
        "--targets",
        default=env_targets,
        help="Comma-separated targets (default: env TARGETS or friedenwald,pallikaris,silver)",
    )
    ap.add_argument(
        "--materials",
        default=env_materials,
        help="Comma-separated materials (default: env MATERIALS or ogden,yeoh)",
    )
    ap.add_argument("--p-final", type=float, default=DP_FEA_FINAL, help="Absolute P at FEA ramp end [mmHg]")
    ap.add_argument("--ne", type=int, default=8)
    ap.add_argument("--max-nfev", type=int, default=30)
    ap.add_argument("--R", type=float, default=12.0)
    ap.add_argument("--t", type=float, default=0.5)
    ap.add_argument("--out", type=Path, default=Path(env_out))
    args = ap.parse_args()

    targets = [t.strip() for t in args.targets.split(",") if t.strip()]
    materials = [m.strip() for m in args.materials.split(",") if m.strip()]
    args.out.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []
    for target in targets:
        for material in materials:
            tag = f"{target}_{material}"
            out = args.out / tag
            print(f"\n{'='*60}\n{tag} (P_final={args.p_final} mmHg)\n{'='*60}")
            payload = run_one(
                target,
                material,
                out,
                ne=args.ne,
                max_nfev=args.max_nfev,
                p_final=args.p_final,
                R=args.R,
                t=args.t,
            )
            results.append(payload)

    write_summary(args.out, results)
    print(f"\nDone — see {args.out / 'LITERATURE_MATRIX_SUMMARY.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
