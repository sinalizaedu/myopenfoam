#!/usr/bin/env python3
"""Renderiza o estado atual da arteria oftalmica de cases/ao-mestrado vs.
o cilindro ONS (R=2.5 mm, z em [0,30] mm), com o ponto P_contact marcado.

Painel 3D: artery_outer.stl (parede anatomica) + cilindro ONS transparente
           + cilindro ON pontilhado + estrela em P_contact.
Painel xy: corte em z = 18.5 +/- 0.5 mm com circulos ON e ONS.
Painel xz: projecao com retangulo do ONS (lembrete: filtra so projecao,
           nao reflete invasao 3D real).
Painel "plot polar" da centerline: r_xy(s) ao longo da centerline,
           para z em [0, 30] mm. Mostra que so um ponto atinge o minimo
           r_xy = 3.25 mm (= R_ONS + R_outer_tube), tangencia unica.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial import cKDTree
from skimage.morphology import skeletonize

REPO = Path(__file__).resolve().parents[1]
TRI = REPO / "cases" / "ao-mestrado" / "constant" / "triSurface"
OUT = REPO / "brunaStuff" / "render_artery_p_contact.png"

R_ON_MM = 1.5
R_ONS_MM = 2.5
R_OUTER_TUBE_MM = 0.75
P_CONTACT_THETA_DEG = -30.0
P_CONTACT_Z_MM = 25.0
_th = np.radians(P_CONTACT_THETA_DEG)
P_CONTACT_MM = np.array([
    R_ONS_MM * np.cos(_th), R_ONS_MM * np.sin(_th), P_CONTACT_Z_MM,
])
P_CL_TARGET_MM = np.array([
    (R_ONS_MM + R_OUTER_TUBE_MM) * np.cos(_th),
    (R_ONS_MM + R_OUTER_TUBE_MM) * np.sin(_th),
    P_CONTACT_Z_MM,
])
Z0_MM, Z1_MM = 0.0, 30.0


def cyl(R, z_lo, z_hi, n=64, m=24):
    th = np.linspace(0, 2*np.pi, n)
    z = np.linspace(z_lo, z_hi, m)
    T, Z = np.meshgrid(th, z)
    return R*np.cos(T), R*np.sin(T), Z


def extract_centerline(mesh: trimesh.Trimesh, pitch_mm: float = 0.15) -> np.ndarray:
    pitch_m = pitch_mm * 1e-3
    vox = mesh.voxelized(pitch=pitch_m).fill()
    skel = skeletonize(vox.matrix.astype(bool))
    pts = vox.indices_to_points(np.argwhere(skel))
    tree = cKDTree(pts)
    counts = tree.query_ball_point(pts, r=1.8 * pitch_m, return_length=True)
    start = int(np.argmin(counts))
    n = len(pts)
    visited = np.zeros(n, dtype=bool)
    order = [start]; visited[start] = True; cur = start
    while len(order) < n:
        _, idxs = tree.query(pts[cur], k=min(20, n))
        nxt = None
        for i in idxs:
            if not visited[i]:
                nxt = int(i); break
        if nxt is None: break
        order.append(nxt); visited[nxt] = True; cur = nxt
    return pts[order] * 1e3  # m -> mm


outer = trimesh.load_mesh(str(TRI / "artery_outer.stl"))
V = outer.vertices * 1e3  # mm
F = outer.faces

cl = extract_centerline(outer, pitch_mm=0.15)

# arc-length along centerline
seg = np.linalg.norm(np.diff(cl, axis=0), axis=1)
s = np.concatenate([[0.0], np.cumsum(seg)])  # mm

fig = plt.figure(figsize=(16, 10))

# --- A: 3D oblique ---
ax3 = fig.add_subplot(2, 3, 1, projection="3d")
coll = Poly3DCollection(V[F], facecolor="tab:red", edgecolor="none", alpha=0.55)
ax3.add_collection3d(coll)
# ONS cylinder (transparent cyan)
X, Y, Z = cyl(R_ONS_MM, Z0_MM, Z1_MM)
ax3.plot_surface(X, Y, Z, color="tab:cyan", alpha=0.18, edgecolor="none")
# ON cylinder (transparent blue)
X, Y, Z = cyl(R_ON_MM, Z0_MM, Z1_MM)
ax3.plot_surface(X, Y, Z, color="tab:blue", alpha=0.10, edgecolor="none")
# Centerline
ax3.plot(cl[:, 0], cl[:, 1], cl[:, 2], "k-", lw=1.5, label="centerline")
ax3.plot(*P_CL_TARGET_MM, "kX", ms=10,
         label=f"centerline alvo ({P_CL_TARGET_MM[0]:+.2f},{P_CL_TARGET_MM[1]:+.2f},{P_CL_TARGET_MM[2]:.1f})")
ax3.plot(*P_CONTACT_MM, "*", c="darkred", ms=14,
         label=f"P_contact ({P_CONTACT_MM[0]:+.2f},{P_CONTACT_MM[1]:+.2f},{P_CONTACT_MM[2]:.1f})")
ax3.set_xlabel("x (mm)"); ax3.set_ylabel("y (mm)"); ax3.set_zlabel("z (mm)")
ax3.set_title("artery_outer.stl + ONS (R=2.5) + ON (R=1.5)")
ax3.set_xlim(-13, 7); ax3.set_ylim(-7, 5); ax3.set_zlim(-5, 36)
ax3.view_init(elev=15, azim=-65)
ax3.legend(fontsize=7, loc="upper left")

# --- B: 3D zoom on contact zone ---
axz = fig.add_subplot(2, 3, 2, projection="3d")
coll2 = Poly3DCollection(V[F], facecolor="tab:red", edgecolor="none", alpha=0.7)
axz.add_collection3d(coll2)
X, Y, Z = cyl(R_ONS_MM, Z0_MM, Z1_MM, n=80, m=40)
axz.plot_surface(X, Y, Z, color="tab:cyan", alpha=0.25, edgecolor="none")
axz.plot(cl[:, 0], cl[:, 1], cl[:, 2], "k-", lw=1.5)
axz.plot(*P_CL_TARGET_MM, "kX", ms=10)
axz.plot(*P_CONTACT_MM, "*", c="darkred", ms=18)
axz.set_xlabel("x"); axz.set_ylabel("y"); axz.set_zlabel("z")
axz.set_title(f"Zoom: zona de contato (z ~ {P_CONTACT_Z_MM:.1f} mm)")
_dx, _dy, _dz = 3.5, 3.5, 4.0
axz.set_xlim(P_CONTACT_MM[0]-_dx, P_CONTACT_MM[0]+_dx)
axz.set_ylim(P_CONTACT_MM[1]-_dy, P_CONTACT_MM[1]+_dy)
axz.set_zlim(P_CONTACT_MM[2]-_dz, P_CONTACT_MM[2]+_dz)
axz.view_init(elev=18, azim=-50)

# --- C: r_xy(s) along centerline ---
axr = fig.add_subplot(2, 3, 3)
mask = (cl[:, 2] >= Z0_MM) & (cl[:, 2] <= Z1_MM)
axr.plot(s, np.hypot(cl[:, 0], cl[:, 1]), "k-", lw=1.2, label="r_xy(s) centerline")
axr.fill_between(s, 0, R_ONS_MM, where=mask, color="tab:cyan", alpha=0.15,
                 label=f"ONS (R={R_ONS_MM} mm)")
axr.axhline(R_ONS_MM + R_OUTER_TUBE_MM, ls="--", c="tab:red",
            label=f"alvo r_xy = {R_ONS_MM + R_OUTER_TUBE_MM} mm")
axr.axhline(R_ONS_MM, ls="-.", c="tab:cyan", alpha=0.6,
            label=f"R_ONS = {R_ONS_MM} mm")
axr.set_xlabel("arclength s (mm)")
axr.set_ylabel("r_xy (mm)")
axr.set_title("Distancia da centerline ao eixo z\n(min unico = tangencia em P_contact)")
axr.legend(fontsize=8, loc="lower right")
axr.grid(alpha=0.3)
axr.set_ylim(0, max(8, np.hypot(cl[:, 0], cl[:, 1]).max() + 1))

# --- D: xy slice z = 18.5 +- 0.5 mm ---
ax_xy = fig.add_subplot(2, 3, 4)
_zlo, _zhi = P_CONTACT_Z_MM - 0.5, P_CONTACT_Z_MM + 0.5
sl = (V[:, 2] >= _zlo) & (V[:, 2] <= _zhi)
ax_xy.scatter(V[sl, 0], V[sl, 1], s=4, c="tab:red", alpha=0.8,
              label=f"artery_outer (z {_zlo:.1f}-{_zhi:.1f} mm)")
th = np.linspace(0, 2*np.pi, 200)
ax_xy.plot(R_ON_MM*np.cos(th), R_ON_MM*np.sin(th), "tab:blue",
           lw=1.0, label=f"ON R={R_ON_MM} mm")
ax_xy.plot(R_ONS_MM*np.cos(th), R_ONS_MM*np.sin(th), "tab:cyan",
           lw=1.5, label=f"ONS R={R_ONS_MM} mm")
ax_xy.plot(*(R_ONS_MM + R_OUTER_TUBE_MM)*np.array([np.cos(th), np.sin(th)]),
           "tab:red", ls=":", lw=1.0, label="R alvo centerline = 3.25 mm")
ax_xy.plot(P_CONTACT_MM[0], P_CONTACT_MM[1], "*", c="darkred", ms=14, label="P_contact")
ax_xy.plot(P_CL_TARGET_MM[0], P_CL_TARGET_MM[1], "X", c="black", ms=10,
           label="centerline alvo")
ax_xy.set_xlim(-5, 5); ax_xy.set_ylim(-5, 5)
ax_xy.set_aspect("equal")
ax_xy.grid(alpha=0.3); ax_xy.legend(fontsize=7, loc="lower left")
ax_xy.set_xlabel("x (mm)"); ax_xy.set_ylabel("y (mm)")
ax_xy.set_title(f"Corte xy em z = {P_CONTACT_Z_MM:.1f} +/- 0.5 mm")

# --- E: r_xy(z) histogram-like for ALL wall vertices ---
ax_h = fig.add_subplot(2, 3, 5)
mask = (V[:, 2] >= Z0_MM) & (V[:, 2] <= Z1_MM)
rxy_band = np.hypot(V[mask, 0], V[mask, 1])
zb = V[mask, 2]
ax_h.scatter(zb, rxy_band, s=2, c="tab:red", alpha=0.4, label="parede anatomica")
ax_h.plot(cl[(cl[:,2]>=Z0_MM)&(cl[:,2]<=Z1_MM), 2],
          np.hypot(cl[(cl[:,2]>=Z0_MM)&(cl[:,2]<=Z1_MM), 0],
                   cl[(cl[:,2]>=Z0_MM)&(cl[:,2]<=Z1_MM), 1]),
          "k-", lw=1.2, label="centerline")
ax_h.axhline(R_ONS_MM, ls="--", c="tab:cyan", label=f"R_ONS = {R_ONS_MM}")
ax_h.axhline(R_ONS_MM + R_OUTER_TUBE_MM, ls=":", c="tab:red",
             label=f"alvo cl = {R_ONS_MM+R_OUTER_TUBE_MM}")
ax_h.set_xlabel("z (mm)"); ax_h.set_ylabel("r_xy (mm)")
ax_h.set_title("r_xy(z): vertices da parede e centerline em z[0,30]")
ax_h.legend(fontsize=8, loc="upper right")
ax_h.grid(alpha=0.3)
ax_h.set_xlim(Z0_MM, Z1_MM); ax_h.set_ylim(0, max(12, rxy_band.max()+1))

# --- F: text panel summary ---
ax_t = fig.add_subplot(2, 3, 6)
ax_t.axis("off")
sj = (TRI / "_artery_translated_summary.json")
hj = (REPO / "cases" / "ao-mestrado" / "constant" / "meshHints.json")
text = []
if sj.exists():
    s_doc = json.loads(sj.read_text())
    d = s_doc.get("delta_translation_mm", [0, 0, 0])
    a = s_doc.get("after_translation", {})
    text.append("=== translate_artery_to_p_contact ===")
    text.append(f"P_contact alvo : ({P_CONTACT_MM[0]:+.2f}, {P_CONTACT_MM[1]:+.2f}, {P_CONTACT_MM[2]:.1f}) mm")
    text.append(f"               theta={P_CONTACT_THETA_DEG:+.1f} deg, +X-Y quadrant")
    text.append(f"P_centerline   : ({P_CL_TARGET_MM[0]:+.2f}, {P_CL_TARGET_MM[1]:+.2f}, {P_CL_TARGET_MM[2]:.1f}) mm")
    text.append(f"R_ONS          : 2.5 mm")
    text.append(f"R_outer_tube   : 0.75 mm")
    text.append("")
    text.append(f"|delta|        : {np.linalg.norm(np.array(d)):.4f} mm")
    text.append(f"delta          : ({d[0]:+.4f}, {d[1]:+.4f}, {d[2]:+.4f}) mm")
    text.append("")
    text.append(f"after_translation:")
    text.append(f"  cl min r_xy   : {a.get('centerline_min_r_xy_mm', '?'):.4f} mm")
    text.append(f"  wall min r_xy : {a.get('wall_min_r_xy_mm_in_z_band', '?'):.4f} mm")
    text.append(f"  wall verts in ONS: {a.get('n_wall_vertices_inside_ons_cylinder', '?')}")
ax_t.text(0.03, 0.97, "\n".join(text), transform=ax_t.transAxes,
          fontsize=9, family="monospace", va="top")

plt.tight_layout()
plt.savefig(OUT, dpi=120)
print(f"[write] {OUT.relative_to(REPO)}")
