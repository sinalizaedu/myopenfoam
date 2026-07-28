#!/usr/bin/env python3
"""Plot doc-g2-sim2 fluid-only 2D meridional mesh (AC + vitreous)."""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.patches import Circle

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "brunaStuff"))
from g2_needle import IVI_TIP_ORIGIN_M, NEEDLE_R_LUMEN_M

CASE = Path(__file__).resolve().parents[1]
GEOM = CASE / "geometry"
FIGS = CASE / "figures"

ZONE_COLORS = {
    "ac": "#85c1e9",
    "vitreous": "#5dade2",
}
FLUID_ORDER = ("vitreous", "ac")
PATCH_STYLE = {
    "fsi_active": ("#d84315", 1.3),
    "fsi_cornea": ("#1565c0", 1.0),
    "fsi_iris": ("#b71c1c", 1.0),
    "symmetry_0": ("#7d3c98", 1.0),
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
    tris: dict[str, list[list[int]]] = defaultdict(list)
    lines: dict[str, list[tuple[int, int]]] = defaultdict(list)
    m = re.search(r"\$Elements\n(\d+)\n([\s\S]*?)\$EndElements", text)
    for raw in m.group(2).strip().splitlines():
        p = list(map(int, raw.split()))
        et, nt = p[1], p[2]
        tags, conn = p[3 : 3 + nt], p[3 + nt :]
        phy = tags[0] if tags else 0
        if et == 2:
            name = names.get((2, phy), str(phy))
            tris[name].append(conn)
        elif et == 1:
            name = names.get((1, phy), str(phy))
            lines[name].append((conn[0], conn[1]))
    return nodes, tris, lines


def _draw_fluid(ax, nodes, tris, id_to_xy) -> tuple[int, int]:
    nt = 0
    for zname in FLUID_ORDER:
        color = ZONE_COLORS[zname]
        polys = [[id_to_xy[n] for n in t] for t in tris.get(zname, [])]
        if not polys:
            continue
        nt += len(polys)
        ax.add_collection(
            PolyCollection(polys, facecolor=color, edgecolor="#333333", linewidth=0.35, alpha=0.58)
        )
        segs = []
        for t in tris.get(zname, []):
            for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
                segs.append(np.vstack([id_to_xy[a], id_to_xy[b]]))
        if segs:
            ax.add_collection(LineCollection(segs, colors="#222222", linewidths=0.25, alpha=0.85))
    return nt, len(nodes)


def plot_fluid_2d(fluid_msh: Path, out: Path, *, mesh_level: str) -> None:
    nodes, tris, line_patches = read_msh2(fluid_msh)
    id_to_xy = {nid: nodes[nid][:2] * 1e3 for nid in nodes}

    fig, axes = plt.subplots(1, 2, figsize=(14, 7), dpi=170, facecolor="white")
    tip_xy = np.array(IVI_TIP_ORIGIN_M[:2]) * 1e3
    r_mm = NEEDLE_R_LUMEN_M * 1e3

    for ax, xlim, ylim, title_suffix in (
        (axes[0], (-0.3, 10.5), (-9.5, 8.5), "visão global"),
        (axes[1], (tip_xy[0] - 1.0, tip_xy[0] + 1.0), (tip_xy[1] - 1.0, tip_xy[1] + 1.0), "zoom IVI tip"),
    ):
        nt, nn = _draw_fluid(ax, nodes, tris, id_to_xy)
        for pname, (color, lw) in PATCH_STYLE.items():
            segs = [np.vstack([id_to_xy[a], id_to_xy[b]]) for a, b in line_patches.get(pname, [])]
            if segs:
                ax.add_collection(
                    LineCollection(segs, colors=color, linewidths=lw, alpha=0.95, label=pname)
                )
        ax.add_patch(
            Circle(
                tip_xy,
                r_mm,
                fill=False,
                edgecolor="#c0392b",
                linewidth=1.4,
                linestyle="--",
                label="lúmen 30G",
            )
        )
        ax.plot(tip_xy[0], tip_xy[1], "+", color="#c0392b", ms=10, mew=1.5)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel("x [mm]")
        ax.set_ylabel("y [mm]  (+ posterior)")
        ax.set_title(f"Malha fluida 2D ({mesh_level}) — {title_suffix}", fontsize=10)
        ax.grid(True, alpha=0.25)
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        if ax is axes[1]:
            ax.legend(loc="upper right", fontsize=7, framealpha=0.92)

    ac_n = len(tris.get("ac", []))
    vit_n = len(tris.get("vitreous", []))
    fig.suptitle(
        f"doc-g2-sim2 — malha fluida 2D meridional · {fluid_msh.name}\n"
        f"AC {ac_n:,} tris · vítreo {vit_n:,} tris · {nn:,} nós",
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
    ap.add_argument("--fluid-msh", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    fluid = args.fluid_msh or GEOM / f"eye_g2_fluid_2d_{args.mesh_level}.msh"
    out = args.out or FIGS / f"g2_fluid_2d_{args.mesh_level}.png"
    if not fluid.exists():
        raise SystemExit(f"missing {fluid}")
    plot_fluid_2d(fluid, out, mesh_level=args.mesh_level)


if __name__ == "__main__":
    main()
