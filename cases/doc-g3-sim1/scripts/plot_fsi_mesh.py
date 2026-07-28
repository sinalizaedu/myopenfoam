#!/usr/bin/env python3
"""Render G3 FSI mesh (fluid + solid) from Gmsh .msh files."""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection, PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


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
PATCH_COLORS = {
    "fsi_active": "#d84315",
    "fsi_wall": "#1565c0",
    "wall": "#1565c0",
    "outer": "#546e7a",
    "symmetry_0": "#78909c",
    "symmetry_90": "#78909c",
}


def patch_tag(surf: dict[int, list[list[int]]], names: dict[tuple[int, int], str], pname: str) -> int:
    for tag in surf:
        if phys_name(names, 2, tag) == pname:
            return tag
    raise KeyError(f"patch {pname!r} not found in .msh")


def read_msh2(path: Path) -> tuple[dict[int, np.ndarray], dict[int, list[list[int]]], dict[int, list[list[int]]], dict[tuple[int, int], str]]:
    text = path.read_text()
    names: dict[tuple[int, int], str] = {}
    m = re.search(r"\$PhysicalNames\n(\d+)\n([\s\S]*?)\$EndPhysicalNames", text)
    if m:
        for line in m.group(2).strip().splitlines():
            dim, tag, name = line.split(None, 2)
            names[(int(dim), int(tag))] = name.strip('"')

    m = re.search(r"\$Nodes\n(\d+)\n([\s\S]*?)\$EndNodes", text)
    nodes = {
        int(parts[0]): np.array(list(map(float, parts[1:4])))
        for line in m.group(2).strip().splitlines()
        for parts in [line.split()]
    }

    m = re.search(r"\$Elements\n(\d+)\n([\s\S]*?)\$EndElements", text)
    vol: dict[int, list[list[int]]] = defaultdict(list)
    surf: dict[int, list[list[int]]] = defaultdict(list)
    for line in m.group(2).strip().splitlines():
        parts = list(map(int, line.split()))
        etype, ntags = parts[1], parts[2]
        tags = parts[3 : 3 + ntags]
        conn = parts[3 + ntags :]
        phys = tags[0] if tags else 0
        if etype == 5:
            vol[phys].append(conn)
        elif etype == 6:
            vol[phys].append(conn)
        elif etype in (3, 4):
            surf[phys].append(conn)
    return nodes, vol, surf, names


def phys_name(names: dict[tuple[int, int], str], dim: int, tag: int) -> str:
    return names.get((dim, tag), str(tag))


def triangulate(conn: list[int]) -> list[tuple[int, int, int]]:
    if len(conn) == 3:
        return [(conn[0], conn[1], conn[2])]
    if len(conn) == 4:
        a, b, c, d = conn
        return [(a, b, c), (a, c, d)]
    if len(conn) == 6:
        return [(conn[i], conn[j], conn[k]) for i, j, k in ((0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 5))]
    if len(conn) == 8:
        a, b, c, d, e, f, g, h = conn
        return [
            (a, b, c, d),
            (e, f, g, h),
            (a, b, f, e),
            (b, c, g, f),
            (c, d, h, g),
            (d, a, e, h),
        ]
    return []


def face_edges(conn: list[int]) -> list[tuple[int, int]]:
    n = len(conn)
    return [(conn[i], conn[(i + 1) % n]) for i in range(n)]


def collect_edges(elems: list[list[int]]) -> set[tuple[int, int]]:
    counts: dict[tuple[int, int], int] = defaultdict(int)
    for conn in elems:
        for a, b in face_edges(conn):
            key = (min(a, b), max(a, b))
            counts[key] += 1
    return {edge for edge, n in counts.items() if n == 1}


def surf_tris(nodes: dict[int, np.ndarray], elems: list[list[int]]) -> np.ndarray:
    tris = []
    for conn in elems:
        for tri in triangulate(conn):
            if len(tri) == 3:
                tris.append(nodes[tri[0]])
                tris.append(nodes[tri[1]])
                tris.append(nodes[tri[2]])
            elif len(tri) == 4:
                a, b, c, d = tri
                tris.extend([nodes[a], nodes[b], nodes[c], nodes[a], nodes[c], nodes[d]])
    if not tris:
        return np.empty((0, 3, 3))
    arr = np.asarray(tris).reshape(-1, 3, 3)
    return arr


def surf_quads(nodes: dict[int, np.ndarray], elems: list[list[int]]) -> np.ndarray:
    quads = []
    for conn in elems:
        if len(conn) == 4:
            quads.append([nodes[i] for i in conn])
        elif len(conn) == 3:
            quads.append([nodes[i] for i in conn])
    return np.asarray(quads) if quads else np.empty((0, len(next(iter(elems), [0, 0, 0])), 3))


def meridional_edges(
    nodes: dict[int, np.ndarray],
    elems: list[list[int]],
    tol: float = 1e-4,
) -> list[np.ndarray]:
    """Element edges on symmetry_0 (z≈0), projected to (x, y) in mm."""
    segments = []
    for conn in elems:
        for i in range(len(conn)):
            a, b = conn[i], conn[(i + 1) % len(conn)]
            pa, pb = nodes[a], nodes[b]
            if abs(pa[2]) <= tol and abs(pb[2]) <= tol:
                segments.append(np.array([[pa[0], pa[1]], [pb[0], pb[1]]]) * 1e3)
    return segments


def add_wire(ax, segments: list[np.ndarray], color: str, lw: float = 0.35, alpha: float = 0.95):
    if not segments:
        return
    lc = LineCollection(segments, colors=color, linewidths=lw, alpha=alpha)
    ax.add_collection(lc)


def add_surface(ax, tris: np.ndarray, color: str, alpha: float = 0.55, edgecolor: str | None = None, lw: float = 0.05):
    if len(tris) == 0:
        return
    coll = Poly3DCollection(tris * 1e3, alpha=alpha, facecolor=color, edgecolor=edgecolor or color, linewidth=lw)
    ax.add_collection3d(coll)


def style_2d(ax, title: str):
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x [mm]")
    ax.set_ylabel("y [mm]  (+ posterior)")
    ax.set_title(title, fontsize=10)
    ax.grid(True, alpha=0.25)


def style_3d(ax, title: str):
    ax.set_xlabel("x [mm]")
    ax.set_ylabel("y [mm]")
    ax.set_zlabel("z [mm]")
    ax.set_title(title, fontsize=10)
    ax.view_init(elev=18, azim=-58)


def plot_fsi_mesh(mesh_level: str, out: Path) -> None:
    fluid_path = GEOM / f"eye_g2_fluid_lamminsalo_{mesh_level}.msh"
    solid_path = GEOM / f"eye_g2_solid_lamminsalo_{mesh_level}.msh"
    fn, fv, sf, nf = read_msh2(fluid_path)
    sn, sv, ss, ns = read_msh2(solid_path)

    fig = plt.figure(figsize=(16, 10), dpi=160, facecolor="white")
    gs = fig.add_gridspec(2, 2, width_ratios=[1.1, 1], height_ratios=[1, 1], wspace=0.18, hspace=0.28)

    ax_cut = fig.add_subplot(gs[0, 0])
    ax_fsi = fig.add_subplot(gs[1, 0])
    ax_3d = fig.add_subplot(gs[:, 1], projection="3d")

    # --- Meridional mesh (symmetry_0, z=0) ---
    for phys, elems in sorted(sv.items()):
        name = phys_name(ns, 3, phys)
        segs = meridional_edges(sn, elems)
        add_wire(ax_cut, segs, ZONE_COLORS.get(name, "#999999"), lw=0.45)
    fluid_phys = next(iter(fv))
    add_wire(ax_cut, meridional_edges(fn, fv[fluid_phys]), ZONE_COLORS["fluid"], lw=0.35, alpha=0.85)
    style_2d(ax_cut, f"Malha meridional (symmetry_0, z=0) — {mesh_level}")

    # --- FSI interface close-up (conformal: fsi_wall ↔ fsi_active) ---
    fluid_fsi_name = "fsi_wall" if any(phys_name(nf, 2, k) == "fsi_wall" for k in sf) else "wall"
    wall_phys = patch_tag(sf, nf, fluid_fsi_name)
    fsi_phys = patch_tag(ss, ns, "fsi_active")
    add_wire(ax_fsi, meridional_edges(fn, sf[wall_phys]), PATCH_COLORS[fluid_fsi_name], lw=0.9)
    add_wire(ax_fsi, meridional_edges(sn, ss[fsi_phys]), PATCH_COLORS["fsi_active"], lw=0.9)
    style_2d(
        ax_fsi,
        f"Interface FSI conforme — fluid {fluid_fsi_name} (azul) vs solid fsi_active (laranja)",
    )
    ax_fsi.set_xlim(-0.5, 10.5)
    ax_fsi.set_ylim(-9.5, 9.0)

    # --- 3D surfaces ---
    for phys, elems in sorted(sv.items()):
        name = phys_name(ns, 3, phys)
        tris = surf_tris(sn, elems)
        add_surface(ax_3d, tris, ZONE_COLORS.get(name, "#bbbbbb"), alpha=0.42, edgecolor="#444444", lw=0.03)

    fluid_tris = surf_tris(fn, sf[wall_phys])
    add_surface(ax_3d, fluid_tris, PATCH_COLORS["wall"], alpha=0.35, edgecolor="#0d47a1", lw=0.04)
    fsi_tris = surf_tris(sn, ss[fsi_phys])
    add_surface(ax_3d, fsi_tris, PATCH_COLORS["fsi_active"], alpha=0.55, edgecolor="#bf360c", lw=0.05)

    outer_phys = next(k for k in ss if phys_name(ns, 2, k) == "outer")
    outer_tris = surf_tris(sn, ss[outer_phys])
    add_surface(ax_3d, outer_tris, PATCH_COLORS["outer"], alpha=0.18, edgecolor="#37474f", lw=0.02)

    pts = np.vstack([np.array(list(fn.values())), np.array(list(sn.values()))]) * 1e3
    pad = 0.6
    ax_3d.set_xlim(pts[:, 0].min() - pad, pts[:, 0].max() + pad)
    ax_3d.set_ylim(pts[:, 1].min() - pad, pts[:, 1].max() + pad)
    ax_3d.set_zlim(pts[:, 2].min() - pad, pts[:, 2].max() + pad)
    style_3d(ax_3d, f"Malha FSI G3 — calotte 90° ({mesh_level})")

    handles = [
        plt.Line2D([0], [0], color=ZONE_COLORS[k], lw=2, label=k)
        for k in ("cornea", "sclera", "choroid", "retina", "ciliary", "lens", "iris", "fluid")
    ]
    handles += [
        plt.Line2D([0], [0], color=PATCH_COLORS[fluid_fsi_name], lw=2, label=f"fluid {fluid_fsi_name}"),
        plt.Line2D([0], [0], color=PATCH_COLORS["fsi_active"], lw=2, label="solid fsi_active"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=5, fontsize=8, frameon=False, bbox_to_anchor=(0.5, 0.01))

    n_fluid = sum(len(v) for v in fv.values())
    n_solid = sum(len(v) for v in sv.values())
    fig.suptitle(
        f"doc-g3-sim1 — malha FSI ({mesh_level}, structured)\n"
        f"fluid: {len(fn):,} nós / {n_fluid:,} elems  ·  "
        f"solid: {len(sn):,} nós / {n_solid:,} elems  ·  "
        f"revolve 90° sobre +y",
        fontsize=12,
        y=0.98,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Wrote {out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mesh-level", default="M1", choices=["M1", "M2", "M3"])
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    out = args.out or FIGS / f"g3_fsi_mesh_{args.mesh_level}.png"
    plot_fsi_mesh(args.mesh_level, out)


if __name__ == "__main__":
    main()
