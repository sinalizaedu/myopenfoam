#!/usr/bin/env python3
"""
Export G2-fluid Gmsh (.msh) boundary surfaces to STL + snappyHexMesh inputs.

Reads G2-fluid meshes from gen_lamminsalo_g2.py (symmetry_0, symmetry_90, wall)
and writes:

  fluid/constant/triSurface/g2_{symmetry_0,symmetry_90,wall}.stl
  fluid/constant/meshHints.json
  fluid/system/blockMeshDict.{M1,M2,M3}
  fluid/system/snappyHexMeshDict.{M1,M2,M3}
  fluid/system/surfaceFeatureExtractDict
  fluid/system/meshQualityDict
  geometry/paraview/M{level}/  — STLs + background box for ParaView preview

Usage:
  .venv-geom/bin/python brunaStuff/g2_msh_to_snappy.py --case doc-g4-sim4 --mesh-level M1
  .venv-geom/bin/python brunaStuff/g2_msh_to_snappy.py --case doc-g4-sim4 --mesh-level M1 --paraview
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "brunaStuff"))

from g2_structured_mesh import read_msh  # noqa: E402

SURFACE_PATCHES = ("symmetry_0", "symmetry_90", "wall")
GMSH_TRI = 2
GMSH_TET = 4
GMSH_WEDGE = 6

WEDGE_FACES = (
    (0, 1, 2),
    (3, 4, 5),
    (0, 1, 4, 3),
    (1, 2, 5, 4),
    (2, 0, 3, 5),
)

SNAPPY_LEVELS = {
    "M1": {"bg_cell_m": 5.0e-4, "surf_level": (1, 2), "feat_level": 2},
    "M2": {"bg_cell_m": 3.5e-4, "surf_level": (2, 3), "feat_level": 3},
    "M3": {"bg_cell_m": 2.5e-4, "surf_level": (2, 3), "feat_level": 3},
}


def _facet_normal(p0: np.ndarray, p1: np.ndarray, p2: np.ndarray) -> np.ndarray:
    n = np.cross(p1 - p0, p2 - p0)
    ln = np.linalg.norm(n)
    if ln < 1e-30:
        return np.array([0.0, 0.0, 1.0])
    return n / ln


def write_ascii_stl(
    path: Path,
    tris: list[tuple[np.ndarray, np.ndarray, np.ndarray]],
    solid: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"solid {solid}"]
    for p0, p1, p2 in tris:
        n = _facet_normal(p0, p1, p2)
        lines.append(f"  facet normal {n[0]:.16e} {n[1]:.16e} {n[2]:.16e}")
        lines.append("    outer loop")
        for p in (p0, p1, p2):
            lines.append(f"      vertex {p[0]:.16e} {p[1]:.16e} {p[2]:.16e}")
        lines.append("    endloop")
        lines.append("  endfacet")
    lines.append(f"endsolid {solid}")
    path.write_text("\n".join(lines) + "\n")


def write_multi_solid_stl(
    path: Path,
    tris_by_patch: dict[str, list],
    patch_order: tuple[str, ...] = SURFACE_PATCHES,
) -> None:
    """One ASCII STL with multiple solids — watertight wedge for snappyHexMesh."""
    path.parent.mkdir(parents=True, exist_ok=True)
    chunks: list[str] = []
    for patch in patch_order:
        tris = tris_by_patch.get(patch, [])
        if not tris:
            continue
        chunks.append(f"solid {patch}")
        for p0, p1, p2 in tris:
            n = _facet_normal(p0, p1, p2)
            chunks.append(f"  facet normal {n[0]:.16e} {n[1]:.16e} {n[2]:.16e}")
            chunks.append("    outer loop")
            for p in (p0, p1, p2):
                chunks.append(f"      vertex {p[0]:.16e} {p[1]:.16e} {p[2]:.16e}")
            chunks.append("    endloop")
            chunks.append("  endfacet")
        chunks.append(f"endsolid {patch}")
    path.write_text("\n".join(chunks) + "\n")


def _face_key(nodes: list[int]) -> tuple[int, ...]:
    return tuple(sorted(nodes))


def _quad_to_tris(
    pts: list[np.ndarray],
) -> tuple[tuple[np.ndarray, np.ndarray, np.ndarray], tuple[np.ndarray, np.ndarray, np.ndarray]]:
    return (pts[0], pts[1], pts[2]), (pts[0], pts[2], pts[3])


def extract_surface_tris_from_tris(
    msh_path: Path,
) -> tuple[dict[str, list], list[np.ndarray]]:
    data = read_msh(msh_path)
    tris_by_patch: dict[str, list] = {p: [] for p in SURFACE_PATCHES}
    fluid_centroids: list[np.ndarray] = []
    phy_to_name = {tag: name for tag, (_dim, name) in data.physical.items()}

    for etype, phy, nodes in data.elements:
        name = phy_to_name.get(phy, "")
        if etype == GMSH_TRI and name in tris_by_patch:
            pts = [np.array(data.nodes[n], dtype=float) for n in nodes[:3]]
            tris_by_patch[name].append(tuple(pts))
        elif etype == GMSH_TET and name == "fluid":
            pts = [np.array(data.nodes[n], dtype=float) for n in nodes[:4]]
            fluid_centroids.append(np.mean(pts, axis=0))
        elif etype == GMSH_WEDGE and name == "fluid":
            pts = [np.array(data.nodes[n], dtype=float) for n in nodes[:6]]
            fluid_centroids.append(np.mean(pts, axis=0))

    return tris_by_patch, fluid_centroids


def extract_surface_tris_from_wedges(msh_path: Path, tol: float = 1e-6) -> tuple[dict[str, list], list[np.ndarray]]:
    """Fallback when .msh has prism volume only (doc-g2-sim2 style)."""
    data = read_msh(msh_path)
    phy_to_name = {tag: name for tag, (_dim, name) in data.physical.items()}
    face_count: dict[tuple[int, ...], int] = defaultdict(int)
    face_node_ids: dict[tuple[int, ...], list[int]] = {}
    fluid_centroids: list[np.ndarray] = []

    for etype, phy, nodes in data.elements:
        name = phy_to_name.get(phy, "")
        if etype != GMSH_WEDGE or name != "fluid":
            continue
        pts = [np.array(data.nodes[n], dtype=float) for n in nodes[:6]]
        fluid_centroids.append(np.mean(pts, axis=0))
        for f in WEDGE_FACES:
            ns = [nodes[i] for i in f]
            key = _face_key(ns)
            face_count[key] += 1
            face_node_ids[key] = ns

    tris_by_patch: dict[str, list] = {p: [] for p in SURFACE_PATCHES}

    def classify(ns: list[int]) -> str:
        pts = np.array([data.nodes[n] for n in ns], dtype=float)
        if np.all(np.abs(pts[:, 2]) < tol):
            return "symmetry_0"
        if np.all(np.abs(pts[:, 0]) < tol):
            return "symmetry_90"
        return "wall"

    for key, count in face_count.items():
        if count != 1:
            continue
        ns = face_node_ids[key]
        patch = classify(ns)
        pts = [np.array(data.nodes[n], dtype=float) for n in ns]
        if len(pts) == 3:
            tris_by_patch[patch].append((pts[0], pts[1], pts[2]))
        else:
            tris_by_patch[patch].append(_quad_to_tris(pts)[0])
            tris_by_patch[patch].append(_quad_to_tris(pts)[1])

    return tris_by_patch, fluid_centroids


def extract_surface_tris(msh_path: Path) -> tuple[dict[str, list], list[np.ndarray], str]:
    tris_by_patch, fluid_centroids = extract_surface_tris_from_tris(msh_path)
    if all(tris_by_patch[p] for p in SURFACE_PATCHES):
        return tris_by_patch, fluid_centroids, "gmsh-surface-tris"
    if any(tris_by_patch[p] for p in SURFACE_PATCHES):
        counts = {p: len(tris_by_patch[p]) for p in SURFACE_PATCHES}
        print(
            f"[warn] incomplete surface tris in {msh_path.name} ({counts}); "
            "extracting prism boundaries"
        )
    else:
        print(f"[warn] no 2D surface tris in {msh_path.name}; extracting prism boundaries")
    tris_by_patch, fluid_centroids = extract_surface_tris_from_wedges(msh_path)
    return tris_by_patch, fluid_centroids, "prism-boundary-fallback"


def combined_arrays(tris_by_patch: dict[str, list]) -> tuple[np.ndarray, np.ndarray]:
    verts: list[np.ndarray] = []
    faces: list[tuple[int, int, int]] = []
    for tris in tris_by_patch.values():
        for p0, p1, p2 in tris:
            base = len(verts)
            verts.extend([p0, p1, p2])
            faces.append((base, base + 1, base + 2))
    return np.asarray(verts, dtype=float), np.asarray(faces, dtype=int)


def ray_cast_hits(
    origin: np.ndarray,
    direction: np.ndarray,
    v0: np.ndarray,
    e1: np.ndarray,
    e2: np.ndarray,
) -> int:
    h = np.cross(direction, e2)
    a = (e1 * h).sum(axis=1)
    valid = np.abs(a) > 1e-20
    f = np.zeros_like(a)
    f[valid] = 1.0 / a[valid]
    s = origin - v0
    u = f * (s * h).sum(axis=1)
    mask_u = (u >= 0) & (u <= 1) & valid
    q = np.cross(s, e1)
    v = f * (direction * q).sum(axis=1)
    mask_v = (v >= 0) & (u + v <= 1) & mask_u
    t = f * (e2 * q).sum(axis=1)
    return int(np.count_nonzero((t > 1e-9) & mask_v))


def is_inside(point: np.ndarray, V: np.ndarray, F: np.ndarray) -> bool:
    v0 = V[F[:, 0]]
    v1 = V[F[:, 1]]
    v2 = V[F[:, 2]]
    e1 = v1 - v0
    e2 = v2 - v0
    dirs = [
        np.array([1.0, 0.337, 0.781]),
        np.array([0.612, 1.0, 0.234]),
        np.array([0.823, 0.516, 1.0]),
    ]
    votes = 0
    for d in dirs:
        d = d / np.linalg.norm(d)
        if ray_cast_hits(point, d, v0, e1, e2) % 2 == 1:
            votes += 1
    return votes >= 2


def pick_location_in_mesh(fluid_centroids: list[np.ndarray], V: np.ndarray, F: np.ndarray) -> np.ndarray:
    if not fluid_centroids:
        raise RuntimeError("No fluid elements in msh — cannot pick locationInMesh")
    c_all = np.array(fluid_centroids)
    center = 0.5 * (c_all.min(axis=0) + c_all.max(axis=0))
    dists = np.linalg.norm(c_all - center, axis=1)
    order = np.argsort(-dists)
    for idx in order[: min(200, len(order))]:
        pt = c_all[idx]
        if is_inside(pt, V, F):
            return pt
    for scale in (0.25, 0.1, 0.0):
        pt = center + scale * (c_all[order[0]] - center)
        if is_inside(pt, V, F):
            return pt
    raise RuntimeError("Could not find locationInMesh inside G2-fluid wedge")


def bbox_from_tris(tris_by_patch: dict[str, list], pad_m: float) -> tuple[np.ndarray, np.ndarray]:
    pts = np.vstack([p for tris in tris_by_patch.values() for tri in tris for p in tri])
    lo = pts.min(axis=0) - pad_m
    hi = pts.max(axis=0) + pad_m
    return lo, hi


def box_tris(lo: np.ndarray, hi: np.ndarray) -> list[tuple[np.ndarray, np.ndarray, np.ndarray]]:
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    v = [
        np.array([x0, y0, z0]),
        np.array([x1, y0, z0]),
        np.array([x1, y1, z0]),
        np.array([x0, y1, z0]),
        np.array([x0, y0, z1]),
        np.array([x1, y0, z1]),
        np.array([x1, y1, z1]),
        np.array([x0, y1, z1]),
    ]
    quads = [
        (0, 4, 7, 3),
        (1, 2, 6, 5),
        (0, 1, 5, 4),
        (3, 7, 6, 2),
        (0, 3, 2, 1),
        (4, 5, 6, 7),
    ]
    tris: list[tuple[np.ndarray, np.ndarray, np.ndarray]] = []
    for a, b, c, d in quads:
        tris.append(_quad_to_tris([v[a], v[b], v[c], v[d]])[0])
        tris.append(_quad_to_tris([v[a], v[b], v[c], v[d]])[1])
    return tris


def marker_tris(center: np.ndarray, radius: float = 2.0e-4) -> list[tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """Small octahedron marker for locationInMesh in ParaView."""
    cx, cy, cz = center
    r = radius
    pts = [
        np.array([cx + r, cy, cz]),
        np.array([cx - r, cy, cz]),
        np.array([cx, cy + r, cz]),
        np.array([cx, cy - r, cz]),
        np.array([cx, cy, cz + r]),
        np.array([cx, cy, cz - r]),
    ]
    faces = [
        (0, 2, 4),
        (2, 1, 4),
        (1, 3, 4),
        (3, 0, 4),
        (2, 0, 5),
        (1, 2, 5),
        (3, 1, 5),
        (0, 3, 5),
    ]
    return [(pts[a], pts[b], pts[c]) for a, b, c in faces]


def _foam_header(obj: str) -> str:
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      {obj};
}}
"""


def write_block_mesh_dict(path: Path, lo: np.ndarray, hi: np.ndarray, bg_cell_m: float) -> tuple[int, int, int]:
    ext = hi - lo
    nx = max(8, int(math.ceil(ext[0] / bg_cell_m)))
    ny = max(8, int(math.ceil(ext[1] / bg_cell_m)))
    nz = max(8, int(math.ceil(ext[2] / bg_cell_m)))
    v = [
        (lo[0], lo[1], lo[2]),
        (hi[0], lo[1], lo[2]),
        (hi[0], hi[1], lo[2]),
        (lo[0], hi[1], lo[2]),
        (lo[0], lo[1], hi[2]),
        (hi[0], lo[1], hi[2]),
        (hi[0], hi[1], hi[2]),
        (lo[0], hi[1], hi[2]),
    ]
    vert_lines = "\n".join(f"    ({x:.6e} {y:.6e} {z:.6e})" for x, y, z in v)
    text = _foam_header("blockMeshDict") + f"""
// G2-fluid background box for snappyHexMesh (STL bbox + pad).
scale   1;

vertices
(
{vert_lines}
);

blocks
(
    hex (0 1 2 3 4 5 6 7)  ({nx} {ny} {nz})  simpleGrading (1 1 1)
);

edges ();

boundary
(
    bg_xmin {{ type patch; faces ( (0 4 7 3) ); }}
    bg_xmax {{ type patch; faces ( (1 2 6 5) ); }}
    bg_ymin {{ type patch; faces ( (0 1 5 4) ); }}
    bg_ymax {{ type patch; faces ( (3 7 6 2) ); }}
    bg_zmin {{ type patch; faces ( (0 3 2 1) ); }}
    bg_zmax {{ type patch; faces ( (4 5 6 7) ); }}
);
"""
    path.write_text(text)
    return nx, ny, nz


def write_snappy_dict(path: Path, mesh_level: str, loc: np.ndarray, levels: dict) -> None:
    sl_min, sl_max = levels["surf_level"]
    feat = levels["feat_level"]
    loc_s = f"({loc[0]:.16e} {loc[1]:.16e} {loc[2]:.16e})"
    text = _foam_header("snappyHexMeshDict") + f"""
// G2-fluid 90° calotte — closed multi-solid STL ({mesh_level}).

castellatedMesh true;
snap            false;
addLayers       false;

geometry
{{
    g2_fluid.stl
    {{
        type triSurfaceMesh;
        name g2_fluid;
    }}
}}

castellatedMeshControls
{{
    maxLocalCells       2000000;
    maxGlobalCells      8000000;
    minRefinementCells  10;
    nCellsBetweenLevels 2;

    features
    (
        {{ file "g2_fluid.eMesh"; level {feat}; }}
    );

    refinementSurfaces
    {{
        g2_fluid
        {{
            level ({sl_min} {sl_max});
            regions
            {{
                symmetry_0
                {{
                    level   ({sl_min} {sl_max});
                    patchInfo {{ type symmetry; }}
                }}
                symmetry_90
                {{
                    level   ({sl_min} {sl_max});
                    patchInfo {{ type symmetry; }}
                }}
                wall
                {{
                    level   ({sl_min} {sl_max + 1});
                    patchInfo {{ type wall; }}
                }}
            }}
        }}
    }}

    resolveFeatureAngle     45;
    refinementRegions {{ }}

    locationInMesh          {loc_s};

    allowFreeStandingZoneFaces false;
}}

snapControls
{{
    nSmoothPatch        3;
    tolerance           1.0;
    nSolveIter          100;
    nRelaxIter          5;
    nFeatureSnapIter    10;
    implicitFeatureSnap false;
    explicitFeatureSnap true;
    multiRegionFeatureSnap false;
}}

addLayersControls
{{
    relativeSizes       true;
    layers              {{ }}
    expansionRatio      1.0;
    finalLayerThickness 0.3;
    minThickness        0.1;
    nGrow               0;
    featureAngle        60;
    nRelaxIter          3;
    nSmoothSurfaceNormals 1;
    nSmoothNormals      3;
    nSmoothThickness    10;
    maxFaceThicknessRatio 0.5;
    maxThicknessToMedialRatio 0.3;
    minMedialAxisAngle  90;
    nBufferCellsNoExtrude 0;
    nLayerIter          50;
}}

meshQualityControls
{{
    #include "meshQualityDict"
    relaxed
    {{
        maxNonOrtho 80;
        maxBoundarySkewness 25;
        maxInternalSkewness 6;
        minVol              1e-15;
        minTetQuality      -1e-30;
    }}
    nSmoothScale        6;
    errorReduction      0.5;
}}

writeFlags ( );
mergeTolerance 1e-5;
"""
    path.write_text(text)


def write_surface_feature_extract(path: Path) -> None:
    text = _foam_header("surfaceFeatureExtractDict") + """
g2_fluid.stl
{
    extractionMethod    extractFromSurface;
    extractFromSurfaceCoeffs
    {
        includedAngle   150;
    }
    writeObj            no;
}
"""
    path.write_text(text)


def write_mesh_quality(path: Path) -> None:
    text = _foam_header("meshQualityDict") + """
// Quality criteria for snappyHexMesh.

#includeEtc "caseDicts/meshQualityDict"

maxNonOrtho         65;
maxBoundarySkewness 20;
maxInternalSkewness 4;
maxConcave          80;
minVol              1e-13;
minTetQuality       1e-15;
minArea             -1;
minTwist            0.02;
minDeterminant      0.001;
minFaceWeight       0.05;
minVolRatio         0.01;
minTriangleTwist    -1;
nSmoothScale        4;
errorReduction      0.75;
"""
    path.write_text(text)


def _msh_has_surface_tris(path: Path) -> bool:
    data = read_msh(path)
    phy_to_name = {tag: name for tag, (_dim, name) in data.physical.items()}
    return any(
        etype == GMSH_TRI and phy_to_name.get(phy, "") in SURFACE_PATCHES
        for etype, phy, _nodes in data.elements
    )


def resolve_msh(case_dir: Path, mesh_level: str, msh_path: Path | None) -> Path:
    if msh_path is not None:
        if not msh_path.is_file():
            raise SystemExit(f"Missing msh: {msh_path}")
        return msh_path

    case_name = case_dir.name
    candidates = [
        case_dir / "geometry" / f"eye_g2_fluid_lamminsalo_{mesh_level}.msh",
    ]
    if case_name.startswith("doc-g5"):
        candidates.append(
            REPO / "cases" / "doc-g3-sim1" / "geometry" / f"eye_g2_fluid_lamminsalo_{mesh_level}.msh"
        )
    else:
        candidates.extend(
            [
                REPO / "cases" / "doc-g2-sim1" / "geometry" / f"eye_g2_fluid_lamminsalo_{mesh_level}.msh",
                REPO / "cases" / "doc-g2-sim2" / "geometry" / f"eye_g2_fluid_lamminsalo_{mesh_level}.msh",
            ]
        )
    tagged: Path | None = None
    fallback: Path | None = None
    for path in candidates:
        if not path.is_file():
            continue
        fallback = fallback or path
        if _msh_has_surface_tris(path):
            tagged = path
            break
    chosen = tagged or fallback
    if chosen is None:
        raise SystemExit(
            "Missing Gmsh mesh. Provide --msh or generate:\n"
            f"  .venv-geom/bin/python brunaStuff/gen_lamminsalo_g2.py "
            f"--case doc-g2-sim1 --mesh --mesh-level {mesh_level}"
        )
    return chosen


def export_paraview_geometry(
    case_dir: Path,
    mesh_level: str,
    tris_by_patch: dict[str, list],
    lo: np.ndarray,
    hi: np.ndarray,
    loc: np.ndarray,
    hints: dict,
) -> Path:
    out = case_dir / "geometry" / "paraview" / mesh_level
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    tri_dir = case_dir / "fluid" / "constant" / "triSurface"
    for patch in SURFACE_PATCHES:
        src = tri_dir / f"g2_{patch}.stl"
        shutil.copy2(src, out / src.name)

    combined: list[tuple[np.ndarray, np.ndarray, np.ndarray]] = []
    for patch in SURFACE_PATCHES:
        combined.extend(tris_by_patch[patch])
    write_ascii_stl(out / "g2_fluid_combined.stl", combined, "g2_fluid_combined")
    write_ascii_stl(out / "snappy_background_box.stl", box_tris(lo, hi), "snappy_background_box")
    write_ascii_stl(out / "location_in_mesh.stl", marker_tris(loc), "location_in_mesh")

    manifest = {
        "mesh_level": mesh_level,
        "paraview_hint": (
            "File → Open → select all .stl in this folder. "
            "Color patches separately; set snappy_background_box opacity ≈ 0.15."
        ),
        "files": {
            "g2_symmetry_0.stl": "symmetry plane z=0",
            "g2_symmetry_90.stl": "symmetry plane x=0",
            "g2_wall.stl": "wall (AC + vitreous + TM outer)",
            "g2_fluid_combined.stl": "all boundary patches merged",
            "snappy_background_box.stl": "blockMesh background box (1 mm pad)",
            "location_in_mesh.stl": "snappyHexMesh locationInMesh marker",
        },
        **hints,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"[ok] {out.relative_to(REPO)}  (ParaView preview)")
    return out


def read_multi_solid_stl(path: Path) -> dict[str, list]:
    """Parse ASCII STL (single- or multi-solid) into patch → triangle list."""
    tris_by_patch: dict[str, list] = {p: [] for p in SURFACE_PATCHES}
    fallback: list[tuple[np.ndarray, np.ndarray, np.ndarray]] = []
    solid = "wall"
    buf: list[np.ndarray] = []

    for raw in path.read_text().splitlines():
        line = raw.strip()
        if line.startswith("solid "):
            solid = line.split(maxsplit=1)[1]
            buf.clear()
            continue
        if line.startswith("endsolid"):
            buf.clear()
            continue
        if line.startswith("vertex"):
            parts = line.split()
            buf.append(np.array([float(parts[1]), float(parts[2]), float(parts[3])]))
            if len(buf) == 3:
                tri = (buf[0], buf[1], buf[2])
                if solid in tris_by_patch:
                    tris_by_patch[solid].append(tri)
                else:
                    fallback.append(tri)
                buf.clear()

    if not any(tris_by_patch[p] for p in SURFACE_PATCHES):
        for p in SURFACE_PATCHES:
            tris_by_patch[p] = []
        tris_by_patch["wall"] = fallback
    return tris_by_patch


def pick_location_for_wedge(tris_by_patch: dict[str, list], V: np.ndarray, F: np.ndarray) -> np.ndarray:
    """Interior point for G2 90° fluid wedge — prefer posterior vitreous (y < 0)."""
    pts = np.vstack([p for tris in tris_by_patch.values() for tri in tris for p in tri])
    lo, hi = pts.min(axis=0), pts.max(axis=0)
    candidates: list[np.ndarray] = []
    for x in np.linspace(max(0.0, lo[0]), hi[0] * 0.6, 10):
        for y in np.linspace(hi[1] * 0.2, lo[1] * 0.95, 14):
            for z in np.linspace(lo[2] * 0.95, min(0.0, hi[2]), 10):
                pt = np.array([x, y, z])
                if is_inside(pt, V, F):
                    candidates.append(pt)
    if candidates:
        return min(candidates, key=lambda p: p[1])
    return pick_location_in_bbox(lo, hi, V, F)


def pick_location_in_bbox(lo: np.ndarray, hi: np.ndarray, V: np.ndarray, F: np.ndarray) -> np.ndarray:
    center = 0.5 * (lo + hi)
    if is_inside(center, V, F):
        return center
    n = 12
    for x in np.linspace(lo[0], hi[0], n):
        for y in np.linspace(lo[1], hi[1], n):
            for z in np.linspace(lo[2], hi[2], n):
                pt = np.array([x, y, z])
                if is_inside(pt, V, F):
                    return pt
    raise RuntimeError("Could not find locationInMesh inside closed G2-fluid STL")


def write_snappy_dicts(
    case_dir: Path,
    mesh_level: str,
    tris_by_patch: dict[str, list],
    loc: np.ndarray,
    pad_mm: float,
    *,
    source: str,
    surface_mode: str,
) -> dict:
    pad_m = pad_mm * 1e-3
    lo, hi = bbox_from_tris(tris_by_patch, pad_m)
    levels = SNAPPY_LEVELS[mesh_level]
    sys_dir = case_dir / "fluid" / "system"
    sys_dir.mkdir(parents=True, exist_ok=True)

    nx, ny, nz = write_block_mesh_dict(
        sys_dir / f"blockMeshDict.{mesh_level}", lo, hi, levels["bg_cell_m"]
    )
    write_snappy_dict(sys_dir / f"snappyHexMeshDict.{mesh_level}", mesh_level, loc, levels)
    write_surface_feature_extract(sys_dir / "surfaceFeatureExtractDict")
    write_mesh_quality(sys_dir / "meshQualityDict")

    hints = {
        "geometry_source": source,
        "mesh_level": mesh_level,
        "mesh_tool": "blockMesh + snappyHexMesh",
        "surface_extraction": surface_mode,
        "fluid_locationInMesh": loc.tolist(),
        "bounds_surface_m": [lo.tolist(), hi.tolist()],
        "pad_mm": pad_mm,
        "bg_cell_m": levels["bg_cell_m"],
        "blockMesh_cells": [nx, ny, nz],
        "surface_counts": {p: len(tris_by_patch[p]) for p in SURFACE_PATCHES},
        "locationInMesh_validation": "raycast on closed g2_fluid.stl",
    }
    hints_path = case_dir / "fluid" / "constant" / "meshHints.json"
    hints_path.write_text(json.dumps(hints, indent=2) + "\n")
    print(f"[ok] {hints_path.relative_to(REPO)}")
    print(f"[ok] locationInMesh = ({loc[0]*1e3:.4f}, {loc[1]*1e3:.4f}, {loc[2]*1e3:.4f}) mm")
    return hints


def prepare_from_stl(
    case: str,
    mesh_level: str,
    pad_mm: float = 1.0,
    *,
    paraview: bool = False,
) -> dict:
    """Regenerate snappy dicts from committed STL geometry (no Gmsh)."""
    case_dir = REPO / "cases" / case
    if mesh_level not in SNAPPY_LEVELS:
        raise SystemExit(f"mesh_level must be one of {sorted(SNAPPY_LEVELS)}")

    tri_dir = case_dir / "fluid" / "constant" / "triSurface"
    closed_stl = tri_dir / "g2_fluid.stl"
    if not closed_stl.is_file():
        raise SystemExit(f"Missing {closed_stl} — case uses STL + snappy only")

    tris_by_patch = read_multi_solid_stl(closed_stl)
    for patch in SURFACE_PATCHES:
        if tris_by_patch[patch]:
            continue
        per_patch = tri_dir / f"g2_{patch}.stl"
        if per_patch.is_file():
            extra = read_multi_solid_stl(per_patch)
            tris_by_patch[patch] = extra.get(patch) or extra.get("wall") or []

    if not any(tris_by_patch[p] for p in SURFACE_PATCHES):
        raise RuntimeError(f"No triangles read from {closed_stl}")

    V, F = combined_arrays(tris_by_patch)
    pad_m = pad_mm * 1e-3
    lo, hi = bbox_from_tris(tris_by_patch, pad_m)
    loc = pick_location_for_wedge(tris_by_patch, V, F)

    hints = write_snappy_dicts(
        case_dir,
        mesh_level,
        tris_by_patch,
        loc,
        pad_mm,
        source=str(closed_stl.relative_to(case_dir)),
        surface_mode="triSurface/g2_fluid.stl",
    )
    if paraview:
        export_paraview_geometry(case_dir, mesh_level, tris_by_patch, lo, hi, loc, hints)
    return hints


def prepare_snappy(
    case: str,
    mesh_level: str,
    msh_path: Path | None,
    pad_mm: float,
    *,
    paraview: bool = False,
) -> dict:
    case_dir = REPO / "cases" / case
    if not case_dir.is_dir():
        raise SystemExit(f"Case not found: {case_dir}")

    msh_path = resolve_msh(case_dir, mesh_level, msh_path)
    if mesh_level not in SNAPPY_LEVELS:
        raise SystemExit(f"mesh_level must be one of {sorted(SNAPPY_LEVELS)}")

    tris_by_patch, fluid_centroids, surface_mode = extract_surface_tris(msh_path)
    for patch in SURFACE_PATCHES:
        if not tris_by_patch[patch]:
            raise RuntimeError(f"No surface triangles for patch {patch!r} in {msh_path}")

    tri_dir = case_dir / "fluid" / "constant" / "triSurface"
    for patch in SURFACE_PATCHES:
        stl = tri_dir / f"g2_{patch}.stl"
        write_ascii_stl(stl, tris_by_patch[patch], f"g2_{patch}")
        print(f"[ok] {stl.relative_to(REPO)}  ({len(tris_by_patch[patch])} tris)")

    closed_stl = tri_dir / "g2_fluid.stl"
    write_multi_solid_stl(closed_stl, tris_by_patch)
    n_closed = sum(len(tris_by_patch[p]) for p in SURFACE_PATCHES)
    print(f"[ok] {closed_stl.relative_to(REPO)}  ({n_closed} tris, closed wedge)")

    V, F = combined_arrays(tris_by_patch)
    loc = pick_location_in_mesh(fluid_centroids, V, F)
    lo, hi = bbox_from_tris(tris_by_patch, pad_mm * 1e-3)

    try:
        rel_msh = str(msh_path.relative_to(REPO))
    except ValueError:
        rel_msh = str(msh_path)

    hints = write_snappy_dicts(
        case_dir,
        mesh_level,
        tris_by_patch,
        loc,
        pad_mm,
        source=rel_msh,
        surface_mode=surface_mode,
    )

    if paraview:
        export_paraview_geometry(case_dir, mesh_level, tris_by_patch, lo, hi, loc, hints)

    return hints


def main() -> None:
    ap = argparse.ArgumentParser(description="G2-fluid STL + snappyHexMesh dict preparation")
    ap.add_argument("--case", default="doc-g4-sim4")
    ap.add_argument("--mesh-level", default="M1", choices=sorted(SNAPPY_LEVELS))
    ap.add_argument("--msh", type=Path, default=None, help="Optional: rebuild STLs from Gmsh .msh")
    ap.add_argument("--from-stl", action="store_true", help="Use committed g2_fluid.stl only (default for g4)")
    ap.add_argument("--pad-mm", type=float, default=1.0, help="Background box padding [mm]")
    ap.add_argument("--paraview", action="store_true")
    args = ap.parse_args()
    if args.from_stl or args.msh is None:
        prepare_from_stl(args.case, args.mesh_level, args.pad_mm, paraview=args.paraview)
    else:
        prepare_snappy(args.case, args.mesh_level, args.msh, args.pad_mm, paraview=args.paraview)


if __name__ == "__main__":
    main()
