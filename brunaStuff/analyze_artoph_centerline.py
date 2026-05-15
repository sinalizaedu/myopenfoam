"""Extract centerline and radius profile of the ophthalmic artery (part_01).

Approach: slice the artery STL by planes perpendicular to z, compute centroid
and radius of each cross-section, then fit polynomials. Output:
  - centerline_artoph.csv : z, cx, cy, r_eq, r_min, r_max
  - relative_to_optic_nerve.csv : artery-vs-nerve separation along z
  - centerline_artoph.png : visual sanity check
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh

PARTS_DIR = Path(__file__).parent / "geom_mestrado_parts"
ART = PARTS_DIR / "part_01.stl"
ON = PARTS_DIR / "part_00.stl"


def slice_centerline(mesh: trimesh.Trimesh, z_levels: np.ndarray):
    rows = []
    for z in z_levels:
        section = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        if section is None:
            continue
        planar, _ = section.to_planar()
        for poly in planar.polygons_full:
            pts = np.array(poly.exterior.coords)
            cx, cy = pts[:, 0].mean(), pts[:, 1].mean()
            r = np.hypot(pts[:, 0] - cx, pts[:, 1] - cy)
            rows.append(
                {
                    "z": float(z),
                    "cx": float(cx),
                    "cy": float(cy),
                    "r_mean": float(r.mean()),
                    "r_min": float(r.min()),
                    "r_max": float(r.max()),
                    "n_pts": len(pts),
                }
            )
    return rows


def main() -> None:
    artery = trimesh.load_mesh(str(ART))
    nerve = trimesh.load_mesh(str(ON))

    z_min, z_max = artery.bounds[0, 2], artery.bounds[1, 2]
    z_levels = np.linspace(z_min + 0.5, z_max - 0.5, 60)

    art_rows = slice_centerline(artery, z_levels)
    nerve_rows = slice_centerline(nerve, z_levels)

    out_csv = PARTS_DIR / "centerline_artoph.csv"
    with out_csv.open("w") as f:
        f.write("z_mm,cx_mm,cy_mm,r_mean_mm,r_min_mm,r_max_mm,n_pts\n")
        for r in art_rows:
            f.write(
                f"{r['z']:.4f},{r['cx']:.4f},{r['cy']:.4f},"
                f"{r['r_mean']:.4f},{r['r_min']:.4f},{r['r_max']:.4f},{r['n_pts']}\n"
            )
    print(f"[write] {out_csv}  ({len(art_rows)} cross-sections)")

    art_z = np.array([r["z"] for r in art_rows])
    art_cx = np.array([r["cx"] for r in art_rows])
    art_cy = np.array([r["cy"] for r in art_rows])
    art_r = np.array([r["r_mean"] for r in art_rows])

    nerve_z = np.array([r["z"] for r in nerve_rows])
    nerve_cx = np.array([r["cx"] for r in nerve_rows])
    nerve_cy = np.array([r["cy"] for r in nerve_rows])
    nerve_r = np.array([r["r_mean"] for r in nerve_rows])

    print(f"\n[artery]")
    print(f"  z range: {art_z.min():.2f}  →  {art_z.max():.2f}  mm")
    print(f"  cx range: {art_cx.min():.2f}  →  {art_cx.max():.2f}  mm")
    print(f"  cy range: {art_cy.min():.2f}  →  {art_cy.max():.2f}  mm")
    print(f"  r mean:   {art_r.mean():.3f}  ±  {art_r.std():.3f}  mm")
    print(f"  r range:  {art_r.min():.3f}  →  {art_r.max():.3f}  mm")

    print(f"\n[nerve]")
    print(f"  z range: {nerve_z.min():.2f}  →  {nerve_z.max():.2f}  mm")
    print(f"  cx range: {nerve_cx.min():.2f}  →  {nerve_cx.max():.2f}  mm")
    print(f"  cy range: {nerve_cy.min():.2f}  →  {nerve_cy.max():.2f}  mm")
    print(f"  r mean:   {nerve_r.mean():.3f}  ±  {nerve_r.std():.3f}  mm")

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    axes[0].plot(art_cx, art_z, "o-", label="artéria oftálmica", color="crimson")
    axes[0].plot(
        nerve_cx, nerve_z, "s-", label="nervo óptico", color="steelblue", alpha=0.7
    )
    axes[0].set_xlabel("x (mm)")
    axes[0].set_ylabel("z (mm) — axial")
    axes[0].set_title("Vista lateral (xz)")
    axes[0].legend()
    axes[0].axis("equal")
    axes[0].grid(alpha=0.3)

    axes[1].plot(art_cy, art_z, "o-", label="artéria oftálmica", color="crimson")
    axes[1].plot(
        nerve_cy, nerve_z, "s-", label="nervo óptico", color="steelblue", alpha=0.7
    )
    axes[1].set_xlabel("y (mm)")
    axes[1].set_ylabel("z (mm)")
    axes[1].set_title("Vista lateral (yz)")
    axes[1].legend()
    axes[1].axis("equal")
    axes[1].grid(alpha=0.3)

    axes[2].plot(art_z, art_r, "o-", color="crimson", label="r artéria")
    axes[2].plot(nerve_z, nerve_r, "s-", color="steelblue", label="r nervo", alpha=0.7)
    axes[2].set_xlabel("z (mm)")
    axes[2].set_ylabel("raio médio (mm)")
    axes[2].set_title("Perfil de raio")
    axes[2].legend()
    axes[2].grid(alpha=0.3)

    fig.suptitle("Geometria Mestrado — centerlines extraídas do STL", fontsize=13)
    fig.tight_layout()
    out_png = PARTS_DIR / "centerline_artoph.png"
    fig.savefig(out_png, dpi=120)
    print(f"\n[write] {out_png}")


if __name__ == "__main__":
    main()
