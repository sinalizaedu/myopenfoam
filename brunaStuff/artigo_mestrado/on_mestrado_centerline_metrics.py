#!/usr/bin/env python3
"""
Métricas de tortuosidade do nervo óptico (zona ON) a partir do campo D.

Compatível com a literatura:
  - Desvio máximo ortogonal à corda (Lee et al., npj Microgravity 2020)
  - ONT = comprimento da curva / distância em linha reta (Chiang et al., IOVS 2025)

Centerline: centróides das células da cellZone 'on', agrupados por faixa em z;
posição deformada = centroide + D_célula.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np

SEGMENT_LENGTH_M = 0.020  # 20 mm intraorbitários (literatura)
Z_MAX_M = 0.030


def _vectors_from_text(text: str, n_expect: int | None = None) -> np.ndarray:
    vecs = []
    for m in re.finditer(r"\(\s*([-\d.eE+\s]+)\s*\)", text):
        parts = m.group(1).split()
        if len(parts) == 3:
            vecs.append([float(x) for x in parts])
    arr = np.array(vecs, dtype=float)
    if n_expect is not None and len(arr) != n_expect:
        raise RuntimeError(f"esperado {n_expect} vetores, obtido {len(arr)}")
    return arr


def read_openfoam_points(path: Path) -> np.ndarray:
    text = path.read_text()
    m = re.search(r"(\d+)\s*\(\s*", text)
    n = int(m.group(1))
    return _vectors_from_text(text[m.end() - 1 :], n)


def read_openfoam_faces(path: Path) -> list[list[int]]:
    out: list[list[int]] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith("4("):
            inner = line[2:-1]
            out.append([int(x) for x in inner.split()])
    return out


def read_openfoam_label_list(path: Path) -> np.ndarray:
    text = path.read_text()
    m = re.search(r"(\d+)\s*\(\s*", text)
    if not m:
        raise RuntimeError(f"labelList não encontrada em {path}")
    n = int(m.group(1))
    start = m.end()
    end = text.find(")", start)
    labels = [int(x) for x in text[start:end].split()]
    if len(labels) != n:
        raise RuntimeError(f"{path}: esperava {n} rótulos, obteve {len(labels)}")
    return np.array(labels, dtype=int)


def read_cell_zone_labels(cell_zones_path: Path, zone_name: str) -> np.ndarray:
    text = cell_zones_path.read_text()
    m = re.search(rf"\n{re.escape(zone_name)}\s*\n\{{\s*type\s+cellZone;\s*cellLabels\s+List<label>\s*\n(\d+)\s*\(", text)
    if not m:
        raise RuntimeError(f"cellZone {zone_name!r} não encontrada")
    n = int(m.group(1))
    start = m.end()
    end = text.find(")", start)
    labels = [int(x) for x in text[start:end].split()]
    if len(labels) != n:
        raise RuntimeError(f"cellZone {zone_name}: esperado {n}, obteve {len(labels)}")
    return np.array(labels, dtype=int)


def read_vol_vector_field(d_path: Path) -> np.ndarray:
    text = d_path.read_text()
    m = re.search(r"internalField\s+nonuniform\s+List<vector>\s*\n(\d+)\s*\(", text)
    if not m:
        raise RuntimeError(f"internalField List<vector> não encontrado em {d_path}")
    n = int(m.group(1))
    start = m.end()
    end = text.find(");", start)
    return _vectors_from_text(text[start:end], n)


def compute_cell_centres(points: np.ndarray, faces: list[list[int]], owner: np.ndarray) -> np.ndarray:
    n_cells = int(owner.max()) + 1
    accum = np.zeros((n_cells, 3))
    counts = np.zeros(n_cells, dtype=int)
    for fi, own in enumerate(owner):
        for pi in faces[fi]:
            accum[own] += points[pi]
            counts[own] += 1
    counts = np.maximum(counts, 1)
    return accum / counts[:, None]


def build_on_centerline(
    cell_centres: np.ndarray,
    d_cells: np.ndarray,
    on_labels: np.ndarray,
    n_bins: int = 60,
) -> tuple[np.ndarray, np.ndarray]:
    """Retorna (z_centros, posições_deformadas 3D) ao longo do eixo z."""
    pos0 = cell_centres[on_labels]
    pos = pos0 + d_cells[on_labels]
    z = pos[:, 2]
    zmin, zmax = float(z.min()), float(z.max())
    edges = np.linspace(zmin, zmax, n_bins + 1)
    z_mid = []
    pts = []
    for i in range(n_bins):
        mask = (z >= edges[i]) & (z < edges[i + 1]) if i < n_bins - 1 else (z >= edges[i]) & (z <= edges[i + 1])
        if not np.any(mask):
            continue
        z_mid.append(0.5 * (edges[i] + edges[i + 1]))
        pts.append(pos[mask].mean(axis=0))
    return np.array(z_mid), np.array(pts)


def _chord_metrics(curve: np.ndarray, z_use: np.ndarray, z0: float, z1: float) -> dict[str, float]:
    """Métricas no trecho [z0, z1] (coordenada z da malha)."""
    mask = (z_use >= z0) & (z_use <= z1)
    pts = curve[mask]
    if len(pts) < 2:
        return {
            "deviation_max_m": float("nan"),
            "ont_index": float("nan"),
            "arc_length_m": float("nan"),
            "chord_length_m": float("nan"),
            "n_points": float(len(pts)),
        }
    chord = pts[-1] - pts[0]
    chord_len = float(np.linalg.norm(chord))
    seg_lens = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    arc_len = float(np.sum(seg_lens))
    if chord_len < 1e-12:
        dev_max = 0.0
        ont = 1.0
    else:
        t_hat = chord / chord_len
        rel = pts - pts[0]
        along = rel @ t_hat
        perp = rel - np.outer(along, t_hat)
        dists = np.linalg.norm(perp, axis=1)
        dev_max = float(np.max(dists))
        ont = arc_len / chord_len
    return {
        "deviation_max_m": dev_max,
        "ont_index": ont,
        "arc_length_m": arc_len,
        "chord_length_m": chord_len,
        "n_points": float(len(pts)),
    }


def centerline_metrics_from_case(
    solid_dir: Path,
    time_name: str = "latest",
    segment_length_m: float = SEGMENT_LENGTH_M,
) -> dict[str, float]:
    """
    Calcula métricas clínicas da centerline da zona ON.

    time_name: pasta de tempo ('0.05', '0', 'latest')
    """
    mesh = solid_dir / "constant" / "polyMesh"
    if time_name == "latest":
        best_t, best_p = -1.0, None
        for p in solid_dir.iterdir():
            if not p.is_dir() or p.name == "0":
                continue
            try:
                t = float(p.name)
            except ValueError:
                continue
            if (p / "D").is_file() and t > best_t:
                best_t, best_p = t, p
        if best_p is None:
            raise FileNotFoundError(f"Nenhuma pasta de tempo com D em {solid_dir}")
        d_path = best_p / "D"
    else:
        d_path = solid_dir / time_name / "D"
    if not d_path.is_file():
        raise FileNotFoundError(d_path)

    points = read_openfoam_points(mesh / "points")
    faces = read_openfoam_faces(mesh / "faces")
    owner = read_openfoam_label_list(mesh / "owner")
    on_labels = read_cell_zone_labels(mesh / "cellZones", "on")
    d_cells = read_vol_vector_field(d_path)
    centres = compute_cell_centres(points, faces, owner)

    z_mid, curve_def = build_on_centerline(centres, d_cells, on_labels)
    z_mid0, curve_ref = build_on_centerline(centres, np.zeros_like(d_cells), on_labels)

    z0 = float(z_mid.min())
    z1_seg = min(z0 + segment_length_m, float(z_mid.max()))

    m_def = _chord_metrics(curve_def, z_mid, z0, z1_seg)
    m_ref = _chord_metrics(curve_ref, z_mid0, z0, z1_seg)

    return {
        "time": d_path.parent.name,
        "z_segment_start_m": z0,
        "z_segment_end_m": z1_seg,
        "deviation_max_m": m_def["deviation_max_m"],
        "deviation_max_mm": m_def["deviation_max_m"] * 1e3,
        "ont_index": m_def["ont_index"],
        "arc_length_m": m_def["arc_length_m"],
        "chord_length_m": m_def["chord_length_m"],
        "deviation_max_ref_mm": m_ref["deviation_max_m"] * 1e3,
        "ont_index_ref": m_ref["ont_index"],
        "n_centerline_points": m_def["n_points"],
    }


def main() -> int:
    import argparse
    import json

    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--case",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "cases" / "on-mestrado" / "solid",
    )
    ap.add_argument("--time", default="latest")
    ap.add_argument("--segment-mm", type=float, default=20.0)
    args = ap.parse_args()

    m = centerline_metrics_from_case(args.case, args.time, segment_length_m=args.segment_mm * 1e-3)
    print(json.dumps(m, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
