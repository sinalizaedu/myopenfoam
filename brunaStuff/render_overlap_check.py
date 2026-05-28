"""Verifica visualmente que a artéria curva (após shift +30 mm em z) está
sobreposta ao nervo óptico do caso on-mestrado.

O nervo do on-mestrado é um cilindro analítico (r=1.5 mm, z=0..30 mm) — não
existe STL dele; é definido só no blockMeshDict. Para a checagem, geramos
aqui um cilindro analítico equivalente e desenhamos junto com:
    - nerve.stl    (do STL original, agora deslocado para z=[0, 30])
    - artery.stl   (do STL original, agora deslocado para z≈[0, 30])
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

REPO = Path(__file__).resolve().parent.parent
TRI = REPO / "cases" / "artoph-curva-mestrado" / "solid" / "constant" / "triSurface"
OUT = REPO / "brunaStuff" / "render_overlap_check.png"


def add_mesh(ax, mesh: trimesh.Trimesh, color: str, alpha: float, label: str):
    verts = mesh.vertices * 1e3  # m → mm para plotar
    faces = mesh.faces
    coll = Poly3DCollection(
        verts[faces], facecolor=color, edgecolor="none", alpha=alpha
    )
    ax.add_collection3d(coll)
    print(
        f"  {label:20s}  bounds(mm) "
        f"x[{verts[:,0].min():7.2f},{verts[:,0].max():7.2f}] "
        f"y[{verts[:,1].min():7.2f},{verts[:,1].max():7.2f}] "
        f"z[{verts[:,2].min():7.2f},{verts[:,2].max():7.2f}]"
    )


def analytical_nerve_cylinder(radius_mm=1.5, z_min_mm=0.0, z_max_mm=30.0, n=48):
    """Gera um cilindro estilo on-mestrado (r=1.5 mm, eixo z, z ∈ [0,30] mm)."""
    theta = np.linspace(0, 2 * np.pi, n, endpoint=False)
    z = np.linspace(z_min_mm, z_max_mm, 30)
    xs = radius_mm * np.cos(theta)
    ys = radius_mm * np.sin(theta)
    T, Z = np.meshgrid(theta, z)
    X = radius_mm * np.cos(T)
    Y = radius_mm * np.sin(T)
    return X, Y, Z


nerve_stl = trimesh.load_mesh(TRI / "nerve.stl")
artery_stl = trimesh.load_mesh(TRI / "artery.stl")
artery_orig = trimesh.load_mesh(TRI / "artery_unscaled.stl") if (
    TRI / "artery_unscaled.stl"
).exists() else None

fig = plt.figure(figsize=(13, 6))

# ── View 1: 3D oblique ────────────────────────────────────────────────────
ax1 = fig.add_subplot(1, 2, 1, projection="3d")
print("[bounds]")
add_mesh(ax1, nerve_stl, "tab:blue", 0.20, "nerve.stl (STL)")
if artery_orig is not None:
    add_mesh(ax1, artery_orig, "tab:gray", 0.15, "artery (unscaled)")
add_mesh(ax1, artery_stl, "tab:red", 0.70, "artery.stl (scaled)")

# Cilindro analítico do on-mestrado, transparente, para comparar
X, Y, Z = analytical_nerve_cylinder()
ax1.plot_surface(X, Y, Z, color="tab:cyan", alpha=0.20, edgecolor="none")
print("  on-mestrado nerve     bounds(mm) "
      f"x[{X.min():7.2f},{X.max():7.2f}] "
      f"y[{Y.min():7.2f},{Y.max():7.2f}] "
      f"z[{Z.min():7.2f},{Z.max():7.2f}]")

ax1.set_xlabel("x (mm)")
ax1.set_ylabel("y (mm)")
ax1.set_zlabel("z (mm)")
ax1.set_title("Artéria curva + nervo óptico (mesmo eixo z agora)")
ax1.view_init(elev=20, azim=-65)
# Bounding cube to equalize aspect
for lim_fn, lim in [
    (ax1.set_xlim, (-14, 6)),
    (ax1.set_ylim, (-6, 5)),
    (ax1.set_zlim, (-4, 35)),
]:
    lim_fn(*lim)

# ── View 2: projeção lateral (xz) ────────────────────────────────────────
ax2 = fig.add_subplot(1, 2, 2)
ax2.set_aspect("equal")
ax2.scatter(
    nerve_stl.vertices[:, 0] * 1e3,
    nerve_stl.vertices[:, 2] * 1e3,
    s=2,
    c="tab:blue",
    alpha=0.4,
    label="nerve.stl",
)
if artery_orig is not None:
    ax2.scatter(
        artery_orig.vertices[:, 0] * 1e3,
        artery_orig.vertices[:, 2] * 1e3,
        s=1,
        c="tab:gray",
        alpha=0.3,
        label="artery (unscaled)",
    )
ax2.scatter(
    artery_stl.vertices[:, 0] * 1e3,
    artery_stl.vertices[:, 2] * 1e3,
    s=2,
    c="tab:red",
    alpha=0.7,
    label="artery.stl (scaled)",
)
# Faixa do nervo on-mestrado (vertical em xz: r=1.5 mm, z∈[0,30])
ax2.fill_betweenx([0, 30], -1.5, 1.5, color="tab:cyan", alpha=0.25,
                   label="on-mestrado nerve (cilindro analítico)")
ax2.axhline(0, ls=":", c="k", lw=0.5)
ax2.axhline(30, ls=":", c="k", lw=0.5)
ax2.set_xlabel("x (mm)")
ax2.set_ylabel("z (mm)")
ax2.set_title("Projeção lateral xz")
ax2.legend(loc="upper right", fontsize=8)
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(OUT, dpi=140)
print(f"\n[write] {OUT.relative_to(REPO)}")
