#!/usr/bin/env python3
"""Plot the actual mesh faces used by the inlet and TM outlet patches."""

from pathlib import Path
import re
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.path import Path as MplPath
from scipy.spatial import cKDTree


CASE = Path(__file__).resolve().parents[1]
REPO = CASE.parents[1]
sys.path.insert(0, str(REPO / "brunaStuff"))

from gen_lamminsalo_2d import (  # noqa: E402
    build_bilateral_m,
    build_outlines_cm,
    fluid_outer_and_holes,
)


def _list_body(path: Path) -> tuple[int, str]:
    text = path.read_text()
    match = re.search(r"(\d+)\s*\n\s*\(", text)
    if not match:
        raise ValueError(f"Cannot parse OpenFOAM list in {path}")
    return int(match.group(1)), text[match.end() :]


def read_points(path: Path) -> np.ndarray:
    count, body = _list_body(path)
    points = [
        [float(value) for value in match.group(1).split()]
        for match in re.finditer(r"\(([^)]+)\)", body)
    ]
    return np.asarray(points[:count])


def read_faces(path: Path) -> list[list[int]]:
    count, body = _list_body(path)
    faces = [
        [int(value) for value in match.group(2).split()]
        for match in re.finditer(r"(\d+)\(([^)]*)\)", body)
    ]
    return faces[:count]


def read_boundary(path: Path) -> dict[str, tuple[int, int]]:
    patches = {}
    for match in re.finditer(r"(\w+)\s*\{([^}]+)\}", path.read_text()):
        face_count = re.search(r"nFaces\s+(\d+)", match.group(2))
        start = re.search(r"startFace\s+(\d+)", match.group(2))
        if face_count and start:
            patches[match.group(1)] = (int(start.group(1)), int(face_count.group(1)))
    return patches


def projected_face_segments(
    name: str,
    points: np.ndarray,
    faces: list[list[int]],
    patches: dict[str, tuple[int, int]],
) -> list[np.ndarray]:
    """Return each extruded boundary face as its distinct XY edge in millimetres."""
    start, count = patches[name]
    segments = []
    for face_id in range(start, start + count):
        xy = points[faces[face_id], :2]
        unique = np.unique(np.round(xy, decimals=12), axis=0)
        if len(unique) < 2:
            continue
        distances = np.linalg.norm(unique[:, None] - unique[None, :], axis=2)
        first, second = np.unravel_index(np.argmax(distances), distances.shape)
        segments.append(unique[[first, second]] * 1e3)
    return segments


def read_internal_vectors(path: Path) -> np.ndarray:
    text = path.read_text()
    match = re.search(
        r"internalField\s+nonuniform\s+List<vector>\s*\n"
        r"\d+\s*\n\((.*?)\)\s*;",
        text,
        re.S,
    )
    if not match:
        raise ValueError(f"Cannot parse vector field in {path}")
    return np.asarray(
        [
            [float(value) for value in vector.split()]
            for vector in re.findall(r"\(([^)]+)\)", match.group(1))
        ]
    )


def latest_solution_time() -> Path:
    candidates = []
    for directory in (CASE / "fluid").iterdir():
        try:
            time = float(directory.name)
        except ValueError:
            continue
        if (directory / "U").exists() and (directory / "C").exists():
            candidates.append((time, directory))
    if not candidates:
        raise FileNotFoundError("No solution time containing both U and C")
    # A rerun may converge at a lower numeric iteration than an older run.
    return max(candidates, key=lambda item: item[1].stat().st_mtime)[1]


def trace_streamlines(
    inlet_segments: list[np.ndarray],
    outlet_segments: list[np.ndarray],
    outer: np.ndarray,
    holes: list[np.ndarray],
) -> list[np.ndarray]:
    """Trace visible curves through the converged U direction field."""
    solution = latest_solution_time()
    centres = read_internal_vectors(solution / "C")[:, :2]
    velocity = read_internal_vectors(solution / "U")[:, :2]
    tree = cKDTree(centres)
    outer_path = MplPath(outer[:, :2])
    hole_paths = [MplPath(hole[:, :2]) for hole in holes]
    outlet_points = np.vstack(outlet_segments) * 1e-3

    def inside(point: np.ndarray) -> bool:
        return outer_path.contains_point(point) and not any(
            hole.contains_point(point) for hole in hole_paths
        )

    def direction(point: np.ndarray) -> np.ndarray:
        _, cell = tree.query(point)
        vector = velocity[cell]
        magnitude = np.linalg.norm(vector)
        return vector / magnitude if magnitude > 1e-12 else np.zeros(2)

    # Three seeds per selected face reveal flow across the full inlet patch.
    seeds = []
    for segment_mm in inlet_segments:
        segment = segment_mm * 1e-3
        for fraction in (0.2, 0.5, 0.8):
            seed = segment[0] + fraction * (segment[1] - segment[0])
            seed[0] -= np.sign(seed[0]) * 3e-5
            seeds.append(seed)

    step = 8e-6  # 8 µm geometric step; speed affects direction, not visibility.
    paths = []
    for seed in seeds:
        point = seed.copy()
        path = [point.copy()]
        for _ in range(3500):
            k1 = direction(point)
            if not np.any(k1):
                break
            k2 = direction(point + 0.5 * step * k1)
            k3 = direction(point + 0.5 * step * k2)
            k4 = direction(point + step * k3)
            following = point + step * (k1 + 2 * k2 + 2 * k3 + k4) / 6
            if not inside(following):
                break
            path.append(following.copy())
            point = following
            if np.min(np.linalg.norm(outlet_points - point, axis=1)) < 5e-5:
                break
        paths.append(np.asarray(path) * 1e3)
    return paths


def add_faces(
    axis,
    segments: list[np.ndarray],
    color: str,
    label: str | None = None,
    annotate: bool = False,
) -> None:
    axis.add_collection(
        LineCollection(
            segments,
            colors=color,
            linewidths=4.0,
            capstyle="butt",
            zorder=8,
            label=label,
        )
    )
    for number, segment in enumerate(segments, start=1):
        axis.scatter(
            segment[:, 0],
            segment[:, 1],
            s=3,
            color=color,
            edgecolor="white",
            linewidth=0.15,
            zorder=9,
        )
        if annotate:
            midpoint = segment.mean(axis=0)
            axis.annotate(
                f"F{number}",
                midpoint,
                xytext=(4, 2),
                textcoords="offset points",
                fontsize=7,
                color=color,
                weight="bold",
                zorder=10,
            )


def main() -> None:
    mesh = CASE / "fluid/constant/polyMesh"
    points = read_points(mesh / "points")
    faces = read_faces(mesh / "faces")
    patches = read_boundary(mesh / "boundary")

    inlet_right = projected_face_segments("ac_inlet", points, faces, patches)
    inlet_left = projected_face_segments("ac_inlet_left", points, faces, patches)
    outlet_right = projected_face_segments("outlet_tm", points, faces, patches)
    outlet_left = projected_face_segments("outlet_tm_left", points, faces, patches)

    outlines = build_outlines_cm()
    bilateral = build_bilateral_m(outlines)
    outer, holes = fluid_outer_and_holes(bilateral)
    streamlines = trace_streamlines(
        inlet_right + inlet_left,
        outlet_right + outlet_left,
        outer,
        holes,
    )

    figure, axis = plt.subplots(figsize=(9, 7.5))
    axis.fill(outer[:, 0] * 1e3, outer[:, 1] * 1e3, color="#e8f4fc", zorder=0)
    for hole in holes:
        axis.fill(hole[:, 0] * 1e3, hole[:, 1] * 1e3, color="white", zorder=1)
    for path in streamlines:
        axis.plot(
            path[:, 0],
            path[:, 1],
            color="#008cba",
            lw=0.85,
            alpha=0.9,
            zorder=3,
        )
        if len(path) > 20:
            arrow = min(len(path) - 1, len(path) // 2)
            axis.annotate(
                "",
                xy=path[arrow],
                xytext=path[arrow - 10],
                arrowprops={"arrowstyle": "-|>", "color": "#008cba", "lw": 0.8},
                zorder=4,
            )

    add_faces(
        axis,
        inlet_right,
        "#0057b8",
        f"ac_inlet: {len(inlet_right)} faces/lado",
    )
    add_faces(axis, inlet_left, "#0057b8")
    add_faces(
        axis,
        outlet_right,
        "#d62728",
        f"outlet_tm: {len(outlet_right)} faces/lado",
    )
    add_faces(axis, outlet_left, "#d62728")

    # Enlarged right-side view makes every selected mesh face explicit.
    inset = axis.inset_axes([0.58, 0.08, 0.39, 0.43])
    inset.fill(outer[:, 0] * 1e3, outer[:, 1] * 1e3, color="#e8f4fc", zorder=0)
    for hole in holes:
        inset.fill(hole[:, 0] * 1e3, hole[:, 1] * 1e3, color="white", zorder=1)
    add_faces(inset, inlet_right, "#0057b8", annotate=True)
    add_faces(inset, outlet_right, "#d62728", annotate=True)
    inset.set_xlim(6.55, 7.12)
    inset.set_ylim(-4.86, -3.22)
    inset.set_aspect("equal")
    inset.set_title("Faces reais da malha — lado direito", fontsize=9)
    inset.set_xlabel("x [mm]", fontsize=8)
    inset.set_ylabel("y [mm]", fontsize=8)
    inset.tick_params(labelsize=7)
    inset.grid(alpha=0.15)
    axis.indicate_inset_zoom(inset, edgecolor="#555555", alpha=0.7)

    axis.set_aspect("equal")
    axis.set_xlim(-8.2, 8.2)
    axis.set_ylim(-9.5, 1.5)
    axis.set_xlabel("x [mm]")
    axis.set_ylabel("y [mm]")
    axis.set_title("Faces de contorno determinadas na malha")
    axis.legend(loc="lower left", fontsize=9)
    axis.grid(alpha=0.12)
    figure.tight_layout()

    output = CASE / "figures/streamlines_inlet_outlet.png"
    figure.savefig(output, dpi=180)
    print(f"Wrote {output}")
    print(
        f"inlet={len(inlet_right)} faces/side; "
        f"outlet={len(outlet_right)} faces/side"
    )


if __name__ == "__main__":
    main()
