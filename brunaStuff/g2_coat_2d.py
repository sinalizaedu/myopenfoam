"""2D meridional quad mesh — conformal solid tissues (+ 3D revolve via g2_solid_2d_revolve)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from gen_lamminsalo_2d import (
    M_PER_CM,
    PTS,
    SURFACES,
    densify_polyline,
    ellipse_phi_at,
    ellipse_point,
    sample_ellipse_arc,
)
from g2_structured_mesh import (
    MshData,
    _cum_arclength,
    _fluid_inner_on_ray,
    _interp_curve,
    _snap_axis,
    _subpath_between,
    build_fluid_outer_stations,
    point_in_poly,
    resample_open,
    resample_pair,
    write_msh,
)

SOLID_2D_ZONES = (
    "cornea",
    "coat",  # unified sclera + choroid + retina (same outer/fsi_active boundaries)
    "tm",
    "ciliary",
    "iris",
    "lens",
)
FLUID_2D_ZONES = ("ac", "vitreous")
ALL_2D_ZONES = SOLID_2D_ZONES + FLUID_2D_ZONES
AXIS_TOL = 5.0e-5

COAT_2D_LEVELS = {
    "M1": {
        "n_merid": 120,
        "n_merid_cap": 720,
        "layers": {
            "cornea": 6,
            "sclera": 12,
            "tm": 3,
            "ciliary": 6,
            "iris": 6,
            "lens": 6,
            "choroid": 8,
            "retina": 4,
            "ac": 10,
            "vitreous": 14,
        },
        "target_cell_m": 25e-6,
        "iris_n_cap": 400,
        "iris_layers_cap": 10,
        "lens_layers_cap": 24,
        "lens_max_aspect": 25.0,
        "lens_equator_min_thick_m": 200e-6,
        "lens_cluster": 2.8,
        "lens_x_floor_m": 1.0e-3,
        "lens_n_cap": 120,
        "fluid_axis_coarsen_m": 1.0e-3,
        "fluid_axis_lc_factor": 3.2,
        "fluid_tip_cells_across": 10,
        "include_lens": False,
    },
    "M2": {
        "n_merid": 180,
        "n_merid_cap": 1080,
        "layers": {
            "cornea": 8,
            "sclera": 16,
            "tm": 4,
            "ciliary": 8,
            "iris": 5,
            "lens": 8,
            "choroid": 10,
            "retina": 5,
            "ac": 12,
            "vitreous": 18,
        },
        "target_cell_m": 18e-6,
        "iris_n_cap": 600,
        "iris_layers_cap": 12,
        "lens_layers_cap": 32,
        "lens_max_aspect": 25.0,
        "lens_equator_min_thick_m": 180e-6,
        "lens_cluster": 2.8,
        "lens_x_floor_m": 0.95e-3,
        "lens_n_cap": 160,
        "fluid_axis_coarsen_m": 0.95e-3,
        "fluid_axis_lc_factor": 3.0,
        "fluid_tip_cells_across": 12,
        "include_lens": False,
    },
    "M3": {
        "n_merid": 240,
        "n_merid_cap": 1440,
        "layers": {
            "cornea": 10,
            "sclera": 20,
            "tm": 5,
            "ciliary": 10,
            "iris": 6,
            "lens": 10,
            "choroid": 14,
            "retina": 7,
            "ac": 16,
            "vitreous": 24,
        },
        "target_cell_m": 12e-6,
        "iris_n_cap": 800,
        "iris_layers_cap": 14,
        "lens_layers_cap": 40,
        "lens_max_aspect": 25.0,
        "lens_equator_min_thick_m": 150e-6,
        "lens_cluster": 2.6,
        "lens_x_floor_m": 0.9e-3,
        "lens_n_cap": 200,
        "fluid_axis_coarsen_m": 0.9e-3,
        "fluid_axis_lc_factor": 2.8,
        "fluid_tip_cells_across": 14,
        "include_lens": False,
    },
}


@dataclass
class Coat2DZone:
    name: str
    node_grid: list[list[int]]
    n_layers: int
    element: str = "quad"  # "quad" or "tri" (structured strip → 2 tris/cell)
    export_name: str | None = None
    equator_nid: int | None = None  # lens rim node when equator columns are trimmed from volume


@dataclass
class Coat2DMesh:
    nodes: dict[int, tuple[float, float, float]] = field(default_factory=dict)
    zones: dict[str, list[tuple[int, int, int, int]]] = field(default_factory=dict)
    tris: dict[str, list[tuple[int, int, int]]] = field(default_factory=dict)
    patches: dict[str, list[tuple[int, int]]] = field(default_factory=dict)


def meridional_stations(curves: list[np.ndarray], *, floor: int, cap: int, target_cell_m: float) -> int:
    lengths = [float(np.sum(np.linalg.norm(np.diff(_snap_axis(c), axis=0), axis=1))) for c in curves]
    arc = max(lengths)
    n_m = int(np.ceil(arc / target_cell_m))
    return int(min(cap, max(floor, n_m)))


def radial_layers(
    outer: np.ndarray,
    inner: np.ndarray,
    n_m: int,
    *,
    floor: int,
    cap: int,
    target_cell_m: float,
) -> int:
    outer_rs, inner_rs = resample_pair(outer, inner, n_m)
    thick_min = float(np.min(np.linalg.norm(outer_rs - inner_rs, axis=1)))
    n_r = int(np.ceil(thick_min / target_cell_m))
    return int(min(cap, max(floor, n_r)))


def _lens_radial_layers(
    outer: np.ndarray,
    inner: np.ndarray,
    *,
    floor: int,
    cap: int,
    target_cell_m: float,
    max_aspect: float = 25.0,
) -> int:
    """Radial layers thick enough that meridional steps near the apex stay bounded."""
    outer = np.asarray(outer, dtype=float)
    inner = np.asarray(inner, dtype=float)
    thick = np.linalg.norm(outer - inner, axis=1)
    thick_ref = float(np.max(thick))
    n_target = int(np.ceil(thick_ref / target_cell_m))
    if len(outer) > 1:
        dx = np.abs(np.diff(outer[:, 0]))
        arc = np.linalg.norm(np.diff(outer, axis=0), axis=1)
        merid_min = float(
            min(
                np.min(dx[dx > 1.0e-9]) if np.any(dx > 1.0e-9) else np.min(arc),
                np.min(arc),
            )
        )
    else:
        merid_min = target_cell_m
    n_aspect = int(np.ceil(thick_ref / max(merid_min * max_aspect, 1.0e-9)))
    return int(min(cap, max(floor, n_target, n_aspect)))


def resample_spine(pts: np.ndarray, n: int) -> np.ndarray:
    s = np.linspace(0.0, 1.0, n)
    return _interp_curve(_snap_axis(pts), s)


def resample_inner_to_outer(outer_rs: np.ndarray, inner: np.ndarray) -> np.ndarray:
    s = _cum_arclength(np.asarray(outer_rs, dtype=float))
    return _interp_curve(_snap_axis(inner), s)


def resample_inner_to_outer_physical(outer_rs: np.ndarray, inner: np.ndarray) -> np.ndarray:
    """Map inner curve by physical arclength of outer (not normalized parameter)."""
    outer_rs = np.asarray(outer_rs, dtype=float)
    inner = _snap_axis(inner)
    s_out = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(outer_rs, axis=0), axis=1))])
    s_in = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(inner, axis=0), axis=1))])
    out = np.zeros((len(outer_rs), 2))
    for i, sq in enumerate(s_out):
        if sq <= 0.0:
            out[i] = inner[0]
            continue
        if sq >= s_in[-1]:
            out[i] = inner[-1]
            continue
        j = max(int(np.searchsorted(s_in, sq, side="right")), 1)
        t = (sq - s_in[j - 1]) / max(s_in[j] - s_in[j - 1], 1e-15)
        out[i] = (1.0 - t) * inner[j - 1] + t * inner[j]
    return out


def _arc_from_ora(surface: str, *, n: int = 80) -> np.ndarray:
    hy = PTS["hyaloid_retina"]
    pole = (0.0, SURFACES[surface]["R2"])
    s = SURFACES[surface]
    phi = ellipse_phi_at(s["R1"], s["R2"], s["xc"], s["zc"], hy[0], hy[1])
    start = ellipse_point(s["R1"], s["R2"], s["xc"], s["zc"], phi)
    return _snap_axis(sample_ellipse_arc(surface, start, pole, n=n) * M_PER_CM)


def _build_iris_curves(bi: dict[str, np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """Table SII iris: AC face (cil→tips) and lens face (cil_post→tips), densified."""
    iris = np.asarray(bi["iris_right"], dtype=float)
    # AC-facing: anterior root → anterior turn → tip ant → tip post
    outer_raw = iris[[0, 1, 2, 3]]
    # Lens-facing: posterior root → posterior turn → tip post → tip ant (same free margin)
    inner_raw = iris[[5, 4, 3, 2]]
    outer = _snap_axis(densify_polyline(outer_raw, n_per_seg=14))
    inner = _snap_axis(densify_polyline(inner_raw, n_per_seg=14))
    return outer, inner


def build_sclera_outer_open(bi: dict[str, np.ndarray]) -> np.ndarray:
    """Open outer sclera meridian: limbus → posterior pole (outer_sclera ellipse).

    TM wrap is fluid-facing and excluded from this outer chain so cornea meets
    sclera cleanly at the limbus (no TM 'tooth' on the outer meridional path).
    """
    return _snap_axis(bi["sclera_post_right"].copy())


def build_sclera_inner_open(bi: dict[str, np.ndarray]) -> np.ndarray:
    """Open inner sclera meridian: inner limbus → choroid–sclera frontier → pole."""
    lim_in = bi["cornea_inside_right"][-1].reshape(1, 2)
    choroid = bi["choroid_sclera_right"]
    return _snap_axis(np.vstack([lim_in, choroid]))


def build_lens_curves(bi: dict[str, np.ndarray]) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    """Lens meridional curves: front (apex→eq), rear (eq→rear apex), equator index."""
    lens_r = _snap_axis(bi["lens_right"].copy())
    ie = int(np.argmax(np.abs(lens_r[:, 0])))
    front = lens_r[: ie + 1].copy()
    rear = lens_r[ie:].copy()
    front[0, 0] = 0.0
    rear[-1, 0] = 0.0
    return front, rear, lens_r, ie


def build_ac_outer_open(bi: dict[str, np.ndarray]) -> np.ndarray:
    """Open AC outer wall: cornea inner → TM → iris margin → hyaloid → lens front."""
    cor_r = bi["cornea_inside_right"]
    tm_r = bi["tm_markers_right"][:-1]
    iris_r = bi["iris_right"][:6]
    hy_r = bi["hyaloid_right"]
    lens_r = bi["lens_right"]
    ie = int(np.argmax(np.abs(lens_r[:, 0])))
    lens_eq_to_apex = lens_r[: ie + 1][::-1]
    iris_run = iris_r[:6]
    purple = hy_r[1]
    eq = hy_r[0]
    cil_ant = iris_run[0]
    path = np.vstack(
        [
            cor_r,
            tm_r[1:],
            cil_ant.reshape(1, 2),
            iris_run[1:],
            purple.reshape(1, 2),
            eq.reshape(1, 2),
            lens_eq_to_apex[1:],
        ]
    )
    path[0, 0] = 0.0
    path[-1, 0] = 0.0
    return _snap_axis(path)


def build_iris_poly(bi: dict[str, np.ndarray]) -> np.ndarray:
    return _snap_axis(bi["iris_right"][:6].copy())


def build_lens_poly(bi: dict[str, np.ndarray]) -> np.ndarray:
    lens = bi["lens_right"].copy()
    lens[0, 0] = 0.0
    lens[-1, 0] = 0.0
    if np.linalg.norm(lens[-1] - lens[0]) > 1e-12:
        lens = np.vstack([lens, lens[0:1]])
    return _snap_axis(lens)


def _axis_row_from_outer(outer_rs: np.ndarray) -> np.ndarray:
    inner = np.asarray(outer_rs, dtype=float).copy()
    inner[:, 0] = 0.0
    return inner


def _pair_lens_meridional(
    front: np.ndarray,
    rear: np.ndarray,
    n: int,
    *,
    cluster: float = 2.4,
) -> tuple[np.ndarray, np.ndarray]:
    """Equator → both apices (x=0); meridional stations sparse near apices."""
    front_open = _snap_axis(np.asarray(front[::-1], dtype=float))  # eq → front apex
    rear_open = _snap_axis(np.asarray(rear, dtype=float))  # eq → rear apex
    if n < 2:
        return front_open[:1].copy(), rear_open[:1].copy()
    t = np.linspace(0.0, 1.0, n)
    if abs(cluster - 1.0) > 1e-9:
        t = 1.0 - (1.0 - t) ** cluster
    outer = _interp_curve(front_open, t)
    inner = _interp_curve(rear_open, t)
    outer[0], inner[0] = front_open[0], rear_open[0]
    outer[-1] = front_open[-1].copy()
    inner[-1] = rear_open[-1].copy()
    outer[-1, 0] = 0.0
    inner[-1, 0] = 0.0
    # Meridional columns are vertical (constant x); rear y at same x as front.
    inner[:, 0] = outer[:, 0]
    return outer, inner


def _pair_lens_bulk(
    front: np.ndarray,
    rear: np.ndarray,
    n: int,
    *,
    cluster: float = 2.4,
    x_floor: float = 0.45e-3,
) -> tuple[np.ndarray, np.ndarray]:
    """Bulk meridional rows eq → near-apex (stop before x < x_floor)."""
    outer, inner = _pair_lens_meridional(front, rear, n, cluster=cluster)
    outer_b, inner_b = outer[:-1], inner[:-1]
    keep = np.where(outer_b[:, 0] >= x_floor)[0]
    if len(keep) < 2:
        return outer_b[:2], inner_b[:2]
    i_last = int(keep[-1])
    return outer_b[: i_last + 1], inner_b[: i_last + 1]


def _trim_lens_equator_columns(
    outer: np.ndarray,
    inner: np.ndarray,
    *,
    min_thick: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    """Drop zero-thickness equator columns; keep rim point for FSI patches."""
    outer = np.asarray(outer, dtype=float)
    inner = np.asarray(inner, dtype=float)
    thick = np.linalg.norm(outer - inner, axis=1)
    keep = np.where(thick >= min_thick)[0]
    if len(keep) == 0:
        return outer[-1:], inner[-1:], outer[0].copy()
    i0 = int(keep[0])
    if i0 == 0:
        return outer, inner, None
    return outer[i0:], inner[i0:], outer[0].copy()


def lens_surface_polylines(b: "Coat2DBuilder") -> tuple[np.ndarray, np.ndarray]:
    """Meshed lens front/rear curves (equator rim → apex) for fluid FSI boundaries."""
    zone = b.zones["lens"]
    front = np.array([b.nodes[n][:2] for n in zone.node_grid[0]], dtype=float)
    rear = np.array([b.nodes[n][:2] for n in zone.node_grid[-1]], dtype=float)
    if zone.equator_nid is not None:
        eq = np.array(b.nodes[zone.equator_nid][:2], dtype=float).reshape(1, 2)
        front = np.vstack([eq, front])
        rear = np.vstack([eq, rear])
    return front, rear


def build_tm_curves(bi: dict[str, np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """TM meridional strip: AC face (lim_in → void → CB attach) / sclera wrap (lim_out → cho_tm)."""
    tm_ac = _snap_axis(bi["tm_markers_right"][:-1].copy())
    tm_scl = _snap_axis(bi["sclera_tm_wrap_right"].copy())
    return tm_ac, tm_scl


def build_ciliary_curves(bi: dict[str, np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """Ciliary meridional shell: TM max-Y → ora (inner) and wine frontier (outer)."""
    bc = bi["band_ciliary_right"]
    ciliary_inner = _snap_axis(bc[0:37].copy())
    # Outer = choroid–sclera wine from TM attachment (cho_tm) to ora (cho_ret).
    ciliary_outer = _snap_axis(np.vstack([bc[0:1], bc[77:37:-1]]))
    return ciliary_outer, ciliary_inner


def build_solid_2d_curves(bi: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Meridional boundary curves for all solid shells [m]."""
    sclera_choroid = _arc_from_ora("choroid_sclera")
    choroid_retina = _snap_axis(bi["retina_choroid_right"].copy())
    tm_ac, tm_scl = build_tm_curves(bi)
    lens_front, lens_rear, _, _ = build_lens_curves(bi)
    ciliary_outer, ciliary_inner = build_ciliary_curves(bi)
    iris_outer, iris_inner = _build_iris_curves(bi)

    return {
        "cornea_outer": _snap_axis(bi["cornea_outside_right"].copy()),
        "cornea_inner": _snap_axis(bi["cornea_inside_right"].copy()),
        "sclera_outer": build_sclera_outer_open(bi),
        "sclera_inner": build_sclera_inner_open(bi),
        "tm_ac": tm_ac,
        "tm_scl": tm_scl,
        "ciliary_outer": ciliary_outer,
        "ciliary_inner": ciliary_inner,
        "iris_outer": _snap_axis(iris_outer),
        "iris_inner": _snap_axis(iris_inner),
        "choroid_outer": sclera_choroid,
        "choroid_inner": choroid_retina,
        "retina_outer": choroid_retina,
        "retina_inner": _snap_axis(bi["vitreous_retina_right"].copy()),
        "ora_point": bi["choroid_ret_right"][0].copy(),
        "limbus_point": bi["cornea_outside_right"][-1].copy(),
        "tm_wrap": _snap_axis(bi["sclera_tm_wrap_right"].copy()),
        "hyaloid": _snap_axis(bi["hyaloid_right"].copy()),
        "lens_front": lens_front,
        "lens_rear": lens_rear,
    }


def build_coat_2d_curves(bi: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Backward-compatible coat-only curves (ora → pole)."""
    c = build_solid_2d_curves(bi)
    return {
        "sclera_outer": c["sclera_outer_ora"] if "sclera_outer_ora" in c else _arc_from_ora("outer_sclera"),
        "sclera_inner": c["choroid_outer"],
        "choroid_outer": c["choroid_outer"],
        "choroid_inner": c["choroid_inner"],
        "retina_outer": c["retina_outer"],
        "retina_inner": c["retina_inner"],
    }


def _junction_index(spine: np.ndarray, point: np.ndarray) -> int:
    return int(np.argmin(np.linalg.norm(spine - np.asarray(point, dtype=float), axis=1)))


def _conformal_subrow(row: list[int], nodes: dict[int, tuple[float, float, float]], curve: np.ndarray) -> list[int]:
    """Contiguous node IDs from row matching curve endpoints (in row order)."""
    row_xy = np.array([nodes[t][:2] for t in row])
    i0 = int(np.argmin(np.linalg.norm(row_xy - curve[0], axis=1)))
    i1 = int(np.argmin(np.linalg.norm(row_xy - curve[-1], axis=1)))
    lo, hi = min(i0, i1), max(i0, i1)
    return row[lo : hi + 1]


def _resample_row_ids(row_ids: list[int], n: int) -> list[int]:
    if n <= 0:
        return []
    if len(row_ids) == n:
        return list(row_ids)
    if len(row_ids) == 1:
        return row_ids * n
    idx = np.linspace(0, len(row_ids) - 1, n).astype(int)
    return [row_ids[i] for i in idx]


def _dedupe_consecutive(row_ids: list[int]) -> list[int]:
    out: list[int] = []
    for nid in row_ids:
        if not out or out[-1] != nid:
            out.append(nid)
    return out


class Coat2DBuilder:
    """Structured quad strips with shared node rows at zone interfaces."""

    def __init__(self) -> None:
        self._node_id = 1
        self.zones: dict[str, Coat2DZone] = {}
        self.nodes: dict[int, tuple[float, float, float]] = {}

    def _new_node(self, x: float, y: float) -> int:
        nid = self._node_id
        self._node_id += 1
        x = float(x)
        if abs(x) < 1.0e-6:
            x = 0.0
        self.nodes[nid] = (x, y, 0.0)
        return nid

    def _row_from_xy(self, row: np.ndarray, bind: list[int] | None = None) -> list[int]:
        tags: list[int] = []
        bind = bind or []
        for i, pt in enumerate(row):
            if i < len(bind) and bind[i] > 0:
                tags.append(int(bind[i]))
            else:
                tags.append(self._new_node(pt[0], pt[1]))
        return tags

    def add_zone_cols(
        self,
        name: str,
        outer_rs: np.ndarray,
        inner_rs: np.ndarray,
        *,
        n_layers: int,
        bind_outer: list[int] | None = None,
        bind_inner: list[int] | None = None,
        collapse_tol: float = 5.0e-6,
        element: str = "quad",
        export_name: str | None = None,
    ) -> None:
        outer_rs = np.asarray(outer_rs, dtype=float)
        inner_rs = np.asarray(inner_rs, dtype=float)
        if len(outer_rs) != len(inner_rs):
            raise ValueError(f"{name}: outer/inner station count mismatch {len(outer_rs)} vs {len(inner_rs)}")

        grid_xy = np.zeros((n_layers + 1, len(outer_rs), 2))
        for j in range(n_layers + 1):
            t = j / n_layers
            grid_xy[j] = (1.0 - t) * outer_rs + t * inner_rs

        node_grid: list[list[int]] = []
        for j in range(n_layers + 1):
            if j == 0:
                bind = bind_outer
            elif j == n_layers:
                bind = bind_inner
            else:
                bind = None
            node_grid.append(self._row_from_xy(grid_xy[j], bind))

        # Collapse thin columns (outer ≈ inner) to a single node stack.
        for i in range(len(outer_rs)):
            if np.linalg.norm(grid_xy[0, i] - grid_xy[-1, i]) < collapse_tol:
                nid = node_grid[0][i]
                for j in range(1, n_layers + 1):
                    node_grid[j][i] = nid

        self.zones[name] = Coat2DZone(
            name=name,
            node_grid=node_grid,
            n_layers=n_layers,
            element=element,
            export_name=export_name,
        )

    def add_lens_zone(
        self,
        front: np.ndarray,
        rear: np.ndarray,
        *,
        n_merid: int,
        n_layers: int,
        cluster: float = 2.4,
        x_floor: float = 0.45e-3,
        equator_min_thick: float = 200e-6,
    ) -> None:
        """Structured brick strip eq → apices; volume starts where lens thickness is physical."""
        outer_bulk, inner_bulk = _pair_lens_bulk(front, rear, n_merid, cluster=cluster, x_floor=x_floor)
        front_apex = np.array([0.0, float(front[0, 1])])
        rear_apex = np.array([0.0, float(rear[-1, 1])])
        outer_rs = np.vstack([outer_bulk, front_apex.reshape(1, 2)])
        inner_rs = np.vstack([inner_bulk, rear_apex.reshape(1, 2)])
        eq_rim: np.ndarray | None = None
        if equator_min_thick > 0.0:
            outer_rs, inner_rs, eq_rim = _trim_lens_equator_columns(
                outer_rs, inner_rs, min_thick=equator_min_thick
            )
        ncols = len(outer_rs)
        grid_xy = np.zeros((n_layers + 1, ncols, 2))
        for k in range(ncols):
            xk = float(outer_rs[k, 0])
            y0 = float(outer_rs[k, 1])
            y1 = float(inner_rs[k, 1])
            for j in range(n_layers + 1):
                s = j / n_layers
                grid_xy[j, k] = (xk, (1.0 - s) * y0 + s * y1)
        grid_xy[0, 0] = outer_rs[0]
        grid_xy[-1, 0] = inner_rs[0]
        grid_xy[0, -1] = front_apex
        grid_xy[-1, -1] = rear_apex

        node_grid: list[list[int]] = []
        for j in range(n_layers + 1):
            node_grid.append(self._row_from_xy(grid_xy[j]))

        eq_nid: int | None = None
        if eq_rim is not None:
            eq_nid = self._new_node(float(eq_rim[0]), float(eq_rim[1]))

        self.zones["lens"] = Coat2DZone(
            name="lens",
            node_grid=node_grid,
            n_layers=n_layers,
            element="quad",
            export_name=None,
            equator_nid=eq_nid,
        )

    def add_fluid_ray_zone(
        self,
        name: str,
        outer_rs: np.ndarray,
        *,
        lens_poly: np.ndarray,
        iris_poly: np.ndarray,
        n_layers: int,
        bind_outer: list[int] | None = None,
    ) -> None:
        outer_rs = np.asarray(outer_rs, dtype=float)
        inner_rs = np.array([_fluid_inner_on_ray(p, lens_poly, iris_poly) for p in outer_rs])
        self.add_zone_cols(name, outer_rs, inner_rs, n_layers=n_layers, bind_outer=bind_outer)

    def add_fluid_axis_zone(
        self,
        name: str,
        outer_bind: list[int],
        *,
        n_layers: int,
    ) -> None:
        outer_rs = np.array([self.nodes[t][:2] for t in outer_bind], dtype=float)
        inner_rs = _axis_row_from_outer(outer_rs)
        self.add_zone_cols(name, outer_rs, inner_rs, n_layers=n_layers, bind_outer=outer_bind)

    def add_vitreous_anterior_zone(
        self,
        name: str,
        hy: np.ndarray,
        lens_rear: np.ndarray,
        *,
        n_layers: int,
        bind_outer: list[int] | None = None,
        bind_inner_eq: int | None = None,
    ) -> None:
        hy_rs = resample_spine(hy, len(hy) if bind_outer is None else len(bind_outer))
        if bind_outer is not None:
            hy_rs = np.array([self.nodes[t][:2] for t in bind_outer], dtype=float)
        inner_rs = resample_inner_to_outer_physical(hy_rs, lens_rear)
        bind_inner = [0] * len(hy_rs)
        if bind_inner_eq is not None:
            bind_inner[0] = int(bind_inner_eq)
        self.add_zone_cols(
            name,
            hy_rs,
            inner_rs,
            n_layers=n_layers,
            bind_outer=bind_outer,
            bind_inner=bind_inner if bind_inner_eq else None,
        )

    def add_zone(
        self,
        name: str,
        outer: np.ndarray,
        inner: np.ndarray,
        *,
        n_m: int,
        n_layers: int,
        bind_outer: list[int] | None = None,
    ) -> None:
        if bind_outer is not None:
            outer_rs = np.array([self.nodes[t][:2] for t in bind_outer], dtype=float)
            inner_rs = resample_inner_to_outer(outer_rs, inner)
        else:
            outer_rs, inner_rs = resample_pair(outer, inner, n_m)
        self.add_zone_cols(name, outer_rs, inner_rs, n_layers=n_layers, bind_outer=bind_outer)

    def add_fluid_grid_split(
        self,
        *,
        outer_rs: np.ndarray,
        inner_rs: np.ndarray,
        col_tags: list[str],
        n_layers: int,
        bind_outer: list[int] | None = None,
    ) -> None:
        """Structured fluid quads; columns tagged 'ac' or 'vitreous' for zone split at build()."""
        self.add_zone_cols(
            "_fluid",
            outer_rs,
            inner_rs,
            n_layers=n_layers,
            bind_outer=bind_outer,
        )
        self._fluid_col_tags = list(col_tags)

    def _valid_tri(self, a: int, b: int, c: int) -> bool:
        pts = [np.array(self.nodes[n][:2]) for n in (a, b, c)]
        edges = [np.linalg.norm(pts[(i + 1) % 3] - pts[i]) for i in range(3)]
        area = abs(
            pts[0][0] * pts[1][1] - pts[1][0] * pts[0][1]
            + pts[1][0] * pts[2][1] - pts[2][0] * pts[1][1]
            + pts[2][0] * pts[0][1] - pts[0][0] * pts[2][1]
        ) * 0.5
        return min(edges) >= 1.0e-12 and area >= 1.0e-15

    def _append_strip_cell(
        self,
        mesh: Coat2DMesh,
        *,
        out_name: str,
        element: str,
        n0: int,
        n1: int,
        n2: int,
        n3: int,
    ) -> None:
        ids = {n0, n1, n2, n3}
        if len(ids) < 3:
            return
        if element == "tri":
            if len(ids) == 3:
                tri = tuple(ids)
                if self._valid_tri(*tri):
                    mesh.tris.setdefault(out_name, []).append(tri)
            elif len(ids) == 4:
                for tri in ((n0, n1, n2), (n0, n2, n3)):
                    if self._valid_tri(*tri):
                        mesh.tris.setdefault(out_name, []).append(tri)
            return
        if len(ids) < 4:
            return
        pts = [np.array(self.nodes[n][:2]) for n in (n0, n1, n2, n3)]
        area = abs(
            pts[0][0] * pts[1][1] - pts[1][0] * pts[0][1]
            + pts[1][0] * pts[2][1] - pts[2][0] * pts[1][1]
            + pts[2][0] * pts[3][1] - pts[3][0] * pts[2][1]
            + pts[3][0] * pts[0][1] - pts[0][0] * pts[3][1]
        ) * 0.5
        edges = [np.linalg.norm(pts[(i + 1) % 4] - pts[i]) for i in range(4)]
        if min(edges) < 1.0e-12 or area < 1.0e-15:
            return
        mesh.zones.setdefault(out_name, []).append((n0, n1, n2, n3))

    def build(self) -> Coat2DMesh:
        mesh = Coat2DMesh(nodes=dict(self.nodes))
        fluid_tags = getattr(self, "_fluid_col_tags", None)
        for zname, zone in self.zones.items():
            out_name = zone.export_name or zname
            g = zone.node_grid
            element = zone.element
            if zname == "_fluid" and fluid_tags:
                element = "quad"
            for j in range(zone.n_layers):
                for i in range(len(g[0]) - 1):
                    cell_element = zone.element
                    if zname == "lens":
                        ncols = len(g[0])
                        x0 = self.nodes[g[0][i]][0]
                        x1 = self.nodes[g[0][i + 1]][0]
                        if x0 <= AXIS_TOL and x1 <= AXIS_TOL:
                            continue
                        if i == ncols - 2:
                            cell_element = "tri"
                    if zname == "_fluid" and fluid_tags:
                        tag = fluid_tags[i]
                        self._append_strip_cell(
                            mesh,
                            out_name=tag,
                            element="quad",
                            n0=g[j][i],
                            n1=g[j][i + 1],
                            n2=g[j + 1][i + 1],
                            n3=g[j + 1][i],
                        )
                    else:
                        self._append_strip_cell(
                            mesh,
                            out_name=out_name,
                            element=cell_element,
                            n0=g[j][i],
                            n1=g[j][i + 1],
                            n2=g[j + 1][i + 1],
                            n3=g[j + 1][i],
                        )
            if zname == "_fluid":
                continue

        if "cornea" in self.zones and "sclera" in self.zones:
            outer = self._edge_row(self.zones["cornea"].node_grid[0])
            outer += self._edge_row(self.zones["sclera"].node_grid[0])
        elif "sclera" in self.zones:
            outer = self._edge_row(self.zones["sclera"].node_grid[0])
        else:
            outer = []

        mesh.patches["outer"] = outer
        mesh.patches["fsi_active"] = self._edge_row(self.zones["retina"].node_grid[-1])
        if "tm" in self.zones:
            mesh.patches["fsi_tm"] = self._edge_row(self.zones["tm"].node_grid[0])
            mesh.patches["interface_coat_tm"] = self._edge_row(self.zones["tm"].node_grid[-1])
        if "cornea" in self.zones and "ac" not in self.zones:
            mesh.patches["fsi_cornea"] = self._edge_row(self.zones["cornea"].node_grid[-1])
        if "iris" in self.zones:
            mesh.patches["fsi_iris"] = self._edge_row(self.zones["iris"].node_grid[0])
        if "lens" in self.zones:
            lens = self.zones["lens"]
            front = self._edge_row(lens.node_grid[0])
            rear = self._edge_row(lens.node_grid[-1])
            if lens.equator_nid is not None:
                eq = int(lens.equator_nid)
                front = [(eq, lens.node_grid[0][0])] + front
                rear = [(eq, lens.node_grid[-1][0])] + rear
            mesh.patches["fsi_lens"] = front
            mesh.patches["interface_lens_vitreous"] = rear
        if "ac" in self.zones:
            mesh.patches["fsi_cornea"] = self._edge_row(self.zones["ac"].node_grid[0])
        if "vitreous" in self.zones or "_vitreous_post" in self.zones:
            hy: list[tuple[int, int]] = []
            if "vitreous" in self.zones:
                hy = self._edge_row(self.zones["vitreous"].node_grid[0])
            if "_vitreous_post" in self.zones:
                post = self.zones["_vitreous_post"].node_grid[0]
                hy += self._edge_row(post[1:] if hy else post)
            mesh.patches["fsi_hyaloid"] = hy
        mesh.patches["symmetry_0"] = self._axis_edges()
        if "sclera" in self.zones and "ciliary" in self.zones:
            cil_outer = self.zones["ciliary"].node_grid[0]
            scl_inner = self.zones["sclera"].node_grid[-1]
            i0 = scl_inner.index(cil_outer[0])
            wine = scl_inner[i0 : i0 + len(cil_outer)]
            mesh.patches["interface_coat_ciliary"] = self._shared_edge(wine, cil_outer)
        return mesh

    def _edge_row(self, row: list[int]) -> list[tuple[int, int]]:
        return [(row[i], row[i + 1]) for i in range(len(row) - 1)]

    def _shared_edge(self, a: list[int], b: list[int]) -> list[tuple[int, int]]:
        if len(a) != len(b):
            n = min(len(a), len(b))
            return [(a[i], a[i + 1]) for i in range(n - 1)]
        return self._edge_row(a)

    def _axis_edges(self) -> list[tuple[int, int]]:
        edges: list[tuple[int, int]] = []
        seen: set[tuple[int, int]] = set()
        for zone in self.zones.values():
            g = zone.node_grid
            for j in range(len(g) - 1):
                a, b = g[j][0], g[j + 1][0]
                if self.nodes[a][0] > AXIS_TOL or self.nodes[b][0] > AXIS_TOL:
                    continue
                key = (min(a, b), max(a, b))
                if key not in seen:
                    seen.add(key)
                    edges.append(key)
        return edges


def _axis_inner_from_outer(outer_rs: np.ndarray) -> np.ndarray:
    """Inner AC/vitreous row on the symmetry plane (x = 0)."""
    out = np.asarray(outer_rs, dtype=float).copy()
    out[:, 0] = 0.0
    return out


def _create_wall_row(b: Coat2DBuilder, curve: np.ndarray, n: int, key: str) -> tuple[np.ndarray, list[int]]:
    rs = resample_open(_snap_axis(curve), n)
    row = [b._new_node(float(p[0]), float(p[1])) for p in rs]
    b.wall_rows[key] = row
    return rs, row


def build_fluid_2d_zones(
    b: Coat2DBuilder,
    bi: dict[str, np.ndarray],
    cfg: dict,
    c: dict[str, np.ndarray],
) -> None:
    """AC + vitreous fluid meshes (tri/quad), lens = wall only."""
    base = cfg["layers"]
    target = cfg.get("target_cell_m", 20e-6)
    lens_poly = build_lens_poly(bi)
    iris_poly = build_iris_poly(bi)

    lens_front, lens_rear, _, _ = build_lens_curves(bi)
    lens_front_open = lens_front[::-1][:-1]
    lens_rear_open = lens_rear[:-1]
    rear_apex = lens_rear_open[-1].copy()

    cor_row = b.zones["cornea"].node_grid[-1]
    ret_row = b.zones["retina"].node_grid[-1]
    cor_xy = np.array([b.nodes[t][:2] for t in cor_row])
    ret_xy = np.array([b.nodes[t][:2] for t in ret_row])
    n_c = len(cor_row)
    hy_eq = bi["hyaloid_right"][0].copy()

    n_lr = meridional_stations(
        [lens_rear_open],
        floor=max(24, cfg["n_merid"] // 4),
        cap=max(120, cfg["n_merid"]),
        target_cell_m=target,
    )
    n_lf = meridional_stations(
        [lens_front_open],
        floor=max(20, cfg["n_merid"] // 5),
        cap=max(96, cfg["n_merid"] // 2),
        target_cell_m=target,
    )
    lr_rs, lr_row = _create_wall_row(b, lens_rear_open, n_lr, "lens_rear")
    lf_rs, lf_row = _create_wall_row(b, lens_front_open, n_lf, "lens_front")
    eq_nid = int(lf_row[0])
    lr_row[0] = eq_nid
    lr_rs[0] = lf_rs[0]
    b.wall_rows["lens_rear"] = lr_row

    # --- AC main: cornea inner → TM / iris / hyaloid (quads) ---
    ac_ref = build_ac_outer_open(bi)
    mid_path = _subpath_between(ac_ref, cor_xy[-1], hy_eq)
    n_mid = meridional_stations(
        [mid_path],
        floor=max(16, cfg["n_merid"] // 3),
        cap=max(96, cfg["n_merid"]),
        target_cell_m=target,
    )
    mid_rs = resample_open(mid_path, n_mid)
    mid_rs[0] = cor_xy[-1]
    mid_rs[-1] = hy_eq
    outer_main = np.vstack([cor_xy, mid_rs[1:]])
    inner_main = np.zeros_like(outer_main)
    inner_main[:n_c] = _axis_inner_from_outer(cor_xy)
    for k in range(len(outer_main) - n_c):
        inner_main[n_c + k] = _fluid_inner_on_ray(outer_main[n_c + k], lens_poly, iris_poly)

    b.add_zone_cols(
        "ac",
        outer_main,
        inner_main,
        n_layers=base["ac"],
        bind_outer=list(cor_row) + [0] * (len(outer_main) - n_c - 1) + [eq_nid],
    )

    # --- AC calotte: lens front → axis (tris; lens = wall) ---
    inner_lf = _axis_inner_from_outer(lf_rs)
    b.add_zone_cols(
        "_ac_lens",
        lf_rs,
        inner_lf,
        n_layers=max(6, base["ac"] // 2),
        bind_outer=lf_row,
        element="tri",
        export_name="ac",
    )

    # --- Vitreous outer: hyaloid → vitreous retina (ora → pole) ---
    hy = _snap_axis(bi["hyaloid_right"].copy())
    n_hy = meridional_stations(
        [hy],
        floor=max(12, cfg["n_merid"] // 5),
        cap=max(64, cfg["n_merid"] // 2),
        target_cell_m=target,
    )
    hy_rs = resample_open(hy, n_hy)
    hy_rs[-1] = ret_xy[0]
    outer_vit = np.vstack([hy_rs[:-1], ret_xy])
    n_hy_cols = len(hy_rs) - 1

    s_out = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(outer_vit, axis=0), axis=1))])
    s_rear = float(np.sum(np.linalg.norm(np.diff(lr_rs, axis=0), axis=1)))
    j_split = max(n_hy_cols, int(np.searchsorted(s_out, s_rear, side="right")) - 1)
    j_split = min(j_split, len(outer_vit) - 2)

    inner_vit = np.zeros_like(outer_vit)
    n_ant = j_split + 1
    inner_vit[:n_ant] = resample_inner_to_outer_physical(outer_vit[:n_ant], lr_rs)
    inner_vit[0] = np.array(b.nodes[eq_nid][:2])
    inner_vit[j_split] = rear_apex

    y_apex = float(rear_apex[1])
    y_pole = float(outer_vit[-1, 1])
    tail = len(outer_vit) - n_ant
    if tail > 0:
        for k in range(tail):
            t = (k + 1) / tail
            inner_vit[n_ant + k] = (0.0, (1.0 - t) * y_apex + t * y_pole)

    vit_bind_o = [eq_nid] + [0] * (n_hy_cols - 1) + [int(ret_row[0])] + [int(t) for t in ret_row[1:]]
    vit_bind_i = [0] * len(outer_vit)
    vit_bind_i[0] = int(lr_row[0])
    j_on_lr = min(int(round((j_split / max(n_ant - 1, 1)) * (len(lr_row) - 1))), len(lr_row) - 1)
    vit_bind_i[j_split] = int(lr_row[j_on_lr])

    n_vit_layers = base["vitreous"]
    b.add_zone_cols(
        "vitreous",
        outer_vit[:n_ant],
        inner_vit[:n_ant],
        n_layers=n_vit_layers,
        bind_outer=vit_bind_o[:n_ant],
        bind_inner=vit_bind_i[:n_ant],
        collapse_tol=12e-6,
    )

    b.add_zone_cols(
        "_vitreous_post",
        outer_vit[j_split:],
        inner_vit[j_split:],
        n_layers=n_vit_layers,
        bind_outer=vit_bind_o[j_split:],
        bind_inner=[0] * (len(outer_vit) - j_split),
        collapse_tol=8e-6,
        element="tri",
        export_name="vitreous",
    )


def build_solid_2d_conformal(bi: dict[str, np.ndarray], cfg: dict) -> Coat2DBuilder:
    """Meridional solid tissues only (fluids meshed separately via g2_fluid_2d)."""
    c = build_solid_2d_curves(bi)
    base = cfg["layers"]
    target = cfg.get("target_cell_m", 20e-6)

    spine_raw = np.vstack([c["cornea_outer"], c["sclera_outer"][1:]])
    n_m = meridional_stations(
        [spine_raw, c["retina_inner"]],
        floor=cfg["n_merid"],
        cap=cfg.get("n_merid_cap", cfg["n_merid"] * 4),
        target_cell_m=target,
    )
    spine_rs = resample_spine(spine_raw, n_m)
    i_lim = _junction_index(spine_rs, c["limbus_point"])
    i_ora = _junction_index(spine_rs, c["ora_point"])

    b = Coat2DBuilder()

    # Cornea (apex → limbus): outer follows shared spine; inner from anatomical arc
    n_cor = i_lim + 1
    cor_o = spine_rs[:n_cor]
    cor_i = resample_inner_to_outer(cor_o, c["cornea_inner"])
    b.add_zone_cols(
        "cornea",
        cor_o,
        cor_i,
        n_layers=radial_layers(c["cornea_outer"], c["cornea_inner"], n_cor, floor=base["cornea"], cap=12, target_cell_m=target),
    )

    # Sclera (limbus → pole): same radial layer count as cornea at shared limbus column.
    n_scl = len(spine_rs) - i_lim
    scl_o = spine_rs[i_lim:]
    scl_i = resample_inner_to_outer(scl_o, c["sclera_inner"])
    cor_zone = b.zones["cornea"]
    scl_layers = cor_zone.n_layers
    cor_bind_o = [cor_zone.node_grid[0][-1]] + [0] * (n_scl - 1)
    cor_bind_i = [cor_zone.node_grid[-1][-1]] + [0] * (n_scl - 1)
    b.add_zone_cols(
        "sclera",
        scl_o,
        scl_i,
        n_layers=scl_layers,
        bind_outer=cor_bind_o,
        bind_inner=cor_bind_i,
        export_name="coat",
    )
    # Full radial column at limbus (bind_outer/inner only pin outer+inner corners).
    scl_zone = b.zones["sclera"]
    for j in range(len(scl_zone.node_grid)):
        scl_zone.node_grid[j][0] = cor_zone.node_grid[j][-1]

    # Ora split on sclera INNER: anterior wine (cho_tm → ora) = ciliary; posterior = choroid
    scl_inner_row = b.zones["sclera"].node_grid[-1]
    scl_inner_xy = np.array([b.nodes[t][:2] for t in scl_inner_row])
    j_cho = _junction_index(scl_inner_xy, c["tm_wrap"][-1])
    j_ora_in = _junction_index(scl_inner_xy, c["ora_point"])
    wine_row = scl_inner_row[j_cho : j_ora_in + 1]
    coat_row = scl_inner_row[j_ora_in:]

    # TM (limbus → cho_tm): AC face ↔ sclera wrap; outer wall stays on spine above
    n_tm = meridional_stations(
        [c["tm_ac"], c["tm_scl"]],
        floor=max(24, base.get("tm", 3) * 8),
        cap=max(96, base.get("tm", 3) * 24),
        target_cell_m=target,
    )
    tm_o, tm_i = resample_pair(c["tm_ac"], c["tm_scl"], n_tm)
    scl_outer_row = b.zones["sclera"].node_grid[0]
    tm_bind_o = [0] * n_tm
    tm_bind_o[0] = int(cor_zone.node_grid[-1][-1])
    tm_bind_o[-1] = int(scl_inner_row[j_cho])
    tm_bind_i = [0] * n_tm
    tm_bind_i[0] = int(scl_outer_row[0])
    tm_bind_i[-1] = int(scl_inner_row[j_cho])
    b.add_zone_cols(
        "tm",
        tm_o,
        tm_i,
        n_layers=radial_layers(c["tm_ac"], c["tm_scl"], n_tm, floor=base.get("tm", 3), cap=8, target_cell_m=target),
        bind_outer=tm_bind_o,
        bind_inner=tm_bind_i,
        collapse_tol=20e-6,
    )

    # Ciliary (TM → ora): outer = wine segment of sclera inner; ends at ora node
    n_cil = meridional_stations(
        [c["ciliary_outer"], c["ciliary_inner"]],
        floor=max(32, base["ciliary"] * 6),
        cap=max(160, base["ciliary"] * 16),
        target_cell_m=target,
    )
    wine_bind = _dedupe_consecutive(_resample_row_ids(wine_row, n_cil))
    n_cil = len(wine_bind)
    cil_o = np.array([b.nodes[t][:2] for t in wine_bind])
    cil_i = resample_inner_to_outer(cil_o, c["ciliary_inner"])
    b.add_zone_cols(
        "ciliary",
        cil_o,
        cil_i,
        n_layers=radial_layers(c["ciliary_outer"], c["ciliary_inner"], n_cil, floor=base["ciliary"], cap=12, target_cell_m=target),
        bind_outer=wine_bind,
    )

    # Choroid + retina (ora → pole): starts at same ora node as ciliary outer end
    cho_bind = coat_row
    cho_outer = np.array([b.nodes[t][:2] for t in cho_bind])
    cho_inner = resample_inner_to_outer(cho_outer, c["choroid_inner"])
    b.add_zone_cols(
        "choroid",
        cho_outer,
        cho_inner,
        n_layers=radial_layers(c["choroid_outer"], c["choroid_inner"], len(cho_outer), floor=base["choroid"], cap=20, target_cell_m=target),
        bind_outer=cho_bind,
        export_name="coat",
    )

    ch_inner_row = b.zones["choroid"].node_grid[-1]
    ret_outer = np.array([b.nodes[t][:2] for t in ch_inner_row])
    ret_inner = resample_inner_to_outer(ret_outer, c["retina_inner"])
    b.add_zone_cols(
        "retina",
        ret_outer,
        ret_inner,
        n_layers=radial_layers(c["retina_outer"], c["retina_inner"], len(ret_outer), floor=base["retina"], cap=20, target_cell_m=target),
        bind_outer=ch_inner_row,
        export_name="coat",
    )

    # Iris — structured strip on Table SII polyline (not the ciliary hyaloid path)
    n_iris = meridional_stations(
        [c["iris_outer"], c["iris_inner"]],
        floor=max(80, base["iris"] * 10),
        cap=cfg.get("iris_n_cap", 400),
        target_cell_m=target,
    )
    iri_outer, iri_inner = resample_pair(c["iris_outer"], c["iris_inner"], n_iris)
    n_ir_layers = radial_layers(
        c["iris_outer"],
        c["iris_inner"],
        n_iris,
        floor=4,
        cap=cfg.get("iris_layers_cap", 8),
        target_cell_m=target,
    )

    # Conformal root: share ciliary-inner node closest to iris anterior root
    cil_inner_row = b.zones["ciliary"].node_grid[-1]
    cil_xy = np.array([b.nodes[t][:2] for t in cil_inner_row])
    j_attach = int(np.argmin(np.linalg.norm(cil_xy - c["iris_outer"][0], axis=1)))
    attach_nid = int(cil_inner_row[j_attach])
    iri_outer[0] = np.array(b.nodes[attach_nid][:2])
    iris_bind: list[int] = [attach_nid] + [0] * (n_iris - 1)

    b.add_zone_cols(
        "iris",
        iri_outer,
        iri_inner,
        n_layers=n_ir_layers,
        bind_outer=iris_bind,
        collapse_tol=35e-6,
    )

    # Lens — lenticular quad strip (front AC-facing ↔ rear vitreous-facing)
    if cfg.get("include_lens", True):
        front_open = c["lens_front"][::-1][:-1]
        rear_open = c["lens_rear"][:-1]
        n_lens = meridional_stations(
            [front_open, rear_open],
            floor=max(36, base.get("lens", 6) * 6),
            cap=cfg.get("lens_n_cap", 120),
            target_cell_m=target,
        )
        outer_bulk, inner_bulk = _pair_lens_bulk(c["lens_front"], c["lens_rear"], n_lens)
        n_lens_layers = _lens_radial_layers(
            outer_bulk,
            inner_bulk,
            floor=base.get("lens", 6),
            cap=cfg.get("lens_layers_cap", 24),
            target_cell_m=target,
            max_aspect=cfg.get("lens_max_aspect", 25.0),
        )
        b.add_lens_zone(
            c["lens_front"],
            c["lens_rear"],
            n_merid=n_lens,
            n_layers=n_lens_layers,
            cluster=cfg.get("lens_cluster", 2.8),
            x_floor=cfg.get("lens_x_floor_m", 1.0e-3),
            equator_min_thick=cfg.get("lens_equator_min_thick_m", 200e-6),
        )

    return b


def build_coat_2d_conformal(bi: dict[str, np.ndarray], cfg: dict) -> Coat2DBuilder:
    return build_solid_2d_conformal(bi, cfg)


def _iface_report(b: Coat2DBuilder, a: list[int], b_row: list[int], label: str) -> dict:
    n = min(len(a), len(b_row))
    same = [int(a[i] == b_row[i]) for i in range(n)]
    gaps = [
        float(np.linalg.norm(np.array(b.nodes[a[i]][:2]) - np.array(b.nodes[b_row[i]][:2])))
        for i in range(n)
        if a[i] != b_row[i]
    ]
    return {
        label: {
            "n_stations": n,
            "shared_node_ids": sum(same),
            "max_coord_gap_m": max(gaps) if gaps else 0.0,
            "conformal": sum(same) == n and (not gaps or max(gaps) == 0.0),
        }
    }


def _element_quality(
    nodes: dict[int, tuple[float, float, float]],
    ids: tuple[int, ...],
) -> dict[str, float]:
    pts = [np.array(nodes[n][:2]) for n in ids]
    n = len(ids)
    edges = [np.linalg.norm(pts[(i + 1) % n] - pts[i]) for i in range(n)]
    mn = min(edges)
    aspect = float("inf") if mn < 1.0e-15 else max(edges) / mn
    if n == 4:
        d1 = np.linalg.norm(pts[2] - pts[0])
        d2 = np.linalg.norm(pts[3] - pts[1])
        diag_ratio = float(max(d1, d2) / max(min(d1, d2), 1.0e-15))
    else:
        diag_ratio = 1.0
    cross = sum(
        pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n)
    )
    area = abs(cross) * 0.5
    return {
        "aspect": float(aspect),
        "diag_ratio": diag_ratio,
        "min_edge_m": float(mn),
        "area_m2": float(area),
    }


def _quad_quality(nodes: dict[int, tuple[float, float, float]], q: tuple[int, int, int, int]) -> dict[str, float]:
    return _element_quality(nodes, q)


def verify_coat_2d_conformal(b: Coat2DBuilder) -> dict:
    report: dict = {}

    if "cornea" in b.zones and "sclera" in b.zones:
        report.update(
            _iface_report(
                b,
                [b.zones["cornea"].node_grid[0][-1]],
                [b.zones["sclera"].node_grid[0][0]],
                "cornea_sclera_limbus_outer",
            )
        )
        report.update(
            _iface_report(
                b,
                [b.zones["cornea"].node_grid[-1][-1]],
                [b.zones["sclera"].node_grid[-1][0]],
                "cornea_sclera_limbus_inner",
            )
        )
    if "cornea" in b.zones and "tm" in b.zones:
        report.update(
            _iface_report(
                b,
                [b.zones["cornea"].node_grid[-1][-1]],
                [b.zones["tm"].node_grid[0][0]],
                "cornea_tm_limbus",
            )
        )
    if "tm" in b.zones and "sclera" in b.zones:
        scl_inner = b.zones["sclera"].node_grid[-1]
        scl_outer = b.zones["sclera"].node_grid[0]
        tm_outer = b.zones["tm"].node_grid[0]
        tm_inner = b.zones["tm"].node_grid[-1]
        j_cho = scl_inner.index(tm_outer[-1]) if tm_outer[-1] in scl_inner else int(
            np.argmin(
                np.linalg.norm(
                    np.array([b.nodes[t][:2] for t in scl_inner]) - np.array(b.nodes[tm_outer[-1]][:2]),
                    axis=1,
                )
            )
        )
        report.update(_iface_report(b, [scl_outer[0]], [tm_inner[0]], "sclera_tm_limbus_outer"))
        report.update(_iface_report(b, [scl_inner[j_cho]], [tm_outer[-1]], "tm_sclera_cho_ac"))
        report.update(_iface_report(b, [scl_inner[j_cho]], [tm_inner[-1]], "tm_sclera_cho_wrap"))
    if "sclera" in b.zones and "choroid" in b.zones:
        scl = b.zones["sclera"].node_grid[-1]
        cho_o = b.zones["choroid"].node_grid[0]
        report.update(_iface_report(b, scl[len(scl) - len(cho_o) :], cho_o, "sclera_choroid"))
    if "choroid" in b.zones and "retina" in b.zones:
        report.update(
            _iface_report(
                b,
                b.zones["choroid"].node_grid[-1],
                b.zones["retina"].node_grid[0],
                "choroid_retina",
            )
        )
    if "ciliary" in b.zones and "choroid" in b.zones:
        report.update(
            _iface_report(
                b,
                [b.zones["ciliary"].node_grid[0][-1]],
                [b.zones["choroid"].node_grid[0][0]],
                "ciliary_choroid_ora",
            )
        )
    if "sclera" in b.zones and "ciliary" in b.zones:
        cil_outer = b.zones["ciliary"].node_grid[0]
        scl_inner = b.zones["sclera"].node_grid[-1]
        i0 = scl_inner.index(cil_outer[0])
        wine = scl_inner[i0 : i0 + len(cil_outer)]
        report.update(_iface_report(b, wine, cil_outer, "sclera_ciliary"))
    if "ciliary" in b.zones and "iris" in b.zones:
        iris_root = b.zones["iris"].node_grid[0][0]
        cil_inner = b.zones["ciliary"].node_grid[-1]
        shared_root = iris_root in cil_inner
        report["ciliary_iris_root"] = {
            "n_stations": 1,
            "shared_node_ids": int(shared_root),
            "max_coord_gap_m": 0.0,
            "conformal": shared_root,
        }
        report["iris"] = {
            "n_merid": len(b.zones["iris"].node_grid[0]),
            "n_layers": b.zones["iris"].n_layers,
        }
    if "lens" in b.zones:
        report["lens"] = {
            "n_merid": len(b.zones["lens"].node_grid[0]),
            "n_layers": b.zones["lens"].n_layers,
        }
    if "cornea" in b.zones and "ac" not in b.zones:
        pass  # fsi_cornea from fluid Gmsh mesh when present

    conformal_keys = [k for k, v in report.items() if isinstance(v, dict) and v.get("conformal") is True]
    failed_keys = [k for k, v in report.items() if isinstance(v, dict) and "conformal" in v and not v["conformal"]]
    report["conformal"] = len(failed_keys) == 0
    if failed_keys:
        report["non_conformal"] = failed_keys
    report["radial_layers"] = {
        z: b.zones[z].n_layers for z in b.zones if not z.startswith("_")
    }
    n_spine = 0
    if "cornea" in b.zones:
        n_spine += len(b.zones["cornea"].node_grid[0]) - 1
    if "sclera" in b.zones:
        n_spine += len(b.zones["sclera"].node_grid[0])
    report["n_merid_spine"] = n_spine

    mesh = b.build()
    aspects: list[float] = []
    zone_quality: dict[str, dict[str, float]] = {}
    for zname, quads in mesh.zones.items():
        z_aspects = [_quad_quality(mesh.nodes, q)["aspect"] for q in quads]
        aspects.extend(z_aspects)
        if z_aspects:
            zone_quality[zname] = {
                "n_quads": len(z_aspects),
                "aspect_max": float(max(z_aspects)),
                "aspect_p95": float(np.percentile(z_aspects, 95)),
            }
    for zname, tris in mesh.tris.items():
        t_aspects = [_element_quality(mesh.nodes, t)["aspect"] for t in tris]
        aspects.extend(t_aspects)
        entry = zone_quality.setdefault(zname, {"n_quads": 0, "aspect_max": 0.0, "aspect_p95": 0.0})
        entry["n_tris"] = len(t_aspects)
        if t_aspects:
            entry["aspect_max"] = float(max(entry.get("aspect_max", 0.0), max(t_aspects)))
            entry["aspect_p95"] = float(
                max(entry.get("aspect_p95", 0.0), np.percentile(t_aspects, 95))
            )
    n_tris = sum(len(v) for v in mesh.tris.values())
    finite = [a for a in aspects if np.isfinite(a)]
    report["quality"] = {
        "n_quads": sum(len(v) for v in mesh.zones.values()),
        "n_tris": n_tris,
        "aspect_max": float(max(finite)) if finite else 0.0,
        "aspect_mean": float(np.mean(finite)) if finite else 0.0,
        "aspect_p95": float(np.percentile(finite, 95)) if finite else 0.0,
        "n_infinite_aspect": int(sum(not np.isfinite(a) for a in aspects)),
        "by_zone": zone_quality,
    }
    return report


def export_coat_2d_msh(mesh: Coat2DMesh, path: Path, *, mesh_level: str, dim: str = "2d_meridional_solid") -> dict:
    data = MshData()
    next_phy = 1
    zone_phy: dict[str, int] = {}
    for zname in SOLID_2D_ZONES:
        if zname not in mesh.zones and zname not in mesh.tris:
            continue
        zone_phy[zname] = next_phy
        data.physical[next_phy] = (2, zname)
        next_phy += 1

    patch_names = (
        "outer",
        "fsi_active",
        "fsi_cornea",
        "fsi_tm",
        "fsi_iris",
        "fsi_lens",
        "fsi_hyaloid",
        "symmetry_0",
        "interface_coat_tm",
        "interface_lens_vitreous",
        "interface_coat_ciliary",
    )
    patch_phy: dict[str, int] = {}
    for pname in patch_names:
        if pname not in mesh.patches or not mesh.patches[pname]:
            continue
        patch_phy[pname] = next_phy
        data.physical[next_phy] = (1, pname)
        next_phy += 1

    data.nodes = dict(mesh.nodes)
    for zname, quads in mesh.zones.items():
        if zname not in zone_phy:
            continue
        phy = zone_phy[zname]
        for q in quads:
            data.elements.append((3, phy, list(q)))

    for zname, tris in mesh.tris.items():
        if zname not in zone_phy:
            zone_phy[zname] = next_phy
            data.physical[next_phy] = (2, zname)
            next_phy += 1
        phy = zone_phy[zname]
        for t in tris:
            data.elements.append((2, phy, list(t)))

    for pname, segs in mesh.patches.items():
        if pname not in patch_phy:
            continue
        phy = patch_phy[pname]
        for a, nb in segs:
            data.elements.append((1, phy, [a, nb]))

    write_msh(path, data)
    all_zones = sorted(set(mesh.zones) | set(mesh.tris))
    report = {
        "mesh_level": mesh_level,
        "dim": dim,
        "zones": all_zones,
        "zone_quads": {k: len(v) for k, v in mesh.zones.items()},
        "zone_tris": {k: len(v) for k, v in mesh.tris.items()},
        "patch_segments": {k: len(v) for k, v in mesh.patches.items()},
        "n_nodes": len(mesh.nodes),
    }
    (path.parent / f"patch_groups_coat_2d_{mesh_level}.json").write_text(json.dumps(report, indent=2))
    print(f"Wrote {path}")
    print(f"Solid 2D report: {report}")
    return report


def mesh_g2_coat_2d(
    bi: dict[str, np.ndarray],
    msh_path: Path,
    *,
    mesh_level: str = "M1",
) -> dict:
    if mesh_level not in COAT_2D_LEVELS:
        raise ValueError(f"unknown coat 2D mesh_level {mesh_level}")
    cfg = COAT_2D_LEVELS[mesh_level]
    builder = build_solid_2d_conformal(bi, cfg)
    verify = verify_coat_2d_conformal(builder)
    print(f"INFO: solid 2D conformal verify: {verify}")
    mesh = builder.build()
    report = export_coat_2d_msh(mesh, msh_path, mesh_level=mesh_level)
    report["verify"] = verify
    return report
