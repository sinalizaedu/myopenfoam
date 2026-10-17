#!/usr/bin/env python3
"""NLGEOM stability probes: parameter perturbations on spherical octant."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "wp1.1" / "scripts"))

from ccx_utils import run_ccx  # noqa: E402
from gen_sphere_shell_mesh import write_mesh  # noqa: E402
from write_deck import write_deck  # noqa: E402


def try_run(mu1: float, alpha1: float, d1: float, tag: str, work: Path) -> str:
    mesh = work / "mesh.inp"
    if not mesh.is_file():
        write_mesh(
            mesh,
            12.0,
            0.5,
            6,
            2,
            "probe",
            bc_mode="symmetry_octant",
            mesh_kind="spherical",
            reduced=True,
        )
    params = {"mu1_MPa": mu1, "alpha1": alpha1, "D1": d1}
    p_targets = [16.9 + i * (80.0 - 16.9) / 16 for i in range(1, 17)]
    deck = work / f"{tag}.inp"
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
    try:
        run_ccx(deck, clean=True)
        return "OK"
    except Exception as exc:
        log = work / f"log_{tag}.txt"
        tail = log.read_text().splitlines()[-5:] if log.is_file() else []
        return f"FAIL: {exc} | log_tail={tail}"


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ccx-bin", default="", help="Override CalculiX binary (e.g. /usr/bin/ccx)")
    args = ap.parse_args()
    if args.ccx_bin:
        import os

        os.environ["CCX_BIN"] = args.ccx_bin

    work = HERE.parent / "output_octant" / "stability_probe"
    if args.ccx_bin:
        tag = Path(args.ccx_bin).name.replace("/", "_")
        work = work / tag
    work.mkdir(parents=True, exist_ok=True)
    from ccx_utils import ccx_bin

    print(f"CalculiX binary: {ccx_bin()}")

    base_mu, base_al, base_d1 = 2.1397, 1.7709, 0.238446
    delta = base_mu * 0.000007  # 0.0007% relative

    cases = [
        ("handoff_exact", base_mu, base_al, base_d1),
        ("handoff_mu_plus", base_mu + delta, base_al, base_d1),
        ("handoff_mu_minus", base_mu - delta, base_al, base_d1),
        ("low_alpha", 2.08, 0.55, 0.5 * (1.0204 / 2.08)),
    ]
    print("=== Octant NLGEOM stability (ne=6, S8R) ===")
    for tag, mu, al, d1 in cases:
        status = try_run(mu, al, d1, tag, work)
        print(f"{tag:18s}  mu={mu:.6f}  alpha={al:.4f}  D1={d1:.6f}  -> {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
