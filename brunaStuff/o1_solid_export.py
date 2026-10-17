#!/usr/bin/env python3
"""Export O1 solid strips to Gmsh 2.2, STL, and wall-extruded blockMeshDict.

Used by A1 (wall extrusion), C1 (STL), D1 (Gmsh 2D + revolve).
"""
from __future__ import annotations

import argparse
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from o1_solid_anatomy import (
    CHOROID_AB,
    CORNEA_OUTER,
    N_THETA_TOTAL,
    RETINA_AB,
    SCLERA_AB,
    T_CORNEA,
    T_POSTERIOR,
    VITREOUS_AB,
    Layers,
    Point,
    stations,
)
from plot_o1_solid_mesh import read_boundary, read_faces, read_points, read_labels

# ---------------------------------------------------------------------------
# STL helpers
# ---------------------------------------------------------------------------

def _tri(f, n, a, b, c) -> None:
    f.write(
        f"  facet normal {n[0]:.8e} {n[1]:.8e} {n[2]:.8e}\n"
        "    outer loop\n"
        f"      vertex {a[0]:.8e} {a[1]:.8e} {a[2]:.8e}\n"
        f"      vertex {b[0]:.8e} {b[1]:.8e} {b[2]:.8e}\n"
        f"      vertex {c[0]:.8e} {c[1]:.8e} {c[2]:.8e}\n"
        "    endloop\n"
        "  endfacet\n"
    )


def _norm(a, b, c):
    u = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    v = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
    n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    mag = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2) or 1.0
    return (n[0] / mag, n[1] / mag, n[2] / mag)


def write_ascii_stl(path: Path, tris: list[tuple], name: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        f.write(f"solid {name}\n")
        for a, b, c in tris:
            _tri(f, _norm(a, b, c), a, b, c)
        f.write(f"endsolid {name}\n")


def patch_to_stl(polymesh: Path, patch: str, out: Path) -> int:
    """Triangulate an OpenFOAM patch (already in metres) to STL."""
    points = read_points(polymesh / "points")
    faces = read_faces(polymesh / "faces")
    patches = read_boundary(polymesh / "boundary")
    start, n = patches[patch]
    tris = []
    for fi in range(start, start + n):
        idx = faces[fi]
        pts = [tuple(float(x) for x in points[i]) for i in idx]
        for k in range(1, len(pts) - 1):
            tris.append((pts[0], pts[k], pts[k + 1]))
    write_ascii_stl(out, tris, patch)
    return len(tris)


def _revolve_pt(r: float, y: float, theta: float) -> tuple[float, float, float]:
    return (r * math.cos(theta) * 1e-3, y * 1e-3, r * math.sin(theta) * 1e-3)


def _rotate_y90(p: tuple[float, float, float]) -> tuple[float, float, float]:
    """Match OpenFOAM ``transformPoints -rotate-y 90``: (x,y,z) → (z, y, -x)."""
    x, y, z = p
    return (z, y, -x)


def analytic_outer_stl(out: Path, n_merid: int = 48, n_theta: int = 12, *, case_frame: bool = True) -> int:
    """Outer cornea circle + sclera ellipse, 90° wedge, metres.

    *case_frame* applies the same -rotate-y 90 as the O1 fluid mesh.
    """
    st = stations()
    lim = st["lim_out"]
    tris = []
    thetas = [i * math.pi / 2 / n_theta for i in range(n_theta + 1)]

    def cornea_phi(t: float) -> tuple[float, float]:
        cy, R = CORNEA_OUTER
        phi = t * math.atan2(lim.r, -(lim.y + abs(cy)))
        return R * math.sin(phi), cy - R * math.cos(phi)

    def sclera_t(t: float) -> tuple[float, float]:
        tdeg = t * 106.850
        a, b = SCLERA_AB
        rad = math.radians(tdeg)
        return a * math.sin(rad), b * math.cos(rad)

    def belt(sample, n: int) -> list:
        rows = []
        for i in range(n + 1):
            r, y = sample(i / n)
            row = [_revolve_pt(r, y, th) for th in thetas]
            if case_frame:
                row = [_rotate_y90(p) for p in row]
            rows.append(row)
        return rows

    for rows in (belt(cornea_phi, n_merid // 2), belt(sclera_t, n_merid)):
        for i in range(len(rows) - 1):
            for j in range(len(thetas) - 1):
                a, b = rows[i][j], rows[i][j + 1]
                c, d = rows[i + 1][j], rows[i + 1][j + 1]
                tris.append((a, b, d))
                tris.append((a, d, c))
    write_ascii_stl(out, tris, "outer")
    return len(tris    )


def flip_inward_boundary_faces(case: Path) -> int:
    """Reverse faces listed in wrongOrientedFaces, or inward boundary faces.

    The B1/D1 C-join fold leaves 288 coincident faces that blockMesh emits
    inward-pointing. Flipping them closes the cells without changing topology.
    """
    poly = case / "constant" / "polyMesh"
    faces = [list(map(int, f)) for f in read_faces(poly / "faces")]
    to_flip: list[int] = []
    setp = poly / "sets" / "wrongOrientedFaces"
    if setp.exists():
        text = setp.read_text()
        m = re.search(r"\n(\d+)\s*\(\s*([\d\s]*)\)", text)
        if m:
            to_flip = [int(x) for x in m.group(2).split()]
    if not to_flip:
        points = read_points(poly / "points")
        owner = list(map(int, read_labels(poly / "owner")))
        neighbour = list(map(int, read_labels(poly / "neighbour")))
        n_int = len(neighbour)
        n_cells = max(owner) + 1
        cell_acc = [[0.0, 0.0, 0.0, 0] for _ in range(n_cells)]

        def fcent(idx):
            pts = [points[i] for i in idx]
            n = len(pts) or 1
            return tuple(sum(p[j] for p in pts) / n for j in range(3))

        for fi, c in enumerate(owner):
            fc = fcent(faces[fi])
            cell_acc[c][0] += fc[0]
            cell_acc[c][1] += fc[1]
            cell_acc[c][2] += fc[2]
            cell_acc[c][3] += 1
        for fi, c in enumerate(neighbour):
            fc = fcent(faces[fi])
            cell_acc[c][0] += fc[0]
            cell_acc[c][1] += fc[1]
            cell_acc[c][2] += fc[2]
            cell_acc[c][3] += 1
        centres = [
            (a[0] / (a[3] or 1), a[1] / (a[3] or 1), a[2] / (a[3] or 1))
            for a in cell_acc
        ]
        for fi in range(n_int, len(faces)):
            idx = faces[fi]
            fc = fcent(idx)
            nx, ny, nz = _face_normal(
                [tuple(float(x) for x in points[i]) for i in idx]
            )
            cc = centres[owner[fi]]
            if (fc[0] - cc[0]) * nx + (fc[1] - cc[1]) * ny + (fc[2] - cc[2]) * nz < 0:
                to_flip.append(fi)

    for fi in to_flip:
        faces[fi] = list(reversed(faces[fi]))
    if to_flip:
        text = (poly / "faces").read_text()
        m = re.search(r"(\d+)\s*\(\s*", text)
        if not m:
            raise ValueError("cannot parse faces file")
        head = text[: m.end()]
        body = "\n".join(
            f"{len(idx)}({' '.join(map(str, idx))})" for idx in faces
        )
        (poly / "faces").write_text(head + "\n" + body + "\n)\n")
    return len(to_flip)


# ---------------------------------------------------------------------------
# A1: extrude fluid wall faces along averaged vertex normals
# ---------------------------------------------------------------------------

def _hex_signed_vol(pts: list[tuple[float, float, float]]) -> float:
    """Signed hex volume from 8 points in blockMesh order."""

    def tet(i: int, j: int, k: int, l: int) -> float:
        a, b, c, d = pts[i], pts[j], pts[k], pts[l]
        ba = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
        ca = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
        da = (d[0] - a[0], d[1] - a[1], d[2] - a[2])
        return (
            ba[0] * (ca[1] * da[2] - ca[2] * da[1])
            + ba[1] * (ca[2] * da[0] - ca[0] * da[2])
            + ba[2] * (ca[0] * da[1] - ca[1] * da[0])
        ) / 6.0

    return tet(0, 1, 2, 4) + tet(0, 2, 3, 4) + tet(2, 4, 5, 6) + tet(2, 4, 6, 7) + tet(2, 3, 4, 7)


def write_solid_fields(case: Path) -> None:
    """Write 0/D and 0/solidForce for whatever patches the mesh actually has."""
    patches = read_boundary(case / "constant" / "polyMesh" / "boundary")
    d_bits = []
    f_bits = []
    for name in patches:
        if name.startswith("symmetry"):
            d_bits.append(f"    {name} {{ type symmetry; }}")
            f_bits.append(f"    {name} {{ type symmetry; }}")
        elif name == "fsi_active":
            d_bits.append(
                "    fsi_active\n    {\n        type        solidForce;\n"
                "        forceField  solidForce;\n        value       uniform (0 0 0);\n    }"
            )
            f_bits.append("    fsi_active { type calculated; value uniform (0 0 0); }")
        elif name in ("fsi_iris", "outer"):
            d_bits.append(
                f"    {name}\n    {{\n        type            fixedDisplacement;\n"
                "        displacement    uniform (0 0 0);\n        value           uniform (0 0 0);\n    }"
            )
            f_bits.append(f"    {name} {{ type calculated; value uniform (0 0 0); }}")
        else:
            d_bits.append(
                f"    {name}\n    {{\n        type        solidTraction;\n"
                "        traction    uniform (0 0 0);\n        pressure    uniform 0;\n"
                "        value       uniform (0 0 0);\n    }"
            )
            f_bits.append(f"    {name} {{ type calculated; value uniform (0 0 0); }}")
    header = (
        "FoamFile\n{\n    version 2.0;\n    format ascii;\n"
        "    class volVectorField;\n    object %s;\n}\n\n"
    )
    zero = case / "0"
    zero.mkdir(exist_ok=True)
    (zero / "D").write_text(
        header % "D"
        + "dimensions      [0 1 0 0 0 0 0];\ninternalField   uniform (0 0 0);\n\n"
        + "boundaryField\n{\n"
        + "\n".join(d_bits)
        + "\n}\n"
    )
    (zero / "solidForce").write_text(
        header % "solidForce"
        + "dimensions      [1 1 -2 0 0 0 0];\ninternalField   uniform (0 0 0);\n\n"
        + "boundaryField\n{\n"
        + "\n".join(f_bits)
        + "\n}\n"
    )


def _face_normal(pts) -> tuple[float, float, float]:
    if len(pts) < 3:
        return (0.0, 0.0, 0.0)
    return _norm(pts[0], pts[1], pts[2])


def extrude_wall_bmd(
    fluid_mesh: Path,
    out_dict: Path,
    *,
    n_layers: int = 4,
    patch: str = "wall",
) -> dict:
    """Conformal hex extrusion of *patch* into a standalone blockMeshDict.

    Thickness is piecewise: cornea 0.36 mm, posterior 0.63 mm, ciliary blend.
    Coordinates in the dict are millimetres (scale 0.001).
    """
    points = read_points(fluid_mesh / "points")
    faces = read_faces(fluid_mesh / "faces")
    patches = read_boundary(fluid_mesh / "boundary")
    start, n = patches[patch]
    wall_faces = [list(map(int, faces[fi])) for fi in range(start, start + n)]

    used: dict[int, int] = {}
    for f in wall_faces:
        for i in f:
            used.setdefault(i, len(used))
    inv = {v: k for k, v in used.items()}
    base = [tuple(float(x) * 1e3 for x in points[inv[j]]) for j in range(len(used))]

    acc = [[0.0, 0.0, 0.0] for _ in base]
    for f in wall_faces:
        pts = [tuple(float(x) * 1e3 for x in points[i]) for i in f]
        nx, ny, nz = _face_normal(pts)
        # Wall normals point into the fluid; solid is the opposite direction.
        nx, ny, nz = -nx, -ny, -nz
        for i in f:
            j = used[i]
            acc[j][0] += nx
            acc[j][1] += ny
            acc[j][2] += nz
    nrm = []
    for a in acc:
        mag = math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2) or 1.0
        nrm.append((a[0] / mag, a[1] / mag, a[2] / mag))

    def thickness(p) -> float:
        x, y, z = p
        rr = math.hypot(x, z)
        if y < -4.6:
            return T_CORNEA
        if y > -2.2:
            return T_POSTERIOR
        t = (y + 4.6) / 2.4
        return T_CORNEA + t * (T_POSTERIOR - T_CORNEA)

    layers_pts: list[list[tuple[float, float, float]]] = [base]
    for k in range(1, n_layers + 1):
        frac = k / n_layers
        layer = []
        for p, nvec in zip(base, nrm):
            d = thickness(p) * frac
            layer.append((p[0] + d * nvec[0], p[1] + d * nvec[1], p[2] + d * nvec[2]))
        layers_pts.append(layer)

    def vid(layer: int, j: int) -> int:
        return layer * len(base) + j

    lines = [
        "/* A1: conformal extrusion of O1 fluid wall (o1_solid_export.py) */",
        "FoamFile",
        "{",
        "    version 2.0;",
        "    format ascii;",
        "    class dictionary;",
        "    object blockMeshDict;",
        "}",
        "",
        "scale 0.001;",
        "",
        "vertices",
        "(",
    ]
    for layer in layers_pts:
        for p in layer:
            lines.append(f"    ({p[0]:.10g} {p[1]:.10g} {p[2]:.10g})")
    lines += [");", "", "blocks", "("]

    n_quad = n_tri = n_hex = n_tri_skip = 0
    zone_of = []
    for f in wall_faces:
        ids = [used[i] for i in f]
        if len(ids) == 3:
            # Wedge-tip fan at r=0: blockMesh cannot collapse hexes on the patch.
            # Volume there is covered by adjacent quad columns; FSI uses 2160 quads.
            n_tri_skip += 1
            continue
        if len(ids) == 4:
            a, b, c, d = ids
            n_quad += 1
        else:
            continue
        cy = sum(base[i][1] for i in ids) / len(ids)
        if cy < -4.6:
            zone = "cornea"
        elif cy > -2.2:
            zone = "sclera"
        else:
            zone = "ciliary"
        for k in range(n_layers):
            v = [
                vid(k, a), vid(k, b), vid(k, c), vid(k, d),
                vid(k + 1, a), vid(k + 1, b), vid(k + 1, c), vid(k + 1, d),
            ]
            pts8 = []
            for vi in v:
                layer, j = divmod(vi, len(base))
                pts8.append(layers_pts[layer][j])
            if _hex_signed_vol(pts8) < 0:
                v = [v[0], v[3], v[2], v[1], v[4], v[7], v[6], v[5]]
            lines.append(
                f"    hex ({' '.join(map(str, v))}) {zone} (1 1 1) simpleGrading (1 1 1)"
            )
            n_hex += 1
        zone_of.append(zone)
    lines += [");", "", "edges", "(", ");", "", "boundary", "("]
    # inner = layer 0, outer = last layer
    inner_faces = []
    outer_faces = []
    for f in wall_faces:
        ids = [used[i] for i in f]
        if len(ids) == 3:
            continue
        if len(ids) == 4:
            a, b, c, d = ids
            inner_faces.append((vid(0, a), vid(0, d), vid(0, c), vid(0, b)))
            k = n_layers
            outer_faces.append((vid(k, a), vid(k, b), vid(k, c), vid(k, d)))

    def emit_patch(name: str, ptype: str, flist: list[tuple[int, int, int, int]]) -> None:
        lines.append(f"    {name}")
        lines.append("    {")
        lines.append(f"        type {ptype};")
        lines.append("        faces")
        lines.append("        (")
        for fc in flist:
            lines.append(f"            ({' '.join(map(str, fc))})")
        lines.append("        );")
        lines.append("    }")

    emit_patch("fsi_active", "wall", inner_faces)
    emit_patch("outer", "patch", outer_faces)
    lines += [
        ");",
        "",
        "defaultPatch",
        "{",
        "    name defaultFaces;",
        "    type patch;",
        "}",
        "",
        "mergePatchPairs",
        "(",
        ");",
        "",
    ]
    out_dict.parent.mkdir(parents=True, exist_ok=True)
    out_dict.write_text("\n".join(lines))
    return {
        "faces": n,
        "quads": n_quad,
        "tris": n_tri_skip,
        "hexes": n_hex,
        "n_layers": n_layers,
        "vertices": len(base) * (n_layers + 1),
    }


# ---------------------------------------------------------------------------
# D1: 2D Gmsh from generator strips
# ---------------------------------------------------------------------------

def build_mesh_from_kwargs(**kwargs):
    """Build Lamminsalo strips with the same knobs as gen_o1_solid_bmd."""
    from gen_o1_solid_bmd import build_mesh

    defaults = {
        "variant": "H1",
        "iris_match": "posterior",
        "n_retina": 5,
        "n_choroid": 5,
        "n_sclera": 5,
        "n_cornea": 0,
        "n_iris": 5,
        "n_ciliary": 0,
        "n_lens_radial": 12,
        "lens_core_r": 0.30,
        "lens_core_inset": 0.15,
        "e_blunt_mm": 0.0,
        "lim_q_frac": 0.50,
        "es2_dt": 0.12,
        "with_lens": False,
    }
    defaults.update(kwargs)
    ns = argparse.Namespace(**defaults)
    ns.layers = Layers(
        n_retina=ns.n_retina,
        n_choroid=ns.n_choroid,
        n_sclera=ns.n_sclera,
        n_cornea=ns.n_cornea,
        n_iris=ns.n_iris,
        n_ciliary=ns.n_ciliary,
    )
    ns.n_cornea = ns.layers.n_cornea
    ns.n_ciliary = ns.layers.n_ciliary
    return build_mesh(ns)


def export_gmsh_2d(
    strips,
    out_msh: Path,
    scale: float = 0.001,
    *,
    radial_scale: int = 1,
    tangential_scale: int = 1,
    split_quad_labels: frozenset[str] | None = None,
) -> dict:
    """Write meridional quads (one per strip segment × radial) as Gmsh 2.2."""
    nodes: dict[tuple[float, float], int] = {}
    node_list: list[tuple[float, float, float]] = []
    elems: list[tuple[int, int, list[int]]] = []
    phy: dict[int, tuple[int, str]] = {}
    zone_tag: dict[str, int] = {}
    next_phy = 1

    def nid(p: Point) -> int:
        key = (round(p.r, 8), round(p.y, 8))
        if key not in nodes:
            nodes[key] = len(node_list) + 1
            node_list.append((p.r * scale, p.y * scale, 0.0))
        return nodes[key]

    def zone_phy(name: str) -> int:
        if name not in zone_tag:
            zone_tag[name] = next_phy
            phy[next_phy] = (2, name)
            nonlocal_next = zone_tag[name]
        return zone_tag[name]

    # fix nonlocal
    next_holder = [1]

    def zp(name: str) -> int:
        if name not in zone_tag:
            zone_tag[name] = next_holder[0]
            phy[next_holder[0]] = (2, name)
            next_holder[0] += 1
        return zone_tag[name]

    patch_tag: dict[str, int] = {}

    def zp1(name: str) -> int:
        if name not in patch_tag:
            patch_tag[name] = next_holder[0]
            phy[next_holder[0]] = (1, name)
            next_holder[0] += 1
        return patch_tag[name]

    split_quad_labels = split_quad_labels or frozenset()
    nquad = 0
    ntri = 0
    for strip in strips:
        tag = zp(strip.zone)
        split_diag = strip.label in split_quad_labels
        for seg in range(len(strip.counts)):
            p0, p1 = strip.inner[seg], strip.inner[seg + 1]
            q0, q1 = strip.outer[seg], strip.outer[seg + 1]
            nr = max(1, strip.radial * radial_scale)
            nt = max(1, strip.counts[seg] * tangential_scale)
            grid = []
            for j in range(nr + 1):
                fj = j / nr
                a = Point((1 - fj) * p0.r + fj * q0.r, (1 - fj) * p0.y + fj * q0.y)
                b = Point((1 - fj) * p1.r + fj * q1.r, (1 - fj) * p1.y + fj * q1.y)
                row = []
                for i in range(nt + 1):
                    fi = i / nt
                    row.append(Point((1 - fi) * a.r + fi * b.r, (1 - fi) * a.y + fi * b.y))
                grid.append(row)
            for j in range(nr):
                for i in range(nt):
                    n00 = nid(grid[j][i])
                    n10 = nid(grid[j][i + 1])
                    n11 = nid(grid[j + 1][i + 1])
                    n01 = nid(grid[j + 1][i])
                    if split_diag:
                        elems.append((2, tag, [n00, n10, n11]))
                        elems.append((2, tag, [n00, n11, n01]))
                        ntri += 2
                    else:
                        elems.append((3, tag, [n00, n10, n11, n01]))
                        nquad += 1
            if strip.inner_patch:
                ptag = zp1(strip.inner_patch)
                for i in range(nt):
                    elems.append((1, ptag, [nid(grid[0][i]), nid(grid[0][i + 1])]))
            if strip.outer_patch:
                ptag = zp1(strip.outer_patch)
                for i in range(nt):
                    elems.append((1, ptag, [nid(grid[nr][i]), nid(grid[nr][i + 1])]))

    lines = ["$MeshFormat", "2.2 0 8", "$EndMeshFormat", "$PhysicalNames", str(len(phy))]
    for tag in sorted(phy):
        dim, name = phy[tag]
        lines.append(f'{dim} {tag} "{name}"')
    lines += ["$EndPhysicalNames", "$Nodes", str(len(node_list))]
    for i, (x, y, z) in enumerate(node_list, 1):
        lines.append(f"{i} {x:.16e} {y:.16e} {z:.16e}")
    lines += ["$EndNodes", "$Elements", str(len(elems))]
    for eid, (etype, tag, conn) in enumerate(elems, 1):
        lines.append(f"{eid} {etype} 1 {tag} " + " ".join(map(str, conn)))
    lines.append("$EndElements")
    out_msh.parent.mkdir(parents=True, exist_ok=True)
    out_msh.write_text("\n".join(lines) + "\n")
    return {"n_quad": nquad, "n_tri": ntri}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=("stl-inner", "stl-outer", "extrude", "gmsh2d", "fields", "flip-inward"), required=True)
    ap.add_argument("--fluid-mesh", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--n-layers", type=int, default=4)
    ap.add_argument("--patch", default="wall")
    ap.add_argument("--case", type=Path)
    ap.add_argument("--variant", choices=("O1", "H1", "G1"), default="H1")
    ap.add_argument("--n-retina", type=int, default=5)
    ap.add_argument("--n-choroid", type=int, default=5)
    ap.add_argument("--n-sclera", type=int, default=5)
    ap.add_argument("--n-iris", type=int, default=5)
    ap.add_argument("--radial-scale", type=int, default=1)
    ap.add_argument("--tangential-scale", type=int, default=1)
    ap.add_argument(
        "--split-limbus",
        action="store_true",
        help="split limbus quads diagonally → prisms after revolve",
    )
    ap.add_argument(
        "--split-zones",
        default="",
        help="comma-separated tissue zones whose quads become tris (prisms in 3D)",
    )
    args = ap.parse_args()
    if args.mode == "fields":
        write_solid_fields(args.case or args.out)
        print(f"Wrote 0/D and 0/solidForce in {args.case or args.out}")
        return
    if args.mode == "flip-inward":
        n = flip_inward_boundary_faces(args.case or Path("."))
        print(f"Flipped {n} inward boundary faces in {args.case or Path('.')}")
        return
    if args.out is None:
        raise SystemExit("--out is required for this mode")
    if args.mode == "stl-inner":
        n = patch_to_stl(args.fluid_mesh, args.patch, args.out)
        print(f"Wrote {args.out}: {n} triangles from {args.patch}")
    elif args.mode == "stl-outer":
        n = analytic_outer_stl(args.out)
        print(f"Wrote {args.out}: {n} triangles")
    elif args.mode == "extrude":
        info = extrude_wall_bmd(args.fluid_mesh, args.out, n_layers=args.n_layers, patch=args.patch)
        print(f"Wrote {args.out}: {info}")
    elif args.mode == "gmsh2d":
        mesh = build_mesh_from_kwargs(
            variant=args.variant,
            n_retina=args.n_retina,
            n_choroid=args.n_choroid,
            n_sclera=args.n_sclera,
            n_iris=args.n_iris,
        )
        split_labels = frozenset()
        if args.split_limbus:
            split_labels = split_labels | frozenset(
                s.label for s in mesh.strips if "limba" in s.label.lower()
            )
        if args.split_zones.strip():
            want = {z.strip() for z in args.split_zones.split(",") if z.strip()}
            split_labels = split_labels | frozenset(
                s.label for s in mesh.strips if s.zone in want
            )
        info = export_gmsh_2d(
            mesh.strips,
            args.out,
            radial_scale=args.radial_scale,
            tangential_scale=args.tangential_scale,
            split_quad_labels=split_labels,
        )
        print(
            f"Wrote {args.out}: {info['n_quad']} quads, {info['n_tri']} tris, "
            f"{len(mesh.strips)} strips [{args.variant}]"
        )


if __name__ == "__main__":
    main()
