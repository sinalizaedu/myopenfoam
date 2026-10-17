#!/usr/bin/env python3
"""Forward Ogden run with exact handoff params; compare P(V) anchor points."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "wp1.1" / "scripts"))

from ccx_utils import run_ccx  # noqa: E402
from extract_pv_curve import extract_pv  # noqa: E402
from gen_sphere_shell_mesh import write_mesh  # noqa: E402
from write_deck import write_deck  # noqa: E402

MU1, ALPHA1, D1 = 2.1397, 1.7709, 0.238446
HANDOFF_ANCHORS = [(2.86, 0.8), (35.99, 10.0), (72.43, 20.0)]


def main() -> int:
    work = HERE.parent / "output_octant" / "forward_handoff"
    work.mkdir(parents=True, exist_ok=True)

    mesh = work / "mesh.inp"
    write_mesh(
        mesh,
        12.0,
        0.5,
        6,
        2,
        "handoff",
        bc_mode="symmetry_octant",
        mesh_kind="spherical",
        reduced=True,
    )

    params = {"mu1_MPa": MU1, "alpha1": ALPHA1, "D1": D1}
    p_targets = [16.9 + i * (80.0 - 16.9) / 16 for i in range(1, 17)]
    deck = work / "forward.inp"
    write_deck(
        deck,
        mesh.name,
        0.5,
        "ogden1",
        params,
        p_targets,
        bc_mode="symmetry_octant",
        p0_mmhg=16.9,
    )
    frd = run_ccx(deck, clean=True)
    rows = extract_pv(deck, frd, 12.0, p0_mmhg=16.9)
    v = np.array([r["dV_uL"] for r in rows], dtype=float)
    p = np.array([r["p_mmhg"] for r in rows], dtype=float)
    order = np.argsort(v)
    v, p = v[order], p[order]

    print(f"Handoff params: mu1={MU1}, alpha1={ALPHA1}, D1={D1}")
    print("\n=== P at their V (interpolate ours) ===")
    for vv, pp in HANDOFF_ANCHORS:
        p_ours = float(np.interp(vv, v, p))
        ratio = p_ours / pp if pp > 0 else float("nan")
        print(f"V={vv:6.2f}  P_handoff={pp:6.2f}  P_ours={p_ours:6.2f}  P_ours/P_handoff={ratio:.2f}x")

    print("\n=== V at their P (interpolate ours) ===")
    for vv, pp in HANDOFF_ANCHORS:
        v_ours = float(np.interp(pp, p, v))
        ratio = v_ours / vv if vv > 0 else float("nan")
        print(f"P={pp:6.2f}  V_handoff={vv:6.2f}  V_ours={v_ours:6.2f}  V_ours/V_handoff={ratio:.2f}x")

    print("\n=== Our curve (all load steps) ===")
    for vi, pi in zip(v, p):
        print(f"  V={vi:8.3f}  P={pi:8.3f}")

    out = work / "pv_curve.csv"
    with open(out, "w") as fh:
        fh.write("V_uL,P_mmHg\n")
        for vi, pi in zip(v, p):
            fh.write(f"{vi:.6f},{pi:.6f}\n")
    print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
