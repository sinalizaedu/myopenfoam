"""2D meridional fluid mesh (AC + vitreous) — standalone Gmsh, FSI coords from solid rows."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from g2_coat_2d import (
    COAT_2D_LEVELS,
    Coat2DMesh,
    build_lens_curves,
    build_solid_2d_conformal,
    lens_surface_polylines,
    verify_coat_2d_conformal,
)
from g2_needle import (
    IVI_TIP_ORIGIN_M,
    NEEDLE_R_LUMEN_M,
    TIP_CELLS_ACROSS_IVI,
    TIP_REFINE_DIST_M,
    lc_tip_for_level,
    tip_origins_2d_meridional,
)
from g2_structured_mesh import MshData, write_msh

FLUID_2D_LC = {"M1": 200e-6, "M2": 140e-6, "M3": 90e-6}
FLUID_PATCHES = (
    "fsi_cornea",
    "fsi_active",
    "fsi_iris",
    "symmetry_0",
)

# Match distance for tagging boundary edges [m].
FSI_TAG_TOL = 0.45e-3
AXIS_TOL = 5.0e-5


def _fluid_lc_at(x: float, lc: float, *, x_coarsen: float, factor: float) -> float:
    """Larger characteristic length near the symmetry axis (x → 0)."""
    if x_coarsen <= 0.0 or factor <= 1.0:
        return lc
    w = float(np.exp(-max(x, 0.0) / x_coarsen))
    return lc * (1.0 + w * (factor - 1.0))


def _fluid_lc_at_xy(
    x: float,
    y: float,
    lc: float,
    *,
    x_coarsen: float,
    lc_axis: float,
    tip_xy: tuple[tuple[float, float], ...],
    lc_tip: float,
    refine_dist: float,
) -> float:
    """Blend axis coarsening with local tip (IVI/ACP) sizing on boundary points."""
    near_tip = any(float(np.hypot(x - tx, y - ty)) < refine_dist for tx, ty in tip_xy)
    if near_tip:
        return min(
            lc,
            max(lc_tip, NEEDLE_R_LUMEN_M / 6.0),
        )
    return _fluid_lc_at(x, lc, x_coarsen=x_coarsen, factor=lc_axis)


def _gmsh_axis_coarsen_field(lc: float, *, x_coarsen: float, factor: float) -> int | None:
    """Gmsh background size field: coarser fluid mesh near x = 0."""
    import gmsh

    if x_coarsen <= 0.0 or factor <= 1.0:
        return None
    amp = factor - 1.0
    inv = 1.0 / x_coarsen
    field = gmsh.model.mesh.field.add("MathEval")
    gmsh.model.mesh.field.setString(field, "F", f"{lc}*(1+{amp}*exp(-{inv}*abs(x)))")
    return field


def _embed_tip_sizing_points(
    surf_tag: int,
    tx: float,
    ty: float,
    *,
    lc_p: float,
    lc_lumen: float,
    lumen_r: float,
) -> list[int]:
    """Embed IVI/ACP sizing anchors inside a fluid surface (30G lumen target)."""
    import gmsh

    occ = gmsh.model.occ
    x0 = max(abs(tx), 1.0e-6) if abs(tx) < 1.0e-8 else float(tx)
    y0 = float(ty)
    ptags: list[int] = [occ.addPoint(x0, y0, 0.0, lc_p)]
    for rr, lc_r in ((0.45 * lumen_r, lc_lumen), (0.95 * lumen_r, lc_lumen)):
        for ang in np.linspace(-0.8 * np.pi / 2.0, 0.8 * np.pi / 2.0, 8, endpoint=False):
            xa = x0 + rr * float(np.cos(ang))
            ya = y0 + rr * float(np.sin(ang))
            if xa < 0.0:
                continue
            ptags.append(occ.addPoint(max(xa, 1.0e-6), ya, 0.0, lc_r))
    occ.synchronize()
    gmsh.model.mesh.embed(0, [int(t) for t in ptags], 2, int(surf_tag))
    return ptags


def _gmsh_tip_refinement_fields_2d(
    tip_xy: list[tuple[float, float]],
    *,
    lc_bulk: float,
    lc_tip: float,
    lumen_r: float = NEEDLE_R_LUMEN_M,
    n_cells_across: int = 10,
    refine_dist: float = TIP_REFINE_DIST_M,
) -> list[int]:
    """Ball sizing at IVI / paracentesis (30G lumen, meridional 2D).

    Tips on x=0 use the exact optical-axis centre (paracentesis / IVI sector).
    """
    import gmsh

    lc_lumen = max(lc_tip, lumen_r / n_cells_across)
    lc_p = max(lumen_r / max(n_cells_across, 6), 4.0e-6)
    fields: list[int] = []

    f_bulk = gmsh.model.mesh.field.add("Constant")
    gmsh.model.mesh.field.setNumber(f_bulk, "VIn", lc_bulk)
    fields.append(f_bulk)

    for tx, ty in tip_xy:
        f_ball = gmsh.model.mesh.field.add("Ball")
        gmsh.model.mesh.field.setNumber(f_ball, "VIn", lc_p)
        gmsh.model.mesh.field.setNumber(f_ball, "VOut", lc_bulk)
        gmsh.model.mesh.field.setNumber(f_ball, "XCenter", float(tx))
        gmsh.model.mesh.field.setNumber(f_ball, "YCenter", float(ty))
        gmsh.model.mesh.field.setNumber(f_ball, "ZCenter", 0.0)
        gmsh.model.mesh.field.setNumber(f_ball, "Radius", refine_dist)
        fields.append(f_ball)

    print(
        f"INFO: 2D tip refine ({len(tip_xy)} sites) "
        f"lc_p={lc_p:.2e} lc_lumen={lc_lumen:.2e} r_lumen={lumen_r:.2e} "
        f"dist={refine_dist:.2e} ball@axis"
    )
    return fields


def _gmsh_set_background_min(field_ids: list[int | None]) -> None:
    import gmsh

    ids = [int(f) for f in field_ids if f is not None]
    if not ids:
        return
    if len(ids) == 1:
        gmsh.model.mesh.field.setAsBackgroundMesh(ids[0])
        return
    f_min = gmsh.model.mesh.field.add("Min")
    gmsh.model.mesh.field.setNumbers(f_min, "FieldsList", ids)
    gmsh.model.mesh.field.setAsBackgroundMesh(f_min)


def _snap_axis_ring(pts: np.ndarray) -> np.ndarray:
    out = np.asarray(pts, dtype=float).copy()
    for i, (x, y) in enumerate(out):
        if abs(x) < 1.0e-6:
            out[i, 0] = 0.0
        elif x < 1.0e-6:
            out[i, 0] = 1.0e-6
    return out


def _axis_closure(a: np.ndarray, b: np.ndarray, *, n: int = 6) -> np.ndarray:
    """Points on x=0 between a and b (meridional symmetry segment)."""
    ya, yb = float(a[1]), float(b[1])
    if abs(ya - yb) < 1.0e-9:
        return np.array([[0.0, ya]])
    ys = np.linspace(ya, yb, max(n, 2))
    return np.column_stack([np.zeros(len(ys)), ys])


def _clean_boundary_ring(pts: np.ndarray, *, min_edge: float = 1.0e-6) -> np.ndarray:
    """Drop consecutive points closer than min_edge (avoids zero-length Gmsh lines)."""
    pts = _snap_axis_ring(np.asarray(pts, dtype=float))
    if len(pts) < 3:
        return pts
    out = [pts[0]]
    for p in pts[1:]:
        if np.linalg.norm(p - out[-1]) >= min_edge:
            out.append(p)
    if len(out) >= 2 and np.linalg.norm(out[0] - out[-1]) < min_edge:
        out.pop()
    return np.asarray(out)


def _finalize_boundary_ring(ring: np.ndarray) -> np.ndarray:
    """Open polygon for Gmsh; last→first edge closes the loop geometrically."""
    ring = _snap_axis_ring(np.asarray(ring, dtype=float))
    if len(ring) < 3:
        return _clean_boundary_ring(ring)
    gap = float(np.linalg.norm(ring[0] - ring[-1]))
    if gap <= 1.0e-5:
        ring = ring.copy()
        ring[-1] = ring[0]
    elif max(ring[-1][0], ring[0][0]) <= AXIS_TOL:
        mid = _axis_closure(ring[-1], ring[0], n=8)
        ring = _snap_axis_ring(np.vstack([ring, mid[1:]]))
        ring[-1] = ring[0]
    return _clean_boundary_ring(ring[:-1])


def _lens_boundary_curves(b, bi: dict[str, np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """Lens front/rear outlines for fluid void (meshed solid or anatomy only)."""
    if "lens" in b.zones:
        return lens_surface_polylines(b)
    front, rear, _, _ = build_lens_curves(bi)
    return front[::-1], rear


def build_ac_boundary(b, bi: dict[str, np.ndarray]) -> np.ndarray:
    """Closed AC polygon: FSI cornea inner + anatomy + lens void outline + axis."""
    cor = _snap_axis_ring(np.array([b.nodes[t][:2] for t in b.zones["cornea"].node_grid[-1]]))
    lf, _ = _lens_boundary_curves(b, bi)

    tm_r = bi["tm_markers_right"][:-1]
    iris_r = bi["iris_right"]
    hy_r = bi["hyaloid_right"]
    iris_run = iris_r[:6]
    path = np.vstack(
        [
            cor,
            tm_r[1:],
            iris_run[0].reshape(1, 2),
            iris_run[1:],
            hy_r[1].reshape(1, 2),
            hy_r[0].reshape(1, 2),
            lf[1:],
        ]
    )
    apex_cor = cor[0].copy()
    apex_cor[0] = 0.0
    apex_lens = path[-1].copy()
    apex_lens[0] = 0.0
    path[0] = apex_cor
    path[-1] = apex_lens
    return _finalize_boundary_ring(path)


def build_vitreous_boundary(b, bi: dict[str, np.ndarray]) -> np.ndarray:
    """Closed vitreous polygon: hyaloid + FSI retina inner + lens void outline + axis."""
    hy_r = bi["hyaloid_right"]
    ret = _snap_axis_ring(np.array([b.nodes[t][:2] for t in b.zones["retina"].node_grid[-1]]))
    _, lr = _lens_boundary_curves(b, bi)
    rear_apex = lr[-1].copy()
    rear_apex[0] = 0.0

    path = np.vstack(
        [
            hy_r,
            ret[1:],
            rear_apex.reshape(1, 2),
            lr[-2::-1],
        ]
    )
    return _finalize_boundary_ring(path)


def _fsi_reference_polylines(b, bi: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    ref: dict[str, np.ndarray] = {
        "fsi_cornea": np.array([b.nodes[t][:2] for t in b.zones["cornea"].node_grid[-1]]),
        "fsi_active": np.array([b.nodes[t][:2] for t in b.zones["retina"].node_grid[-1]]),
        "fsi_iris": np.array([b.nodes[t][:2] for t in b.zones["iris"].node_grid[0]]),
    }
    return ref


def _tag_boundary_edge(a: np.ndarray, b: np.ndarray, fsi: dict[str, np.ndarray]) -> str | None:
    mid = 0.5 * (a + b)
    if max(a[0], b[0]) <= AXIS_TOL:
        return "symmetry_0"
    best, best_d = None, float("inf")
    for name, poly in fsi.items():
        if len(poly) < 2:
            continue
        d = float(np.min(np.linalg.norm(poly - mid, axis=1)))
        if d < best_d:
            best_d, best = d, name
    return best if best_d <= FSI_TAG_TOL else None


def mesh_g2_fluid_2d(
    bi: dict[str, np.ndarray],
    fluid: dict[str, np.ndarray],
    solid_builder,
    *,
    mesh_level: str = "M1",
) -> Coat2DMesh:
    """Standalone fluid mesh (own node IDs). FSI boundaries use solid row coordinates."""
    if mesh_level not in COAT_2D_LEVELS:
        raise ValueError(mesh_level)
    cfg = COAT_2D_LEVELS[mesh_level]
    lc = FLUID_2D_LC.get(mesh_level, 200e-6)
    x_coarsen = float(cfg.get("fluid_axis_coarsen_m", 0.9e-3))
    lc_axis = float(cfg.get("fluid_axis_lc_factor", 2.6))

    ac_b = build_ac_boundary(solid_builder, bi)
    vit_b = build_vitreous_boundary(solid_builder, bi)
    fsi_ref = _fsi_reference_polylines(solid_builder, bi)

    ivi_xy, acp_xy = tip_origins_2d_meridional(ac_b)
    n_across = int(cfg.get("fluid_tip_cells_across", TIP_CELLS_ACROSS_IVI.get(mesh_level, 10)))
    lc_tip = lc_tip_for_level(mesh_level, n_cells_across=n_across)
    tip_xy = (ivi_xy, acp_xy)
    min_edge = max(lc_tip * 0.4, 5.0e-6)
    vit_b = _clean_boundary_ring(vit_b, min_edge=min_edge)
    ac_b = _clean_boundary_ring(ac_b, min_edge=min_edge)

    import gmsh

    gmsh.initialize()
    gmsh.model.add("g2_fluid_2d")
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.option.setNumber("Mesh.Algorithm", 6)
    gmsh.option.setNumber("Mesh.RecombineAll", 0)
    gmsh.option.setNumber("Mesh.Optimize", 1)
    lc_p = max(NEEDLE_R_LUMEN_M / max(n_across, 6), 4.0e-6)
    lc_min = min(lc_p, lc_tip * 0.45, 8.0e-6)
    lc_max = max(lc * max(lc_axis, 2.2), lc_tip * 8.0)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", lc_min)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", lc_max)
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 1)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 1)

    occ = gmsh.model.occ
    lc_lumen = max(lc_tip, NEEDLE_R_LUMEN_M / n_across)
    surf_tags: dict[str, int] = {}
    for zname, pts in (("ac", ac_b), ("vitreous", vit_b)):
        ptags = [
            occ.addPoint(
                float(x),
                float(y),
                0.0,
                _fluid_lc_at_xy(
                    float(x),
                    float(y),
                    lc,
                    x_coarsen=x_coarsen,
                    lc_axis=lc_axis,
                    tip_xy=tip_xy,
                    lc_tip=lc_tip,
                    refine_dist=TIP_REFINE_DIST_M,
                ),
            )
            for x, y in pts
        ]
        ltags = []
        for i in range(len(ptags)):
            a, b = ptags[i], ptags[(i + 1) % len(ptags)]
            if a != b:
                ltags.append(occ.addLine(a, b))
        surf_tags[zname] = occ.addPlaneSurface([occ.addCurveLoop(ltags)])

    occ.synchronize()
    # Paracentesis on x=0 lies on the AC symmetry edge — Ball field only (no embed).
    embed_tips: list[tuple[str, tuple[float, float]]] = []
    for zname, txy in (("vitreous", ivi_xy), ("ac", acp_xy)):
        if zname == "ac" and abs(txy[0]) < 1.0e-8:
            continue
        embed_tips.append((zname, txy))
    for zname, txy in embed_tips:
        _embed_tip_sizing_points(
            surf_tags[zname],
            txy[0],
            txy[1],
            lc_p=lc_p,
            lc_lumen=lc_lumen,
            lumen_r=NEEDLE_R_LUMEN_M,
        )

    bg_fields: list[int | None] = []
    bg_fields.extend(
        _gmsh_tip_refinement_fields_2d(
            [ivi_xy, acp_xy],
            lc_bulk=lc,
            lc_tip=lc_tip,
            n_cells_across=n_across,
        )
    )
    _gmsh_set_background_min(bg_fields)
    gmsh.model.mesh.generate(2)

    node_tags, coords, _ = gmsh.model.mesh.getNodes()
    gmsh_xyz: dict[int, tuple[float, float, float]] = {}
    for i, tag in enumerate(node_tags):
        gmsh_xyz[int(tag)] = (float(coords[3 * i]), float(coords[3 * i + 1]), float(coords[3 * i + 2]))

    raw_zones: dict[str, list[tuple[int, ...]]] = {"ac": [], "vitreous": []}
    edge_use: dict[tuple[int, int], int] = {}

    for zname, stag in surf_tags.items():
        etypes, _, nodeTags = gmsh.model.mesh.getElements(2, stag)
        for etype, flat in zip(etypes, nodeTags, strict=True):
            npe = 3 if etype == 2 else 4
            for conn in np.asarray(flat, dtype=int).reshape(-1, npe):
                c = tuple(int(n) for n in conn)
                raw_zones[zname].append(c)
                for i in range(npe):
                    a, b = c[i], c[(i + 1) % npe]
                    key = (min(a, b), max(a, b))
                    edge_use[key] = edge_use.get(key, 0) + 1

    gmsh.finalize()

    used = sorted({n for z in raw_zones.values() for c in z for n in c})
    remap = {g: i + 1 for i, g in enumerate(used)}
    nodes = {remap[g]: gmsh_xyz[g] for g in used}

    mesh = Coat2DMesh(nodes=nodes)
    for zname, elems in raw_zones.items():
        for c in elems:
            rc = tuple(remap[n] for n in c)
            if len(rc) == 3:
                mesh.tris.setdefault(zname, []).append(rc)  # type: ignore[arg-type]
            else:
                mesh.zones.setdefault(zname, []).append(rc)  # type: ignore[arg-type]

    patch_sets: dict[str, set[tuple[int, int]]] = {p: set() for p in FLUID_PATCHES}
    for (ga, gb), count in edge_use.items():
        if count != 1:
            continue
        a = np.array(nodes[remap[ga]][:2])
        b = np.array(nodes[remap[gb]][:2])
        pname = _tag_boundary_edge(a, b, fsi_ref)
        if pname:
            patch_sets[pname].add((remap[ga], remap[gb]))

    for pname, edges in patch_sets.items():
        if edges:
            mesh.patches[pname] = sorted(edges)

    nq = sum(len(v) for v in mesh.zones.values())
    nt = sum(len(v) for v in mesh.tris.values())
    print(
        f"INFO: fluid 2D standalone: {nq} quads, {nt} tris, lc={lc:.1e}, "
        f"lc_tip={lc_tip:.1e} ({n_across} cells/30G ID), "
        f"axis_coarsen={x_coarsen:.1e}×{lc_axis:.1f}, nodes={len(nodes)}"
    )
    return mesh


def export_fluid_2d_msh(mesh: Coat2DMesh, path: Path, *, mesh_level: str) -> dict:
    data = MshData()
    next_phy = 1
    zone_phy: dict[str, int] = {}
    for zname in ("ac", "vitreous"):
        if zname not in mesh.zones and zname not in mesh.tris:
            continue
        zone_phy[zname] = next_phy
        data.physical[next_phy] = (2, zname)
        next_phy += 1

    patch_phy: dict[str, int] = {}
    for pname in FLUID_PATCHES:
        if pname not in mesh.patches or not mesh.patches[pname]:
            continue
        patch_phy[pname] = next_phy
        data.physical[next_phy] = (1, pname)
        next_phy += 1

    data.nodes = dict(mesh.nodes)
    for zname, quads in mesh.zones.items():
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
        for a, b in segs:
            data.elements.append((1, phy, [a, b]))

    write_msh(path, data)
    report = {
        "mesh_level": mesh_level,
        "dim": "2d_meridional_fluid",
        "zones": sorted(set(mesh.zones) | set(mesh.tris)),
        "zone_quads": {k: len(v) for k, v in mesh.zones.items()},
        "zone_tris": {k: len(v) for k, v in mesh.tris.items()},
        "patch_segments": {k: len(v) for k, v in mesh.patches.items()},
        "n_nodes": len(mesh.nodes),
    }
    (path.parent / f"patch_groups_fluid_2d_{mesh_level}.json").write_text(json.dumps(report, indent=2))
    print(f"Wrote {path}")
    print(f"Fluid 2D report: {report}")
    return report


def mesh_g2_fluid_2d_file(
    bi: dict[str, np.ndarray],
    fluid: dict[str, np.ndarray],
    solid_builder,
    msh_path: Path,
    *,
    mesh_level: str = "M1",
) -> dict:
    mesh = mesh_g2_fluid_2d(bi, fluid, solid_builder, mesh_level=mesh_level)
    return export_fluid_2d_msh(mesh, msh_path, mesh_level=mesh_level)


def mesh_g2_coat_2d_pair(
    bi: dict[str, np.ndarray],
    fluid: dict[str, np.ndarray],
    solid_path: Path,
    fluid_path: Path,
    *,
    mesh_level: str = "M1",
) -> dict:
    """Write separate solid (+ lens) + fluid 2D meshes."""
    from g2_coat_2d import export_coat_2d_msh

    if mesh_level not in COAT_2D_LEVELS:
        raise ValueError(mesh_level)
    cfg = COAT_2D_LEVELS[mesh_level]
    builder = build_solid_2d_conformal(bi, cfg)
    verify = verify_coat_2d_conformal(builder)
    print(f"INFO: solid 2D conformal verify: {verify}")
    solid_mesh = builder.build()
    solid_report = export_coat_2d_msh(solid_mesh, solid_path, mesh_level=mesh_level, dim="2d_meridional_solid")

    solid_report["verify"] = verify

    fluid_report = mesh_g2_fluid_2d_file(bi, fluid, builder, fluid_path, mesh_level=mesh_level)
    return {"solid": solid_report, "fluid": fluid_report}
