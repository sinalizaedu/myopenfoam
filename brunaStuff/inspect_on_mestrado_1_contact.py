"""Diagnostico visual do patch contact_local + campos de stress no on-mestrado-1.

Renderiza 3 vistas (lateral, axial, isometrica) mostrando:
  - malha externa (pia + sclera)
  - posicao das 2 faces do contact_local destacadas em vermelho
  - campo sigma_eq sobreposto na lateral
  - outros patches importantes (posterior_pia, anterior_sclera) com cor
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection
from matplotlib.patches import Circle

CASE = Path(__file__).resolve().parent.parent / "cases" / "on-mestrado-1" / "solid"
POLY = CASE / "constant" / "polyMesh"
TIME = CASE / "1"


def parse_points(path):
    text = path.read_text()
    out = []
    for m in re.finditer(r"\(([-0-9.eE+ ]+)\)", text):
        parts = m.group(1).split()
        if len(parts) == 3:
            out.append([float(x) for x in parts])
    return np.array(out)


def parse_faces(path):
    text = path.read_text()
    out = []
    for m in re.finditer(r"(\d+)\(([^)]*)\)", text):
        n = int(m.group(1))
        pts = [int(p) for p in m.group(2).split()]
        if len(pts) == n:
            out.append(pts)
    return out


def parse_boundary(path):
    text = path.read_text()
    patches = {}
    for m in re.finditer(
        r"(\w+)[\s\n]*\{[^}]*?nFaces\s+(\d+);[^}]*?startFace\s+(\d+);", text
    ):
        patches[m.group(1)] = (int(m.group(2)), int(m.group(3)))
    return patches


def parse_volScalar(path):
    text = path.read_text()
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\d+\s*\(([^)]+)\)", text)
    if not m:
        m2 = re.search(r"internalField\s+uniform\s+([0-9.eE+-]+);", text)
        if m2:
            return None
        raise RuntimeError(f"cannot parse {path}")
    return np.fromstring(m.group(1), sep=" ")


def main():
    pts = parse_points(POLY / "points")
    faces = parse_faces(POLY / "faces")
    patches = parse_boundary(POLY / "boundary")
    print(f"loaded {len(pts)} points, {len(faces)} faces, {len(patches)} patches")
    for name, (n, s) in patches.items():
        print(f"  {name:20s} nFaces={n:5d} startFace={s}")

    sigmaEq = parse_volScalar(TIME / "sigmaEq")
    print(f"loaded sigmaEq: {len(sigmaEq) if sigmaEq is not None else 'uniform'} cells")

    fig = plt.figure(figsize=(18, 12))

    ax_lat = fig.add_subplot(3, 2, 1)
    ax_lat.set_title("vista lateral GERAL (XZ plane, projetada em +X)")
    ax_lat.set_xlabel("z (mm)")
    ax_lat.set_ylabel("x (mm)")

    for name, color, label in [
        ("pia_outer", "lightgray", None),
        ("sclera_outer", "lightblue", None),
        ("posterior_pia", "yellow", "P_CSF=1333 Pa"),
        ("anterior_sclera", "green", "fixedDisp"),
        ("anterior_lc", "white", None),
        ("contact_local", "red", "P_contact=9034 Pa"),
    ]:
        if name not in patches:
            continue
        n_f, s_f = patches[name]
        polys = []
        for i in range(n_f):
            fpts = faces[s_f + i]
            verts = pts[fpts]
            if np.std(verts[:, 1]) < 0.6e-3:
                polys.append([(v[2] * 1000, v[0] * 1000) for v in verts])
        if polys:
            pc = PolyCollection(
                polys,
                facecolors=color,
                edgecolors="black",
                linewidths=0.2,
                alpha=0.9,
            )
            ax_lat.add_collection(pc)
            if label:
                ax_lat.plot([], [], "s", color=color, label=f"{name}: {label}", markersize=10)

    ax_lat.set_xlim(-2, 32)
    ax_lat.set_ylim(-3.5, 3.5)
    ax_lat.set_aspect("equal")
    ax_lat.legend(loc="upper right", fontsize=8)
    ax_lat.axvline(22.5, color="red", linestyle=":", alpha=0.5, linewidth=0.8)
    ax_lat.text(22.5, 3.2, "z=22.5", ha="center", color="red", fontsize=8)
    ax_lat.grid(True, alpha=0.3)

    ax_lat_zoom = fig.add_subplot(3, 2, 2)
    ax_lat_zoom.set_title("ZOOM em z=20-25 mm (vista lateral, +X)")
    ax_lat_zoom.set_xlabel("z (mm)")
    ax_lat_zoom.set_ylabel("x (mm)")
    for name, color, label in [
        ("pia_outer", "lightgray", None),
        ("contact_local", "red", "contact_local"),
    ]:
        if name not in patches:
            continue
        n_f, s_f = patches[name]
        polys = []
        for i in range(n_f):
            fpts = faces[s_f + i]
            verts = pts[fpts]
            if np.std(verts[:, 1]) < 0.6e-3 and verts[:, 2].min() * 1000 > 18 and verts[:, 2].max() * 1000 < 27:
                polys.append([(v[2] * 1000, v[0] * 1000) for v in verts])
        if polys:
            ax_lat_zoom.add_collection(
                PolyCollection(polys, facecolors=color, edgecolors="black", linewidths=0.4, alpha=0.9)
            )
            if label:
                ax_lat_zoom.plot([], [], "s", color=color, label=label, markersize=12)
    ax_lat_zoom.set_xlim(20, 25)
    ax_lat_zoom.set_ylim(2.35, 2.6)
    ax_lat_zoom.set_aspect("equal")
    ax_lat_zoom.axvline(22.5, color="red", linestyle=":", alpha=0.6)
    ax_lat_zoom.legend(loc="upper right", fontsize=9)
    ax_lat_zoom.grid(True, alpha=0.3)

    ax_axial = fig.add_subplot(3, 2, 3)
    ax_axial.set_title("vista axial em z=22.5 mm (XY plane)")
    ax_axial.set_xlabel("x (mm)")
    ax_axial.set_ylabel("y (mm)")
    ax_axial.add_patch(Circle((0, 0), 1.50, fill=False, edgecolor="lightgray", linewidth=1, label="r_on=1.50"))
    ax_axial.add_patch(Circle((0, 0), 2.50, fill=False, edgecolor="black", linewidth=1, label="r_pia=2.50"))

    if "contact_local" in patches:
        n_f, s_f = patches["contact_local"]
        for i in range(n_f):
            fpts = faces[s_f + i]
            verts = pts[fpts]
            polys_xy = [(v[0] * 1000, v[1] * 1000) for v in verts]
            from matplotlib.patches import Polygon
            ax_axial.add_patch(
                Polygon(polys_xy, closed=True, facecolor="red", edgecolor="darkred", alpha=0.8)
            )

    box_x = [2.40, 2.65, 2.65, 2.40, 2.40]
    box_y = [-0.50, -0.50, 0.50, 0.50, -0.50]
    ax_axial.plot(box_x, box_y, "r--", linewidth=1, alpha=0.6, label="topoSet box")
    ax_axial.set_xlim(-3.0, 3.5)
    ax_axial.set_ylim(-3.0, 3.0)
    ax_axial.set_aspect("equal")
    ax_axial.legend(loc="upper left", fontsize=8)
    ax_axial.grid(True, alpha=0.3)

    ax_axial_zoom = fig.add_subplot(3, 2, 4)
    ax_axial_zoom.set_title("ZOOM axial em z=22.5 mm (XY, eixo +X)")
    ax_axial_zoom.set_xlabel("x (mm)")
    ax_axial_zoom.set_ylabel("y (mm)")
    ax_axial_zoom.add_patch(Circle((0, 0), 2.50, fill=False, edgecolor="black", linewidth=1))
    if "contact_local" in patches:
        n_f, s_f = patches["contact_local"]
        for i in range(n_f):
            fpts = faces[s_f + i]
            verts = pts[fpts]
            polys_xy = [(v[0] * 1000, v[1] * 1000) for v in verts]
            from matplotlib.patches import Polygon
            ax_axial_zoom.add_patch(
                Polygon(polys_xy, closed=True, facecolor="red", edgecolor="darkred", alpha=0.8)
            )
            cx, cy = np.mean(polys_xy, axis=0)
            ax_axial_zoom.annotate(f"face {i}", (cx, cy), xytext=(cx + 0.05, cy + 0.15),
                                   fontsize=7, color="darkred",
                                   arrowprops=dict(arrowstyle="->", color="darkred", alpha=0.5))
    ax_axial_zoom.set_xlim(2.30, 2.70)
    ax_axial_zoom.set_ylim(-0.6, 0.6)
    ax_axial_zoom.set_aspect("equal")
    ax_axial_zoom.grid(True, alpha=0.3)
    ax_axial_zoom.text(2.32, -0.55, "Patch = 2 faces:\n  face 0: y<0 (theta=-5.63 deg)\n  face 1: y>0 (theta=+5.63 deg)\nSeparadas pela linha y=0",
                       fontsize=8, va="bottom", ha="left",
                       bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8))

    ax_sig = fig.add_subplot(3, 2, 5)
    ax_sig.set_title(f"sigmaEq (Pa) - max={sigmaEq.max():.0f}, mean={sigmaEq.mean():.0f}")
    ax_sig.hist(sigmaEq, bins=100, color="steelblue", edgecolor="black", linewidth=0.3)
    ax_sig.set_xlabel("sigmaEq (Pa)")
    ax_sig.set_ylabel("celulas")
    ax_sig.set_yscale("log")
    ax_sig.axvline(sigmaEq.max(), color="red", linestyle=":", label=f"max={sigmaEq.max():.0f} Pa")
    ax_sig.axvline(sigmaEq.mean(), color="orange", linestyle=":", label=f"mean={sigmaEq.mean():.0f} Pa")
    ax_sig.legend(fontsize=8)

    ax_info = fig.add_subplot(3, 2, 6)
    ax_info.axis("off")
    info = []
    info.append("contact_local: posicao das 2 faces")
    if "contact_local" in patches:
        n_f, s_f = patches["contact_local"]
        info.append(f"  nFaces = {n_f}")
        for i in range(n_f):
            fpts = faces[s_f + i]
            verts = pts[fpts]
            cx, cy, cz = verts.mean(axis=0) * 1000
            r = math.hypot(cx, cy)
            theta = math.degrees(math.atan2(cy, cx))
            info.append(
                f"  face {i}: (x,y,z)=({cx:6.3f},{cy:7.3f},{cz:6.3f}) mm  r={r:.3f}mm  theta={theta:+.2f}deg"
            )
        info.append("")
    info.append("Outros patches relevantes:")
    for name in ("posterior_pia", "anterior_sclera", "anterior_lc", "pia_outer", "sclera_outer"):
        if name in patches:
            n_f, _ = patches[name]
            info.append(f"  {name:18s}: {n_f} faces")
    info.append("")
    info.append("Cargas:")
    info.append("  P_CSF=1333 Pa em posterior_pia (axial -> +z)")
    info.append("  P_contact=9034 Pa em contact_local (radial -> -X)")
    info.append("  Winkler k=200 kPa/m em pia_outer (gordura)")
    ax_info.text(
        0.02, 0.98, "\n".join(info),
        ha="left", va="top",
        family="monospace", fontsize=8,
        transform=ax_info.transAxes,
    )

    fig.suptitle("Diagnostico on-mestrado-1: contact_local + outros patches", fontsize=12, weight="bold")
    fig.tight_layout()
    out = Path(__file__).resolve().parent / "inspect_on_mestrado_1_contact.png"
    fig.savefig(out, dpi=140, bbox_inches="tight")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
