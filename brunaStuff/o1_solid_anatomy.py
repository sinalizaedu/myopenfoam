#!/usr/bin/env python3
"""Shared O1 Lamminsalo solid landmarks, layer counts, and offset helpers.

Coordinates are millimetres in the generator frame (r, y) used by
``gen_o1_solid_bmd.py``.  ``scale 0.001`` converts them to metres for OpenFOAM.
Each thin wall is 3–5 cells through thickness (Redaelli); posterior tissues
sum to ``n_retina + n_choroid + n_sclera`` so hex blocks share faces at the
limbus and ora.
"""
from __future__ import annotations

import argparse
import math
from dataclasses import dataclass

THETAS = (0.0, 45.0, 90.0)
N_THETA = 6
N_THETA_TOTAL = N_THETA * (len(THETAS) - 1)  # 12 azimuthal cells in the 90° wedge
Z_SLAB_MM = 1.0e-3

# Lamminsalo / Missel coat thicknesses (mm).
T_RETINA = 0.10
T_CHOROID = 0.20
T_SCLERA = 0.33
T_POSTERIOR = T_RETINA + T_CHOROID + T_SCLERA  # 0.63
T_CORNEA = 0.36  # apex: inner y=-8.16 → outer y=-8.52

# Posterior ellipses (equatorial R1, polar R2) and cornea circles.
RETINA_AB = (8.47, 7.00)
CHOROID_AB = (8.67, 7.20)
SCLERA_AB = (9.00, 7.53)
VITREOUS_AB = (8.37, 6.90)
CORNEA_INNER = (-0.15, 8.01)  # (center_y, R)
CORNEA_OUTER = (-0.23, 8.29)
HYALOID = (2.95, 9.41)

LAYER_MIN = 3
LAYER_MAX = 5


@dataclass(frozen=True)
class Point:
    r: float
    y: float
    name: str = ""


@dataclass
class Curve:
    kind: str = "line"  # line, circle, ellipse, polyline
    data: tuple = ()


@dataclass(frozen=True)
class Layers:
    n_retina: int = 3
    n_choroid: int = 4
    n_sclera: int = 5
    n_cornea: int = 0  # 0 → n_wine + n_sclera (hex-conformity default)
    n_iris: int = 4
    n_ciliary: int = 0  # 0 → n_wine + n_sclera

    def __post_init__(self) -> None:
        for name in ("n_retina", "n_choroid", "n_sclera", "n_iris"):
            n = getattr(self, name)
            if not LAYER_MIN <= n <= LAYER_MAX:
                raise ValueError(f"{name} must be in {LAYER_MIN}..{LAYER_MAX}, got {n}")
        if self.n_cornea <= 0:
            object.__setattr__(self, "n_cornea", self.n_wine + self.n_sclera)
        if self.n_ciliary <= 0:
            object.__setattr__(self, "n_ciliary", self.n_wine + self.n_sclera)
        if self.n_cornea != self.n_wall:
            raise ValueError(
                f"n_cornea={self.n_cornea} must equal n_wall={self.n_wall} "
                "so limbus hexes share faces with TM-back and the posterior coat"
            )
        if self.n_ciliary != self.n_wall:
            raise ValueError(
                f"n_ciliary={self.n_ciliary} must equal n_wall={self.n_wall} "
                "so the ora face is conformal"
            )

    @property
    def n_wine(self) -> int:
        return self.n_retina + self.n_choroid

    @property
    def n_wall(self) -> int:
        return self.n_wine + self.n_sclera

    @property
    def frac_wine(self) -> float:
        return self.n_wine / self.n_wall

    @property
    def t_wine(self) -> float:
        return T_RETINA + T_CHOROID


def parse_layer_args(argv: list[str] | None = None) -> Layers:
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--n-retina", type=int, default=3)
    p.add_argument("--n-choroid", type=int, default=4)
    p.add_argument("--n-sclera", type=int, default=5)
    p.add_argument("--n-cornea", type=int, default=0)
    p.add_argument("--n-iris", type=int, default=4)
    p.add_argument("--n-ciliary", type=int, default=0)
    ns, _ = p.parse_known_args(argv)
    return Layers(
        n_retina=ns.n_retina,
        n_choroid=ns.n_choroid,
        n_sclera=ns.n_sclera,
        n_cornea=ns.n_cornea,
        n_iris=ns.n_iris,
        n_ciliary=ns.n_ciliary,
    )


def lerp_point(a: Point, b: Point, frac: float, name: str) -> Point:
    return Point((1.0 - frac) * a.r + frac * b.r, (1.0 - frac) * a.y + frac * b.y, name)


def cornea_outer(p: Point, *, cy: float = -0.23, radius: float = 8.29, name: str = "") -> Point:
    phi = math.atan2(p.r, -(p.y + abs(cy)))
    return Point(radius * math.sin(phi), cy - radius * math.cos(phi), name or f"{p.name}o")


def ellipse_point(a: float, b: float, t_deg: float, name: str) -> Point:
    t = math.radians(t_deg)
    return Point(a * math.sin(t), b * math.cos(t), name)


def ellipse_curve(a: float, b: float, t0: float, t1: float) -> Curve:
    tm = math.radians(0.5 * (t0 + t1))
    return Curve("ellipse", (a * math.sin(tm), b * math.cos(tm)))


def projected_ellipse(p: Point, a: float, b: float, name: str) -> Point:
    t = math.atan2(p.r / a, p.y / b)
    return Point(a * math.sin(t), b * math.cos(t), name)


def parametric_t(p: Point, a: float, b: float) -> float:
    return math.degrees(math.atan2(p.r / a, p.y / b))


def circle_points(center_y: float, radius: float, points: list[Point]) -> list[Curve]:
    return [Curve("circle", (center_y, radius)) for _ in range(len(points) - 1)]


def along_segment(a: Point, b: Point, dist: float, name: str) -> Point:
    dx, dy = b.r - a.r, b.y - a.y
    mag = math.hypot(dx, dy)
    if mag < 1e-12:
        raise ValueError(f"zero-length segment for {name}")
    s = min(dist / mag, 0.49)
    return Point(a.r + s * dx, a.y + s * dy, name)


def _tri_area(a: Point, b: Point, c: Point) -> float:
    return 0.5 * ((b.r - a.r) * (c.y - a.y) - (c.r - a.r) * (b.y - a.y))


def quad_signed_area(pts: list[Point]) -> float:
    return 0.5 * sum(
        pts[i].r * pts[(i + 1) % 4].y - pts[(i + 1) % 4].r * pts[i].y
        for i in range(4)
    )


def quad_convex(pts: list[Point]) -> bool:
    if len(pts) != 4:
        raise ValueError("quad_convex expects 4 points")
    areas = [_tri_area(pts[i], pts[(i + 1) % 4], pts[(i + 2) % 4]) for i in range(4)]
    return all(a > 1e-12 for a in areas) or all(a < -1e-12 for a in areas)


def require_convex(pts: list[Point], label: str) -> None:
    if not quad_convex(pts):
        raise ValueError(
            f"non-convex hex {label}: "
            + ", ".join(f"{p.name}({p.r:.4f},{p.y:.4f})" for p in pts)
        )
    inner = math.hypot(pts[1].r - pts[0].r, pts[1].y - pts[0].y)
    outer = math.hypot(pts[2].r - pts[3].r, pts[2].y - pts[3].y)
    if inner > 1e-9 and outer / inner < 0.15:
        print(
            f"WARNING sliver {label}: outer/inner = {outer / inner:.3f} "
            f"(outer {outer:.4f} mm, inner {inner:.4f} mm)",
            flush=True,
        )


def outward_normal(
    prev: Point,
    p: Point,
    nxt: Point,
    *,
    interior: tuple[float, float] = (0.0, 0.0),
) -> tuple[float, float]:
    """Unit meridional normal at *p* pointing away from the fluid interior."""
    tr, ty = nxt.r - prev.r, nxt.y - prev.y
    mag = math.hypot(tr, ty)
    if mag < 1e-12:
        tr, ty = p.r - interior[0], p.y - interior[1]
        mag = math.hypot(tr, ty) or 1.0
        return (tr / mag, ty / mag)
    n1 = (ty / mag, -tr / mag)
    n2 = (-ty / mag, tr / mag)
    away = (p.r - interior[0], p.y - interior[1])
    if n1[0] * away[0] + n1[1] * away[1] >= n2[0] * away[0] + n2[1] * away[1]:
        return n1
    return n2


def polyline_normals(pts: list[Point]) -> list[tuple[float, float]]:
    nrm: list[tuple[float, float]] = []
    for i, p in enumerate(pts):
        prev = pts[i - 1] if i else pts[0]
        nxt = pts[i + 1] if i + 1 < len(pts) else pts[-1]
        if i == 0:
            prev = Point(p.r - (nxt.r - p.r), p.y - (nxt.y - p.y), "prev")
        if i + 1 == len(pts):
            nxt = Point(p.r + (p.r - prev.r), p.y + (p.y - prev.y), "nxt")
        nrm.append(outward_normal(prev, p, nxt))
    return nrm


def offset_point(p: Point, normal: tuple[float, float], dist: float, name: str) -> Point:
    return Point(p.r + dist * normal[0], p.y + dist * normal[1], name)


def parallel_offset(a: Point, b: Point, dist: float, suffix: str) -> tuple[Point, Point]:
    """Offset segment *a-b* along one shared outward normal (parallelogram)."""
    mid = lerp_point(a, b, 0.5, "mid")
    n = outward_normal(a, mid, b)
    return offset_point(a, n, dist, a.name + suffix), offset_point(b, n, dist, b.name + suffix)


def offset_polyline(pts: list[Point], dist: float, suffix: str) -> list[Point]:
    """Offset a polyline.  Non-convex corners fall back to a parallel segment offset."""
    if len(pts) < 2:
        raise ValueError("offset_polyline needs at least 2 points")
    nrm = polyline_normals(pts)
    out = [offset_point(p, n, dist, p.name + suffix) for p, n in zip(pts, nrm)]
    for i in range(len(pts) - 1):
        quad = [pts[i], pts[i + 1], out[i + 1], out[i]]
        if quad_convex(quad):
            continue
        ao, bo = parallel_offset(pts[i], pts[i + 1], dist, suffix)
        out[i], out[i + 1] = ao, bo
    return out


def blend_to(p: Point, target: Point, frac: float, name: str) -> Point:
    """frac=0 keeps *p*; frac=1 snaps to *target*."""
    return lerp_point(p, target, frac, name)


# ---------------------------------------------------------------------------
# Canonical inner-wall stations (mm).  Names match blockMeshDict.O1 comments.
# ---------------------------------------------------------------------------

def stations() -> dict[str, Point]:
    return {
        "A": Point(0.0, -8.16, "A"),
        "T": Point(3.11, -7.5315989, "T"),
        "U": Point(3.78, -7.2119900, "U"),
        "B": Point(6.61, -4.68, "B"),
        "C": Point(6.70, -4.75, "C"),
        "lim_out": Point(6.87, -4.87, "lim_out"),
        "D": Point(6.93, -4.49, "D"),
        "E": Point(6.84, -4.42, "E"),
        "F": Point(6.90, -4.02, "F"),
        "G": Point(6.92, -3.86, "G"),
        "H": Point(7.00, -3.35, "H"),
        "I": Point(8.01, -2.00, "I"),
        "J": Point(0.0, 6.90, "J"),
        "P": Point(3.00, -5.27, "P"),
        "O": Point(3.11, -5.38, "O"),
    }


POSTERIOR_T_DEG = (0.0, 18.0, 36.0, 54.0, 72.0, 90.0, 106.850)
POSTERIOR_NAMES = ("J", "S1", "S2", "S3", "S4", "S5", "I")
POSTERIOR_VIT = (
    Point(0.0, 6.90, "J"),
    Point(2.58647221, 6.56228999, "S1"),
    Point(4.91976254, 5.58221723, "S2"),
    Point(6.77147221, 4.05571823, "S3"),
    Point(7.96034307, 2.13221723, "S4"),
    Point(8.37, 0.0, "S5"),
    Point(8.01, -2.00, "I"),
)
POSTERIOR_COUNTS = (17, 16, 15, 14, 14, 13)
POSTERIOR_VIT_MID = (
    (1.30935652, 6.81504955),
    (3.79990049, 6.14794499),
    (5.91848375, 4.87903678),
    (7.45772457, 3.13253445),
    (8.26695141, 1.07939784),
    (8.27967096, -1.01096040),
)

IRIS_ANT_MID = ((3.78, -4.94), (6.075475, -4.26313))
IRIS_POST_MID = ((3.69, -4.81), (5.21718, -4.36082941))


def ciliary_outer_from_normals(
    inner: list[Point],
    *,
    snap_start: Point | None,
    snap_end: Point | None,
    dist: float,
    suffix: str,
    end_blend: float = 0.35,
) -> list[Point]:
    """Offset *inner* by *dist* along local outward normals.

    *snap_start* / *snap_end* replace the first / last offset so the strip
    shares vertices with the limbus and the posterior coat.  A short blend
    near the ora avoids a kink that would invert the last hex.
    """
    raw = offset_polyline(inner, dist, suffix)
    out = list(raw)
    if snap_start is not None:
        out[0] = Point(snap_start.r, snap_start.y, inner[0].name + suffix)
    if snap_end is not None:
        out[-1] = Point(snap_end.r, snap_end.y, inner[-1].name + suffix)
        if len(out) >= 3 and end_blend > 0.0:
            out[-2] = blend_to(raw[-2], out[-1], end_blend, inner[-2].name + suffix)
    return out
