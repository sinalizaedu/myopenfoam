#!/usr/bin/env python3
"""E1/E2 stability sweeps — Ogden α₁ map and Yeoh control (wp1.2 exploration).

E1: fix μ₁=3.0, sweep α₁, 3 fresh runs per point.
E2: Yeoh-2 with comparable (C10, C20) pairs, 3 fresh runs per point.

See plano_exploracao_instabilidade.md Part 4.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "wp1.1" / "scripts"))

from ccx_utils import ccx_bin, d1_from_ogden_mu1  # noqa: E402
from gen_sphere_shell_mesh import write_mesh  # noqa: E402
from write_deck import write_deck  # noqa: E402

# Pallikaris octant reference geometry / load
R_MM = 12.0
T_MM = 0.5
P0_MMHG = 16.9
P_FINAL_MMHG = 80.0
N_LOAD_STEPS = 16
MU1_FIXED = 3.0

E1_ALPHAS = [0.3, 0.5, 0.8, 1.2, 2.0, 3.0, 5.0]
E2_YEOH_PAIRS = [
    (0.30, 0.020),
    (0.50, 0.050),
    (0.612, 0.058),  # selftest reference
    (1.00, 0.080),
    (1.50, 0.100),
]


@dataclass
class TrialResult:
    tag: str
    rep: int
    model: str
    params: dict
    status: str
    elapsed_s: float


def p_targets() -> list[float]:
    return [
        P0_MMHG + (P_FINAL_MMHG - P0_MMHG) * i / N_LOAD_STEPS
        for i in range(1, N_LOAD_STEPS + 1)
    ]


def run_ccx_checked(deck: Path, timeout_s: int = 600) -> tuple[str, float]:
    ccx = ccx_bin()
    work = deck.parent
    stem = deck.stem
    t0 = time.perf_counter()
    for ext in (".frd", ".sta", ".cvg", ".dat", ".12d", ".stm", ".out"):
        p = work / f"{stem}{ext}"
        if p.exists():
            p.unlink()
    log = work / f"log_{stem}.txt"
    env = os.environ.copy()
    env.setdefault("OMP_NUM_THREADS", str(os.cpu_count() or 4))
    try:
        with log.open("w") as fh:
            subprocess.run(
                [ccx, "-i", stem],
                cwd=work,
                check=True,
                stdout=fh,
                stderr=subprocess.STDOUT,
                env=env,
                timeout=timeout_s,
            )
    except subprocess.CalledProcessError:
        tail = log.read_text().splitlines()[-6:] if log.is_file() else []
        return f"FAIL exit!=0 tail={tail}", time.perf_counter() - t0
    except subprocess.TimeoutExpired:
        return f"FAIL timeout>{timeout_s}s", time.perf_counter() - t0

    frd = work / f"{stem}.frd"
    text = log.read_text() if log.is_file() else ""
    elapsed = time.perf_counter() - t0
    if not frd.is_file():
        return "FAIL no FRD", elapsed
    if "*ERROR" in text and "Job finished" not in text:
        return "FAIL CCX error in log", elapsed
    return "OK", elapsed


def fresh_mesh(work: Path, ne: int, rep: int) -> str:
    """Regenerate mesh from scratch (unique name per rep)."""
    mesh_name = f"mesh_ne{ne}_r{rep}.inp"
    write_mesh(
        work / mesh_name,
        R_MM,
        T_MM,
        ne,
        2,
        "e1e2",
        bc_mode="symmetry_octant",
        mesh_kind="spherical",
        reduced=True,
    )
    return mesh_name


def run_ogden_trial(work: Path, alpha1: float, rep: int, ne: int) -> TrialResult:
    d1 = d1_from_ogden_mu1(MU1_FIXED)
    params = {"mu1_MPa": MU1_FIXED, "alpha1": alpha1, "D1": d1}
    tag = f"ogden_a{alpha1:.1f}_r{rep}"
    mesh = fresh_mesh(work, ne, rep)
    deck = work / f"{tag}.inp"
    write_deck(
        deck,
        mesh,
        T_MM,
        "ogden1",
        params,
        p_targets(),
        label=f"E1 {tag}",
        bc_mode="symmetry_octant",
        p0_mmhg=P0_MMHG,
    )
    status, elapsed = run_ccx_checked(deck)
    return TrialResult(tag, rep, "ogden1", params, status, elapsed)


def run_yeoh_trial(
    work: Path, c10: float, c20: float, rep: int, ne: int
) -> TrialResult:
    params = {"C10_MPa": c10, "C20_MPa": c20}
    tag = f"yeoh_c10{c10:.3f}_c20{c20:.3f}_r{rep}"
    mesh = fresh_mesh(work, ne, rep)
    deck = work / f"{tag}.inp"
    write_deck(
        deck,
        mesh,
        T_MM,
        "yeoh2",
        params,
        p_targets(),
        label=f"E2 {tag}",
        bc_mode="symmetry_octant",
        p0_mmhg=P0_MMHG,
    )
    status, elapsed = run_ccx_checked(deck)
    return TrialResult(tag, rep, "yeoh2", params, status, elapsed)


def summarize_group(results: list[TrialResult], key_fn) -> list[dict]:
    groups: dict[str, list[TrialResult]] = {}
    for r in results:
        groups.setdefault(key_fn(r), []).append(r)
    rows = []
    for key in sorted(groups, key=lambda k: (isinstance(k, tuple), k)):
        trials = groups[key]
        n_ok = sum(1 for t in trials if t.status == "OK")
        rows.append(
            {
                "key": key,
                "n_trials": len(trials),
                "n_ok": n_ok,
                "fail_rate": 1.0 - n_ok / len(trials),
                "conv_rate": n_ok / len(trials),
                "statuses": [t.status for t in sorted(trials, key=lambda x: x.rep)],
            }
        )
    return rows


def write_results_md(
    out: Path,
    ccx: str,
    ne: int,
    n_rep: int,
    e1_results: list[TrialResult],
    e2_results: list[TrialResult],
) -> None:
    e1_summary = summarize_group(e1_results, lambda r: r.params["alpha1"])
    e2_summary = summarize_group(
        e2_results, lambda r: (r.params["C10_MPa"], r.params["C20_MPa"])
    )

    def mono_e1(rows: list[dict]) -> str:
        if len(rows) < 2:
            return "insufficient data"
        ordered = sorted(rows, key=lambda x: x["key"])
        rates = [r["fail_rate"] for r in ordered]
        if max(rates) < 1e-9:
            return "inconclusive — 0% failure at all α₁ (no gradient to test)"
        if all(rates[i] <= rates[i + 1] + 1e-9 for i in range(len(rates) - 1)):
            return "yes — fail rate non-decreasing as α₁ decreases"
        return "no — fail rate not monotonic in α₁"

    e2_min_conv = min((r["conv_rate"] for r in e2_summary), default=0.0)
    e2_pass = e2_min_conv >= 0.95

    lines = [
        "# E1/E2 — stability exploration (Ogden vs Yeoh)",
        "",
        f"- **ccx**: `{ccx}`",
        f"- **geometry**: R={R_MM} mm, t={T_MM} mm, octant, ne={ne}",
        f"- **load**: P₀={P0_MMHG} → P_final={P_FINAL_MMHG} mmHg ({N_LOAD_STEPS} steps)",
        f"- **repetitions per point**: {n_rep} (fresh mesh + deck each)",
        "",
        "## E1 — Ogden N=1, μ₁ fixed",
        "",
        f"- **μ₁**: {MU1_FIXED} MPa",
        f"- **D₁**: {d1_from_ogden_mu1(MU1_FIXED):.8f} (tied to μ₁)",
        f"- **α₁ sweep**: {E1_ALPHAS}",
        "",
        "| α₁ | OK | fail | conv rate | statuses |",
        "|---:|---:|---:|---:|---|",
    ]
    for row in sorted(e1_summary, key=lambda x: x["key"]):
        st = ", ".join(row["statuses"])
        lines.append(
            f"| {row['key']:.1f} | {row['n_ok']} | {row['n_trials'] - row['n_ok']} | "
            f"{row['conv_rate']:.0%} | {st} |"
        )
    lines.extend(
        [
            "",
            f"**Monotonic fail rate (α₁ ↓)?** {mono_e1(e1_summary)}",
            "",
            "## E2 — Yeoh-2 control",
            "",
            f"- **(C10, C20) pairs**: {E2_YEOH_PAIRS}",
            "",
            "| C10 | C20 | OK | fail | conv rate | statuses |",
            "|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in sorted(e2_summary, key=lambda x: x["key"]):
        c10, c20 = row["key"]
        st = ", ".join(row["statuses"])
        lines.append(
            f"| {c10:.3f} | {c20:.3f} | {row['n_ok']} | {row['n_trials'] - row['n_ok']} | "
            f"{row['conv_rate']:.0%} | {st} |"
        )
    lines.extend(
        [
            "",
            f"**E2 success criterion (≥95% all points)?** {'PASS' if e2_pass else 'FAIL'} "
            f"(min conv rate = {e2_min_conv:.0%})",
            "",
            "## Interpretation gates",
            "",
            "- E1 confirms Part 3 hypothesis if fail rate rises as α₁ decreases.",
            "- E2 PASS → proceed to E3 (full Yeoh fit vs Pallikaris).",
            "- E1 PASS + E2 PASS → close mesh/CCX/deck investigation lines.",
        ]
    )
    out.write_text("\n".join(lines) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ne", type=int, default=8)
    ap.add_argument("--n-rep", type=int, default=3)
    ap.add_argument("--out", type=Path, default=HERE.parent / "output_exploration")
    ap.add_argument("--e1-only", action="store_true")
    ap.add_argument("--e2-only", action="store_true")
    ap.add_argument("--ccx-bin", default=os.environ.get("CCX_BIN", ""))
    args = ap.parse_args()

    if args.ccx_bin:
        os.environ["CCX_BIN"] = args.ccx_bin

    ccx = ccx_bin()
    args.out.mkdir(parents=True, exist_ok=True)
    e1_work = args.out / "e1_ogden"
    e2_work = args.out / "e2_yeoh"
    e1_work.mkdir(parents=True, exist_ok=True)
    e2_work.mkdir(parents=True, exist_ok=True)

    run_e1 = not args.e2_only
    run_e2 = not args.e1_only

    print(f"=== E1/E2 stability exploration ===")
    print(f"  ccx={ccx}")
    print(f"  ne={args.ne}  n_rep={args.n_rep}  out={args.out}")

    e1_results: list[TrialResult] = []
    e2_results: list[TrialResult] = []

    if run_e1:
        print("\n--- E1: Ogden α₁ sweep ---")
        for alpha in E1_ALPHAS:
            for rep in range(1, args.n_rep + 1):
                tr = run_ogden_trial(e1_work, alpha, rep, args.ne)
                e1_results.append(tr)
                print(f"  α₁={alpha:.1f} rep={rep} -> {tr.status} ({tr.elapsed_s:.1f}s)")

    if run_e2:
        print("\n--- E2: Yeoh-2 control ---")
        for c10, c20 in E2_YEOH_PAIRS:
            for rep in range(1, args.n_rep + 1):
                tr = run_yeoh_trial(e2_work, c10, c20, rep, args.ne)
                e2_results.append(tr)
                print(f"  C10={c10:.3f} C20={c20:.3f} rep={rep} -> {tr.status} ({tr.elapsed_s:.1f}s)")

    payload = {
        "ccx": ccx,
        "ne": args.ne,
        "n_rep": args.n_rep,
        "e1": [asdict(r) for r in e1_results],
        "e2": [asdict(r) for r in e2_results],
    }
    (args.out / "e1_e2_results.json").write_text(json.dumps(payload, indent=2))

    write_results_md(args.out / "RESULTS.md", ccx, args.ne, args.n_rep, e1_results, e2_results)
    print(f"\nWrote {args.out / 'RESULTS.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
