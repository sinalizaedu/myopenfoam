"""Revolve G2 solid 2D meridional mesh (coat quads) → 90° 3D calotte hexes."""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

from g2_structured_mesh import (
    HEX_FACES,
    REVOLVE_RAD,
    MshData,
    classify_solid_patch,
    read_msh,
    write_msh,
)

N_THETA_2D = {"M1": 8, "M2": 12, "M3": 16}
AXIS_WELD = 1.0e-5

PATCH_2D_TO_3D = {
    "outer": "outer",
    "fsi_active": "fsi_active",
    "fsi_cornea": "fsi_active",
    "fsi_hyaloid": "fsi_active",
    "fsi_iris": "fsi_iris",
    "fsi_lens": "fsi_lens",
    "symmetry_0": "symmetry_0",
}

INTERNAL_2D_PATCHES = frozenset(
    {
        "interface_coat_tm",
        "interface_lens_vitreous",
        "interface_coat_ciliary",
        "fsi_tm",
    }
)

SOLID_3D_PATCHES = (
    "symmetry_0",
    "symmetry_90",
    "outer",
    "fsi_active",
    "fsi_iris",
    "fsi_lens",
    "lens_rim",
)


def _weld_axis_nodes(src: MshData) -> tuple[MshData, dict[int, int]]:
    """Merge 2D nodes on x≈0 with same y (revolve axis)."""
    remap: dict[int, int] = {}
    groups: dict[int, int] = {}
    for nid, (x, y, z) in sorted(src.nodes.items()):
        if abs(x) > AXIS_WELD:
            remap[nid] = nid
            continue
        key = int(round(y / AXIS_WELD))
        if key in groups:
            remap[nid] = groups[key]
        else:
            groups[key] = nid
            remap[nid] = nid

    welded = MshData(nodes={}, elements=[], physical=dict(src.physical))
    for rn in set(remap.values()):
        x, y, z = src.nodes[rn]
        welded.nodes[rn] = (0.0, y, z) if abs(x) <= AXIS_WELD else (x, y, z)
    for etype, phy, nodes in src.elements:
        welded.elements.append((etype, phy, [remap[int(n)] for n in nodes]))
    return welded, remap


def _revolve_point(x: float, y: float, z: float, theta: float) -> tuple[float, float, float]:
    c, s = math.cos(theta), math.sin(theta)
    return x * c + z * s, y, -x * s + z * c


def _face_key(nodes: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sorted(nodes))


def _hex_volume_sign(nodes: dict[int, tuple[float, float, float]], conn: list[int]) -> float:
    """Signed volume of an 8-node hex (Gmsh brick order)."""

    def signed_tet(
        a: tuple[float, float, float],
        b: tuple[float, float, float],
        c: tuple[float, float, float],
        d: tuple[float, float, float],
    ) -> float:
        ba = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
        ca = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
        da = (d[0] - a[0], d[1] - a[1], d[2] - a[2])
        cross = (
            ba[1] * ca[2] - ba[2] * ca[1],
            ba[2] * ca[0] - ba[0] * ca[2],
            ba[0] * ca[1] - ba[1] * ca[0],
        )
        return (cross[0] * da[0] + cross[1] * da[1] + cross[2] * da[2]) / 6.0

    p = [nodes[i] for i in conn]
    return (
        signed_tet(p[0], p[1], p[3], p[4])
        + signed_tet(p[1], p[2], p[3], p[6])
        + signed_tet(p[1], p[4], p[5], p[6])
        + signed_tet(p[3], p[4], p[6], p[7])
        + signed_tet(p[1], p[3], p[4], p[6])
    )


def _prism_volume_sign(
    nodes: dict[int, tuple[float, float, float]],
    b0: int,
    b1: int,
    b2: int,
    t0: int,
    t1: int,
    t2: int,
) -> float:
    def v(a: int, b: int, c: int, d: int) -> float:
        pa, pb, pc, pd = nodes[a], nodes[b], nodes[c], nodes[d]
        return (
            (pb[0] - pa[0]) * ((pc[1] - pa[1]) * (pd[2] - pa[2]) - (pc[2] - pa[2]) * (pd[1] - pa[1]))
            - (pb[1] - pa[1]) * ((pc[0] - pa[0]) * (pd[2] - pa[2]) - (pc[2] - pa[2]) * (pd[0] - pa[0]))
            + (pb[2] - pa[2]) * ((pc[0] - pa[0]) * (pd[1] - pa[1]) - (pc[1] - pa[1]) * (pd[0] - pa[0]))
        ) / 6.0

    return v(b0, b1, b2, t0) + v(b1, b2, t2, t1) + v(b0, b2, t2, t0) + v(b0, t0, t1, b1)


def _flip_hex(conn: list[int]) -> list[int]:
    """Swap bottom face winding to flip hex volume sign."""
    return [conn[0], conn[3], conn[2], conn[1], conn[4], conn[7], conn[6], conn[5]]


def _weld_coincident_nodes(data: MshData, tol: float = 1.0e-12) -> MshData:
    """Merge 3D nodes at identical positions (exact/near-exact duplicates only)."""
    key_to_id: dict[tuple[int, int, int], int] = {}
    remap: dict[int, int] = {}
    welded = MshData(nodes={}, elements=[], physical=dict(data.physical))
    next_id = 1
    for nid in sorted(data.nodes):
        x, y, z = data.nodes[nid]
        key = (round(x / tol), round(y / tol), round(z / tol))
        if key not in key_to_id:
            key_to_id[key] = next_id
            welded.nodes[next_id] = (x, y, z)
            remap[nid] = next_id
            next_id += 1
        else:
            remap[nid] = key_to_id[key]
    for etype, phy, nodes in data.elements:
        welded.elements.append((etype, phy, [remap[int(n)] for n in nodes]))
    return welded


def _hex_face_area(nodes: dict[int, tuple[float, float, float]], fn: tuple[int, ...]) -> float:
    if len(fn) == 4:
        pts = [nodes[n] for n in fn]
        c1 = (
            (pts[1][0] - pts[0][0], pts[1][1] - pts[0][1], pts[1][2] - pts[0][2]),
            (pts[2][0] - pts[0][0], pts[2][1] - pts[0][1], pts[2][2] - pts[0][2]),
        )
        n = (
            c1[0][1] * c1[1][2] - c1[0][2] * c1[1][1],
            c1[0][2] * c1[1][0] - c1[0][0] * c1[1][2],
            c1[0][0] * c1[1][1] - c1[0][1] * c1[1][0],
        )
        return math.sqrt(n[0] * n[0] + n[1] * n[1] + n[2] * n[2])
    if len(fn) == 3:
        a, b, c = (nodes[n] for n in fn)
        return 0.5 * math.sqrt(
            ((b[1] - a[1]) * (c[2] - a[2]) - (b[2] - a[2]) * (c[1] - a[1])) ** 2
            + ((b[2] - a[2]) * (c[0] - a[0]) - (b[0] - a[0]) * (c[2] - a[2])) ** 2
            + ((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])) ** 2
        )
    return 0.0


def revolve_solid_2d_msh(
    msh_2d: Path,
    msh_3d: Path,
    *,
    mesh_level: str = "M1",
    n_theta: int | None = None,
) -> dict:
    """Revolve 2D solid quads 90° about +y → 3D hexes (OpenFOAM .msh)."""
    if n_theta is None:
        n_theta = N_THETA_2D.get(mesh_level, 8)
    src_raw = read_msh(msh_2d)
    src, _ = _weld_axis_nodes(src_raw)
    phy_names = {tag: name for tag, (_, name) in src.physical.items()}

    edge_patch: dict[tuple[int, int], str] = {}
    quads: list[tuple[int, list[int]]] = []
    tris: list[tuple[int, list[int]]] = []
    for etype, phy, nodes in src.elements:
        name = phy_names.get(phy, str(phy))
        if etype == 3 and len(nodes) == 4:
            quads.append((phy, nodes))
        elif etype == 2 and len(nodes) == 3:
            tris.append((phy, nodes))
        elif etype == 1 and len(nodes) == 2:
            a, b = int(nodes[0]), int(nodes[1])
            edge_patch[(min(a, b), max(a, b))] = name

    thetas = [i * REVOLVE_RAD / n_theta for i in range(n_theta + 1)]
    layer_node: dict[tuple[int, int], int] = {}
    out = MshData()
    next_nid = 1

    def node_3d(n2d: int, k: int) -> int:
        key = (n2d, k)
        if key not in layer_node:
            nonlocal next_nid
            x, y, z = src.nodes[n2d]
            x3, y3, z3 = _revolve_point(x, y, z, thetas[k])
            out.nodes[next_nid] = (x3, y3, z3)
            layer_node[key] = next_nid
            next_nid += 1
        return layer_node[key]

    face_count: dict[tuple[int, ...], int] = defaultdict(int)
    face_orient: dict[tuple[int, ...], tuple[int, ...]] = {}
    face_hint: dict[tuple[int, ...], str] = {}

    zone_phy: dict[str, int] = {}
    next_phy = 1
    zone_counts: dict[str, int] = defaultdict(int)
    n_hex_flipped = 0
    n_prism_flipped = 0

    def zone_tag(zname: str) -> int:
        if zname not in zone_phy:
            nonlocal next_phy
            zone_phy[zname] = next_phy
            out.physical[next_phy] = (3, zname)
            next_phy += 1
        return zone_phy[zname]

    def track_face(fn: tuple[int, ...], hint: str = "") -> None:
        key = _face_key(fn)
        if key not in face_count:
            face_orient[key] = fn
        face_count[key] += 1
        if hint and key not in face_hint:
            face_hint[key] = hint

    n_hex_skipped = 0
    min_hex_volume = 1.0e-21

    for phy, conn in quads:
        zname = phy_names.get(phy, f"zone_{phy}")
        if len(conn) != 4:
            continue
        n0, n1, n2, n3 = int(conn[0]), int(conn[1]), int(conn[2]), int(conn[3])
        e01 = (min(n0, n1), max(n0, n1))
        e12 = (min(n1, n2), max(n1, n2))
        e23 = (min(n2, n3), max(n2, n3))
        e30 = (min(n3, n0), max(n3, n0))
        for k in range(n_theta):
            b0, b1, b2, b3 = node_3d(n0, k), node_3d(n1, k), node_3d(n2, k), node_3d(n3, k)
            t0, t1, t2, t3 = node_3d(n0, k + 1), node_3d(n1, k + 1), node_3d(n2, k + 1), node_3d(n3, k + 1)
            hex_conn = [b0, b1, b2, b3, t0, t1, t2, t3]
            if _hex_volume_sign(out.nodes, hex_conn) < 0:
                hex_conn = _flip_hex(hex_conn)
                n_hex_flipped += 1
            if abs(_hex_volume_sign(out.nodes, hex_conn)) < min_hex_volume:
                n_hex_skipped += 1
                continue
            out.elements.append((5, zone_tag(zname), hex_conn))
            zone_counts[zname] += 1

            track_face(tuple(hex_conn[i] for i in HEX_FACES[0]), "symmetry_0" if k == 0 else "")
            track_face(tuple(hex_conn[i] for i in HEX_FACES[1]), "symmetry_90" if k == n_theta - 1 else "")

            side_edges = (
                (tuple(hex_conn[i] for i in HEX_FACES[2]), e01),
                (tuple(hex_conn[i] for i in HEX_FACES[3]), e12),
                (tuple(hex_conn[i] for i in HEX_FACES[4]), e23),
                (tuple(hex_conn[i] for i in HEX_FACES[5]), e30),
            )
            for fn, edge in side_edges:
                ep = edge_patch.get(edge)
                hint = ""
                if ep and ep not in INTERNAL_2D_PATCHES:
                    hint = PATCH_2D_TO_3D.get(ep, "")
                track_face(fn, hint)

    for phy, conn in tris:
        zname = phy_names.get(phy, f"zone_{phy}")
        if len(conn) != 3:
            continue
        n0, n1, n2 = int(conn[0]), int(conn[2]), int(conn[1])
        e01 = (min(n0, n1), max(n0, n1))
        e12 = (min(n1, n2), max(n1, n2))
        e20 = (min(n2, n0), max(n2, n0))
        for k in range(n_theta):
            b0, b1, b2 = node_3d(n0, k), node_3d(n1, k), node_3d(n2, k)
            t0, t1, t2 = node_3d(n0, k + 1), node_3d(n1, k + 1), node_3d(n2, k + 1)
            if _prism_volume_sign(out.nodes, b0, b1, b2, t0, t1, t2) < 0:
                b1, b2 = b2, b1
                t1, t2 = t2, t1
                n_prism_flipped += 1
            out.elements.append((6, zone_tag(zname), [b0, b1, b2, t0, t1, t2]))
            zone_counts[zname] += 1

            track_face((b0, b1, b2), "symmetry_0" if k == 0 else "")
            track_face((t0, t1, t2), "symmetry_90" if k == n_theta - 1 else "")
            for fn, edge in (
                ((b0, b1, t1, t0), e01),
                ((b1, b2, t2, t1), e12),
                ((b2, b0, t0, t2), e20),
            ):
                ep = edge_patch.get(edge)
                hint = ""
                if ep and ep not in INTERNAL_2D_PATCHES:
                    hint = PATCH_2D_TO_3D.get(ep, "")
                track_face(fn, hint)

    patch_phy: dict[str, int] = {}
    patch_export: dict[str, int] = defaultdict(int)
    for key, cnt in face_count.items():
        if cnt != 1:
            continue
        fn = face_orient[key]
        if len(set(fn)) != len(fn):
            continue
        if _hex_face_area(out.nodes, fn) < 1.0e-18:
            continue
        coords = [out.nodes[n] for n in fn]
        cx = sum(p[0] for p in coords) / len(coords)
        cy = sum(p[1] for p in coords) / len(coords)
        cz = sum(p[2] for p in coords) / len(coords)
        pname = face_hint.get(key) or classify_solid_patch(cx, cy, cz)
        if pname not in patch_phy:
            patch_phy[pname] = next_phy
            out.physical[next_phy] = (2, pname)
            next_phy += 1
        phy = patch_phy[pname]
        etype = 3 if len(fn) == 4 else 2
        out.elements.append((etype, phy, list(fn)))
        patch_export[pname] += 1

    out = _weld_coincident_nodes(out)

    patch_counts: dict[str, int] = dict(patch_export)

    n_hex = sum(1 for e in out.elements if e[0] == 5)
    n_prism = sum(1 for e in out.elements if e[0] == 6)
    report = {
        "source_2d": msh_2d.name,
        "mesh_level": mesh_level,
        "n_theta": n_theta,
        "structured": True,
        "from_coat_2d": True,
        "n_hex": n_hex,
        "n_prism": n_prism,
        "n_hex_flipped": n_hex_flipped,
        "n_hex_skipped": n_hex_skipped,
        "n_prism_flipped": n_prism_flipped,
        "n_nodes": len(out.nodes),
        "zones": dict(zone_counts),
        "patches": dict(patch_counts),
        "patches_exported": dict(patch_export),
        "n_quads_2d": len(quads),
        "n_tris_2d": len(tris),
    }
    write_msh(msh_3d, out)
    report_path = msh_3d.parent / f"patch_groups_g2_solid_revolve_{mesh_level}.json"
    report_path.write_text(json.dumps(report, indent=2))
    print(
        f"INFO: solid revolve 2D→3D ({mesh_level}): {len(quads)} quads × {n_theta} layers "
        f"→ {n_hex} hex + {n_prism} prism ({n_hex_flipped} hex flipped), {len(out.nodes)} nodes"
    )
    print(f"Wrote {msh_3d}")
    print(f"Solid revolve report: {report}")
    return report


def revolve_solid_2d_file(
    msh_2d: Path,
    msh_3d: Path,
    *,
    mesh_level: str = "M1",
    n_theta: int | None = None,
) -> dict:
    if not msh_2d.exists():
        raise FileNotFoundError(msh_2d)
    return revolve_solid_2d_msh(msh_2d, msh_3d, mesh_level=mesh_level, n_theta=n_theta)
