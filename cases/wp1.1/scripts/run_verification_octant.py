#!/usr/bin/env python3
"""wp1.1 — linear K verification on spherical octant (θ,φ) with symmetry BCs."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WP1_1 = HERE.parent
CCX_DIR = WP1_1 / "ccx"
OUT = WP1_1 / "output_octant"

sys.path.insert(0, str(HERE))
from extract_K import K_analytic_mmHg_per_uL, extract  # noqa: E402
from gen_sphere_shell_mesh import write_mesh  # noqa: E402

MMHG_TO_MPA = 133.322e-6
CASES = {
    "human": {"R": 12.0, "t": 0.5},
    "rabbit": {"R": 7.6, "t": 0.33},
}
E_MPA = 3.0
NU = 0.47
DP_MMHG = 1.0
# ne divisions per θ/φ → octant elems = ne², full-sphere equiv = 8·ne²
CONVERGENCE_LEVELS = (3, 6, 12, 24)
NE_RECOMMENDED = 6  # 288 full-sphere equivalent elements


def ccx_bin() -> str:
    for name in ("ccx", "ccx_preCICE", "ccx_2.23", "ccx_2.21", "ccx_2.20"):
        p = shutil.which(name)
        if p:
            return p
    for p in ("/opt/calculix/bin/ccx_preCICE", "/opt/homebrew/bin/ccx_2.23"):
        if Path(p).is_file():
            return p
    raise RuntimeError("CalculiX (ccx) not found in PATH")


def write_deck(
    deck: Path,
    mesh_name: str,
    R_mm: float,
    t_mm: float,
    dP_mmHg: float,
    case_label: str,
) -> None:
    p_mpa = dP_mmHg * MMHG_TO_MPA
    K_an = K_analytic_mmHg_per_uL(R_mm, t_mm, E_MPA, NU)
    text = f"""*HEADING
wp1.1 octant K verification — {case_label}
** Units: mm, N, MPa. Linear static (NLGEOM=NO).
** Geometry: R={R_mm} mm, t={t_mm} mm, spherical octant (θ,φ), S8R
** Symmetry BCs on x=0, y=0, z=0 planes; volume_scale=8 in post
** K_analytic ≈ {K_an:.6f} mmHg/µL
** Load: uniform internal pressure ΔP={dP_mmHg} mmHg on INNER_SURF
*INCLUDE, INPUT={mesh_name}
*MATERIAL, NAME=SHELL_MAT
*ELASTIC
{E_MPA:.6f}, {NU:.6f}
*SHELL SECTION, ELSET=SHELL, MATERIAL=SHELL_MAT
{t_mm:.6f}
*STEP, NAME=PRESSURE, NLGEOM=NO, INC=10
*STATIC
1.0, 1.0, 1e-6, 1.0
*BOUNDARY
SYM_X, 1, 1, 0.0
SYM_Y, 2, 2, 0.0
SYM_Z, 3, 3, 0.0
*DSLOAD
INNER_SURF, P, {p_mpa:.12e}
*NODE FILE
U
*END STEP
"""
    deck.write_text(text)


def run_ccx(deck: Path) -> Path:
    ccx = ccx_bin()
    work = deck.parent
    stem = deck.stem
    env = os.environ.copy()
    env.setdefault("OMP_NUM_THREADS", str(os.cpu_count() or 4))
    log = work / f"log_{stem}.txt"
    with open(log, "w") as fh:
        subprocess.run(
            [ccx, "-i", stem],
            cwd=work,
            check=True,
            stdout=fh,
            stderr=subprocess.STDOUT,
            env=env,
        )
    frd = work / f"{stem}.frd"
    if not frd.is_file():
        raise RuntimeError(f"Missing {frd}; see {log}")
    return frd


def run_case(name: str, ne: int, dP_mmHg: float = DP_MMHG, tag_suffix: str = "") -> dict:
    geom = CASES[name]
    R, t = geom["R"], geom["t"]
    tag = f"oct_ne{ne}{tag_suffix}"
    mesh = CCX_DIR / f"{name}_oct_ne{ne}_mesh.inp"
    deck = CCX_DIR / f"{name}_{tag}.inp"

    write_mesh(
        mesh,
        R,
        t,
        ne,
        2,
        label=f"{name} spherical octant ne={ne}",
        bc_mode="symmetry_octant",
        mesh_kind="spherical",
        theta_min_deg=3.0,
        reduced=True,
    )
    write_deck(deck, mesh.name, R, t, dP_mmHg, f"{name} ({tag})")

    for ext in (".frd", ".sta", ".cvg", ".dat", ".12d"):
        p = CCX_DIR / f"{name}_{tag}{ext}"
        if p.exists():
            p.unlink()

    frd = run_ccx(deck)
    res = extract(deck, frd, R, t, E_MPA, NU)
    res.update(
        {
            "case": name,
            "mesh_tag": tag,
            "ne": ne,
            "full_sphere_equiv_elements": ne * ne * 8,
            "dP_mmHg": dP_mmHg,
            "deck": str(deck),
        }
    )
    return res


def mesh_independence_epsilon(rows: list[dict]) -> list[dict]:
    """Relative change in K between successive mesh levels."""
    out: list[dict] = []
    for i, row in enumerate(rows):
        if i == 0:
            out.append({**row, "epsilon_i_pct": float("nan")})
            continue
        k_prev = rows[i - 1]["K_FEA_mmHg_per_uL"]
        k_cur = row["K_FEA_mmHg_per_uL"]
        eps_i = 100.0 * abs(k_cur - k_prev) / k_cur if abs(k_cur) > 1e-20 else float("nan")
        out.append({**row, "epsilon_i_pct": eps_i})
    return out


def run_linearity(case: str) -> dict:
    """Phalf/Pfull at recommended mesh (ne=6, 288 full-sphere equiv elements)."""
    print(f"\n=== {case} linearity (ne={NE_RECOMMENDED}) ===")
    r_half = run_case(case, NE_RECOMMENDED, dP_mmHg=0.5 * DP_MMHG, tag_suffix="_Phalf")
    r_full = run_case(case, NE_RECOMMENDED, dP_mmHg=DP_MMHG, tag_suffix="")
    ratio = r_full["dV_uL"] / r_half["dV_uL"] if abs(r_half["dV_uL"]) > 1e-20 else float("nan")
    lin = {
        "case": case,
        "ne": NE_RECOMMENDED,
        "full_sphere_equiv_elements": NE_RECOMMENDED * NE_RECOMMENDED * 8,
        "dV_half_uL": r_half["dV_uL"],
        "dV_full_uL": r_full["dV_uL"],
        "volume_ratio": ratio,
        "linear_ok": abs(ratio - 2.0) < 0.02,
    }
    print(f"  dV ratio (2x load) = {ratio:.4f}  linear={'OK' if lin['linear_ok'] else 'FAIL'}")
    return lin


def format_results_md(case: str, rows: list[dict], lin: dict | None = None) -> str:
    geom = CASES[case]
    lines = [
        f"# wp1.1 octant — K verification ({case})\n",
        f"Geometria: R={geom['R']} mm, t={geom['t']} mm. "
        f"Malha esférica (θ,φ), S8R, θ_min=3°, simetria nos 3 planos.\n",
        "| elem (full eq.) | K_FEA | ε_i (%) | erro vs analítico (%) |",
        "|---:|---:|---:|---:|",
    ]
    for r in rows:
        eps = r.get("epsilon_i_pct", float("nan"))
        eps_s = "—" if eps != eps else f"{eps:.4f}"
        lines.append(
            f"| {r['full_sphere_equiv_elements']} | {r['K_FEA_mmHg_per_uL']:.6f} | "
            f"{eps_s} | {r['error_pct']:.2f} |"
        )
    final = next((r for r in rows if r["ne"] == NE_RECOMMENDED), rows[-1])
    lines.extend(
        [
            f"\nK_analítico: {final['K_analytic_mmHg_per_uL']:.6f} mmHg/µL\n",
            f"Erro @ ne={final['ne']} (≈{final['full_sphere_equiv_elements']} elem): "
            f"**{final['error_pct']:+.2f}%**\n",
        ]
    )
    if lin is not None:
        lines.extend(
            [
                f"\n## Linearidade (ne={NE_RECOMMENDED}, ≈{lin['full_sphere_equiv_elements']} elem)\n",
                "| ΔV @0.5 mmHg | ΔV @1.0 mmHg | razão |",
                "|---:|---:|---:|",
                f"| {lin['dV_half_uL']:.6f} | {lin['dV_full_uL']:.6f} | {lin['volume_ratio']:.4f} |",
            ]
        )
    return "\n".join(lines) + "\n"


def publish_report_decks(cases: tuple[str, ...], ne: int = NE_RECOMMENDED) -> None:
    """Copy ne=6 octant decks to ccx/{case}_wp1.1.inp (deliverables cited in wp1.tex)."""
    for case in cases:
        mesh_src = CCX_DIR / f"{case}_oct_ne{ne}_mesh.inp"
        deck_src = CCX_DIR / f"{case}_oct_ne{ne}.inp"
        mesh_dst = CCX_DIR / f"{case}_wp1.1_mesh.inp"
        deck_dst = CCX_DIR / f"{case}_wp1.1.inp"
        if not deck_src.is_file() or not mesh_src.is_file():
            continue
        shutil.copy2(mesh_src, mesh_dst)
        deck_dst.write_text(deck_src.read_text().replace(mesh_src.name, mesh_dst.name))


def write_combined_results(
    case_rows: dict[str, list[dict]],
    linearity: list[dict],
) -> None:
    """Single RESULTS.md under output_wp1.1/ (report-style octant verification)."""
    out_dir = WP1_1 / "output_wp1.1"
    out_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# wp1.1 — verificação FEA (octante, wp1.tex)\n",
        "Geometria: octante esférico (θ,φ) com simetria em x=0, y=0, z=0; "
        f"ΔV integrado no octante × 8. Malha de referência: **ne={NE_RECOMMENDED}** "
        f"(**{NE_RECOMMENDED * NE_RECOMMENDED * 8}** elementos equivalentes na esfera). "
        "NLGEOM=NO, ΔP=1 mmHg.\n",
    ]
    for case in case_rows:
        rows = case_rows[case]
        geom = CASES[case]
        lines.append(f"\n## {case} (R={geom['R']} mm, t={geom['t']} mm)\n")
        lines.append("| elem (full eq.) | K_FEA | ε_i (%) | erro (%) |")
        lines.append("|---:|---:|---:|---:|")
        for r in rows:
            eps = r.get("epsilon_i_pct", float("nan"))
            eps_s = "—" if eps != eps else f"{eps:.4f}"
            lines.append(
                f"| {r['full_sphere_equiv_elements']} | {r['K_FEA_mmHg_per_uL']:.6f} | "
                f"{eps_s} | {r['error_pct']:+.2f} |"
            )
        lin = next(x for x in linearity if x["case"] == case)
        final = next(r for r in rows if r["ne"] == NE_RECOMMENDED)
        lines.append(
            f"\nErro @ malha de referência (≈288 elem humano / coelho na tabela do relatório): "
            f"**{final['error_pct']:+.2f}%**. "
            f"Linearidade (razão ΔV): **{lin['volume_ratio']:.4f}**.\n"
        )
    lines.append("\nDetalhe por espécie: `output_octant/RESULTS_human.md`, `RESULTS_rabbit.md`.\n")
    (out_dir / "RESULTS.md").write_text("\n".join(lines))
    summary_src = OUT / "summary.json"
    if summary_src.is_file():
        shutil.copy2(summary_src, out_dir / "summary.json")


def load_theta_min_sensitivity() -> dict:
    src = WP1_1.parent / "claude-wp1.1" / "output" / "results.json"
    if not src.is_file():
        return {"source": str(src), "note": "claude-wp1.1 theta_min sweep not found", "results": []}
    return {
        "source": str(src),
        "note": "ne=6 (288 full-sphere equiv), S8R, NLGEOM=NO, theta_min sweep 1/3/5 deg",
        "results": json.loads(src.read_text()),
    }


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="WP1.1 octant K verification (wp1.tex)")
    parser.add_argument(
        "cases",
        nargs="*",
        choices=("human", "rabbit"),
        help="species to run (default: both)",
    )
    args = parser.parse_args(argv)
    run_cases = tuple(args.cases) if args.cases else ("human", "rabbit")

    CCX_DIR.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"CalculiX: {ccx_bin()}")

    all_rows: list[dict] = []
    linearity: list[dict] = []
    case_rows: dict[str, list[dict]] = {}

    for case in run_cases:
        print(f"\n=== {case} mesh independence (spherical octant) ===")
        rows: list[dict] = []
        for ne in CONVERGENCE_LEVELS:
            print(f"  ne={ne} (full equiv {ne*ne*8} elements)...")
            rows.append(run_case(case, ne))
        rows = mesh_independence_epsilon(rows)
        all_rows.extend(rows)
        case_rows[case] = rows
        linearity.append(run_linearity(case))

    for case in run_cases:
        lin = next(x for x in linearity if x["case"] == case)
        md = format_results_md(case, case_rows[case], lin)
        (OUT / f"RESULTS_{case}.md").write_text(md)
        print(md)

    publish_report_decks(run_cases, ne=NE_RECOMMENDED)

    theta_min = load_theta_min_sensitivity()
    (OUT / "theta_min_sensitivity.json").write_text(json.dumps(theta_min, indent=2))

    summary = {
        "mesh_kind": "spherical_octant",
        "bc_mode": "symmetry_octant",
        "theta_min_deg": 3.0,
        "gauss_order": 3,
        "convergence_levels": list(CONVERGENCE_LEVELS),
        "ne_recommended": NE_RECOMMENDED,
        "full_sphere_equiv_reference": NE_RECOMMENDED * NE_RECOMMENDED * 8,
        "results": all_rows,
        "linearity": linearity,
        "theta_min_sensitivity": theta_min,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))

    if len(run_cases) == 2:
        write_combined_results(case_rows, linearity)

    ok = all(abs(r["error_pct"]) < 2.0 for r in all_rows if r["ne"] == NE_RECOMMENDED)
    ok = ok and all(l["linear_ok"] for l in linearity)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
