#!/usr/bin/env python3
"""inspect_teste_geom.py

Gera um PNG comparativo (3 views: 3D oblique, xz lateral, xy top) de um caso
gerado por build_teste_geom.py, mostrando:
  - centerline extraida (preto, lida do polyMesh ou re-extraida)
  - annulus do solido (vermelho semi-transparente, lido do polyMesh)
  - artery.stl original ja escalada (cinza wireframe) -- a geometria fonte
  - nerve.stl (azul claro)

Uso:
  python3 brunaStuff/inspect_teste_geom.py --case cases/teste-geom-1
  python3 brunaStuff/inspect_teste_geom.py --case cases/teste-geom-1 --out brunaStuff/inspect_teste_geom_1.png

Saida default: brunaStuff/inspect_<nome_caso>.png
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

REPO = Path(__file__).resolve().parents[1]


def read_polymesh_points(pm_dir: Path) -> np.ndarray:
    """Le points do polyMesh OpenFOAM ASCII. Retorna array (N, 3) em metros."""
    text = (pm_dir / "points").read_text()
    # Localiza o bloco "N\n(\n... )" apos o cabecalho
    m = re.search(r"\n\s*(\d+)\s*\n\s*\(\s*\n", text)
    if not m:
        raise RuntimeError(f"Nao consegui parsear cabecalho de {pm_dir / 'points'}")
    n_pts = int(m.group(1))
    body_start = m.end()
    # Le n_pts linhas no formato "(x y z)"
    lines_iter = text[body_start:].splitlines()
    pts = np.zeros((n_pts, 3))
    j = 0
    for line in lines_iter:
        line = line.strip()
        if not line or line == "(" or line.startswith(")"):
            continue
        if line.startswith("//"):
            continue
        # remove paren
        s = line.strip("()")
        parts = s.split()
        if len(parts) < 3:
            continue
        pts[j] = [float(parts[0]), float(parts[1]), float(parts[2])]
        j += 1
        if j == n_pts:
            break
    if j != n_pts:
        raise RuntimeError(
            f"Esperava {n_pts} pontos em {pm_dir / 'points'}, li {j}"
        )
    return pts


def read_ascii_stl_vertices(path: Path) -> np.ndarray:
    """STL ASCII -> array (N, 3) de vertices (com repeticao)."""
    pts: list[tuple[float, float, float]] = []
    with path.open() as f:
        for line in f:
            ls = line.strip()
            if ls.startswith("vertex"):
                a, b, c = ls.split()[1:4]
                pts.append((float(a), float(b), float(c)))
    return np.array(pts)


def read_stl_triangles(path: Path) -> np.ndarray:
    """STL ASCII -> array (M, 3, 3) de triangulos."""
    tris: list[list[tuple[float, float, float]]] = []
    current: list[tuple[float, float, float]] = []
    with path.open() as f:
        for line in f:
            ls = line.strip()
            if ls.startswith("vertex"):
                a, b, c = ls.split()[1:4]
                current.append((float(a), float(b), float(c)))
                if len(current) == 3:
                    tris.append(current)
                    current = []
    return np.array(tris)


def estimate_centerline_from_polymesh(pts_solid: np.ndarray, nz_guess: int = 160,
                                       ncirc_guess: int = 32, nrad_p1: int = 4) -> np.ndarray:
    """A polyMesh do annulus tem pontos ordenados como
        iz * (ncirc * (nrad+1)) + k * ncirc + t
    O builder usa nz=160, ncirc=32, nrad=3 -> 128 pts/secao.
    Centerline = media dos pontos por secao iz.
    """
    n_per_sec = ncirc_guess * nrad_p1
    n_total = len(pts_solid)
    # Tenta inferir nz a partir de n_total
    if n_total % n_per_sec != 0:
        # Tenta com nrad_p1=5 (nrad_lumen=4 -> 5*32=160)
        for trial_p1 in (5, 4, 3):
            if n_total % (ncirc_guess * trial_p1) == 0:
                n_per_sec = ncirc_guess * trial_p1
                nrad_p1 = trial_p1
                break
        else:
            raise RuntimeError(
                f"Nao consigo inferir layout do polyMesh: n_total={n_total}, "
                f"ncirc={ncirc_guess}"
            )
    nz = n_total // n_per_sec
    cl = np.zeros((nz, 3))
    for iz in range(nz):
        cl[iz] = pts_solid[iz * n_per_sec:(iz + 1) * n_per_sec].mean(axis=0)
    return cl


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--case", required=True, type=Path,
        help="diretorio do caso (ex: cases/teste-geom-1)",
    )
    ap.add_argument(
        "--out", type=Path, default=None,
        help="caminho do PNG de saida (default: brunaStuff/inspect_<case>.png)",
    )
    args = ap.parse_args()

    case_dir = args.case
    if not case_dir.is_absolute():
        case_dir = REPO / case_dir
    case_dir = case_dir.resolve()

    case_name = case_dir.name
    out_png = args.out
    if out_png is None:
        out_png = REPO / "brunaStuff" / f"inspect_{case_name}.png"
    elif not out_png.is_absolute():
        out_png = REPO / out_png

    pm_solid = case_dir / "solid" / "constant" / "polyMesh"
    if not (pm_solid / "points").exists():
        raise FileNotFoundError(f"Faltam pontos em {pm_solid}")

    print(f"[load] {pm_solid / 'points'}")
    pts_solid = read_polymesh_points(pm_solid)
    print(f"  {len(pts_solid)} pontos")

    cl = estimate_centerline_from_polymesh(pts_solid)
    print(f"  centerline inferida: {len(cl)} secoes")
    arc = float(np.sum(np.linalg.norm(np.diff(cl, axis=0), axis=1)))
    print(f"  arc length: {arc*1e3:.2f} mm")

    # STLs de referencia (copiadas pelo builder)
    tri_dir = case_dir / "constant" / "triSurface"
    artery_stl = tri_dir / "artery.stl"
    artery_unscaled_stl = tri_dir / "artery_unscaled.stl"
    nerve_stl = tri_dir / "nerve.stl"

    artery_pts = (
        read_ascii_stl_vertices(artery_stl) if artery_stl.exists() else None
    )
    nerve_tris = read_stl_triangles(nerve_stl) if nerve_stl.exists() else None

    fig = plt.figure(figsize=(18, 6))

    # --- View 1: 3D oblique ---
    ax1 = fig.add_subplot(1, 3, 1, projection="3d")
    if artery_pts is not None:
        ax1.scatter(
            artery_pts[::10, 0] * 1e3, artery_pts[::10, 1] * 1e3,
            artery_pts[::10, 2] * 1e3,
            s=0.5, c="lightgray", alpha=0.3, label="artery.stl (orig)",
        )
    if nerve_tris is not None:
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        coll = Poly3DCollection(
            nerve_tris * 1e3, facecolor="tab:cyan",
            edgecolor="none", alpha=0.20,
        )
        ax1.add_collection3d(coll)
    # Annulus pts (downsampled)
    ax1.scatter(
        pts_solid[::4, 0] * 1e3, pts_solid[::4, 1] * 1e3, pts_solid[::4, 2] * 1e3,
        s=0.4, c="tab:red", alpha=0.40, label="annulus (extruded)",
    )
    ax1.plot(cl[:, 0] * 1e3, cl[:, 1] * 1e3, cl[:, 2] * 1e3,
             c="black", lw=2.0, label="centerline")
    ax1.set_xlabel("x (mm)")
    ax1.set_ylabel("y (mm)")
    ax1.set_zlabel("z (mm)")
    ax1.set_title(f"{case_name} -- 3D oblique\narc length = {arc*1e3:.1f} mm")
    ax1.view_init(elev=20, azim=-65)
    ax1.legend(loc="upper left", fontsize=7)

    # --- View 2: xz lateral projection ---
    ax2 = fig.add_subplot(1, 3, 2)
    ax2.set_aspect("equal")
    if artery_pts is not None:
        ax2.scatter(
            artery_pts[:, 0] * 1e3, artery_pts[:, 2] * 1e3,
            s=1, c="lightgray", alpha=0.3, label="artery.stl",
        )
    if nerve_tris is not None:
        nerve_pts = nerve_tris.reshape(-1, 3)
        ax2.scatter(
            nerve_pts[:, 0] * 1e3, nerve_pts[:, 2] * 1e3,
            s=1, c="tab:cyan", alpha=0.4, label="nerve.stl",
        )
    ax2.scatter(
        pts_solid[:, 0] * 1e3, pts_solid[:, 2] * 1e3,
        s=1, c="tab:red", alpha=0.30, label="annulus",
    )
    ax2.plot(cl[:, 0] * 1e3, cl[:, 2] * 1e3,
             c="black", lw=2.0, label="centerline")
    ax2.set_xlabel("x (mm)")
    ax2.set_ylabel("z (mm)")
    ax2.set_title("xz lateral")
    ax2.grid(alpha=0.3)
    ax2.legend(loc="best", fontsize=7)

    # --- View 3: xy top ---
    ax3 = fig.add_subplot(1, 3, 3)
    ax3.set_aspect("equal")
    if artery_pts is not None:
        ax3.scatter(
            artery_pts[:, 0] * 1e3, artery_pts[:, 1] * 1e3,
            s=1, c="lightgray", alpha=0.3, label="artery.stl",
        )
    if nerve_tris is not None:
        nerve_pts = nerve_tris.reshape(-1, 3)
        ax3.scatter(
            nerve_pts[:, 0] * 1e3, nerve_pts[:, 1] * 1e3,
            s=1, c="tab:cyan", alpha=0.4, label="nerve.stl",
        )
    ax3.scatter(
        pts_solid[:, 0] * 1e3, pts_solid[:, 1] * 1e3,
        s=1, c="tab:red", alpha=0.30, label="annulus",
    )
    ax3.plot(cl[:, 0] * 1e3, cl[:, 1] * 1e3,
             c="black", lw=2.0, label="centerline")
    ax3.set_xlabel("x (mm)")
    ax3.set_ylabel("y (mm)")
    ax3.set_title("xy top")
    ax3.grid(alpha=0.3)
    ax3.legend(loc="best", fontsize=7)

    plt.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=130, bbox_inches="tight")
    print(f"[write] {out_png.relative_to(REPO)}")


if __name__ == "__main__":
    main()
