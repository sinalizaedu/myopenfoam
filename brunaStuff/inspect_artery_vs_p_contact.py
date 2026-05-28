#!/usr/bin/env python3
"""
Verifica como a artery_outer.stl em ao-mestrado se comporta em relacao
a posicao P_contact = (0, 2.5, 18.5) mm definida em on-mestrado.

Checagens:
1) Vertice mais proximo do ponto P_contact (deveria ser ~zero).
2) Para cada vertice em z in [0, 30] mm: distancia ao eixo z.
   Quantos vertices invadem o cilindro ONS (R = 2.5 mm)?
3) Para cada vertice em z in [0, 30] mm: distancia ao eixo z e ao ponto
   P_contact. Identifica o vertice realmente mais proximo do ONS,
   nao apenas o que ficou em P_contact apos translacao.
4) Salva um plot mostrando a interseccao xy e a vista 3D da arteria + cilindros.
"""
from __future__ import annotations

from pathlib import Path

import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

REPO = Path(__file__).resolve().parents[1]
CASE = REPO / "cases" / "ao-mestrado" / "constant" / "triSurface"
OUTER = CASE / "artery_outer.stl"

R_ON_MM = 1.5
R_ONS_MM = 2.5
Z0_MM, Z1_MM = 0.0, 30.0
P_CONTACT_MM = np.array([0.0, 2.5, 18.5])


def read_stl_facets(path: Path) -> tuple[np.ndarray, np.ndarray]:
    verts: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int]] = []
    key_to_idx: dict[tuple[float, float, float], int] = {}
    buf: list[tuple[float, float, float]] = []

    def add_v(x: float, y: float, z: float) -> int:
        k = (round(x, 9), round(y, 9), round(z, 9))
        i = key_to_idx.get(k)
        if i is not None:
            return i
        i = len(verts)
        verts.append((x, y, z))
        key_to_idx[k] = i
        return i

    with path.open() as f:
        for line in f:
            ls = line.strip()
            if ls.startswith("vertex"):
                p = ls.split()
                buf.append((float(p[1]), float(p[2]), float(p[3])))
                if len(buf) == 3:
                    i0 = add_v(*buf[0])
                    i1 = add_v(*buf[1])
                    i2 = add_v(*buf[2])
                    faces.append((i0, i1, i2))
                    buf.clear()
    return np.array(verts, dtype=np.float64), np.array(faces, dtype=np.int64)


V_m, F = read_stl_facets(OUTER)
V = V_m * 1e3  # m -> mm

# 1) vertice mais proximo do ponto P_contact
d_to_P = np.linalg.norm(V - P_CONTACT_MM, axis=1)
i_closest_to_P = int(np.argmin(d_to_P))
v_closest_to_P = V[i_closest_to_P]
d_min_to_P = float(d_to_P[i_closest_to_P])

# 2 / 3) vertices in z in [0, 30] mm
mask_z = (V[:, 2] >= Z0_MM) & (V[:, 2] <= Z1_MM)
V_band = V[mask_z]
print(f"vertices total                                  : {len(V)}")
print(f"vertices em z in [0, 30] mm                      : {len(V_band)}")

# distance ao eixo z (cilindro)
r_band = np.hypot(V_band[:, 0], V_band[:, 1])

# vertices invadindo o cilindro ONS
inside_ons = r_band < R_ONS_MM - 1e-6
n_inside_ons = int(inside_ons.sum())
inside_on = r_band < R_ON_MM - 1e-6
n_inside_on = int(inside_on.sum())

# vertice REALMENTE mais proximo do eixo z
i_closest_axis_band = int(np.argmin(r_band))
v_closest_axis = V_band[i_closest_axis_band]
r_closest_axis = float(r_band[i_closest_axis_band])

# vertice mais proximo da SUPERFICIE ONS (R=2.5)
d_to_ons_surface = np.abs(r_band - R_ONS_MM)
i_closest_ons = int(np.argmin(d_to_ons_surface))
v_closest_ons = V_band[i_closest_ons]

# distancia minima vertice -> superficie ONS lateral (sinal: negativo = invasao)
sd_to_ons = r_band - R_ONS_MM  # >0 fora do cilindro, <0 dentro
i_min_sd = int(np.argmin(sd_to_ons))

# RESUMO
print("\n=== Vertice mais proximo do ponto P_contact (0, 2.5, 18.5) mm ===")
print(f"  idx={i_closest_to_P}  pos_mm=({v_closest_to_P[0]:+.4f}, "
      f"{v_closest_to_P[1]:+.4f}, {v_closest_to_P[2]:+.4f})")
print(f"  distancia 3D ao alvo: {d_min_to_P*1000:.3f} um")

print("\n=== Cilindro ONS (R=2.5 mm) entre z=0 e z=30 mm ===")
print(f"  vertices DENTRO do cilindro ONS                : {n_inside_ons}")
print(f"  vertices DENTRO do cilindro ON (R=1.5 mm)      : {n_inside_on}")
print(f"  vertice mais proximo do eixo z  : "
      f"({v_closest_axis[0]:+.4f}, {v_closest_axis[1]:+.4f}, "
      f"{v_closest_axis[2]:+.4f}) mm,  r_xy = {r_closest_axis:.4f} mm")
print(f"  vertice mais proximo da superficie do ONS: "
      f"({v_closest_ons[0]:+.4f}, {v_closest_ons[1]:+.4f}, "
      f"{v_closest_ons[2]:+.4f}) mm")
print(f"  signed distance min (negativa = INVASAO): "
      f"{sd_to_ons[i_min_sd]:.4f} mm  em "
      f"({V_band[i_min_sd, 0]:+.4f}, {V_band[i_min_sd, 1]:+.4f}, "
      f"{V_band[i_min_sd, 2]:+.4f}) mm")

# Plot
fig = plt.figure(figsize=(15, 5))

# A) xy slice em z=18.5 +- 0.5 mm
ax_xy = fig.add_subplot(1, 3, 1)
sl = (V[:, 2] >= 18.0) & (V[:, 2] <= 19.0)
ax_xy.scatter(V[sl, 0], V[sl, 1], s=4, c="tab:red", alpha=0.7, label="artery_outer (z 18-19 mm)")
th = np.linspace(0, 2*np.pi, 200)
ax_xy.plot(R_ON_MM*np.cos(th), R_ON_MM*np.sin(th), "tab:blue", lw=1.2, label=f"ON R={R_ON_MM} mm")
ax_xy.plot(R_ONS_MM*np.cos(th), R_ONS_MM*np.sin(th), "tab:cyan", lw=1.5, label=f"ONS R={R_ONS_MM} mm")
ax_xy.plot(P_CONTACT_MM[0], P_CONTACT_MM[1], "*", c="darkred", ms=14, label="P_contact alvo")
ax_xy.set_xlim(-4, 4)
ax_xy.set_ylim(-4, 4)
ax_xy.set_aspect("equal")
ax_xy.grid(alpha=0.3)
ax_xy.legend(fontsize=8, loc="lower left")
ax_xy.set_xlabel("x (mm)"); ax_xy.set_ylabel("y (mm)")
ax_xy.set_title("Slice xy em z = 18.5 +/- 0.5 mm")

# B) xz scatter
ax_xz = fig.add_subplot(1, 3, 2)
ax_xz.scatter(V[:, 0], V[:, 2], s=2, c="tab:red", alpha=0.4, label="artery_outer (todos)")
ax_xz.fill_betweenx([Z0_MM, Z1_MM], -R_ONS_MM, R_ONS_MM, color="tab:cyan", alpha=0.2,
                    label=f"ONS R={R_ONS_MM} mm (z 0-30)")
ax_xz.fill_betweenx([Z0_MM, Z1_MM], -R_ON_MM, R_ON_MM, color="tab:blue", alpha=0.25,
                    label=f"ON R={R_ON_MM} mm")
ax_xz.plot(P_CONTACT_MM[0], P_CONTACT_MM[2], "*", c="darkred", ms=14, label="P_contact")
ax_xz.set_aspect("equal")
ax_xz.grid(alpha=0.3); ax_xz.legend(fontsize=8, loc="lower left")
ax_xz.set_xlabel("x (mm)"); ax_xz.set_ylabel("z (mm)")
ax_xz.set_title("Projecao xz")

# C) yz scatter
ax_yz = fig.add_subplot(1, 3, 3)
ax_yz.scatter(V[:, 1], V[:, 2], s=2, c="tab:red", alpha=0.4, label="artery_outer (todos)")
ax_yz.fill_betweenx([Z0_MM, Z1_MM], -R_ONS_MM, R_ONS_MM, color="tab:cyan", alpha=0.2,
                    label=f"ONS R={R_ONS_MM} mm (z 0-30)")
ax_yz.fill_betweenx([Z0_MM, Z1_MM], -R_ON_MM, R_ON_MM, color="tab:blue", alpha=0.25,
                    label=f"ON R={R_ON_MM} mm")
ax_yz.plot(P_CONTACT_MM[1], P_CONTACT_MM[2], "*", c="darkred", ms=14, label="P_contact")
ax_yz.set_aspect("equal")
ax_yz.grid(alpha=0.3); ax_yz.legend(fontsize=8, loc="lower left")
ax_yz.set_xlabel("y (mm)"); ax_yz.set_ylabel("z (mm)")
ax_yz.set_title("Projecao yz")

plt.tight_layout()
out = REPO / "brunaStuff" / "inspect_artery_vs_p_contact.png"
plt.savefig(out, dpi=140)
print(f"\n[plot] {out.relative_to(REPO)}")

summary = {
    "P_contact_mm": P_CONTACT_MM.tolist(),
    "closest_vertex_to_P_contact_mm": v_closest_to_P.tolist(),
    "distance_to_P_contact_um": d_min_to_P * 1000,
    "n_vertices_inside_ONS_cylinder_R2.5mm_z[0,30]": n_inside_ons,
    "n_vertices_inside_ON_cylinder_R1.5mm_z[0,30]": n_inside_on,
    "min_radial_distance_in_band_mm": r_closest_axis,
    "vertex_closest_to_axis_mm": v_closest_axis.tolist(),
    "min_signed_distance_to_ONS_mm": float(sd_to_ons[i_min_sd]),
    "vertex_at_min_signed_distance_mm": V_band[i_min_sd].tolist(),
}
out_json = REPO / "brunaStuff" / "inspect_artery_vs_p_contact.json"
out_json.write_text(json.dumps(summary, indent=2))
print(f"[json] {out_json.relative_to(REPO)}")
