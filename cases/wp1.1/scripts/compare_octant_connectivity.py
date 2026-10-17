#!/usr/bin/env python3
"""Compare octant S8 connectivity: map nodes by position, not node_id."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from gen_sphere_shell_mesh import build_spherical_octant


def pos_key(x: float, y: float, z: float, tol: float = 1e-6) -> tuple[int, int, int]:
    return tuple(int(round(c / tol)) for c in (x, y, z))


def load_nodes_csv(path: Path) -> dict[int, np.ndarray]:
    out: dict[int, np.ndarray] = {}
    for row in csv.DictReader(path.open()):
        nid = int(row["node_id"])
        out[nid] = np.array([float(row["x"]), float(row["y"]), float(row["z"])])
    return out


def build_grid_from_nodes(
    nodes: dict[int, np.ndarray],
    ne: int,
    theta_min_deg: float = 3.0,
) -> np.ndarray:
    """Assign grid[i,j] = node_id assuming row-major in phi (j) for each theta row (i).

    Matches ordering in meus_nos_octante_n8.csv (ids 1..17 = i=0, etc.).
    """
    ngrid = 2 * ne + 1
    keys = {pos_key(*xyz): nid for nid, xyz in nodes.items()}
    theta_min = np.deg2rad(theta_min_deg)
    theta_max = np.pi / 2.0
    phi_max = np.pi / 2.0
    grid = np.zeros((ngrid, ngrid), dtype=int)
    for i in range(ngrid):
        for j in range(ngrid):
            theta = theta_min + (theta_max - theta_min) * i / (2 * ne)
            phi = phi_max * j / (2 * ne)
            st, ct = np.sin(theta), np.cos(theta)
            cp, sp = np.cos(phi), np.sin(phi)
            x, y, z = 12.0 * st * cp, 12.0 * st * sp, 12.0 * ct
            k = pos_key(x, y, z)
            if k not in keys:
                raise KeyError(f"No node at grid[{i},{j}] pos {k}")
            grid[i, j] = keys[k]
    return grid


def elements_from_grid(grid: np.ndarray, ne: int) -> list[tuple[int, ...]]:
    elems: list[tuple[int, ...]] = []
    for ej in range(ne):
        for ei in range(ne):
            i, j = 2 * ei, 2 * ej
            conn = (
                int(grid[i, j]),
                int(grid[i + 2, j]),
                int(grid[i + 2, j + 2]),
                int(grid[i, j + 2]),
                int(grid[i + 1, j]),
                int(grid[i + 2, j + 1]),
                int(grid[i + 1, j + 2]),
                int(grid[i, j + 1]),
            )
            elems.append(conn)
    return elems


def elem_position_set(conn: tuple[int, ...], nodes: dict[int, np.ndarray]) -> frozenset:
    return frozenset(pos_key(*nodes[nid]) for nid in conn)


def elem_corner_cycle(conn: tuple[int, ...], nodes: dict[int, np.ndarray]) -> tuple:
    """First 4 corners only, cyclic canonical form for orientation check."""
    corners = [pos_key(*nodes[nid]) for nid in conn[:4]]
    # canonical rotation
    rots = [tuple(corners[k:] + corners[:k]) for k in range(4)]
    rev = list(reversed(corners))
    rots += [tuple(rev[k:] + rev[:k]) for k in range(4)]
    return min(rots)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ne", type=int, default=8)
    ap.add_argument(
        "--theirs-nodes",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / ".."
        / ".."
        / ".cursor"
        / "projects"
        / "Users-brunaenne-Documents-repos-myopenfoam"
        / "attachments"
        / "8a4074d8-e44b-4bb3-972d-cda47a6f5e57"
        / "meus_nos_octante_n8.csv",
    )
    ap.add_argument(
        "--theirs-elems",
        type=Path,
        default=None,
        help="Optional meus_elementos_octante_n8.csv",
    )
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[1] / "output_octant")
    args = ap.parse_args()

    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    # Ours from generator
    coords, ours_elems_raw, nsets, _ = build_spherical_octant(12.0, args.ne, 2, 3.0)
    ours_nodes = {int(n): np.asarray(x) for n, x in coords.items()}
    ours_elems = [tuple(int(x) for x in ns) for _, ns in ours_elems_raw]

    # Theirs from CSV (+ optional elem file)
    if not args.theirs_nodes.is_file():
        print(f"Missing {args.theirs_nodes}")
        return 1
    theirs_nodes = load_nodes_csv(args.theirs_nodes)

    if args.theirs_elems and args.theirs_elems.is_file():
        theirs_elems = []
        for row in csv.DictReader(args.theirs_elems.open()):
            theirs_elems.append(
                tuple(int(row[f"n{k}"]) for k in range(1, 9))
            )
    else:
        grid = build_grid_from_nodes(theirs_nodes, args.ne)
        theirs_elems = elements_from_grid(grid, args.ne)
        print("Note: theirs elements reconstructed from node grid order (i-outer, j-inner).")

    if len(ours_elems) != len(theirs_elems):
        print(f"Element count mismatch: ours={len(ours_elems)} theirs={len(theirs_elems)}")
        return 1

    # Compare element-by-element (same parametric cell order ei, ej)
    n = len(ours_elems)
    same_node_set = 0
    same_corner_orient = 0
    mismatches: list[dict] = []

    for k in range(n):
        o_conn = ours_elems[k]
        t_conn = theirs_elems[k]
        o_set = elem_position_set(o_conn, ours_nodes)
        t_set = elem_position_set(t_conn, theirs_nodes)
        o_cyc = elem_corner_cycle(o_conn, ours_nodes)
        t_cyc = elem_corner_cycle(t_conn, theirs_nodes)
        if o_set == t_set:
            same_node_set += 1
        if o_cyc == t_cyc:
            same_corner_orient += 1
        if o_set != t_set or o_cyc != t_cyc:
            mismatches.append(
                {
                    "elem_index": k + 1,
                    "ours_ids": list(o_conn),
                    "theirs_ids": list(t_conn),
                    "same_8_positions": o_set == t_set,
                    "same_corner_cycle": o_cyc == t_cyc,
                }
            )

    # Orphan analysis
    ours_used = {n for c in ours_elems for n in c}
    theirs_used = {n for c in theirs_elems for n in c}
    ours_orphan = sorted(set(ours_nodes) - ours_used)
    theirs_orphan = sorted(set(theirs_nodes) - theirs_used)

    report = {
        "ne": args.ne,
        "n_elements": n,
        "elements_same_8_positions": same_node_set,
        "elements_same_corner_orientation": same_corner_orient,
        "ours_orphan_nodes": len(ours_orphan),
        "theirs_orphan_nodes": len(theirs_orphan),
        "theirs_orphan_ids": theirs_orphan,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches[:10],
    }
    report_path = out_dir / f"connectivity_compare_n{args.ne}.json"
    report_path.write_text(json.dumps(report, indent=2))

    print(f"Elements: {n}")
    print(f"Same 8-node position set: {same_node_set}/{n}")
    print(f"Same corner orientation:    {same_corner_orient}/{n}")
    print(f"Orphan nodes (not in any S8): ours={len(ours_orphan)} theirs={len(theirs_orphan)}")
    if theirs_orphan:
        print(f"  theirs orphan ids (first 10): {theirs_orphan[:10]}")
    if mismatches:
        print(f"First mismatch: {mismatches[0]}")
    else:
        print("All elements match by position (connectivity equivalent up to node renumbering).")
    print(f"Report: {report_path}")
    return 0 if same_node_set == n else 1


if __name__ == "__main__":
    raise SystemExit(main())
