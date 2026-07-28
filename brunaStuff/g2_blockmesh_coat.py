"""G2-solid coat 2D quads → OpenFOAM blockMeshDict (90° calotte, solid tissues).

Builds blockMesh-native hex blocks directly from the structured Coat2DBuilder
grid (same topology as g2_coat_2d / g2_solid_2d_revolve): one (1×1×1) block per
(meridional × radial × θ) cell.  Compatible with OpenFOAM ``blockMesh``.

ParaView: run ``blockMesh`` in the solid case, then open ``constant/polyMesh``
with the OpenFOAM reader, or ``foamToVTK`` → ``.vtm``.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from g2_coat_2d import COAT_2D_LEVELS, Coat2DMesh, build_solid_2d_conformal
from g2_solid_2d_revolve import (
    INTERNAL_2D_PATCHES,
    N_THETA_2D,
    PATCH_2D_TO_3D,
    _face_key,
    _flip_hex,
    _hex_volume_sign,
    _revolve_point,
    _weld_axis_nodes,
)
from g2_structured_mesh import HEX_FACES, REVOLVE_RAD, MshData, classify_solid_patch, read_msh


def _coat2d_to_msh(mesh: Coat2DMesh) -> MshData:
    data = MshData(nodes=dict(mesh.nodes), elements=[], physical={})
    next_phy = 1
    for zname, quads in mesh.zones.items():
        phy = next_phy
        data.physical[phy] = (2, zname)
        next_phy += 1
        for q in quads:
            data.elements.append((3, phy, list(q)))
    for zname, tris in mesh.tris.items():
        phy = next_phy
        data.physical[phy] = (2, zname)
        next_phy += 1
        for t in tris:
            data.elements.append((2, phy, list(t)))
    for pname, segs in mesh.patches.items():
        if not segs:
            continue
        phy = next_phy
        data.physical[phy] = (1, pname)
        next_phy += 1
        for a, b in segs:
            data.elements.append((1, phy, [a, b]))
    return data


def _load_coat_2d(msh_2d: Path | Coat2DMesh | MshData) -> MshData:
    if isinstance(msh_2d, MshData):
        return msh_2d
    if isinstance(msh_2d, Coat2DMesh):
        return _coat2d_to_msh(msh_2d)
    return read_msh(msh_2d)


def _face_centroid(verts: list[tuple[float, float, float]], nodes: tuple[int, ...]) -> tuple[float, float, float]:
    pts = [verts[i] for i in nodes]
    n = len(pts)
    return (
        sum(p[0] for p in pts) / n,
        sum(p[1] for p in pts) / n,
        sum(p[2] for p in pts) / n,
    )


def _orient_block(
    verts: list[tuple[float, float, float]],
    b0: int,
    b1: int,
    b2: int,
    b3: int,
    t0: int,
    t1: int,
    t2: int,
    t3: int,
) -> tuple[int, ...] | None:
    """Positive-volume hex; bottom-face flip if needed (matches g2_solid_2d_revolve)."""
    nodes = {i: verts[i] for i in range(len(verts))}
    conn = [b0, b1, b2, b3, t0, t1, t2, t3]
    if len(set(conn)) < 8:
        return None
    if _hex_volume_sign(nodes, conn) < 0:
        conn = _flip_hex(conn)
    if abs(_hex_volume_sign(nodes, conn)) < 1.0e-21:
        return None
    return tuple(conn)


def write_coat_blockmesh_dict(
    msh_2d: Path | Coat2DMesh,
    out_path: Path,
    *,
    mesh_level: str = "M1",
    n_theta: int | None = None,
) -> dict:
    """Structured coat 2D → 3D blockMeshDict (one hex block per θ-slice cell)."""
    if n_theta is None:
        n_theta = N_THETA_2D.get(mesh_level, 8)

    src_raw = _load_coat_2d(msh_2d)
    src, _ = _weld_axis_nodes(src_raw)
    phy_names = {tag: name for tag, (_, name) in src.physical.items()}

    edge_patch: dict[tuple[int, int], str] = {}
    quads: list[tuple[str, list[int]]] = []
    tris: list[tuple[str, list[int]]] = []
    for etype, phy, nodes in src.elements:
        name = phy_names.get(phy, str(phy))
        if etype == 3 and len(nodes) == 4:
            quads.append((name, [int(n) for n in nodes]))
        elif etype == 2 and len(nodes) == 3:
            tris.append((name, [int(n) for n in nodes]))
        elif etype == 1 and len(nodes) == 2:
            a, b = int(nodes[0]), int(nodes[1])
            edge_patch[(min(a, b), max(a, b))] = name

    if tris:
        raise ValueError(
            f"blockMesh coat: {len(tris)} triangle(s) — only quads supported "
            "(use g2_solid_2d_revolve → Gmsh for tri zones)"
        )

    thetas = [i * REVOLVE_RAD / n_theta for i in range(n_theta + 1)]
    layer_vid: dict[tuple[int, int], int] = {}
    verts: list[tuple[float, float, float]] = []

    def node_3d(n2d: int, k: int) -> int:
        key = (n2d, k)
        if key not in layer_vid:
            x, y, z = src.nodes[n2d]
            x3, y3, z3 = _revolve_point(x, y, z, thetas[k])
            if k == 0:
                z3 = 0.0
            if k == n_theta:
                x3 = 0.0
            layer_vid[key] = len(verts)
            verts.append((x3, y3, z3))
        return layer_vid[key]

    vid_to_nk = {vid: nk for nk, vid in layer_vid.items()}  # filled after verts built

    def edge_hint_for_face(fn: tuple[int, ...], k_levels: set[int]) -> str:
        n2d_on_face: set[int] = set()
        for vid in fn:
            n2d, k = vid_to_nk[vid]
            if k in k_levels:
                n2d_on_face.add(n2d)
        if len(n2d_on_face) != 2:
            return ""
        edge = tuple(sorted(n2d_on_face))
        ep = edge_patch.get(edge)
        if not ep or ep in INTERNAL_2D_PATCHES:
            return ""
        return PATCH_2D_TO_3D.get(ep, "")

    # Pre-create all revolved vertices.
    for n2d in src.nodes:
        for k in range(n_theta + 1):
            node_3d(n2d, k)
    vid_to_nk = {vid: nk for nk, vid in layer_vid.items()}

    blocks: list[tuple[int, ...]] = []
    zone_counts: dict[str, int] = defaultdict(int)
    n_hex_skipped = 0

    face_count: dict[tuple[int, ...], int] = defaultdict(int)
    face_orient: dict[tuple[int, ...], tuple[int, ...]] = {}
    face_hint: dict[tuple[int, ...], str] = {}

    def track_face(fn: tuple[int, ...], hint: str = "") -> None:
        key = _face_key(fn)
        if key not in face_count:
            face_orient[key] = fn
        face_count[key] += 1
        if hint and key not in face_hint:
            face_hint[key] = hint

    for zname, conn in quads:
        n0, n1, n2, n3 = conn
        for k in range(n_theta):
            b0, b1, b2, b3 = node_3d(n0, k), node_3d(n1, k), node_3d(n2, k), node_3d(n3, k)
            t0, t1, t2, t3 = node_3d(n0, k + 1), node_3d(n1, k + 1), node_3d(n2, k + 1), node_3d(n3, k + 1)
            v = _orient_block(verts, b0, b1, b2, b3, t0, t1, t2, t3)
            if v is None:
                n_hex_skipped += 1
                continue
            blocks.append(v)
            zone_counts[zname] += 1
            track_face(tuple(v[i] for i in HEX_FACES[0]), "symmetry_0" if k == 0 else "")
            track_face(tuple(v[i] for i in HEX_FACES[1]), "symmetry_90" if k == n_theta - 1 else "")
            k_levels = {k, k + 1}
            for loc in HEX_FACES[2:]:
                fn = tuple(v[i] for i in loc)
                track_face(fn, edge_hint_for_face(fn, k_levels))

    patch_faces: dict[str, list[tuple[int, int, int, int]]] = {
        "symmetry_0": [],
        "symmetry_90": [],
        "outer": [],
        "fsi_active": [],
        "fsi_iris": [],
        "fsi_lens": [],
        "lens_rim": [],
    }
    seen_faces: set[tuple[int, ...]] = set()

    for key, cnt in face_count.items():
        if cnt != 1:
            continue
        fn = face_orient[key]
        if len(set(fn)) != len(fn):
            continue
        if key in seen_faces:
            continue
        seen_faces.add(key)
        cx, cy, cz = _face_centroid(verts, fn)
        pname = face_hint.get(key) or classify_solid_patch(cx, cy, cz)
        if pname not in patch_faces:
            patch_faces["fsi_active"].append(fn)
        else:
            patch_faces[pname].append(fn)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    patch_type = {
        "symmetry_0": "symmetry",
        "symmetry_90": "symmetry",
        "outer": "wall",
        "fsi_active": "wall",
        "fsi_iris": "wall",
        "fsi_lens": "wall",
        "lens_rim": "wall",
    }
    patch_report: dict[str, int] = {}

    with out_path.open("w") as fh:
        fh.write(
            "FoamFile\n{\n"
            "    version     2.0;\n"
            "    format      ascii;\n"
            "    class       dictionary;\n"
            "    object      blockMeshDict;\n"
            "}\n\n"
            f"// G2-solid coat — g2_blockmesh_coat.py  level={mesh_level}  n_theta={n_theta}\n\n"
            "scale   1;\n\n"
            "vertices\n(\n"
        )
        for x, y, z in verts:
            fh.write(f"    ({x:.16e} {y:.16e} {z:.16e})\n")
        fh.write(");\n\nblocks\n(\n")
        for v in blocks:
            fh.write(
                f"    hex ({v[0]} {v[1]} {v[2]} {v[3]} {v[4]} {v[5]} {v[6]} {v[7]}) "
                f"(1 1 1) simpleGrading (1 1 1)\n"
            )
        fh.write(");\n\nboundary\n(\n")
        for pname in patch_faces:
            faces = patch_faces[pname]
            if not faces:
                continue
            patch_report[pname] = len(faces)
            fh.write(f"    {pname}\n    {{\n")
            fh.write(f"        type {patch_type.get(pname, 'wall')};\n")
            fh.write("        faces\n        (\n")
            for a, b, c, d in faces:
                fh.write(f"            ({a} {b} {c} {d})\n")
            fh.write("        );\n    }\n")
        fh.write(");\n\n")

    n_cells = len(blocks)
    report = {
        "mesh_level": mesh_level,
        "n_theta": n_theta,
        "n_blocks": len(blocks),
        "n_cells": n_cells,
        "n_vertices": len(verts),
        "n_hex_skipped": n_hex_skipped,
        "zones": dict(zone_counts),
        "patches": patch_report,
        "method": "blockMesh",
        "from_coat_2d": True,
    }
    print(
        f"Wrote {out_path}  ({n_cells} hexes, {len(blocks)} blocks, "
        f"{len(verts)} verts, patches={patch_report})"
    )
    return report


def mesh_g2_coat_blockmesh(
    bi: dict,
    dict_path: Path,
    *,
    mesh_level: str = "M1",
    n_theta: int | None = None,
) -> dict:
    if mesh_level not in COAT_2D_LEVELS:
        raise ValueError(f"unknown coat 2D mesh_level {mesh_level}")
    cfg = COAT_2D_LEVELS[mesh_level]
    builder = build_solid_2d_conformal(bi, cfg)
    mesh = builder.build()
    report = write_coat_blockmesh_dict(mesh, dict_path, mesh_level=mesh_level, n_theta=n_theta)
    report_path = dict_path.parent / f"patch_groups_g2_coat_blockmesh_{mesh_level}.json"
    report_path.write_text(json.dumps(report, indent=2))
    return report


def mesh_g2_coat_blockmesh_from_msh(
    msh_2d: Path,
    dict_path: Path,
    *,
    mesh_level: str = "M1",
    n_theta: int | None = None,
) -> dict:
    if not msh_2d.exists():
        raise FileNotFoundError(msh_2d)
    report = write_coat_blockmesh_dict(msh_2d, dict_path, mesh_level=mesh_level, n_theta=n_theta)
    report_path = dict_path.parent / f"patch_groups_g2_coat_blockmesh_{mesh_level}.json"
    report_path.write_text(json.dumps(report, indent=2))
    return report


def main() -> None:
    ap = argparse.ArgumentParser(description="G2-solid coat blockMeshDict generator")
    ap.add_argument("--case", default="doc-g3-sim1", help="Case under cases/")
    ap.add_argument("--mesh-level", default="M1", choices=sorted(COAT_2D_LEVELS))
    ap.add_argument("--n-theta", type=int, default=None, help="θ slices (default: N_THETA_2D[level])")
    ap.add_argument("--msh-2d", type=Path, default=None)
    ap.add_argument("--from-builder", action="store_true")
    args = ap.parse_args()

    repo = Path(__file__).resolve().parent.parent
    case = repo / "cases" / args.case
    geom = case / "geometry"
    msh_2d = args.msh_2d or geom / f"eye_g2_solid_2d_{args.mesh_level}.msh"
    dict_path = case / "solid" / "system" / f"blockMeshDict.{args.mesh_level}"

    if args.from_builder or not msh_2d.exists():
        import sys

        sys.path.insert(0, str(repo / "brunaStuff"))
        from gen_lamminsalo_g2 import build_bilateral_m, build_outlines_cm

        bi = build_bilateral_m(build_outlines_cm())
        mesh_g2_coat_blockmesh(bi, dict_path, mesh_level=args.mesh_level, n_theta=args.n_theta)
    else:
        mesh_g2_coat_blockmesh_from_msh(
            msh_2d, dict_path, mesh_level=args.mesh_level, n_theta=args.n_theta,
        )

    active = case / "solid" / "system" / "blockMeshDict"
    active.write_text(dict_path.read_text())
    print(f"Active blockMeshDict → {active}")


if __name__ == "__main__":
    main()
