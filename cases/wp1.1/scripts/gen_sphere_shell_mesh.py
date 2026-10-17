#!/usr/bin/env python3
"""Generate a closed spherical shell mesh (cubic-sphere mapping, S8 or S4).

Full sphere at mean radius R [mm], constant thickness t [mm].
Writes CalculiX *NODE, *ELEMENT, *NSET, *SURFACE blocks.

    python3 gen_sphere_shell_mesh.py --R 12 --t 0.5 --ne 6 --order 2 \\
        --out ../ccx/human_mesh.inp
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

FACE_MAPS = (
    lambda u, v: np.array([1.0, u, v]),
    lambda u, v: np.array([-1.0, u, v]),
    lambda u, v: np.array([u, 1.0, v]),
    lambda u, v: np.array([u, -1.0, v]),
    lambda u, v: np.array([u, v, 1.0]),
    lambda u, v: np.array([u, v, -1.0]),
)


def _nset(fh, name: str, ids: list[int], per_line: int = 8) -> None:
    ids = sorted(set(int(i) for i in ids))
    fh.write(f"*NSET, NSET={name}\n")
    for i in range(0, len(ids), per_line):
        chunk = ids[i : i + per_line]
        fh.write(", ".join(f"{n:7d}" for n in chunk) + "\n")


def _surf(fh, name: str, pairs: list[tuple[int, int]]) -> None:
    fh.write(f"*SURFACE, NAME={name}, TYPE=ELEMENT\n")
    for eid, loc in pairs:
        fh.write(f"{eid:8d}, S{loc}\n")


def _node_key(x: np.ndarray, tol: float) -> tuple[int, int, int]:
    return tuple(int(round(c / tol)) for c in x)


def _orient_nodes(nodes: list[int], coords: dict[int, np.ndarray]) -> list[int]:
    """Ensure element normal points outward (n · r > 0 at centroid)."""
    pts = np.array([coords[n] for n in nodes[:4]])
    c = pts.mean(axis=0)
    e1 = pts[1] - pts[0]
    e2 = pts[3] - pts[0]
    n = np.cross(e1, e2)
    if np.dot(n, c) < 0.0:
        if len(nodes) == 4:
            return [nodes[0], nodes[3], nodes[2], nodes[1]]
        # S8: swap corners 1<->3 and 2<->4, keep mids consistent
        return [
            nodes[0],
            nodes[3],
            nodes[2],
            nodes[1],
            nodes[7],
            nodes[6],
            nodes[5],
            nodes[4],
        ]
    return nodes


def build_mesh(R: float, ne: int, order: int) -> tuple[dict, list, dict, list]:
    """Return coords, elements[(eid, nodes)], nsets, inner_surface pairs."""
    ngrid = 2 * ne + 1 if order == 2 else ne + 1
    tol = R * 1e-9
    key2nid: dict[tuple[int, int, int], int] = {}
    coords: dict[int, np.ndarray] = {}
    nid = 0

    def get_nid(x: np.ndarray) -> int:
        nonlocal nid
        x = x / np.linalg.norm(x) * R
        k = _node_key(x, tol)
        if k not in key2nid:
            nid += 1
            key2nid[k] = nid
            coords[nid] = x
        return key2nid[k]

    def uv_grid(i: int, j: int) -> tuple[float, float]:
        if order == 2:
            u = -1.0 + 2.0 * i / (2 * ne)
            v = -1.0 + 2.0 * j / (2 * ne)
        else:
            u = -1.0 + 2.0 * i / ne
            v = -1.0 + 2.0 * j / ne
        return u, v

    elems: list[tuple[int, list[int]]] = []
    eid = 0
    for fmap in FACE_MAPS:
        grid = np.zeros((ngrid, ngrid), dtype=int)
        for j in range(ngrid):
            for i in range(ngrid):
                u, v = uv_grid(i, j)
                grid[i, j] = get_nid(fmap(u, v))

        step = 2 if order == 2 else 1
        ncell = ne
        for j in range(ncell):
            for i in range(ncell):
                if order == 2:
                    n1 = grid[2 * i, 2 * j]
                    n2 = grid[2 * i + 2, 2 * j]
                    n3 = grid[2 * i + 2, 2 * j + 2]
                    n4 = grid[2 * i, 2 * j + 2]
                    n5 = grid[2 * i + 1, 2 * j]
                    n6 = grid[2 * i + 2, 2 * j + 1]
                    n7 = grid[2 * i + 1, 2 * j + 2]
                    n8 = grid[2 * i, 2 * j + 1]
                    nodes = [n1, n2, n3, n4, n5, n6, n7, n8]
                else:
                    n1 = grid[i, j]
                    n2 = grid[i + 1, j]
                    n3 = grid[i + 1, j + 1]
                    n4 = grid[i, j + 1]
                    nodes = [n1, n2, n3, n4]
                nodes = _orient_nodes(nodes, coords)
                eid += 1
                elems.append((eid, nodes))

    inner_pairs = [(e, 1) for e, _ in elems]  # S1 = inner after outward orientation
    nall = sorted(coords.keys())

    # Rigid-body pin nodes: +X (all), near +Y (y,z), near +Z (z only)
    def _pick(target: np.ndarray) -> int:
        return min(
            nall,
            key=lambda n: float(np.linalg.norm(coords[n] - target)),
        )

    pin1 = _pick(np.array([R, 0.0, 0.0]))
    pin2 = _pick(np.array([0.0, R, 0.0]))
    pin3 = _pick(np.array([0.0, 0.0, R]))

    nsets = {
        "NALL": nall,
        "PIN1": [pin1],
        "PIN2": [pin2],
        "PIN3": [pin3],
    }
    return coords, elems, nsets, inner_pairs


def _clip_to_octant(
    coords: dict[int, np.ndarray],
    elems: list[tuple[int, list[int]]],
    R: float,
) -> tuple[list[tuple[int, list[int]]], dict[str, list[int]], list[tuple[int, int]]]:
    """Keep the x,y,z >= 0 octant; add symmetry plane nsets."""
    tol = R * 1e-6

    def _in_octant(nid: int) -> bool:
        x, y, z = coords[nid]
        return x >= -tol and y >= -tol and z >= -tol

    kept: list[tuple[int, list[int]]] = []
    eid = 0
    used: set[int] = set()
    for _, nodes in elems:
        if all(_in_octant(n) for n in nodes):
            eid += 1
            kept.append((eid, nodes))
            used.update(nodes)

    sym_x: list[int] = []
    sym_y: list[int] = []
    sym_z: list[int] = []
    for nid in sorted(used):
        x, y, z = coords[nid]
        if abs(x) <= tol:
            sym_x.append(nid)
        if abs(y) <= tol:
            sym_y.append(nid)
        if abs(z) <= tol:
            sym_z.append(nid)

    nsets = {
        "NALL": sorted(used),
        "SYM_X": sym_x,
        "SYM_Y": sym_y,
        "SYM_Z": sym_z,
    }
    inner_pairs = [(e, 1) for e, _ in kept]
    return kept, nsets, inner_pairs


def build_spherical_octant(
    R: float,
    ne: int,
    order: int = 2,
    theta_min_deg: float = 3.0,
) -> tuple[dict, list, dict, list]:
    """Spherical (θ, φ) octant mesh: θ∈[θ_min, 90°], φ∈[0, 90°], x,y,z ≥ 0."""
    theta_min = math.radians(theta_min_deg)
    theta_max = math.pi / 2.0
    phi_max = math.pi / 2.0
    ngrid = 2 * ne + 1 if order == 2 else ne + 1
    tol = R * 1e-6

    def _spherical(theta: float, phi: float) -> np.ndarray:
        st, ct = math.sin(theta), math.cos(theta)
        cp, sp = math.cos(phi), math.sin(phi)
        return np.array([R * st * cp, R * st * sp, R * ct])

    key2nid: dict[tuple[int, int, int], int] = {}
    coords: dict[int, np.ndarray] = {}
    nid = 0

    def get_nid(theta: float, phi: float) -> int:
        nonlocal nid
        x = _spherical(theta, phi)
        k = _node_key(x, tol)
        if k not in key2nid:
            nid += 1
            key2nid[k] = nid
            coords[nid] = x
        return key2nid[k]

    def tp_grid(i: int, j: int) -> tuple[float, float]:
        if order == 2:
            theta = theta_min + (theta_max - theta_min) * i / (2 * ne)
            phi = phi_max * j / (2 * ne)
        else:
            theta = theta_min + (theta_max - theta_min) * i / ne
            phi = phi_max * j / ne
        return theta, phi

    grid = np.zeros((ngrid, ngrid), dtype=int)
    for j in range(ngrid):
        for i in range(ngrid):
            theta, phi = tp_grid(i, j)
            grid[i, j] = get_nid(theta, phi)

    elems: list[tuple[int, list[int]]] = []
    eid = 0
    for j in range(ne):
        for i in range(ne):
            if order == 2:
                n1 = grid[2 * i, 2 * j]
                n2 = grid[2 * i + 2, 2 * j]
                n3 = grid[2 * i + 2, 2 * j + 2]
                n4 = grid[2 * i, 2 * j + 2]
                n5 = grid[2 * i + 1, 2 * j]
                n6 = grid[2 * i + 2, 2 * j + 1]
                n7 = grid[2 * i + 1, 2 * j + 2]
                n8 = grid[2 * i, 2 * j + 1]
                nodes = [n1, n2, n3, n4, n5, n6, n7, n8]
            else:
                n1 = grid[i, j]
                n2 = grid[i + 1, j]
                n3 = grid[i + 1, j + 1]
                n4 = grid[i, j + 1]
                nodes = [n1, n2, n3, n4]
            nodes = _orient_nodes(nodes, coords)
            eid += 1
            elems.append((eid, nodes))

    used = sorted({n for _, ns in elems for n in ns})
    sym_x: list[int] = []
    sym_y: list[int] = []
    sym_z: list[int] = []
    for nid in used:
        x, y, z = coords[nid]
        if abs(x) <= tol:
            sym_x.append(nid)
        if abs(y) <= tol:
            sym_y.append(nid)
        if abs(z) <= tol:
            sym_z.append(nid)

    nsets = {
        "NALL": used,
        "SYM_X": sym_x,
        "SYM_Y": sym_y,
        "SYM_Z": sym_z,
    }
    inner_pairs = [(e, 1) for e, _ in elems]
    return coords, elems, nsets, inner_pairs


def build_mesh_with_bc(
    R: float,
    ne: int,
    order: int,
    bc_mode: str = "pins",
    mesh_kind: str = "cubic",
    theta_min_deg: float = 3.0,
) -> tuple[dict, list, dict, list]:
    """Return mesh data.

    bc_mode: ``pins`` | ``symmetry_octant``
    mesh_kind: ``cubic`` (6-face map) | ``spherical`` (θ,φ octant)
    """
    if mesh_kind == "spherical":
        if bc_mode == "pins":
            raise ValueError("spherical mesh requires bc_mode=symmetry_octant")
        return build_spherical_octant(R, ne, order, theta_min_deg=theta_min_deg)
    coords, elems, nsets, inner_pairs = build_mesh(R, ne, order)
    if bc_mode == "pins":
        return coords, elems, nsets, inner_pairs
    if bc_mode == "symmetry_octant":
        elems, nsets, inner_pairs = _clip_to_octant(coords, elems, R)
        return coords, elems, nsets, inner_pairs
    raise ValueError(f"Unknown bc_mode={bc_mode!r}")


def write_mesh(
    out: Path,
    R: float,
    t: float,
    ne: int,
    order: int,
    label: str,
    bc_mode: str = "pins",
    mesh_kind: str = "cubic",
    theta_min_deg: float = 3.0,
    reduced: bool = False,
) -> dict:
    coords, elems, nsets, inner_pairs = build_mesh_with_bc(
        R,
        ne,
        order,
        bc_mode=bc_mode,
        mesh_kind=mesh_kind,
        theta_min_deg=theta_min_deg,
    )
    if order == 2:
        etype = "S8R" if reduced else "S8"
    else:
        etype = "S4"
    out.parent.mkdir(parents=True, exist_ok=True)
    volume_scale = 8 if bc_mode == "symmetry_octant" else 1
    ne_label = f"ne={ne}" if mesh_kind == "spherical" else f"ne/face={ne}"
    with open(out, "w") as fh:
        fh.write(f"** wp1.1 closed spherical shell — {label}\n")
        fh.write(f"** R={R} mm  t={t} mm  {ne_label}  type={etype}\n")
        fh.write(f"** mesh_kind={mesh_kind}  bc_mode={bc_mode}  volume_scale={volume_scale}\n")
        if mesh_kind == "spherical":
            fh.write(f"** theta_min_deg={theta_min_deg}\n")
        fh.write(f"** nodes={len(nsets['NALL'])}  elements={len(elems)}\n")
        fh.write("*NODE, NSET=NALL\n")
        for nid in nsets["NALL"]:
            x, y, z = coords[nid]
            fh.write(f"{nid:8d}, {x: .8f}, {y: .8f}, {z: .8f}\n")
        fh.write(f"*ELEMENT, TYPE={etype}, ELSET=SHELL\n")
        for eid, nodes in elems:
            fh.write(", ".join(f"{v:8d}" for v in [eid, *nodes]) + "\n")
        for name, ids in nsets.items():
            if name != "NALL":
                _nset(fh, name, ids)
        _surf(fh, "INNER_SURF", inner_pairs)

    meta = {
        "R_mm": R,
        "t_mm": t,
        "ne_per_face": ne,
        "ne": ne,
        "order": order,
        "etype": etype,
        "mesh_kind": mesh_kind,
        "bc_mode": bc_mode,
        "volume_scale": volume_scale,
        "n_nodes": len(nsets["NALL"]),
        "n_elements": len(elems),
        "full_sphere_equiv_elements": len(elems) * volume_scale,
    }
    if mesh_kind == "spherical":
        meta["theta_min_deg"] = theta_min_deg
        meta["reduced"] = reduced
    if bc_mode == "pins":
        meta["pin_nodes"] = {k: nsets[k][0] for k in ("PIN1", "PIN2", "PIN3")}
    else:
        meta["symmetry_nsets"] = {k: len(nsets[k]) for k in ("SYM_X", "SYM_Y", "SYM_Z")}
    meta_path = out.with_suffix(".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2))
    return meta


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--R", type=float, required=True, help="mean radius [mm]")
    ap.add_argument("--t", type=float, required=True, help="thickness [mm]")
    ap.add_argument("--ne", type=int, default=6, help="elements per cube face edge")
    ap.add_argument("--order", type=int, choices=(1, 2), default=2, help="1=S4, 2=S8")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--label", default="sphere")
    args = ap.parse_args()
    meta = write_mesh(args.out, args.R, args.t, args.ne, args.order, args.label)
    print(f"wrote {args.out}")
    print(
        f"  {meta['etype']}  nodes={meta['n_nodes']}  "
        f"elements={meta['n_elements']}  ne/face={meta['ne_per_face']}"
    )


if __name__ == "__main__":
    main()
