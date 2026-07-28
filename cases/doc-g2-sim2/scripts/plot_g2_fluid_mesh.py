#!/usr/bin/env python3
"""Plot doc-g2-sim2 fluid mesh: z=0 meridional cut + optional IVI tip zoom (tets)."""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "brunaStuff"))
from g2_needle import ACP_TIP_ORIGIN_M, IVI_TIP_ORIGIN_M, NEEDLE_R_LUMEN_M, TOPOSET_TIP_RADIUS_M

CASE = Path(__file__).resolve().parents[1]
GEOM = CASE / "geometry"
FIGS = CASE / "figures"

TET_EDGES = ((0, 1), (1, 2), (2, 0), (0, 3), (1, 3), (2, 3))
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
EDGE_TABLE = {4: TET_EDGES, 5: HEX_EDGES, 6: PRISM_EDGES}


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
        if etype not in EDGE_TABLE:
            continue
        tags, conn = p[3 : 3 + ntags], p[3 + ntags :]
        vol[tags[0] if tags else 0].append((etype, conn))
    return nodes, vol, names


def slab_segments_meridional(
    nodes: dict[int, np.ndarray],
    elems: list[tuple[int, list[int]]],
    *,
    slab_half: float = 8.0e-5,
) -> list[np.ndarray]:
    """Edges of tets intersecting |x| < slab_half, projected to x=0 (z, y)."""
    segs: list[np.ndarray] = []
    for etype, conn in elems:
        pts = [nodes[n] for n in conn]
        xs = [p[0] for p in pts]
        if min(abs(x) for x in xs) > slab_half and not (min(xs) <= 0 <= max(xs)):
            continue
        for a, b in EDGE_TABLE[etype]:
            pa, pb = pts[a], pts[b]
            segs.append(np.array([[pa[2], pa[1]], [pb[2], pb[1]]]))
    return segs


def count_lumen_centres(nodes, elems, origin, r: float) -> int:
    n = 0
    for _, conn in elems:
        c = np.mean([nodes[i] for i in conn], axis=0)
        if np.linalg.norm(c - origin) <= r:
            n += 1
    return n


def mesh_yz_bounds_mm(nodes: dict[int, np.ndarray], *, pad_frac: float = 0.04) -> tuple[float, float, float, float]:
    """Axis limits (z_min, z_max, y_min, y_max) in mm with padding."""
    arr = np.array(list(nodes.values()))
    z_mm = arr[:, 2] * 1e3
    y_mm = arr[:, 1] * 1e3
    z0, z1 = float(z_mm.min()), float(z_mm.max())
    y0, y1 = float(y_mm.min()), float(y_mm.max())
    dz, dy = z1 - z0, y1 - y0
    return (
        z0 - pad_frac * dz,
        z1 + pad_frac * dz,
        y0 - pad_frac * dy,
        y1 + pad_frac * dy,
    )


def wedge_sphere_arc_yz(
    center_yz_mm: np.ndarray,
    r_mm: float,
    *,
    n: int = 48,
) -> tuple[np.ndarray, np.ndarray]:
    """Meridional (z,y) arc of topoSet sphere with z >= 0 — 1/4 sphere in the 90° wedge."""
    cz, cy = float(center_yz_mm[0]), float(center_yz_mm[1])
    theta = np.linspace(-0.5 * np.pi, 0.5 * np.pi, n)
    z = cz + r_mm * np.cos(theta)
    y = cy + r_mm * np.sin(theta)
    mask = z >= cz - 1.0e-9
    return z[mask], y[mask]


def plot_g2_fluid_mesh(
    fluid_path: Path,
    out: Path,
    *,
    mesh_level: str,
    z_tol: float = 5.0e-5,
    case_label: str = "doc-g2-sim1",
) -> None:
    nodes, vol, _ = read_msh(fluid_path)
    all_elems = [e for elems in vol.values() for e in elems]
    n_vol = len(all_elems)
    tip = np.array(IVI_TIP_ORIGIN_M)
    acp = np.array(ACP_TIP_ORIGIN_M)
    if abs(tip[0]) > 1e-9 or abs(tip[2]) > 1e-9 or abs(acp[0]) > 1e-9 or abs(acp[2]) > 1e-9:
        raise ValueError("IVI/ACP tips must have x=0 and z=0 (wedge axis)")
    n_lumen = count_lumen_centres(nodes, all_elems, tip, NEEDLE_R_LUMEN_M)

    # Meridional slab through symmetry_90 (|x|≈0): project to (z, y).
    segs_full = slab_segments_meridional(nodes, all_elems, slab_half=z_tol)
    tip_yz = np.array([tip[2], tip[1]]) * 1e3
    acp_yz = np.array([acp[2], acp[1]]) * 1e3
    r_lumen_mm = NEEDLE_R_LUMEN_M * 1e3
    r_topo_mm = TOPOSET_TIP_RADIUS_M * 1e3
    zlim = mesh_yz_bounds_mm(nodes)

    fig, axes = plt.subplots(1, 2, figsize=(15, 8), dpi=170, facecolor="white")

    for ax, segs_use, title, xlim, ylim, xlab, ylab, show_sym in (
        (
            axes[0],
            segs_full,
            f"Corte meridional (|x|<{z_tol*1e3:.2f} mm) — {len(segs_full):,} arestas · {n_vol:,} elems",
            (zlim[0], zlim[1]),
            (zlim[2], zlim[3]),
            "z [mm]",
            "y [mm]  (+ posterior)",
            True,
        ),
        (
            axes[1],
            segs_full,
            f"Zoom IVI (intra-vítreo) · topoSet r={r_topo_mm:.2f} mm",
            (tip_yz[0] - 1.2, tip_yz[0] + 1.2),
            (tip_yz[1] - 1.2, tip_yz[1] + 1.2),
            "z [mm]",
            "y [mm]",
            False,
        ),
    ):
        if segs_use:
            lc = LineCollection(
                [s * 1e3 for s in segs_use],
                colors="#1a5276",
                linewidths=0.30 if ax is axes[0] else 0.55,
                alpha=0.85,
            )
            ax.add_collection(lc)
        if show_sym:
            ax.axvline(0.0, color="#7d3c98", lw=1.0, ls="--", alpha=0.7, label="symmetry_0 / eixo z=0 (θ=0°)")
        for center_yz, color, lbl in (
            (tip_yz, "#c0392b", f"IVI — topoSet ¼ esfera r={r_topo_mm:.2f} mm"),
            (acp_yz, "#d35400", f"Paracentese — topoSet ¼ esfera r={r_topo_mm:.2f} mm"),
        ):
            if ax is axes[1] and not np.allclose(center_yz, tip_yz):
                continue
            arc_z, arc_y = wedge_sphere_arc_yz(center_yz, r_topo_mm)
            ax.plot(
                arc_z,
                arc_y,
                ls="--",
                color=color,
                lw=1.4,
                label=lbl if (ax is axes[0] or np.allclose(center_yz, tip_yz)) else None,
            )
        ax.plot(
            tip_yz[0],
            tip_yz[1],
            "+",
            color="#c0392b",
            ms=10,
            mew=1.5,
            label="IVI (intra-vítreo) · centro z=0",
        )
        if ax is axes[0]:
            ax.plot(
                acp_yz[0],
                acp_yz[1],
                "x",
                color="#d35400",
                ms=9,
                mew=1.5,
                label="Paracentese (ACP) · centro z=0",
            )
            ax.annotate(
                "IVI",
                xy=tip_yz,
                xytext=(tip_yz[0] + 0.55, tip_yz[1] + 0.35),
                fontsize=9,
                color="#c0392b",
                arrowprops=dict(arrowstyle="->", color="#c0392b", lw=0.9),
            )
            ax.annotate(
                "Paracentese",
                xy=acp_yz,
                xytext=(acp_yz[0] + 0.55, acp_yz[1] - 0.45),
                fontsize=9,
                color="#d35400",
                arrowprops=dict(arrowstyle="->", color="#d35400", lw=0.9),
            )
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel(xlab)
        ax.set_ylabel(ylab)
        ax.set_title(title, fontsize=10)
        ax.grid(True, alpha=0.25)
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        if ax is axes[0]:
            ax.legend(loc="upper right", fontsize=7, framealpha=0.92)
        elif ax is axes[1]:
            ax.legend(loc="upper right", fontsize=8)

    fig.suptitle(
        f"{case_label} — malha fluida 3D ({mesh_level}) · setor 90° · {fluid_path.name}\n"
        f"IVI (+) e paracentese (×) no eixo z=0 · arco tracejado = topoSet (¼ esfera no wedge, r={r_topo_mm:.2f} mm)\n"
        f"Linha roxa z=0 = symmetry_0 (borda do setor; não é ac_inlet)",
        fontsize=10,
        y=0.99,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Wrote {out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mesh-level", default="M1", choices=["M1", "M2", "M3"])
    ap.add_argument("--fluid", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--case-label", default="doc-g2-sim2")
    ap.add_argument("--slab-half", type=float, default=8.0e-5, help="Half-width of meridional slab [m]")
    args = ap.parse_args()

    fluid = args.fluid or GEOM / f"eye_g2_fluid_lamminsalo_{args.mesh_level}.msh"
    out = args.out or FIGS / f"g2_fluid_mesh_cut_{args.mesh_level}.png"
    if not fluid.exists():
        raise SystemExit(f"missing {fluid} — run gen_meshes_ivi.sh")

    plot_g2_fluid_mesh(
        fluid, out, mesh_level=args.mesh_level, z_tol=args.slab_half, case_label=args.case_label
    )


if __name__ == "__main__":
    main()
