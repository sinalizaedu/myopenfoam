#!/usr/bin/env python3
"""Mesh-independence study for WP1.2 hyperelastic NLGEOM forward runs.

Uses final fitted material parameters from the literature matrix (no re-fit).
QoI: ΔV(P) along the 16-step ramp; primary scalar = ΔV at P_final.

Refinement: ne ∈ {6, 8, 10, 12} on spherical octant (S8R, symmetry BCs).
Stop criterion: ε_i = |ΔV_i − ΔV_{i−1}|/|ΔV_i| < 1% for two consecutive refinements.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
WP12 = HERE.parent
WP1 = WP12.parent / "wp1.1" / "scripts"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(WP1))

from ccx_utils import ccx_bin, run_ccx  # noqa: E402
from extract_pv_curve import extract_pv  # noqa: E402
from fit_pallikaris import DP_FEA_FINAL, Geometry, P0_MMHG, PallikarisForward  # noqa: E402
from gen_sphere_shell_mesh import write_mesh  # noqa: E402
from run_e3_e1b import PallikarisYeohForward  # noqa: E402
from write_deck import write_deck  # noqa: E402

NE_LEVELS = (6, 8, 10, 12)
EPS_TARGET = 0.01
DEFAULT_FIT_ROOT = WP12 / "output_literature_p50_digitized"
DEFAULT_OUT = WP12 / "output_mesh_independence"

CASES = (
    "friedenwald_ogden",
    "friedenwald_yeoh",
    "pallikaris_ogden",
    "pallikaris_yeoh",
    "silver_ogden",
    "silver_yeoh",
)


def n_octant_elements(ne: int) -> int:
    return ne * ne


def h_char_mm(R_mm: float, ne: int) -> float:
    """Characteristic arc length on octant (θ,φ grid)."""
    return math.pi * R_mm / (2.0 * ne)


def load_case(fit_path: Path) -> dict:
    data = json.loads(fit_path.read_text())
    sel = data["selected"]
    geom = data.get("geometry") or {}
    ramp = data.get("fea_ramp") or {}
    return {
        "name": f"{data['target']}_{data['material']}",
        "target": data["target"],
        "material": data["material"],
        "model": sel["model"],
        "params": dict(sel["params"]),
        "R_mm": float(geom.get("R_mm", 12.0)),
        "t_mm": float(geom.get("t_mm", 0.5)),
        "nu": float(geom.get("nu", 0.47)),
        "E_mpa": float(geom.get("E_mpa", 3.0)),
        "p_final": float(ramp.get("P_final_mmHg_abs", DP_FEA_FINAL)),
        "p0": float(ramp.get("P0_mmHg", P0_MMHG)),
        "fit_ne": int(data.get("mesh", {}).get("ne", 8)),
        "fit_path": fit_path,
    }


def run_forward(case: dict, ne: int, work: Path) -> list[dict]:
    """Forward NLGEOM run at fixed params; return extract_pv rows."""
    work.mkdir(parents=True, exist_ok=True)
    material = case["material"]
    params = case["params"]
    p_final = case["p_final"]
    p0 = case["p0"]
    R, t = case["R_mm"], case["t_mm"]

    if material == "ogden":
        geom = Geometry(R_mm=R, t_mm=t, source=f"{case['target']}_mesh_ind")
        fwd = PallikarisForward(geom, work, ne=ne, dp_fea_final=p_final, p0_mmhg=p0)
        mu1, alpha1 = params["mu1_MPa"], params["alpha1"]
        deck = work / "mesh_ind.inp"
        # PallikarisForward.run writes deck; reuse its logic via run()
        fwd.run(mu1, alpha1, tag="mesh_ind")
    elif material == "yeoh":
        fwd = PallikarisYeohForward(work, ne=ne, p_final=p_final)
        fwd.geom = Geometry(R_mm=R, t_mm=t, source=f"{case['target']}_mesh_ind")
        c10, c20 = params["C10_MPa"], params["C20_MPa"]
        fwd.run(c10, c20, tag="mesh_ind")
        deck = work / "mesh_ind.inp"
    else:
        raise ValueError(material)

    frd = work / "mesh_ind.frd"
    if not frd.is_file():
        frd = run_ccx(deck, clean=False)
    return extract_pv(deck, frd, R, p0_mmhg=p0)


def summarize_pv(rows: list[dict], p0: float) -> dict:
    dv = np.array([r["dV_uL"] for r in rows], dtype=float)
    p = np.array([r["p_mmhg"] for r in rows], dtype=float)
    dp = p - p0
    dv_final = float(dv[-1]) if len(dv) else float("nan")
    dp_final = float(dp[-1]) if len(dp) else float("nan")
    k_sec = dp_final / dv_final if abs(dv_final) > 1e-12 else float("nan")
    return {
        "dV_final_uL": dv_final,
        "dp_final_mmHg": dp_final,
        "K_sec_mmHg_per_uL": k_sec,
        "n_steps": len(rows),
        "dV_curve_uL": dv.tolist(),
        "p_abs_mmHg": p.tolist(),
    }


def max_stepwise_rel_diff(curve_a: list[float], curve_b: list[float]) -> float:
    n = min(len(curve_a), len(curve_b))
    if n == 0:
        return float("nan")
    diffs = []
    for i in range(n):
        ref = abs(curve_a[i])
        if ref < 1e-12:
            continue
        diffs.append(abs(curve_a[i] - curve_b[i]) / ref)
    return float(max(diffs)) * 100.0 if diffs else float("nan")


def recommend_level(rows: list[dict]) -> dict:
    for i in range(1, len(rows) - 1):
        e1, e2 = rows[i].get("eps_dV_final_pct"), rows[i + 1].get("eps_dV_final_pct")
        if e1 is None or e2 is None:
            continue
        if e1 < EPS_TARGET * 100 and e2 < EPS_TARGET * 100:
            ne = rows[i]["ne"]
            return {
                "ne": ne,
                "reason": (
                    f"ε({rows[i-1]['ne']}→{ne})={e1:.3f}% and "
                    f"ε({ne}→{rows[i+1]['ne']})={e2:.3f}% both < {EPS_TARGET*100:.0f}%"
                ),
            }
    return {"ne": None, "reason": "criterion not met on any pair of consecutive refinements"}


def run_case_study(case: dict, out_root: Path, ne_levels: tuple[int, ...]) -> dict:
    name = case["name"]
    case_dir = out_root / name
    case_dir.mkdir(parents=True, exist_ok=True)
    R = case["R_mm"]

    print(f"\n{'='*60}\nCase: {name}  (fit at ne={case['fit_ne']})\n{'='*60}")

    rows: list[dict] = []
    for ne in ne_levels:
        work = case_dir / f"ne_{ne}"
        t0 = time.perf_counter()
        print(f"  ne={ne}  (octant elems={n_octant_elements(ne)}, full-equiv={8*n_octant_elements(ne)})")
        try:
            pv_rows = run_forward(case, ne, work)
            summary = summarize_pv(pv_rows, case["p0"])
            status = "OK"
        except Exception as exc:
            summary = {"dV_final_uL": float("nan"), "dV_curve_uL": [], "K_sec_mmHg_per_uL": float("nan")}
            status = f"FAIL: {exc}"
            print(f"    ERROR: {exc}")

        elapsed = time.perf_counter() - t0
        row = {
            "case": name,
            "ne": ne,
            "n_octant_elements": n_octant_elements(ne),
            "n_full_equiv": 8 * n_octant_elements(ne),
            "h_char_mm": h_char_mm(R, ne),
            "status": status,
            "time_s": elapsed,
            **{k: v for k, v in summary.items() if k != "dV_curve_uL"},
        }
        row["dV_curve_uL"] = summary.get("dV_curve_uL", [])
        rows.append(row)
        if status == "OK":
            print(f"    ΔV_final={row['dV_final_uL']:.4f} µL  K_sec={row['K_sec_mmHg_per_uL']:.4f}  t={elapsed:.1f}s")

    for i, row in enumerate(rows):
        if i == 0 or row["status"] != "OK" or rows[i - 1]["status"] != "OK":
            row["eps_dV_final_pct"] = None
            row["eps_max_step_pct"] = None
            row["eps_label"] = "—"
        else:
            cur = row["dV_final_uL"]
            prev = rows[i - 1]["dV_final_uL"]
            eps = 100.0 * abs(cur - prev) / abs(cur) if abs(cur) > 1e-12 else float("nan")
            row["eps_dV_final_pct"] = eps
            row["eps_max_step_pct"] = max_stepwise_rel_diff(
                rows[i - 1]["dV_curve_uL"], row["dV_curve_uL"]
            )
            row["eps_label"] = f"{eps:.3f}"

    # ne=6 vs ne=8 spot check (production vs multistart default)
    ne6 = next((r for r in rows if r["ne"] == 6 and r["status"] == "OK"), None)
    ne8 = next((r for r in rows if r["ne"] == 8 and r["status"] == "OK"), None)
    ne6_vs_8 = {}
    if ne6 and ne8:
        dv6, dv8 = ne6["dV_final_uL"], ne8["dV_final_uL"]
        ne6_vs_8 = {
            "dV6_uL": dv6,
            "dV8_uL": dv8,
            "abs_diff_uL": abs(dv8 - dv6),
            "rel_diff_pct": 100.0 * abs(dv8 - dv6) / abs(dv8) if abs(dv8) > 1e-12 else float("nan"),
            "max_step_rel_pct": max_stepwise_rel_diff(ne6["dV_curve_uL"], ne8["dV_curve_uL"]),
        }

    rec = recommend_level(rows)
    study = {
        "case": name,
        "material": case["material"],
        "target": case["target"],
        "fit_ne": case["fit_ne"],
        "params": case["params"],
        "R_mm": R,
        "t_mm": case["t_mm"],
        "p_final_mmHg": case["p_final"],
        "rows": [{k: v for k, v in r.items()} for r in rows],
        "ne6_vs_ne8": ne6_vs_8,
        "recommend": rec,
    }

    write_case_report(study, case_dir)
    (case_dir / "results.json").write_text(json.dumps(study, indent=2))
    return study


def write_case_report(study: dict, case_dir: Path) -> None:
    lines = [
        f"# wp1.2 — independência de malha ({study['case']})\n",
        f"Material: **{study['material']}** ({study['target']}). "
        f"Forward NLGEOM com parâmetros fixos do fit (ne={study['fit_ne']}).\n",
        f"QoI primário: **ΔV_final** @ P={study['p_final_mmHg']:.1f} mmHg. "
        f"Critério: ε_i < {EPS_TARGET*100:.0f}% em dois refinamentos consecutivos.\n",
        "| ne | octant elems | full-equiv | h_char (mm) | ΔV_final (µL) | K_sec (mmHg/µL) | ε vs anterior (%) | max ε passo (%) | t (s) | status |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in study["rows"]:
        k = r.get("K_sec_mmHg_per_uL", float("nan"))
        lines.append(
            f"| {r['ne']} | {r['n_octant_elements']} | {r['n_full_equiv']} | "
            f"{r['h_char_mm']:.4f} | {r.get('dV_final_uL', float('nan')):.4f} | "
            f"{k:.4f} | {r.get('eps_label', '—')} | "
            f"{r.get('eps_max_step_pct') or '—'} | {r['time_s']:.1f} | {r['status']} |"
        )

    n68 = study.get("ne6_vs_ne8") or {}
    if n68:
        lines.extend(
            [
                "\n## Checagem ne=6 vs ne=8 (multistart vs produção)\n",
                f"- ΔV_final(ne=6) = **{n68['dV6_uL']:.4f}** µL",
                f"- ΔV_final(ne=8) = **{n68['dV8_uL']:.4f}** µL",
                f"- |Δ| = **{n68['abs_diff_uL']:.4f}** µL (**{n68['rel_diff_pct']:.3f}%** relativo a ne=8)",
                f"- max ε ao longo da rampa: **{n68['max_step_rel_pct']:.3f}%**",
            ]
        )

    rec = study["recommend"]
    lines.append("\n## Recomendação\n")
    if rec["ne"]:
        lines.append(f"ne = **{rec['ne']}**: {rec['reason']}.")
    else:
        lines.append(f"Critério **não atingido**: {rec['reason']}.")

    (case_dir / "MESH_INDEPENDENCE.md").write_text("\n".join(lines))


def write_summary(studies: list[dict], out_root: Path) -> None:
    lines = [
        "# wp1.2 — estudo de independência de malha (6 casos literatura)\n",
        "Forward NLGEOM hiperelástico (Ogden/Yeoh), parâmetros fixos do fit em `output_literature_p50_digitized/`.\n",
        f"Refinamento: ne ∈ {list(NE_LEVELS)}. Critério: ε(ΔV_final) < {EPS_TARGET*100:.0f}% "
        "em dois níveis consecutivos.\n",
        "## Resumo ne=6 vs ne=8\n",
        "| caso | ΔV@ne=6 (µL) | ΔV@ne=8 (µL) | |Δ| (µL) | rel (%) | max ε passo (%) | OK (<1%)? |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    all_ok_68 = True
    for s in studies:
        n = s.get("ne6_vs_ne8") or {}
        if not n:
            lines.append(f"| {s['case']} | — | — | — | — | — | — |")
            continue
        ok = "sim" if n["rel_diff_pct"] < 1.0 else "**NÃO**"
        if n["rel_diff_pct"] >= 1.0:
            all_ok_68 = False
        lines.append(
            f"| {s['case']} | {n['dV6_uL']:.4f} | {n['dV8_uL']:.4f} | "
            f"{n['abs_diff_uL']:.4f} | {n['rel_diff_pct']:.3f} | {n['max_step_rel_pct']:.3f} | {ok} |"
        )

    lines.extend(["\n## Recomendação por caso\n", "| caso | ne recomendado | motivo |", "|---|---:|---|"])
    for s in studies:
        rec = s["recommend"]
        ne = rec["ne"] if rec["ne"] else "—"
        lines.append(f"| {s['case']} | {ne} | {rec['reason']} |")

    lines.append("\n## Conclusão\n")
    if all_ok_68:
        lines.append(
            "A diferença **ne=6 vs ne=8** fica abaixo de **1%** em ΔV_final para todos os 6 casos. "
            "O uso misto de ne=6 (multistart/dev) e ne=8 (matriz final) **não altera** o resultado de forma material."
        )
    else:
        lines.append(
            "⚠ Pelo menos um caso excede **1%** entre ne=6 e ne=8 — revisar antes de misturar malhas entre rodadas."
        )

    (out_root / "MESH_INDEPENDENCE.md").write_text("\n".join(lines))
    (out_root / "summary.json").write_text(
        json.dumps({s["case"]: {k: v for k, v in s.items() if k != "rows"} for s in studies}, indent=2)
    )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fit-root", type=Path, default=DEFAULT_FIT_ROOT)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--cases", default=",".join(CASES), help="Comma-separated case folder names")
    p.add_argument("--ne-levels", default=",".join(str(n) for n in NE_LEVELS))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    ne_levels = tuple(int(x.strip()) for x in args.ne_levels.split(",") if x.strip())
    case_names = [c.strip() for c in args.cases.split(",") if c.strip()]
    args.out.mkdir(parents=True, exist_ok=True)

    print(f"CalculiX: {ccx_bin()}")
    print(f"Fit root: {args.fit_root}")
    print(f"Cases: {', '.join(case_names)}")
    print(f"ne levels: {ne_levels}")

    studies: list[dict] = []
    for name in case_names:
        fit_path = args.fit_root / name / "fit_results.json"
        if not fit_path.is_file():
            print(f"SKIP {name}: missing {fit_path}", file=sys.stderr)
            continue
        case = load_case(fit_path)
        studies.append(run_case_study(case, args.out, ne_levels))

    if not studies:
        print("No cases run.", file=sys.stderr)
        return 1

    write_summary(studies, args.out)
    print(f"\nWrote {args.out}/MESH_INDEPENDENCE.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
