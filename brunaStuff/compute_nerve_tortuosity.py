#!/usr/bin/env python3
"""
Calcula a tortuosidade do nervo optico ao longo do ciclo cardiaco no caso
`cases/sugestao/`.

Definicao:
    tortuosidade(t) = arc_length(t) / chord_length(t) - 1
        (= 0 quando o nervo eh perfeitamente reto;
         valores tipicos in vivo: 0.005 - 0.02 em saudaveis,
         0.05 - 0.15 em SANS/HDTBR)

Etapas:
  1. Le pontos da malha do nervo (zona "on", cellZone) — extraidos previamente
     via OpenFOAM/Python (write_cellCentres ou direto polyMesh/points + 
     cellZones).
  2. Identifica pontos da centerline do nervo (proximos do eixo z, |x|<TOL e
     |y|<TOL).
  3. Para cada timestep:
       - le solid/<t>/D (campo de deslocamento)
       - aplica D nos pontos da centerline -> centerline deformada
       - calcula arc_length (somatorio das normas dos segmentos)
       - calcula chord_length = ||P_end - P_start||
       - tortuosidade(t) = arc/chord - 1
  4. Salva CSV e PNG.

Uso:
    python3 compute_nerve_tortuosity.py [--case CASE_DIR] [--zone on]
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

import numpy as np


def find_case_default() -> Path:
    candidates = [
        Path(__file__).resolve().parents[1] / "cases" / "sugestao",
        Path("/simulation/sugestao"),
    ]
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError("cases/sugestao nao encontrado")


def read_polymesh_points(polymesh_dir: Path) -> np.ndarray:
    """Le constant/polyMesh/points (formato ASCII)."""
    pts_file = polymesh_dir / "points"
    pts = []
    with pts_file.open() as f:
        in_list = False
        for line in f:
            ls = line.strip()
            if not in_list:
                if ls.startswith("(") and not pts:
                    in_list = True
                continue
            if ls.startswith(")"):
                break
            m = re.match(r"\(([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\)", ls)
            if m:
                pts.append([float(m.group(1)), float(m.group(2)), float(m.group(3))])
    return np.array(pts)


def read_cellzones(polymesh_dir: Path) -> dict[str, np.ndarray]:
    """Le constant/polyMesh/cellZones e retorna {zone_name: cell_indices}."""
    fpath = polymesh_dir / "cellZones"
    if not fpath.exists():
        return {}
    zones: dict[str, np.ndarray] = {}
    txt = fpath.read_text()
    # Encontra blocos <zone_name>{...cellLabels  List<label> N (... )}
    pattern = re.compile(
        r"(\w+)\s*\{\s*type\s+cellZone;\s*"
        r"cellLabels\s+List<label>\s*(\d+)\s*\(([\s\d]+?)\)",
        re.DOTALL,
    )
    for m in pattern.finditer(txt):
        name = m.group(1)
        idx = np.array([int(x) for x in m.group(3).split()])
        zones[name] = idx
    return zones


def cell_centres_from_polymesh(polymesh_dir: Path) -> np.ndarray:
    """Calcula centroides das celulas a partir de points/faces/owner/neighbour
    (suficiente para hex regulares; usa media dos 8 vertices da celula).

    Implementacao simples: para cada cell, identifica seus 8 pontos via faces
    e tira a media. Para hex estruturado isso eh exato.
    """
    pts = read_polymesh_points(polymesh_dir)
    # parse faces
    faces_file = polymesh_dir / "faces"
    faces: list[list[int]] = []
    with faces_file.open() as f:
        in_list = False
        for line in f:
            ls = line.strip()
            if not in_list:
                if ls.startswith("("):
                    in_list = True
                continue
            if ls.startswith(")"):
                break
            m = re.match(r"\d+\(([\d ]+)\)", ls)
            if m:
                faces.append([int(x) for x in m.group(1).split()])
    # parse owner
    owner = []
    with (polymesh_dir / "owner").open() as f:
        in_list = False
        for line in f:
            ls = line.strip()
            if not in_list:
                if ls.startswith("("):
                    in_list = True
                continue
            if ls.startswith(")"):
                break
            if ls and ls.lstrip("-").isdigit():
                owner.append(int(ls))
    # parse neighbour
    neigh = []
    with (polymesh_dir / "neighbour").open() as f:
        in_list = False
        for line in f:
            ls = line.strip()
            if not in_list:
                if ls.startswith("("):
                    in_list = True
                continue
            if ls.startswith(")"):
                break
            if ls and ls.lstrip("-").isdigit():
                neigh.append(int(ls))

    n_cells = max(max(owner), max(neigh) if neigh else 0) + 1
    cell_pts: list[set[int]] = [set() for _ in range(n_cells)]
    for fi, face in enumerate(faces):
        c_o = owner[fi]
        cell_pts[c_o].update(face)
        if fi < len(neigh):
            c_n = neigh[fi]
            cell_pts[c_n].update(face)

    centres = np.zeros((n_cells, 3))
    for ci, p_set in enumerate(cell_pts):
        if p_set:
            centres[ci] = pts[list(p_set)].mean(axis=0)
    return centres


def parse_volvector_field(fpath: Path, n_cells: int) -> np.ndarray:
    """Le um volVectorField OpenFOAM em ASCII e retorna (n_cells, 3)."""
    arr = np.zeros((n_cells, 3))
    with fpath.open() as f:
        in_internal = False
        in_list = False
        idx = 0
        for line in f:
            ls = line.strip()
            if not in_internal:
                if ls.startswith("internalField"):
                    in_internal = True
                    if "uniform" in ls:
                        # uniform single value
                        m = re.search(r"uniform\s*\(([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\)", ls)
                        if m:
                            v = np.array([float(m.group(1)), float(m.group(2)), float(m.group(3))])
                            arr[:] = v
                        return arr
                continue
            if not in_list:
                if ls.startswith("("):
                    in_list = True
                continue
            if ls.startswith(")"):
                break
            m = re.match(r"\(([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\)", ls)
            if m:
                arr[idx] = [float(m.group(1)), float(m.group(2)), float(m.group(3))]
                idx += 1
    return arr


def list_time_dirs(solid_dir: Path) -> list[float]:
    times: list[float] = []
    for d in solid_dir.iterdir():
        if not d.is_dir():
            continue
        try:
            t = float(d.name)
        except ValueError:
            continue
        times.append(t)
    return sorted(times)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", default=None,
                    help="Path do caso (default: cases/sugestao)")
    ap.add_argument("--zone", default="on",
                    help="Nome da cellZone do nervo (default: on)")
    ap.add_argument("--centerline-tol", type=float, default=0.1e-3,
                    help="Tol radial (m) para considerar uma cell como "
                         "centerline. Default: 0.1 mm")
    ap.add_argument("--out-csv", default=None)
    ap.add_argument("--out-png", default=None)
    args = ap.parse_args()

    case = Path(args.case) if args.case else find_case_default()
    solid_dir = case / "solid"
    polymesh_dir = solid_dir / "constant" / "polyMesh"

    print(f"[tortuosity] caso: {case}")
    print(f"[tortuosity] zona: {args.zone}")

    print("[tortuosity] calculando centroides das cells...")
    centres = cell_centres_from_polymesh(polymesh_dir)
    print(f"[tortuosity]   {len(centres)} cells")

    print("[tortuosity] lendo cellZones...")
    zones = read_cellzones(polymesh_dir)
    if args.zone not in zones:
        print(f"ERROR: zona '{args.zone}' nao encontrada. "
              f"Disponiveis: {list(zones)}")
        sys.exit(1)
    on_idx = zones[args.zone]
    print(f"[tortuosity]   zona '{args.zone}': {len(on_idx)} cells")

    # Centerline = cells na zona on com |x| e |y| < tol
    on_centres = centres[on_idx]
    radial = np.sqrt(on_centres[:, 0] ** 2 + on_centres[:, 1] ** 2)
    cl_mask = radial < args.centerline_tol
    cl_idx_in_zone = on_idx[cl_mask]
    print(f"[tortuosity]   centerline (|r|<{args.centerline_tol*1e3:.2f} mm): "
          f"{len(cl_idx_in_zone)} cells")

    if len(cl_idx_in_zone) < 4:
        print("ERROR: centerline com poucos pontos. Aumente --centerline-tol.")
        sys.exit(1)

    # Ordena por z
    cl_centres = centres[cl_idx_in_zone]
    z_order = np.argsort(cl_centres[:, 2])
    cl_idx_sorted = cl_idx_in_zone[z_order]
    cl_centres_sorted = cl_centres[z_order]

    # Loop nos timesteps
    times = list_time_dirs(solid_dir)
    print(f"[tortuosity] {len(times)} timesteps encontrados")
    if not times:
        print("ERROR: nenhum timestep. Rode o solver primeiro.")
        sys.exit(1)

    rows: list[tuple[float, float, float, float]] = []
    n_cells = len(centres)
    for t in times:
        d_file = solid_dir / f"{t:g}" / "D"
        if not d_file.exists():
            d_file = solid_dir / str(t) / "D"
        if not d_file.exists():
            continue
        try:
            D = parse_volvector_field(d_file, n_cells)
        except Exception as e:
            print(f"[tortuosity]   skip t={t}: {e}")
            continue
        deformed = cl_centres_sorted + D[cl_idx_sorted]
        seg = np.diff(deformed, axis=0)
        arc = float(np.sum(np.linalg.norm(seg, axis=1)))
        chord = float(np.linalg.norm(deformed[-1] - deformed[0]))
        tort = arc / chord - 1.0 if chord > 0 else 0.0
        rows.append((t, arc, chord, tort))
        print(f"[tortuosity]   t={t:.4f} s   arc={arc*1e3:.3f} mm   "
              f"chord={chord*1e3:.3f} mm   tort={tort:.5f}")

    out_csv = Path(args.out_csv) if args.out_csv else (
        Path(__file__).resolve().parent / "sugestao_nerve_tortuosity.csv"
    )
    with out_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t_s", "arc_m", "chord_m", "tortuosity"])
        for r in rows:
            w.writerow(r)
    print(f"[tortuosity] CSV salvo: {out_csv}")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        ts = np.array([r[0] for r in rows])
        torts = np.array([r[3] for r in rows])
        out_png = Path(args.out_png) if args.out_png else (
            Path(__file__).resolve().parent / "sugestao_nerve_tortuosity.png"
        )
        plt.figure(figsize=(8, 4))
        plt.plot(ts, torts * 100, lw=1.5)
        plt.xlabel("Tempo (s)")
        plt.ylabel("Tortuosidade (%)  =  (arc/chord - 1) x 100")
        plt.title("Tortuosidade do nervo optico — caso sugestao")
        plt.grid(True, alpha=0.4)
        plt.axhline(0, color="k", lw=0.4)
        plt.tight_layout()
        plt.savefig(out_png, dpi=120)
        print(f"[tortuosity] PNG salvo: {out_png}")
    except Exception as e:
        print(f"[tortuosity] (skip plot: {e})")


if __name__ == "__main__":
    main()
