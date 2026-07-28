#!/usr/bin/env python3
"""
G2 / G2-fluid anatomical rabbit-eye geometry (Missel 2012 / Lamminsalo 2018).

Naming (mirrors G1):
  G1        = full anatomical 2D planar bilateral
  G1-fluid  = AC ∪ vitreous ∪ TM only (Sim 1 CFD domain)

  G2        = G1 right-half, revolved 90° about optical axis (+y)
  G2-fluid  = G1-fluid right-half, revolved 90° about +y

Both are quarter-calottes with symmetry faces at θ=0° and θ=90°
(4 × 90° = 360° eye).

Usage:
  .venv-geom/bin/python brunaStuff/gen_lamminsalo_g2.py
  .venv-geom/bin/python brunaStuff/gen_lamminsalo_g2.py --mesh          # G2-fluid mesh
  .venv-geom/bin/python brunaStuff/gen_lamminsalo_g2.py --mesh-solid   # G2 solid tissues (90°)
  .venv-geom/bin/python brunaStuff/gen_lamminsalo_g2.py --case doc-g2-sim1 --mesh
"""


from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
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

try:
    from g2_coat_2d import mesh_g2_coat_2d
except ImportError:
    from brunaStuff.g2_coat_2d import mesh_g2_coat_2d

try:
    from g2_structured_mesh import (  # noqa: E402
        mesh_g2_fluid_structured,
        mesh_g2_fsi_conformal_pair,
        mesh_g2_solid_structured,
    )
except ImportError:
    from brunaStuff.g2_structured_mesh import (  # noqa: E402
        mesh_g2_fluid_structured,
        mesh_g2_fsi_conformal_pair,
        mesh_g2_solid_structured,
    )

try:
    from g2_needle import (  # noqa: E402
        TOPOSET_REFINE_DIST_M,
        ACP_TIP_ORIGIN_M,
        IVI_TIP_ORIGIN_M,
        NEEDLE_R_LUMEN_M,
        TIP_BOX_HALF_M,
        TIP_CELLS_ACROSS,
        TIP_CELLS_ACROSS_IVI,
        TIP_ORIGINS_M,
        TIP_REFINE_DIST_M,
        TOPOSET_TIP_RADIUS_M,
        _inject_axis_stations,
        lc_tip_for_level,
        lc_tip_target,
        lc_toposet_for_level,
        lumen_anchor_points,
        lumen_embed_points,
        lumen_sizing_points,
        sync_case_topo_sets,
        tip_origins_for,
    )
except ImportError:
    from brunaStuff.g2_needle import (  # noqa: E402
        TOPOSET_REFINE_DIST_M,
        ACP_TIP_ORIGIN_M,
        IVI_TIP_ORIGIN_M,
        NEEDLE_R_LUMEN_M,
        TIP_BOX_HALF_M,
        TIP_CELLS_ACROSS,
        TIP_CELLS_ACROSS_IVI,
        TIP_ORIGINS_M,
        TIP_REFINE_DIST_M,
        TOPOSET_TIP_RADIUS_M,
        _inject_axis_stations,
        lc_tip_for_level,
        lc_tip_target,
        lc_toposet_for_level,
        lumen_anchor_points,
        lumen_embed_points,
        lumen_sizing_points,
        sync_case_topo_sets,
        tip_origins_for,
    )

DEFAULT_CASE = "doc-g2-sim1"
REVOLVE_DEG = 90.0
REVOLVE_RAD = math.radians(REVOLVE_DEG)


def case_paths(case_name: str = DEFAULT_CASE):
    case = REPO / "cases" / case_name
    return case, case / "geometry", case / "figures"


# ---------------------------------------------------------------------------
# Right-half rings (meridional plane z = 0, x ≥ 0)
# ---------------------------------------------------------------------------
def build_half_ac_m(bi: dict[str, np.ndarray]) -> np.ndarray:
    """Closed right-half AC ∪ TM (cornea → TM → ciliary outer margin → hyaloid → lens → axis).

    Follows the outer ciliary/TM margin only — no indent along the free iris edge.
    The iris cavity is punched separately (precise Table-SII loop + OCC cut).
    """
    cor_r = bi["cornea_inside_right"]
    tm_r = bi["tm_markers_right"][:-1]
    iris_r = bi["iris_right"]
    hy_r = bi["hyaloid_right"]
    lens_r = bi["lens_right"]
    ie = int(np.argmax(np.abs(lens_r[:, 0])))
    lens_eq_to_apex = lens_r[: ie + 1][::-1]
    iris_run = iris_r[:6]
    purple = hy_r[1]
    eq = hy_r[0]
    cil_ant = iris_run[0]
    # Outer iris root → hyaloid (skip Table-SII indent x≈3 mm — causes spurious fluid void)
    iris_outer = iris_run[5]

    path = np.vstack(
        [
            cor_r,
            tm_r[1:],
            cil_ant.reshape(1, 2),
            iris_outer.reshape(1, 2),
            purple.reshape(1, 2),
            eq.reshape(1, 2),
            lens_eq_to_apex[1:],
        ]
    )
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
    lens_rear = lens_r[ie:].copy()
    lens_rear[-1, 0] = 0.0
    rear_apex = lens_rear[-1].copy()
    rear_apex[0] = 0.0

    path = np.vstack(
        [
            hy_r,
            vit_r[1:],
            rear_apex.reshape(1, 2),
            lens_rear[-2::-1],
        ]
    )
    # Snap closure onto hyaloid anchor (avoid ~1 µm sliver at ora junction).
    if len(path) > 2 and np.linalg.norm(path[-1] - path[0]) < 2.0e-6:
        path[-1] = path[0]
    if np.linalg.norm(path[-1] - path[0]) > 1e-12:
        path = np.vstack([path, path[0:1]])
    return _clean_ring(path)


def build_half_lens_m(bi: dict[str, np.ndarray]) -> np.ndarray:
    """Closed right-half lens (front apex → eq → rear apex → axis back)."""
    lens_r = bi["lens_right"].copy()
    lens_r[0, 0] = 0.0
    lens_r[-1, 0] = 0.0
    # Close on optical axis: rear apex → front apex
    if np.linalg.norm(lens_r[-1] - lens_r[0]) > 1e-12:
        lens_r = np.vstack([lens_r, lens_r[0:1]])
    return _clean_ring(lens_r)


def _ensure_closed_half(pts: np.ndarray) -> np.ndarray:
    p = np.asarray(pts, dtype=float).copy()
    if len(p) < 3:
        return p
    # Snap any near-axis endpoints
    if abs(p[0, 0]) < 1e-9:
        p[0, 0] = 0.0
    if abs(p[-1, 0]) < 1e-9:
        p[-1, 0] = 0.0
    return _clean_ring(p)


def build_g2_anatomy_half(bi: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """
    G2 = full G1 anatomy, right half only.

    Tissue shells + solids + fluid chambers (same regions as g1_anatomy_2d).
    """
    half: dict[str, np.ndarray] = {}

    # Tissue shells (already closed half-bands in outlines)
    for key in (
        "band_sclera_right",
        "band_choroid_right",
        "band_retina_right",
        "band_cornea_right",
        "band_ciliary_right",
    ):
        src = key.replace("_right", "")
        # Prefer continuous right band from bi
        if key in bi:
            half[src] = _ensure_closed_half(bi[key])
        elif f"{src}_right" in bi:
            half[src] = _ensure_closed_half(bi[f"{src}_right"])

    half["lens"] = build_half_lens_m(bi)
    half["iris"] = _clean_ring(_iris_loop_m(bi["iris_right"]))

    # Fluid chambers (also part of full anatomy view)
    half["ac"] = build_half_ac_m(bi)
    half["vitreous"] = build_half_vitreous_m(bi)

    # Context outlines (open curves for plotting)
    for k in (
        "outer_wall_right",
        "cornea_outside_right",
        "cornea_inside_right",
        "vitreous_retina_right",
        "hyaloid_right",
        "tm_markers_right",
        "sclera_tm_wrap_right",
    ):
        if k in bi:
            half[k] = bi[k]

    return half


def build_g2_fluid_half(bi: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """
    G2-fluid = G1-fluid right half only (AC ∪ vitreous ∪ TM − lens − iris).
    """
    return {
        "band_ac_half": build_half_ac_m(bi),
        "band_vitreous_half": build_half_vitreous_m(bi),
        "iris_half": _clean_ring(_iris_loop_m(bi["iris_right"])),
        "lens_half": build_half_lens_m(bi),
        # context
        "cornea_inside_right": bi["cornea_inside_right"],
        "vitreous_retina_right": bi["vitreous_retina_right"],
        "hyaloid_right": bi["hyaloid_right"],
        "tm_markers_right": bi["tm_markers_right"],
        "lens_right": bi["lens_right"],
    }


# ---------------------------------------------------------------------------
# Revolve helper (plotting)
# ---------------------------------------------------------------------------
def _revolve_polyline(pts_xy: np.ndarray, n_theta: int = 24) -> tuple[np.ndarray, list]:
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
            c_ = (j + 1) * n + i2
            d = (j + 1) * n + i
            faces.append([a, b, c_, d])
    return verts, faces


def _add_revolved(
    ax, pts, *, color, alpha, label, n_theta=24, edge_alpha=0.06
):
    verts, faces = _revolve_polyline(pts, n_theta=n_theta)
    vmm = verts * 1.0e3
    polys = [[vmm[i] for i in f] for f in faces]
    coll = Poly3DCollection(
        polys,
        alpha=alpha,
        facecolor=color,
        edgecolor=(0.1, 0.1, 0.1, edge_alpha),
        linewidths=0.12,
        label=label,
    )
    ax.add_collection3d(coll)


def _style_3d_axes(ax, title: str):
    ax.plot([0, 0], [-8.5, 8.0], [0, 0], color="#c0392b", lw=1.5, label="Optical axis +y")
    ax.set_xlabel("x [mm]")
    ax.set_ylabel("y [mm] (optical)")
    ax.set_zlabel("z [mm]")
    ax.set_title(title)
    ax.legend(loc="upper left", fontsize=7)
    ax.set_box_aspect((1, 1.15, 1))
    ax.view_init(elev=22, azim=-48)
    ax.set_xlim(0, 10)
    ax.set_ylim(-9, 8)
    ax.set_zlim(0, 10)


# ---------------------------------------------------------------------------
# Figures — G2 (full anatomy)
# ---------------------------------------------------------------------------
def plot_g2_anatomy_half(anatomy: dict[str, np.ndarray], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.2, 8.2))
    mm = 1.0e3

    def fill(key, color, label, alpha=0.75):
        if key not in anatomy:
            return
        p = anatomy[key] * mm
        ax.fill(p[:, 0], p[:, 1], color=color, alpha=alpha, label=label, linewidth=0, zorder=1)

    def stroke(key, **kw):
        if key not in anatomy:
            return
        p = anatomy[key] * mm
        ax.plot(p[:, 0], p[:, 1], **kw)

    # Same colours as G1 anatomy
    fill("band_sclera", "#4a6fa5", "Sclera")
    fill("band_choroid", "#c1666b", "Choroid")
    fill("band_retina", "#e4c15f", "Retina")
    fill("band_cornea", "#e8a87c", "Cornea")
    fill("band_ciliary", "#9b59b6", "Ciliary", alpha=0.65)
    fill("vitreous", "#5dade2", "Vitreous", alpha=0.45)
    fill("ac", "#a8dadc", "AC", alpha=0.55)
    fill("lens", "#2d6a4f", "Lens", alpha=0.75)
    fill("iris", "#c0392b", "Iris", alpha=0.80)

    stroke("outer_wall_right", color="#1d3557", lw=0.9, label="Outer wall", zorder=3)
    stroke("tm_markers_right", color="#f4a261", lw=1.4, marker="o", ms=3, label="TM", zorder=4)
    stroke("hyaloid_right", color="#8e44ad", lw=1.0, label="Hyaloid", zorder=3)

    ax.axvline(0.0, color="0.35", ls="--", lw=0.9, label="Optical axis (revolve)")
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x [mm]  (radial, half-domain x ≥ 0)")
    ax.set_ylabel("y [mm]  (optical axis, + posterior)")
    ax.set_title(
        "G2 anatomy — meridional half (from G1)\n"
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


def plot_g2_anatomy_3d(anatomy: dict[str, np.ndarray], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(9.0, 7.2))
    ax = fig.add_subplot(111, projection="3d")

    # Outer → inner (matching G1 anatomy colours)
    layers = (
        ("band_sclera", "#4a6fa5", 0.55, "Sclera"),
        ("band_choroid", "#c1666b", 0.55, "Choroid"),
        ("band_retina", "#e4c15f", 0.50, "Retina"),
        ("band_cornea", "#e8a87c", 0.55, "Cornea"),
        ("vitreous", "#5dade2", 0.30, "Vitreous"),
        ("ac", "#a8dadc", 0.40, "AC"),
        ("lens", "#2d6a4f", 0.65, "Lens"),
        ("iris", "#c0392b", 0.70, "Iris"),
        ("band_ciliary", "#9b59b6", 0.55, "Ciliary"),
    )
    for key, color, alpha, label in layers:
        if key in anatomy and len(anatomy[key]) >= 3:
            _add_revolved(ax, anatomy[key], color=color, alpha=alpha, label=label, n_theta=22)

    # Symmetry outlines on outer wall / sclera
    for key, c0, c90 in (
        ("band_sclera", "#1a5276", "#7d3c98"),
        ("band_cornea", "#1a5276", "#7d3c98"),
    ):
        if key not in anatomy:
            continue
        p = anatomy[key] * 1e3
        ax.plot(p[:, 0], p[:, 1], np.zeros_like(p[:, 0]), color=c0, lw=1.0)
        ax.plot(np.zeros_like(p[:, 0]), p[:, 1], p[:, 0], color=c90, lw=1.0, ls="--")

    ax.plot([], [], [], color="#1a5276", lw=1.0, label="symmetry_0 (θ=0°)")
    ax.plot([], [], [], color="#7d3c98", lw=1.0, ls="--", label="symmetry_90 (θ=90°)")
    _style_3d_axes(ax, "G2 anatomy — 90° calotte (from G1) · 4× → 360°")
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {path}")


# ---------------------------------------------------------------------------
# Figures — G2-fluid
# ---------------------------------------------------------------------------
def plot_g2_fluid_half(fluid: dict[str, np.ndarray], path: Path) -> None:
    """G2-fluid = AC ∪ vitreous ∪ TM only. Lens / iris are walls (not meshed)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.2, 8.0))
    mm = 1.0e3

    def fill(pts, color, label, alpha=0.40):
        p = np.asarray(pts) * mm
        ax.fill(p[:, 0], p[:, 1], color=color, alpha=alpha, label=label, linewidth=0)

    def stroke(pts, **kw):
        p = np.asarray(pts) * mm
        ax.plot(p[:, 0], p[:, 1], **kw)

    # Fluid domains only (same as G1-fluid)
    fill(fluid["band_vitreous_half"], "#5dade2", "Vitreous", alpha=0.55)
    fill(fluid["band_ac_half"], "#a8dadc", "AC ∪ TM", alpha=0.65)
    tmm = fluid["tm_markers_right"] * mm
    ax.fill(tmm[:, 0], tmm[:, 1], color="#f4a261", alpha=0.75, label="TM", linewidth=0, zorder=2)

    # Walls only — outline, not filled tissue
    stroke(fluid["lens_half"], color="#1e8449", lw=1.4, label="Lens (wall)")
    stroke(fluid["iris_half"], color="#9b2226", lw=1.2, label="Iris (wall)")
    stroke(fluid["cornea_inside_right"], color="#1d3557", lw=0.9, label="Outer outline")
    stroke(fluid["vitreous_retina_right"], color="#1d3557", lw=0.9)
    stroke(fluid["hyaloid_right"], color="#2874a6", lw=1.0, label="Hyaloid")

    ax.axvline(0.0, color="0.35", ls="--", lw=0.9, label="Optical axis (revolve)")
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x [mm]  (radial, half-domain x ≥ 0)")
    ax.set_ylabel("y [mm]  (optical axis, + posterior)")
    ax.set_title(
        "G2-fluid — meridional half (from G1-fluid)\n"
        f"AC / vitreous / TM only  (walls: lens, iris)  ·  revolve {REVOLVE_DEG:.0f}°"
    )
    ax.legend(loc="upper right", fontsize=7, framealpha=0.92)
    ax.grid(True, alpha=0.25)
    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-9.5, 9.0)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {path}")


def plot_g2_fluid_3d(fluid: dict[str, np.ndarray], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(8.5, 7.0))
    ax = fig.add_subplot(111, projection="3d")

    _add_revolved(
        ax, fluid["band_vitreous_half"], color="#2874a6", alpha=0.45, label="Vitreous", n_theta=28
    )
    _add_revolved(
        ax, fluid["band_ac_half"], color="#48a9a6", alpha=0.50, label="AC ∪ TM", n_theta=28
    )

    for key, c0, c90 in (
        ("band_ac_half", "#1a5276", "#7d3c98"),
        ("band_vitreous_half", "#1a5276", "#7d3c98"),
    ):
        p = fluid[key] * 1e3
        ax.plot(p[:, 0], p[:, 1], np.zeros_like(p[:, 0]), color=c0, lw=1.0)
        ax.plot(np.zeros_like(p[:, 0]), p[:, 1], p[:, 0], color=c90, lw=1.0, ls="--")

    ax.plot([], [], [], color="#1a5276", lw=1.0, label="symmetry_0 (θ=0°)")
    ax.plot([], [], [], color="#7d3c98", lw=1.0, ls="--", label="symmetry_90 (θ=90°)")
    _style_3d_axes(ax, "G2-fluid — 90° calotte (from G1-fluid) · 4× → 360°")
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {path}")


# ---------------------------------------------------------------------------
# Docs
# ---------------------------------------------------------------------------
def write_tables_md(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""# G2 / G2-fluid geometry (Missel / Lamminsalo ESM)

Same SI–SII tables as G1. Units in tables: **cm**. OpenFOAM uses **metres**.

## Nomenclature

| Name | Source | Domain |
|------|--------|--------|
| **G1** | Missel/Lamminsalo | full anatomy, 2D planar bilateral |
| **G1-fluid** | subset of G1 | AC + vitreous + TM only |
| **G2** | G1 right-half × revolve {REVOLVE_DEG:.0f}° | full anatomy calotte |
| **G2-fluid** | G1-fluid right-half × revolve {REVOLVE_DEG:.0f}° | CFD fluid calotte |

Two planar cut faces = **symmetry** patches; **4 × 90° = 360°** of the eye.

## Construction

1. Take the **right half** (`x ≥ 0`) of the corresponding G1 silhouette.
2. `OCC revolve` about optical axis `(0,1,0)` by `{REVOLVE_DEG:.0f}°`.
3. Patches: `symmetry_0` (θ=0°, `z=0`), `symmetry_90` (θ=90°, `x=0`), plus walls/inlets.

## Coordinate map

| Missel | OpenFOAM G2 |
|--------|-------------|
| X (radial) | `x = X·10⁻²` (half-plane, then revolved) |
| Z (optical) | `y = Z·10⁻²` (**revolve axis**) |
| — | `z` from revolution |

## Generated artefacts

### G2 (anatomy)
- `figures/g2_anatomy_half.png`
- `figures/g2_anatomy_3d.png`
- `geometry/eye_g2_lamminsalo.geo`

### G2-fluid (CFD)
- `figures/g2_fluid_half.png`
- `figures/g2_fluid_3d.png`
- `geometry/eye_g2_fluid_lamminsalo.{{geo,msh,vtk}}` (with `--mesh`)
"""
    )
    print(f"Wrote {path}")


def write_readme(path: Path) -> None:
    path.write_text(
        f"""# doc-g2-sim1 — G2 / G2-fluid (90° calotte)

Missel 2012 / Lamminsalo 2018 **3D quarter-eye**.

## Naming (same split as G1)

| Name | Based on | Content |
|------|----------|---------|
| **G2** | **G1** | full anatomy (sclera, choroid, retina, cornea, lens, iris, ciliary, AC, vitreous, TM) |
| **G2-fluid** | **G1-fluid** | AC + vitreous + TM only (Sim 1 CFD domain) |

Both: right-half meridional profile revolved **{REVOLVE_DEG:.0f}°** about the optical
axis → calotte with two **symmetry** faces (4× recovers 360°).

## Generate (host)

```bash
# figures + geo for G2 and G2-fluid
.venv-geom/bin/python brunaStuff/gen_lamminsalo_g2.py --case doc-g2-sim1

# + G2-fluid volume mesh (CFD)
.venv-geom/bin/python brunaStuff/gen_lamminsalo_g2.py --case doc-g2-sim1 --mesh
```

## Artefacts

- `figures/g2_anatomy_{{half,3d}}.png` — **G2** from G1
- `figures/g2_fluid_{{half,3d}}.png` — **G2-fluid** from G1-fluid
- `geometry/eye_g2_lamminsalo.geo` — anatomy stub
- `geometry/eye_g2_fluid_lamminsalo.msh` — fluid mesh (`--mesh`)

## Patches (G2-fluid)

| Patch | Role |
|-------|------|
| `symmetry_0` | θ = 0° (`z = 0`) — `symmetryPlane` |
| `symmetry_90` | θ = 90° (`x = 0`) — `symmetryPlane` |
| `ac_inlet` | AC–CB production (1/4 eye) |
| `outlet_tm` | TM SE outlet (1/4 eye) |
| `lens_wall` / `iris_wall` / `wall` | no-slip |
"""
    )
    print(f"Wrote {path}")


def write_geo_stub_anatomy(anatomy: dict[str, np.ndarray], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "// G2 Missel/Lamminsalo — full anatomy 90° calotte (from G1)",
        "// Generated by brunaStuff/gen_lamminsalo_g2.py",
        "SetFactory(\"OpenCASCADE\");",
        f"angle = {REVOLVE_RAD:.10f};  // {REVOLVE_DEG:.0f} deg",
        "lc = 4.0e-4;",
        "",
        "// Closed right-half rings (z=0). Revolve about +y via --mesh-anatomy.",
        "",
    ]
    pid = 1
    for name in (
        "band_sclera",
        "band_choroid",
        "band_retina",
        "band_cornea",
        "band_ciliary",
        "lens",
        "iris",
        "ac",
        "vitreous",
    ):
        if name not in anatomy:
            continue
        pts = anatomy[name]
        core = pts[:-1] if np.linalg.norm(pts[0] - pts[-1]) < 1e-14 else pts
        ids = []
        for x, y in core:
            lines.append(f"Point({pid}) = {{{x:.8e}, {y:.8e}, 0, lc}};")
            ids.append(pid)
            pid += 1
        if len(ids) >= 2:
            lines.append(f"Spline({pid}) = {{{', '.join(map(str, ids + [ids[0]]))}}};")
            lines.append(f"// {name} curve {pid}")
            pid += 1
            lines.append("")
    path.write_text("\n".join(lines) + "\n")
    print(f"Wrote {path}")


def write_geo_stub_fluid(fluid: dict[str, np.ndarray], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "// G2-fluid Missel/Lamminsalo — AC/vitreous/TM 90° calotte (from G1-fluid)",
        "// Generated by brunaStuff/gen_lamminsalo_g2.py",
        "SetFactory(\"OpenCASCADE\");",
        f"angle = {REVOLVE_RAD:.10f};",
        "lc = 4.0e-4;",
        "",
        "// Boolean fluid + revolve via gmsh Python API (--mesh).",
        "",
    ]
    pid = 1
    for name in ("band_ac_half", "band_vitreous_half", "iris_half", "lens_half"):
        pts = fluid[name]
        core = pts[:-1] if np.linalg.norm(pts[0] - pts[-1]) < 1e-14 else pts
        ids = []
        for x, y in core:
            lines.append(f"Point({pid}) = {{{x:.8e}, {y:.8e}, 0, lc}};")
            ids.append(pid)
            pid += 1
        lines.append(f"Spline({pid}) = {{{', '.join(map(str, ids + [ids[0]]))}}};")
        lines.append(f"// {name} curve {pid}")
        pid += 1
        lines.append("")
    path.write_text("\n".join(lines) + "\n")
    print(f"Wrote {path}")


def write_toposet_g2_fluid(path: Path, *, tm_markers: np.ndarray | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if tm_markers is not None and len(tm_markers) >= 3:
        p1, p2, outer_r, inner_r = _tm_toposet_cylinder_params(tm_markers)
        cyl = (
            f"p1      ({p1[0]:.5f} {p1[1]:.5f} {p1[2]:.5f});\n"
            f"        p2      ({p2[0]:.5f} {p2[1]:.5f} {p2[2]:.5f});\n"
            f"        outerRadius {outer_r:.5f};\n"
            f"        innerRadius {inner_r:.5f};"
        )
    else:
        cyl = (
            "p1      (0 -0.00500 0);\n"
            "        p2      (0 -0.00424 0);\n"
            "        outerRadius 0.00720;\n"
            "        innerRadius 0.00640;"
        )
    path.write_text(
        f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      topoSetDict;
}}

// G2-fluid 90° calotte cellZones.
// TM is a revolved annulus about +y — use cylinderAnnulusToCell (not a box).

actions
(
    {{
        name    tm_zone;
        type    cellSet;
        action  new;
        source  cylinderAnnulusToCell;
        {cyl}
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
        box     (-1.0e-4 -1.5e-3 -9.0e-3) (9.0e-3 7.5e-3 1.0e-4);
    }}
    {{
        name    vitreous_zone;
        type    cellSet;
        action  delete;
        source  cellToCell;
        set     tm_zone;
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
    )
    print(f"Wrote {path}")


# ---------------------------------------------------------------------------
# Gmsh — G2-fluid mesh
# ---------------------------------------------------------------------------
IRIS_REFINE_LC_FRAC = 0.62
IRIS_INFERIOR_LC_FRAC = 0.55
IRIS_INFERIOR_TIP_LC_FRAC = 0.42
IRIS_REFINE_DIST_M = {
    "M5": 0.42e-3,
    "M4": 0.38e-3,
    "M1": 0.34e-3,
    "M2": 0.26e-3,
    "M3": 0.20e-3,
}
IRIS_INFERIOR_Y_M = -4.65e-3
IRIS_INFERIOR_TIP_Y_M = -5.15e-3
IRIS_INFERIOR_TIP_X_M = 4.0e-3
IRIS_INFERIOR_X_M = 5.5e-3
IRIS_INFERIOR_TIP_DIST_M = 0.14e-3
IRIS_REFINE_TM_MARGIN_M = 0.06e-3
VITREOUS_SYM0_LAYERS = 6
VITREOUS_SYM0_LC_INNER_FRAC = 0.46
VITREOUS_SYM0_LC_MID_FRAC = 0.68
VITREOUS_SYM0_IVI_LC_FRAC = 0.32
VITREOUS_SYM0_IVI_Y_HALF_M = 1.4e-3
VITREOUS_SYM0_IVI_Y_GAP_M = 0.32e-3
VITREOUS_SYM0_IVI_AXIS_Y_HALF_M = 1.8e-3
VITREOUS_SYM0_IVI_AXIS_LC_FACTOR = 1.25
TM_ANNULUS_RADIAL_M = 0.8e-3  # matches topoSet inner/outer Δr (6.4–7.2 mm)
TM_SEED_BAND_M = 0.38e-3


def _lc_vitreous_sym0_for_level(mesh_level: str) -> dict[str, float]:
    """Structured symmetry_0 wall bands: inner layers + IVI-local finest tier."""
    lc_topo = lc_toposet_for_level(mesh_level)
    lc_inner = max(lc_topo * VITREOUS_SYM0_LC_INNER_FRAC, 7.5e-5)
    lc_mid = max(lc_topo * VITREOUS_SYM0_LC_MID_FRAC, lc_inner * 1.12)
    lc_ivi = max(lc_topo * VITREOUS_SYM0_IVI_LC_FRAC, 6.5e-5)
    dist_inner = VITREOUS_SYM0_LAYERS * lc_inner * 1.08
    return {
        "lc_topo": lc_topo,
        "lc_inner": lc_inner,
        "lc_mid": lc_mid,
        "lc_ivi": lc_ivi,
        "dist_inner": dist_inner,
        "dist_mid": TOPOSET_REFINE_DIST_M,
    }


def _polyline_y_window(
    poly_xy: np.ndarray,
    y0: float,
    y1: float,
) -> np.ndarray | None:
    """Contiguous sub-chain with one anchor point on each side of [y0, y1]."""
    pts = np.asarray(poly_xy, dtype=float)
    if len(pts) < 2:
        return None
    idx = [i for i, p in enumerate(pts) if y0 <= float(p[1]) <= y1]
    if len(idx) < 2:
        return None
    i0 = max(0, idx[0] - 1)
    i1 = min(len(pts) - 1, idx[-1] + 1)
    seg = pts[i0 : i1 + 1]
    return seg if len(seg) >= 2 else None


def _gmsh_vitreous_sym0_layer_fields(
    poly_xy: np.ndarray,
    *,
    lc_inner: float,
    lc_mid: float,
    lc_bulk: float,
    dist_inner: float,
    dist_mid: float,
    n_per_seg: int = 8,
    lc_wall: float | None = None,
    dist_wall: float | None = None,
) -> list[int]:
    """Edge bands normal to symmetry_0 vitreous wall (2–3 tiers)."""
    seg = np.asarray(poly_xy, dtype=float)
    if len(seg) < 2:
        return []
    fields: list[int] = []
    if lc_wall is not None and dist_wall is not None and lc_wall < lc_inner - 1.0e-8:
        fields.append(
            _gmsh_polyline_edge_distance_field(
                seg,
                lc_min=lc_wall,
                lc_bulk=lc_inner,
                dist_max=dist_wall,
                n_per_seg=max(10, n_per_seg),
            )
        )
    fields.extend(
        [
            _gmsh_polyline_edge_distance_field(
                seg,
                lc_min=lc_inner,
                lc_bulk=lc_mid,
                dist_max=dist_inner,
                n_per_seg=n_per_seg,
            ),
            _gmsh_polyline_edge_distance_field(
                seg,
                lc_min=lc_mid,
                lc_bulk=lc_bulk,
                dist_max=dist_mid,
                n_per_seg=max(4, n_per_seg // 2),
            ),
        ]
    )
    return fields


def _gmsh_vitreous_sym0_refinement_fields(
    wall_poly: np.ndarray,
    *,
    lc_inner: float,
    lc_mid: float,
    lc_ivi: float,
    lc_bulk: float,
    dist_inner: float,
    dist_mid: float,
) -> list[int]:
    """symmetry_0 vitreous wall: structured layers everywhere incl. IVI band."""
    wall = np.asarray(wall_poly, dtype=float)
    fields: list[int] = []
    y_ivi = float(IVI_TIP_ORIGIN_M[1])
    ivi_seg = _polyline_y_window(
        wall,
        y_ivi - VITREOUS_SYM0_IVI_Y_HALF_M,
        y_ivi + VITREOUS_SYM0_IVI_Y_HALF_M,
    )
    if ivi_seg is not None:
        dist_ivi = VITREOUS_SYM0_LAYERS * lc_ivi * 1.05
        dist_wall = 3.0 * lc_ivi * 1.05
        fields.extend(
            _gmsh_vitreous_sym0_layer_fields(
                ivi_seg,
                lc_inner=lc_inner,
                lc_mid=lc_mid,
                lc_bulk=lc_bulk,
                dist_inner=dist_ivi,
                dist_mid=dist_mid,
                n_per_seg=12,
                lc_wall=lc_ivi,
                dist_wall=dist_wall,
            )
        )
    y_gap = VITREOUS_SYM0_IVI_Y_GAP_M
    wall_segs = _split_polyline_by_y_exclusion(
        wall,
        y_center=y_ivi,
        y_half=y_gap,
    )
    for seg in wall_segs:
        fields.extend(
            _gmsh_vitreous_sym0_layer_fields(
                seg,
                lc_inner=lc_inner,
                lc_mid=lc_mid,
                lc_bulk=lc_bulk,
                dist_inner=dist_inner,
                dist_mid=dist_mid,
                n_per_seg=8,
            )
        )
    print(
        f"INFO: vitreous symmetry_0 layers>={VITREOUS_SYM0_LAYERS} "
        f"lc_inner={lc_inner:.2e} lc_ivi={lc_ivi:.2e} lc_mid={lc_mid:.2e} "
        f"dist_inner={dist_inner:.2e} dist_mid={dist_mid:.2e} "
        f"ivi_seg={'yes' if ivi_seg is not None else 'no'} "
        f"({len(wall_segs)} outer segments, IVI y-gap ±{y_gap*1e3:.2f} mm)"
    )
    return fields


def _lc_tm_for_level(mesh_level: str, tm_layers: int) -> float:
    """Target TM edge length — catalog lc_tm capped by radial depth / layers."""
    lc_cat = float(MESH_LEVELS[mesh_level]["lc_tm"])
    lc_geom = TM_ANNULUS_RADIAL_M / (tm_layers + 0.5)
    return min(lc_cat, lc_geom)


def _tm_se_segment_polyline(lm: dict[str, np.ndarray | float]) -> np.ndarray:
    a = np.asarray(lm["tm_se_a"], dtype=float)
    b = np.asarray(lm["tm_se_b"], dtype=float)
    return np.vstack([a, b])


def _ring_lc_tm_band(
    pts_m: np.ndarray,
    tm_markers: np.ndarray,
    *,
    lc_default: float,
    lc_tm: float,
    band_m: float = TM_SEED_BAND_M,
) -> np.ndarray:
    """Finer seed-ring sizing on AC outer wall near TM markers."""
    pts = np.asarray(pts_m, dtype=float)
    tm = _clean_ring(np.asarray(tm_markers, dtype=float), tol=1e-9)[:-1]
    lc = np.full(len(pts), lc_default, dtype=float)
    for i, (x, y) in enumerate(pts):
        ax = abs(float(x))
        d = _dist_to_polyline_xy(np.array([ax, y], dtype=float), tm)
        if d <= band_m:
            lc[i] = min(lc[i], lc_tm)
    return lc


def _gmsh_tm_refinement_fields(
    tm_markers: np.ndarray,
    tm_se_poly: np.ndarray,
    *,
    lc_tm: float,
    lc_bulk: float,
    tm_layers: int,
    radial_depth: float = TM_ANNULUS_RADIAL_M,
) -> list[int]:
    """TM annulus band + outlet_tm SE strip (Distance ramps, geometry unchanged)."""
    import gmsh

    fields: list[int] = []
    tm_loop = _clean_ring(np.asarray(tm_markers, dtype=float), tol=1e-9)[:-1]
    tm_pts = densify_polyline(tm_loop, n_per_seg=4)
    pt_tags = [
        gmsh.model.occ.addPoint(float(x), float(y), 0.0, lc_tm) for x, y in tm_pts
    ]
    gmsh.model.occ.synchronize()
    f_dist = gmsh.model.mesh.field.add("Distance")
    gmsh.model.mesh.field.setNumbers(f_dist, "PointsList", pt_tags)
    f_band = gmsh.model.mesh.field.add("Threshold")
    gmsh.model.mesh.field.setNumber(f_band, "InField", f_dist)
    gmsh.model.mesh.field.setNumber(f_band, "SizeMin", lc_tm)
    gmsh.model.mesh.field.setNumber(f_band, "SizeMax", lc_bulk)
    gmsh.model.mesh.field.setNumber(f_band, "Sigmoid", 0)
    dist_band = radial_depth * 0.92
    gmsh.model.mesh.field.setNumber(f_band, "DistMin", 0.0)
    gmsh.model.mesh.field.setNumber(f_band, "DistMax", dist_band)
    fields.append(f_band)

    lc_wall = lc_tm * 0.88
    se_pts = densify_polyline(np.asarray(tm_se_poly, dtype=float), n_per_seg=4)
    se_tags = [
        gmsh.model.occ.addPoint(float(x), float(y), 0.0, lc_wall) for x, y in se_pts
    ]
    gmsh.model.occ.synchronize()
    f_se = gmsh.model.mesh.field.add("Distance")
    gmsh.model.mesh.field.setNumbers(f_se, "PointsList", se_tags)
    f_wall = gmsh.model.mesh.field.add("Threshold")
    gmsh.model.mesh.field.setNumber(f_wall, "InField", f_se)
    gmsh.model.mesh.field.setNumber(f_wall, "SizeMin", lc_wall)
    gmsh.model.mesh.field.setNumber(f_wall, "SizeMax", lc_bulk)
    gmsh.model.mesh.field.setNumber(f_wall, "Sigmoid", 0)
    dist_wall = max(tm_layers * lc_tm * 1.12, lc_tm * 2.5)
    gmsh.model.mesh.field.setNumber(f_wall, "DistMin", 0.0)
    gmsh.model.mesh.field.setNumber(f_wall, "DistMax", dist_wall)
    fields.append(f_wall)

    print(
        f"INFO: TM refinement lc_tm={lc_tm:.2e} lc_wall={lc_wall:.2e} "
        f"band_r={dist_band:.2e} wall_r={dist_wall:.2e} layers>={tm_layers}"
    )
    return fields


def _tm_toposet_cylinder_params(
    tm_markers: np.ndarray,
) -> tuple[tuple[float, float, float], tuple[float, float, float], float, float]:
    """Cylinder annulus for tm_zone topoSet aligned with Lamminsalo TM band."""
    tm = np.asarray(tm_markers, dtype=float)
    rs = np.abs(tm[:, 0])
    y0 = float(tm[:, 1].min()) - 0.08e-3
    y1 = float(tm[:, 1].max()) + 0.08e-3
    inner_r = max(float(rs.min()) - 0.18e-3, 5.8e-3)
    outer_r = min(float(rs.max()) + 0.32e-3, 7.4e-3)
    return (0.0, y0, 0.0), (0.0, y1, 0.0), outer_r, inner_r


def _lc_iris_for_level(mesh_level: str, lc_fine: float) -> float:
    return max(lc_fine * IRIS_REFINE_LC_FRAC, 1.15e-4)


def _iris_refine_dist_max_m(
    iris_poly: np.ndarray,
    tm_markers: np.ndarray | None,
    *,
    mesh_level: str,
) -> float:
    """Ramp length for iris sizing — capped so TM markers stay outside the fine band."""
    return _iris_refine_dist_max_segment(
        iris_poly, tm_markers, mesh_level=mesh_level
    )


def _iris_refine_dist_max_segment(
    iris_seg: np.ndarray,
    tm_markers: np.ndarray | None,
    *,
    mesh_level: str,
) -> float:
    cap = IRIS_REFINE_DIST_M.get(mesh_level, 0.34e-3)
    if tm_markers is None:
        return cap
    seg = np.asarray(iris_seg, dtype=float)
    d_tm = min(
        _dist_to_polyline_xy(np.asarray(p, dtype=float), seg)
        for p in np.asarray(tm_markers, dtype=float)
    )
    return min(cap, max(0.14e-3, d_tm - IRIS_REFINE_TM_MARGIN_M))


def _iris_pupil_tip_chain(iris_poly: np.ndarray) -> np.ndarray:
    """Short pupil-tip edges (Table-SII indices 2–4)."""
    pts = np.asarray(iris_poly, dtype=float)
    return pts[2:5]


def _iris_cut_seed_polyline(iris_poly: np.ndarray) -> np.ndarray:
    """Densify pupil arc for OCC cut — keeps Table-SII endpoints 0 and 5."""
    pts = np.asarray(iris_poly, dtype=float)
    tip = densify_polyline(pts[1:5], n_per_seg=8)
    return np.vstack([pts[0:1], tip, pts[5:6]])


def _iris_inferior_chain(iris_poly: np.ndarray) -> np.ndarray:
    """Pupil-tip arc (Table-SII indices 1–4) — far from TM, needs finer structured band."""
    pts = np.asarray(iris_poly, dtype=float)
    return pts[1:5]


def _iris_superior_chain(iris_poly: np.ndarray) -> np.ndarray:
    """Outer iris root arc (indices 4→5→0→1) — TM-proximal, keep TM-safe ramp."""
    pts = np.asarray(iris_poly, dtype=float)
    return np.vstack([pts[4:6], pts[0:2]])


def _ring_lc_iris_cut(
    pts_m: np.ndarray,
    lc_iris: float,
    *,
    inferior_scale: float = IRIS_INFERIOR_LC_FRAC,
    tip_scale: float = IRIS_INFERIOR_TIP_LC_FRAC,
) -> np.ndarray:
    """Per-vertex sizing on iris cut ring — graded pupil tip."""
    pts = np.asarray(pts_m, dtype=float)
    lc = np.full(len(pts), lc_iris, dtype=float)
    lc_inf = lc_iris * inferior_scale
    lc_tip = lc_iris * tip_scale
    for i, (x, y) in enumerate(pts):
        if float(y) < IRIS_INFERIOR_TIP_Y_M and float(x) < IRIS_INFERIOR_TIP_X_M:
            lc[i] = lc_tip
        elif float(y) < IRIS_INFERIOR_Y_M and float(x) < IRIS_INFERIOR_X_M:
            lc[i] = lc_inf
    return lc


def _gmsh_polyline_distance_refinement_field(
    poly_xy: np.ndarray,
    *,
    lc_min: float,
    lc_bulk: float,
    dist_max: float,
    n_per_seg: int | None = 2,
) -> int:
    """Linear-ramp Distance sizing from a meridional polyline (field anchors only)."""
    import gmsh

    pts = np.asarray(poly_xy, dtype=float)
    if n_per_seg:
        pts = densify_polyline(pts, n_per_seg=n_per_seg)
    pt_tags = [
        gmsh.model.occ.addPoint(float(x), float(y), 0.0, lc_min) for x, y in pts
    ]
    gmsh.model.occ.synchronize()
    f_dist = gmsh.model.mesh.field.add("Distance")
    gmsh.model.mesh.field.setNumbers(f_dist, "PointsList", pt_tags)
    f_th = gmsh.model.mesh.field.add("Threshold")
    gmsh.model.mesh.field.setNumber(f_th, "InField", f_dist)
    gmsh.model.mesh.field.setNumber(f_th, "SizeMin", lc_min)
    gmsh.model.mesh.field.setNumber(f_th, "SizeMax", lc_bulk)
    gmsh.model.mesh.field.setNumber(f_th, "Sigmoid", 0)
    gmsh.model.mesh.field.setNumber(f_th, "DistMin", 0.0)
    gmsh.model.mesh.field.setNumber(f_th, "DistMax", dist_max)
    return f_th


def _gmsh_polyline_edge_distance_field(
    poly_xy: np.ndarray,
    *,
    lc_min: float,
    lc_bulk: float,
    dist_max: float,
    n_per_seg: int = 4,
) -> int:
    """Smooth wall band via Distance to OCC edge chain (no point lobes)."""
    import gmsh

    occ = gmsh.model.occ
    pts = densify_polyline(np.asarray(poly_xy, dtype=float), n_per_seg=n_per_seg)
    ptags = [occ.addPoint(float(x), float(y), 0.0, lc_min) for x, y in pts]
    ltags = [
        occ.addLine(ptags[i], ptags[i + 1]) for i in range(len(ptags) - 1) if ptags[i] != ptags[i + 1]
    ]
    occ.synchronize()
    f_dist = gmsh.model.mesh.field.add("Distance")
    gmsh.model.mesh.field.setNumbers(f_dist, "EdgesList", ltags)
    f_th = gmsh.model.mesh.field.add("Threshold")
    gmsh.model.mesh.field.setNumber(f_th, "InField", f_dist)
    gmsh.model.mesh.field.setNumber(f_th, "SizeMin", lc_min)
    gmsh.model.mesh.field.setNumber(f_th, "SizeMax", lc_bulk)
    gmsh.model.mesh.field.setNumber(f_th, "Sigmoid", 0)
    gmsh.model.mesh.field.setNumber(f_th, "DistMin", 0.0)
    gmsh.model.mesh.field.setNumber(f_th, "DistMax", dist_max)
    return f_th


def _split_polyline_by_y_exclusion(
    poly_xy: np.ndarray,
    *,
    y_center: float,
    y_half: float,
) -> list[np.ndarray]:
    """Split an open polyline, dropping vertices with |y - y_center| <= y_half."""
    pts = np.asarray(poly_xy, dtype=float)
    segments: list[list[np.ndarray]] = []
    current: list[np.ndarray] = []
    for p in pts:
        if abs(float(p[1]) - y_center) <= y_half:
            if len(current) >= 2:
                segments.append(current)
            current = []
            continue
        current.append(p)
    if len(current) >= 2:
        segments.append(current)
    return [np.asarray(s, dtype=float) for s in segments if len(s) >= 2]


def _vitreous_sym0_wall_polyline(fluid: dict[str, np.ndarray]) -> np.ndarray:
    """Outer vitreous wall on symmetry_0 (θ=0, z=0): hyaloid → ora → posterior pole."""
    hy = np.asarray(fluid["hyaloid_right"], dtype=float)
    vit = np.asarray(fluid["vitreous_retina_right"], dtype=float)
    return np.vstack([hy, vit[1:]])


def _ring_lc_vitreous_wall_band(
    pts_m: np.ndarray,
    wall_poly: np.ndarray,
    *,
    lc_default: float,
    lc_wall: float,
    lc_wall_inner: float | None = None,
    band_m: float = TOPOSET_REFINE_DIST_M,
    inner_band_m: float | None = None,
    x_coarsen: float = 0.85e-3,
    axis_factor: float = 2.2,
    ivi_y_center: float | None = None,
    ivi_y_half: float = VITREOUS_SYM0_IVI_AXIS_Y_HALF_M,
    ivi_axis_factor: float = VITREOUS_SYM0_IVI_AXIS_LC_FACTOR,
) -> np.ndarray:
    """Seed-ring sizing: graded wall bands; soften axis coarsen in IVI meridian."""
    pts = np.asarray(pts_m, dtype=float)
    wall = np.asarray(wall_poly, dtype=float)
    lc_inner = lc_wall_inner if lc_wall_inner is not None else lc_wall
    inner_m = inner_band_m if inner_band_m is not None else band_m * 0.48
    y_ivi = float(ivi_y_center if ivi_y_center is not None else IVI_TIP_ORIGIN_M[1])
    lc = np.full(len(pts), lc_default, dtype=float)
    for i, (x, y) in enumerate(pts):
        ax = abs(float(x))
        d_wall = _dist_to_polyline_xy(np.array([ax, float(y)], dtype=float), wall)
        if d_wall <= inner_m:
            lc[i] = min(lc[i], lc_inner)
        elif d_wall <= band_m:
            lc[i] = min(lc[i], lc_wall)
        elif ax < x_coarsen and d_wall > band_m * 1.15:
            factor = axis_factor
            if abs(float(y) - y_ivi) <= ivi_y_half:
                factor = min(factor, ivi_axis_factor)
            w = math.exp(-ax / x_coarsen)
            lc[i] = lc_default * (1.0 + w * (factor - 1.0))
    return lc

def _gmsh_iris_refinement_fields(
    iris_poly: np.ndarray,
    *,
    lc_iris: float,
    lc_bulk: float,
    tm_markers: np.ndarray | None,
    mesh_level: str,
) -> list[int]:
    """Edge-based iris bands: fine structured inferior pupil + TM-safe outer root."""
    lc_inf = lc_iris * IRIS_INFERIOR_LC_FRAC
    lc_tip = lc_iris * IRIS_INFERIOR_TIP_LC_FRAC
    lc_mid = max(lc_inf * 1.35, lc_iris * 0.78)
    inf = _iris_inferior_chain(iris_poly)
    tip = _iris_pupil_tip_chain(iris_poly)
    sup = _iris_superior_chain(iris_poly)
    dist_inf = _iris_refine_dist_max_segment(inf, tm_markers, mesh_level=mesh_level)
    dist_sup = _iris_refine_dist_max_segment(sup, tm_markers, mesh_level=mesh_level)
    fields = [
        _gmsh_polyline_edge_distance_field(
            tip,
            lc_min=lc_tip,
            lc_bulk=lc_inf,
            dist_max=IRIS_INFERIOR_TIP_DIST_M,
            n_per_seg=12,
        ),
        _gmsh_polyline_edge_distance_field(
            inf,
            lc_min=lc_inf,
            lc_bulk=lc_mid,
            dist_max=dist_inf,
            n_per_seg=10,
        ),
        _gmsh_polyline_edge_distance_field(
            inf,
            lc_min=lc_mid,
            lc_bulk=lc_bulk,
            dist_max=min(dist_inf * 1.35, IRIS_REFINE_DIST_M.get(mesh_level, 0.34e-3)),
            n_per_seg=6,
        ),
        _gmsh_polyline_edge_distance_field(
            sup,
            lc_min=lc_iris,
            lc_bulk=lc_bulk,
            dist_max=dist_sup,
            n_per_seg=4,
        ),
    ]
    print(
        f"INFO: iris edge refine tip lc={lc_tip:.2e}; inferior lc={lc_inf:.2e} "
        f"dist={dist_inf:.2e}; superior lc={lc_iris:.2e} dist={dist_sup:.2e}"
    )
    return fields


def _gmsh_iris_refinement_field(
    iris_poly: np.ndarray,
    *,
    lc_iris: float,
    lc_bulk: float,
    dist_max: float,
) -> int:
    """Legacy single-band iris field (prefer _gmsh_iris_refinement_fields)."""
    return _gmsh_polyline_edge_distance_field(
        iris_poly,
        lc_min=lc_iris,
        lc_bulk=lc_bulk,
        dist_max=dist_max,
        n_per_seg=4,
    )


def _gmsh_set_background_mesh(field_tags: list[int]) -> None:
    import gmsh

    if not field_tags:
        return
    if len(field_tags) == 1:
        gmsh.model.mesh.field.setAsBackgroundMesh(field_tags[0])
        return
    f_min = gmsh.model.mesh.field.add("Min")
    gmsh.model.mesh.field.setNumbers(f_min, "FieldsList", field_tags)
    gmsh.model.mesh.field.setAsBackgroundMesh(f_min)


def _gmsh_tip_refinement_fields(
    tip_origins_m: list[tuple[float, float, float]],
    *,
    lc_bulk: float,
    lc_tip: float,
    dist_max: float = TIP_REFINE_DIST_M,
    box_half: float = TIP_BOX_HALF_M,
    lumen_r: float = NEEDLE_R_LUMEN_M,
    n_cells_across: int = TIP_CELLS_ACROSS,
) -> tuple[list[int], list[int]]:
    """Local size fields at IVI/ACP Model B sites (30G lumen scale).

    Embeds lumen centre only; Ball + Distance sizing for ≥5 centres inside r = 0.07 mm.
    """
    import gmsh

    lc_lumen = max(lc_tip, lumen_r / n_cells_across)
    lc_p = max(lumen_r / 18.0, 2.0e-6)  # ~3.9 µm → ~13 centres inside r = 0.07 mm
    fields: list[int] = []
    embed_tags: list[int] = []

    for origin in tip_origins_m:
        ox, oy, oz = origin
        x = 0.0 if abs(ox) < 1.0e-8 else float(ox)

        for a in lumen_embed_points(origin, r=lumen_r):
            embed_tags.append(gmsh.model.occ.addPoint(*a, lc_p))

        f_lumen = gmsh.model.mesh.field.add("Ball")
        gmsh.model.mesh.field.setNumber(f_lumen, "VIn", lc_p)
        gmsh.model.mesh.field.setNumber(f_lumen, "VOut", lc_bulk)
        gmsh.model.mesh.field.setNumber(f_lumen, "XCenter", x)
        gmsh.model.mesh.field.setNumber(f_lumen, "YCenter", float(oy))
        gmsh.model.mesh.field.setNumber(f_lumen, "ZCenter", float(oz))
        gmsh.model.mesh.field.setNumber(f_lumen, "Radius", max(2.0 * lumen_r, lc_lumen * 4.0))
        fields.append(f_lumen)

        print(
            f"INFO: tip refine @ ({ox:.4f},{oy:.4f},{oz:.4f}) m "
            f"lc_lumen={lc_lumen:.2e} lc_p={lc_p:.2e} ball_r={lumen_r:.2e} "
            f"embed={len(embed_tags)}"
        )
    return fields, embed_tags


def _report_lumen_tet_centres(
    tip_origins_m: list[tuple[float, float, float]],
    *,
    lumen_r: float = NEEDLE_R_LUMEN_M,
) -> dict[str, float | int]:
    """Count Gmsh tet/prism centroids inside each lumen sphere (post mesh.generate)."""
    import gmsh

    node_tags, coords, _ = gmsh.model.mesh.getNodes()
    xyz = np.asarray(coords, dtype=float).reshape(-1, 3)
    node_idx = {int(t): i for i, t in enumerate(node_tags)}

    stats: dict[str, float | int] = {}
    for i, (ox, oy, oz) in enumerate(tip_origins_m):
        origin = np.array([ox, oy, oz], dtype=float)
        inside = 0
        nearest = float("inf")
        for etype in gmsh.model.mesh.getElementTypes(3):
            npe = gmsh.model.mesh.getElementProperties(etype)[3]
            _etags, enodes = gmsh.model.mesh.getElementsByType(etype)
            enodes = np.asarray(enodes, dtype=int).reshape(-1, npe)
            for nodes in enodes:
                idx = [node_idx[int(n)] for n in nodes]
                ctr = xyz[idx].mean(axis=0)
                d = float(np.linalg.norm(ctr - origin))
                nearest = min(nearest, d)
                if d <= lumen_r:
                    inside += 1
        stats[f"tip{i}_inside_r"] = inside
        stats[f"tip{i}_nearest_m"] = nearest
        print(
            f"INFO: lumen check tip{i} @ ({ox:.4f},{oy:.4f},{oz:.4f}) "
            f"centres inside r={lumen_r:.2e}: {inside}, nearest={nearest:.2e} m"
        )
    return stats


def _gmsh_toposet_refinement_fields(
    tip_origins_m: tuple[tuple[float, float, float], ...],
    *,
    lc_bulk: float,
    lc_topo: float,
    r_topo: float = TOPOSET_TIP_RADIUS_M,
    ball_r: float | None = None,
    skip_ivi: bool = False,
) -> list[int]:
    """Ball sizing at IVI/ACP topoSet sites (Model B) — no embed, stable with structured revolve."""
    import gmsh

    br = ball_r or TOPOSET_REFINE_DIST_M
    fields: list[int] = []
    for ox, oy, oz in tip_origins_m:
        if skip_ivi and abs(float(oy) - IVI_TIP_ORIGIN_M[1]) < 1.0e-6:
            continue
        x = 0.0 if abs(ox) < 1.0e-8 else float(ox)
        f_ball = gmsh.model.mesh.field.add("Ball")
        gmsh.model.mesh.field.setNumber(f_ball, "VIn", lc_topo)
        gmsh.model.mesh.field.setNumber(f_ball, "VOut", lc_bulk)
        gmsh.model.mesh.field.setNumber(f_ball, "XCenter", x)
        gmsh.model.mesh.field.setNumber(f_ball, "YCenter", float(oy))
        gmsh.model.mesh.field.setNumber(f_ball, "ZCenter", float(oz))
        gmsh.model.mesh.field.setNumber(f_ball, "Radius", br)
        fields.append(f_ball)
        print(
            f"INFO: topoSet ball @ ({ox:.4f},{oy:.4f},{oz:.4f}) m "
            f"lc_topo={lc_topo:.2e} r_topo={r_topo:.2e} ball_r={br:.2e}"
        )
    if skip_ivi:
        print("INFO: IVI topoSet ball skipped — covered by vitreous symmetry_0 edge field")
    return fields


def _report_toposet_centres(
    tip_origins_m: tuple[tuple[float, float, float], ...],
    *,
    r_topo: float = TOPOSET_TIP_RADIUS_M,
) -> dict[str, float | int]:
    """Count mesh cell centroids inside each topoSet sphere (post generate)."""
    import gmsh

    node_tags, coords, _ = gmsh.model.mesh.getNodes()
    xyz = np.asarray(coords, dtype=float).reshape(-1, 3)
    node_idx = {int(t): i for i, t in enumerate(node_tags)}
    labels = ("ivi", "acp")
    stats: dict[str, float | int] = {}
    for i, (ox, oy, oz) in enumerate(tip_origins_m):
        origin = np.array([ox, oy, oz], dtype=float)
        inside = 0
        nearest = float("inf")
        for etype in gmsh.model.mesh.getElementTypes(3):
            npe = gmsh.model.mesh.getElementProperties(etype)[3]
            _etags, enodes = gmsh.model.mesh.getElementsByType(etype)
            enodes = np.asarray(enodes, dtype=int).reshape(-1, npe)
            for nodes in enodes:
                idx = [node_idx[int(n)] for n in nodes]
                ctr = xyz[idx].mean(axis=0)
                d = float(np.linalg.norm(ctr - origin))
                nearest = min(nearest, d)
                if d <= r_topo:
                    inside += 1
        lab = labels[i] if i < len(labels) else f"tip{i}"
        stats[f"{lab}_toposet_inside_r"] = inside
        stats[f"{lab}_toposet_nearest_m"] = nearest
        print(
            f"INFO: topoSet check {lab} @ ({ox:.4f},{oy:.4f},{oz:.4f}) "
            f"centres inside r={r_topo:.2e}: {inside}, nearest={nearest:.2e} m"
        )
    return stats


def _ring_lc_near_tips(
    pts_m: np.ndarray,
    tip_origins_m: tuple[tuple[float, float, float], ...],
    *,
    lc_bulk: float,
    lc_tip: float,
    dist_max: float = TIP_REFINE_DIST_M,
) -> np.ndarray:
    """Per-vertex sizing on meridional seed ring near IVI/ACP sites."""
    pts = np.asarray(pts_m, dtype=float)
    lc = np.full(len(pts), lc_bulk, dtype=float)
    for ox, oy, _oz in tip_origins_m:
        d = np.sqrt((pts[:, 0] - ox) ** 2 + (pts[:, 1] - oy) ** 2)
        blend = np.clip(1.0 - d / dist_max, 0.0, 1.0)
        lc = np.minimum(lc, lc_bulk + (lc_tip - lc_bulk) * blend)
    return lc


# Coarser cells near x=0 (symmetry_0 wedge) → lower max non-orthogonality there.
AXIS_COARSEN_M = {
    "M5": 1.0e-3,
    "M4": 0.92e-3,
    "M1": 0.85e-3,
    "M2": 0.75e-3,
    "M3": 0.65e-3,
}
AXIS_LC_FACTOR = {"M5": 2.5, "M4": 2.35, "M1": 2.2, "M2": 2.0, "M3": 1.8}
N_THETA_LEVELS = {"M5": 4, "M4": 5, "M1": 6, "M2": 8, "M3": 10}


def _ring_lc_axis_coarsen(
    pts_m: np.ndarray,
    lc_base: float,
    *,
    x_coarsen: float,
    factor: float,
) -> np.ndarray:
    pts = np.asarray(pts_m, dtype=float)
    if x_coarsen <= 0.0 or factor <= 1.0:
        return np.full(len(pts), lc_base, dtype=float)
    w = np.exp(-np.maximum(pts[:, 0], 0.0) / x_coarsen)
    return lc_base * (1.0 + w * (factor - 1.0))


def _gmsh_axis_coarsen_field(lc: float, *, x_coarsen: float, factor: float) -> int | None:
    import gmsh

    if x_coarsen <= 0.0 or factor <= 1.0:
        return None
    amp = factor - 1.0
    inv = 1.0 / x_coarsen
    field = gmsh.model.mesh.field.add("MathEval")
    gmsh.model.mesh.field.setString(field, "F", f"{lc}*(1+{amp}*exp(-{inv}*abs(x)))")
    return field


def _decimate_ring_min_spacing(pts_m: np.ndarray, min_seg: float) -> np.ndarray:
    """Drop consecutive vertices closer than min_seg (keeps outline, removes micro-vertices)."""
    pts = _snap_axis_ring(_clean_ring(np.asarray(pts_m, dtype=float))[:-1])
    if len(pts) < 3:
        return pts
    out = [pts[0]]
    for p in pts[1:]:
        if float(np.linalg.norm(p - out[-1])) >= min_seg:
            out.append(p)
    if float(np.linalg.norm(out[-1] - out[0])) < min_seg and len(out) > 2:
        out.pop()
    return np.asarray(out)


def _snap_axis_ring(pts: np.ndarray) -> np.ndarray:
    """Keep true axis at x=0 (no 1 µm nudge — that duplicates the symmetry spine)."""
    pts = np.asarray(pts, dtype=float).copy()
    for i, (x, _y) in enumerate(pts):
        if abs(x) < 1.0e-9:
            pts[i, 0] = 0.0
    return pts


def _g2_fluid_landmarks_m() -> dict[str, np.ndarray | float]:
    """Lamminsalo Table SI/SII segments for G2-fluid patch tagging [m]."""
    tm_se_a = np.array(PTS["tm_cornea_void"], dtype=float) * M_PER_CM
    tm_se_b = np.array(PTS["tm_ciliary_void"], dtype=float) * M_PER_CM
    iris_post = np.array(PTS["iris_ciliary_post"], dtype=float) * M_PER_CM
    purple = np.array(PTS["hyaloid_curved_flat"], dtype=float) * M_PER_CM
    tm_seg = tm_se_b - tm_se_a
    inl_seg = purple - iris_post
    return {
        "tm_se_a": tm_se_a,
        "tm_se_b": tm_se_b,
        "tm_se_L": float(np.linalg.norm(tm_seg)),
        "tm_se_u": tm_seg / max(float(np.linalg.norm(tm_seg)), 1e-16),
        "iris_post": iris_post,
        "inl_seg": inl_seg,
        "inl_L": float(np.linalg.norm(inl_seg)),
        "inl_u": inl_seg / max(float(np.linalg.norm(inl_seg)), 1e-16),
    }


def _dist_point_to_segment_xy(p: np.ndarray, a: np.ndarray, b: np.ndarray) -> float:
    ab = b - a
    L2 = float(np.dot(ab, ab))
    if L2 < 1e-20:
        return float(np.linalg.norm(p - a))
    t = float(np.clip(np.dot(p - a, ab) / L2, 0.0, 1.0))
    return float(np.linalg.norm(p - (a + t * ab)))


def _dist_to_polyline_xy(p: np.ndarray, poly: np.ndarray) -> float:
    poly = np.asarray(poly, dtype=float)
    if len(poly) < 2:
        return float("inf")
    dmin = float("inf")
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        dmin = min(dmin, _dist_point_to_segment_xy(p, a, b))
    return dmin


def _on_tm_se_face_m(ax: float, cy: float, lm: dict[str, np.ndarray | float], *, tol: float) -> bool:
    p = np.array([ax, cy], dtype=float)
    t = float(np.dot(p - lm["tm_se_a"], lm["tm_se_u"]))
    if t < -tol or t > float(lm["tm_se_L"]) + tol:
        return False
    closest = lm["tm_se_a"] + np.clip(t, 0.0, float(lm["tm_se_L"])) * lm["tm_se_u"]
    return float(np.linalg.norm(p - closest)) <= tol


def _on_ac_inlet_face_m(ax: float, cy: float, lm: dict[str, np.ndarray | float], *, tol: float) -> bool:
    """AC–CB production face: iris_ciliary_post → hyaloid_curved_flat (Table SI)."""
    p = np.array([ax, cy], dtype=float)
    t = float(np.dot(p - lm["iris_post"], lm["inl_u"]))
    if t < -tol or t > float(lm["inl_L"]) + tol:
        return False
    closest = lm["iris_post"] + np.clip(t, 0.0, float(lm["inl_L"])) * lm["inl_u"]
    return float(np.linalg.norm(p - closest)) <= tol


def _iris_cut_polyline(fluid: dict[str, np.ndarray]) -> np.ndarray:
    """Table-SII iris loop for OCC hole (exact vertices, no AC-boundary indent)."""
    pts = _clean_ring(np.asarray(fluid["iris_half"], dtype=float), tol=1e-9)[:-1]
    if len(pts) < 4:
        raise ValueError("iris_half too short for OCC cut")
    return pts


def _face_xy_samples(tag: int) -> list[tuple[float, float]]:
    """Meridional (|x|, y) samples at bbox corners — robust for revolved micro-faces."""
    import gmsh

    xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(2, tag)
    out: list[tuple[float, float]] = []
    for x in (xmin, xmax):
        for y in (ymin, ymax):
            for _z in (zmin, zmax):
                out.append((abs(float(x)), float(y)))
    cx, cy = 0.5 * (xmin + xmax), 0.5 * (ymin + ymax)
    out.append((abs(float(cx)), float(cy)))
    return out


def _face_y_extent_m(tag: int) -> tuple[float, float]:
    import gmsh

    _xmin, ymin, _zmin, _xmax, ymax, _zmax = gmsh.model.getBoundingBox(2, tag)
    return float(ymin), float(ymax)


def _classify_g2_fluid_face(
    tag: int,
    *,
    iris_poly: np.ndarray,
    lm: dict[str, np.ndarray | float],
    tm_tol: float = 8.0e-5,
    inlet_tol: float = 1.0e-4,
    iris_tol: float = 1.5e-4,
) -> str:
    samples = _face_xy_samples(tag)
    if any(_on_tm_se_face_m(ax, cy, lm, tol=tm_tol) for ax, cy in samples):
        return "outlet_tm"

    # ac_inlet: outer-wall samples on Table-SI segment; y-extent must stay on that edge.
    y_inl_a = float(lm["iris_post"][1])
    y_inl_b = float((lm["iris_post"] + lm["inl_seg"])[1])
    y_lo = min(y_inl_a, y_inl_b) - inlet_tol
    y_hi = max(y_inl_a, y_inl_b) + inlet_tol
    r_min_inlet = float(lm["iris_post"][0]) - 0.3e-3
    ymin, ymax = _face_y_extent_m(tag)
    outer = [(ax, cy) for ax, cy in samples if ax >= r_min_inlet]
    if (
        ymin >= y_lo
        and ymax <= y_hi
        and outer
        and any(_on_ac_inlet_face_m(ax, cy, lm, tol=inlet_tol) for ax, cy in outer)
    ):
        return "ac_inlet"

    if any(
        _dist_to_polyline_xy(np.array([ax, cy], dtype=float), iris_poly) <= iris_tol
        for ax, cy in samples
    ):
        return "iris_wall"
    return "wall"


def sync_g2_fluid_split_patches(case_name: str = DEFAULT_CASE) -> None:
    """Write topoSet fallback cylinders from Lamminsalo landmarks (if gmsh patches missing)."""
    case, _, _ = case_paths(case_name)
    lm = _g2_fluid_landmarks_m()
    tm_a, tm_b = lm["tm_se_a"], lm["tm_se_b"]
    inl_a, inl_b = lm["iris_post"], lm["iris_post"] + lm["inl_seg"]
    pad_r = 5.5e-4
    pad_y = 3.0e-4

    def _vec(v: np.ndarray) -> str:
        return f"({v[0]:.5f} {v[1]:.5f} 0)"

    text = f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      topoSetDict;
}}

// Fallback carve from Table SI/SII landmarks (m). Prefer gmsh physical patches.

actions
(
    {{
        name    wall_pool;
        type    faceSet;
        action  new;
        source  patchToFace;
        patch   wall;
    }}

    {{
        name    outlet_tm_faces;
        type    faceSet;
        action  new;
        source  faceToFace;
        set     wall_pool;
    }}
    {{
        name    outlet_tm_faces;
        type    faceSet;
        action  subset;
        source  cylinderAnnulusToFace;
        p1      {_vec(tm_a - np.array([0.0, pad_y]))};
        p2      {_vec(tm_b + np.array([0.0, pad_y]))};
        outerRadius {max(tm_a[0], tm_b[0]) + pad_r:.5f};
        innerRadius {min(tm_a[0], tm_b[0]) - pad_r:.5f};
    }}

    {{
        name    ac_inlet_faces;
        type    faceSet;
        action  new;
        source  faceToFace;
        set     wall_pool;
    }}
    {{
        name    ac_inlet_faces;
        type    faceSet;
        action  subset;
        source  cylinderAnnulusToFace;
        p1      {_vec(inl_a - np.array([0.0, pad_y]))};
        p2      {_vec(inl_b + np.array([0.0, pad_y]))};
        outerRadius {max(inl_a[0], inl_b[0]) + pad_r:.5f};
        innerRadius {min(inl_a[0], inl_b[0]) - pad_r:.5f};
    }}
    {{
        name    ac_inlet_faces;
        type    faceSet;
        action  delete;
        source  faceToFace;
        set     outlet_tm_faces;
    }}
);
"""
    out = case / "fluid" / "system" / "topoSetDict.splitPatches"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(f"INFO: synced {out.name} from Lamminsalo landmarks")


def mesh_g2_fluid(
    fluid: dict[str, np.ndarray],
    msh_path: Path,
    *,
    mesh_level: str = "M1",
    tm_markers: np.ndarray | None = None,
    tm_layers: int = 0,
    tip_refine: bool = True,
    tip_sites: str = "both",
    tm_size_field: bool = True,
    tip_topo_refine: bool = True,
    iris_refine: bool = True,
    vitreous_sym0_refine: bool = True,
    n_theta_override: int | None = None,
) -> None:
    """G2-fluid: (AC ∪ vitreous ∪ TM)_half − iris hole, structured 90° revolve about +y.

    Iris is a precise Table-SII OCC cut on outer AC (no boundary indent).
    Patches iris_wall / ac_inlet / outlet_tm tagged from Lamminsalo landmarks (CAD
    physical groups → gmshToFoam; Allrun skips topoSet carve when present).
    """
    import gmsh

    if mesh_level not in MESH_LEVELS:
        raise ValueError(f"unknown mesh_level {mesh_level}")
    sizes = MESH_LEVELS[mesh_level]
    # Keep min size from collapsing on the optical axis
    lc_bulk = max(sizes["lc"], 5.0e-4)
    lc_fine = max(sizes["lc_fine"], 1.5e-4)
    lc_iris = _lc_iris_for_level(mesh_level, lc_fine)
    n_theta = n_theta_override or N_THETA_LEVELS.get(mesh_level, 6)
    x_coarsen = AXIS_COARSEN_M.get(mesh_level, 0.85e-3)
    axis_factor = AXIS_LC_FACTOR.get(mesh_level, 2.2)

    gmsh.initialize()
    gmsh.model.add("eye_g2_fluid_lamminsalo")
    gmsh.option.setNumber("General.Terminal", 1)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", lc_fine)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", lc_bulk * 1.2)
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 1)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 1)
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.option.setNumber("Mesh.Optimize", 1)
    gmsh.option.setNumber("Mesh.Smoothing", 20)
    gmsh.option.setNumber("Mesh.OptimizeNetgen", 1)
    gmsh.option.setNumber("Mesh.Algorithm", 6)  # Frontal-Delaunay for 2D seed
    gmsh.option.setNumber("Mesh.RecombineAll", 0)

    occ = gmsh.model.occ

    def add_ring(
        pts_m,
        lc=2.0e-4,
        n_per_seg: int | None = 4,
        tip_lc: tuple | None = None,
        tm_lc: tuple[np.ndarray, float] | None = None,
        vit_wall_lc: tuple[np.ndarray, float, float, float, float] | None = None,
        iris_cut_lc: float | None = None,
    ):
        pts = np.asarray(pts_m, dtype=float)
        if n_per_seg:
            pts = densify_polyline(pts, n_per_seg=n_per_seg)
        pts = _clean_ring(pts, tol=1e-9)[:-1]
        if len(pts) > 120:
            idx = np.linspace(0, len(pts) - 1, 120).astype(int)
            pts = pts[idx]
        # Remove sub-50 µm consecutive edges (ora/hyaloid micro-vertices from outlines).
        merged = [pts[0]]
        for p in pts[1:]:
            if float(np.linalg.norm(p - merged[-1])) >= 50.0e-6:
                merged.append(p)
        pts = _snap_axis_ring(np.asarray(merged))
        if tm_lc is not None:
            tm_markers, lc_tm_v = tm_lc
            lc_arr = _ring_lc_tm_band(
                pts, tm_markers, lc_default=lc, lc_tm=lc_tm_v
            )
        elif vit_wall_lc is not None:
            wall_poly, lc_wall_v, lc_inner_v, band_m, inner_m = vit_wall_lc
            lc_arr = _ring_lc_vitreous_wall_band(
                pts,
                wall_poly,
                lc_default=lc,
                lc_wall=lc_wall_v,
                lc_wall_inner=lc_inner_v,
                band_m=band_m,
                inner_band_m=inner_m,
                x_coarsen=x_coarsen,
                axis_factor=axis_factor,
            )
        elif tip_lc is not None:
            origins, lc_bulk_v, lc_tip_v = tip_lc
            lc_arr = _ring_lc_near_tips(
                pts, origins, lc_bulk=lc_bulk_v, lc_tip=lc_tip_v
            )
        elif iris_cut_lc is not None:
            lc_arr = _ring_lc_iris_cut(pts, iris_cut_lc)
        else:
            lc_arr = _ring_lc_axis_coarsen(
                pts, lc, x_coarsen=x_coarsen, factor=axis_factor
            )
        ptags = [
            occ.addPoint(float(x), float(y), 0.0, float(lc_arr[i]))
            for i, (x, y) in enumerate(pts)
        ]
        ltags = []
        for i in range(len(ptags)):
            a, b = ptags[i], ptags[(i + 1) % len(ptags)]
            if a != b:
                ltags.append(occ.addLine(a, b))
        return occ.addPlaneSurface([occ.addCurveLoop(ltags)])

    vit_pts = np.asarray(fluid["band_vitreous_half"], dtype=float)
    vit_tip_lc = None
    lc_tip = None
    lc_topo = lc_toposet_for_level(mesh_level) if tip_topo_refine and not tip_refine else None
    sym0_sizes = (
        _lc_vitreous_sym0_for_level(mesh_level) if vitreous_sym0_refine else None
    )
    vit_wall_poly = (
        _vitreous_sym0_wall_polyline(fluid) if vitreous_sym0_refine else None
    )
    lc_tm_val: float | None = None
    tm_lc_arg = None
    ac_pts = np.asarray(fluid["band_ac_half"], dtype=float)
    if tm_markers is not None and tm_layers >= 5 and tm_size_field:
        lc_tm_val = _lc_tm_for_level(mesh_level, tm_layers)
        tm_lc_arg = (np.asarray(tm_markers, dtype=float), lc_tm_val)
    s_ac = add_ring(
        ac_pts,
        lc=min(lc_fine, lc_tm_val) if lc_tm_val is not None else lc_fine,
        n_per_seg=2,
        tm_lc=tm_lc_arg,
    )
    if tip_refine:
        n_across = (
            TIP_CELLS_ACROSS_IVI.get(mesh_level, 10)
            if tip_sites == "ivi"
            else TIP_CELLS_ACROSS
        )
        lc_tip = lc_tip_for_level(mesh_level, n_cells_across=n_across)
        refine_origins = tip_origins_for(tip_sites)
        if tip_sites in ("ivi", "both"):
            vit_pts = _inject_axis_stations(
                vit_pts, [(IVI_TIP_ORIGIN_M[1], lc_tip)]
            )
        vit_tip_lc = (refine_origins, lc_bulk, lc_tip)
    vit_wall_lc_arg = None
    if vit_wall_poly is not None and sym0_sizes is not None:
        vit_wall_lc_arg = (
            vit_wall_poly,
            sym0_sizes["lc_mid"],
            sym0_sizes["lc_inner"],
            sym0_sizes["dist_mid"],
            sym0_sizes["dist_inner"],
        )
    s_vit = add_ring(
        vit_pts,
        lc=lc_bulk,
        n_per_seg=2,
        tip_lc=vit_tip_lc,
        vit_wall_lc=vit_wall_lc_arg,
    )
    fused = occ.fuse([(2, s_ac)], [(2, s_vit)], removeObject=True, removeTool=True)
    occ.synchronize()
    if not fused[0]:
        raise RuntimeError("OCC fuse AC∪vitreous (half) produced nothing")

    iris_poly = _iris_cut_polyline(fluid)
    iris_seed = _iris_cut_seed_polyline(iris_poly)
    try:
        cut = occ.cut(
            [e for e in fused[0] if e[0] == 2],
            [(2, add_ring(iris_seed, lc=lc_iris, n_per_seg=None, iris_cut_lc=lc_iris))],
            removeObject=True,
            removeTool=True,
        )
        occ.synchronize()
        fluid_surfaces = [e for e in cut[0] if e[0] == 2] if cut[0] else []
        if not fluid_surfaces:
            raise RuntimeError("iris cut emptied fluid")
        print(
            f"INFO: cut Lamminsalo iris hole ({len(iris_poly)} Table-SII vertices, "
            f"outer AC boundary)"
        )
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"iris OCC cut failed: {exc}") from exc

    print(f"INFO: G2-fluid faces before revolve: {len(fluid_surfaces)}")
    seed_tags = [s[1] for s in fluid_surfaces]

    # Auto revolve needed for Ball tip fields; structured layers block local 3D sizing.
    if tip_refine:
        out = occ.revolve(
            fluid_surfaces,
            0, 0, 0,
            0, 1, 0,
            REVOLVE_RAD,
            recombine=True,
        )
    else:
        out = occ.revolve(
            fluid_surfaces,
            0, 0, 0,
            0, 1, 0,
            REVOLVE_RAD,
            numElements=[n_theta],
            heights=[1],
            recombine=True,
        )
    occ.synchronize()
    volume_tags = [e[1] for e in out if e[0] == 3]
    if not volume_tags:
        raise RuntimeError("No revolved volume")
    print(
        f"INFO: revolve n_theta={'auto' if tip_refine else n_theta}, volumes={volume_tags}"
    )

    lm = _g2_fluid_landmarks_m()
    groups: dict[str, list[int]] = {
        "symmetry_0": [],
        "symmetry_90": [],
        "iris_wall": [],
        "ac_inlet": [],
        "outlet_tm": [],
        "wall": [],
    }
    boundaries = gmsh.model.getBoundary([(3, v) for v in volume_tags], oriented=False)
    plane_tol = 2.0e-4
    reserved = set(seed_tags)

    for dim, tag in boundaries:
        xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(dim, tag)
        dx, dy, dz = xmax - xmin, ymax - ymin, zmax - zmin
        if abs(zmin) < plane_tol and abs(zmax) < plane_tol and dx * dy > 1e-12:
            groups["symmetry_0"].append(tag)
            reserved.add(tag)
        elif abs(xmin) < plane_tol and abs(xmax) < plane_tol and dy * dz > 1e-12:
            groups["symmetry_90"].append(tag)
            reserved.add(tag)

    for stag in seed_tags:
        if stag not in reserved:
            groups["symmetry_0"].append(stag)
            reserved.add(stag)

    for dim, tag in boundaries:
        if tag in reserved:
            continue
        patch = _classify_g2_fluid_face(tag, iris_poly=iris_poly, lm=lm)
        groups[patch].append(tag)

    for name in ("iris_wall", "ac_inlet", "outlet_tm"):
        print(f"INFO: patch {name}: {len(set(groups[name]))} faces")
    if not groups["iris_wall"]:
        print("WARNING: no iris_wall faces tagged — check iris loop / tolerances")
    if not groups["ac_inlet"]:
        print("WARNING: no ac_inlet faces tagged")
    if not groups["outlet_tm"]:
        print("WARNING: no outlet_tm faces tagged")

    if not groups["symmetry_0"] or not groups["symmetry_90"]:
        print(
            f"WARNING: symmetry incomplete sym0={len(groups['symmetry_0'])} "
            f"sym90={len(groups['symmetry_90'])}"
        )

    gmsh.model.addPhysicalGroup(3, volume_tags, tag=1, name="fluid")
    pid = 2
    for name, tags in groups.items():
        if not tags:
            print(f"WARNING: empty patch group '{name}'")
            continue
        # unique tags
        utags = sorted(set(tags))
        gmsh.model.addPhysicalGroup(2, utags, tag=pid, name=name)
        pid += 1

    lc_min = lc_fine
    if lc_topo is not None:
        lc_min = min(lc_min, lc_topo)
    if iris_refine:
        lc_min = min(lc_min, lc_iris * IRIS_INFERIOR_TIP_LC_FRAC)
    if vitreous_sym0_refine and sym0_sizes is not None:
        lc_min = min(lc_min, sym0_sizes["lc_ivi"], sym0_sizes["lc_inner"])
    if lc_tm_val is not None:
        lc_min = min(lc_min, lc_tm_val)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", lc_min)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", lc_bulk)
    bg_fields: list[int] = []
    embed_pts: list[int] = []
    tip_origin_list = list(tip_origins_for(tip_sites)) if tip_refine else []
    if tip_refine and lc_tip is not None:
        n_across = (
            TIP_CELLS_ACROSS_IVI.get(mesh_level, 10)
            if tip_sites == "ivi"
            else TIP_CELLS_ACROSS
        )
        fields, embed_pts = _gmsh_tip_refinement_fields(
            tip_origin_list,
            lc_bulk=lc_bulk,
            lc_tip=lc_tip,
            n_cells_across=n_across,
        )
        bg_fields.extend(fields)
    elif lc_topo is not None:
        bg_fields.extend(
            _gmsh_toposet_refinement_fields(
                TIP_ORIGINS_M,
                lc_bulk=lc_bulk,
                lc_topo=lc_topo,
                skip_ivi=vitreous_sym0_refine,
            )
        )
    if embed_pts and volume_tags:
        gmsh.model.occ.synchronize()
        for v in volume_tags:
            try:
                gmsh.model.mesh.embed(0, embed_pts, 3, v)
            except Exception as exc:  # noqa: BLE001
                print(f"WARNING: embed {len(embed_pts)} points in vol {v}: {exc}")
        print(f"INFO: embedded {len(embed_pts)} lumen anchor nodes in volume(s)")
    if tm_markers is not None and tm_layers >= 5 and tm_size_field:
        bg_fields.extend(
            _gmsh_tm_refinement_fields(
                np.asarray(tm_markers, dtype=float),
                _tm_se_segment_polyline(lm),
                lc_tm=lc_tm_val or _lc_tm_for_level(mesh_level, tm_layers),
                lc_bulk=lc_bulk,
                tm_layers=tm_layers,
            )
        )
    if iris_refine:
        bg_fields.extend(
            _gmsh_iris_refinement_fields(
                iris_poly,
                lc_iris=lc_iris,
                lc_bulk=lc_bulk,
                tm_markers=tm_markers,
                mesh_level=mesh_level,
            )
        )
    if vitreous_sym0_refine and vit_wall_poly is not None and sym0_sizes is not None:
        bg_fields.extend(
            _gmsh_vitreous_sym0_refinement_fields(
                vit_wall_poly,
                lc_inner=sym0_sizes["lc_inner"],
                lc_mid=sym0_sizes["lc_mid"],
                lc_ivi=sym0_sizes["lc_ivi"],
                lc_bulk=lc_bulk,
                dist_inner=sym0_sizes["dist_inner"],
                dist_mid=sym0_sizes["dist_mid"],
            )
        )
    # Ring-level axis coarsening only (MathEval volume field stacks slivers at x≈0).
    print(
        f"INFO: symmetry-axis coarsening on seed rings x<{x_coarsen:.2e} m "
        f"lc×{axis_factor:.1f} (non-ortho at θ=0)"
    )
    _gmsh_set_background_mesh(bg_fields)
    gmsh.model.mesh.generate(3)
    lumen_stats: dict[str, float | int] = {}
    if tip_refine and tip_origin_list:
        lumen_stats = _report_lumen_tet_centres(tip_origin_list)
    elif lc_topo is not None:
        lumen_stats = _report_toposet_centres(TIP_ORIGINS_M)
    if not embed_pts:
        for opt in ("Netgen",):
            try:
                gmsh.model.mesh.optimize(opt)
            except Exception as exc:  # noqa: BLE001
                print(f"WARNING: {opt} optimize skipped ({exc})")

    msh_path.parent.mkdir(parents=True, exist_ok=True)
    gmsh.write(str(msh_path))
    report = {k: len(set(v)) for k, v in groups.items()}
    report["n_theta"] = n_theta
    if tm_layers >= 5:
        report["fluid_tm_layers"] = tm_layers
        report["tm_refined"] = True
        if lc_tm_val is not None:
            report["lc_tm_m"] = lc_tm_val
    if iris_refine:
        report["iris_refined"] = True
        report["lc_iris_m"] = lc_iris
    if vitreous_sym0_refine and sym0_sizes is not None:
        report["vitreous_sym0_refined"] = True
        report["vitreous_sym0_layers"] = VITREOUS_SYM0_LAYERS
        report["lc_vitreous_sym0_m"] = sym0_sizes["lc_mid"]
        report["lc_vitreous_sym0_inner_m"] = sym0_sizes["lc_inner"]
        report["lc_vitreous_sym0_ivi_m"] = sym0_sizes["lc_ivi"]
    if tip_refine and lc_tip is not None:
        report["tip_refined"] = True
        report["tip_sites"] = tip_sites
        report["tip_lc_m"] = lc_tip
        report["tip_r_lumen_m"] = NEEDLE_R_LUMEN_M
        report.update(lumen_stats)
    elif lc_topo is not None:
        report["tip_topo_refined"] = True
        report["tip_lc_topo_m"] = lc_topo
        report["tip_r_toposet_m"] = TOPOSET_TIP_RADIUS_M
        report.update(lumen_stats)
    (msh_path.parent / "patch_groups_g2_fluid.json").write_text(json.dumps(report, indent=2))
    print(f"Wrote {msh_path}")
    print(f"Patch groups: {report}")
    gmsh.finalize()


# Tissue keys in build_g2_anatomy_half that form the solid (not fluid chambers).
G2_SOLID_BANDS = (
    "band_sclera",
    "band_choroid",
    "band_retina",
    "band_cornea",
    "band_ciliary",
    "lens",
    "iris",
)


def mesh_g2_solid(
    anatomy: dict[str, np.ndarray],
    msh_path: Path,
    *,
    mesh_level: str = "M1",
    bands: tuple[str, ...] | None = None,
) -> None:
    """G2 solid tissues: half-bands revolved 90° about +y.

    Multi-zone mesh (one volume per tissue). Patches: symmetry_0/90, outer,
    fsi_active, fsi_iris, fsi_lens, lens_rim (Winkler / zonula).
    """
    import gmsh

    tissue_bands = bands or G2_SOLID_BANDS
    if mesh_level not in MESH_LEVELS:
        raise ValueError(f"unknown mesh_level {mesh_level}")
    sizes = MESH_LEVELS[mesh_level]
    lc_bulk = max(sizes["lc"], 4.0e-4)
    lc_fine = max(sizes["lc_fine"], 1.2e-4)
    n_theta = N_THETA_LEVELS.get(mesh_level, 6)

    missing = [k for k in tissue_bands if k not in anatomy]
    if missing:
        raise RuntimeError(f"anatomy missing solid bands: {missing}")

    gmsh.initialize()
    gmsh.model.add("eye_g2_solid_lamminsalo")
    gmsh.option.setNumber("General.Terminal", 1)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", lc_fine)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", lc_bulk * 1.2)
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.option.setNumber("Mesh.Optimize", 1)
    gmsh.option.setNumber("Mesh.Smoothing", 10)
    gmsh.option.setNumber("Mesh.Algorithm", 6)

    occ = gmsh.model.occ

    def add_ring(pts_m, lc=2.0e-4, n_per_seg: int | None = 3):
        pts = np.asarray(pts_m, dtype=float)
        if n_per_seg:
            pts = densify_polyline(pts, n_per_seg=n_per_seg)
        pts = _clean_ring(pts, tol=1e-9)[:-1]
        if len(pts) > 140:
            idx = np.linspace(0, len(pts) - 1, 140).astype(int)
            pts = pts[idx]
        pts = pts.copy()
        for i, (x, y) in enumerate(pts):
            if abs(x) < 1.0e-6:
                pts[i, 0] = 1.0e-6
        ptags = [occ.addPoint(float(x), float(y), 0.0, lc) for x, y in pts]
        ltags = []
        for i in range(len(ptags)):
            a, b = ptags[i], ptags[(i + 1) % len(ptags)]
            if a != b:
                ltags.append(occ.addLine(a, b))
        return occ.addPlaneSurface([occ.addCurveLoop(ltags)])

    def revolve_ring(name: str) -> list[int]:
        ring = anatomy[name]
        lc = lc_fine if name in ("band_retina", "band_choroid", "iris", "band_cornea") else lc_bulk
        s = add_ring(ring, lc=lc, n_per_seg=2)
        occ.synchronize()
        out = occ.revolve(
            [(2, s)],
            0,
            0,
            0,
            0,
            1,
            0,
            REVOLVE_RAD,
            numElements=[n_theta],
            heights=[1],
            recombine=True,
        )
        occ.synchronize()
        vtags = [e[1] for e in out if e[0] == 3]
        if not vtags:
            raise RuntimeError(f"revolve produced no volume for {name}")
        print(f"INFO: solid {name}: volumes={vtags}")
        return vtags

    volume_by_name: dict[str, list[int]] = {}
    for name in tissue_bands:
        try:
            vtags = revolve_ring(name)
            volume_by_name[name] = vtags
        except Exception as exc:  # noqa: BLE001
            print(f"WARNING: failed to revolve {name}: {exc}")

    if not volume_by_name:
        gmsh.finalize()
        raise RuntimeError("mesh_g2_solid produced no volumes")

    all_vols = [(3, v) for vs in volume_by_name.values() for v in vs]

    # Meridional bounding boxes (x, y) for patch heuristics (+y = optical axis).
    ring_bbox: dict[str, tuple[float, float, float, float]] = {}
    for name in tissue_bands:
        if name not in anatomy:
            continue
        pts = np.asarray(anatomy[name], dtype=float)
        ring_bbox[name] = (pts[:, 0].min(), pts[:, 1].min(), pts[:, 0].max(), pts[:, 1].max())

    def _in_ring_xy(cx: float, cy: float, name: str, margin: float = 4.0e-4) -> bool:
        if name not in ring_bbox:
            return False
        xmin, ymin, xmax, ymax = ring_bbox[name]
        return xmin - margin <= cx <= xmax + margin and ymin - margin <= cy <= ymax + margin

    def _face_bbox(tag: int) -> tuple[float, ...]:
        return gmsh.model.getBoundingBox(2, tag)

    def _face_centroid(tag: int) -> tuple[float, float, float]:
        xmin, ymin, zmin, xmax, ymax, zmax = _face_bbox(tag)
        return (0.5 * (xmin + xmax), 0.5 * (ymin + ymax), 0.5 * (zmin + zmax))

    def _is_lens_rim(cx: float, cy: float, cz: float) -> bool:
        r = math.hypot(cx, cz)
        return _in_ring_xy(cx, cy, "lens", margin=6.0e-4) and 3.4e-3 <= r <= 4.85e-3

    def _is_iris_face(cx: float, cy: float, cz: float) -> bool:
        r = math.hypot(cx, cz)
        return (
            2.5e-3 <= r <= 7.2e-3
            and -5.55e-3 <= cy <= -3.65e-3
            and r >= 4.85e-3
        )

    groups: dict[str, list[int]] = {
        "symmetry_0": [],
        "symmetry_90": [],
        "outer": [],
        "fsi_active": [],
        "fsi_iris": [],
        "fsi_lens": [],
        "lens_rim": [],
    }
    plane_tol = 2.0e-4
    reserved: set[int] = set()
    boundaries = gmsh.model.getBoundary(all_vols, oriented=False)

    for dim, tag in boundaries:
        xmin, ymin, zmin, xmax, ymax, zmax = _face_bbox(tag)
        dx, dy, dz = xmax - xmin, ymax - ymin, zmax - zmin
        if abs(zmin) < plane_tol and abs(zmax) < plane_tol and dx * dy > 1e-12:
            groups["symmetry_0"].append(tag)
            reserved.add(tag)
        elif abs(xmin) < plane_tol and abs(xmax) < plane_tol and dy * dz > 1e-12:
            groups["symmetry_90"].append(tag)
            reserved.add(tag)

    for dim, tag in boundaries:
        if tag in reserved:
            continue
        xmin, ymin, zmin, xmax, ymax, zmax = _face_bbox(tag)
        corners = ((xmin, zmin), (xmin, zmax), (xmax, zmin), (xmax, zmax))
        r_max = max(math.hypot(x, z) for x, z in corners)
        cx, cy, cz = _face_centroid(tag)
        r = math.hypot(cx, cz)

        if r_max >= 7.8e-3:
            groups["outer"].append(tag)
        elif _in_ring_xy(cx, cy, "iris", margin=8.0e-4) or _is_iris_face(cx, cy, cz):
            groups["fsi_iris"].append(tag)
        elif _in_ring_xy(cx, cy, "lens"):
            groups["fsi_lens"].append(tag)
        elif _in_ring_xy(cx, cy, "band_cornea") or _in_ring_xy(cx, cy, "band_retina"):
            groups["fsi_active"].append(tag)
        elif r < 7.6e-3:
            groups["fsi_active"].append(tag)
        else:
            groups["outer"].append(tag)

    # Promote lens-equator faces from fsi_lens → lens_rim (Winkler patch).
    kept_lens: list[int] = []
    for tag in groups["fsi_lens"]:
        cx, cy, cz = _face_centroid(tag)
        if _is_lens_rim(cx, cy, cz):
            groups["lens_rim"].append(tag)
        else:
            kept_lens.append(tag)
    groups["fsi_lens"] = kept_lens

    pid = 1
    zone_report: dict[str, int] = {}
    for name, vtags in volume_by_name.items():
        zname = name.replace("band_", "")
        gmsh.model.addPhysicalGroup(3, vtags, tag=pid, name=zname)
        zone_report[zname] = len(vtags)
        pid += 1

    for name, tags in groups.items():
        utags = sorted(set(tags))
        if not utags:
            print(f"WARNING: empty solid patch '{name}'")
            continue
        gmsh.model.addPhysicalGroup(2, utags, tag=pid, name=name)
        pid += 1

    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", lc_fine)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", lc_bulk)
    gmsh.model.mesh.generate(3)
    try:
        gmsh.model.mesh.optimize("Netgen")
    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: Netgen optimize skipped ({exc})")

    msh_path.parent.mkdir(parents=True, exist_ok=True)
    gmsh.write(str(msh_path))
    gmsh.write(str(msh_path.with_suffix(".vtk")))
    report = {
        "zones": zone_report,
        "patches": {k: len(set(v)) for k, v in groups.items()},
        "n_theta": n_theta,
        "mesh_level": mesh_level,
    }
    (msh_path.parent / "patch_groups_g2_solid.json").write_text(json.dumps(report, indent=2))
    print(f"Wrote {msh_path}")
    print(f"Solid report: {report}")
    gmsh.finalize()


def main():
    ap = argparse.ArgumentParser(description="G2 anatomy + G2-fluid 90° calottes")
    ap.add_argument("--mesh", action="store_true", help="Build G2-fluid revolved mesh")
    ap.add_argument(
        "--mesh-solid",
        action="store_true",
        help="Build G2 solid tissues revolved mesh (sclera/choroid/retina/cornea/ciliary/lens/iris)",
    )
    ap.add_argument(
        "--coat-2d",
        action="store_true",
        help="2D meridional conformal coat (sclera/choroid/retina); optional 3D revolve flags",
    )
    ap.add_argument(
        "--revolve-fluid-2d",
        action="store_true",
        help="Revolve eye_g2_fluid_2d_{level}.msh 90° → eye_g2_fluid_lamminsalo_{level}.msh",
    )
    ap.add_argument(
        "--revolve-solid-2d",
        action="store_true",
        help="Revolve eye_g2_solid_2d_{level}.msh 90° → eye_g2_solid_lamminsalo_{level}.msh",
    )
    ap.add_argument(
        "--structured",
        action="store_true",
        help="Structured meridional quad mesh + 90° revolve (conformal coat interfaces)",
    )
    ap.add_argument(
        "--mesh-level",
        default="M1",
        choices=sorted(MESH_LEVELS),
        help="Size field level for G2 meshes (default M1)",
    )
    ap.add_argument(
        "--tip-refine",
        default="both",
        choices=("ivi", "acp", "both", "none"),
        help="Local 30G tip refinement sites (default both IVI+ACP)",
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
    anatomy = build_g2_anatomy_half(bi)
    fluid = build_g2_fluid_half(bi)

    out_geom.mkdir(parents=True, exist_ok=True)
    out_fig.mkdir(parents=True, exist_ok=True)
    (case / "fluid" / "system").mkdir(parents=True, exist_ok=True)

    # Export rings
    (out_geom / "g2_anatomy_half_m.json").write_text(
        json.dumps({k: np.asarray(v).tolist() for k, v in anatomy.items() if np.asarray(v).ndim == 2})
    )
    (out_geom / "g2_fluid_half_m.json").write_text(
        json.dumps({k: np.asarray(v).tolist() for k, v in fluid.items() if np.asarray(v).ndim == 2})
    )

    # G2 cases own their README/tables; G3 (and others) keep theirs if present
    if args.case.startswith("doc-g2-sim1"):
        write_tables_md(case / "geometry_tables.md")
        write_readme(case / "README.md")
        write_toposet_g2_fluid(
            case / "fluid" / "system" / "topoSetDict.g2",
            tm_markers=bi.get("tm_markers_right"),
        )
    elif args.case.startswith("doc-g2") and not (case / "geometry_tables.md").exists():
        write_tables_md(case / "geometry_tables.md")
        write_toposet_g2_fluid(
            case / "fluid" / "system" / "topoSetDict.g2",
            tm_markers=bi.get("tm_markers_right"),
        )
    elif not (case / "fluid" / "system" / "topoSetDict.g2").exists():
        write_toposet_g2_fluid(
            case / "fluid" / "system" / "topoSetDict.g2",
            tm_markers=bi.get("tm_markers_right"),
        )

    write_geo_stub_anatomy(anatomy, out_geom / "eye_g2_lamminsalo.geo")
    write_geo_stub_fluid(fluid, out_geom / "eye_g2_fluid_lamminsalo.geo")

    # G2 = anatomy (from G1)
    plot_g2_anatomy_half(anatomy, out_fig / "g2_anatomy_half.png")
    plot_g2_anatomy_3d(anatomy, out_fig / "g2_anatomy_3d.png")

    # G2-fluid = fluid (from G1-fluid)
    plot_g2_fluid_half(fluid, out_fig / "g2_fluid_half.png")
    plot_g2_fluid_3d(fluid, out_fig / "g2_fluid_3d.png")

    # Remove obsolete names from the first (wrong) G2 attempt
    for obsolete in (
        out_fig / "g2_half_meridional.png",
        out_fig / "g2_calotte_3d.png",
        out_geom / "eye_g2_lamminsalo.msh",
        out_geom / "eye_g2_lamminsalo.vtk",
        out_geom / "eye_g2_lamminsalo_M1.msh",
        out_geom / "eye_g2_lamminsalo_M1.vtk",
        out_geom / "half_rings_m.json",
        out_geom / "patch_groups_g2.json",
    ):
        if obsolete.exists():
            obsolete.unlink()
            print(f"Removed obsolete {obsolete.name}")

    if args.coat_2d:
        msh_solid = out_geom / f"eye_g2_solid_2d_{args.mesh_level}.msh"
        msh_fluid = out_geom / f"eye_g2_fluid_2d_{args.mesh_level}.msh"
        from g2_fluid_2d import mesh_g2_coat_2d_pair

        mesh_g2_coat_2d_pair(bi, fluid, msh_solid, msh_fluid, mesh_level=args.mesh_level)
        plot_fluid = case / "scripts" / "plot_fluid_2d.py"
        if plot_fluid.exists():
            subprocess.run(
                [sys.executable, str(plot_fluid), "--mesh-level", args.mesh_level],
                check=True,
            )
        if args.revolve_fluid_2d:
            msh_3d = out_geom / f"eye_g2_fluid_lamminsalo_{args.mesh_level}.msh"
            from g2_fluid_2d_revolve import revolve_fluid_2d_file

            revolve_fluid_2d_file(msh_fluid, msh_3d, mesh_level=args.mesh_level)
            shutil.copy2(msh_3d, out_geom / "eye_g2_fluid_lamminsalo.msh")
            plot_cut = case / "scripts" / "plot_g2_fluid_mesh.py"
            if plot_cut.exists():
                subprocess.run(
                    [sys.executable, str(plot_cut), "--mesh-level", args.mesh_level],
                    check=True,
                )
        if args.revolve_solid_2d:
            msh_3d_s = out_geom / f"eye_g2_solid_lamminsalo_{args.mesh_level}.msh"
            from g2_solid_2d_revolve import revolve_solid_2d_file

            revolve_solid_2d_file(msh_solid, msh_3d_s, mesh_level=args.mesh_level)
            shutil.copy2(msh_3d_s, out_geom / "eye_g2_solid_lamminsalo.msh")
    elif args.revolve_solid_2d:
        msh_solid = out_geom / f"eye_g2_solid_2d_{args.mesh_level}.msh"
        msh_3d_s = out_geom / f"eye_g2_solid_lamminsalo_{args.mesh_level}.msh"
        from g2_solid_2d_revolve import revolve_solid_2d_file

        revolve_solid_2d_file(msh_solid, msh_3d_s, mesh_level=args.mesh_level)
        shutil.copy2(msh_3d_s, out_geom / "eye_g2_solid_lamminsalo.msh")
    elif args.revolve_fluid_2d:
        msh_fluid = out_geom / f"eye_g2_fluid_2d_{args.mesh_level}.msh"
        msh_3d = out_geom / f"eye_g2_fluid_lamminsalo_{args.mesh_level}.msh"
        from g2_fluid_2d_revolve import revolve_fluid_2d_file

        revolve_fluid_2d_file(msh_fluid, msh_3d, mesh_level=args.mesh_level)
        shutil.copy2(msh_3d, out_geom / "eye_g2_fluid_lamminsalo.msh")
        if args.case.startswith("doc-g2-sim"):
            sync_case_topo_sets(REPO)
        plot_cut = case / "scripts" / "plot_g2_fluid_mesh.py"
        if plot_cut.exists():
            subprocess.run(
                [sys.executable, str(plot_cut), "--mesh-level", args.mesh_level],
                check=True,
            )
    elif args.structured and args.mesh and args.mesh_solid:
        msh_f = out_geom / f"eye_g2_fluid_lamminsalo_{args.mesh_level}.msh"
        msh_s = out_geom / f"eye_g2_solid_lamminsalo_{args.mesh_level}.msh"
        mesh_g2_fsi_conformal_pair(
            bi, fluid, anatomy, msh_f, msh_s, mesh_level=args.mesh_level,
        )
        shutil.copy2(msh_f, out_geom / "eye_g2_fluid_lamminsalo.msh")
        shutil.copy2(msh_s, out_geom / "eye_g2_solid_lamminsalo.msh")
        coat = out_geom / f"eye_g2_solid_coat_struct_{args.mesh_level}.msh"
        mesh_g2_solid_structured(bi, anatomy, coat, mesh_level=args.mesh_level, merged=False)
    elif args.mesh:
        msh = out_geom / f"eye_g2_fluid_lamminsalo_{args.mesh_level}.msh"
        tip_refine = args.tip_refine != "none"
        tip_sites = args.tip_refine if tip_refine else "both"
        if args.structured:
            mesh_g2_fluid_structured(
                bi,
                fluid,
                msh,
                mesh_level=args.mesh_level,
                tip_refine=tip_refine,
                tip_sites=tip_sites,
            )
        else:
            mesh_g2_fluid(
                fluid,
                msh,
                mesh_level=args.mesh_level,
                tip_refine=tip_refine,
                tip_sites=tip_sites,
            )
        shutil.copy2(msh, out_geom / "eye_g2_fluid_lamminsalo.msh")
        vtk = msh.with_suffix(".vtk")
        if vtk.exists():
            shutil.copy2(vtk, out_geom / "eye_g2_fluid_lamminsalo.vtk")
        if args.case.startswith("doc-g2-sim"):
            sync_case_topo_sets(REPO)
            sync_g2_fluid_split_patches(args.case)
            print("INFO: synced topoSetDict.iviTip / acpTip (30G lumen) to doc-g2-sim2–4")

    elif args.mesh_solid:
        if args.structured:
            msh = out_geom / f"eye_g2_solid_lamminsalo_{args.mesh_level}.msh"
            mesh_g2_solid_structured(bi, anatomy, msh, mesh_level=args.mesh_level, merged=True)
            shutil.copy2(msh, out_geom / "eye_g2_solid_lamminsalo.msh")
            vtk = msh.with_suffix(".vtk")
            if vtk.exists():
                shutil.copy2(vtk, out_geom / "eye_g2_solid_lamminsalo.vtk")
            coat = out_geom / f"eye_g2_solid_coat_struct_{args.mesh_level}.msh"
            mesh_g2_solid_structured(bi, anatomy, coat, mesh_level=args.mesh_level, merged=False)
        else:
            msh = out_geom / f"eye_g2_solid_lamminsalo_{args.mesh_level}.msh"
            mesh_g2_solid(anatomy, msh, mesh_level=args.mesh_level)
            shutil.copy2(msh, out_geom / "eye_g2_solid_lamminsalo.msh")
            vtk = msh.with_suffix(".vtk")
            if vtk.exists():
                shutil.copy2(vtk, out_geom / "eye_g2_solid_lamminsalo.vtk")

    print(f"Done. Case: {case}")
    print("  G2        = anatomy (from G1)       → figures/g2_anatomy_*")
    print("  G2-fluid  = fluid   (from G1-fluid) → figures/g2_fluid_*")
    if args.mesh_solid:
        print("  G2-solid  = tissue shells + lens/iris → geometry/eye_g2_solid_*")


if __name__ == "__main__":
    main()
