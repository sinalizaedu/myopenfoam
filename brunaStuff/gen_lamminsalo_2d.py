#!/usr/bin/env python3
"""
G1 anatomical rabbit-eye geometry (Missel 2012 / Lamminsalo 2018 Tables SI–SII).

2D planar bilateral (mirror about optical axis), empty slab in z.

Coordinate tables are in cm (Missel):
  X = radial (perpendicular to optical axis)
  Z = optical axis, positive = posterior

OpenFOAM mapping (SI meters):
  x = X * 1e-2   (mirror x -> -x for left half)
  y = Z * 1e-2   (optical axis)
  z in [0, 1e-3]

Usage:
  .venv-geom/bin/python brunaStuff/gen_lamminsalo_2d.py
  .venv-geom/bin/python brunaStuff/gen_lamminsalo_2d.py --mesh
  .venv-geom/bin/python brunaStuff/gen_lamminsalo_2d.py --case doc-g1-sim1 --mesh
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

# ---------------------------------------------------------------------------
# Units
# ---------------------------------------------------------------------------
CM = 1.0  # table values
M_PER_CM = 1.0e-2
Z_SLAB_M = 1.0e-3

REPO = Path(__file__).resolve().parents[1]
DEFAULT_CASE = "doc-g1-sim1"


def case_paths(case_name: str = DEFAULT_CASE):
    case = REPO / "cases" / case_name
    return case, case / "geometry", case / "figures"


# ---------------------------------------------------------------------------
# Table SI / SII key data (cm) — Lamminsalo ESM
# ---------------------------------------------------------------------------
# Ellipse: (x/R1)^2 + (z/R2)^2 = 1, centre (Xcent, Zcent) usually (0,0)
SURFACES = {
    "outer_sclera": dict(R1=0.900, R2=0.753, xc=0.0, zc=0.0),
    "choroid_sclera": dict(R1=0.867, R2=0.720, xc=0.0, zc=0.0),
    "retina_choroid": dict(R1=0.847, R2=0.700, xc=0.0, zc=0.0),
    "vitreous_retina": dict(R1=0.837, R2=0.690, xc=0.0, zc=0.0),
    "lens_rear": dict(R=0.479, xc=0.0, zc=-0.415),
    "lens_front": dict(R=0.576, xc=0.0, zc=-0.031),
    "cornea_outside": dict(R=0.829, xc=0.0, zc=-0.023),
    "cornea_inside": dict(R=0.801, xc=0.0, zc=-0.015),
    "hyaloid_curved": dict(R=0.941, xc=0.0, zc=0.295),
    "ciliary_hyaloid": dict(R=0.965, xc=0.0, zc=0.321),
    "ciliary_sclera": dict(R=0.904, xc=0.0, zc=0.149),
}

PTS = {
    # Table SI intersections
    "lens_eq_hyaloid": (0.475, -0.357),
    "hyaloid_curved_flat": (0.700, -0.335),
    "hyaloid_retina": (0.801, -0.200),
    "outer_sclera_cornea": (0.687, -0.487),
    "inner_sclera_cornea": (0.661, -0.468),
    "ciliary_tm_aqueous_sclera": (0.684, -0.442),
    # Table SII (iris / TM / ciliary) — base model WITHOUT canal of Petit
    "iris_ciliary_post": (0.692, -0.386),
    "iris_ciliary_ant": (0.690, -0.402),
    "iris_turn_post": (0.369, -0.481),
    "iris_turn_ant": (0.378, -0.494),
    "iris_tip_post": (0.300, -0.527),
    "iris_tip_ant": (0.311, -0.538),
    "tm_cornea_void": (0.670, -0.475),
    "tm_ciliary_void": (0.693, -0.449),
}


# ---------------------------------------------------------------------------
# Curve helpers (cm)
# ---------------------------------------------------------------------------
def ellipse_point(R1: float, R2: float, xc: float, zc: float, phi: float):
    """phi=0 → +X equator; phi increases toward +Z (posterior)."""
    return xc + R1 * math.cos(phi), zc + R2 * math.sin(phi)


def ellipse_phi_at(R1: float, R2: float, xc: float, zc: float, x: float, z: float) -> float:
    return math.atan2((z - zc) / R2, (x - xc) / R1)


def circle_point(R: float, xc: float, zc: float, phi: float):
    return xc + R * math.cos(phi), zc + R * math.sin(phi)


def circle_phi_at(R: float, xc: float, zc: float, x: float, z: float) -> float:
    return math.atan2(z - zc, x - xc)


def sample_ellipse_arc(name: str, p0, p1, n: int = 48, through_posterior: bool = True):
    s = SURFACES[name]
    R1, R2, xc, zc = s["R1"], s["R2"], s["xc"], s["zc"]
    phi0 = ellipse_phi_at(R1, R2, xc, zc, *p0)
    phi1 = ellipse_phi_at(R1, R2, xc, zc, *p1)
    if through_posterior:
        # Prefer the posterior-going arc (phi increasing through +pi/2) when wrapping
        if phi1 < phi0:
            phi1 += 2 * math.pi
        phis = np.linspace(phi0, phi1, n)
    else:
        # Shortest arc (used for anterior choroid–sclera wine segment)
        d = phi1 - phi0
        if d > math.pi:
            d -= 2 * math.pi
        elif d < -math.pi:
            d += 2 * math.pi
        phis = phi0 + np.linspace(0.0, d, n)
    return np.array([ellipse_point(R1, R2, xc, zc, float(p)) for p in phis])


def sample_circle_arc(name: str, p0, p1, n: int = 40, direction: str = "auto"):
    s = SURFACES[name]
    R, xc, zc = s["R"], s["xc"], s["zc"]
    phi0 = circle_phi_at(R, xc, zc, *p0)
    phi1 = circle_phi_at(R, xc, zc, *p1)
    d = phi1 - phi0
    if direction == "ccw":
        if d < 0:
            d += 2 * math.pi
    elif direction == "cw":
        if d > 0:
            d -= 2 * math.pi
    else:
        # shortest
        if d > math.pi:
            d -= 2 * math.pi
        elif d < -math.pi:
            d += 2 * math.pi
    phis = phi0 + np.linspace(0.0, d, n)
    return np.array([circle_point(R, xc, zc, float(p)) for p in phis])


def to_xy_m(pts_cm: np.ndarray) -> np.ndarray:
    """Missel (X,Z) cm → OpenFOAM (x,y) m."""
    out = np.empty_like(pts_cm, dtype=float)
    out[:, 0] = pts_cm[:, 0] * M_PER_CM
    out[:, 1] = pts_cm[:, 1] * M_PER_CM
    return out


def mirror_x(pts: np.ndarray) -> np.ndarray:
    m = pts.copy()
    m[:, 0] *= -1.0
    return m


# ---------------------------------------------------------------------------
# Tissue outlines (right half, cm) — closed or open polylines for plotting
# ---------------------------------------------------------------------------
def build_outlines_cm() -> dict[str, np.ndarray]:
    P = PTS
    S = SURFACES

    lim_out = P["outer_sclera_cornea"]
    z_cor_ant = S["cornea_outside"]["zc"] - S["cornea_outside"]["R"]
    cor_apex = (0.0, z_cor_ant)
    cornea_out = sample_circle_arc("cornea_outside", cor_apex, lim_out, n=50, direction="ccw")
    post_pole = (0.0, S["outer_sclera"]["R2"])
    sclera_out = sample_ellipse_arc("outer_sclera", lim_out, post_pole, n=60)

    # Retina / vitreous–retina stop at the ora (hyaloid–retina).
    # Sclera meets TM on the outer face only (adjacent, no shared interior),
    # then follows choroid–sclera around the posterior pole to the other side.
    # Choroid *fill* still ends at the retina cut (no choroid past the ora).
    hy_ret = P["hyaloid_retina"]

    def shell_from_anchor(surf, anchor_xz, n=55):
        s = SURFACES[surf]
        phi = ellipse_phi_at(s["R1"], s["R2"], s["xc"], s["zc"], *anchor_xz)
        start = ellipse_point(s["R1"], s["R2"], s["xc"], s["zc"], phi)
        pole = (0.0, s["R2"])
        return sample_ellipse_arc(surf, start, pole, n=n), start, phi

    vit_ret, vit_ant, _ = shell_from_anchor("vitreous_retina", hy_ret)
    retina_ch, ret_ant, phi_cut = shell_from_anchor("retina_choroid", hy_ret)

    lim_in = P["inner_sclera_cornea"]
    tm_corners = [
        lim_in,
        P["tm_cornea_void"],
        P["tm_ciliary_void"],
        P["ciliary_tm_aqueous_sclera"],
    ]
    tm_min_y = min(tm_corners, key=lambda p: p[1])
    tm_max_y = max(tm_corners, key=lambda p: p[1])
    tm_ymax = tm_max_y  # alias for ciliary / TM contacts

    s_out = SURFACES["outer_sclera"]
    s_cho = SURFACES["choroid_sclera"]

    # Choroid–sclera frontier starts at TM max-Y angle (after the TM wrap)
    phi_tm = ellipse_phi_at(s_cho["R1"], s_cho["R2"], s_cho["xc"], s_cho["zc"], *tm_max_y)
    cho_tm = ellipse_point(s_cho["R1"], s_cho["R2"], s_cho["xc"], s_cho["zc"], phi_tm)

    choroid_scl = sample_ellipse_arc(
        "choroid_sclera", cho_tm, (0.0, s_cho["R2"]), n=70
    )
    sclera_post = sclera_out  # lim_out → posterior pole

    # Choroid fill only from retina cut → pole
    cho_ret = ellipse_point(s_cho["R1"], s_cho["R2"], s_cho["xc"], s_cho["zc"], phi_cut)
    choroid_ret = sample_ellipse_arc(
        "choroid_sclera", cho_ret, (0.0, s_cho["R2"]), n=55
    )

    # Ora endcap only through retina + choroid (NOT across sclera)
    shell_endcap = np.array([vit_ant, ret_ant, cho_ret])
    hyaloid_stub = np.array([vit_ant, ret_ant])

    # Sclera TM wrap — outer face of TM only (adjacent, no shared interior):
    # lim_out → min-Y → TM max-X (tm_ciliary_void) → max-Y.
    # Do NOT go to min-X (lim_in): that AC-facing corner would swallow the TM.
    tm_max_x = max(tm_corners, key=lambda p: p[0])
    sclera_tm_wrap = np.array(
        [lim_out, tm_min_y, tm_max_x, tm_max_y], dtype=float
    )

    def _snap_pole(arc: np.ndarray) -> np.ndarray:
        """Force posterior tip onto the optical axis (kills L/R seam wedges)."""
        out = np.asarray(arc, dtype=float).copy()
        out[-1, 0] = 0.0
        return out

    def _shell_band(outer_arc: np.ndarray, inner_arc: np.ndarray) -> np.ndarray:
        """Closed half-band with on-axis radial endcap at the pole (no white wedge)."""
        outer = _snap_pole(outer_arc)
        inner = _snap_pole(inner_arc)
        pole_o = outer[-1]
        pole_i = inner[-1]
        # outer ant→pole_o → pole_i (axis thickness) → inner near-pole→ant → close
        band = np.vstack(
            [
                outer,
                pole_i.reshape(1, 2),
                inner[-2::-1],
                outer[0:1],
            ]
        )
        return band

    def _shell_band_full(
        outer_r: np.ndarray, outer_l: np.ndarray, inner_r: np.ndarray, inner_l: np.ndarray
    ) -> np.ndarray:
        """One continuous bilateral shell band (no L/R pole seam)."""
        or_, ol = _snap_pole(outer_r), _snap_pole(outer_l)
        ir_, il = _snap_pole(inner_r), _snap_pole(inner_l)
        full = np.vstack(
            [
                or_,                 # ant_r → pole_o
                ol[-2::-1],          # → ant_o_l
                il[0:1],             # ora chord to ant_i_l
                il[1:],              # → pole_i
                ir_[-2::-1],         # → ant_i_r
                or_[0:1],            # ora chord close
            ]
        )
        if np.linalg.norm(full[-1] - full[0]) > 1e-15:
            full = np.vstack([full, full[0:1]])
        return full

    # Snap posterior arcs used below
    choroid_scl = _snap_pole(choroid_scl)
    choroid_ret = _snap_pole(choroid_ret)
    sclera_post = _snap_pole(sclera_post)
    retina_ch = _snap_pole(retina_ch)
    vit_ret = _snap_pole(vit_ret)

    # Right-half sclera: wrap TM → choroid to pole → axis to sclera pole → outer back
    band_sclera = np.vstack(
        [
            sclera_tm_wrap,
            np.asarray(cho_tm, dtype=float).reshape(1, 2),
            choroid_scl[1:],
            sclera_post[-1:].reshape(1, 2),  # include outer pole on axis
            sclera_post[-2::-1],
        ]
    )
    if np.linalg.norm(band_sclera[-1] - band_sclera[0]) > 1e-15:
        band_sclera = np.vstack([band_sclera, band_sclera[0:1]])
    band_choroid = _shell_band(choroid_ret, retina_ch)
    band_retina = _shell_band(retina_ch, vit_ret)

    # Cornea inside: apex → inner limbus ONLY (never close limbus-to-limbus across
    # both sides — that false chord cuts through the lens on the bilateral plot).
    z_cor_in = S["cornea_inside"]["zc"] - S["cornea_inside"]["R"]
    cornea_in = sample_circle_arc(
        "cornea_inside", (0.0, z_cor_in), lim_in, n=50, direction="ccw"
    )

    # Short limbal connector inner-cornea → outer wall at limbus (angle closure)
    limbus_close = np.array([lim_in, lim_out])

    # Closed cornea stroma (right half): outer apex→lim_out → lim_in → inner lim_in→apex
    band_cornea = np.vstack(
        [
            cornea_out,
            np.asarray(lim_in, dtype=float).reshape(1, 2),
            cornea_in[-2::-1],
            cornea_out[0:1],  # explicit close on anterior apex
        ]
    )
    eq = P["lens_eq_hyaloid"]
    z_front_apex = S["lens_front"]["zc"] - S["lens_front"]["R"]
    z_rear_apex = S["lens_rear"]["zc"] + S["lens_rear"]["R"]
    lens_front = sample_circle_arc(
        "lens_front", (0.0, z_front_apex), eq, n=40, direction="ccw"
    )
    lens_rear = sample_circle_arc(
        "lens_rear", eq, (0.0, z_rear_apex), n=40, direction="ccw"
    )
    lens = np.vstack([lens_front, lens_rear[1:]])

    # Hyaloid: lens equator → curved hyaloid → vitreous–retina junction
    # (not a cornea→lens chord)
    hyaloid = sample_circle_arc(
        "hyaloid_curved", P["hyaloid_curved_flat"], P["hyaloid_retina"], n=35, direction="ccw"
    )
    hyaloid = np.vstack([np.array(eq).reshape(1, 2), np.array(P["hyaloid_curved_flat"]).reshape(1, 2), hyaloid])

    # Iris — Lamminsalo ESM Table SII polyline (Missel Fig. 7), NOT a curve.
    # Order: anterior root → anterior turn (dobra) → tip ant → tip post →
    #        posterior turn → posterior root → close.
    # Coordinates (cm): exact Table SII values; no spline / gap shifting.
    iris = np.array(
        [
            P["iris_ciliary_ant"],   # Iris–ciliary body, anterior
            P["iris_turn_ant"],      # Iris turning point, anterior (dobra)
            P["iris_tip_ant"],       # Iris tip, anterior corner
            P["iris_tip_post"],      # Iris tip, posterior corner
            P["iris_turn_post"],     # Iris turning point, posterior (dobra)
            P["iris_ciliary_post"],  # Iris–ciliary body, posterior
            P["iris_ciliary_ant"],   # close root
        ],
        dtype=float,
    )
    # Gap iris–lens already ≥ 30 µm at Table SII tip corners (Lamminsalo base model).
    # Do NOT move tip coordinates — keep Lamminsalo parameters exact.

    # Iris–ciliary attachment (geometry only; not plotted as big markers)
    iris_ciliary_pts = np.array(
        [P["iris_ciliary_ant"], P["iris_ciliary_post"]], dtype=float
    )

    # Closed ciliary body:
    #   TM max-Y → purple hyaloid point → retina (ora) → choroid (ora)
    #   → return along wine choroid–sclera frontier → TM max-Y
    purple = P["hyaloid_curved_flat"]
    # hyaloid segment purple → retina junction (skip shared first of sampled arc)
    hy_to_ret = np.vstack(
        [
            np.asarray(purple, dtype=float).reshape(1, 2),
            hyaloid[2:],  # arc after purple (hyaloid[0]=eq, [1]=purple)
        ]
    )
    # Short wine segment along choroid–sclera: ora choroid → cho at TM max-Y
    wine = sample_ellipse_arc(
        "choroid_sclera", cho_ret, cho_tm, n=40, through_posterior=False
    )
    band_ciliary = np.vstack(
        [
            np.asarray(tm_ymax, dtype=float).reshape(1, 2),
            hy_to_ret,
            np.asarray(ret_ant, dtype=float).reshape(1, 2),  # touch retina
            np.asarray(cho_ret, dtype=float).reshape(1, 2),  # touch choroid
            wine[1:],
            np.asarray(tm_ymax, dtype=float).reshape(1, 2),  # close
        ]
    )
    ciliary_body = np.array([tm_ymax, purple], dtype=float)

    # Closed TM = quadrilateral:
    #   3 vertices with highest Y (Missel TM / ciliary intersections)
    #   + corner of smallest X on the INNER cornea (lim_in), not outer limbus.
    # Boundary order around the angle (inner cornea → AC/TM → ciliary → scleral)
    tm = np.array(
        [
            lim_in,                # inner cornea (min-X corner)
            P["tm_cornea_void"],
            P["tm_ciliary_void"],
            P["ciliary_tm_aqueous_sclera"],
            lim_in,
        ]
    )
    tm_ymax_pt = max(
        [lim_in, P["tm_cornea_void"], P["tm_ciliary_void"], P["ciliary_tm_aqueous_sclera"]],
        key=lambda p: p[1],
    )
    # Purple connector stops at TM max-Y vertex
    tm_iris_hyaloid = np.array([tm_ymax_pt, P["hyaloid_curved_flat"]])

    ciliary = np.array(
        [
            P["iris_ciliary_post"],
            P["iris_ciliary_ant"],
            P["tm_ciliary_void"],
            P["ciliary_tm_aqueous_sclera"],
            P["hyaloid_retina"],
            P["hyaloid_curved_flat"],
            eq,
        ]
    )

    outer_wall = np.vstack([cornea_out, sclera_out[1:]])

    return {
        "outer_wall": outer_wall,
        "cornea_outside": cornea_out,
        "cornea_inside": cornea_in,  # open arc only (apex→limbus)
        "band_cornea": band_cornea,
        "limbus_close": limbus_close,
        "outer_sclera": sclera_out,
        "choroid_sclera": choroid_scl,
        "choroid_ret": choroid_ret,  # ora→pole (choroid fill outer)
        "retina_choroid": retina_ch,
        "vitreous_retina": vit_ret,
        "sclera_post": sclera_post,
        "band_sclera": band_sclera,
        "band_choroid": band_choroid,
        "band_retina": band_retina,
        "shell_endcap": shell_endcap,
        "sclera_tm_wrap": sclera_tm_wrap,
        "hyaloid_stub": hyaloid_stub,
        "lens": lens,
        "hyaloid": hyaloid,
        "iris": iris,
        "iris_ciliary_pts": iris_ciliary_pts,
        "ciliary_body": ciliary_body,
        "band_ciliary": band_ciliary,
        "tm_markers": tm,
        "tm_iris_hyaloid": tm_iris_hyaloid,
        "ciliary_markers": ciliary,
        "limbus_outer": np.array([lim_out]),
        "post_pole": np.array([post_pole]),
    }


def densify_polyline(pts: np.ndarray, n_per_seg: int = 8) -> np.ndarray:
    """Linear subdivision of each segment — keeps corners (iris turns) exact."""
    pts = np.asarray(pts, dtype=float)
    if len(pts) < 2:
        return pts
    closed = np.linalg.norm(pts[0] - pts[-1]) < 1e-14
    core = pts[:-1] if closed else pts
    out = []
    n = len(core)
    n_seg = n if closed else n - 1
    for i in range(n_seg):
        a = core[i]
        b = core[(i + 1) % n]
        for k in range(n_per_seg):
            t = k / n_per_seg
            out.append((1.0 - t) * a + t * b)
    if closed:
        out.append(core[0].copy())
    else:
        out.append(core[-1].copy())
    return np.asarray(out, dtype=float)


def enforce_iris_lens_gap(iris_cm: np.ndarray, gap_cm: float) -> np.ndarray:
    """Report-only check: Lamminsalo tip corners must stay on Table SII.

    Historical helper that used to nudge tip_z — disabled so the iris remains
    the exact polygonal Table SII silhouette (cil → turn → tip).
    """
    del gap_cm  # documented minimum 30 µm already satisfied by Table SII tips
    return np.asarray(iris_cm, dtype=float).copy()


# ---------------------------------------------------------------------------
# Bilateral outlines in meters (OpenFOAM xy)
# ---------------------------------------------------------------------------
def build_bilateral_m(outlines_cm: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    bi = {}
    for k, arr in outlines_cm.items():
        if arr.ndim != 2 or arr.shape[0] == 0:
            continue
        right = to_xy_m(arr)
        left = mirror_x(right)
        bi[f"{k}_right"] = right
        bi[f"{k}_left"] = left
        # Closed silhouette about the optical axis (must already end/start on axis
        # or pass the posterior pole — never invent a limbus-to-limbus chord).
        if k == "outer_wall":
            full = np.vstack([right, left[-2::-1]])
            bi[f"{k}_full"] = full
        if k in ("vitreous_retina", "choroid_sclera", "retina_choroid"):
            # Posterior shells: arc right → pole → arc left (no anterior chord)
            full = np.vstack([right, left[-2::-1]])
            bi[f"{k}_full"] = full
        if k == "lens":
            # Right half: front apex → eq → rear apex; left returns without
            # duplicating apices. Explicitly close onto the front apex so the
            # stroke has no optical-axis gap (fill already looks closed).
            full = np.vstack([right, left[-2:0:-1], right[0:1]])
            bi["lens_full"] = full
    # Closed vitreous chamber: hyaloid (±) + vitreous–retina shell + lens rear.
    # Right hyaloid ends at hyaloid–retina; vitreous–retina arc goes to the pole;
    # left hyaloid returns to the left lens equator; lens rear closes equator→equator.
    if all(
        k in bi
        for k in (
            "hyaloid_right",
            "hyaloid_left",
            "vitreous_retina_right",
            "vitreous_retina_left",
            "lens_right",
            "lens_left",
        )
    ):
        hy_r = bi["hyaloid_right"]
        hy_l = bi["hyaloid_left"]
        vit_r = bi["vitreous_retina_right"].copy()
        vit_l = bi["vitreous_retina_left"].copy()
        vit_r[-1, 0] = 0.0
        vit_l[-1, 0] = 0.0
        # lens_* : front apex → equator → rear apex; rear face only = equator→rear apex
        ie_r = int(np.argmax(np.abs(bi["lens_right"][:, 0])))
        ie_l = int(np.argmax(np.abs(bi["lens_left"][:, 0])))
        lens_rear_r = bi["lens_right"][ie_r:]  # right eq → rear apex
        lens_rear_l = bi["lens_left"][ie_l:]  # left eq → rear apex
        # Walk: right hyaloid → vit shell (R→pole→L) → left hyaloid rev → lens rear L→apex→R
        vit_shell = np.vstack([vit_r, vit_l[-2::-1]])
        # Drop duplicate join at hyaloid–retina if coincident with hy_r[-1]
        if np.linalg.norm(vit_shell[0] - hy_r[-1]) < 1e-9:
            vit_shell = vit_shell[1:]
        lens_post = np.vstack([lens_rear_l, lens_rear_r[-2::-1]])
        # hy_l ends at left hyaloid–retina; hy_l[::-1] starts there → left eq
        # Drop first of hy_l[::-1] if duplicate with vit_shell end; drop last of lens_post
        # if duplicate with hy_r[0] when matplotlib closes — keep explicit close to hy_r[0].
        hy_l_rev = hy_l[::-1]
        if np.linalg.norm(hy_l_rev[0] - vit_shell[-1]) < 1e-9:
            hy_l_rev = hy_l_rev[1:]
        if np.linalg.norm(lens_post[0] - hy_l_rev[-1]) < 1e-9:
            lens_post = lens_post[1:]
        chamber = np.vstack([hy_r, vit_shell, hy_l_rev, lens_post])
        # Explicit close onto first point (right lens equator)
        if np.linalg.norm(chamber[-1] - chamber[0]) > 1e-12:
            chamber = np.vstack([chamber, chamber[0]])
        bi["band_vitreous"] = chamber

    # One continuous sclera shell: outer L↔R + TM wrap (minY→minX→maxY) each side
    if all(
        k in bi
        for k in (
            "sclera_post_right",
            "sclera_post_left",
            "choroid_sclera_right",
            "choroid_sclera_left",
            "sclera_tm_wrap_right",
            "sclera_tm_wrap_left",
        )
    ):
        sr, sl = bi["sclera_post_right"], bi["sclera_post_left"]
        cr, cl = bi["choroid_sclera_right"], bi["choroid_sclera_left"]
        wr, wl = bi["sclera_tm_wrap_right"], bi["sclera_tm_wrap_left"]
        # outer lim_r → pole → lim_l; wrap_l (lim→minY→minX→maxY);
        # choroid lim_lside → pole → lim_rside; wrap_r reverse (maxY→minX→minY→lim)
        scl_full = np.vstack(
            [
                sr,
                sl[-2::-1],
                wl[1:],
                cl[0:1],
                cl[1:],
                cr[-2::-1],
                wr[-2::-1],
            ]
        )
        if np.linalg.norm(scl_full[-1] - scl_full[0]) > 1e-12:
            scl_full = np.vstack([scl_full, scl_full[0:1]])
        bi["band_sclera_full"] = scl_full

    # Continuous choroid / retina bands — single polygon, shared pole on x=0
    # (half-band L/R fills leave white wedges on the optical axis).
    def _full_shell_band(outer_r, outer_l, inner_r, inner_l):
        or_, ol = outer_r.copy(), outer_l.copy()
        ir_, il = inner_r.copy(), inner_l.copy()
        for a in (or_, ol, ir_, il):
            a[-1, 0] = 0.0
        full = np.vstack(
            [
                or_,
                ol[-2::-1],
                il[0:1],
                il[1:],
                ir_[-2::-1],
                or_[0:1],
            ]
        )
        if np.linalg.norm(full[-1] - full[0]) > 1e-15:
            full = np.vstack([full, full[0:1]])
        return full

    if all(
        k in bi
        for k in (
            "choroid_ret_right",
            "choroid_ret_left",
            "retina_choroid_right",
            "retina_choroid_left",
            "vitreous_retina_right",
            "vitreous_retina_left",
        )
    ):
        bi["band_choroid_full"] = _full_shell_band(
            bi["choroid_ret_right"],
            bi["choroid_ret_left"],
            bi["retina_choroid_right"],
            bi["retina_choroid_left"],
        )
        bi["band_retina_full"] = _full_shell_band(
            bi["retina_choroid_right"],
            bi["retina_choroid_left"],
            bi["vitreous_retina_right"],
            bi["vitreous_retina_left"],
        )

    # Closed aqueous chamber: cornea → TM → CB → contour iris (through tip/gap)
    # → CB again → vitreous (hyaloid) → lens (front to apex), bilateral.
    need = (
        "cornea_inside_right",
        "cornea_inside_left",
        "tm_markers_right",
        "tm_markers_left",
        "iris_right",
        "iris_left",
        "hyaloid_right",
        "hyaloid_left",
        "lens_right",
        "lens_left",
    )
    if all(k in bi for k in need):
        cor_r = bi["cornea_inside_right"]  # apex → lim_in
        tm_r = bi["tm_markers_right"]  # lim → … → maxY → lim
        iris_r = bi["iris_right"]  # cil_ant … tip_ant, tip_post … cil_post …
        hy_r = bi["hyaloid_right"]  # eq → purple → … → hy_ret
        lens_r = bi["lens_right"]  # front apex → eq → rear apex
        ie_r = int(np.argmax(np.abs(lens_r[:, 0])))
        lens_front_r = lens_r[: ie_r + 1]  # apex → eq
        lens_eq_to_apex_r = lens_front_r[::-1]  # eq → apex

        tm_run_r = tm_r[:-1]  # lim → … → maxY  (TM high-Y / CB attach)
        # Contour iris along free margin: ant root → tip_ant → tip_post → post root
        iris_run_r = iris_r[:6]
        purple_r = hy_r[1]
        eq_r = hy_r[0]
        cil_ant_r = iris_run_r[0]

        right = np.vstack(
            [
                cor_r,                         # 1 cornea
                tm_run_r[1:],                  # 2 TM → ends at max-Y
                cil_ant_r.reshape(1, 2),       # 3 CB lateral (TM max-Y → iris root)
                iris_run_r[1:],                # 4 iris Table SII polyline
                purple_r.reshape(1, 2),        # 5 post root → purple
                eq_r.reshape(1, 2),            # 6 hyaloid → lens eq
                lens_eq_to_apex_r[1:],         # 7 lens → anterior apex
            ]
        )
        left = mirror_x(right)
        ac = np.vstack([right, left[-2::-1], right[0:1]])
        bi["band_ac"] = ac
    return bi


# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------
def plot_geometry(
    bi: dict[str, np.ndarray],
    outlines_cm: dict,
    path: Path,
    *,
    fluid_only: bool = False,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10.5, 9.0), dpi=160)
    LW = 0.7  # uniform thin stroke for all anatomy outlines

    def draw(key, **kw):
        if key not in bi:
            return
        p = bi[key] * 1e3  # mm for readability
        kw.setdefault("lw", LW)
        ax.plot(p[:, 0], p[:, 1], **kw)

    # Outer wall outline (context) — same as original figure
    if "outer_wall_full" in bi:
        ow = bi["outer_wall_full"] * 1e3
        if not fluid_only:
            ax.fill(ow[:, 0], ow[:, 1], color="#eef4f8", zorder=0)
        ax.plot(ow[:, 0], ow[:, 1], color="#1d3557", lw=LW, label="Outer wall", zorder=3)

    def fill_band(key: str, color: str, label: str):
        for side in (f"{key}_right", f"{key}_left"):
            if side not in bi:
                continue
            p = bi[side] * 1e3
            ax.fill(
                p[:, 0],
                p[:, 1],
                color=color,
                alpha=0.75,
                zorder=1,
                label=label if side.endswith("_right") else None,
                edgecolor="none",
            )

    if not fluid_only:
        # Tissue bands
        if "band_sclera_full" in bi:
            sf = bi["band_sclera_full"] * 1e3
            ax.fill(
                sf[:, 0],
                sf[:, 1],
                color="#4a6fa5",
                alpha=0.75,
                zorder=1,
                label="Sclera",
                edgecolor="none",
            )
            ax.plot(sf[:, 0], sf[:, 1], color="#4a6fa5", lw=LW, zorder=1)
        else:
            fill_band("band_sclera", "#4a6fa5", "Sclera")
        if "band_choroid_full" in bi:
            cf = bi["band_choroid_full"] * 1e3
            ax.fill(
                cf[:, 0],
                cf[:, 1],
                color="#c1666b",
                alpha=0.75,
                zorder=1,
                label="Choroid",
                edgecolor="none",
            )
        else:
            fill_band("band_choroid", "#c1666b", "Choroid")
        if "band_retina_full" in bi:
            rf = bi["band_retina_full"] * 1e3
            ax.fill(
                rf[:, 0],
                rf[:, 1],
                color="#e4c15f",
                alpha=0.75,
                zorder=1,
                label="Retina",
                edgecolor="none",
            )
        else:
            fill_band("band_retina", "#e4c15f", "Retina")

    # --- Fluid regions: vitreous, AC, TM (always when fluid_only; also in full plot) ---
    if "band_vitreous" in bi:
        vv = bi["band_vitreous"] * 1e3
        ax.fill(
            vv[:, 0],
            vv[:, 1],
            color="#5dade2",
            alpha=0.55 if fluid_only else 0.45,
            zorder=1.5,
            label="Vitreous",
            edgecolor="none",
        )

    if "band_ac" in bi:
        ac = bi["band_ac"] * 1e3
        ax.fill(
            ac[:, 0],
            ac[:, 1],
            color="#a8dadc",
            alpha=0.65 if fluid_only else 0.55,
            zorder=1.3,
            label="AC",
            edgecolor="none",
        )

    if not fluid_only:
        draw("choroid_sclera_full", color="#8b3a3e")
        draw("retina_choroid_full", color="#b89b3e")
        draw("vitreous_retina_full", color="#9bc0d4", label="Vitreous–retina")
        draw("shell_endcap_right", color="#333333", label="Endcap (choroid+retina)")
        draw("shell_endcap_left", color="#333333")
        draw("sclera_tm_wrap_right", color="#1d3557", label="Sclera→TM wrap")
        draw("sclera_tm_wrap_left", color="#1d3557")
        draw("hyaloid_stub_right", color="#9bc0d4")
        draw("hyaloid_stub_left", color="#9bc0d4")

        if "band_cornea_right" in bi:
            for side, lab in (("band_cornea_right", "Cornea"), ("band_cornea_left", None)):
                c = bi[side] * 1e3
                ax.fill(
                    c[:, 0],
                    c[:, 1],
                    color="#f7b267",
                    alpha=0.8,
                    zorder=1.2,
                    edgecolor="none",
                    label=lab,
                )
        draw("cornea_inside_right", color="#e08a55", label="Cornea inside")
        draw("cornea_inside_left", color="#e08a55")
        draw("limbus_close_right", color="#e08a55")
        draw("limbus_close_left", color="#e08a55")
        draw("band_cornea_right", color="#c45c26")
        draw("band_cornea_left", color="#c45c26")

    # Walls as outlines (always — solid obstacles in fluid problem)
    if "lens_full" in bi:
        ln = bi["lens_full"] * 1e3
        if not fluid_only:
            ax.fill(ln[:, 0], ln[:, 1], color="#95d5b2", alpha=0.85, zorder=2)
        ax.plot(ln[:, 0], ln[:, 1], color="#2d6a4f", lw=LW, label="Lens", zorder=3)
    draw("hyaloid_right", color="#6a4c93", label="Hyaloid")
    draw("hyaloid_left", color="#6a4c93")

    if not fluid_only:
        if "band_ciliary_right" in bi:
            for side, lab in (("band_ciliary_right", "Ciliary body"), ("band_ciliary_left", None)):
                cb = bi[side] * 1e3
                ax.fill(
                    cb[:, 0],
                    cb[:, 1],
                    color="#7b2d8e",
                    alpha=0.55,
                    zorder=2.2,
                    edgecolor="none",
                    label=lab,
                )
        draw("band_ciliary_right", color="#5a1a6a")
        draw("band_ciliary_left", color="#5a1a6a")

    if "iris_right" in bi:
        for side, lab in (("iris_right", "Iris"), ("iris_left", None)):
            ir = bi[side] * 1e3
            if not fluid_only:
                ax.fill(
                    ir[:, 0],
                    ir[:, 1],
                    color="#e76f51",
                    alpha=0.85,
                    zorder=2.5,
                    edgecolor="none",
                    label=lab,
                )
            ax.plot(
                ir[:, 0],
                ir[:, 1],
                color="#9b2226",
                lw=LW,
                zorder=3,
                label=lab if fluid_only and lab else None,
            )

    # TM fluid / porous zone
    draw("tm_markers_right", color="#f4a261", label="TM" if fluid_only else "TM region")
    draw("tm_markers_left", color="#f4a261")
    if "tm_markers_right" in bi:
        for side, lab in (("tm_markers_right", "TM"), ("tm_markers_left", None)):
            t = bi[side] * 1e3
            ax.fill(
                t[:, 0],
                t[:, 1],
                color="#f4a261",
                alpha=0.75 if fluid_only else 0.35,
                zorder=2,
                label=lab if fluid_only and lab else None,
                edgecolor="none",
            )

    if not fluid_only:
        draw(
            "tm_iris_hyaloid_right",
            color="#6a4c93",
            ls="-",
            label="TM→hyaloid angle",
        )
        draw("tm_iris_hyaloid_left", color="#6a4c93")

    # --- Inlet / outlet markers ---
    # outlet = FULL SE face of TM (tm_cornea_void → tm_ciliary_void) — larger SE wall
    out_a_r = np.array(PTS["tm_cornea_void"]) * 1e1
    out_b_r = np.array(PTS["tm_ciliary_void"]) * 1e1
    out_a_l = np.array([-out_a_r[0], out_a_r[1]])
    out_b_l = np.array([-out_b_r[0], out_b_r[1]])
    out_mid_r = 0.5 * (out_a_r + out_b_r)
    out_mid_l = 0.5 * (out_a_l + out_b_l)

    # inlet = AC–CB from iris edge → vitreous edge (post → hyaloid)
    post = np.array(PTS["iris_ciliary_post"]) * 1e1
    purple = np.array(PTS["hyaloid_curved_flat"]) * 1e1
    inl_a_r = post
    inl_b_r = purple
    inl_a_l = np.array([-inl_a_r[0], inl_a_r[1]])
    inl_b_l = np.array([-inl_b_r[0], inl_b_r[1]])
    inl_mid_r = 0.5 * (inl_a_r + inl_b_r)
    inl_mid_l = 0.5 * (inl_a_l + inl_b_l)

    ax.plot(
        [out_a_r[0], out_b_r[0]],
        [out_a_r[1], out_b_r[1]],
        color="#d00000",
        lw=2.0,
        zorder=6,
        solid_capstyle="round",
        label="outlet_tm (TM SE face)",
    )
    ax.plot(
        [out_a_l[0], out_b_l[0]],
        [out_a_l[1], out_b_l[1]],
        color="#d00000",
        lw=2.0,
        zorder=6,
        solid_capstyle="round",
    )
    ax.plot([out_mid_r[0]], [out_mid_r[1]], "s", color="#d00000", ms=3.5, zorder=7)
    ax.plot([out_mid_l[0]], [out_mid_l[1]], "s", color="#d00000", ms=3.5, zorder=7)
    ax.annotate(
        "outlet_tm",
        xy=out_mid_r,
        xytext=(out_mid_r[0] + 1.2, out_mid_r[1] - 1.4),
        fontsize=7,
        color="#d00000",
        ha="left",
        arrowprops=dict(arrowstyle="->", color="#d00000", lw=0.8),
        zorder=8,
    )
    ax.annotate(
        "outlet_tm_left",
        xy=out_mid_l,
        xytext=(out_mid_l[0] - 2.8, out_mid_l[1] - 1.4),
        fontsize=7,
        color="#d00000",
        ha="left",
        arrowprops=dict(arrowstyle="->", color="#d00000", lw=0.8),
        zorder=8,
    )

    ax.plot(
        [inl_a_r[0], inl_b_r[0]],
        [inl_a_r[1], inl_b_r[1]],
        color="#0077b6",
        lw=2.0,
        zorder=6,
        solid_capstyle="round",
        label="ac_inlet (iris→vitreous)",
    )
    ax.plot(
        [inl_a_l[0], inl_b_l[0]],
        [inl_a_l[1], inl_b_l[1]],
        color="#0077b6",
        lw=2.0,
        zorder=6,
        solid_capstyle="round",
    )
    ax.plot([inl_mid_r[0]], [inl_mid_r[1]], "^", color="#0077b6", ms=4.5, zorder=7)
    ax.plot([inl_mid_l[0]], [inl_mid_l[1]], "^", color="#0077b6", ms=4.5, zorder=7)
    ax.annotate(
        "ac_inlet",
        xy=inl_mid_r,
        xytext=(inl_mid_r[0] - 2.5, inl_mid_r[1] + 1.2),
        fontsize=7,
        color="#0077b6",
        arrowprops=dict(arrowstyle="->", color="#0077b6", lw=0.8),
        zorder=8,
    )
    ax.annotate(
        "ac_inlet_left",
        xy=inl_mid_l,
        xytext=(inl_mid_l[0] + 0.5, inl_mid_l[1] + 1.2),
        fontsize=7,
        color="#0077b6",
        arrowprops=dict(arrowstyle="->", color="#0077b6", lw=0.8),
        zorder=8,
    )

    # Optical axis
    ax.axvline(0.0, color="0.5", ls="--", lw=LW, label="Optical axis")

    # Labels (mm)
    if fluid_only:
        ax.text(0.2, -4.5, "AC", color="#1b6a7a", fontsize=10, ha="center", fontweight="bold")
        ax.text(0.2, 3.5, "Vitreous", color="#2874a6", fontsize=10, ha="center", fontweight="bold")
        ax.text(7.2, -4.5, "TM", color="#b5651d", fontsize=9, fontweight="bold")
        ax.text(-7.2, -4.5, "TM", color="#b5651d", fontsize=9, fontweight="bold", ha="right")
    else:
        ax.text(0.2, -7.8, "Cornea", color="#c45c26", fontsize=9, ha="center")
        ax.text(0.2, -4.5, "AC", color="0.25", fontsize=9, ha="center")
        ax.text(0.2, -2.0, "Lens", color="#2d6a4f", fontsize=9, ha="center")
        ax.text(0.2, 3.5, "Vitreous", color="#2874a6", fontsize=9, ha="center")
        ax.text(5.5, -4.8, "Iris", color="#9b2226", fontsize=8)
        ax.text(6.5, -4.3, "TM", color="#b5651d", fontsize=8)
        ax.text(7.5, 0.0, "Sclera / Choroid / Retina", color="#2c5f8a", fontsize=7, ha="left")

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x [mm]  (mirrored bilaterally)")
    ax.set_ylabel("y [mm]  (optical axis, + posterior)")
    if fluid_only:
        ax.set_title(
            "G1 fluid — AC / vitreous / TM only\n"
            "Missel 2012 / Lamminsalo 2018  (walls: lens, iris, outer outline)"
        )
    else:
        ax.set_title(
            "G1 anatomical rabbit eye — 2D planar bilateral\n"
            "Missel 2012 / Lamminsalo 2018 Tables SI–SII  (no canal of Petit)"
        )
    ax.legend(loc="upper right", fontsize=7, framealpha=0.92)
    ax.grid(True, alpha=0.25)
    ax.set_xlim(-10.5, 10.5)
    ax.set_ylim(-9.5, 9.0)

    note = (
        "empty front/back (1 mm slab) · gap iris–lens ≥ 30 µm · "
        "Q=3 µL/min, P_TM=P_sclera=10 Torr, P_cornea=0 Torr"
    )
    ax.text(
        0.5,
        -0.06,
        note,
        transform=ax.transAxes,
        ha="center",
        fontsize=7.5,
    )

    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {path}")


# ---------------------------------------------------------------------------
# Gmsh (optional)
# ---------------------------------------------------------------------------
def write_geo_stub(bi: dict[str, np.ndarray], path: Path) -> None:
    """Write a Gmsh .geo with bilateral outline splines (meshing entry point)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "// G1 Missel/Lamminsalo anatomical eye — 2D planar bilateral",
        "// Generated by brunaStuff/gen_lamminsalo_2d.py",
        "SetFactory(\"OpenCASCADE\");",
        f"Lz = {Z_SLAB_M};",
        "lc = 2.0e-4;  // characteristic length ~0.2 mm",
        "lc_fine = 3.0e-5; // near iris-lens gap / TM",
        "",
    ]
    pid = 1

    def dump_spline(name: str, pts: np.ndarray, closed: bool = False):
        nonlocal pid
        ids = []
        for x, y in pts:
            lines.append(f"Point({pid}) = {{{x:.8e}, {y:.8e}, 0, lc}};")
            ids.append(pid)
            pid += 1
        if closed and len(ids) > 2:
            ids_loop = ids + [ids[0]]
        else:
            ids_loop = ids
        lines.append(f"Spline({pid}) = {{{', '.join(map(str, ids_loop))}}};")
        lines.append(f"// {name} curve {pid}")
        cid = pid
        pid += 1
        return cid

    for key in (
        "cornea_outside_full",
        "cornea_inside_full",
        "outer_sclera_full",
        "vitreous_retina_full",
        "lens_full",
        "iris_right",
        "iris_left",
        "hyaloid_right",
        "hyaloid_left",
        "tm_markers_right",
        "tm_markers_left",
    ):
        if key in bi and len(bi[key]) >= 2:
            dump_spline(key, bi[key], closed=key.endswith("_full"))

    lines += [
        "",
        "// NOTE: Boolean fluid regions (AC/PC/vitreous/TM shells) are built in",
        "// gen_lamminsalo_2d.py --mesh via the gmsh Python API.",
        "",
    ]
    path.write_text("\n".join(lines) + "\n")
    print(f"Wrote {path}")


def _iris_loop_m(iris_open: np.ndarray) -> np.ndarray:
    """Close iris polyline into a thin solid polygon."""
    pts = np.asarray(iris_open, dtype=float)
    if np.linalg.norm(pts[0] - pts[-1]) > 1e-12:
        pts = np.vstack([pts, pts[0]])
    return pts


def mesh_with_gmsh(bi: dict[str, np.ndarray], msh_path: Path) -> None:
    """
    Anatomical G1 fluid slab for OpenFOAM (gmshToFoam):
      (AC ∪ vitreous ∪ TM) − lens − iris(±), extruded 1 mm in z.
      Tissue shells (sclera/choroid/retina/cornea stroma) are NOT included.
    Physical patch names match Step-0 BCs:
      front, back (empty); ac_inlet, ac_inlet_left; outlet_tm, outlet_tm_left;
      lens_wall, iris_wall, wall.
    Writes MeshFormat 2.2 for gmshToFoam.
    """
    import gmsh

    gmsh.initialize()
    gmsh.model.add("eye_g1_lamminsalo")
    gmsh.option.setNumber("General.Terminal", 1)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", 1.0e-4)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", 1.2e-3)
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)

    occ = gmsh.model.occ

    def add_polygon(pts_m: np.ndarray, lc: float = 2.0e-4):
        pts = [np.asarray(p, dtype=float) for p in pts_m]
        if np.linalg.norm(pts[0] - pts[-1]) < 1e-14:
            pts = pts[:-1]
        # downsample very dense curves to keep OCC stable
        if len(pts) > 180:
            idx = np.linspace(0, len(pts) - 1, 180).astype(int)
            pts = [pts[i] for i in idx]
        ptags = [occ.addPoint(float(x), float(y), 0.0, lc) for x, y in pts]
        ltags = [
            occ.addLine(ptags[i], ptags[(i + 1) % len(ptags)]) for i in range(len(ptags))
        ]
        return occ.addPlaneSurface([occ.addCurveLoop(ltags)])

    # Direct AC ∪ vitreous (TM already inside band_ac). Punch exact Lamminsalo
    # polygonal iris holes (+ lens is already a hole in AC∪vit geometry).
    def add_ring(pts_m, lc=2.0e-4, n_per_seg: int | None = 6):
        pts = np.asarray(pts_m, dtype=float)
        if n_per_seg:
            pts = densify_polyline(pts, n_per_seg=n_per_seg)
        pts = _clean_ring(pts, tol=1e-9)[:-1]
        ptags = []
        for x, y in pts:
            ptags.append(occ.addPoint(float(x), float(y), 0.0, lc))
        ltags = []
        for i in range(len(ptags)):
            a, b = ptags[i], ptags[(i + 1) % len(ptags)]
            if a != b:
                ltags.append(occ.addLine(a, b))
        return occ.addPlaneSurface([occ.addCurveLoop(ltags)])

    s_ac = add_ring(bi["band_ac"], lc=2.0e-4, n_per_seg=4)
    s_vit = add_ring(bi["band_vitreous"], lc=2.5e-4, n_per_seg=4)
    fused = occ.fuse([(2, s_ac)], [(2, s_vit)], removeObject=True, removeTool=True)
    occ.synchronize()
    if not fused[0]:
        raise RuntimeError("OCC fuse AC∪vitreous produced nothing")
    # Cut exact Table SII iris polygons (polyline holes — preserve turns)
    iris_r = densify_polyline(_iris_loop_m(bi["iris_right"]), n_per_seg=10)
    iris_l = densify_polyline(_iris_loop_m(bi["iris_left"]), n_per_seg=10)
    try:
        cut = occ.cut(
            [e for e in fused[0] if e[0] == 2],
            [(2, add_ring(iris_r, lc=4.0e-5, n_per_seg=None)),
             (2, add_ring(iris_l, lc=4.0e-5, n_per_seg=None))],
            removeObject=True,
            removeTool=True,
        )
        occ.synchronize()
        fluid_surfaces = [e for e in cut[0] if e[0] == 2] if cut[0] else []
        if not fluid_surfaces:
            raise RuntimeError("iris cut emptied fluid")
        print("INFO: cut Lamminsalo polygonal iris holes L/R")
    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: iris hole cut failed ({exc}); keeping AC∪vit fuse only")
        fluid_surfaces = [e for e in fused[0] if e[0] == 2]
    print(f"INFO: fluid faces after AC∪vitreous (±iris): {len(fluid_surfaces)}")
    # Remember pre-extrusion surfaces (= back caps at z=0)
    back_caps = [s[1] for s in fluid_surfaces]
    # 1-layer prism slab (recombine) — valid empty front/back for 2D simpleFoam
    out = occ.extrude(
        fluid_surfaces, 0, 0, Z_SLAB_M,
        numElements=[1], heights=[1], recombine=True,
    )
    occ.synchronize()

    volume_tags = [e[1] for e in out if e[0] == 3]
    # Extrude returns: [volume, topSurfaces..., lateralSurfaces...]
    # Top surfaces are the first dim=2 entities after each volume in typical OCC order;
    # collect all new dim=2 not in back_caps that lie near z=Lz.
    all_surf = [e[1] for e in out if e[0] == 2]
    front_caps = []
    for stag in all_surf:
        xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(2, stag)
        cz = 0.5 * (zmin + zmax)
        dz = zmax - zmin
        if abs(cz - Z_SLAB_M) < 0.2 * Z_SLAB_M and dz < 0.2 * Z_SLAB_M:
            front_caps.append(stag)

    if not volume_tags:
        raise RuntimeError("No extruded volume")

    # Do NOT assign physical groups to extrusion caps — gmshToFoam puts them in
    # defaultFaces; OpenFOAM createPatch then splits them into empty front/back.
    groups: dict[str, list[int]] = {
        "front": [],
        "back": [],
        "ac_inlet": [],
        "ac_inlet_left": [],
        "outlet_tm": [],
        "outlet_tm_left": [],
        "lens_wall": [],
        "iris_wall": [],
        "wall": [],
    }
    # Cap CAD tags (excluded from lateral classification)
    reserved = set(front_caps) | set(back_caps)

    # Landmark points (m)
    # outlet_tm = FULL SE face of TM (tm_cornea_void → tm_ciliary_void) — larger SE wall
    # ac_inlet  = AC–CB from iris edge → vitreous edge (iris_ciliary_post → hyaloid_curved_flat)
    tm_se_a = np.array(PTS["tm_cornea_void"]) * M_PER_CM
    tm_se_b = np.array(PTS["tm_ciliary_void"]) * M_PER_CM
    tm_se = tm_se_b - tm_se_a
    tm_se_L = float(np.linalg.norm(tm_se))
    tm_se_u = tm_se / max(tm_se_L, 1e-16)
    tm_r = 0.5 * (tm_se_a + tm_se_b)
    tm_l = np.array([-tm_r[0], tm_r[1]])

    iris_post = np.array(PTS["iris_ciliary_post"]) * M_PER_CM
    purple = np.array(PTS["hyaloid_curved_flat"]) * M_PER_CM
    inl_seg = purple - iris_post
    inl_r = iris_post + 0.50 * inl_seg
    inl_l = np.array([-inl_r[0], inl_r[1]])
    lens_c = np.array(
        [0.0, 0.5 * (SURFACES["lens_front"]["zc"] + SURFACES["lens_rear"]["zc"])]
    ) * M_PER_CM

    def on_tm_se_face(cx: float, cy: float, side: float) -> bool:
        """Full SE voids face of TM (larger southeast wall)."""
        if cx * side <= 0:
            return False
        p = np.array([abs(cx), cy])
        t = float(np.dot(p - tm_se_a, tm_se_u))
        if t < -5e-5 or t > tm_se_L + 5e-5:
            return False
        closest = tm_se_a + np.clip(t, 0.0, tm_se_L) * tm_se_u
        # ~0.06 mm: full SE edge faces only (neighbours sit ~0.085 mm off-segment)
        return float(np.linalg.norm(p - closest)) < 6.0e-5

    def on_ac_cb_iris_to_vitreous(cx: float, cy: float, side: float) -> bool:
        """AC–CB wall from iris edge to vitreous edge (post → hyaloid), full segment."""
        if cx * side <= 0:
            return False
        p = np.array([abs(cx), cy])
        L = float(np.linalg.norm(inl_seg))
        u = inl_seg / max(L, 1e-16)
        t = float(np.dot(p - iris_post, u))
        if t < -1e-5 or t > L + 1e-5:
            return False
        closest = iris_post + np.clip(t, 0.0, L) * u
        return float(np.linalg.norm(p - closest)) < 2.0e-4

    boundaries = gmsh.model.getBoundary([(3, v) for v in volume_tags], oriented=False)
    for dim, tag in boundaries:
        xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(dim, tag)
        cx, cy = 0.5 * (xmin + xmax), 0.5 * (ymin + ymax)
        dz = zmax - zmin
        dx = xmax - xmin
        dy = ymax - ymin
        span_xy = max(dx, dy, 1e-16)

        if tag in reserved:
            continue
        if dz <= 0.05 * span_xy and dx * dy > 1e-10:
            continue

        p = np.array([cx, cy])
        d_lens = np.linalg.norm(p - lens_c)

        if on_tm_se_face(cx, cy, +1.0):
            groups["outlet_tm"].append(tag)
        elif on_tm_se_face(cx, cy, -1.0):
            groups["outlet_tm_left"].append(tag)
        elif on_ac_cb_iris_to_vitreous(cx, cy, +1.0):
            groups["ac_inlet"].append(tag)
        elif on_ac_cb_iris_to_vitreous(cx, cy, -1.0):
            groups["ac_inlet_left"].append(tag)
        elif d_lens < 4.5e-3 and -0.0065 < cy < 0.0015:
            groups["lens_wall"].append(tag)
        elif 2.5e-3 < abs(cx) < 7.2e-3 and -0.0056 < cy < -0.0036:
            groups["iris_wall"].append(tag)
        else:
            groups["wall"].append(tag)

    print(f"INFO: caps reserved for defaultFaces frontCAD={front_caps} backCAD={back_caps}")

    # Fallback: ensure mandatory patches exist (pick nearest lateral faces)
    laterals = [
        tag
        for dim, tag in boundaries
        if (gmsh.model.getBoundingBox(dim, tag)[5] - gmsh.model.getBoundingBox(dim, tag)[2]) > 1e-7
    ]

    def ensure(name: str, pred):
        if groups[name]:
            return
        best, best_d = None, 1e99
        for tag in laterals:
            xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(2, tag)
            cx, cy = 0.5 * (xmin + xmax), 0.5 * (ymin + ymax)
            d = pred(cx, cy)
            if d < best_d:
                best_d, best = d, tag
        if best is not None:
            # remove from wall if present
            groups["wall"] = [t for t in groups["wall"] if t != best]
            groups[name].append(best)
            print(f"INFO: fallback patch {name} <- surface {best}")

    ensure("outlet_tm", lambda cx, cy: np.hypot(cx - tm_r[0], cy - tm_r[1]) if cx > 0 else 1e9)
    ensure("outlet_tm_left", lambda cx, cy: np.hypot(cx - tm_l[0], cy - tm_l[1]) if cx < 0 else 1e9)
    ensure("ac_inlet", lambda cx, cy: np.hypot(cx - inl_r[0], cy - inl_r[1]) if cx > 0 else 1e9)
    ensure("ac_inlet_left", lambda cx, cy: np.hypot(cx - inl_l[0], cy - inl_l[1]) if cx < 0 else 1e9)

    gmsh.model.addPhysicalGroup(3, volume_tags, tag=1, name="fluid")
    pid = 2
    for name, tags in groups.items():
        if name in ("front", "back"):
            continue  # created later via createPatch from defaultFaces
        if not tags:
            print(f"WARNING: empty patch group '{name}'")
            continue
        gmsh.model.addPhysicalGroup(2, tags, tag=pid, name=name)
        pid += 1

    # Mild size clamp
    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", 1.0e-4)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", 7.5e-4)

    gmsh.model.mesh.generate(3)
    msh_path.parent.mkdir(parents=True, exist_ok=True)
    gmsh.write(str(msh_path))
    gmsh.write(str(msh_path.with_suffix(".vtk")))
    # patch report
    report = {k: len(v) for k, v in groups.items()}
    (msh_path.parent / "patch_groups.json").write_text(json.dumps(report, indent=2))
    print(f"Wrote {msh_path}")
    print(f"Patch groups: {report}")
    gmsh.finalize()


def write_toposet_anatomical(path: Path) -> None:
    """topoSetDict for vitreous / TM cellZones on the anatomical mesh (metres)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    # Symmetric TM box about optical axis (equal pad both sides)
    tm = PTS["tm_cornea_void"]
    t2 = PTS["tm_ciliary_void"]
    pad = 2.5e-4
    x0 = min(tm[0], t2[0]) * M_PER_CM - pad
    x1 = max(tm[0], t2[0]) * M_PER_CM + pad
    y0 = min(tm[1], t2[1]) * M_PER_CM - pad
    y1 = max(tm[1], t2[1]) * M_PER_CM + pad
    # Vitreous bulk: posterior of lens equator inside ~vitreous–retina ellipse
    text = f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      topoSetDict;
}}

// Anatomical G1 cellZones (Missel/Lamminsalo planar bilateral)
// TM boxes are exact L/R mirrors (pad={pad:.1e} m).

actions
(
    // --- TM right ---
    {{
        name    tm_zone;
        type    cellSet;
        action  new;
        source  boxToCell;
        box     ({x0:.6e} {y0:.6e} -1e-5) ({x1:.6e} {y1:.6e} 1.001e-3);
    }}
    {{
        name    tm_zone;
        type    cellZoneSet;
        action  new;
        source  setToCellZone;
        set     tm_zone;
    }}

    // --- TM left (exact mirror) ---
    {{
        name    tm_zone_left;
        type    cellSet;
        action  new;
        source  boxToCell;
        box     ({-x1:.6e} {y0:.6e} -1e-5) ({-x0:.6e} {y1:.6e} 1.001e-3);
    }}
    {{
        name    tm_zone_left;
        type    cellZoneSet;
        action  new;
        source  setToCellZone;
        set     tm_zone_left;
    }}

    // --- Vitreous (posterior bulk) ---
    {{
        name    vitreous_zone;
        type    cellSet;
        action  new;
        source  boxToCell;
        box     (-8.0e-3 -1.5e-3 -1e-5) (8.0e-3 7.4e-3 1.001e-3);
    }}
    // Remove TM cells from vitreous (not needed physically but keeps zones disjoint)
    {{
        name    vitreous_zone;
        type    cellSet;
        action  delete;
        source  boxToCell;
        box     ({x0:.6e} {y0:.6e} -1e-5) ({x1:.6e} {y1:.6e} 1.001e-3);
    }}
    {{
        name    vitreous_zone;
        type    cellSet;
        action  delete;
        source  boxToCell;
        box     ({-x1:.6e} {y0:.6e} -1e-5) ({-x0:.6e} {y1:.6e} 1.001e-3);
    }}
    {{
        name    vitreous_zone;
        type    cellZoneSet;
        action  new;
        source  setToCellZone;
        set     vitreous_zone;
    }}
);
"""
    path.write_text(text)
    print(f"Wrote {path}")


# ---------------------------------------------------------------------------
# Tables dump
# ---------------------------------------------------------------------------
def write_tables_md(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows_si = [
        ("Outer sclera", "0.900", "0.753", "0", "0"),
        ("Choroid–sclera", "0.867", "0.720", "0", "0"),
        ("Retina–choroid", "0.847", "0.700", "0", "0"),
        ("Vitreous–retina", "0.837", "0.690", "0", "0"),
        ("Lens rear", "0.479", "—", "0", "−0.415"),
        ("Lens front", "0.576", "—", "0", "−0.031"),
        ("Cornea outside", "0.829", "—", "0", "−0.023"),
        ("Cornea inside", "0.801", "—", "0", "−0.015"),
    ]
    lines = [
        "# G1 geometry tables (Missel / Lamminsalo ESM)",
        "",
        "Source: Lamminsalo et al. Pharm Res 2018 electronic supplementary Tables SI–SII,",
        "from Missel 2012. Units in tables: **cm**. OpenFOAM uses **metres** via",
        "`x = X·10⁻²`, `y = Z·10⁻²`, slab `z ∈ [0, 10⁻³]` with `empty` front/back.",
        "",
        "## Nomenclature",
        "",
        "- **G1** = anatomical 2D planar bilateral (Missel/Lamminsalo).",
        "- **Sim 1 fluid domain** = **AC + vitreous + TM only** (no sclera/choroid/retina/cornea stroma).",
        "- **G2** = G1 right-half revolved 90° (`gen_lamminsalo_g2.py`, case `doc-g2-sim1`).",
        "- **G2-fluid** = G1-fluid right-half revolved 90° (same script, `--mesh`).",
        "",
        "## Table SI (selected)",
        "",
        "| Surface | R1 [cm] | R2 [cm] | X-cent | Z-cent |",
        "|---------|---------|---------|--------|--------|",
    ]
    for r in rows_si:
        lines.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} |")
    lines += [
        "",
        "## Key intersections (cm)",
        "",
        "| Point | X | Z |",
        "|-------|---|---|",
    ]
    for name, (x, z) in PTS.items():
        lines.append(f"| `{name}` | {x} | {z} |")
    lines += [
        "",
        "## Model choices (G1)",
        "",
        "- No canal of Petit (base model).",
        "- **Iris = Table SII polyline** (cil → turn/dobra → tip), not a spline/curve.",
        "- Iris–lens gap ≥ 30 µm at Table SII tip corners (tips not shifted).",
        "- Bilateral mirror about the optical axis (`x = 0`).",
        "",
        "## Generated artefacts",
        "",
        "- `geometry/eye_g1_lamminsalo.geo` — Gmsh outline stub",
        "- `geometry/eye_g1_lamminsalo.msh` — volume mesh (if `--mesh`)",
        "- `figures/g1_anatomy_2d.png` — labelled geometry print",
        "",
    ]
    path.write_text("\n".join(lines))
    print(f"Wrote {path}")


def export_json(outlines_cm: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {k: v.tolist() for k, v in outlines_cm.items()}
    path.write_text(json.dumps({"units": "cm_Missel_XZ", "curves": data}, indent=2))
    print(f"Wrote {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


MESH_LEVELS = {
    # bulk / lens-iris / TM local sizes [m]
    "M1": {"lc": 1.0e-3, "lc_fine": 3.0e-4, "lc_tm": 1.2e-4},
    "M2": {"lc": 5.0e-4, "lc_fine": 1.2e-4, "lc_tm": 5.0e-5},
    "M3": {"lc": 3.5e-4, "lc_fine": 8.0e-5, "lc_tm": 3.5e-5},
}


def _clean_ring(pts, tol: float = 1e-10):
    """Drop consecutive near-duplicates; keep closed ring (first==last)."""
    import numpy as np

    pts = np.asarray(pts, dtype=float)
    if len(pts) < 3:
        return pts
    out = [pts[0]]
    for p in pts[1:]:
        if np.linalg.norm(p - out[-1]) > tol:
            out.append(p)
    if np.linalg.norm(out[0] - out[-1]) > tol:
        out.append(out[0].copy())
    else:
        out[-1] = out[0].copy()
    return np.asarray(out, dtype=float)


def fluid_outer_and_holes(
    bi: dict[str, np.ndarray],
) -> tuple[np.ndarray, list[np.ndarray]]:
    """
    Sim 1 fluid silhouette: AC ∪ vitreous ∪ TM only.

    Outer = cornea_inside + TM + hyaloid (purple→ora) + vitreous–retina.
    Holes = lens + iris(±) + ciliary(±) so tissue shells / CB are excluded.
    """
    if "band_ac" not in bi or "band_vitreous" not in bi:
        raise RuntimeError("band_ac / band_vitreous required for fluid-only mesh")

    cor_r = bi["cornea_inside_right"]
    tm_r = bi["tm_markers_right"][:-1]  # lim → … → maxY
    hy_r = bi["hyaloid_right"]  # eq, purple, …, ora
    vit_r = bi["vitreous_retina_right"].copy()
    vit_l = bi["vitreous_retina_left"].copy()
    vit_r[-1, 0] = 0.0
    vit_l[-1, 0] = 0.0

    hy_po = hy_r[1:]  # purple → ora
    vit_shell = np.vstack([vit_r, vit_l[-2::-1]])
    if np.linalg.norm(vit_shell[0] - hy_po[-1]) < 1e-9:
        vit_shell = vit_shell[1:]

    # CB lateral: TM max-Y (ciliary_tm_aqueous_sclera) → purple, then ora.
    # tm_run ends at max-Y; hy_po starts at purple.
    right = np.vstack([cor_r, tm_r[1:], hy_po, vit_shell])

    cor_l = bi["cornea_inside_left"]
    tm_l = bi["tm_markers_left"][:-1]  # lim → … → maxY
    hy_l = bi["hyaloid_left"]
    # Mirror return MUST include TM max-Y (high-Y corner) — do not skip it.
    left_back = np.vstack(
        [
            hy_l[1:][-2::-1],  # ora → … → purple
            tm_l[::-1],  # purple → TM max-Y → … → lim  (CB lateral + TM)
            cor_l[-2::-1],  # lim → apex
        ]
    )
    if np.linalg.norm(left_back[0] - right[-1]) < 1e-9:
        left_back = left_back[1:]
    outer = _clean_ring(np.vstack([right, left_back]))

    holes = [
        _clean_ring(bi["lens_full"]),
        _clean_ring(_iris_loop_m(bi["iris_right"])),
        _clean_ring(_iris_loop_m(bi["iris_left"])),
    ]
    if "band_ciliary_right" in bi and "band_ciliary_left" in bi:
        holes.append(_clean_ring(bi["band_ciliary_right"]))
        holes.append(_clean_ring(bi["band_ciliary_left"]))
    return outer, holes



def write_extrude_geo(
    bi: dict[str, np.ndarray],
    path: Path,
    *,
    mesh_level: str = "M1",
) -> None:
    """Built-in-kernel .geo with Extrude Layers{1} → prism mesh for empty front/back.

    Fluid domain = AC ∪ vitreous ∪ TM (cornea_inside / vitreous–retina outer).
    Solid holes = lens + iris. Tissue shells are NOT meshed.
    """
    if mesh_level not in MESH_LEVELS:
        raise ValueError(f"unknown mesh_level {mesh_level}; choose from {list(MESH_LEVELS)}")
    sizes = MESH_LEVELS[mesh_level]

    def densify(pts, nmax=160):
        pts = np.asarray(pts, dtype=float)
        if np.linalg.norm(pts[0] - pts[-1]) < 1e-14:
            pts = pts[:-1]
        if len(pts) > nmax:
            idx = np.linspace(0, len(pts) - 1, nmax).astype(int)
            pts = pts[idx]
        return pts

    # Diagnostic .geo: outer = cornea_inside+TM+ora+vit-retina; holes = lens+iris
    # (ciliary excluded from Extrude path — production mesh uses OCC fuse).
    outer0, holes0 = fluid_outer_and_holes(bi)
    holes0 = holes0[:3]  # lens + iris L/R only
    outer = densify(outer0, 200)
    holes = [densify(h, 100 if i == 0 else 40) for i, h in enumerate(holes0)]
    for i, h in enumerate(holes):
        if np.linalg.norm(h[0] - h[-1]) < 1e-14:
            holes[i] = h[:-1]

    lines = [
        f"// G1 fluid (AC / vitreous / TM only) — Extrude Layers{{1}} ({mesh_level})",
        "// Generated by brunaStuff/gen_lamminsalo_2d.py",
        "// Outer = cornea_inside + TM + hyaloid ora join + vitreous–retina",
        "// Holes = lens + iris (L/R). No sclera/choroid/retina/cornea stroma.",
        f"lc = {sizes['lc']:.3e};",
        f"lc_fine = {sizes['lc_fine']:.3e};",
        f"lc_tm = {sizes['lc_tm']:.3e};",
        f"Lz = {Z_SLAB_M};",
        "",
    ]
    pid = 1

    def add_pts(arr, fine=False):
        nonlocal pid
        ids = []
        lcv = "lc_fine" if fine else "lc"
        for x, y in arr:
            lines.append(f"Point({pid}) = {{{x:.8e}, {y:.8e}, 0, {lcv}}};")
            ids.append(pid)
            pid += 1
        return ids

    def add_loop(ids):
        nonlocal pid
        lids = []
        for i in range(len(ids)):
            lines.append(f"Line({pid}) = {{{ids[i]}, {ids[(i + 1) % len(ids)]}}};")
            lids.append(pid)
            pid += 1
        lines.append(f"Curve Loop({pid}) = {{{', '.join(map(str, lids))}}};")
        loop = pid
        pid += 1
        return loop

    lo = add_loop(add_pts(outer))
    hole_loops = [add_loop(add_pts(h, fine=True)) for h in holes]

    # Symmetric TM size attractors (Table SII voids ± mirrors)
    tm_pts = [
        PTS["tm_cornea_void"],
        PTS["tm_ciliary_void"],
        PTS["ciliary_tm_aqueous_sclera"],
    ]
    tm_ids = []
    for x_cm, y_cm in tm_pts:
        x, y = x_cm * M_PER_CM, y_cm * M_PER_CM
        lines.append(f"Point({pid}) = {{{x:.8e}, {y:.8e}, 0, lc_tm}};")
        tm_ids.append(pid)
        pid += 1
        lines.append(f"Point({pid}) = {{{-x:.8e}, {y:.8e}, 0, lc_tm}};")
        tm_ids.append(pid)
        pid += 1

    loops_csv = ", ".join(str(x) for x in [lo, *hole_loops])
    lines += [
        f"Plane Surface(1) = {{{loops_csv}}};",
        'Physical Surface("back") = {1};',
        "out[] = Extrude {0, 0, Lz} { Surface{1}; Layers{1}; Recombine; };",
        'Physical Surface("front") = {out[0]};',
        'Physical Volume("fluid") = {out[1]};',
        'Physical Surface("wall") = {out[2]:out[#out[]-1]};',
        "",
        "// Local TM refinement (symmetric L/R) — keep boundary point sizes active",
        "Field[1] = Distance;",
        f"Field[1].PointsList = {{{', '.join(map(str, tm_ids))}}};",
        "Field[2] = Threshold;",
        "Field[2].InField = 1;",
        "Field[2].SizeMin = lc_tm;",
        "Field[2].SizeMax = lc;",
        "Field[2].DistMin = 2.5e-4;",
        "Field[2].DistMax = 1.2e-3;",
        "Background Field = 2;",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")
    print(f"Wrote {path} ({mesh_level})")


def mesh_extrude_layers(geo_path: Path, msh_path: Path) -> None:
    """Run gmsh CLI on Extrude-Layers .geo (prism mesh, msh2)."""
    import shutil
    import subprocess

    gmsh_bin = shutil.which("gmsh")
    if not gmsh_bin:
        # fall back to python API runner
        import gmsh

        gmsh.initialize()
        gmsh.open(str(geo_path))
        gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
        gmsh.model.mesh.generate(3)
        gmsh.write(str(msh_path))
        gmsh.finalize()
    else:
        cmd = [gmsh_bin, str(geo_path), "-3", "-format", "msh2", "-o", str(msh_path)]
        print("Running:", " ".join(cmd))
        subprocess.check_call(cmd)
    print(f"Wrote {msh_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mesh", action="store_true", help="Build extruded 3D slab mesh with gmsh")
    ap.add_argument(
        "--mesh-level",
        default="M1",
        choices=sorted(MESH_LEVELS),
        help="Size field level for independence study (default M1)",
    )
    ap.add_argument(
        "--case",
        default=DEFAULT_CASE,
        help=f"Case directory under cases/ (default {DEFAULT_CASE})",
    )
    args = ap.parse_args()

    case, out_geom, out_fig = case_paths(args.case)
    outlines = build_outlines_cm()
    bi = build_bilateral_m(outlines)

    out_geom.mkdir(parents=True, exist_ok=True)
    out_fig.mkdir(parents=True, exist_ok=True)
    (case / "fluid" / "system").mkdir(parents=True, exist_ok=True)

    export_json(outlines, out_geom / "outlines_cm.json")
    write_tables_md(case / "geometry_tables.md")
    write_toposet_anatomical(case / "fluid" / "system" / "topoSetDict.anatomical")
    # Primary print for Sim 1 = fluid-only (AC / vitreous / TM)
    plot_geometry(bi, outlines, out_fig / "g1_fluid_2d.png", fluid_only=True)
    plot_geometry(bi, outlines, out_fig / "g1_anatomy_2d.png", fluid_only=False)

    geo = out_geom / f"eye_g1_lamminsalo_{args.mesh_level}.geo"
    msh = out_geom / f"eye_g1_lamminsalo_{args.mesh_level}.msh"
    write_extrude_geo(bi, geo, mesh_level=args.mesh_level)
    write_extrude_geo(bi, out_geom / "eye_g1_lamminsalo.geo", mesh_level=args.mesh_level)
    if args.mesh:
        import shutil

        # OCC AC∪vit fuse + 1-layer recombine extrude (prisms, empty front/back)
        mesh_with_gmsh(bi, msh)
        shutil.copy2(msh, out_geom / "eye_g1_lamminsalo.msh")

    print(f"Done. Case: {case}")


if __name__ == "__main__":
    main()
