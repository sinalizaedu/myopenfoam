#!/usr/bin/env python3
"""wp1.1 — thin spherical shell K verification (CalculiX vs analytic).

Generates meshes and .inp decks, runs ccx/ccx_preCICE, mesh convergence,
linearity check, and writes summary tables.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
WP1_1 = HERE.parent
CCX_DIR = WP1_1 / "ccx"
OUT = WP1_1 / "output_wp1.1"

sys.path.insert(0, str(HERE))
from extract_K import K_analytic_mmHg_per_uL, extract  # noqa: E402
from gen_sphere_shell_mesh import write_mesh  # noqa: E402

MMHG_TO_MPA = 133.322e-6  # N/mm²

CASES = {
    "human": {"R": 12.0, "t": 0.5},
    "rabbit": {"R": 7.6, "t": 0.33},
}
E_MPA = 3.0
NU = 0.47
DP_MMHG = 1.0
NE_BASE = 6
NE_MID = 12
NE_COARSE_INDEP = 24  # extra level for convergence table (mesh-independence study)
NE_FINE = 12  # deliverable mesh (864 elements; KDTree mapping)
CONVERGENCE_LEVELS = (NE_BASE, NE_MID, NE_COARSE_INDEP)


def ccx_bin() -> str:
    for name in ("ccx", "ccx_preCICE", "ccx_2.23", "ccx_2.21", "ccx_2.20"):
        p = shutil.which(name)
        if p:
            return p
    for p in (
        "/opt/calculix/bin/ccx_preCICE",
        "/opt/homebrew/bin/ccx_2.23",
    ):
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
wp1.1 thin spherical shell verification — {case_label}
** Code verification: compare K_FEA=ΔP/ΔV vs K_analytic = t*E/(2*pi*R^4*(1-nu))
** Units: mm, N, MPa (N/mm²). Linear static (NLGEOM=NO).
** Geometry: R={R_mm} mm mean radius, t={t_mm} mm, full closed sphere (S8 shell)
** Material: E={E_MPA} MPa, nu={NU}
** K_analytic ≈ {K_an:.6f} mmHg/µL (reference only; do not tune mesh/material to match)
** Load: uniform internal pressure ΔP={dP_mmHg} mmHg on INNER_SURF (S1)
*INCLUDE, INPUT={mesh_name}
*MATERIAL, NAME=SHELL_MAT
*ELASTIC
{E_MPA:.6f}, {NU:.6f}
*SHELL SECTION, ELSET=SHELL, MATERIAL=SHELL_MAT
{t_mm:.6f}
** Rigid-body removal (6 DOF): 3 non-collinear nodes, minimal constraints
*STEP, NAME=PRESSURE, NLGEOM=NO, INC=10
*STATIC
1.0, 1.0, 1e-6, 1.0
*BOUNDARY
PIN1, 1, 3, 0.0
PIN2, 2, 3, 0.0
PIN3, 3, 3, 0.0
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
    stem = deck.stem  # ccx appends .inp itself — pass basename without extension
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


def run_case(
    name: str,
    ne: int,
    dP_mmHg: float = DP_MMHG,
    order: int = 2,
    tag: str = "",
) -> dict:
    geom = CASES[name]
    R, t = geom["R"], geom["t"]
    suffix = tag or f"ne{ne}"
    mesh = CCX_DIR / f"{name}_{suffix}_mesh.inp"
    deck = CCX_DIR / f"{name}_{suffix}.inp"

    write_mesh(mesh, R, t, ne, order, label=f"{name} {suffix}")
    write_deck(deck, mesh.name, R, t, dP_mmHg, f"{name} ({suffix})")

    for ext in (".frd", ".sta", ".cvg", ".dat", ".12d"):
        p = CCX_DIR / f"{name}_{suffix}{ext}"
        if p.exists():
            p.unlink()

    frd = run_ccx(deck)
    res = extract(deck, frd, R, t, E_MPA, NU)
    res.update(
        {
            "case": name,
            "mesh_tag": suffix,
            "ne_per_face": ne,
            "order": order,
            "dP_mmHg": dP_mmHg,
            "deck": str(deck),
        }
    )
    return res


def run_one_species(case: str) -> tuple[dict, list[dict], dict]:
    """Run mesh sweep + linearity for a single species; return (final, convergence, linearity)."""
    convergence: list[dict] = []
    for ne in CONVERGENCE_LEVELS:
        tag = f"ne{ne}"
        print(f"\n=== {case} mesh convergence ne={ne} ===")
        r = run_case(case, ne, tag=tag)
        convergence.append(r)

    final = next(x for x in convergence if x["ne_per_face"] == NE_FINE)
    r_coarse = next(x for x in convergence if x["ne_per_face"] == NE_BASE)
    dK = abs(final["K_FEA_mmHg_per_uL"] - r_coarse["K_FEA_mmHg_per_uL"])
    rel = 100.0 * dK / final["K_FEA_mmHg_per_uL"]
    print(f"  {case} |dK|/K(ne={NE_FINE}) coarse→fine = {rel:.3f}%")

    print(f"\n=== {case} linearity check ===")
    r_half = run_case(case, NE_FINE, dP_mmHg=0.5 * DP_MMHG, tag=f"ne{NE_FINE}_Phalf")
    r_full = run_case(case, NE_FINE, dP_mmHg=DP_MMHG, tag=f"ne{NE_FINE}_Pfull")
    ratio = r_full["dV_uL"] / r_half["dV_uL"] if abs(r_half["dV_uL"]) > 1e-20 else float("nan")
    lin = {
        "case": case,
        "dV_half_uL": r_half["dV_uL"],
        "dV_full_uL": r_full["dV_uL"],
        "volume_ratio": ratio,
        "linear_ok": abs(ratio - 2.0) < 0.02,
    }
    print(f"  dV ratio (2x load) = {ratio:.4f}  linear={'OK' if lin['linear_ok'] else 'FAIL'}")
    return final, convergence, lin


def copy_deliverable_deck(name: str) -> None:
    import shutil

    src = CCX_DIR / f"{name}_ne{NE_FINE}.inp"
    dst = CCX_DIR / f"{name}_wp1.1.inp"
    if not src.is_file():
        return
    shutil.copy2(src, dst)
    mesh_src = CCX_DIR / f"{name}_ne{NE_FINE}_mesh.inp"
    mesh_dst = CCX_DIR / f"{name}_wp1.1_mesh.inp"
    if mesh_src.is_file():
        shutil.copy2(mesh_src, mesh_dst)
    if dst.is_file() and mesh_dst.is_file():
        dst.write_text(dst.read_text().replace(f"{name}_ne{NE_FINE}_mesh.inp", mesh_dst.name))


def format_results_md(
    case: str,
    final: dict,
    convergence: list[dict],
    lin: dict,
) -> str:
    rs = final["radial"]
    flag = " ⚠" if rs["u_r_std_over_mean_pct"] > 5.0 else ""
    geom = CASES[case]
    lines = [
        f"# wp1.1 — verificação K ({case})\n",
        f"Geometria: R={geom['R']} mm, t={geom['t']} mm.  "
        f"Malha final: **ne/face = {NE_FINE}** ({final['n_elements']} elementos).\n",
        f"Mapeamento FRD: KDTree R±t/2 + média. "
        f"Independência: `mesh_independence/{case}/MESH_INDEPENDENCE.md`.\n",
        "| malha (elem) | ΔP (mmHg) | ΔV (µL) | K_FEA | K_analítico | erro (%) | u_r std/mean (%) |",
        "|---:|---:|---:|---:|---:|---:|---:|",
        f"| {final['n_elements']} | {final['dP_mmHg']:.3f} | {final['dV_uL']:.6f} | "
        f"{final['K_FEA_mmHg_per_uL']:.6f} | {final['K_analytic_mmHg_per_uL']:.6f} | "
        f"{final['error_pct']:.2f} | {rs['u_r_std_over_mean_pct']:.2f}{flag} |",
        "\n## Convergência (ne = 6 / 12 / 24)\n",
        "| ne/face | elementos | K_FEA | erro vs analítico (%) |",
        "|---:|---:|---:|---:|",
    ]
    for r in convergence:
        lines.append(
            f"| {r['ne_per_face']} | {r['n_elements']} | {r['K_FEA_mmHg_per_uL']:.6f} | {r['error_pct']:.2f} |"
        )
    lines.extend(
        [
            f"\n## Linearidade (ne/face = {NE_FINE})\n",
            "| ΔV @0.5 mmHg | ΔV @1.0 mmHg | razão |",
            "|---:|---:|---:|",
            f"| {lin['dV_half_uL']:.6f} | {lin['dV_full_uL']:.6f} | {lin['volume_ratio']:.4f} |",
            "\n## Conclusão\n",
            f"Erro vs analítico: **{final['error_pct']:+.2f}%** "
            f"({'OK <2%' if abs(final['error_pct']) < 2.0 else 'FAIL ≥2%'}).\n",
        ]
    )
    return "\n".join(lines)


def parse_args():
    import argparse

    p = argparse.ArgumentParser(description="wp1.1 K verification")
    p.add_argument("case", nargs="?", choices=("human", "rabbit", "all"), default="all")
    return p.parse_args()


def main() -> int:
    CCX_DIR.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    args = parse_args()
    cases = ("human", "rabbit") if args.case == "all" else (args.case,)

    print(f"CalculiX: {ccx_bin()}")
    results: list[dict] = []
    all_convergence: list[dict] = []
    all_linearity: list[dict] = []

    for case in cases:
        final, convergence, lin = run_one_species(case)
        results.append(final)
        all_convergence.extend(convergence)
        all_linearity.append(lin)
        copy_deliverable_deck(case)
        md_one = format_results_md(case, final, convergence, lin)
        (OUT / f"RESULTS_{case}.md").write_text(md_one)
        print("\n" + md_one)

    summary_path = OUT / "summary.json"
    prev = json.loads(summary_path.read_text()) if summary_path.is_file() else {}
    prev_cases = {c["case"]: c for c in prev.get("cases", [])}
    prev_conv = {(c["case"], c["ne_per_face"]): c for c in prev.get("mesh_convergence", [])}
    prev_lin = {c["case"]: c for c in prev.get("linearity", [])}
    for r in results:
        prev_cases[r["case"]] = r
    for r in all_convergence:
        prev_conv[(r["case"], r["ne_per_face"])] = r
    for r in all_linearity:
        prev_lin[r["case"]] = r
    summary = {
        "cases": [prev_cases[k] for k in ("human", "rabbit") if k in prev_cases],
        "mesh_convergence": sorted(prev_conv.values(), key=lambda x: (x["case"], x["ne_per_face"])),
        "linearity": [prev_lin[k] for k in ("human", "rabbit") if k in prev_lin],
        "parameters": {"E_MPa": E_MPA, "nu": NU, "dP_mmHg_default": DP_MMHG, "ne_fine": NE_FINE},
    }
    summary_path.write_text(json.dumps(summary, indent=2))

    if len(summary["cases"]) >= 1:
        lines = [
            "# wp1.1 — thin shell K verification\n",
            f"Malha final: **ne/face = {NE_FINE}** ({6 * NE_FINE * NE_FINE} elementos).\n",
            "Relatórios por espécie: `RESULTS_human.md`, `RESULTS_rabbit.md`.\n",
            "| caso | malha (elementos) | ΔP (mmHg) | ΔV (µL) | K_FEA | K_analítico | erro (%) | u_r std/mean (%) |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
        for r in results:
            rs = r["radial"]
            flag = " ⚠" if rs["u_r_std_over_mean_pct"] > 5.0 else ""
            lines.append(
                f"| {r['case']} | {r['n_elements']} | {r['dP_mmHg']:.3f} | "
                f"{r['dV_uL']:.6f} | {r['K_FEA_mmHg_per_uL']:.6f} | "
                f"{r['K_analytic_mmHg_per_uL']:.6f} | {r['error_pct']:.2f} | "
                f"{rs['u_r_std_over_mean_pct']:.2f}{flag} |"
            )
        lines.append("\n## Convergência de malha (K_FEA, ne = 6 / 12 / 24)\n")
        lines.append("| caso | ne/face | elementos | K_FEA | erro vs analítico (%) |")
        lines.append("|---|---:|---:|---:|---:|")
        for r in all_convergence:
            lines.append(
                f"| {r['case']} | {r['ne_per_face']} | {r['n_elements']} | "
                f"{r['K_FEA_mmHg_per_uL']:.6f} | {r['error_pct']:.2f} |"
            )
        lines.append(f"\n## Linearidade (ne/face = {NE_FINE})\n")
        lines.append("| caso | ΔV @0.5 mmHg (µL) | ΔV @1.0 mmHg (µL) | razão |")
        lines.append("|---|---:|---:|---:|")
        for r in all_linearity:
            lines.append(
                f"| {r['case']} | {r['dV_half_uL']:.6f} | {r['dV_full_uL']:.6f} | {r['volume_ratio']:.4f} |"
            )
        ok = all(abs(r["error_pct"]) < 2.0 for r in results)
        errs = ", ".join(f"{r['case']} {r['error_pct']:+.2f}%" for r in results)
        lines.append(
            f"\n## Conclusão\n\n**Critério <2% {'atingido' if ok else 'NÃO atingido'}** ({errs}).\n"
        )
        (OUT / "RESULTS.md").write_text("\n".join(lines))

    ok = all(abs(r["error_pct"]) < 2.0 for r in results)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
