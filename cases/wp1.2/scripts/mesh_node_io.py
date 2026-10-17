#!/usr/bin/env python3
"""Read/write nodal coordinates in wp1.1 CalculiX mesh .inp files."""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np

from extract_K import parse_nodes, parse_nsets  # noqa: E402


def coords_dict_to_json(coords: dict[int, np.ndarray]) -> dict:
    return {str(k): [float(v[0]), float(v[1]), float(v[2])] for k, v in coords.items()}


def coords_dict_from_json(data: dict) -> dict[int, np.ndarray]:
    return {int(k): np.array(v, dtype=float) for k, v in data.items()}


def save_coords_json(path: Path, coords: dict[int, np.ndarray]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(coords_dict_to_json(coords), indent=2))


def load_coords_json(path: Path) -> dict[int, np.ndarray]:
    return coords_dict_from_json(json.loads(path.read_text()))


def enforce_symmetry(
    coords: dict[int, np.ndarray],
    nsets: dict[str, list[int]],
    tol: float = 1e-9,
) -> dict[int, np.ndarray]:
    """Snap symmetry-plane nodes after reference update (octant BC)."""
    out = {nid: np.array(x, dtype=float) for nid, x in coords.items()}
    for nid in nsets.get("SYM_X", []):
        if nid in out:
            out[nid][0] = 0.0
    for nid in nsets.get("SYM_Y", []):
        if nid in out:
            out[nid][1] = 0.0
    for nid in nsets.get("SYM_Z", []):
        if nid in out:
            out[nid][2] = 0.0
    return out


def max_coord_delta(
    a: dict[int, np.ndarray],
    b: dict[int, np.ndarray],
) -> float:
    keys = sorted(set(a) & set(b))
    if not keys:
        return float("nan")
    diffs = [float(np.linalg.norm(a[k] - b[k])) for k in keys]
    return float(max(diffs))


def update_mesh_node_coords(mesh_path: Path, coords: dict[int, np.ndarray]) -> None:
    """Rewrite *NODE block in a mesh .inp (in place)."""
    lines = mesh_path.read_text().splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r"^\*NODE\b", line, re.I):
            out.append(line)
            i += 1
            while i < len(lines) and not lines[i].startswith("*"):
                s = lines[i].strip()
                if s and not s.startswith("**"):
                    nid = int(s.split(",")[0].strip())
                    if nid in coords:
                        x, y, z = coords[nid]
                        out.append(f"{nid:8d}, {x: .8f}, {y: .8f}, {z: .8f}")
                    else:
                        out.append(lines[i])
                else:
                    out.append(lines[i])
                i += 1
            continue
        out.append(line)
        i += 1
    mesh_path.write_text("\n".join(out) + "\n")


def deformed_coords(
    x_ref: dict[int, np.ndarray],
    disp: dict[int, tuple[float, float, float]],
) -> dict[int, np.ndarray]:
    out: dict[int, np.ndarray] = {}
    for nid, x0 in x_ref.items():
        du = disp.get(nid, (0.0, 0.0, 0.0))
        out[nid] = x0 + np.asarray(du, dtype=float)
    return out
