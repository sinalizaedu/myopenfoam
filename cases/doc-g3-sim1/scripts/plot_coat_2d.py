#!/usr/bin/env python3
"""Plot 2D meridional solid + fluid meshes (separate .msh files)."""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection, PolyCollection

CASE = Path(__file__).resolve().parents[1]
GEOM = CASE / "geometry"
FIGS = CASE / "figures"

ZONE_COLORS = {
    "cornea": "#e8a87c",
    "coat": "#4a6fa5",
    "tm": "#f4a261",
    "ciliary": "#9b59b6",
    "iris": "#c0392b",
    "lens": "#2d6a4f",
    "ac": "#85c1e9",
    "vitreous": "#5dade2",
}
SOLID_ORDER = ("cornea", "coat", "tm", "ciliary", "iris")
FLUID_ORDER = ("vitreous", "ac")
PATCH_STYLE = {
    "outer": ("#1d3557", 1.2),
    "fsi_active": ("#d84315", 1.4),
    "fsi_cornea": ("#1565c0", 1.1),
    "fsi_tm": ("#6a1b9a", 1.2),
    "fsi_iris": ("#b71c1c", 1.1),
    "fsi_hyaloid": ("#2874a6", 1.0),
    "symmetry_0": ("#7d3c98", 1.0),
    "interface_coat_tm": ("#e76f51", 0.95),
    "interface_coat_ciliary": ("#8e44ad", 0.9),
}


def read_msh2(path: Path):
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
    quads: dict[str, list[list[int]]] = defaultdict(list)
    tris: dict[str, list[list[int]]] = defaultdict(list)
    lines: dict[str, list[tuple[int, int]]] = defaultdict(list)
    m = re.search(r"\$Elements\n(\d+)\n([\s\S]*?)\$EndElements", text)
    for raw in m.group(2).strip().splitlines():
        p = list(map(int, raw.split()))
        et, nt = p[1], p[2]
        tags, conn = p[3 : 3 + nt], p[3 + nt :]
        phy = tags[0] if tags else 0
        if et == 3:
            name = names.get((2, phy), str(phy))
            quads[name].append(conn)
        elif et == 2:
            name = names.get((2, phy), str(phy))
            tris[name].append(conn)
        elif et == 1:
            name = names.get((1, phy), str(phy))
            lines[name].append((conn[0], conn[1]))
    return nodes, quads, tris, lines


def _draw_zones(ax, nodes, quads, tris, order, id_to_xy):
    nq = nt = 0
    for zname in order:
        color = ZONE_COLORS.get(zname)
        if not color:
            continue
        polys = [[id_to_xy[n] for n in q] for q in quads.get(zname, [])]
        polys += [[id_to_xy[n] for n in t] for t in tris.get(zname, [])]
        if not polys:
            continue
        nq += len(quads.get(zname, []))
        nt += len(tris.get(zname, []))
        ax.add_collection(
            PolyCollection(polys, facecolor=color, edgecolor="#333333", linewidth=0.35, alpha=0.55)
        )
        segs = []
        for q in quads.get(zname, []):
            for a, b in ((q[0], q[1]), (q[1], q[2]), (q[2], q[3]), (q[3], q[0])):
                segs.append(np.vstack([id_to_xy[a], id_to_xy[b]]))
        for t in tris.get(zname, []):
            for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
                segs.append(np.vstack([id_to_xy[a], id_to_xy[b]]))
        if segs:
            ax.add_collection(LineCollection(segs, colors="#222222", linewidths=0.25, alpha=0.8))
    return nq, nt


def plot_coat_2d(
    solid_msh: Path,
    fluid_msh: Path | None,
    out: Path,
    *,
    mesh_level: str,
) -> None:
    s_nodes, s_quads, s_tris, s_lines = read_msh2(solid_msh)
    f_nodes, f_quads, f_tris, f_lines = ({}, {}, {}, {})
    if fluid_msh and fluid_msh.exists():
        f_nodes, f_quads, f_tris, f_lines = read_msh2(fluid_msh)
        offset = max(s_nodes) if s_nodes else 0
        f_nodes = {nid + offset: xyz for nid, xyz in f_nodes.items()}
        f_quads = {z: [[n + offset for n in q] for q in qs] for z, qs in f_quads.items()}
        f_tris = {z: [[n + offset for n in t] for t in ts] for z, ts in f_tris.items()}
        f_lines = {p: [(a + offset, b + offset) for a, b in segs] for p, segs in f_lines.items()}

    all_nodes = {**s_nodes, **f_nodes}
    id_to_xy = {nid: all_nodes[nid][:2] * 1e3 for nid in all_nodes}

    fig, ax = plt.subplots(figsize=(9, 10), dpi=170, facecolor="white")
    nq_s, nt_s = _draw_zones(ax, s_nodes, s_quads, s_tris, SOLID_ORDER, id_to_xy)
    nq_f, nt_f = _draw_zones(ax, f_nodes, f_quads, f_tris, FLUID_ORDER, id_to_xy)

    lines = defaultdict(list)
    for src in (s_lines, f_lines):
        for k, v in src.items():
            lines[k].extend(v)

    for pname, (color, lw) in PATCH_STYLE.items():
        segs = [np.vstack([id_to_xy[a], id_to_xy[b]]) for a, b in lines.get(pname, [])]
        if segs:
            ax.add_collection(LineCollection(segs, colors=color, linewidths=lw, alpha=0.95, label=pname))

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x [mm]")
    ax.set_ylabel("y [mm]  (+ posterior)")
    ax.set_title(
        f"Malha 2D meridional ({mesh_level})\n"
        f"Sólido: {solid_msh.name} · Fluido: {fluid_msh.name if fluid_msh else '—'}",
        fontsize=11,
    )
    ax.grid(True, alpha=0.25)
    ax.legend(loc="upper right", fontsize=7, framealpha=0.92)
    ax.set_xlim(-0.3, 10.5)
    ax.set_ylim(-9.5, 8.5)

    fig.suptitle(
        f"doc-g3-sim1 · sólido {nq_s} quads · fluido {nt_f} tris · {len(all_nodes)} nós",
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
    ap.add_argument("--solid-msh", type=Path, default=None)
    ap.add_argument("--fluid-msh", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    solid = args.solid_msh or GEOM / f"eye_g2_solid_2d_{args.mesh_level}.msh"
    fluid = args.fluid_msh or GEOM / f"eye_g2_fluid_2d_{args.mesh_level}.msh"
    out = args.out or FIGS / f"g3_coat_2d_{args.mesh_level}.png"
    if not solid.exists():
        raise SystemExit(f"missing {solid} — run gen_lamminsalo_g2.py --coat-2d first")
    plot_coat_2d(solid, fluid if fluid.exists() else None, out, mesh_level=args.mesh_level)


if __name__ == "__main__":
    main()
