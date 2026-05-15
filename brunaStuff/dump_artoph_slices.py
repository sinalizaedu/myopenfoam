"""Dump per-z slice details for part_01 to understand its real topology."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh

PARTS_DIR = Path(__file__).parent / "geom_mestrado_parts"
ART = PARTS_DIR / "part_01.stl"


def main() -> None:
    mesh = trimesh.load_mesh(str(ART))
    print(f"[part_01] bbox: {mesh.bounds}")

    z_levels = np.linspace(-29.5, -0.5, 30)
    fig, axes = plt.subplots(5, 6, figsize=(20, 16))
    for ax, z in zip(axes.flat, z_levels):
        section = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        if section is None:
            ax.set_title(f"z={z:.1f}  (no section)")
            continue
        planar, _ = section.to_planar()
        polys = list(planar.polygons_full)
        ax.set_title(f"z={z:.1f}  npoly={len(polys)}")
        for i, p in enumerate(polys):
            x, y = p.exterior.xy
            ax.fill(x, y, alpha=0.5, label=f"P{i} A={p.area:.2f}")
            for ring in p.interiors:
                rx, ry = ring.xy
                ax.fill(rx, ry, color="white")
            cx_ext = np.mean(p.exterior.coords.xy[0])
            cy_ext = np.mean(p.exterior.coords.xy[1])
            ax.plot(cx_ext, cy_ext, "k+", markersize=8)
        ax.axhline(0, color="gray", lw=0.5)
        ax.axvline(0, color="gray", lw=0.5)
        ax.set_xlim(-13, 4)
        ax.set_ylim(-6, 4)
        ax.set_aspect("equal")
        ax.grid(alpha=0.2)
        ax.legend(fontsize=6, loc="upper right")

    fig.suptitle(
        "part_01 — fatias perpendiculares ao eixo z (xy plane)\n"
        "+ = centróide do exterior do polígono, branco = furo interno",
        fontsize=12,
    )
    fig.tight_layout()
    out = PARTS_DIR / "slices_part01.png"
    fig.savefig(out, dpi=110)
    print(f"[write] {out}")

    print("\nDetailed dump:")
    for z in [-29.0, -25.0, -20.0, -15.0, -10.0, -5.0, -1.0]:
        section = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        planar, _ = section.to_planar()
        print(f"\n  z={z}")
        for i, p in enumerate(planar.polygons_full):
            cx, cy = p.centroid.x, p.centroid.y
            print(
                f"    poly {i}: area={p.area:.3f}  "
                f"centroid=({cx:.2f},{cy:.2f})  "
                f"bbox=({p.bounds[0]:.2f},{p.bounds[1]:.2f})→"
                f"({p.bounds[2]:.2f},{p.bounds[3]:.2f})  "
                f"interiors={len(p.interiors)}"
            )


if __name__ == "__main__":
    main()
