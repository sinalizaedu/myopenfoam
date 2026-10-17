#!/usr/bin/env python3
"""Plot the O1 Lamminsalo structured solid mesh, coloured by tissue cellZone.

The 90 deg wedge is sliced on its exact ``symmetry_0`` plane (x = 0 after
``transformPoints -rotate-y 90``), so every drawn quad is a real mesh face
rather than an interpolated cut. Radial coordinate is -z, axial is y.
"""

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

REPO = Path(__file__).resolve().parents[1]

ZONE_STYLE = {
    "sclera": ("#d8cbb4", "sclera (0.33 mm)"),
    "choroid": ("#a93226", "choroid (0.20 mm)"),
    "retina": ("#f1948a", "retina (0.10 mm)"),
    "cornea": ("#aed6f1", "cornea (0.36 mm)"),
    "ciliary": ("#7dcea0", "ciliary body"),
    "lens": ("#f7dc6f", "lens"),
    "iris": ("#bb8fce", "iris"),
}

FSI_PATCH_STYLE = {
    "fsi_active": ("#0b3d91", "fsi_active (main wall interface)"),
    "fsi_lens": ("#e67e22", "fsi_lens"),
    "fsi_iris": ("#8e44ad", "fsi_iris"),
}

EDGE_COLOR = "#8fa0ad"


def _strip_header(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"//[^\n]*", "", text)
    m = re.search(r"\bFoamFile\s*\{", text)
    if m is None:
        return text
    depth, i = 1, m.end()
    while i < len(text) and depth > 0:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    return text[: m.start()] + text[i:]


def read_points(path: Path) -> np.ndarray:
    body = _strip_header(path.read_text())
    m = re.search(r"(\d+)\s*\(", body)
    count = int(m.group(1))
    vals = np.fromstring(
        body[m.end():].replace("(", " ").replace(")", " "), sep=" "
    )
    arr = vals[: 3 * count].reshape(-1, 3)
    if arr.shape[0] != count:
        raise ValueError(f"points: expected {count}, got {arr.shape[0]}")
    return arr


def read_faces(path: Path) -> list[np.ndarray]:
    body = _strip_header(path.read_text())
    m = re.search(r"(\d+)\s*\(", body)
    count = int(m.group(1))
    faces = [
        np.fromstring(g, dtype=np.int64, sep=" ")
        for g in re.findall(r"\d+\s*\(([^)]*)\)", body[m.end():])
    ]
    if len(faces) != count:
        raise ValueError(f"faces: expected {count}, got {len(faces)}")
    return faces


def read_labels(path: Path) -> np.ndarray:
    body = _strip_header(path.read_text())
    m = re.search(r"(\d+)\s*\(", body)
    count = int(m.group(1))
    end = body.index(")", m.end())
    arr = np.fromstring(body[m.end():end], dtype=np.int64, sep=" ")
    if arr.size != count:
        raise ValueError(f"{path.name}: expected {count}, got {arr.size}")
    return arr


def read_cell_zones(path: Path, n_cells: int) -> tuple[np.ndarray, list[str]]:
    """Return per-cell zone index (-1 if unzoned) and the ordered zone names."""
    body = _strip_header(path.read_text())
    zone_of_cell = np.full(n_cells, -1, dtype=np.int64)
    names: list[str] = []
    pattern = re.compile(
        r"(\w+)\s*\{[^{}]*?cellLabels\s+List<label>\s*(\d+)\s*\(([^)]*)\)", re.S
    )
    for m in pattern.finditer(body):
        name, n_str, payload = m.group(1), m.group(2), m.group(3)
        labels = np.fromstring(payload, dtype=np.int64, sep=" ")
        if labels.size != int(n_str):
            raise ValueError(f"zone {name}: expected {n_str}, got {labels.size}")
        zone_of_cell[labels] = len(names)
        names.append(name)
    return zone_of_cell, names


def read_boundary(path: Path) -> dict[str, tuple[int, int]]:
    body = _strip_header(path.read_text())
    out: dict[str, tuple[int, int]] = {}
    for m in re.finditer(
        r"(\w+)\s*\{[^{}]*?nFaces\s+(\d+);[^{}]*?startFace\s+(\d+);[^{}]*?\}", body, re.S
    ):
        out[m.group(1)] = (int(m.group(3)), int(m.group(2)))
    return out


def _ordered_quad(p2: np.ndarray) -> np.ndarray:
    """Sort polygon vertices by angle so PolyCollection draws a convex quad."""
    c = p2.mean(axis=0)
    ang = np.arctan2(p2[:, 1] - c[1], p2[:, 0] - c[0])
    return p2[np.argsort(ang)]


def _meridional_xy(p: np.ndarray) -> np.ndarray:
    """Radial–axial coords [mm] for any wedge orientation (x=0 or z=0 symmetry)."""
    r = np.hypot(p[:, 0], p[:, 2]) * 1e3
    y = p[:, 1] * 1e3
    return np.column_stack([r, y])


def _faces_on_plane(
    points: np.ndarray, faces: list[np.ndarray], axis: int, *, tol: float
) -> list[int]:
    return [
        fi
        for fi, idx in enumerate(faces)
        if np.all(np.abs(points[idx][:, axis]) < tol)
    ]


def _median_quad_span(
    points: np.ndarray, faces: list[np.ndarray], face_indices: list[int]
) -> float:
    spans: list[float] = []
    for fi in face_indices[: min(500, len(face_indices))]:
        p2 = _meridional_xy(points[faces[fi]])
        spans.append(float(max(np.ptp(p2[:, 0]), np.ptp(p2[:, 1]))))
    return float(np.median(spans)) if spans else 0.0


def _pick_slice_plane(
    points: np.ndarray,
    faces: list[np.ndarray],
    patches: dict[str, tuple[int, int]],
    *,
    plane_tol: float,
) -> tuple[list[int], int]:
    """Return face indices on the best meridional plane and its axis (0=x, 2=z)."""
    if "symmetry_0" in patches:
        start, n = patches["symmetry_0"]
        return list(range(start, start + n)), 0

    # Extruded coat (A1): wedge lies on z = 0; rotated solids (B2) on x = 0.
    loose_tol = max(plane_tol, 1.0e-5)
    candidates: list[tuple[float, list[int], int]] = []
    for axis in (0, 2):
        slice_faces = _faces_on_plane(points, faces, axis, tol=loose_tol)
        if not slice_faces:
            continue
        span = _median_quad_span(points, faces, slice_faces)
        candidates.append((span, slice_faces, axis))

    if not candidates:
        return [], 0

    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1], candidates[0][2]


def build_slice(polymesh: Path, *, plane_tol: float = 1.0e-9):
    points = read_points(polymesh / "points")
    faces = read_faces(polymesh / "faces")
    owner = read_labels(polymesh / "owner")
    n_cells = int(owner.max()) + 1
    zone_of_cell, zone_names = read_cell_zones(polymesh / "cellZones", n_cells)
    patches = read_boundary(polymesh / "boundary")

    zone_cells = {
        nm: int((zone_of_cell == i).sum()) for i, nm in enumerate(zone_names)
    }

    slice_faces, plane_axis = _pick_slice_plane(
        points, faces, patches, plane_tol=plane_tol
    )
    on_plane_tol = max(plane_tol, 1.0e-5)

    def _face_poly(fi: int) -> tuple[np.ndarray, int]:
        idx = faces[fi]
        p2 = _meridional_xy(points[idx])
        return p2, int(zone_of_cell[owner[fi]])

    polys_by_zone: dict[str, list[np.ndarray]] = {nm: [] for nm in zone_names}
    for f in slice_faces:
        p2, zi = _face_poly(f)
        if zi < 0:
            continue
        polys_by_zone[zone_names[zi]].append(_ordered_quad(p2))

    # Traces of coupling patches on the meridional slice plane.
    fsi_segs: dict[str, list[np.ndarray]] = {}
    for name in FSI_PATCH_STYLE:
        if name not in patches:
            continue
        s, cnt = patches[name]
        segs: list[np.ndarray] = []
        for f in range(s, s + cnt):
            idx = faces[f]
            on = np.abs(points[idx][:, plane_axis]) < on_plane_tol
            k = len(idx)
            for i in range(k):
                a, b = i, (i + 1) % k
                if on[a] and on[b]:
                    pa = _meridional_xy(points[idx[a]][None, :])[0]
                    pb = _meridional_xy(points[idx[b]][None, :])[0]
                    segs.append(np.array([pa, pb]))
        fsi_segs[name] = segs

    return points, polys_by_zone, fsi_segs, n_cells, len(faces), zone_cells


def zone_bbox_report(polys_by_zone: dict[str, list[np.ndarray]]) -> str:
    lines = []
    for name, polys in polys_by_zone.items():
        if not polys:
            lines.append(f"{name:8s}  (no faces on slice plane)")
            continue
        a = np.concatenate(polys, axis=0)
        lines.append(
            f"{name:8s}  r=[{a[:, 0].min():7.3f},{a[:, 0].max():7.3f}] mm   "
            f"y=[{a[:, 1].min():7.3f},{a[:, 1].max():7.3f}] mm   "
            f"{len(polys):5d} slice faces"
        )
    return "\n".join(lines)


def _draw(ax, polys_by_zone, fsi_segs, *, lw: float, fsi_lw: float = 2.2) -> None:
    """Draw the slice. The y axis is inverted so anterior (cornea) points up."""
    for name, polys in polys_by_zone.items():
        if not polys:
            continue
        face, _ = ZONE_STYLE.get(name, ("#cccccc", name))
        ax.add_collection(
            PolyCollection(
                polys,
                facecolors=face,
                edgecolors=EDGE_COLOR,
                linewidths=lw,
                alpha=0.95,
            )
        )
    for name, segs in fsi_segs.items():
        if not segs:
            continue
        color, _ = FSI_PATCH_STYLE[name]
        ax.add_collection(
            LineCollection(segs, colors=color, linewidths=fsi_lw, zorder=5)
        )
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("radial  -z  [mm]", fontsize=8)
    ax.set_ylabel("axial  y  [mm]  (up = anterior)", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.grid(True, alpha=0.2, zorder=0)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--polymesh",
        type=Path,
        default=REPO / "cases/fsi-baseline-o1-volume-fluid/solid/constant/polyMesh",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO / "cases/fsi-baseline-o1-volume-fluid/figures/o1_solid_mesh.png",
    )
    ap.add_argument("--case-label", default="fsi-baseline-o1-volume-fluid")
    args = ap.parse_args()

    points, polys_by_zone, fsi_segs, n_cells, n_faces, zone_cells = build_slice(
        args.polymesh
    )
    print(zone_bbox_report(polys_by_zone))
    print()
    for nm, nc in sorted(zone_cells.items(), key=lambda kv: -kv[1]):
        print(f"{nm:8s} {nc:6d} cells  ({100.0 * nc / n_cells:5.1f} % of solid)")
    print()
    for name, segs in fsi_segs.items():
        print(f"{name:12s} {len(segs)} slice edges")

    allp = np.concatenate([p for v in polys_by_zone.values() for p in v], axis=0)
    r0, r1 = allp[:, 0].min(), allp[:, 0].max()
    y0, y1 = allp[:, 1].min(), allp[:, 1].max()
    pad = 0.04

    fig = plt.figure(figsize=(17, 10.5), dpi=170, facecolor="white")
    gs = fig.add_gridspec(2, 3, width_ratios=[1.5, 1, 1], wspace=0.24, hspace=0.16)

    ax_full = fig.add_subplot(gs[:, 0])
    _draw(ax_full, polys_by_zone, fsi_segs, lw=0.18)
    ax_full.set_xlim(r0 - pad * (r1 - r0), r1 + pad * (r1 - r0))
    ax_full.set_ylim(y1 + pad * (y1 - y0), y0 - pad * (y1 - y0))
    ax_full.set_title(
        "Meridional slice on x = 0 — tissue zones", fontsize=10
    )

    zooms = (
        (gs[0, 1], (5.8, 7.8), (-5.4, -3.6), "Limbus / TM-back / ciliary"),
        (gs[0, 2], (-0.2, 4.3), (-8.9, -4.7), "Cornea apex + lens front"),
        (gs[1, 1], (7.4, 9.2), (-2.9, -0.9), "Ora: ciliary -> retina/choroid junction"),
        (gs[1, 2], (-0.2, 3.6), (5.6, 7.8), "Posterior pole: posterior coat"),
    )
    for spec, xlim, ylim, title in zooms:
        ax = fig.add_subplot(spec)
        _draw(ax, polys_by_zone, fsi_segs, lw=0.45, fsi_lw=1.8)
        ax.set_xlim(*xlim)
        ax.set_ylim(ylim[1], ylim[0])
        ax.set_title(title, fontsize=9)

    handles = [
        Patch(
            facecolor=ZONE_STYLE[n][0],
            edgecolor="#2c3e50",
            label=f"{ZONE_STYLE[n][1]} — {zone_cells[n]:,} cells "
            f"({100.0 * zone_cells[n] / n_cells:.0f} %)",
        )
        for n in ZONE_STYLE
        if polys_by_zone.get(n)
    ]
    handles += [
        plt.Line2D([], [], color=FSI_PATCH_STYLE[n][0], lw=2.2, label=FSI_PATCH_STYLE[n][1])
        for n, s in fsi_segs.items()
        if s
    ]
    ax_full.legend(handles=handles, loc="upper right", fontsize=7.5, framealpha=0.95)

    fig.suptitle(
        f"{args.case_label} — solid mesh (90 deg wedge) · {n_cells:,} cells · "
        f"{n_faces:,} faces · {len(points):,} points\n"
        "blockMeshDict.O1solid, Lamminsalo tissue boundaries, after "
        "transformPoints -rotate-y 90",
        fontsize=11,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
