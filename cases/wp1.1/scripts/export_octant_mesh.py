#!/usr/bin/env python3
"""Export octant node coords + S8 connectivity for cross-side comparison."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from gen_sphere_shell_mesh import build_mesh_with_bc, write_mesh


def export(R: float, ne: int, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    coords, elems, nsets, _ = build_mesh_with_bc(
        R,
        ne,
        2,
        bc_mode="symmetry_octant",
        mesh_kind="spherical",
        theta_min_deg=3.0,
    )

    nodes_csv = out_dir / f"nossos_nos_octante_n{ne}.csv"
    with nodes_csv.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["node_id", "x", "y", "z"])
        for nid in sorted(coords.keys()):
            x, y, z = coords[nid]
            w.writerow([nid, f"{x:.10f}", f"{y:.10f}", f"{z:.10f}"])

    elems_csv = out_dir / f"nossos_elementos_octante_n{ne}.csv"
    with elems_csv.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["elem_id", "n1", "n2", "n3", "n4", "n5", "n6", "n7", "n8"])
        for eid, ns in elems:
            w.writerow([eid, *ns])

    orphan = sorted(set(coords) - set(nsets["NALL"]))
    meta = {
        "R_mm": R,
        "ne": ne,
        "mesh_kind": "spherical",
        "theta_min_deg": 3.0,
        "n_nodes_coords": len(coords),
        "n_nodes_nall": len(nsets["NALL"]),
        "n_orphan_nodes": len(orphan),
        "orphan_node_ids": orphan,
        "n_elements": len(elems),
    }
    (out_dir / f"mesh_meta_n{ne}.json").write_text(json.dumps(meta, indent=2))

    mesh_inp = out_dir / f"octant_n{ne}_mesh.inp"
    write_mesh(
        mesh_inp,
        R,
        0.5,
        ne,
        2,
        f"export n{ne}",
        bc_mode="symmetry_octant",
        mesh_kind="spherical",
        reduced=True,
    )
    print(f"Wrote {nodes_csv} ({len(coords)} nodes)")
    print(f"Wrote {elems_csv} ({len(elems)} elements)")
    print(f"NALL in CalculiX mesh: {len(nsets['NALL'])} nodes ({len(orphan)} orphans excluded)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--R", type=float, default=12.0)
    ap.add_argument("--ne", type=int, default=8)
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[1] / "output_octant")
    args = ap.parse_args()
    export(args.R, args.ne, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
