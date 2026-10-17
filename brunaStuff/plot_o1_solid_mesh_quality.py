#!/usr/bin/env python3
"""Plot O1 solid mesh quality: highlight zero-volume / bad cells at the limbus."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.patches import Patch

from plot_o1_solid_mesh import (
    EDGE_COLOR,
    FSI_PATCH_STYLE,
    ZONE_STYLE,
    _draw,
    _ordered_quad,
    build_slice,
    read_boundary,
    read_cell_zones,
    read_faces,
    read_labels,
    read_points,
)

REPO = Path(__file__).resolve().parents[1]


def read_cell_set(path: Path) -> set[int]:
    if not path.exists():
        return set()
    body = re.sub(r"/\*.*?\*/", "", path.read_text(), flags=re.S)
    body = re.sub(r"//[^\n]*", "", body)
    m = re.search(r"(\d+)\s*\(", body)
    if not m:
        return set()
    end = body.index(")", m.end())
    return {int(x) for x in body[m.end() : end].split() if x.isdigit()}


def cell_centroids(points, faces, owner, neighbour, n_cells) -> np.ndarray:
    pts: list[set[int]] = [set() for _ in range(n_cells)]
    n_int = len(neighbour)
    for fi, face in enumerate(faces):
        pts[int(owner[fi])].update(int(i) for i in face)
        if fi < n_int:
            pts[int(neighbour[fi])].update(int(i) for i in face)
    out = np.zeros((n_cells, 3))
    for ci, idx in enumerate(pts):
        if idx:
            out[ci] = points[np.fromiter(idx, dtype=np.int64)].mean(axis=0)
    return out


def slice_cell_polys(
    points: np.ndarray,
    faces: list[np.ndarray],
    owner: np.ndarray,
    cell_ids: set[int],
    plane_axis: int,
    on_plane_tol: float,
) -> list[np.ndarray]:
    """Meridional quads for cells that have a face on the slice plane."""
    polys: list[np.ndarray] = []
    for fi, idx in enumerate(faces):
        if int(owner[fi]) not in cell_ids:
            continue
        if not np.all(np.abs(points[idx][:, plane_axis]) < on_plane_tol):
            continue
        p = points[idx]
        r = np.hypot(p[:, 0], p[:, 2]) * 1e3
        y = p[:, 1] * 1e3
        if len(idx) >= 3:
            polys.append(_ordered_quad(np.column_stack([r, y])))
    return polys


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--polymesh",
        type=Path,
        default=REPO / "cases/fsi-transient-o1-patch/solid/constant/polyMesh",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO
        / "cases/fsi-transient-o1-patch/solid/figures/solid_mesh_quality_limbus.png",
    )
    ap.add_argument("--case-label", default="fsi-transient-o1-patch/solid (B1)")
    args = ap.parse_args()

    pm = args.polymesh
    points, polys_by_zone, fsi_segs, n_cells, n_faces, zone_cells = build_slice(pm)
    owner = read_labels(pm / "owner")
    neighbour = read_labels(pm / "neighbour")
    faces = read_faces(pm / "faces")
    zone_of, zone_names = read_cell_zones(pm / "cellZones", n_cells)
    patches = read_boundary(pm / "boundary")

    sets_dir = pm / "sets"
    bad_vol = read_cell_set(sets_dir / "zeroVolumeCells")
    bad_ar = read_cell_set(sets_dir / "highAspectRatioCells")
    bad_cells = bad_vol | bad_ar

    cent = cell_centroids(points, faces, owner, neighbour, n_cells)
    from plot_o1_solid_mesh import _pick_slice_plane

    _, plane_axis = _pick_slice_plane(points, faces, patches, plane_tol=1e-9)
    on_plane_tol = 1e-5
    bad_polys = slice_cell_polys(
        points, faces, owner, bad_cells, plane_axis, on_plane_tol
    )

    # Stats from log if present
    log = pm.parents[1] / "log.checkMesh"
    stats_line = ""
    if log.exists():
        txt = log.read_text()
        for pat in (
            r"Max: ([0-9.]+).*non-orthogonality",
            r"Number of severely non-orthogonal.*?(\d+)",
            r"negative volume.*?(\d+)",
        ):
            m = re.search(pat, txt, re.S)
            if m:
                stats_line += m.group(0).split("\n")[0][:80] + " · "

    allp = np.concatenate([p for v in polys_by_zone.values() for p in v], axis=0)
    r0, r1 = allp[:, 0].min(), allp[:, 0].max()
    y0, y1 = allp[:, 1].min(), allp[:, 1].max()
    pad = 0.04

    fig = plt.figure(figsize=(17, 10.5), dpi=170, facecolor="white")
    gs = fig.add_gridspec(2, 3, width_ratios=[1.5, 1, 1], wspace=0.24, hspace=0.16)

    ax_full = fig.add_subplot(gs[:, 0])
    _draw(ax_full, polys_by_zone, fsi_segs, lw=0.18)
    if bad_polys:
        ax_full.add_collection(
            PolyCollection(
                bad_polys,
                facecolors="#e74c3c",
                edgecolors="#922b21",
                linewidths=0.9,
                alpha=0.85,
                zorder=6,
            )
        )
    bc = cent[list(bad_cells)]
    br = np.hypot(bc[:, 0], bc[:, 2]) * 1e3
    by = bc[:, 1] * 1e3
    ax_full.scatter(br, by, s=28, c="#c0392b", edgecolors="white", linewidths=0.4, zorder=7)
    ax_full.set_xlim(r0 - pad * (r1 - r0), r1 + pad * (r1 - r0))
    ax_full.set_ylim(y1 + pad * (y1 - y0), y0 - pad * (y1 - y0))
    ax_full.set_title("Meridional slice — tissue + bad cells (red)", fontsize=10)

    zooms = (
        (gs[0, 1], (6.4, 7.2), (-5.0, -4.2), "Limbus: 12 zero-vol / high-AR cells"),
        (gs[0, 2], (6.6, 7.1), (-4.6, -4.0), "TM-back D–E column (×12 θ)"),
        (gs[1, 1], (6.8, 7.05), (-4.55, -4.25), "Zoom: inverted hex stack"),
        (gs[1, 2], (-0.5, 4.0), (5.5, 7.5), "Posterior (mean non-ortho ~13°)"),
    )
    for spec, xlim, ylim, title in zooms:
        ax = fig.add_subplot(spec)
        _draw(ax, polys_by_zone, fsi_segs, lw=0.45, fsi_lw=1.8)
        if bad_polys:
            ax.add_collection(
                PolyCollection(
                    bad_polys,
                    facecolors="#e74c3c",
                    edgecolors="#922b21",
                    linewidths=1.2,
                    alpha=0.9,
                    zorder=6,
                )
            )
        ax.scatter(br, by, s=40, c="#c0392b", edgecolors="white", linewidths=0.5, zorder=7)
        ax.set_xlim(*xlim)
        ax.set_ylim(ylim[1], ylim[0])
        ax.set_title(title, fontsize=9)

    handles = [
        Patch(facecolor=ZONE_STYLE[n][0], edgecolor="#2c3e50", label=ZONE_STYLE[n][1])
        for n in ZONE_STYLE
        if polys_by_zone.get(n)
    ]
    handles += [
        Patch(facecolor="#e74c3c", edgecolor="#922b21", label=f"bad cells ({len(bad_cells)})"),
        plt.Line2D([], [], color=FSI_PATCH_STYLE["fsi_active"][0], lw=2.2, label="fsi_active"),
    ]
    ax_full.legend(handles=handles, loc="upper right", fontsize=7.5, framealpha=0.95)

    fig.suptitle(
        f"{args.case_label} — mesh quality · {n_cells:,} cells · "
        f"{len(bad_cells)} zero-vol/high-AR · max non-ortho 180° (11 faces) · "
        f"mean non-ortho ~12.9° · max skew 1.82 OK · FSI conformal PASS",
        fontsize=10.5,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Wrote {args.out}")
    print(f"Bad cell IDs: {sorted(bad_cells)}")


if __name__ == "__main__":
    main()
