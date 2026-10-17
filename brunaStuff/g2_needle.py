"""30G needle lumen + Model B tip sites for G2-fluid IVI/ACP."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np

# 30G lumen (clinical IVI/ACP): ID ≈ 0.14 mm → r = 0.07 mm
NEEDLE_GAUGE = "30G"
NEEDLE_ID_M = 1.4e-4
NEEDLE_R_LUMEN_M = 0.5 * NEEDLE_ID_M  # 7.0e-5 m
# topoSet sphere for subsetMesh tip cavity (numeric patch; dose/drainage via Q(t))
TOPOSET_TIP_RADIUS_M = 5.5e-4  # 0.55 mm → ~15 IVI cells on M1 bulk mesh
TOPOSET_IVI_RADIUS_M = TOPOSET_TIP_RADIUS_M
TOPOSET_ACP_RADIUS_M = TOPOSET_TIP_RADIUS_M

# Model B — 90° calotte (4× → 360°): tip centres on optical axis at x=0, z=0.
# topoSet sphereToCell ∩ wedge ≈ 1/4 sphere (numeric patch; dose/drainage via Q(t)).
IVI_TIP_ORIGIN_M = (0.0, 0.0030, 0.0)
ACP_TIP_ORIGIN_M = (0.0, -0.0070, 0.0)
TIP_ORIGINS_M = (IVI_TIP_ORIGIN_M, ACP_TIP_ORIGIN_M)


def validate_tip_on_wedge_axis(name: str, origin: tuple[float, float, float]) -> None:
    x, _y, z = origin
    if abs(x) > 1.0e-9 or abs(z) > 1.0e-9:
        raise ValueError(
            f"{name} tip must be on wedge axis (x=0, z=0) for 1/4-sphere topoSet — got {origin}"
        )


validate_tip_on_wedge_axis("IVI", IVI_TIP_ORIGIN_M)
validate_tip_on_wedge_axis("ACP", ACP_TIP_ORIGIN_M)

# Gmsh local refinement: ≥5 cells across lumen diameter
TIP_CELLS_ACROSS = 5
TIP_REFINE_DIST_M = 6.0e-4  # transition radius around each tip [m]
TIP_BOX_HALF_M = 1.5e-4     # ±0.15 mm box (covers 30G lumen ID 0.14 mm)
# IVI-only mesh-independence targets (cells across 30G ID)
TIP_CELLS_ACROSS_IVI = {
    "M6": 5,
    "M5": 8,
    "M4": 9,
    "M1": 10,
    "M7": 10,
    "M8": 8,
    "N1": 6,
    "N2": 7,
    "M2": 12,
    "M3": 14,
}
# Model B topoSet sphere (r = 0.55 mm): target cells inside sphere (OpenFOAM topoSet)
TOPOSET_CELLS_INSIDE = {
    "M6": 45,
    "M5": 55,
    "M4": 70,
    "M1": 90,
    "M7": 90,
    "M8": 55,
    "N1": 40,
    "N2": 50,
    "M2": 100,
    "M3": 110,
}
TOPOSET_REFINE_DIST_M = 9.0e-4  # Ball transition (~1.6× r_topo; limits bulk aspect ratio)
TOPOSET_REFINE_DIST_BY_LEVEL = {
    "M8": 6.5e-4,  # tighter ball — less bulk inflation around topoSet cavities
    "N1": 6.0e-4,
    "N2": 6.4e-4,
}
# Finer tip sizing on M2/M3 for mesh-independence at 30G lumen
TIP_LC_LEVEL_SCALE = {
    "M6": 1.5,
    "M5": 1.25,
    "M4": 1.12,
    "M1": 1.0,
    "M7": 1.0,
    "M8": 1.08,
    "N1": 1.28,
    "N2": 1.14,
    "M2": 0.85,
    "M3": 0.70,
}


def toposet_refine_dist_for_level(mesh_level: str) -> float:
    """Gmsh Ball radius at IVI/ACP topoSet sites (Model B)."""
    return TOPOSET_REFINE_DIST_BY_LEVEL.get(mesh_level, TOPOSET_REFINE_DIST_M)


def _clean_ring(pts, tol: float = 1e-10):
    p = np.asarray(pts, dtype=float)
    if len(p) < 3:
        return p
    out = [p[0]]
    for q in p[1:]:
        if np.linalg.norm(q - out[-1]) > tol:
            out.append(q)
    if np.linalg.norm(out[-1] - out[0]) > tol:
        out.append(out[0])
    return np.asarray(out)


def lc_tip_target(*, n_cells_across: int = 5) -> float:
    """Target edge length for ≥n_cells_across over 30G lumen ID."""
    return max(NEEDLE_ID_M / n_cells_across, 4.0e-6)


def lc_tip_for_level(
    mesh_level: str,
    *,
    n_cells_across: int = TIP_CELLS_ACROSS,
) -> float:
    """Mesh-level tip edge length (M3 finest at nominal 30G lumen)."""
    scale = TIP_LC_LEVEL_SCALE.get(mesh_level, 1.0)
    return lc_tip_target(n_cells_across=n_cells_across) * scale


def lc_toposet_for_level(
    mesh_level: str,
    *,
    n_cells_inside: int | None = None,
) -> float:
    """Edge length for ~n uniform cells inside topoSet sphere (Model B, no 30G embed)."""
    n = n_cells_inside or TOPOSET_CELLS_INSIDE.get(mesh_level, 28)
    vol = (4.0 / 3.0) * math.pi * TOPOSET_TIP_RADIUS_M**3
    return max((vol / n) ** (1.0 / 3.0), 6.0e-5)


def acp_tip_2d_meridional(ac_boundary: np.ndarray) -> tuple[float, float]:
    """Paracentesis site on optical axis (x=0) inside AC meridional bulk."""
    p = np.asarray(ac_boundary, dtype=float)
    axis = p[p[:, 0] <= 1.0e-8]
    if len(axis):
        y = float(np.median(axis[:, 1]))
    else:
        y = float(ACP_TIP_ORIGIN_M[1])
    return (0.0, y)


def tip_origins_2d_meridional(
    ac_boundary: np.ndarray | None = None,
) -> tuple[tuple[float, float], tuple[float, float]]:
    """IVI (vitreous) and ACP/paracentesis (AC) sites in the meridional (x, y) plane [m]."""
    ivi = (float(IVI_TIP_ORIGIN_M[0]), float(IVI_TIP_ORIGIN_M[1]))
    if ac_boundary is not None:
        acp = acp_tip_2d_meridional(ac_boundary)
    else:
        acp = (float(ACP_TIP_ORIGIN_M[0]), float(ACP_TIP_ORIGIN_M[1]))
    return ivi, acp


def tip_origins_for(sites: str) -> tuple[tuple[float, float, float], ...]:
    """Return tip origin(s) for Gmsh refinement: 'ivi', 'acp', or 'both'."""
    if sites == "ivi":
        return (IVI_TIP_ORIGIN_M,)
    if sites == "acp":
        return (ACP_TIP_ORIGIN_M,)
    if sites == "both":
        return TIP_ORIGINS_M
    raise ValueError(f"tip sites must be ivi, acp, or both — got {sites!r}")


def _foam_vec(xyz: tuple[float, float, float]) -> str:
    return f"({xyz[0]:.4f} {xyz[1]:.4f} {xyz[2]:.4f})"


def lumen_embed_points(
    origin: tuple[float, float, float],
    *,
    r: float = NEEDLE_R_LUMEN_M,
) -> list[tuple[float, float, float]]:
    """Embedded nodes on / inside lumen sphere (centre + surface ring)."""
    return lumen_anchor_points(origin, r=r)


def _tip_x(ox: float) -> float:
    """Meridional / quarter-eye: IVI and paracentesis sit on x=0 (optical axis)."""
    return 0.0 if abs(ox) < 1.0e-8 else float(ox)


def lumen_sizing_points(
    origin: tuple[float, float, float],
    *,
    r: float = NEEDLE_R_LUMEN_M,
) -> list[tuple[float, float, float]]:
    """Off-body sizing anchors for Gmsh Distance field (not embedded)."""
    ox, oy, oz = origin
    x = _tip_x(ox)
    rs = 0.85 * r
    pts = [
        (x, float(oy), float(oz)),
        (x, float(oy + rs), float(oz)),
        (x, float(oy - rs), float(oz)),
        (x, float(oy), float(oz + rs)),
        (x, float(oy), float(oz - rs)),
    ]
    if x + rs >= 0.0:
        pts.append((x + rs, float(oy), float(oz)))
    return pts


def lumen_anchor_points(
    origin: tuple[float, float, float],
    *,
    r: float = NEEDLE_R_LUMEN_M,
) -> list[tuple[float, float, float]]:
    """Nodes on / inside the 30G lumen sphere (centre + surface samples)."""
    ox, oy, oz = origin
    x = _tip_x(ox)
    centre = (x, float(oy), float(oz))
    pts = [centre]
    # Surface ring in y–z and x-offset samples (≥12 around lumen)
    for dy, dz in (
        (r, 0.0),
        (-r, 0.0),
        (0.0, r),
        (0.0, -r),
        (r * 0.866, r * 0.5),
        (r * 0.866, -r * 0.5),
        (-r * 0.866, r * 0.5),
        (-r * 0.866, -r * 0.5),
        (r * 0.5, r * 0.866),
        (r * 0.5, -r * 0.866),
        (-r * 0.5, r * 0.866),
        (-r * 0.5, -r * 0.866),
    ):
        pts.append((x, float(oy + dy), float(oz + dz)))
    for dx in (r, -r, r * 0.707, -r * 0.707):
        xa = x + dx
        if xa >= 0.0:
            pts.append((xa, float(oy), float(oz)))
    return pts


def _inject_axis_stations(
    pts: np.ndarray,
    stations: list[tuple[float, float]],
    *,
    x_axis: float = 0.0,
) -> np.ndarray:
    """Insert (y, lc) anchor vertices on a meridional polyline (for Gmsh point sizing)."""
    p = np.asarray(pts, dtype=float).copy()
    if len(p) < 2:
        return p
    if np.linalg.norm(p[0] - p[-1]) < 1e-12:
        p = p[:-1]
    out = [p[0]]
    si = 0
    stations = sorted(stations, key=lambda t: t[0])
    for i in range(1, len(p)):
        a, b = p[i - 1], p[i]
        while si < len(stations) and stations[si][0] <= max(a[1], b[1]) + 1e-12:
            y_t, _lc = stations[si]
            if min(a[1], b[1]) - 1e-9 <= y_t <= max(a[1], b[1]) + 1e-9:
                t = (y_t - a[1]) / (b[1] - a[1] + 1e-30)
                if 0.0 < t < 1.0:
                    out.append(np.array([x_axis, y_t]))
            si += 1
        out.append(b)
    ring = np.vstack(out)
    return _clean_ring(ring)


def _ring_with_tip_stations(
    pts_m: np.ndarray,
    tip_y: float | None,
    *,
    lc_default: float,
    lc_tip: float,
) -> tuple[np.ndarray, float]:
    pts = np.asarray(pts_m, dtype=float)
    if tip_y is not None:
        pts = _inject_axis_stations(pts, [(tip_y, lc_tip)])
    return pts, lc_default


def write_topo_set_ivi(path: Path) -> None:
    ox, oy, oz = IVI_TIP_ORIGIN_M
    r = TOPOSET_IVI_RADIUS_M
    r_lumen = NEEDLE_R_LUMEN_M
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      topoSetDict;
}}

// Model B — IVI tip cavity (topoSet r={r:.6g} m; physical 30G lumen r={r_lumen:.6g} m). Dose via Q(t).

actions
(
    // Nearest cell to tip point (guaranteed non-empty)
    {{
        name    ivi_tip_cells;
        type    cellSet;
        action  new;
        source  nearestToCell;
        points
        (
            ({ox} {oy} {oz})
        );
    }}
    // Add any cells whose centres fall inside the lumen sphere
    {{
        name    ivi_tip_cells;
        type    cellSet;
        action  add;
        source  sphereToCell;
        origin  ({ox} {oy} {oz});
        radius  {r:.6g};
    }}
    {{
        name    fluid_keep;
        type    cellSet;
        action  new;
        source  boxToCell;
        box     (-1 -1 -1) (1 1 1);
    }}
    {{
        name    fluid_keep;
        type    cellSet;
        action  delete;
        source  cellToCell;
        set     ivi_tip_cells;
    }}
);
"""
    )


def write_topo_set_acp(path: Path) -> None:
    ox, oy, oz = ACP_TIP_ORIGIN_M
    r = TOPOSET_ACP_RADIUS_M
    r_lumen = NEEDLE_R_LUMEN_M
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      topoSetDict;
}}

// Model B — ACP tip cavity (topoSet r={r:.6g} m; physical 30G lumen r={r_lumen:.6g} m). Drainage via Q(t).

actions
(
    {{
        name    acp_tip_cells;
        type    cellSet;
        action  new;
        source  nearestToCell;
        points
        (
            ({ox} {oy} {oz})
        );
    }}
    {{
        name    acp_tip_cells;
        type    cellSet;
        action  add;
        source  sphereToCell;
        origin  ({ox} {oy} {oz});
        radius  {r:.6g};
    }}
    {{
        name    fluid_keep;
        type    cellSet;
        action  new;
        source  boxToCell;
        box     (-1 -1 -1) (1 1 1);
    }}
    {{
        name    fluid_keep;
        type    cellSet;
        action  delete;
        source  cellToCell;
        set     acp_tip_cells;
    }}
);
"""
    )


def write_topo_set_ivi_zone(path: Path) -> None:
    """IVI tip as cellZone only (doc-g2-sim5 — no subsetMesh cavity)."""
    ox, oy, oz = IVI_TIP_ORIGIN_M
    r = TOPOSET_IVI_RADIUS_M
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      topoSetDict;
}}

// Model C — IVI volumetric source zone (r={r:.6g} m). Dose via fvOptions semiImplicitSource.

actions
(
    {{
        name    ivi_tip_cells;
        type    cellSet;
        action  new;
        source  nearestToCell;
        points
        (
            ({ox} {oy} {oz})
        );
    }}
    {{
        name    ivi_tip_cells;
        type    cellSet;
        action  add;
        source  sphereToCell;
        origin  ({ox} {oy} {oz});
        radius  {r:.6g};
    }}
    {{
        name    ivi_tip_zone;
        type    cellZoneSet;
        action  new;
        source  setToCellZone;
        set     ivi_tip_cells;
    }}
);
"""
    )


def write_topo_set_acp_zone(path: Path) -> None:
    """ACP tip as cellZone only (doc-g2-sim5 — no subsetMesh cavity)."""
    ox, oy, oz = ACP_TIP_ORIGIN_M
    r = TOPOSET_ACP_RADIUS_M
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      topoSetDict;
}}

// Model C — ACP volumetric sink zone (r={r:.6g} m). Drainage via fvOptions semiImplicitSource.

actions
(
    {{
        name    acp_tip_cells;
        type    cellSet;
        action  new;
        source  nearestToCell;
        points
        (
            ({ox} {oy} {oz})
        );
    }}
    {{
        name    acp_tip_cells;
        type    cellSet;
        action  add;
        source  sphereToCell;
        origin  ({ox} {oy} {oz});
        radius  {r:.6g};
    }}
    {{
        name    acp_tip_zone;
        type    cellZoneSet;
        action  new;
        source  setToCellZone;
        set     acp_tip_cells;
    }}
);
"""
    )


def sync_case_topo_sets(repo: Path) -> None:
    cases = repo / "cases"
    write_topo_set_ivi(cases / "doc-g2-sim2/fluid/system/topoSetDict.iviTip")
    write_topo_set_ivi(cases / "doc-g2-sim4/fluid/system/topoSetDict.iviTip")
    write_topo_set_acp(cases / "doc-g2-sim3/fluid/system/topoSetDict.acpTip")
    write_topo_set_acp(cases / "doc-g2-sim4/fluid/system/topoSetDict.acpTip")
    write_topo_set_ivi_zone(cases / "T1: Volume vs Patch/doc-g2-sim5/fluid/system/topoSetDict.iviZone")
    write_topo_set_acp_zone(cases / "T1: Volume vs Patch/doc-g2-sim5/fluid/system/topoSetDict.acpZone")
