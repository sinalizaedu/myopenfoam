#!/usr/bin/env python3
"""Compare the O1 volume corrections against patch and the uncorrected volume.

Cases (all t=0->1 s, dt=0.005 s, IVI + wall cheat active the whole time):
  patch    doc-run-o1-patch-fluid geometry, cavity + flowRateInletVelocity
  volume   original Model C: needle cells still inside the porous vitreous
  nodarcy  correction 1 only: ivi_tip_cells subtracted from vitreous_zone
  fix      corrections 1 + 2: no Darcy in the tip + vectorSemiImplicitSource on U
"""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "cmp", REPO / "brunaStuff/compare_o1_patch_vs_volume_ivi.py"
)
cmp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cmp)

ARCHIVE = REPO / "cases/T1: Volume vs Patch"
CASES = {
    "patch": "diag-o1-patch-1s-active",
    "volume": "diag-o1-volume-1s-active",
    "nodarcy": "diag-o1-volume-1s-nodarcy",
    "fix": "diag-o1-volume-1s-fix",
}
OUT = ARCHIVE / "figures/o1_volume_corrections"


def analyse(fluid: Path) -> tuple[dict, tuple]:
    mesh = fluid / "constant/polyMesh"
    cc = cmp.cell_centres(mesh)
    p = cmp.read_internal_field(fluid / "1/p", 1)
    U = cmp.read_internal_field(fluid / "1/U", 3)

    steps = cmp.parse_log(fluid / "log.pimpleFoam")["steps"]
    txt = (fluid / "log.pimpleFoam").read_text()
    wall = int(re.search(r"WALL_SECONDS=(\d+)", txt).group(1))

    owner = cmp.read_int_list(mesh / "owner")
    nei = cmp.read_int_list(mesh / "neighbour")
    ni = len(nei)
    dist = np.linalg.norm(cc - cmp.TIP, axis=1)
    o, n = owner[:ni], nei
    near_face = ((dist[o] + dist[n]) / 2) < 1.5e-3
    grad = np.abs(cmp.p_to_mmhg(p[o] - p[n])) / (np.linalg.norm(cc[o] - cc[n], axis=1) * 1e3)
    g = grad[near_face]

    speed = np.linalg.norm(U, axis=1)
    shell = (dist > 0.56e-3) & (dist < 1.5e-3) & (speed > 1e-12)
    rhat = (cc[shell] - cmp.TIP) / dist[shell, None]
    cos = np.sum(U[shell] * rhat, axis=1) / speed[shell]

    sums = np.array([s["sum_iter"] for s in steps])
    hits = np.array([s["n_hit_500"] for s in steps])
    co = np.array([s["courant_max"] for s in steps if s["courant_max"] is not None])

    fs = cmp.field_stats(cc, p, U)
    return {
        "n_cells": int(len(cc)),
        "n_steps": len(steps),
        "wall_seconds": wall,
        "gamg_total_iterations": int(sums.sum()),
        "gamg_mean_sum_per_step": float(sums.mean()),
        "pFinal_500_hits_total": int(hits.sum()),
        "steps_with_500_hit": int((hits > 0).sum()),
        "courant_max_mean": float(co.mean()),
        "courant_max_peak": float(co.max()),
        "p_max_near_mmHg": fs["near_1p5mm"]["p_max_mmHg"],
        "p_p99_near_mmHg": fs["near_1p5mm"]["p_p99_mmHg"],
        "p_p50_near_mmHg": fs["near_1p5mm"]["p_p50_mmHg"],
        "p_max_core_mmHg": fs["core_0p825mm"]["p_max_mmHg"],
        "p_max_global_mmHg": fs["global"]["p_max_mmHg"],
        "pmax_r_mm": fs["near_1p5mm"]["pmax_r_mm"],
        "grad_p50_mmHg_per_mm": float(np.percentile(g, 50)),
        "grad_p95_mmHg_per_mm": float(np.percentile(g, 95)),
        "grad_p99_mmHg_per_mm": float(np.percentile(g, 99)),
        "grad_max_mmHg_per_mm": float(g.max()),
        "U_max_near_mm_s": fs["near_1p5mm"]["U_max_mm_s"],
        "U_max_global_mm_s": fs["global"]["U_max_mm_s"],
        "shell_mean_U_mm_s": float(speed[shell].mean() * 1e3),
        "shell_mean_radial_cosine": float(cos.mean()),
        "shell_frac_outward": float((cos > 0.8).mean()),
    }, (cc, p, U)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    report, cache = {}, {}
    for key, case in CASES.items():
        fluid = ARCHIVE / case / "fluid"
        if not (fluid / "1/p").exists():
            print(f"skip {key}: no t=1 output")
            continue
        print(f"analysing {key} ...", flush=True)
        report[key], cache[key] = analyse(fluid)

    pmin = min(float(cmp.p_to_mmhg(v[1]).min()) for v in cache.values())
    pmax = max(float(cmp.p_to_mmhg(v[1]).max()) for v in cache.values())
    umax = max(float(np.linalg.norm(v[2], axis=1).max() * 1e3) for v in cache.values())
    for key, (cc, p, U) in cache.items():
        cmp.plot_slice(
            cc, p, U,
            f"O1 {key} · t=1.0 s · IVI + wall cheat active · shared scale",
            OUT / f"{key}_t1.png",
            p_clim=(pmin, pmax), u_clim=(0, umax),
        )

    (OUT / "comparison.json").write_text(json.dumps(report, indent=2))

    rows = [
        ("p_max near tip (mmHg)", "p_max_near_mmHg", "{:.1f}"),
        ("p_p99 near tip (mmHg)", "p_p99_near_mmHg", "{:.1f}"),
        ("p_p50 near tip (mmHg)", "p_p50_near_mmHg", "{:.1f}"),
        ("max grad (mmHg/mm)", "grad_max_mmHg_per_mm", "{:.1f}"),
        ("p99 grad (mmHg/mm)", "grad_p99_mmHg_per_mm", "{:.1f}"),
        ("GAMG iters/step", "gamg_mean_sum_per_step", "{:.0f}"),
        ("pFinal maxIter hits", "pFinal_500_hits_total", "{:.0f}"),
        ("wall clock (s)", "wall_seconds", "{:.0f}"),
        ("U max near tip (mm/s)", "U_max_near_mm_s", "{:.2f}"),
        ("shell mean U (mm/s)", "shell_mean_U_mm_s", "{:.2f}"),
        ("Courant peak", "courant_max_peak", "{:.3f}"),
    ]
    keys = [k for k in CASES if k in report]
    width = max(len(r[0]) for r in rows) + 2
    print()
    print("metric".ljust(width) + "".join(k.rjust(12) for k in keys))
    print("-" * (width + 12 * len(keys)))
    for label, field, fmt in rows:
        line = label.ljust(width)
        for k in keys:
            line += fmt.format(report[k][field]).rjust(12)
        print(line)
    print(f"\nwrote {OUT/'comparison.json'}")


if __name__ == "__main__":
    main()
