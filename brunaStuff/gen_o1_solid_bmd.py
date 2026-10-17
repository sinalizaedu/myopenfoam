#!/usr/bin/env python3
"""Generate the O1 Lamminsalo quarter-eye solid blockMesh dictionary.

The existing O1 fluid dictionary is the source of truth for interface stations
and cell counts.  This generator never reads or modifies it at run time; the
values below are transcribed from its documented analytic construction.

The posterior coat, cornea and lens interfaces reuse the O1 stations, curves,
and divisions. Separate block interpolation leaves a measured sub-micrometre
centroid mismatch. The wall is one face-connected checkMesh region with
per-tissue cellZones (cornea, retina, choroid, sclera, ciliary, iris).  The lens
is an impermeable fluid void (``lens_wall`` on the fluid mesh only); by default
no solid lens is meshed (``--with-lens`` to restore the butterfly body).
The Table-SII iris cannot be conformal on both faces
because the fluid uses 40 anterior and 48 posterior cells.  ``--iris-match``
selects which side controls the solid count; nearest-neighbour preCICE mapping
is therefore retained for the complete wall.
"""
from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

from o1_solid_anatomy import (
    CHOROID_AB,
    CORNEA_INNER,
    CORNEA_OUTER,
    HYALOID,
    IRIS_ANT_MID,
    IRIS_POST_MID,
    N_THETA,
    POSTERIOR_COUNTS,
    POSTERIOR_NAMES,
    POSTERIOR_T_DEG,
    POSTERIOR_VIT,
    POSTERIOR_VIT_MID,
    RETINA_AB,
    SCLERA_AB,
    THETAS,
    T_POSTERIOR,
    Z_SLAB_MM,
    Curve,
    Layers,
    Point,
    along_segment,
    ciliary_outer_from_normals,
    circle_points,
    cornea_outer,
    ellipse_curve,
    ellipse_point,
    lerp_point,
    offset_point,
    parallel_offset,
    parametric_t,
    polyline_normals,
    projected_ellipse,
    quad_convex,
    require_convex,
    stations,
)

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "cases/doc-g2-sim1/solid/system/blockMeshDict.O1solid"
# One face-connected wall region (checkMesh region 0); lens is region 1.
# cellZone names below map to per-tissue E, nu in mechanicalProperties.


@dataclass
class Strip:
    zone: str
    inner: list[Point]
    outer: list[Point]
    counts: list[int]
    inner_curves: list[Curve]
    outer_curves: list[Curve]
    inner_patch: str
    outer_patch: str = "outer"
    radial: int = 4
    label: str = ""
    theta_arcs: bool = True
    grading: str = "1 1 1"
    invert: bool = False
    collapse_outer: bool = False
    start_patch: str = ""  # radial face at inner[0]–outer[0]
    end_patch: str = ""    # radial face at inner[-1]–outer[-1]


@dataclass
class Mesh:
    vertices: list[tuple[float, float, float, str]] = field(default_factory=list)
    lookup: dict[tuple[float, float, float], int] = field(default_factory=dict)
    blocks: list[str] = field(default_factory=list)
    edges: dict[tuple[int, int], str] = field(default_factory=dict)
    patches: dict[str, list[tuple[int, int, int, int]]] = field(default_factory=dict)
    strips: list[Strip] = field(default_factory=list)
    mode: str = "3d"  # "3d" blockMesh wedge; "2d" meridional slab (G1)

    def _key(self, xyz: tuple[float, float, float]) -> tuple[float, float, float]:
        return tuple(round(v, 10) for v in xyz)

    def vertex(self, p: Point, theta: float) -> int:
        # Axis vertices are shared by all theta layers, as in the fluid O1 mesh.
        if abs(p.r) < 1e-12:
            xyz = (0.0, p.y, 0.0)
        else:
            a = math.radians(theta)
            xyz = (p.r * math.cos(a), p.y, p.r * math.sin(a))
        key = self._key(xyz)
        if key not in self.lookup:
            self.lookup[key] = len(self.vertices)
            self.vertices.append((*xyz, p.name))
        return self.lookup[key]

    def vertex2d(self, p: Point, *, back: bool = False) -> int:
        """Meridional slab vertex: x=r, y=axial, z=0 or Z_SLAB (G1)."""
        z = Z_SLAB_MM if back else 0.0
        xyz = (p.r, p.y, z)
        key = self._key(xyz)
        if key not in self.lookup:
            self.lookup[key] = len(self.vertices)
            suffix = "_back" if back else ""
            self.vertices.append((*xyz, p.name + suffix))
        return self.lookup[key]

    def patch(self, name: str, face: tuple[int, int, int, int]) -> None:
        if name:
            self.patches.setdefault(name, []).append(face)


def circle_at_r(center_y: float, radius: float, r: float, *, anterior: bool, name: str) -> Point:
    disc = radius * radius - r * r
    if disc < 0.0:
        raise ValueError(f"{name}: r={r} outside circle R={radius}")
    dy = math.sqrt(disc)
    y = center_y - dy if anterior else center_y + dy
    return Point(r, y, name)


def add_two_layer(
    mesh: Mesh,
    zone: str,
    inner: list[Point],
    outer: list[Point],
    counts: list[int],
    inner_curves: list[Curve],
    outer_curves: list[Curve],
    inner_patch: str,
    n_inner: int,
    n_outer: int,
    outer_patch: str = "outer",
    label: str = "",
    mid: list[Point] | None = None,
    mid_curves: list[Curve] | None = None,
    theta_arcs: bool = True,
    grading: str = "1 1 1",
    invert: bool = False,
    collapse_outer: bool = False,
    start_patch: str = "",
    end_patch: str = "",
) -> None:
    """Two stacked hex layers so a 7+5 wall can share faces with wine/outer."""
    frac = n_inner / (n_inner + n_outer)
    if mid is None:
        mid = [lerp_point(p, q, frac, p.name + "_m") for p, q in zip(inner, outer)]
    if mid_curves is None:
        mid_curves = [Curve()] * len(counts)
    add_strip(mesh, Strip(
        zone, inner, mid, counts, inner_curves, mid_curves,
        inner_patch, outer_patch="", radial=n_inner, label=f"{label} inner",
        theta_arcs=theta_arcs, grading=grading, invert=invert,
        start_patch=start_patch, end_patch=end_patch,
    ))
    add_strip(mesh, Strip(
        zone, mid, outer, counts, mid_curves, outer_curves,
        "", outer_patch=outer_patch, radial=n_outer, label=f"{label} outer",
        theta_arcs=theta_arcs, grading=grading, invert=invert,
        collapse_outer=collapse_outer,
        start_patch=start_patch, end_patch=end_patch,
    ))


def add_curve(mesh: Mesh, a: int, b: int, curve: Curve, theta: float) -> None:
    if a == b or curve.kind == "line":
        return
    key = tuple(sorted((a, b)))
    if key in mesh.edges:
        return
    if curve.kind == "circle":
        cy, _radius = curve.data
        mesh.edges[key] = f"arc {a} {b} origin (0 {cy:.10g} 0)"
    elif curve.kind == "ellipse":
        r, y = curve.data
        ang = math.radians(theta)
        mesh.edges[key] = (
            f"arc {a} {b} ({r * math.cos(ang):.10g} {y:.10g} "
            f"{r * math.sin(ang):.10g})"
        )
    elif curve.kind == "polyline":
        pts = curve.data
        ang = math.radians(theta)
        body = " ".join(
            f"({r * math.cos(ang):.10g} {y:.10g} {r * math.sin(ang):.10g})"
            for r, y in pts
        )
        mesh.edges[key] = f"polyLine {a} {b} ({body})"


def add_strip(mesh: Mesh, strip: Strip) -> None:
    if not (
        len(strip.inner) == len(strip.outer)
        and len(strip.counts) == len(strip.inner) - 1
        and len(strip.inner_curves) == len(strip.counts)
        and len(strip.outer_curves) == len(strip.counts)
    ):
        raise ValueError(f"inconsistent strip {strip.label or strip.zone}")

    mesh.strips.append(strip)
    for seg, tangential in enumerate(strip.counts):
        p0, p1 = strip.inner[seg : seg + 2]
        q0, q1 = strip.outer[seg : seg + 2]
        inner_curve = strip.inner_curves[seg]
        outer_curve = strip.outer_curves[seg]
        same_inner = abs(p0.r - p1.r) < 1e-12 and abs(p0.y - p1.y) < 1e-12
        if strip.collapse_outer:
            # Repeat the outer vertex so blockMesh emits a prism
            # hex (p0 p1 q0 q0 ...).  The collapsed edge sits at the pinch.
            q1 = q0
            outer_curve = Curve()
        prism = strip.collapse_outer or same_inner
        polygon = (p0, p1, q1, q0)
        signed_area = 0.5 * sum(
            polygon[i].r * polygon[(i + 1) % 4].y
            - polygon[(i + 1) % 4].r * polygon[i].y
            for i in range(4)
        )
        if not prism and (signed_area < 0) != strip.invert:
            p0, p1, q0, q1 = p1, p0, q1, q0
            if inner_curve.kind == "polyline":
                inner_curve = Curve("polyline", tuple(reversed(inner_curve.data)))
            if outer_curve.kind == "polyline":
                outer_curve = Curve("polyline", tuple(reversed(outer_curve.data)))

        if same_inner:
            mer = (p0, q0, q1, p0)
        elif (
            not quad_convex([p0, p1, q1, q0])
            and (strip.label or "").endswith("outer")
            and "limba" in (strip.label or "")
        ):
            mer = (p0, p1, q0, q1)
        else:
            mer = (p0, p1, q1, q0)

        if mesh.mode == "2d":
            vf = [mesh.vertex2d(p) for p in mer]
            vb = [mesh.vertex2d(p, back=True) for p in mer]
            ids = vf + vb
            mesh.blocks.append(
                f"    hex ({' '.join(map(str, ids))}) {strip.zone} "
                f"({tangential} {strip.radial} 1) "
                f"simpleGrading ({strip.grading})"
            )
            if same_inner:
                add_curve(mesh, vf[1], vf[2], outer_curve, 0.0)
            else:
                add_curve(mesh, vf[0], vf[1], inner_curve, 0.0)
                add_curve(mesh, vf[3], vf[2], outer_curve, 0.0)
            if same_inner:
                inner_face = (vf[0], vf[0], vf[0], vf[0])
                outer_face = (vf[1], vf[2], vb[2], vb[1])
            else:
                inner_face = (vf[0], vf[1], vb[1], vb[0])
                outer_face = (vf[3], vf[2], vb[2], vb[3])
            if len(set(inner_face)) >= 3:
                mesh.patch(strip.inner_patch, inner_face)
            if len(set(outer_face)) >= 3:
                mesh.patch(strip.outer_patch, outer_face)
            mesh.patch("front", tuple(vf))
            mesh.patch("back", tuple(reversed(vb)))
            continue

        for t0, t1 in zip(THETAS[:-1], THETAS[1:]):
            # Collapsed-inner prism: hex (C Q lim C / …) so the repeated
            # vertex is one hex edge, not the (C C lim Q) inward winding.
            if same_inner:
                mer_w = (p0, q0, q1, p0)
            elif (
                not quad_convex([p0, p1, q1, q0])
                and (strip.label or "").endswith("outer")
                and "limba" in (strip.label or "")
            ):
                mer_w = (p0, p1, q0, q1)
            else:
                mer_w = (p0, p1, q1, q0)
            v0 = [mesh.vertex(p, t0) for p in mer_w]
            v1 = [mesh.vertex(p, t1) for p in mer_w]
            ids = v0 + v1
            mesh.blocks.append(
                f"    hex ({' '.join(map(str, ids))}) {strip.zone} "
                f"({tangential} {strip.radial} {N_THETA}) "
                f"simpleGrading ({strip.grading})"
            )
            if same_inner:
                add_curve(mesh, v0[1], v0[2], outer_curve, t0)
                add_curve(mesh, v1[1], v1[2], outer_curve, t1)
            else:
                add_curve(mesh, v0[0], v0[1], inner_curve, t0)
                add_curve(mesh, v1[0], v1[1], inner_curve, t1)
                add_curve(mesh, v0[3], v0[2], outer_curve, t0)
                add_curve(mesh, v1[3], v1[2], outer_curve, t1)
            for j, p in enumerate(mer_w):
                a, b = v0[j], v1[j]
                if a != b and strip.theta_arcs:
                    add_curve(mesh, a, b, Curve("circle", (p.y, p.r)), t0)

            # Axis prisms have 3 unique vertices; skip only zero-area ribbons.
            if same_inner:
                inner_face = (v0[0], v1[0], v1[0], v0[0])
                outer_face = (v0[1], v0[2], v1[2], v1[1])
            else:
                inner_face = (v0[0], v1[0], v1[1], v0[1])
                outer_face = (v0[3], v0[2], v1[2], v1[3])
            if len(set(inner_face)) >= 3:
                mesh.patch(strip.inner_patch, inner_face)
            if len(set(outer_face)) >= 3:
                mesh.patch(strip.outer_patch, outer_face)
            if not same_inner:
                start_face = (v0[0], v0[3], v1[3], v1[0])
                end_face = (v0[1], v0[2], v1[2], v1[1])
                if seg == 0:
                    mesh.patch(strip.start_patch, start_face)
                if seg == len(strip.counts) - 1:
                    mesh.patch(strip.end_patch, end_face)
            if t0 == THETAS[0]:
                mesh.patch("symmetry_0", tuple(v0))
            if t1 == THETAS[-1]:
                mesh.patch("symmetry_90", tuple(reversed(v1)))


def add_lens_butterfly(mesh: Mesh, args: argparse.Namespace) -> None:
    """Quarter-wedge butterfly: axial core, annular C-grid, two polar caps.

    Capsule stations and tangential counts still sum to the O1 ``fsi_lens``
    set (152 meridional faces × 12 theta = 1824).  The pole blocks no longer
    use M or K as both inner and outer of the same strip.
    """
    r_core = args.lens_core_r
    n_rad = args.n_lens_radial
    n_core_r = n_rad

    M = Point(0.0, -6.07, "M")
    K = Point(0.0, 0.64, "K")
    R = Point(3.0, -5.2270723, "R")
    L = Point(4.75, -3.57, "L")
    W6 = Point(4.53380010, -2.60443900, "W6")
    W5 = Point(4.11925900, -1.70545300, "W5")
    W4 = Point(3.52877400, -0.91087800, "W4")
    W3 = Point(2.78754500, -0.25466200, "W3")
    W2 = Point(1.92726600, 0.23517400, "W2")
    W1 = Point(0.98466162, 0.53770000, "W1")

    def _cang(cy: float, p: Point) -> float:
        return math.atan2(p.r, p.y - cy)

    def _con_circle(cy: float, radius: float, a: float, name: str) -> Point:
        return Point(radius * math.sin(a), cy + radius * math.cos(a), name)

    # Same arc parameter as the fluid O1 M-R (32) and K-W1 (17) blocks.
    a_m1 = _cang(-0.31, M) + 8.0 / 32.0 * (_cang(-0.31, R) - _cang(-0.31, M))
    a_k1 = _cang(-4.15, K) + 8.0 / 17.0 * (_cang(-4.15, W1) - _cang(-4.15, K))
    M1s = _con_circle(-0.31, 5.76, a_m1, "M1s")
    K1s = _con_circle(-4.15, 4.79, a_k1, "K1s")
    if not (0.0 < r_core < min(M1s.r, K1s.r)):
        raise ValueError(
            f"need 0 < lens-core-r < min(M1s,K1s)=({M1s.r:.3f},{K1s.r:.3f}); "
            f"got core={r_core}"
        )
    cap_inset = min(0.010, 0.20 * (M1s.y - M.y), 0.20 * (K.y - K1s.y))
    M1c = Point(r_core, M1s.y + cap_inset, "M1c")
    K1c = Point(r_core, K1s.y - cap_inset, "K1c")
    axis_m1 = Point(0.0, M1c.y, "axis_M1")
    axis_k1 = Point(0.0, K1c.y, "axis_K1")

    if M1c.y >= R.y or K1c.y <= W1.y:
        raise ValueError("lens core cut overlaps the annulus stations")

    front = circle_points(-0.31, 5.76, [M, M1s, R, L])
    rear = circle_points(-4.15, 4.79, [L, W6, W5, W4, W3, W2, W1, K1s, K])

    add_strip(mesh, Strip(
        "lens", [axis_m1, M1c], [M, M1s], [n_core_r],
        [Curve()], [front[0]],
        "", outer_patch="fsi_lens", radial=n_rad, label="lens anterior cap",
    ))
    add_strip(mesh, Strip(
        "lens", [axis_k1, K1c], [K, K1s], [n_core_r],
        [Curve()], [rear[-1]],
        "", outer_patch="fsi_lens", radial=n_rad, label="lens posterior cap",
    ))

    ring_out = [M1s, R, L, W6, W5, W4, W3, W2, W1, K1s]
    ring_in = [M1c] + [Point(r_core, p.y, "core_" + p.name) for p in ring_out[1:-1]] + [K1c]
    ring_counts = [24, 20, 11, 13, 14, 14, 15, 16, 9]
    ring_outer_curves = [front[1], front[2]] + rear[0:7]
    add_strip(mesh, Strip(
        "lens", ring_in, ring_out, ring_counts,
        [Curve()] * len(ring_counts), ring_outer_curves,
        "", outer_patch="fsi_lens", radial=n_rad, label="lens annulus",
    ))

    core_out = ring_in
    core_in = [axis_m1] + [Point(0.0, p.y, "axis_" + p.name) for p in ring_out[1:-1]] + [axis_k1]
    add_strip(mesh, Strip(
        "lens", core_in, core_out, ring_counts,
        [Curve()] * len(ring_counts), [Curve()] * len(ring_counts),
        "", outer_patch="", radial=n_core_r, label="lens core",
    ))


def add_limba_bc(
    mesh: Mesh,
    args: argparse.Namespace,
    B: Point,
    C: Point,
    Bo: Point,
    Q: Point,
    cor_mid_b: Point,
    n_wine: int,
    n_sclera: int,
    frac_w: float,
) -> None:
    """B-C limbus: single 5-cell strip (O1/G1) or convex 2+3 split (H1)."""
    C_m = lerp_point(C, Q, frac_w, "C_m")
    if args.variant == "H1":
        n1, n2 = 2, 3
        t = n1 / (n1 + n2)
        M = lerp_point(B, C, t, "M")
        Mm = lerp_point(cor_mid_b, C_m, t, "M_m")
        Mo = lerp_point(Bo, Q, t, "Mo")
        Mo2 = lerp_point(cor_mid_b, Q, t, "Mo2")
        require_convex([B, M, Mm, cor_mid_b], "H1 limba inner-1")
        require_convex([cor_mid_b, Mm, Mo, Bo], "H1 limba outer-1")
        require_convex([M, C, C_m, Mm], "H1 limba inner-2")
        require_convex([Mm, C_m, Q, Mo2], "H1 limba outer-2")
        add_two_layer(
            mesh, "cornea", [B, M], [Bo, Mo], [n1],
            [Curve()], [Curve()],
            "fsi_active", n_wine, n_sclera, label="limba B-M",
            mid=[cor_mid_b, Mm],
        )
        add_two_layer(
            mesh, "cornea", [M, C], [Mo2, Q], [n2],
            [Curve()], [Curve()],
            "fsi_active", n_wine, n_sclera, label="limba M-C",
            mid=[Mm, C_m],
        )
        return
    add_two_layer(
        mesh, "cornea", [B, C], [Bo, Q], [5],
        [Curve()], [Curve()],
        "fsi_active", n_wine, n_sclera, label="limba B-C",
        mid=[cor_mid_b, C_m],
    )


def build_mesh(args: argparse.Namespace) -> Mesh:
    mesh = Mesh(mode="2d" if args.variant == "G1" else "3d")

    # Cornea-limba: A→T→U→B→C on the fluid wall (60+5 = 65 meridional faces).
    # A single 65-cell hex would smear the O1 32+6+22+5 spacing and break FSI,
    # so the same chain is four strips.  B's outer stays on the outer-cornea
    # circle (Bo).  C's outer is the parallelogram Q = C+(Bo−B); the anatomic
    # lim_out is 12 µm from Bo and turned B–C into a dart (12 inverted hexes).
    # fsi_active meridional: 65 + 5 (D-E) + 12 (E-F) + 100 (J→I + I-H) = 182
    # → 182 × 12 θ = 2184, matching fluid wall.
    A = Point(0.0, -8.16, "A")
    T = Point(3.11, -7.5315989, "T")
    U = Point(3.78, -7.2119900, "U")
    B = Point(6.61, -4.68, "B")
    C = Point(6.70, -4.75, "C")
    cor_in = [A, T, U, B]
    cor_out = [cornea_outer(p, name=p.name + "o") for p in cor_in]
    Bo = cor_out[-1]
    n_wine = args.n_retina + args.n_choroid
    n_wall = n_wine + args.n_sclera
    frac_w = n_wine / n_wall
    cy_m = -0.15 + frac_w * (-0.23 + 0.15)
    R_m = 8.01 + frac_w * (8.29 - 8.01)
    cor_mid = []
    for p, q in zip(cor_in, cor_out):
        if p.name == "B":
            # Circle mid at B is 40 µm off B–Bo and bows the B–C wine hex
            # (12 inverted cells, all one meridional column × 12 θ).
            cor_mid.append(lerp_point(p, q, frac_w, p.name + "_m"))
        else:
            phi = math.atan2(p.r, -(p.y + 0.15))
            cor_mid.append(
                Point(R_m * math.sin(phi), cy_m - R_m * math.cos(phi), p.name + "_m")
            )
    # Circular U–B mid-edge onto lerp B_m (off-circle by 40 µm).  A line
    # across all 22 cells inverted U–B; 21+1 split did not close the C join.
    mid_curves_ab = circle_points(cy_m, R_m, cor_mid)
    # Parallelogram outer at C: Q = C + (Bo−B).  lerp(Bo, lim_out) sits
    # 12 µm from Bo and makes B–C wine non-convex even with lerp B_m.
    Q = Point(C.r + Bo.r - B.r, C.y + Bo.y - B.y, "Co")
    add_two_layer(
        mesh, "cornea", cor_in, cor_out, [32, 6, 22],
        circle_points(-0.15, 8.01, cor_in),
        circle_points(-0.23, 8.29, cor_out),
        "fsi_active", n_wine, args.n_sclera, label="cornea A-B",
        mid=cor_mid, mid_curves=mid_curves_ab,
    )
    C_m = lerp_point(C, Q, frac_w, "C_m")
    require_convex([B, C, C_m, cor_mid[-1]], "limba B-C wine")
    require_convex([cor_mid[-1], C_m, Q, Bo], "limba B-C outer")
    add_limba_bc(mesh, args, B, C, Bo, Q, cor_mid[-1], n_wine, args.n_sclera, frac_w)

    # Posterior retina/choroid/sclera.  Concentric ellipses — do not project
    # the ciliary wall onto these; that fold is what inverted 12 D-E hexes.
    ts = list(POSTERIOR_T_DEG)
    names = list(POSTERIOR_NAMES)
    vit = list(POSTERIOR_VIT)
    ret = [ellipse_point(*RETINA_AB, t, n + "r") for t, n in zip(ts, names)]
    cho = [ellipse_point(*CHOROID_AB, t, n + "c") for t, n in zip(ts, names)]
    scl = [ellipse_point(*SCLERA_AB, t, n + "s") for t, n in zip(ts, names)]
    counts = list(POSTERIOR_COUNTS)
    add_strip(mesh, Strip(
        "retina", vit, ret, counts,
        [Curve("ellipse", p) for p in POSTERIOR_VIT_MID],
        [ellipse_curve(*RETINA_AB, ts[i], ts[i + 1]) for i in range(6)],
        "fsi_active", radial=args.n_retina, outer_patch="",
        label="posterior retina",
    ))
    add_strip(mesh, Strip(
        "choroid", ret, cho, counts,
        [ellipse_curve(*RETINA_AB, ts[i], ts[i + 1]) for i in range(6)],
        [ellipse_curve(*CHOROID_AB, ts[i], ts[i + 1]) for i in range(6)],
        "", radial=args.n_choroid, outer_patch="",
        label="posterior choroid",
    ))
    add_strip(mesh, Strip(
        "sclera", cho, scl, counts,
        [ellipse_curve(*CHOROID_AB, ts[i], ts[i + 1]) for i in range(6)],
        [ellipse_curve(*SCLERA_AB, ts[i], ts[i + 1]) for i in range(6)],
        "", radial=args.n_sclera, label="posterior sclera",
    ))

    # Ciliary: wine then outer so cho[I]-scl[I] is a shared face with the
    # posterior coat.  Ellipse projection is kept here — local-normal offset
    # of the whole chain inverted hundreds of hexes.  The 12-cell failure is
    # the limbus B-C strip (lerp mid at B, no theta arcs), not this coat.
    E = Point(6.84, -4.42, "E")
    F = Point(6.90, -4.02, "F")
    G = Point(6.92, -3.86, "G")
    H = Point(7.00, -3.35, "H")
    I = Point(8.01, -2.00, "I")
    e_blunt = args.e_blunt_mm
    if e_blunt <= 0.0:
        e_blunt = 3.0 / 12.0 * math.hypot(F.r - E.r, F.y - E.y)
    Estar = along_segment(E, F, e_blunt, "Estar")
    cil_in = [Estar, F, G, H, I]
    cil_wine = [projected_ellipse(p, *CHOROID_AB, p.name + "c") for p in cil_in]
    cil_wine[-1] = cho[-1]
    cil_scl = [projected_ellipse(p, *SCLERA_AB, p.name + "s") for p in cil_in]
    cil_scl[-1] = scl[-1]
    wine_ts = [parametric_t(p, *CHOROID_AB) for p in cil_wine]
    scl_ts = [parametric_t(p, *SCLERA_AB) for p in cil_scl]
    for i, (count, patch) in enumerate(zip(
        (9, 6, 8, 11), ("fsi_active", "", "outer", "fsi_active")
    )):
        add_strip(mesh, Strip(
            "ciliary", cil_in[i:i + 2], cil_wine[i:i + 2], [count],
            [Curve("circle", HYALOID) if i == 3 else Curve()],
            [ellipse_curve(*CHOROID_AB, wine_ts[i], wine_ts[i + 1])],
            patch, radial=n_wine, outer_patch="", label=f"ciliary-wine-{i}",
        ))
        add_strip(mesh, Strip(
            "ciliary", cil_wine[i:i + 2], cil_scl[i:i + 2], [count],
            [ellipse_curve(*CHOROID_AB, wine_ts[i], wine_ts[i + 1])],
            [ellipse_curve(*SCLERA_AB, scl_ts[i], scl_ts[i + 1])],
            "", radial=args.n_sclera, label=f"ciliary-outer-{i}",
        ))

    D = Point(6.93, -4.49, "D")
    Es = projected_ellipse(E, *SCLERA_AB, "Es")
    Es_star = projected_ellipse(Estar, *SCLERA_AB, "Es_star")
    t_es = parametric_t(Es, *SCLERA_AB)
    es2_dt = args.es2_dt
    Es2 = ellipse_point(*SCLERA_AB, t_es + es2_dt, "Es2")
    require_convex([C, D, Es2, Q], "C-D to Q-Es2")
    require_convex([D, E, Es, Es2], "D-E to Es2-Es")
    require_convex([E, Estar, Es_star, Es], "E-E* to Es-Es*")

    add_two_layer(
        mesh, "sclera", [C, D], [Q, Es2], [12],
        [Curve()], [Curve()],
        "", n_wine, args.n_sclera, label="TM-back C-D",
    )
    add_two_layer(
        mesh, "sclera", [D, E], [Es2, Es], [5],
        [Curve()], [ellipse_curve(*SCLERA_AB, t_es + es2_dt, t_es)],
        "fsi_active", n_wine, args.n_sclera, label="TM-back D-E",
    )
    frac = n_wine / (n_wine + args.n_sclera)
    E_m = lerp_point(E, Es, frac, "E_m")
    Ec_star = cil_wine[0]
    require_convex([E, Estar, Ec_star, E_m], "tip wine E-E*")
    require_convex([E_m, Ec_star, Es_star, Es], "tip outer E-E*")
    add_strip(mesh, Strip(
        "ciliary", [E, Estar], [E_m, Ec_star], [3],
        [Curve()], [Curve()],
        "fsi_active", radial=n_wine, outer_patch="", label="ciliary tip wine",
    ))
    add_strip(mesh, Strip(
        "ciliary", [E_m, Ec_star], [Es, Es_star], [3],
        [Curve()], [Curve()],
        "", radial=args.n_sclera, outer_patch="", label="ciliary tip outer",
    ))

    if args.with_lens:
        add_lens_butterfly(mesh, args)

    st = stations()
    # Iris: one plate block.  Radial count is 3–5 (Redaelli); the posterior
    # or anterior O1 side controls the tangential count, the other is mapped.
    iris_count = 48 if args.iris_match == "posterior" else 40
    add_strip(mesh, Strip(
        "iris",
        [st["P"], G],
        [st["O"], F],
        [iris_count],
        [Curve("polyline", IRIS_POST_MID)],
        [Curve("polyline", IRIS_ANT_MID)],
        "fsi_iris", outer_patch="fsi_iris", radial=6, label="iris",
    ))
    return mesh


def render(mesh: Mesh, args: argparse.Namespace) -> str:
    header = (
        f"/* O1 Lamminsalo solid variant {args.variant}; "
        f"generated by brunaStuff/gen_o1_solid_bmd.py */"
    )
    if mesh.mode == "2d":
        header += "\n// G1: meridional slab — run extrudeMesh next (see extrudeMeshDict.G1)."
    patch_types = {
        "fsi_active": "wall", "fsi_lens": "wall", "fsi_iris": "wall",
        "outer": "patch", "retina_choroid": "patch",
        "choroid_sclera": "patch", "ciliary_sclera": "patch",
        "lens_axis": "patch", "symmetry_0": "symmetry", "symmetry_90": "symmetry",
        "front": "empty", "back": "empty",
    }
    lines = [
        header,
        "FoamFile",
        "{",
        "    version 2.0;",
        "    format ascii;",
        "    class dictionary;",
        "    object blockMeshDict;",
        "}",
        "",
        "scale 0.001; // coordinates are millimetres",
        "",
        "vertices",
        "(",
    ]
    for i, (x, y, z, name) in enumerate(mesh.vertices):
        lines.append(f"    ({x:.10g} {y:.10g} {z:.10g}) // {i} {name}")
    lines += [");", "", "blocks", "(", *mesh.blocks, ");", "", "edges", "("]
    lines += [f"    {e}" for e in mesh.edges.values()]
    lines += [");", "", "boundary", "("]
    for name, faces in mesh.patches.items():
        lines += [f"    {name}", "    {", f"        type {patch_types.get(name, 'patch')};", "        faces", "        ("]
        lines += [f"            ({' '.join(map(str, f))})" for f in faces]
        lines += ["        );", "    }"]
    # Unlisted end faces cap the lens void and iris/wall junctions.  blockMesh
    # otherwise assigns type ``empty`` to defaultFaces, which would incorrectly
    # turn this 3-D quarter-eye into a zero-dimensional solution mesh.
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
    return "\n".join(lines)


def render_extrude_g1(n_theta: int = 12) -> str:
    """Sector extrude 90 deg → 12 theta layers (matches O1 fsi_active count)."""
    return f"""/* G1: extrude meridional slab to 90-deg wedge ({n_theta} layers). */
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      extrudeMeshDict;
}}
constructFrom mesh;
sourceCase ".";
sourcePatches (front);
extrudeModel sector;
nLayers {n_theta};
expansionRatio 1;
flipNormals false;
sectorCoeffs
{{
    point  (0 0 0);
    axis   (0 1 0);
    angle  90;
}}
mergeFaces false;
"""


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--variant",
        choices=("O1", "H1", "G1"),
        default="O1",
        help="O1=legacy limbus; H1=2+3 split; G1=2D slab for extrudeMesh",
    )
    p.add_argument("--iris-match", choices=("posterior", "anterior"), default="posterior")
    p.add_argument("--n-retina", type=int, default=3)
    p.add_argument("--n-choroid", type=int, default=4)
    p.add_argument("--n-sclera", type=int, default=5)
    p.add_argument("--n-cornea", type=int, default=0,
                   help="0 = n_retina+n_choroid+n_sclera (required for limbus conformity)")
    p.add_argument("--n-iris", type=int, default=4)
    p.add_argument("--n-ciliary", type=int, default=0,
                   help="0 = n_wall so the ora face is conformal")
    p.add_argument("--n-lens-radial", type=int, default=8)
    p.add_argument("--lens-core-r", type=float, default=0.30)
    p.add_argument("--lens-cut-r", type=float, default=0.0, help="unused; cuts follow O1 8/32 and 8/17")
    p.add_argument("--lens-core-inset", type=float, default=0.15)
    p.add_argument("--e-blunt-mm", type=float, default=0.0, help="0 = 3/12 of E-F")
    p.add_argument(
        "--lim-q-frac",
        type=float,
        default=0.50,
        help="outer limbus corner Co = lerp(Bo, lim_out, frac); 0.5–0.75 convex",
    )
    p.add_argument(
        "--es2-dt",
        type=float,
        default=0.12,
        help="ellipse parameter offset (deg) for TM-back outer corner Es2",
    )
    p.add_argument(
        "--with-lens",
        action="store_true",
        help="mesh solid lens (default: lens is fluid void only, like O1 fluid)",
    )
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    try:
        args.layers = Layers(
            n_retina=args.n_retina,
            n_choroid=args.n_choroid,
            n_sclera=args.n_sclera,
            n_cornea=args.n_cornea,
            n_iris=args.n_iris,
            n_ciliary=args.n_ciliary,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    args.n_cornea = args.layers.n_cornea
    args.n_ciliary = args.layers.n_ciliary
    if args.n_lens_radial < 1:
        raise SystemExit("--n-lens-radial must be positive")
    if args.with_lens:
        if args.lens_core_r <= 0.0 or args.lens_core_inset <= 0.0:
            raise SystemExit("--lens-core-r and --lens-core-inset must be positive")
    mesh = build_mesh(args)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render(mesh, args))
    tag = args.variant
    if args.variant == "G1":
        extrude_path = args.out.parent / "extrudeMeshDict.G1"
        extrude_path.write_text(render_extrude_g1())
        print(f"Wrote {extrude_path}")
    print(f"Wrote {args.out}: {len(mesh.vertices)} vertices, {len(mesh.blocks)} blocks [{tag}]")
    if args.with_lens:
        print("Node-aligned: cornea-limbal-coat continuum, butterfly lens; mapped: iris")
    else:
        print("Node-aligned: cornea-limbal-coat continuum; lens void; mapped: iris")


if __name__ == "__main__":
    main()
