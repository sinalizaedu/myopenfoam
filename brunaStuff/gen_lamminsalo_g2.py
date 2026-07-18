#!/usr/bin/env python3
"""
G2 anatomical rabbit-eye geometry (Missel 2012 / Lamminsalo 2018).

G1 right-half meridional fluid silhouette, revolved 90° about the optical
axis → 3D quarter-calotte (1/4 of the eye). The two cut planes are symmetry
faces; four copies recover the full 360° eye.

Coordinate tables are in cm (Missel):
  X = radial (perpendicular to optical axis)
  Z = optical axis, positive = posterior

OpenFOAM mapping (SI meters):
  x = X * 1e-2   (meridional radial; G2 uses x ≥ 0 half only)
  y = Z * 1e-2   (optical axis = revolve axis)
  revolve about +y by +90° → octant x ≥ 0, z ≥ 0

Usage:
  .venv-geom/bin/python brunaStuff/gen_lamminsalo_g2.py
  .venv-geom/bin/python brunaStuff/gen_lamminsalo_g2.py --mesh
  .venv-geom/bin/python brunaStuff/gen_lamminsalo_g2.py --case doc-g2-sim1 --mesh
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "brunaStuff"))

from gen_lamminsalo_2d import (  # noqa: E402
    MESH_LEVELS,
    M_PER_CM,
    PTS,
    SURFACES,
    _clean_ring,
    _iris_loop_m,
    build_bilateral_m,
    build_outlines_cm,
    densify_polyline,
)

DEFAULT_CASE = "doc-g2-sim1"
REVOLVE_DEG = 90.0
REVOLVE_RAD = math.radians(REVOLVE_DEG)


def case_paths(case_name: str = DEFAULT_CASE):
    case = REPO / "cases" / case_name
    return case, case / "geometry", case / "figures"


# ---------------------------------------------------------------------------
# Right-half fluid rings (meridional plane z = 0, x ≥ 0)
# ---------------------------------------------------------------------------
def build_half_ac_m(bi: dict[str, np.ndarray]) -> np.ndarray:
    """Closed right-half AC ∪ TM (cornea → TM → iris margin → hyaloid → lens front → axis)."""
    cor_r = bi["cornea_inside_right"]
    tm_r = bi["tm_markers_right"][:-1]
    iris_r = bi["iris_right"]
    hy_r = bi["hyaloid_right"]
    lens_r = bi["lens_right"]
    ie = int(np.argmax(np.abs(lens_r[:, 0])))
    lens_eq_to_apex = lens_r[: ie + 1][::-1]  # eq → front apex
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
    # Close on optical axis: front lens apex → cornea apex
    apex_cor = cor_r[0].copy()
    apex_cor[0] = 0.0
    apex_lens = path[-1].copy()
    apex_lens[0] = 0.0
    path[0] = apex_cor
    path[-1] = apex_lens
    if abs(apex_lens[1] - apex_cor[1]) > 1e-12:
        path = np.vstack([path, apex_cor.reshape(1, 2)])
    else:
        path = np.vstack([path, path[0:1]])
    return _clean_ring(path)


def build_half_vitreous_m(bi: dict[str, np.ndarray]) -> np.ndarray:
    """Closed right-half vitreous (hyaloid → ora → pole → axis → lens rear → eq)."""
    hy_r = bi["hyaloid_right"]
    vit_r = bi["vitreous_retina_right"].copy()
    vit_r[-1, 0] = 0.0
    lens_r = bi["lens_right"]
    ie = int(np.argmax(np.abs(lens_r[:, 0])))
    lens_rear = lens_r[ie:].copy()  # eq → rear apex
    lens_rear[-1, 0] = 0.0
    pole = vit_r[-1].copy()
    pole[0] = 0.0
    rear_apex = lens_rear[-1].copy()
    rear_apex[0] = 0.0

    path = np.vstack(
        [
            hy_r,  # eq → purple → … → ora
            vit_r[1:],  # ora → pole
            rear_apex.reshape(1, 2),  # axis pole → rear apex
            lens_rear[-2::-1],  # rear → eq
        ]
    )
    if np.linalg.norm(path[-1] - path[0]) > 1e-12:
        path = np.vstack([path, path[0:1]])
    return _clean_ring(path)


def build_half_fluid_rings(bi: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    ac = build_half_ac_m(bi)
    vit = build_half_vitreous_m(bi)
    iris = _clean_ring(_iris_loop_m(bi["iris_right"]))
    return {"band_ac_half": ac, "band_vitreous_half": vit, "iris_half": iris}


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------
def plot_half_meridional(
    bi: dict[str, np.ndarray],
    half: dict[str, np.ndarray],
    path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.2, 8.0))
    mm = 1.0e3

    def stroke(pts, **kw):
        p = np.asarray(pts) * mm
        ax.plot(p[:, 0], p[:, 1], **kw)

    def fill(pts, color, label, alpha=0.35):
        p = np.asarray(pts) * mm
        ax.fill(p[:, 0], p[:, 1], color=color, alpha=alpha, label=label, linewidth=0)

    fill(half["band_ac_half"], "#7ec8c8", "AC ∪ TM (half)", alpha=0.40)
    fill(half["band_vitreous_half"], "#6fa8dc", "Vitreous (half)", alpha=0.40)
    fill(half["iris_half"], "#c0392b", "Iris (hole)", alpha=0.55)

    stroke(bi["lens_right"], color="#1e8449", lw=1.6, label="Lens (half)")
    stroke(bi["cornea_inside_right"], color="#e67e22", lw=1.2, label="Cornea inside")
    stroke(bi["vitreous_retina_right"], color="#2874a6", lw=1.2, label="Vitreous–retina")
    stroke(bi["hyaloid_right"], color="#8e44ad", lw=1.2, label="Hyaloid")
    stroke(bi["tm_markers_right"], color="#d35400", lw=1.4, marker="o", ms=3, label="TM")

    ax.axvline(0.0, color="0.35", ls="--", lw=0.9, label="Optical axis (revolve)")
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x [mm]  (radial, half-domain x ≥ 0)")
    ax.set_ylabel("y [mm]  (optical axis, + posterior)")
    ax.set_title(
        "G2 meridional half — Missel / Lamminsalo\n"
        f"revolve {REVOLVE_DEG:.0f}° about +y → quarter calotte"
    )
    ax.legend(loc="upper right", fontsize=7, framealpha=0.92)
    ax.grid(True, alpha=0.25)
    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-9.5, 9.0)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {path}")


def _revolve_polyline(pts_xy: np.ndarray, n_theta: int = 24) -> tuple[np.ndarray, list]:
    """Revolve (x,y) polyline about +y over [0, 90°]; return verts and faces."""
    pts = np.asarray(pts_xy, dtype=float)
    if np.linalg.norm(pts[0] - pts[-1]) < 1e-14:
        pts = pts[:-1]
    thetas = np.linspace(0.0, REVOLVE_RAD, n_theta)
    verts = []
    for th in thetas:
        c, s = math.cos(th), math.sin(th)
        for x, y in pts:
            verts.append((x * c, y, x * s))
    verts = np.asarray(verts, dtype=float)
    n = len(pts)
    faces = []
    for j in range(n_theta - 1):
        for i in range(n):
            i2 = (i + 1) % n
            a = j * n + i
            b = j * n + i2
            c = (j + 1) * n + i2
            d = (j + 1) * n + i
            faces.append([a, b, c, d])
    return verts, faces


def plot_calotte_3d(half: dict[str, np.ndarray], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(8.5, 7.0))
    ax = fig.add_subplot(111, projection="3d")
    mm = 1.0e3

    # Outer fluid silhouette only (cleaner 3D calotte)
    outer = half["band_vitreous_half"]
    # Prefer fused-looking envelope: vitreous + AC outline via cornea/TM from AC ring
    # Draw both volumes with denser angular samples
    for key, color, alpha, label in (
        ("band_vitreous_half", "#2874a6", 0.45, "Vitreous"),
        ("band_ac_half", "#48a9a6", 0.50, "AC ∪ TM"),
    ):
        verts, faces = _revolve_polyline(half[key], n_theta=28)
        vmm = verts * mm
        polys = [[vmm[i] for i in f] for f in faces]
        coll = Poly3DCollection(
            polys,
            alpha=alpha,
            facecolor=color,
            edgecolor=(0.15, 0.15, 0.15, 0.08),
            linewidths=0.15,
            label=label,
        )
        ax.add_collection3d(coll)

    # Symmetry plane outlines (θ=0 solid, θ=90 dashed)
    for key, color in (("band_ac_half", "#1a5276"), ("band_vitreous_half", "#1a5276")):
        p = np.asarray(half[key]) * mm
        ax.plot(p[:, 0], p[:, 1], np.zeros_like(p[:, 0]), color=color, lw=1.1)
        ax.plot(np.zeros_like(p[:, 0]), p[:, 1], p[:, 0], color="#7d3c98", lw=1.1, ls="--")

    ax.plot([0, 0], [-8.5, 8.0], [0, 0], color="#c0392b", lw=1.6, label="Optical axis +y")
    ax.plot([], [], [], color="#1a5276", lw=1.1, label="symmetry_0 (θ=0°)")
    ax.plot([], [], [], color="#7d3c98", lw=1.1, ls="--", label="symmetry_90 (θ=90°)")
    ax.set_xlabel("x [mm]")
    ax.set_ylabel("y [mm] (optical)")
    ax.set_zlabel("z [mm]")
    ax.set_title("G2 — 90° calotte · 4× symmetry → 360° eye")
    ax.legend(loc="upper left", fontsize=7)
    ax.set_box_aspect((1, 1.15, 1))
    ax.view_init(elev=22, azim=-48)
    ax.set_xlim(0, 10)
    ax.set_ylim(-9, 8)
    ax.set_zlim(0, 10)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {path}")

# ---------------------------------------------------------------------------
# Docs
# ---------------------------------------------------------------------------
def write_tables_md(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = f"""# G2 geometry tables (Missel / Lamminsalo ESM)

Same SI–SII tables as G1. Units in tables: **cm**. OpenFOAM uses **metres**.

## Nomenclature

- **G1** = anatomical 2D planar bilateral (empty slab in z).
- **G2** = G1 **right-half** meridional fluid silhouette, **revolved {REVOLVE_DEG:.0f}°**
  about the optical axis (`+y`) → 3D quarter-calotte.
- Two planar cut faces = **symmetry** patches; **4 × 90° = 360°** of the eye.
- **Sim 1 fluid domain** = AC + vitreous + TM only (lens / iris are holes).

## Construction

1. Build right-half rings in the plane `z = 0`, `x ≥ 0` (same curves as G1).
2. Fuse AC ∪ vitreous, cut iris hole.
3. `OCC revolve` about `(0,1,0)` by `{REVOLVE_DEG:.0f}°`.
4. Physical patches:
   - `symmetry_0` — original meridional plane (`z = 0`)
   - `symmetry_90` — revolved plane (`x = 0`, `z ≥ 0`)
   - `ac_inlet`, `outlet_tm`, `lens_wall`, `iris_wall`, `wall`

## Coordinate map

| Missel | OpenFOAM G2 |
|--------|-------------|
| X (radial) | `x = X·10⁻²` (half-plane, then revolved) |
| Z (optical) | `y = Z·10⁻²` (**revolve axis**) |
| — | `z` from revolution |

## Model choices (shared with G1)

- No canal of Petit.
- Iris = Table SII polyline; iris–lens gap ≥ 30 µm.
- Single-sided TM / inlet (no left mirrors).

## Generated artefacts

- `geometry/eye_g2_lamminsalo.{{geo,msh,vtk}}`
- `figures/g2_half_meridional.png`
- `figures/g2_calotte_3d.png`
"""
    path.write_text(text)
    print(f"Wrote {path}")


def write_geo_stub(half: dict[str, np.ndarray], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "// G2 Missel/Lamminsalo — 90° calotte (revolve half about optical axis)",
        "// Generated by brunaStuff/gen_lamminsalo_g2.py",
        "SetFactory(\"OpenCASCADE\");",
        f"angle = {REVOLVE_RAD:.10f};  // {REVOLVE_DEG:.0f} deg",
        "lc = 4.0e-4;",
        "",
        "// NOTE: Boolean fluid + revolve are built via the gmsh Python API (--mesh).",
        "",
    ]
    pid = 1
    for name in ("band_ac_half", "band_vitreous_half", "iris_half"):
        pts = half[name]
        ids = []
        for x, y in pts[:-1] if np.linalg.norm(pts[0] - pts[-1]) < 1e-14 else pts:
            lines.append(f"Point({pid}) = {{{x:.8e}, {y:.8e}, 0, lc}};")
            ids.append(pid)
            pid += 1
        lines.append(f"Spline({pid}) = {{{', '.join(map(str, ids + [ids[0]]))}}};")
        lines.append(f"// {name} curve {pid}")
        pid += 1
        lines.append("")
    path.write_text("\n".join(lines) + "\n")
    print(f"Wrote {path}")


def write_toposet_g2(path: Path) -> None:
    """topoSetDict for vitreous / TM cellZones on the G2 90° sector."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tm = PTS["tm_cornea_void"]
    t2 = PTS["tm_ciliary_void"]
    pad = 2.5e-4
    x0 = min(tm[0], t2[0]) * M_PER_CM - pad
    x1 = max(tm[0], t2[0]) * M_PER_CM + pad
    y0 = min(tm[1], t2[1]) * M_PER_CM - pad
    y1 = max(tm[1], t2[1]) * M_PER_CM + pad
    # After 90° revolve, TM sits in x≥0, z≥0 — use a cylindrical pad via box
    z1 = x1  # same radial extent
    text = f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      topoSetDict;
}}

// G2 90° calotte cellZones (Missel/Lamminsalo)
// TM: single sector (no left mirror). pad={pad:.1e} m.

actions
(
    {{
        name    tm_zone;
        type    cellSet;
        action  new;
        source  boxToCell;
        box     ({x0:.6e} {y0:.6e} {-pad:.6e}) ({x1:.6e} {y1:.6e} {z1:.6e});
    }}
    {{
        name    tm_zone;
        type    cellZoneSet;
        action  new;
        source  setToCellZone;
        set     tm_zone;
    }}

    {{
        name    vitreous_zone;
        type    cellSet;
        action  new;
        source  boxToCell;
        box     (-1.0e-4 -1.5e-3 -1.0e-4) (8.5e-3 7.4e-3 8.5e-3);
    }}
    {{
        name    vitreous_zone;
        type    cellSet;
        action  delete;
        source  boxToCell;
        box     ({x0:.6e} {y0:.6e} {-pad:.6e}) ({x1:.6e} {y1:.6e} {z1:.6e});
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
# Gmsh mesh
# ---------------------------------------------------------------------------
def mesh_with_gmsh(
    half: dict[str, np.ndarray],
    msh_path: Path,
    *,
    mesh_level: str = "M1",
) -> None:
    """
    G2 fluid calotte for OpenFOAM (gmshToFoam):
      (AC ∪ vitreous ∪ TM)_half − iris, revolved 90° about +y.
    Patches: symmetry_0, symmetry_90, ac_inlet, outlet_tm, lens_wall, iris_wall, wall.
    """
    import gmsh

    if mesh_level not in MESH_LEVELS:
        raise ValueError(f"unknown mesh_level {mesh_level}")
    sizes = MESH_LEVELS[mesh_level]
    # 3D sector needs slightly coarser bulk than the 1-layer G1 slab
    lc_bulk = max(sizes["lc"], 4.0e-4)
    lc_fine = sizes["lc_fine"]

    gmsh.initialize()
    gmsh.model.add("eye_g2_lamminsalo")
    gmsh.option.setNumber("General.Terminal", 1)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", lc_fine)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", lc_bulk * 1.5)
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)

    occ = gmsh.model.occ

    def add_ring(pts_m, lc=2.0e-4, n_per_seg: int | None = 4):
        pts = np.asarray(pts_m, dtype=float)
        if n_per_seg:
            pts = densify_polyline(pts, n_per_seg=n_per_seg)
        pts = _clean_ring(pts, tol=1e-9)[:-1]
        # Keep OCC stable
        if len(pts) > 160:
            idx = np.linspace(0, len(pts) - 1, 160).astype(int)
            pts = pts[idx]
        ptags = [occ.addPoint(float(x), float(y), 0.0, lc) for x, y in pts]
        ltags = []
        for i in range(len(ptags)):
            a, b = ptags[i], ptags[(i + 1) % len(ptags)]
            if a != b:
                ltags.append(occ.addLine(a, b))
        return occ.addPlaneSurface([occ.addCurveLoop(ltags)])

    s_ac = add_ring(half["band_ac_half"], lc=lc_fine, n_per_seg=3)
    s_vit = add_ring(half["band_vitreous_half"], lc=lc_bulk, n_per_seg=3)
    fused = occ.fuse([(2, s_ac)], [(2, s_vit)], removeObject=True, removeTool=True)
    occ.synchronize()
    if not fused[0]:
        raise RuntimeError("OCC fuse AC∪vitreous (half) produced nothing")

    iris = densify_polyline(half["iris_half"], n_per_seg=8)
    try:
        cut = occ.cut(
            [e for e in fused[0] if e[0] == 2],
            [(2, add_ring(iris, lc=lc_fine * 0.5, n_per_seg=None))],
            removeObject=True,
            removeTool=True,
        )
        occ.synchronize()
        fluid_surfaces = [e for e in cut[0] if e[0] == 2] if cut[0] else []
        if not fluid_surfaces:
            raise RuntimeError("iris cut emptied fluid")
        print("INFO: cut Lamminsalo iris hole (right half)")
    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: iris hole cut failed ({exc}); keeping AC∪vit fuse only")
        fluid_surfaces = [e for e in fused[0] if e[0] == 2]

    print(f"INFO: fluid faces before revolve: {len(fluid_surfaces)}")
    seed_caps = [s[1] for s in fluid_surfaces]

    # Revolve about optical axis (+y) by 90°
    out = occ.revolve(
        fluid_surfaces,
        0,
        0,
        0,  # point on axis
        0,
        1,
        0,  # +y
        REVOLVE_RAD,
    )
    occ.synchronize()

    volume_tags = [e[1] for e in out if e[0] == 3]
    if not volume_tags:
        raise RuntimeError("No revolved volume")
    print(f"INFO: revolved volumes: {volume_tags}")

    groups: dict[str, list[int]] = {
        "symmetry_0": [],
        "symmetry_90": [],
        "ac_inlet": [],
        "outlet_tm": [],
        "lens_wall": [],
        "iris_wall": [],
        "wall": [],
    }

    # Landmark points (m) — right half only
    tm_se_a = np.array(PTS["tm_cornea_void"]) * M_PER_CM
    tm_se_b = np.array(PTS["tm_ciliary_void"]) * M_PER_CM
    tm_se = tm_se_b - tm_se_a
    tm_se_L = float(np.linalg.norm(tm_se))
    tm_se_u = tm_se / max(tm_se_L, 1e-16)

    iris_post = np.array(PTS["iris_ciliary_post"]) * M_PER_CM
    purple = np.array(PTS["hyaloid_curved_flat"]) * M_PER_CM
    inl_seg = purple - iris_post
    lens_c = np.array(
        [0.0, 0.5 * (SURFACES["lens_front"]["zc"] + SURFACES["lens_rear"]["zc"])]
    ) * M_PER_CM

    def on_tm_se_face(r: float, y: float) -> bool:
        p = np.array([r, y])
        t = float(np.dot(p - tm_se_a, tm_se_u))
        if t < -5e-5 or t > tm_se_L + 5e-5:
            return False
        closest = tm_se_a + np.clip(t, 0.0, tm_se_L) * tm_se_u
        return float(np.linalg.norm(p - closest)) < 8.0e-5

    def on_ac_inlet(r: float, y: float) -> bool:
        p = np.array([r, y])
        L = float(np.linalg.norm(inl_seg))
        u = inl_seg / max(L, 1e-16)
        t = float(np.dot(p - iris_post, u))
        if t < -1e-5 or t > L + 1e-5:
            return False
        closest = iris_post + np.clip(t, 0.0, L) * u
        return float(np.linalg.norm(p - closest)) < 2.5e-4

    boundaries = gmsh.model.getBoundary([(3, v) for v in volume_tags], oriented=False)
    plane_tol = 1.5e-4

    for dim, tag in boundaries:
        xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(dim, tag)
        cx = 0.5 * (xmin + xmax)
        cy = 0.5 * (ymin + ymax)
        cz = 0.5 * (zmin + zmax)
        dx, dy, dz = xmax - xmin, ymax - ymin, zmax - zmin
        # Cylindrical radius in xz
        r = math.hypot(cx, cz)

        # Symmetry planes
        if abs(zmin) < plane_tol and abs(zmax) < plane_tol and dx * dy > 1e-12:
            groups["symmetry_0"].append(tag)
            continue
        if abs(xmin) < plane_tol and abs(xmax) < plane_tol and dy * dz > 1e-12:
            groups["symmetry_90"].append(tag)
            continue

        # Skip tiny / degenerate
        if max(dx, dy, dz) < 1e-7:
            continue

        if on_tm_se_face(r, cy):
            groups["outlet_tm"].append(tag)
        elif on_ac_inlet(r, cy):
            groups["ac_inlet"].append(tag)
        elif r < 4.5e-3 and -0.0065 < cy < 0.0015 and abs(r) + abs(cy - lens_c[1]) < 6e-3:
            # lens surface of revolution
            groups["lens_wall"].append(tag)
        elif 2.5e-3 < r < 7.2e-3 and -0.0056 < cy < -0.0036:
            groups["iris_wall"].append(tag)
        else:
            groups["wall"].append(tag)

    # Fallbacks for mandatory patches
    laterals = [
        tag
        for dim, tag in boundaries
        if tag not in set(groups["symmetry_0"]) | set(groups["symmetry_90"])
    ]

    def ensure(name: str, pred):
        if groups[name]:
            return
        best, best_d = None, 1e99
        for tag in laterals:
            xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(2, tag)
            cx = 0.5 * (xmin + xmax)
            cy = 0.5 * (ymin + ymax)
            cz = 0.5 * (zmin + zmax)
            d = pred(math.hypot(cx, cz), cy)
            if d < best_d:
                best_d, best = d, tag
        if best is not None:
            groups["wall"] = [t for t in groups["wall"] if t != best]
            groups[name].append(best)
            print(f"INFO: fallback patch {name} <- surface {best}")

    tm_mid = 0.5 * (tm_se_a + tm_se_b)
    inl_mid = iris_post + 0.50 * inl_seg
    ensure("outlet_tm", lambda r, y: math.hypot(r - tm_mid[0], y - tm_mid[1]))
    ensure("ac_inlet", lambda r, y: math.hypot(r - inl_mid[0], y - inl_mid[1]))

    if not groups["symmetry_0"] or not groups["symmetry_90"]:
        print(
            f"WARNING: symmetry faces incomplete: "
            f"sym0={len(groups['symmetry_0'])} sym90={len(groups['symmetry_90'])} "
            f"(seed caps={seed_caps})"
        )

    gmsh.model.addPhysicalGroup(3, volume_tags, tag=1, name="fluid")
    pid = 2
    for name, tags in groups.items():
        if not tags:
            print(f"WARNING: empty patch group '{name}'")
            continue
        gmsh.model.addPhysicalGroup(2, tags, tag=pid, name=name)
        pid += 1

    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", lc_fine)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", lc_bulk)
    gmsh.model.mesh.generate(3)

    msh_path.parent.mkdir(parents=True, exist_ok=True)
    gmsh.write(str(msh_path))
    gmsh.write(str(msh_path.with_suffix(".vtk")))
    report = {k: len(v) for k, v in groups.items()}
    (msh_path.parent / "patch_groups_g2.json").write_text(json.dumps(report, indent=2))
    print(f"Wrote {msh_path}")
    print(f"Patch groups: {report}")
    gmsh.finalize()


def write_readme(path: Path) -> None:
    path.write_text(
        f"""# doc-g2-sim1 — G2 Simulação 1 (90° calotte)

Missel 2012 / Lamminsalo 2018 **3D quarter-eye** from the G1 right-half profile.

## What this is

- **G1** = 2D planar bilateral, empty slab.
- **G2** = G1 cut to the **right half**, revolved **{REVOLVE_DEG:.0f}°** about the
  optical axis → calotte with two **symmetry** faces (4× recovers 360°).

## Fluid domain

Same as G1 Sim 1: **AC + vitreous + TM** only (lens / iris holes).

## Generate geometry + mesh (host)

```bash
.venv-geom/bin/python brunaStuff/gen_lamminsalo_g2.py --case doc-g2-sim1 --mesh
# optional: --mesh-level M2|M3
```

Artefacts: `geometry/eye_g2_lamminsalo*.{{geo,msh,vtk}}`,
`figures/g2_half_meridional.png`, `figures/g2_calotte_3d.png`, `geometry_tables.md`.

## Patches

| Patch | Role |
|-------|------|
| `symmetry_0` | cut plane θ = 0° (`z = 0`) — `symmetryPlane` |
| `symmetry_90` | cut plane θ = 90° (`x = 0`) — `symmetryPlane` |
| `ac_inlet` | AC–CB production (single sector) |
| `outlet_tm` | TM SE outlet (single sector) |
| `lens_wall` / `iris_wall` / `wall` | no-slip walls |
"""
    )
    print(f"Wrote {path}")


def main():
    ap = argparse.ArgumentParser(description="G2 90° Lamminsalo calotte")
    ap.add_argument("--mesh", action="store_true", help="Build revolved 3D mesh with gmsh")
    ap.add_argument(
        "--mesh-level",
        default="M1",
        choices=sorted(MESH_LEVELS),
        help="Size field level (default M1)",
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
    half = build_half_fluid_rings(bi)

    out_geom.mkdir(parents=True, exist_ok=True)
    out_fig.mkdir(parents=True, exist_ok=True)
    (case / "fluid" / "system").mkdir(parents=True, exist_ok=True)

    # Export half rings
    export = {k: v.tolist() for k, v in half.items()}
    (out_geom / "half_rings_m.json").write_text(json.dumps(export))

    write_tables_md(case / "geometry_tables.md")
    write_readme(case / "README.md")
    write_toposet_g2(case / "fluid" / "system" / "topoSetDict.g2")
    write_geo_stub(half, out_geom / "eye_g2_lamminsalo.geo")

    plot_half_meridional(bi, half, out_fig / "g2_half_meridional.png")
    plot_calotte_3d(half, out_fig / "g2_calotte_3d.png")

    if args.mesh:
        msh = out_geom / f"eye_g2_lamminsalo_{args.mesh_level}.msh"
        mesh_with_gmsh(half, msh, mesh_level=args.mesh_level)
        shutil.copy2(msh, out_geom / "eye_g2_lamminsalo.msh")
        vtk = msh.with_suffix(".vtk")
        if vtk.exists():
            shutil.copy2(vtk, out_geom / "eye_g2_lamminsalo.vtk")

    print(f"Done. Case: {case}")


if __name__ == "__main__":
    main()
