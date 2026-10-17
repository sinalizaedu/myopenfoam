#!/usr/bin/env python3
"""Write octant Ogden deck matching external WP1 compat convention."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

WP1_SCRIPTS = Path(__file__).resolve().parents[2] / "wp1.1" / "scripts"
sys.path.insert(0, str(WP1_SCRIPTS))

from octant_mesh_compat import build_octant_mesh  # noqa: E402

MMHG_TO_MPA = 133.322e-6


def _write_nset_lines(fh, ids: list[int], per_line: int = 10) -> None:
    ids = sorted(set(int(i) for i in ids))
    for i in range(0, len(ids), per_line):
        fh.write(",".join(str(x) for x in ids[i : i + per_line]) + "\n")


def d1_from_mu1(mu1_mpa: float) -> float:
    return 0.12 * (1.0204 / float(mu1_mpa))


def write_octant_ogden_compat(
    path: Path,
    n_theta: int,
    n_phi: int,
    R: float,
    t: float,
    mu1: float,
    alpha1: float,
    d1: float | None,
    p_mmhg_final: float,
    n_steps: int = 25,
) -> tuple[dict, list]:
    """Deck: NLGEOM ramp, STATIC 1/n..2/n, SNEG surface, OUTPUT=2D."""
    if d1 is None:
        d1 = d1_from_mu1(mu1)
    nodes, elements, sym_x, sym_y, sym_z, _inner = build_octant_mesh(n_theta, n_phi, R)
    p_mpa = p_mmhg_final * MMHG_TO_MPA
    inc0 = 1.0 / n_steps
    inc_max = 2.0 / n_steps

    with path.open("w") as fh:
        fh.write("*HEADING\noctante compat — Ogden N=1, rampa unica NLGEOM\n")
        fh.write("*NODE, NSET=NALL\n")
        for nid in sorted(nodes):
            x, y, z = nodes[nid]
            fh.write(f"{nid}, {x:.10f}, {y:.10f}, {z:.10f}\n")
        fh.write("*ELEMENT, TYPE=S8R, ELSET=SHELL\n")
        for i, conn in enumerate(elements, start=1):
            fh.write(f"{i}, " + ", ".join(str(c) for c in conn) + "\n")

        fh.write("*NSET, NSET=SYMX\n")
        _write_nset_lines(fh, sym_x)
        fh.write("*NSET, NSET=SYMY\n")
        _write_nset_lines(fh, sym_y)
        fh.write("*NSET, NSET=SYMZ\n")
        _write_nset_lines(fh, sym_z)

        fh.write("*SURFACE, NAME=INNER_SURF, TYPE=ELEMENT\nSHELL, SNEG\n")
        fh.write("*MATERIAL, NAME=OGDEN_MAT\n*HYPERELASTIC, OGDEN, N=1\n")
        fh.write(f"{mu1:.6f}, {alpha1:.6f}, {d1:.8f}\n")
        fh.write(f"*SHELL SECTION, ELSET=SHELL, MATERIAL=OGDEN_MAT\n{t:.6f}\n")

        fh.write(f"*STEP, NLGEOM=YES, INC=500\n*STATIC\n")
        fh.write(f"{inc0:.5f}, 1.0, 1e-8, {inc_max:.5f}\n")
        fh.write("*BOUNDARY\nSYMX,1,1,0.0\nSYMY,2,2,0.0\nSYMZ,3,3,0.0\n")
        fh.write(f"*DSLOAD\nINNER_SURF, P, {p_mpa:.12e}\n")
        fh.write("*NODE FILE, OUTPUT=2D, FREQUENCY=1\nU\n*END STEP\n")

    return nodes, elements


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--n", type=int, default=6, help="n_theta = n_phi")
    ap.add_argument("--R", type=float, default=12.0)
    ap.add_argument("--t", type=float, default=0.5)
    ap.add_argument("--mu1", type=float, default=2.08)
    ap.add_argument("--alpha1", type=float, default=0.55)
    ap.add_argument("--D1", type=float, default=0.0, help="0 = tied from mu1")
    ap.add_argument("--p-mmhg", type=float, default=80.0)
    ap.add_argument("--n-steps", type=int, default=25)
    args = ap.parse_args()

    d1 = None if args.D1 <= 0 else args.D1
    write_octant_ogden_compat(
        args.out,
        args.n,
        args.n,
        args.R,
        args.t,
        args.mu1,
        args.alpha1,
        d1,
        args.p_mmhg,
        n_steps=args.n_steps,
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
