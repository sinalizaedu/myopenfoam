#!/usr/bin/env python3
"""Run WP1.2–1.3 in parallel material tracks: ogden and yeoh.

WP1.1 is linear-only (material-independent); see wp1.1/scripts/run_verification_octant.py.

Outputs under wp1_octant/output/wp1.{2,3}-{ogden,yeoh}/
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WP12_SCRIPTS = ROOT / "wp1.2" / "scripts"
WP13_SCRIPTS = ROOT / "wp1.3" / "scripts"
OUT_ROOT = Path(__file__).resolve().parents[1] / "output"
WP11_LINEAR_OUT = ROOT / "wp1.1" / "output_octant"


def run(cmd: list[str], label: str) -> None:
    print(f"\n{'='*60}\n{label}\n{'='*60}")
    subprocess.run(cmd, check=True)


def wp12_ogden(out: Path, ne: int, max_nfev: int) -> None:
    run(
        [
            sys.executable,
            str(WP12_SCRIPTS / "fit_pallikaris.py"),
            "--ne",
            str(ne),
            "--max-nfev",
            str(max_nfev),
            "--out",
            str(out),
        ],
        "WP1.2 Ogden fit",
    )


def wp12_yeoh(out: Path, ne: int, max_nfev: int, repro: int) -> None:
    run(
        [
            sys.executable,
            str(WP12_SCRIPTS / "run_e3_e1b.py"),
            "--ne",
            str(ne),
            "--max-nfev",
            str(max_nfev),
            "--repro-trials",
            str(repro),
            "--skip-e1b",
            "--out",
            str(out),
        ],
        "WP1.2 Yeoh fit (E3)",
    )


def wp13_mulf_gee(
    fit_json: Path,
    out: Path,
    material: str,
    ne: int,
    n_steps: int,
    max_iter: int,
) -> None:
    run(
        [
            sys.executable,
            str(WP13_SCRIPTS / "run_wp13_mulf_gee.py"),
            "--fit",
            str(fit_json),
            "--material",
            material,
            "--ne",
            str(ne),
            "--n-steps",
            str(n_steps),
            "--max-iter",
            str(max_iter),
            "--out",
            str(out),
        ],
        f"WP1.3 MULF Gee ({material})",
    )


def write_wp12_results_md(out: Path, mat: str) -> None:
    fit = json.loads((out / "fit_results.json").read_text())
    sel = fit.get("selected") or fit.get("fit")
    q = sel["quality"]
    p = sel["params"]
    lines = [
        f"# wp1.2-{mat} — Pallikaris fit\n",
        f"- **Model**: {sel.get('model', mat)}",
        f"- **Parameters**: {json.dumps(p)}",
        f"- **R²**: {q['R2']:.6f}",
        f"- **Max residual**: {q['max_residual_mmHg']:.2f} mmHg",
    ]
    if "optimizer" in sel:
        lines.append(f"- **nfev**: {sel['optimizer']['nfev']}")
    if "isolated_repro" in fit:
        ok = sum(1 for r in fit["isolated_repro"] if r["status"] == "OK")
        lines.append(f"- **Isolated repro**: {ok}/{len(fit['isolated_repro'])} OK")
    (out / "RESULTS.md").write_text("\n".join(lines) + "\n")


def _convergence_status(wp: str, path: Path) -> str:
    if wp == "wp1.2":
        fit = path / "fit_results.json"
        if not fit.is_file():
            return "MISSING"
        data = json.loads(fit.read_text())
        sel = data.get("selected") or data.get("fit")
        ok = bool(sel.get("optimizer", {}).get("success", True))
        return "OK" if ok else "FAIL"
    if wp == "wp1.3":
        mulf = path / "pretension_mulf_gee.json"
        if mulf.is_file():
            data = json.loads(mulf.read_text())
            if data.get("mulf", {}).get("converged"):
                return "OK"
            return "FAIL"
        return "MISSING"
    return "?"


def write_summary(tracks: dict[str, dict]) -> None:
    wp11_status = "OK" if (WP11_LINEAR_OUT / "summary.json").is_file() else "MISSING"
    lines = [
        "# WP1 material matrix — ogden vs yeoh (octant)\n",
        "WP1.1 is **linear only** (material-independent). See "
        f"`{WP11_LINEAR_OUT.relative_to(OUT_ROOT.parent)}`.",
        "",
        f"| Track | WP1.1 (linear, shared) | WP1.2 | WP1.3 (MULF) |",
        f"|---|---|---|---|",
    ]
    for tag, info in tracks.items():
        cols = [_convergence_status(wp, info[wp]) for wp in ("wp1.2", "wp1.3")]
        lines.append(f"| {tag} | {wp11_status} | {' | '.join(cols)} |")
    lines.append("")

    for tag, info in tracks.items():
        lines.append(f"## {tag}\n")
        for wp, path in info.items():
            res = path / "RESULTS.md"
            lines.append(
                f"- **{wp}** [{_convergence_status(wp, path)}]: "
                f"`{path.relative_to(OUT_ROOT.parent)}`"
            )
            if res.is_file():
                first = res.read_text().splitlines()[0:10]
                lines.extend(["  ```"] + first + ["  ```"])
        lines.append("")
    (OUT_ROOT / "MATERIAL_MATRIX_SUMMARY.md").write_text("\n".join(lines) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ne", type=int, default=8)
    ap.add_argument("--max-nfev", type=int, default=30)
    ap.add_argument("--repro", type=int, default=3, help="Yeoh isolated repro trials")
    ap.add_argument("--skip-wp12", action="store_true")
    ap.add_argument("--skip-wp13", action="store_true")
    ap.add_argument("--wp13-n-steps", type=int, default=24, help="loading curve points above P0")
    ap.add_argument("--mulf-max-iter", type=int, default=12, help="Gee MULF fixed-point iterations")
    ap.add_argument("--only", choices=["ogden", "yeoh", ""], default="")
    args = ap.parse_args()

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    materials = ["ogden", "yeoh"]
    if args.only:
        materials = [args.only]

    tracks: dict[str, dict] = {}

    for mat in materials:
        tag = f"wp1-{mat}"
        o12 = OUT_ROOT / f"wp1.2-{mat}"
        o13 = OUT_ROOT / f"wp1.3-{mat}"
        for p in (o12, o13):
            p.mkdir(parents=True, exist_ok=True)
        tracks[tag] = {"wp1.2": o12, "wp1.3": o13}

        if not args.skip_wp12:
            if mat == "ogden":
                wp12_ogden(o12, args.ne, args.max_nfev)
            else:
                wp12_yeoh(o12, args.ne, args.max_nfev, args.repro)
            write_wp12_results_md(o12, mat)

        fit_json = o12 / "fit_results.json"
        if not fit_json.is_file():
            print(f"Missing {fit_json}")
            return 1

        if not args.skip_wp13:
            wp13_mulf_gee(fit_json, o13, mat, args.ne, args.wp13_n_steps, args.mulf_max_iter)

    write_summary(tracks)
    print(f"\nDone — see {OUT_ROOT / 'MATERIAL_MATRIX_SUMMARY.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
