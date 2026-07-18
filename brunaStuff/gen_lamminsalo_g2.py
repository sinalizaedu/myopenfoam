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
  .venv-geom/bin/python brunaStuff/gen_lamminsalo_g2.py --mesh-anatomy  # G2 multi-volume (experimental)
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
# Right-half rings (meridional plane z = 0, x ≥ 0)
# ---------------------------------------------------------------------------
def build_half_ac_m(bi: dict[str, np.ndarray]) -> np.ndarray:
    """Closed right-half AC ∪ TM (cornea → TM → iris margin → hyaloid → lens front → axis)."""
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
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.2, 8.0))
    mm = 1.0e3

    def fill(pts, color, label, alpha=0.40):
        p = np.asarray(pts) * mm
        ax.fill(p[:, 0], p[:, 1], color=color, alpha=alpha, label=label, linewidth=0)

    def stroke(pts, **kw):
        p = np.asarray(pts) * mm
        ax.plot(p[:, 0], p[:, 1], **kw)

    fill(fluid["band_ac_half"], "#7ec8c8", "AC ∪ TM (half)", alpha=0.45)
    fill(fluid["band_vitreous_half"], "#6fa8dc", "Vitreous (half)", alpha=0.45)
    fill(fluid["iris_half"], "#c0392b", "Iris (hole)", alpha=0.55)
    fill(fluid["lens_half"], "#2d6a4f", "Lens (hole)", alpha=0.55)

    stroke(fluid["cornea_inside_right"], color="#e67e22", lw=1.2, label="Cornea inside")
    stroke(fluid["vitreous_retina_right"], color="#2874a6", lw=1.2, label="Vitreous–retina")
    stroke(fluid["hyaloid_right"], color="#8e44ad", lw=1.2, label="Hyaloid")
    stroke(fluid["tm_markers_right"], color="#d35400", lw=1.4, marker="o", ms=3, label="TM")

    ax.axvline(0.0, color="0.35", ls="--", lw=0.9, label="Optical axis (revolve)")
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x [mm]  (radial, half-domain x ≥ 0)")
    ax.set_ylabel("y [mm]  (optical axis, + posterior)")
    ax.set_title(
        "G2-fluid — meridional half (from G1-fluid)\n"
        f"AC / vitreous / TM · revolve {REVOLVE_DEG:.0f}° about +y"
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


def write_toposet_g2_fluid(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tm = PTS["tm_cornea_void"]
    t2 = PTS["tm_ciliary_void"]
    pad = 2.5e-4
    x0 = min(tm[0], t2[0]) * M_PER_CM - pad
    x1 = max(tm[0], t2[0]) * M_PER_CM + pad
    y0 = min(tm[1], t2[1]) * M_PER_CM - pad
    y1 = max(tm[1], t2[1]) * M_PER_CM + pad
    z1 = x1
    path.write_text(
        f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      topoSetDict;
}}

// G2-fluid 90° calotte cellZones (from G1-fluid)
// TM: single sector. pad={pad:.1e} m.

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
    )
    print(f"Wrote {path}")


# ---------------------------------------------------------------------------
# Gmsh — G2-fluid mesh
# ---------------------------------------------------------------------------
def mesh_g2_fluid(
    fluid: dict[str, np.ndarray],
    msh_path: Path,
    *,
    mesh_level: str = "M1",
) -> None:
    """G2-fluid: (AC ∪ vitreous ∪ TM)_half − iris, revolved 90° about +y."""
    import gmsh

    if mesh_level not in MESH_LEVELS:
        raise ValueError(f"unknown mesh_level {mesh_level}")
    sizes = MESH_LEVELS[mesh_level]
    lc_bulk = max(sizes["lc"], 4.0e-4)
    lc_fine = sizes["lc_fine"]

    gmsh.initialize()
    gmsh.model.add("eye_g2_fluid_lamminsalo")
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

    s_ac = add_ring(fluid["band_ac_half"], lc=lc_fine, n_per_seg=3)
    s_vit = add_ring(fluid["band_vitreous_half"], lc=lc_bulk, n_per_seg=3)
    fused = occ.fuse([(2, s_ac)], [(2, s_vit)], removeObject=True, removeTool=True)
    occ.synchronize()
    if not fused[0]:
        raise RuntimeError("OCC fuse AC∪vitreous (half) produced nothing")

    iris = densify_polyline(fluid["iris_half"], n_per_seg=8)
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

    print(f"INFO: G2-fluid faces before revolve: {len(fluid_surfaces)}")

    out = occ.revolve(fluid_surfaces, 0, 0, 0, 0, 1, 0, REVOLVE_RAD)
    occ.synchronize()
    volume_tags = [e[1] for e in out if e[0] == 3]
    if not volume_tags:
        raise RuntimeError("No revolved volume")

    groups: dict[str, list[int]] = {
        "symmetry_0": [],
        "symmetry_90": [],
        "ac_inlet": [],
        "outlet_tm": [],
        "lens_wall": [],
        "iris_wall": [],
        "wall": [],
    }

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
        r = math.hypot(cx, cz)

        if abs(zmin) < plane_tol and abs(zmax) < plane_tol and dx * dy > 1e-12:
            groups["symmetry_0"].append(tag)
            continue
        if abs(xmin) < plane_tol and abs(xmax) < plane_tol and dy * dz > 1e-12:
            groups["symmetry_90"].append(tag)
            continue
        if max(dx, dy, dz) < 1e-7:
            continue

        if on_tm_se_face(r, cy):
            groups["outlet_tm"].append(tag)
        elif on_ac_inlet(r, cy):
            groups["ac_inlet"].append(tag)
        elif r < 4.5e-3 and -0.0065 < cy < 0.0015:
            groups["lens_wall"].append(tag)
        elif 2.5e-3 < r < 7.2e-3 and -0.0056 < cy < -0.0036:
            groups["iris_wall"].append(tag)
        else:
            groups["wall"].append(tag)

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
    (msh_path.parent / "patch_groups_g2_fluid.json").write_text(json.dumps(report, indent=2))
    print(f"Wrote {msh_path}")
    print(f"Patch groups: {report}")
    gmsh.finalize()


def main():
    ap = argparse.ArgumentParser(description="G2 anatomy + G2-fluid 90° calottes")
    ap.add_argument("--mesh", action="store_true", help="Build G2-fluid revolved mesh")
    ap.add_argument(
        "--mesh-level",
        default="M1",
        choices=sorted(MESH_LEVELS),
        help="Size field level for G2-fluid (default M1)",
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

    write_tables_md(case / "geometry_tables.md")
    write_readme(case / "README.md")
    write_toposet_g2_fluid(case / "fluid" / "system" / "topoSetDict.g2")
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

    if args.mesh:
        msh = out_geom / f"eye_g2_fluid_lamminsalo_{args.mesh_level}.msh"
        mesh_g2_fluid(fluid, msh, mesh_level=args.mesh_level)
        shutil.copy2(msh, out_geom / "eye_g2_fluid_lamminsalo.msh")
        vtk = msh.with_suffix(".vtk")
        if vtk.exists():
            shutil.copy2(vtk, out_geom / "eye_g2_fluid_lamminsalo.vtk")

    print(f"Done. Case: {case}")
    print("  G2        = anatomy (from G1)       → figures/g2_anatomy_*")
    print("  G2-fluid  = fluid   (from G1-fluid) → figures/g2_fluid_*")


if __name__ == "__main__":
    main()
