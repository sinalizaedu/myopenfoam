#!/usr/bin/env python3
"""Plot Gmsh hex mesh with visible cell edges (meridional slice + 3D wireframe)."""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from mpl_toolkits.mplot3d.art3d import Line3DCollection

CASE = Path(__file__).resolve().parents[1]
GEOM = CASE / "geometry"
FIGS = CASE / "figures"

ZONE_COLORS = {
    "cornea": "#e8a87c",
    "sclera": "#4a6fa5",
    "choroid": "#c1666b",
    "retina": "#e4c15f",
    "ciliary": "#9b59b6",
    "lens": "#2d6a4f",
    "iris": "#c0392b",
    "fluid": "#5dade2",
}

HEX_EDGES = (
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7),
)
PRISM_EDGES = (
    (0, 1), (1, 2), (2, 0),
    (3, 4), (4, 5), (5, 3),
    (0, 3), (1, 4), (2, 5),
)


def read_msh(path: Path):
    text = path.read_text()
    names: dict[tuple[int, int], str] = {}
    m = re.search(r"\$PhysicalNames\n(\d+)\n([\s\S]*?)\$EndPhysicalNames", text)
    if m:
        for line in m.group(2).strip().splitlines():
            dim, tag, name = line.split(None, 2)
            names[(int(dim), int(tag))] = name.strip('"')

    m = re.search(r"\$Nodes\n(\d+)\n([\s\S]*?)\$EndNodes", text)
    nodes = {
        int(p[0]): np.array(list(map(float, p[1:4])))
        for line in m.group(2).strip().splitlines()
        for p in [line.split()]
    }

    vol: dict[int, list[tuple[int, list[int]]]] = defaultdict(list)
    m = re.search(r"\$Elements\n(\d+)\n([\s\S]*?)\$EndElements", text)
    for line in m.group(2).strip().splitlines():
        p = list(map(int, line.split()))
        etype, ntags = p[1], p[2]
        if etype not in (5, 6):
            continue
        tags, conn = p[3 : 3 + ntags], p[3 + ntags :]
        vol[tags[0] if tags else 0].append((etype, conn))
    return nodes, vol, names


def zone_name(names, tag: int) -> str:
    return names.get((3, tag), str(tag))


def elem_segments_2d(
    nodes: dict[int, np.ndarray],
    elems: list[tuple[int, list[int]]],
    *,
    plane: str = "z0",
    tol: float = 2.0e-4,
) -> list[np.ndarray]:
    """Edges lying on symmetry plane z=0 (x,y) or x=0 (y,z)."""
    segs: list[np.ndarray] = []
    for etype, conn in elems:
        edge_list = HEX_EDGES if etype == 5 else PRISM_EDGES
        pts = {i: nodes[n] for i, n in enumerate(conn)}
        for a, b in edge_list:
            pa, pb = pts[a], pts[b]
            if plane == "z0":
                if abs(pa[2]) > tol or abs(pb[2]) > tol:
                    continue
                segs.append(np.array([[pa[0], pa[1]], [pb[0], pb[1]]]))
            else:
                if abs(pa[0]) > tol or abs(pb[0]) > tol:
                    continue
                segs.append(np.array([[pa[1], pb[1]], [pa[2], pb[2]]]))
    return segs


def elem_segments_3d(nodes: dict[int, np.ndarray], elems: list[tuple[int, list[int]]]) -> list[np.ndarray]:
    segs: list[np.ndarray] = []
    for etype, conn in elems:
        edge_list = HEX_EDGES if etype == 5 else PRISM_EDGES
        pts = [nodes[n] for n in conn]
        for a, b in edge_list:
            segs.append(np.array([pts[a], pts[b]]))
    return segs


def add_lc(ax, segments: list[np.ndarray], color: str, lw: float = 0.35, alpha: float = 0.9):
    if not segments:
        return
    lc = LineCollection([s * 1e3 for s in segments], colors=color, linewidths=lw, alpha=alpha)
    ax.add_collection(lc)


def add_lc3d(ax, segments: list[np.ndarray], color: str, lw: float = 0.15, alpha: float = 0.55):
    if not segments:
        return
    lc = Line3DCollection([s * 1e3 for s in segments], colors=color, linewidths=lw, alpha=alpha)
    ax.add_collection3d(lc)


def plot_mesh_cells(
    solid_path: Path,
    fluid_path: Path | None,
    out: Path,
    *,
    mesh_level: str,
    z_tol: float = 2.0e-4,
) -> None:
    sn, sv, sns = read_msh(solid_path)
    fn, fv, fns = (None, None, None)
    if fluid_path and fluid_path.exists():
        fn, fv, fns = read_msh(fluid_path)

    fig = plt.figure(figsize=(18, 10), dpi=170, facecolor="white")
    gs = fig.add_gridspec(2, 2, width_ratios=[1.15, 1], height_ratios=[1, 1], wspace=0.12, hspace=0.22)

    ax_s2 = fig.add_subplot(gs[0, 0])
    ax_f2 = fig.add_subplot(gs[1, 0])
    ax_3d = fig.add_subplot(gs[:, 1], projection="3d")

    n_solid_hex = 0
    for tag, elems in sorted(sv.items()):
        name = zone_name(sns, tag)
        color = ZONE_COLORS.get(name, "#888888")
        segs = elem_segments_2d(sn, elems, plane="z0", tol=z_tol)
        add_lc(ax_s2, segs, color, lw=0.45)
        add_lc3d(ax_3d, elem_segments_3d(sn, elems), color, lw=0.12)
        n_solid_hex += len(elems)

    if fn is not None and fv is not None:
        for tag, elems in fv.items():
            name = zone_name(fns, tag)
            color = ZONE_COLORS.get(name, "#5dade2")
            segs = elem_segments_2d(fn, elems, plane="z0", tol=z_tol)
            add_lc(ax_f2, segs, color, lw=0.35, alpha=0.85)
            add_lc3d(ax_3d, elem_segments_3d(fn, elems), color, lw=0.10, alpha=0.45)
        n_fluid_hex = sum(len(h) for h in fv.values())
    else:
        n_fluid_hex = 0

    for ax, title in (
        (ax_s2, f"Sólido — corte z=0 (células hex visíveis) · {n_solid_hex:,} elems"),
        (ax_f2, f"Fluido — corte z=0 · {n_fluid_hex:,} elems"),
    ):
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel("x [mm]")
        ax.set_ylabel("y [mm]")
        ax.set_title(title, fontsize=10)
        ax.grid(True, alpha=0.2)
        ax.set_xlim(-0.5, 10.5)
        ax.set_ylim(-9.5, 9.5)

    # axis limits 3D
    all_pts = np.vstack([np.array(list(sn.values()))] + ([np.array(list(fn.values()))] if fn else []))
    all_mm = all_pts * 1e3
    pad = 0.5
    ax_3d.set_xlim(all_mm[:, 0].min() - pad, all_mm[:, 0].max() + pad)
    ax_3d.set_ylim(all_mm[:, 1].min() - pad, all_mm[:, 1].max() + pad)
    ax_3d.set_zlim(all_mm[:, 2].min() - pad, all_mm[:, 2].max() + pad)
    ax_3d.set_xlabel("x [mm]")
    ax_3d.set_ylabel("y [mm]")
    ax_3d.set_zlabel("z [mm]")
    ax_3d.set_title(f"Malha 3D — arestas de todas as células hex ({mesh_level})", fontsize=10)
    ax_3d.view_init(elev=18, azim=-58)

    handles = [plt.Line2D([0], [0], color=c, lw=1.5, label=k) for k, c in ZONE_COLORS.items()]
    fig.legend(handles=handles, loc="lower center", ncol=5, fontsize=8, frameon=False, bbox_to_anchor=(0.5, 0.01))

    fig.suptitle(
        f"doc-g2-sim2 — malha fluida G3 · corte z=0 · {mesh_level}\n"
        f"sólido: {solid_path.name}  ·  "
        f"fluido: {fluid_path.name if fluid_path else '—'}",
        fontsize=12,
        y=0.98,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Wrote {out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mesh-level", default="M3", choices=["M1", "M2", "M3"])
    ap.add_argument("--solid", type=Path, default=None, help="Override solid .msh path")
    ap.add_argument("--fluid", type=Path, default=None, help="Override fluid .msh path")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    solid = args.solid or GEOM / f"eye_g2_solid_lamminsalo_{args.mesh_level}.msh"
    fluid = args.fluid if args.fluid is not None else GEOM / f"eye_g2_fluid_lamminsalo_{args.mesh_level}.msh"
    out = args.out or FIGS / f"g2_mesh_cells_{args.mesh_level}.png"

    if not solid.exists():
        raise SystemExit(f"missing {solid}")

    plot_mesh_cells(solid, fluid if fluid.exists() else None, out, mesh_level=args.mesh_level)


if __name__ == "__main__":
    main()
