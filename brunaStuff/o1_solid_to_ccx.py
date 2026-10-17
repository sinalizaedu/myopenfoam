#!/usr/bin/env python3
"""Convert an O1/B2 OpenFOAM solid polyMesh (hex + axis prisms) to CalculiX.

Emits C3D8I hexes and C3D6 wedges, NSETs per patch, extra AXIS / POSTERIOR_POLE
sets, and *SURFACE definitions for *DSLOAD on fsi_active and fsi_iris.

    python3 brunaStuff/o1_solid_to_ccx.py \\
        --polymesh cases/fsi-transient-o1-patch/solid_meshes/B2/constant/polyMesh \\
        --out cases/fea-sim/ccx/fea-sim_mesh.inp
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "artigo_mestrado"))
import foam_polymesh_to_ccx_inp as fp  # noqa: E402


# ---------------------------------------------------------------------------
# Mixed hex / prism reconstruction
# ---------------------------------------------------------------------------

def _cell_faces(owner: np.ndarray, neighbour: np.ndarray, n_cells: int) -> List[List[int]]:
    cell_faces: List[List[int]] = [[] for _ in range(n_cells)]
    for f, c in enumerate(owner):
        cell_faces[int(c)].append(f)
    for f, c in enumerate(neighbour):
        cell_faces[int(c)].append(f)
    return cell_faces


def _orient_polygon_inward(verts: List[int], points: np.ndarray, centroid: np.ndarray) -> List[int]:
    """Return verts ordered so the polygon normal points toward centroid."""
    p = points[np.asarray(verts)]
    if len(verts) == 3:
        nrm = np.cross(p[1] - p[0], p[2] - p[0])
        fc = p.mean(axis=0)
    else:
        nrm = np.cross(p[1] - p[0], p[-1] - p[0])
        fc = p.mean(axis=0)
    if np.dot(nrm, centroid - fc) < 0:
        return list(reversed(verts))
    return list(verts)


def reconstruct_hex(cf: List[int], faces: List[List[int]], points: np.ndarray, c: int):
    all_v = set()
    for f in cf:
        all_v.update(faces[f])
    if len(all_v) != 8:
        raise ValueError(f"hex cell {c}: {len(all_v)} unique verts")
    v_list = list(all_v)
    centroid = points[v_list].mean(axis=0)
    face_a_idx = cf[0]
    face_a = faces[face_a_idx]
    face_a_set = set(face_a)
    face_b_idx = None
    for f in cf[1:]:
        if not (set(faces[f]) & face_a_set):
            face_b_idx = f
            break
    if face_b_idx is None:
        raise ValueError(f"hex cell {c}: no opposite face")
    face_a_ord = _orient_polygon_inward(list(face_a), points, centroid)
    side_faces = [f for f in cf if f not in (face_a_idx, face_b_idx)]
    face_b_set = set(faces[face_b_idx])
    v_top = [-1, -1, -1, -1]
    for i, va in enumerate(face_a_ord):
        for sf_idx in side_faces:
            sf_verts = faces[sf_idx]
            if va not in sf_verts:
                continue
            j = sf_verts.index(va)
            for nb in (sf_verts[(j - 1) % 4], sf_verts[(j + 1) % 4]):
                if nb in face_b_set:
                    v_top[i] = nb
                    break
            if v_top[i] != -1:
                break
        if v_top[i] == -1:
            raise ValueError(f"hex cell {c}: v_top[{i}] missing")
    conn = np.empty(8, dtype=np.int32)
    conn[0:4] = face_a_ord
    conn[4:8] = v_top
    return conn, centroid


def reconstruct_prism(cf: List[int], faces: List[List[int]], points: np.ndarray, c: int):
    tris = [f for f in cf if len(faces[f]) == 3]
    quads = [f for f in cf if len(faces[f]) == 4]
    if len(tris) != 2 or len(quads) != 3:
        raise ValueError(f"prism cell {c}: tris={len(tris)} quads={len(quads)}")
    all_v = set()
    for f in cf:
        all_v.update(faces[f])
    centroid = points[list(all_v)].mean(axis=0)
    bot = _orient_polygon_inward(list(faces[tris[0]]), points, centroid)
    top_set = set(faces[tris[1]])
    top = [-1, -1, -1]
    for i, va in enumerate(bot):
        for qf in quads:
            qv = faces[qf]
            if va not in qv:
                continue
            j = qv.index(va)
            for nb in (qv[(j - 1) % 4], qv[(j + 1) % 4]):
                if nb in top_set:
                    top[i] = nb
                    break
            if top[i] != -1:
                break
        if top[i] == -1:
            raise ValueError(f"prism cell {c}: top[{i}] missing")
    conn = np.empty(6, dtype=np.int32)
    conn[0:3] = bot
    conn[3:6] = top
    return conn, centroid


def reconstruct_all(points, faces, owner, neighbour, n_cells):
    cell_faces = _cell_faces(owner, neighbour, n_cells)
    kinds: List[str] = [""] * n_cells
    conn_hex = np.full((n_cells, 8), -1, dtype=np.int32)
    conn_prism = np.full((n_cells, 6), -1, dtype=np.int32)
    centroids = np.empty((n_cells, 3), dtype=np.float64)
    n_hex = n_prism = 0
    for c in range(n_cells):
        cf = cell_faces[c]
        nfaces = len(cf)
        if nfaces == 6:
            conn, cen = reconstruct_hex(cf, faces, points, c)
            kinds[c] = "hex"
            conn_hex[c] = conn
            centroids[c] = cen
            n_hex += 1
        elif nfaces == 5:
            conn, cen = reconstruct_prism(cf, faces, points, c)
            kinds[c] = "prism"
            conn_prism[c] = conn
            centroids[c] = cen
            n_prism += 1
        else:
            raise ValueError(f"cell {c}: {nfaces} faces (not hex or prism)")
    print(f"      hex={n_hex}  prism={n_prism}")
    return kinds, conn_hex, conn_prism, centroids


def find_face_hex(face_set, conn8) -> Optional[int]:
    f1 = {conn8[0], conn8[1], conn8[2], conn8[3]}
    f2 = {conn8[4], conn8[5], conn8[6], conn8[7]}
    f3 = {conn8[0], conn8[1], conn8[5], conn8[4]}
    f4 = {conn8[1], conn8[2], conn8[6], conn8[5]}
    f5 = {conn8[2], conn8[3], conn8[7], conn8[6]}
    f6 = {conn8[3], conn8[0], conn8[4], conn8[7]}
    for k, fset in enumerate((f1, f2, f3, f4, f5, f6), start=1):
        if face_set == fset:
            return k
    return None


def find_face_prism(face_set, conn6) -> Optional[int]:
    # C3D6: S1=1-2-3, S2=4-5-6, S3=1-2-5-4, S4=2-3-6-5, S5=3-1-4-6
    faces_ccx = (
        {conn6[0], conn6[1], conn6[2]},
        {conn6[3], conn6[4], conn6[5]},
        {conn6[0], conn6[1], conn6[4], conn6[3]},
        {conn6[1], conn6[2], conn6[5], conn6[4]},
        {conn6[2], conn6[0], conn6[3], conn6[5]},
    )
    for k, fset in enumerate(faces_ccx, start=1):
        if face_set == fset:
            return k
    return None


def face_local(kinds, conn_hex, conn_prism, c: int, face_verts) -> int:
    fs = set(face_verts)
    if kinds[c] == "hex":
        loc = find_face_hex(fs, conn_hex[c])
    else:
        loc = find_face_prism(fs, conn_prism[c])
    if loc is None:
        raise ValueError(f"face of cell {c} ({kinds[c]}) did not match a CCX side")
    return loc


# ---------------------------------------------------------------------------
# Writers
# ---------------------------------------------------------------------------

def write_nset(fh, name: str, node_ids_0based, per_line: int = 8):
    ids = sorted(set(int(v) + 1 for v in node_ids_0based))
    if not ids:
        return
    fh.write(f"*NSET, NSET={name}\n")
    for i in range(0, len(ids), per_line):
        chunk = ids[i:i + per_line]
        fh.write(", ".join(f"{n:7d}" for n in chunk) + "\n")


def write_surface(fh, name: str, pairs: List[Tuple[int, int]]):
    fh.write(f"*SURFACE, NAME={name}, TYPE=ELEMENT\n")
    for eid, loc in pairs:
        fh.write(f"{eid:8d}, S{loc}\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--polymesh", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    pm = args.polymesh

    print(f"[1/4] reading {pm}")
    points = fp.parse_points(pm / "points")
    faces = fp.parse_faces(pm / "faces")
    owner = fp.parse_label_list(pm / "owner")
    neighbour = fp.parse_label_list(pm / "neighbour")
    boundary = fp.parse_boundary(pm / "boundary")
    cell_zones = fp.parse_cell_zones(pm / "cellZones")
    n_cells = int(owner.max()) + 1
    print(f"      nodes={len(points)} cells={n_cells} patches={list(boundary)} "
          f"zones={list(cell_zones)}")

    print("[2/4] reconstructing mixed hex/prism connectivity")
    kinds, conn_hex, conn_prism, centroids = reconstruct_all(
        points, faces, owner, neighbour, n_cells
    )

    axis_nodes = [i for i, p in enumerate(points) if hypot_xz(p) < 1e-9]
    # posterior pole of the OUTER surface: max y among axis nodes, else max y overall
    if axis_nodes:
        posterior = max(axis_nodes, key=lambda i: points[i, 1])
    else:
        posterior = int(np.argmax(points[:, 1]))

    print("[3/4] writing", args.out)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as fh:
        fh.write("** O1/B2 solid → CalculiX (C3D8I + C3D6)\n")
        fh.write(f"** source: {pm}\n")
        fh.write("*NODE, NSET=NALL\n")
        for i, (x, y, z) in enumerate(points, start=1):
            fh.write(f"{i:8d}, {x: .8e}, {y: .8e}, {z: .8e}\n")

        # hex elements grouped by zone
        for zname, zcells in cell_zones.items():
            hex_cells = [int(c) for c in zcells if kinds[int(c)] == "hex"]
            prism_cells = [int(c) for c in zcells if kinds[int(c)] == "prism"]
            if hex_cells:
                fh.write(f"*ELEMENT, TYPE=C3D8I, ELSET={zname.upper()}\n")
                for c in hex_cells:
                    v = conn_hex[c] + 1
                    fh.write(
                        f"{c + 1:8d}, {v[0]:8d}, {v[1]:8d}, {v[2]:8d}, {v[3]:8d}, "
                        f"{v[4]:8d}, {v[5]:8d}, {v[6]:8d}, {v[7]:8d}\n"
                    )
            if prism_cells:
                # prisms share the zone ELSET via GENERATE-style second block
                fh.write(f"*ELEMENT, TYPE=C3D6, ELSET={zname.upper()}\n")
                for c in prism_cells:
                    v = conn_prism[c] + 1
                    fh.write(
                        f"{c + 1:8d}, {v[0]:8d}, {v[1]:8d}, {v[2]:8d}, "
                        f"{v[3]:8d}, {v[4]:8d}, {v[5]:8d}\n"
                    )

        for pname, (start, n) in boundary.items():
            face_idx = list(range(start, start + n))
            verts = []
            for f in face_idx:
                verts.extend(faces[f])
            write_nset(fh, pname.upper(), verts)

        write_nset(fh, "AXIS", axis_nodes)
        write_nset(fh, "POSTERIOR_POLE", [posterior])

        for pname, (start, n) in boundary.items():
            pairs = []
            for f in range(start, start + n):
                c = int(owner[f])
                loc = face_local(kinds, conn_hex, conn_prism, c, faces[f])
                pairs.append((c + 1, loc))
            write_surface(fh, f"{pname.upper()}_SURF", pairs)

    print(f"[4/4] wrote {args.out}  axis_nodes={len(axis_nodes)}  "
          f"posterior_pole={posterior + 1}")


def hypot_xz(p) -> float:
    return float(np.hypot(p[0], p[2]))


if __name__ == "__main__":
    main()
