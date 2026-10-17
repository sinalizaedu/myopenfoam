#!/usr/bin/env python3
"""Plot O1 blockMesh fluid domain from OpenFOAM polyMesh.

Meridional slab cut (|x| < slab_half) projected to (z, y), plus TM and IVI zooms.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "brunaStuff"))
from g2_needle import ACP_TIP_ORIGIN_M, IVI_TIP_ORIGIN_M, TOPOSET_TIP_RADIUS_M


def _strip_header(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"//[^\n]*", "", text)
    m = re.search(r"\bFoamFile\s*\{", text)
    if m is None:
        return text
    depth = 1
    i = m.end()
    while i < len(text) and depth > 0:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    return text[: m.start()] + text[i:]


def _read_count_list(text: str, item_parser):
    m = re.search(r"(\d+)\s*\(", text)
    if not m:
        raise ValueError("expected count + ( ... ) list")
    count = int(m.group(1))
    start = m.end()
    depth = 1
    i = start
    while i < len(text) and depth > 0:
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
        i += 1
    return item_parser(text[start : i - 1], count)


def read_points(path: Path) -> np.ndarray:
    text = _strip_header(path.read_text())

    def parse(body: str, count: int) -> np.ndarray:
        vals = [float(x) for x in re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", body)]
        arr = np.asarray(vals, dtype=np.float64).reshape(-1, 3)
        if arr.shape[0] != count:
            raise ValueError(f"points: expected {count}, got {arr.shape[0]}")
        return arr

    return _read_count_list(text, parse)


def read_faces(path: Path) -> list[list[int]]:
    text = _strip_header(path.read_text())
    face_re = re.compile(r"(\d+)\s*\(([^)]*)\)")

    def parse(body: str, count: int) -> list[list[int]]:
        faces = []
        for m in face_re.finditer(body):
            n = int(m.group(1))
            verts = [int(x) for x in m.group(2).split()]
            if len(verts) != n:
                raise ValueError(f"face vertex count mismatch: {n} vs {len(verts)}")
            faces.append(verts)
        if len(faces) != count:
            raise ValueError(f"faces: expected {count}, got {len(faces)}")
        return faces

    return _read_count_list(text, parse)


def read_owner(path: Path) -> int:
    text = _strip_header(path.read_text())
    m = re.search(r"(\d+)\s*\(", text)
    if not m:
        raise ValueError("owner list not found")
    count = int(m.group(1))
    end = text.index(")", m.end())
    vals = [int(x) for x in text[m.end() : end].split()]
    if len(vals) != count:
        raise ValueError(f"owner: expected {count}, got {len(vals)}")
    return count


def slab_segments_from_faces(
    points: np.ndarray,
    faces: list[list[int]],
    *,
    slab_half: float,
) -> list[np.ndarray]:
    """Face edges in meridional slab |x| < slab_half, projected to (z, y)."""
    xs = points[:, 0]
    segs: list[np.ndarray] = []
    for face in faces:
        idx = np.asarray(face, dtype=np.int64)
        p = points[idx]
        ax = np.abs(p[:, 0])
        if np.min(ax) > slab_half and not (np.min(p[:, 0]) <= 0.0 <= np.max(p[:, 0])):
            continue
        n = len(face)
        for i in range(n):
            a, b = face[i], face[(i + 1) % n]
            pa, pb = points[a], points[b]
            segs.append(np.array([[pa[2], pa[1]], [pb[2], pb[1]]]))
    return segs


def mesh_yz_bounds_mm(points: np.ndarray, *, pad_frac: float = 0.04) -> tuple[float, float, float, float]:
    z_mm = points[:, 2] * 1e3
    y_mm = points[:, 1] * 1e3
    z0, z1 = float(z_mm.min()), float(z_mm.max())
    y0, y1 = float(y_mm.min()), float(y_mm.max())
    dz, dy = z1 - z0, y1 - y0
    return (
        z0 - pad_frac * dz,
        z1 + pad_frac * dz,
        y0 - pad_frac * dy,
        y1 + pad_frac * dy,
    )


def wedge_sphere_arc_yz(center_yz_mm: np.ndarray, r_mm: float, *, n: int = 48) -> tuple[np.ndarray, np.ndarray]:
    cz, cy = float(center_yz_mm[0]), float(center_yz_mm[1])
    theta = np.linspace(-0.5 * np.pi, 0.5 * np.pi, n)
    z = cz + r_mm * np.cos(theta)
    y = cy + r_mm * np.sin(theta)
    mask = z >= cz - 1.0e-9
    return z[mask], y[mask]


def plot_o1_mesh(
    polymesh_dir: Path,
    out: Path,
    *,
    slab_half: float = 8.0e-5,
    case_label: str = "O1 blockMesh",
) -> None:
    points = read_points(polymesh_dir / "points")
    faces = read_faces(polymesh_dir / "faces")
    n_internal = read_owner(polymesh_dir / "owner")
    n_cells = n_internal + 1  # upper bound; not used directly

    segs = slab_segments_from_faces(points, faces, slab_half=slab_half)
    tip_yz = np.array([IVI_TIP_ORIGIN_M[2], IVI_TIP_ORIGIN_M[1]]) * 1e3
    acp_yz = np.array([ACP_TIP_ORIGIN_M[2], ACP_TIP_ORIGIN_M[1]]) * 1e3
    r_topo_mm = TOPOSET_TIP_RADIUS_M * 1e3
    zlim = mesh_yz_bounds_mm(points)

    # TM outlet parallelogram (Table SI landmarks, mm)
    tm_z = np.array([6.61, 6.70, 6.93, 6.84])
    tm_y = np.array([-4.68, -4.75, -4.49, -4.42])

    fig, axes = plt.subplots(1, 3, figsize=(18, 7), dpi=170, facecolor="white")

    panels = (
        (
            axes[0],
            segs,
            f"Meridional cut (|x|<{slab_half * 1e3:.2f} mm) — {len(segs):,} edges",
            (zlim[0], zlim[1]),
            (zlim[2], zlim[3]),
            True,
            False,
        ),
        (
            axes[1],
            segs,
            f"Zoom TM outlet — 5 cells across thickness",
            (5.8, 7.4),
            (-5.2, -3.8),
            False,
            True,
        ),
        (
            axes[2],
            segs,
            f"Zoom IVI tip · topoSet r={r_topo_mm:.2f} mm",
            (tip_yz[0] - 1.2, tip_yz[0] + 1.2),
            (tip_yz[1] - 1.2, tip_yz[1] + 1.2),
            False,
            False,
        ),
    )

    for ax, segs_use, title, xlim, ylim, show_sym, show_tm in panels:
        if segs_use:
            lw = 0.30 if ax is axes[0] else 0.55
            lc = LineCollection(
                [s * 1e3 for s in segs_use],
                colors="#1a5276",
                linewidths=lw,
                alpha=0.85,
            )
            ax.add_collection(lc)
        if show_sym:
            ax.axvline(0.0, color="#7d3c98", lw=1.0, ls="--", alpha=0.7, label="symmetry_0 (z=0)")
        if show_tm:
            tm_poly = np.column_stack([tm_z, tm_y])
            tm_poly = np.vstack([tm_poly, tm_poly[0]])
            ax.plot(tm_poly[:, 0], tm_poly[:, 1], color="#27ae60", lw=1.5, ls=":", label="TM parallelogram (Table SI)")
        for center_yz, color, lbl in (
            (tip_yz, "#c0392b", "IVI topoSet arc"),
            (acp_yz, "#d35400", "ACP topoSet arc"),
        ):
            if ax is axes[2] and not np.allclose(center_yz, tip_yz):
                continue
            arc_z, arc_y = wedge_sphere_arc_yz(center_yz, r_topo_mm)
            ax.plot(arc_z, arc_y, ls="--", color=color, lw=1.4, label=lbl)
        ax.plot(tip_yz[0], tip_yz[1], "+", color="#c0392b", ms=10, mew=1.5, label="IVI centre")
        if ax is axes[0]:
            ax.plot(acp_yz[0], acp_yz[1], "x", color="#d35400", ms=9, mew=1.5, label="ACP centre")
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel("z [mm]")
        ax.set_ylabel("y [mm]  (+ posterior)")
        ax.set_title(title, fontsize=10)
        ax.grid(True, alpha=0.25)
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.legend(loc="upper right", fontsize=7, framealpha=0.92)

    n_pts, n_faces = len(points), len(faces)
    fig.suptitle(
        f"{case_label} — fluid mesh (90° wedge) · {n_pts:,} points · {n_faces:,} faces · ~{n_cells:,} cells\n"
        f"blockMeshDict.O1 · meridional projection (z, y) at x ≈ 0",
        fontsize=11,
        y=1.02,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Wrote {out}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--polymesh",
        type=Path,
        default=REPO / "cases/doc-baseline-o1-patch-fluid/fluid/constant/polyMesh",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO / "cases/doc-baseline-o1-patch-fluid/figures/o1_mesh.png",
    )
    ap.add_argument("--case-label", default="doc-baseline-o1-patch-fluid")
    ap.add_argument("--slab-half", type=float, default=8.0e-5, help="Half-width of meridional slab [m]")
    args = ap.parse_args()

    if not (args.polymesh / "points").exists():
        raise SystemExit(f"missing polyMesh at {args.polymesh}")

    plot_o1_mesh(
        args.polymesh,
        args.out,
        slab_half=args.slab_half,
        case_label=args.case_label,
    )


if __name__ == "__main__":
    main()
