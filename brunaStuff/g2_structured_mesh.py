"""Structured G2 meridional quad mesh + 90° revolve (3D hexes, shared interface nodes)."""

from __future__ import annotations

import json
import math
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import numpy as np

REVOLVE_RAD = math.radians(90.0)
PLANE_TOL = 2.0e-4
NODE_WELD = 7

STRUCTURED_LEVELS = {
    "M5": {
        "n_theta": 4,
        "n_merid": 28,
        "n_r_fluid": 10,
        "layers": {"cornea": 2, "sclera": 3, "choroid": 2, "retina": 2},
        "fluid_tm_layers": 4,
    },
    "M4": {
        "n_theta": 5,
        "n_merid": 32,
        "n_r_fluid": 12,
        "layers": {"cornea": 3, "sclera": 3, "choroid": 3, "retina": 3},
        "fluid_tm_layers": 4,
    },
    "M1": {
        "n_theta": 6,
        "n_merid": 36,
        "n_r_fluid": 14,
        "layers": {"cornea": 3, "sclera": 4, "choroid": 3, "retina": 3},
        "fluid_tm_layers": 5,
    },
    "M2": {
        "n_theta": 8,
        "n_merid": 52,
        "n_r_fluid": 16,
        "layers": {"cornea": 4, "sclera": 5, "choroid": 4, "retina": 4},
        "fluid_tm_layers": 6,
    },
    "M3": {
        "n_theta": 10,
        "n_merid": 72,
        "n_r_fluid": 18,
        "layers": {"cornea": 5, "sclera": 6, "choroid": 5, "retina": 5},
        "fluid_tm_layers": 8,
    },
}

SOLID_PATCHES = (
    "symmetry_0",
    "symmetry_90",
    "outer",
    "fsi_active",
    "fsi_iris",
    "fsi_lens",
    "lens_rim",
)

HEX_FACES = (
    (0, 1, 2, 3),
    (4, 7, 6, 5),
    (0, 4, 5, 1),
    (1, 5, 6, 2),
    (2, 6, 7, 3),
    (3, 7, 4, 0),
)

INTERNAL_ZONES = {"ciliary", "lens", "iris"}


def _snap_axis(pts: np.ndarray) -> np.ndarray:
    out = np.asarray(pts, dtype=float).copy()
    if len(out) and abs(out[-1, 0]) < 5.0e-4:
        out[-1, 0] = 0.0
    return out


def _cum_arclength(pts: np.ndarray) -> np.ndarray:
    pts = np.asarray(pts, dtype=float)
    d = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    s = np.concatenate([[0.0], np.cumsum(d)])
    if s[-1] < 1e-15:
        return np.linspace(0.0, 1.0, len(pts))
    return s / s[-1]


def _interp_curve(pts: np.ndarray, s_query: np.ndarray) -> np.ndarray:
    pts = np.asarray(pts, dtype=float)
    s = _cum_arclength(pts)
    out = np.zeros((len(s_query), 2))
    for i, sq in enumerate(s_query):
        j = min(np.searchsorted(s, sq, side="right"), len(pts) - 1)
        j = max(j, 1)
        t = (sq - s[j - 1]) / max(s[j] - s[j - 1], 1e-15)
        out[i] = (1.0 - t) * pts[j - 1] + t * pts[j]
    return out


def resample_pair(outer: np.ndarray, inner: np.ndarray, n: int) -> tuple[np.ndarray, np.ndarray]:
    outer = _snap_axis(outer)
    inner = _snap_axis(inner)
    if np.linalg.norm(outer[0] - inner[0]) > np.linalg.norm(outer[0] - inner[-1]):
        inner = inner[::-1]
    s = np.linspace(0.0, 1.0, n)
    return _interp_curve(outer, s), _interp_curve(inner, s)


def resample_curve(pts: np.ndarray, n: int) -> np.ndarray:
    pts = np.asarray(pts, dtype=float)
    if np.linalg.norm(pts[0] - pts[-1]) < 1e-12:
        pts = pts[:-1]
    s = np.linspace(0.0, 1.0, n)
    return _interp_curve(pts, s)


def point_in_poly(p: np.ndarray, poly: np.ndarray) -> bool:
    x, y = float(p[0]), float(p[1])
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-30) + xi):
            inside = not inside
        j = i
    return inside


def _hex_volume_sign(nodes: dict[int, tuple[float, float, float]], conn: list[int]) -> float:
    """Signed volume of an 8-node hex (Gmsh brick order)."""

    def signed_tet(a, b, c, d):
        ba = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
        ca = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
        da = (d[0] - a[0], d[1] - a[1], d[2] - a[2])
        cross = (
            ba[1] * ca[2] - ba[2] * ca[1],
            ba[2] * ca[0] - ba[0] * ca[2],
            ba[0] * ca[1] - ba[1] * ca[0],
        )
        return (cross[0] * da[0] + cross[1] * da[1] + cross[2] * da[2]) / 6.0

    p = [nodes[i] for i in conn]
    return (
        signed_tet(p[0], p[1], p[3], p[4])
        + signed_tet(p[1], p[2], p[3], p[6])
        + signed_tet(p[1], p[4], p[5], p[6])
        + signed_tet(p[3], p[4], p[6], p[7])
        + signed_tet(p[1], p[3], p[4], p[6])
    )


def _flip_hex(conn: list[int]) -> list[int]:
    return [conn[0], conn[3], conn[2], conn[1], conn[4], conn[7], conn[6], conn[5]]


def classify_solid_patch(cx: float, cy: float, cz: float) -> str:
    r = math.hypot(cx, cz)
    if abs(cz) < PLANE_TOL and abs(cx) > 1e-8:
        return "symmetry_0"
    if abs(cx) < PLANE_TOL and abs(cz) > 1e-8:
        return "symmetry_90"
    if r >= 7.8e-3:
        return "outer"
    if 2.5e-3 <= r <= 7.2e-3 and -5.55e-3 <= cy <= -3.65e-3 and r >= 4.85e-3:
        return "fsi_iris"
    if 3.4e-3 <= r <= 4.85e-3 and -5.0e-3 <= cy <= -3.0e-3:
        return "lens_rim"
    if r <= 4.2e-3 and cy < -3.0e-3:
        return "fsi_lens"
    return "fsi_active"


def classify_fluid_patch(cx: float, cy: float, cz: float, *, hole: str | None = None) -> str:
    if hole == "lens":
        return "lens_wall"
    if hole == "iris":
        return "iris_wall"
    r = math.hypot(cx, cz)
    if abs(cz) < PLANE_TOL and abs(cx) > 1e-8:
        return "symmetry_0"
    if abs(cx) < PLANE_TOL and abs(cz) > 1e-8:
        return "symmetry_90"
    return "wall"


@dataclass
class MshData:
    nodes: dict[int, tuple[float, float, float]] = field(default_factory=dict)
    elements: list[tuple[int, int, list[int]]] = field(default_factory=list)
    physical: dict[int, tuple[int, str]] = field(default_factory=dict)


def read_msh(path: Path) -> MshData:
    data = MshData()
    section = None
    n_nodes = n_elems = n_phy = 0
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("//"):
            continue
        if line.startswith("$"):
            if line in ("$Nodes", "$Elements", "$PhysicalNames"):
                section = line[1:]
                n_nodes = n_elems = n_phy = 0
            else:
                section = None
            continue
        if section == "PhysicalNames":
            if n_phy == 0:
                n_phy = int(line)
                continue
            parts = line.split()
            dim, tag = int(parts[0]), int(parts[1])
            name = line.split('"')[1]
            data.physical[tag] = (dim, name)
            continue
        if section == "Nodes":
            if n_nodes == 0:
                n_nodes = int(line)
                continue
            parts = line.split()
            nid = int(parts[0])
            data.nodes[nid] = (float(parts[1]), float(parts[2]), float(parts[3]))
            continue
        if section == "Elements":
            if n_elems == 0:
                n_elems = int(line)
                continue
            parts = [int(x) for x in line.split()]
            etype, ntags = parts[1], parts[2]
            tags = parts[3 : 3 + ntags]
            nodes = parts[3 + ntags :]
            phy = tags[0] if tags else 0
            data.elements.append((etype, phy, nodes))
    return data


def write_msh(path: Path, data: MshData) -> None:
    lines = ["$MeshFormat", "2.2 0 8", "$EndMeshFormat", "$PhysicalNames", str(len(data.physical))]
    for tag in sorted(data.physical):
        dim, name = data.physical[tag]
        lines.append(f'{dim} {tag} "{name}"')
    lines.append("$EndPhysicalNames")
    lines.append("$Nodes")
    lines.append(str(len(data.nodes)))
    for nid in sorted(data.nodes):
        x, y, z = data.nodes[nid]
        lines.append(f"{nid} {x:.16e} {y:.16e} {z:.16e}")
    lines.append("$EndNodes")
    lines.append("$Elements")
    lines.append(str(len(data.elements)))
    eid = 1
    for etype, phy, nodes in data.elements:
        lines.append(f"{eid} {etype} 1 {phy} " + " ".join(str(n) for n in nodes))
        eid += 1
    lines.append("$EndElements")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def merge_msh_files(
    out_path: Path,
    parts: list[tuple[Path, set[str] | None, bool]],
    *,
    tol: float = 1e-7,
) -> dict:
    phy_name_to_tag: dict[tuple[int, str], int] = {}
    next_phy = 1
    merged = MshData()
    node_key_to_id: dict[tuple[int, int, int], int] = {}
    next_node = 1
    next_elem = 1
    zone_counts: dict[str, int] = {}
    patch_counts: dict[str, int] = {}

    def weld_node(x: float, y: float, z: float) -> int:
        nonlocal next_node
        key = (round(x / tol), round(y / tol), round(z / tol))
        if key not in node_key_to_id:
            node_key_to_id[key] = next_node
            merged.nodes[next_node] = (x, y, z)
            next_node += 1
        return node_key_to_id[key]

    def phy_tag(dim: int, name: str) -> int:
        nonlocal next_phy
        key = (dim, name)
        if key not in phy_name_to_tag:
            phy_name_to_tag[key] = next_phy
            merged.physical[next_phy] = key
            next_phy += 1
        return phy_name_to_tag[key]

    for msh_path, keep_zones, include_patches in parts:
        src = read_msh(msh_path)
        for etype, phy, nodes in src.elements:
            name = src.physical.get(phy, (0, ""))[1]
            if etype in (5, 6):
                if keep_zones is not None and name not in keep_zones:
                    continue
                new_phy = phy_tag(3, name)
                new_nodes = [weld_node(*src.nodes[n]) for n in nodes]
                merged.elements.append((etype, new_phy, new_nodes))
                zone_counts[name] = zone_counts.get(name, 0) + 1
            elif etype == 3 and include_patches:
                if name not in SOLID_PATCHES and name not in ("wall", "fsi_wall", "lens_wall", "iris_wall"):
                    continue
                new_phy = phy_tag(2, name)
                new_nodes = [weld_node(*src.nodes[n]) for n in nodes]
                merged.elements.append((etype, new_phy, new_nodes))
                patch_counts[name] = patch_counts.get(name, 0) + 1

    write_msh(out_path, merged)
    return {"zones": zone_counts, "patches": patch_counts, "n_nodes": len(merged.nodes)}


class HexVolumeMesher:
    """Build structured hex volumes by revolving a meridional quad grid."""

    def __init__(self):
        self.gmsh = __import__("gmsh")
        self.curves: dict[str, np.ndarray] = {}
        self.surface_tags: dict[str, list[int]] = {}
        self.volume_tags: dict[str, list[int]] = {}
        self.node_grids: dict[str, list[list[int]]] = {}
        self._revolve_node_cache: dict[tuple[int, int], int] = {}
        self._node_id = 1
        self._elem_id = 1
        self._surf_id = 1
        self._vol_id = 1

    def add_grid(
        self,
        name: str,
        grid: np.ndarray,
        *,
        shared_outer: str | None = None,
        bind_rows: dict[int, list[int]] | None = None,
    ) -> None:
        n_r, n_m, _ = grid.shape
        bind_rows = bind_rows or {}
        surf = self._surf_id
        self._surf_id += 1
        self.gmsh.model.addDiscreteEntity(2, surf)

        node_grid = [[0] * n_m for _ in range(n_r)]
        flat_tags: list[int] = []
        flat_coords: list[float] = []
        for j in range(n_r):
            bound = bind_rows.get(j)
            for i in range(n_m):
                if bound is not None and i < len(bound) and bound[i] > 0:
                    node_grid[j][i] = int(bound[i])
                    continue
                tag = self._node_id
                self._node_id += 1
                node_grid[j][i] = tag
                x, y = grid[j, i]
                x = max(x, 1.0e-6) if abs(x) < 1.0e-6 else float(x)
                flat_tags.append(tag)
                flat_coords.extend([x, y, 0.0])

        if flat_tags:
            self.gmsh.model.mesh.addNodes(2, surf, flat_tags, flat_coords)
        elem_tags: list[int] = []
        conn: list[int] = []
        for j in range(n_r - 1):
            for i in range(n_m - 1):
                eid = self._elem_id
                self._elem_id += 1
                elem_tags.append(eid)
                conn.extend(
                    [
                        node_grid[j][i],
                        node_grid[j][i + 1],
                        node_grid[j + 1][i + 1],
                        node_grid[j + 1][i],
                    ]
                )
        if elem_tags:
            self.gmsh.model.mesh.addElements(2, surf, [3], [elem_tags], [conn])
        self.surface_tags[name] = [surf]
        self.node_grids[name] = node_grid
        self.curves[name] = grid[-1]

    def add_shell(
        self,
        name: str,
        outer: np.ndarray,
        inner: np.ndarray,
        *,
        n_m: int,
        n_r: int,
        shared_outer: str | None = None,
    ) -> None:
        if shared_outer and shared_outer in self.curves:
            outer_rs = self.curves[shared_outer]
            # FSI-facing inner row follows its own anatomical arclength (not choroid s-param).
            inner_rs = resample_open(_snap_axis(inner), n_m)
        else:
            outer_rs, inner_rs = resample_pair(outer, inner, n_m)
        outer_rs = outer_rs.copy()
        inner_rs = inner_rs.copy()
        # Only cornea meets the calotte apex on the meridional plane; other shells keep anatomy endpoints.
        if name == "cornea":
            apex_y = 0.5 * (outer_rs[0, 1] + inner_rs[0, 1])
            outer_rs[0] = (1.0e-6, apex_y)
            inner_rs[0] = (2.5e-6, apex_y)
        grid = np.zeros((n_r + 1, n_m, 2))
        for j in range(n_r + 1):
            t = j / n_r
            grid[j] = (1.0 - t) * outer_rs + t * inner_rs
        self.add_grid(name, grid, shared_outer=shared_outer)

    def revolve(self, names: Iterable[str], *, n_theta: int) -> None:
        thetas = np.linspace(0.0, REVOLVE_RAD, n_theta + 1)
        for name in names:
            vols: list[int] = []
            for stag in self.surface_tags.get(name, []):
                vol_tag = self._vol_id
                self._vol_id += 1
                self.gmsh.model.addDiscreteEntity(3, vol_tag)
                vols.append(vol_tag)

                ntags, coord, _ = self.gmsh.model.mesh.getNodes(2, stag)
                etypes, _, enodes = self.gmsh.model.mesh.getElements(2, stag)
                quad_node_tags: set[int] = set(int(t) for t in ntags)
                if 3 in etypes:
                    qi = list(etypes).index(3)
                    for qn in enodes[qi]:
                        quad_node_tags.add(int(qn))
                idx_of: dict[int, int] = {}
                coord_list: list[float] = []
                for t in sorted(quad_node_tags):
                    xyz = self.gmsh.model.mesh.getNode(t)[0]
                    idx_of[t] = len(idx_of)
                    coord_list.extend([float(xyz[0]), float(xyz[1]), float(xyz[2])])
                ntags = list(idx_of.keys())
                coord = coord_list
                layer_maps: list[dict[int, int]] = []
                vol_nodes: list[int] = []
                vol_coords: list[float] = []
                node_dict: dict[int, tuple[float, float, float]] = {}

                for th_idx, th in enumerate(thetas):
                    c, s = math.cos(th), math.sin(th)
                    mapping: dict[int, int] = {}
                    for t in ntags:
                        i = idx_of[t]
                        x, y, z = coord[3 * i], coord[3 * i + 1], coord[3 * i + 2]
                        x3 = x * c + z * s
                        z3 = -x * s + z * c
                        cache_key = (int(t), th_idx)
                        if cache_key in self._revolve_node_cache:
                            nt3 = self._revolve_node_cache[cache_key]
                        else:
                            nt3 = self._node_id
                            self._node_id += 1
                            self._revolve_node_cache[cache_key] = nt3
                            vol_nodes.append(nt3)
                            vol_coords.extend([x3, y, z3])
                        node_dict[int(nt3)] = (x3, y, z3)
                        mapping[t] = nt3
                    layer_maps.append(mapping)

                if vol_nodes:
                    self.gmsh.model.mesh.addNodes(3, vol_tag, vol_nodes, vol_coords)
                hex_tags: list[int] = []
                hex_conn: list[int] = []
                if 3 in etypes:
                    qi = list(etypes).index(3)
                    quads = enodes[qi]
                    for q in range(0, len(quads), 4):
                        n0, n1, n2, n3 = (int(quads[q]), int(quads[q + 1]), int(quads[q + 2]), int(quads[q + 3]))
                        for k in range(n_theta):
                            hc = [
                                layer_maps[k][n0],
                                layer_maps[k][n1],
                                layer_maps[k][n2],
                                layer_maps[k][n3],
                                layer_maps[k + 1][n0],
                                layer_maps[k + 1][n1],
                                layer_maps[k + 1][n2],
                                layer_maps[k + 1][n3],
                            ]
                            if _hex_volume_sign(node_dict, hc) < 0:
                                hc = _flip_hex(hc)
                            hex_tags.append(self._elem_id)
                            self._elem_id += 1
                            hex_conn.extend(hc)
                if hex_tags:
                    self.gmsh.model.mesh.addElements(3, vol_tag, [5], [hex_tags], [hex_conn])
            self.volume_tags[name] = vols

    def _node_coords(self) -> dict[int, tuple[float, float, float]]:
        coords: dict[int, tuple[float, float, float]] = {}
        for vols in self.volume_tags.values():
            for v in vols:
                ntags, c, _ = self.gmsh.model.mesh.getNodes(3, v)
                for i, t in enumerate(ntags):
                    coords[int(t)] = (c[3 * i], c[3 * i + 1], c[3 * i + 2])
        return coords

    def _boundary_hex_faces(self, vol_tags: list[int]) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
        """Return (sorted_key, oriented_nodes) for each boundary hex face."""
        face_count: dict[tuple[int, ...], int] = {}
        face_orient: dict[tuple[int, ...], tuple[int, ...]] = {}
        for hn in self._collect_hexes(vol_tags):
            for loc in HEX_FACES:
                fn = tuple(hn[i] for i in loc)
                key = tuple(sorted(fn))
                face_count[key] = face_count.get(key, 0) + 1
                face_orient[key] = fn
        return [(k, face_orient[k]) for k, c in face_count.items() if c == 1]

    def extract_conformal_fsi_faces(
        self,
        *,
        solid_vols: list[int],
        fluid_vols: list[int],
        fsi_2d_tags: set[int],
        n_theta: int,
    ) -> tuple[list[tuple[int, ...]], list[tuple[int, ...]]]:
        """Faces whose four nodes lie on the shared FSI 2D node ring (both sides)."""
        fsi_3d: set[int] = set()
        for t in fsi_2d_tags:
            for k in range(n_theta + 1):
                key = (int(t), k)
                if key in self._revolve_node_cache:
                    fsi_3d.add(self._revolve_node_cache[key])

        def pick(vols: list[int]) -> list[tuple[int, ...]]:
            out: list[tuple[int, ...]] = []
            for _, fn in self._boundary_hex_faces(vols):
                if all(n in fsi_3d for n in fn):
                    out.append(fn)
            return out

        return pick(solid_vols), pick(fluid_vols)

    def verify_conformal_fsi(
        self,
        solid_faces: list[tuple[int, ...]],
        fluid_faces: list[tuple[int, ...]],
    ) -> float:
        """Max distance between matched face centroids (same 3D node rings)."""
        coords = self._node_coords()

        def centroids(faces: list[tuple[int, ...]]) -> dict[tuple[int, ...], tuple[float, float, float]]:
            out: dict[tuple[int, ...], tuple[float, float, float]] = {}
            for fn in faces:
                pts = [coords[n] for n in fn]
                out[tuple(sorted(fn))] = (
                    sum(p[0] for p in pts) / 4.0,
                    sum(p[1] for p in pts) / 4.0,
                    sum(p[2] for p in pts) / 4.0,
                )
            return out

        s_map = centroids(solid_faces)
        f_map = centroids(fluid_faces)
        common = set(s_map) & set(f_map)
        if len(common) != len(s_map) or len(common) != len(f_map):
            raise ValueError(
                f"conformal FSI face mismatch: solid={len(s_map)} fluid={len(f_map)} common={len(common)}"
            )
        max_dist = 0.0
        for key in common:
            sc = np.array(s_map[key])
            fc = np.array(f_map[key])
            max_dist = max(max_dist, float(np.linalg.norm(sc - fc)))
        print(f"INFO: conformal FSI centroid max distance = {max_dist:.3e} m ({len(common)} faces)")
        return max_dist

    def _write_quad_patch(self, quads: list[tuple[int, ...]], pname: str) -> list[int]:
        if not quads:
            return []
        stag = self._surf_id
        self._surf_id += 1
        self.gmsh.model.addDiscreteEntity(2, stag)
        elem_tags: list[int] = []
        conn: list[int] = []
        for fn in quads:
            elem_tags.append(self._elem_id)
            self._elem_id += 1
            conn.extend(fn)
        self.gmsh.model.mesh.addElements(2, stag, [3], [elem_tags], [conn])
        return [stag]
        coords: dict[int, tuple[float, float, float]] = {}
        for vols in self.volume_tags.values():
            for v in vols:
                ntags, c, _ = self.gmsh.model.mesh.getNodes(3, v)
                for i, t in enumerate(ntags):
                    coords[int(t)] = (c[3 * i], c[3 * i + 1], c[3 * i + 2])
        return coords

    def _collect_hexes(self, vol_tags: list[int]) -> list[list[int]]:
        hexes: list[list[int]] = []
        for v in vol_tags:
            etypes, _, enodes = self.gmsh.model.mesh.getElements(3, v)
            if 5 not in etypes:
                continue
            hi = list(etypes).index(5)
            nodes = enodes[hi]
            for h in range(0, len(nodes), 8):
                hexes.append([int(x) for x in nodes[h : h + 8]])
        return hexes

    def extract_boundary_patches(
        self,
        vol_tags: list[int],
        *,
        classifier,
        patch_names: tuple[str, ...],
        hole_classifier=None,
    ) -> dict[str, list[int]]:
        node_coords = self._node_coords()
        face_count: dict[tuple[int, ...], int] = {}
        face_nodes: dict[tuple[int, ...], tuple[int, ...]] = {}
        for hn in self._collect_hexes(vol_tags):
            for loc in HEX_FACES:
                fn = tuple(hn[i] for i in loc)
                key = tuple(sorted(fn))
                face_count[key] = face_count.get(key, 0) + 1
                face_nodes[key] = fn

        grouped: dict[str, list[tuple[int, ...]]] = {p: [] for p in patch_names}
        for key, cnt in face_count.items():
            if cnt != 1:
                continue
            fn = face_nodes[key]
            pts = [node_coords[n] for n in fn]
            cx = sum(p[0] for p in pts) / 4.0
            cy = sum(p[1] for p in pts) / 4.0
            cz = sum(p[2] for p in pts) / 4.0
            hole = hole_classifier(cx, cy, cz) if hole_classifier else None
            pname = classifier(cx, cy, cz, hole=hole) if hole_classifier else classifier(cx, cy, cz)
            if pname in grouped:
                grouped[pname].append(fn)

        patch_surfaces: dict[str, list[int]] = {}
        for pname, quads in grouped.items():
            if not quads:
                continue
            stag = self._surf_id
            self._surf_id += 1
            self.gmsh.model.addDiscreteEntity(2, stag)
            elem_tags: list[int] = []
            conn: list[int] = []
            for fn in quads:
                elem_tags.append(self._elem_id)
                self._elem_id += 1
                conn.extend(fn)
            self.gmsh.model.mesh.addElements(2, stag, [3], [elem_tags], [conn])
            patch_surfaces[pname] = [stag]
        return patch_surfaces

    def write(
        self,
        msh_path: Path,
        zone_volumes: dict[str, list[int]],
        patch_surfaces: dict[str, list[int]],
        *,
        report_extra: dict | None = None,
    ) -> None:
        pid = 1
        zone_report: dict[str, int] = {}
        for zname, vtags in zone_volumes.items():
            if not vtags:
                continue
            self.gmsh.model.addPhysicalGroup(3, vtags, tag=pid, name=zname)
            zone_report[zname] = len(vtags)
            pid += 1
        patch_report: dict[str, int] = {}
        for pname, stags in patch_surfaces.items():
            ut = sorted(set(stags))
            if not ut:
                continue
            self.gmsh.model.addPhysicalGroup(2, ut, tag=pid, name=pname)
            patch_report[pname] = len(ut)
            pid += 1
        msh_path.parent.mkdir(parents=True, exist_ok=True)
        self.gmsh.write(str(msh_path))
        report = {"structured": True, "zones": zone_report, "patches": patch_report, **(report_extra or {})}
        (msh_path.parent / "patch_groups_g2_solid.json").write_text(json.dumps(report, indent=2))
        print(f"Wrote {msh_path}")
        print(f"Structured report: {report}")


def build_solid_curves(bi: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    scl_outer = np.vstack([bi["sclera_tm_wrap_right"], bi["sclera_post_right"][-2::-1]])
    return {
        "cornea_outer": bi["cornea_outside_right"],
        "cornea_inner": bi["cornea_inside_right"],
        "sclera_outer": _snap_axis(scl_outer),
        "sclera_inner": bi["choroid_sclera_right"],
        "choroid_outer": bi["choroid_ret_right"],
        "choroid_inner": bi["retina_choroid_right"],
        "retina_outer": bi["retina_choroid_right"],
        "retina_inner": bi["vitreous_retina_right"],
    }


def _build_coat_grids(ms: HexVolumeMesher, bi: dict[str, np.ndarray], cfg: dict) -> list[str]:
    c = build_solid_curves(bi)
    n_m = cfg["n_merid"]
    ly = cfg["layers"]
    ms.add_shell("cornea", c["cornea_outer"], c["cornea_inner"], n_m=n_m // 2, n_r=ly["cornea"])
    ms.add_shell("sclera", c["sclera_outer"], c["sclera_inner"], n_m=n_m, n_r=ly["sclera"])
    ms.add_shell("choroid", c["choroid_outer"], c["choroid_inner"], n_m=n_m, n_r=ly["choroid"])
    ms.add_shell(
        "retina",
        c["retina_outer"],
        c["retina_inner"],
        n_m=n_m,
        n_r=ly["retina"],
        shared_outer="choroid",
    )
    return ["cornea", "sclera", "choroid", "retina"]


def _build_coat_mesh(ms: HexVolumeMesher, bi: dict[str, np.ndarray], cfg: dict) -> list[str]:
    zone_names = _build_coat_grids(ms, bi, cfg)
    ms.revolve(zone_names, n_theta=cfg["n_theta"])
    return zone_names


def mesh_g2_solid_structured(
    bi: dict[str, np.ndarray],
    anatomy: dict[str, np.ndarray],
    msh_path: Path,
    *,
    mesh_level: str = "M1",
    merged: bool = False,
) -> None:
    if mesh_level not in STRUCTURED_LEVELS:
        raise ValueError(f"unknown structured mesh_level {mesh_level}")
    cfg = STRUCTURED_LEVELS[mesh_level]

    if merged:
        mesh_g2_solid_merged(bi, anatomy, msh_path, mesh_level=mesh_level)
        return

    import gmsh

    gmsh.initialize()
    gmsh.model.add("eye_g2_solid_structured")
    gmsh.option.setNumber("General.Terminal", 1)
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)

    ms = HexVolumeMesher()
    zone_names = _build_coat_mesh(ms, bi, cfg)
    all_vols = [v for n in zone_names for v in ms.volume_tags.get(n, [])]
    patches = ms.extract_boundary_patches(all_vols, classifier=classify_solid_patch, patch_names=SOLID_PATCHES)
    ms.write(
        msh_path,
        {n: ms.volume_tags.get(n, []) for n in zone_names},
        patches,
        report_extra={"n_theta": cfg["n_theta"], "n_merid": cfg["n_merid"], "mesh_level": mesh_level, "coat_only": True},
    )
    gmsh.finalize()


def mesh_g2_solid_merged(
    bi: dict[str, np.ndarray],
    anatomy: dict[str, np.ndarray],
    msh_path: Path,
    *,
    mesh_level: str = "M1",
) -> None:
    try:
        from gen_lamminsalo_g2 import mesh_g2_solid
    except ImportError:
        from brunaStuff.gen_lamminsalo_g2 import mesh_g2_solid

    cfg = STRUCTURED_LEVELS[mesh_level]
    import gmsh

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        coat_path = tmp_path / "coat.msh"
        int_path = tmp_path / "internals.msh"

        gmsh.initialize()
        gmsh.model.add("coat")
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
        ms = HexVolumeMesher()
        zone_names = _build_coat_mesh(ms, bi, cfg)
        all_vols = [v for n in zone_names for v in ms.volume_tags.get(n, [])]
        patches = ms.extract_boundary_patches(all_vols, classifier=classify_solid_patch, patch_names=SOLID_PATCHES)
        ms.write(
            coat_path,
            {n: ms.volume_tags.get(n, []) for n in zone_names},
            patches,
            report_extra={"coat_only": True},
        )
        gmsh.finalize()

        mesh_g2_solid(
            anatomy,
            int_path,
            mesh_level=mesh_level,
            bands=("band_ciliary", "lens", "iris"),
        )

        report = merge_msh_files(
            msh_path,
            [
                (coat_path, {"cornea", "sclera", "choroid", "retina"}, True),
                (int_path, INTERNAL_ZONES, False),
            ],
        )
        report.update({"merged": True, "mesh_level": mesh_level, "n_theta": cfg["n_theta"]})
        (msh_path.parent / "patch_groups_g2_solid.json").write_text(json.dumps(report, indent=2))
        print(f"Merged solid → {msh_path}")
        print(f"Merge report: {report}")


def resample_open(pts: np.ndarray, n: int) -> np.ndarray:
    pts = np.asarray(pts, dtype=float)
    s = np.linspace(0.0, 1.0, n)
    return _interp_curve(pts, s)


def build_fluid_meridional_outer(bi: dict[str, np.ndarray]) -> np.ndarray:
    """Open meridional outer fluid silhouette (cornea apex → lens apex)."""
    return build_fluid_cavity_meridional(bi)


def build_fluid_cavity_meridional(bi: dict[str, np.ndarray]) -> np.ndarray:
    """Continuous AC∪vitreous outer wall (cornea → TM → hyaloid → vitreous → lens front)."""
    cor = bi["cornea_inside_right"]
    tm = bi["tm_markers_right"]
    hy = bi["hyaloid_right"]
    vit = bi["vitreous_retina_right"].copy()
    vit[-1, 0] = 0.0
    lens = bi["lens_right"]
    ie = int(np.argmax(np.abs(lens[:, 0])))
    lens_front = lens[: ie + 1][::-1]
    path = np.vstack([cor, tm[1:], hy[1:], vit[1:], lens_front[1:]])
    path[0, 0] = 0.0
    path[-1, 0] = 0.0
    return path


def _fluid_inner_on_ray(
    p_outer: np.ndarray,
    lens: np.ndarray,
    iris: np.ndarray,
    *,
    base_frac: float = 0.35,
) -> np.ndarray:
    """Move inward along a meridional ray (fixed y) so the quad grid stays structured."""
    r = float(p_outer[0])
    y = float(p_outer[1])
    if r < 2.0e-6:
        return np.array([1.0e-6, y])
    for frac in np.linspace(base_frac, 0.96, 36):
        p = np.array([max(1.0e-6, r * frac), y])
        if not point_in_poly(p, lens) and not point_in_poly(p, iris):
            return p
    return np.array([max(1.0e-6, r * 0.96), y])


# Radial grading at TM: lower exponent → smoother cell transition, better orthogonality.
TM_CLUSTER_EXP = 1.22
TM_STATION_MARGIN_M = 2.4e-3


def _tm_indices(outer_rs: np.ndarray, tm_pts: np.ndarray, *, margin: float = TM_STATION_MARGIN_M) -> set[int]:
    idx: set[int] = set()
    for i, p in enumerate(outer_rs):
        if np.min(np.linalg.norm(tm_pts - p, axis=1)) < margin:
            idx.add(i)
    return idx


def _subpath_between(path: np.ndarray, p_start: np.ndarray, p_end: np.ndarray) -> np.ndarray:
    """Extract the contiguous stretch of `path` between the nodes closest to p_start/p_end."""
    i0 = int(np.argmin(np.linalg.norm(path - p_start, axis=1)))
    i1 = int(np.argmin(np.linalg.norm(path - p_end, axis=1)))
    if i1 < i0:
        i0, i1 = i1, i0
    if i1 == i0:
        return np.vstack([p_start, p_end])
    return path[i0 : i1 + 1]


def _resample_segment(path: np.ndarray, n: int, p0: np.ndarray, p1: np.ndarray) -> np.ndarray:
    """Resample a path stretch to `n` points pinned at p0 and p1."""
    if n < 2:
        raise ValueError("segment needs at least two stations")
    sub = _subpath_between(path, p0, p1)
    if len(sub) < 2:
        sub = np.vstack([p0, p1])
    rs = resample_open(sub, n)
    rs[0] = p0
    rs[-1] = p1
    return rs


def build_fluid_outer_stations(
    bi: dict[str, np.ndarray],
    *,
    n_c: int,
    n_mid: int,
    n_v: int,
    n_lens: int,
) -> tuple[np.ndarray, slice, slice]:
    """Meridional fluid outer polyline with fixed segment sizes for FSI binding."""
    cor = resample_open(bi["cornea_inside_right"], n_c)
    tm = bi["tm_markers_right"]
    hy = bi["hyaloid_right"]
    mid = resample_open(np.vstack([tm[1:], hy[1:]]), n_mid)
    vit = resample_open(bi["vitreous_retina_right"], n_v)
    vit[-1, 0] = 0.0
    lens = bi["lens_right"]
    ie = int(np.argmax(np.abs(lens[:, 0])))
    lens_front = lens[: ie + 1][::-1]
    lens_seg = resample_open(lens_front, n_lens)
    lens_seg[-1, 0] = 0.0
    outer = np.vstack([cor, mid[1:], vit[1:], lens_seg[1:]])
    outer[0, 0] = max(outer[0, 0], 1.0e-6)
    outer[-1, 0] = max(outer[-1, 0], 1.0e-6)
    i_vit = slice(n_c + n_mid - 1, n_c + n_mid - 1 + n_v)
    return outer, slice(0, n_c), i_vit


def build_fluid_outer_conformal(
    bi: dict[str, np.ndarray],
    ms: HexVolumeMesher,
    *,
    n_mid: int,
    n_lens: int,
) -> tuple[np.ndarray, slice, slice]:
    """Continuous meridional outer path with coat FSI rows for cornea + retina."""
    cor = np.asarray(ms.curves["cornea"], dtype=float)
    ret = np.asarray(ms.curves["retina"], dtype=float)
    n_c, n_v = len(cor), len(ret)
    full = build_fluid_cavity_meridional(bi)
    mid = _resample_segment(full, n_mid, cor[-1], ret[0])

    lens = bi["lens_right"]
    ie = int(np.argmax(np.abs(lens[:, 0])))
    lens_apex = lens[: ie + 1][::-1][-1].copy()
    lens_apex[0] = 0.0
    # Posterior pole (ret[-1]) → anterior lens apex along symmetry plane x=0 (90° calotte spine).
    n_axis = max(4, n_lens // 2 + 2)
    axis = np.column_stack([np.zeros(n_axis), np.linspace(ret[-1, 1], lens_apex[1], n_axis)])
    axis[0] = ret[-1]
    axis[-1] = lens_apex

    outer = np.vstack([cor, mid[1:], ret, axis[1:]])
    i_cor = slice(0, n_c)
    i_vit = slice(n_c + n_mid - 1, n_c + n_mid - 1 + n_v)
    return outer, i_cor, i_vit


def _build_fluid_mesh_conformal(
    ms: HexVolumeMesher,
    bi: dict[str, np.ndarray],
    fluid: dict[str, np.ndarray],
    cfg: dict,
    *,
    fsi_cornea_row: list[int],
    fsi_retina_row: list[int],
) -> None:
    n_m = cfg["n_merid"]
    n_mid = max(n_m // 3, 6)
    n_lens = max(n_m // 4, 6)
    outer, i_cor, i_vit = build_fluid_outer_conformal(
        bi, ms, n_mid=n_mid, n_lens=n_lens,
    )
    if len(fsi_cornea_row) != i_cor.stop - i_cor.start or len(fsi_retina_row) != i_vit.stop - i_vit.start:
        raise ValueError(
            f"FSI station count mismatch cornea {len(fsi_cornea_row)} vs {i_cor.stop - i_cor.start}, "
            f"retina {len(fsi_retina_row)} vs {i_vit.stop - i_vit.start}"
        )

    lens = resample_curve(fluid["lens_half"], max(16, n_m // 3) + 1)
    iris = resample_curve(fluid["iris_half"], max(12, n_m // 4) + 1)
    tm_idx = _tm_indices(outer, bi["tm_markers_right"])
    n_r = max(cfg["n_r_fluid"], cfg["fluid_tm_layers"] + 3)

    inner_pts = np.array([_fluid_inner_on_ray(p, lens, iris) for p in outer])
    grid = np.zeros((n_r + 1, len(outer), 2))
    for i, p_out in enumerate(outer):
        p_in = inner_pts[i]
        cluster = i in tm_idx or any(abs(i - j) <= 1 for j in tm_idx)
        for j in range(n_r + 1):
            s = j / n_r
            if cluster:
                s = 1.0 - (1.0 - s) ** TM_CLUSTER_EXP
            grid[j, i] = (1.0 - s) * p_out + s * p_in

    outer_tags: list[int] = [0] * len(outer)
    for i in range(i_cor.start, i_cor.stop):
        outer_tags[i] = fsi_cornea_row[i - i_cor.start]
    for i in range(i_vit.start, i_vit.stop):
        outer_tags[i] = fsi_retina_row[i - i_vit.start]

    ms.add_grid("fluid", grid, bind_rows={0: outer_tags})


def _export_gmsh_domain(
    ms: HexVolumeMesher,
    *,
    volume_names: list[str],
    patch_surfaces: dict[str, list[int]],
    msh_path: Path,
    report_path: Path | None,
    report_extra: dict | None = None,
) -> dict:
    """Write one OpenFOAM .msh subset from the current discrete model."""
    node_coords: dict[int, tuple[float, float, float]] = {}
    elements: list[tuple[int, int, list[int]]] = []
    zone_counts: dict[str, int] = {}

    phy: dict[int, tuple[int, str]] = {}
    next_phy = 1
    ztag: dict[str, int] = {}
    for zname in volume_names:
        ztag[zname] = next_phy
        phy[next_phy] = (3, zname)
        next_phy += 1

    for zname in volume_names:
        count = 0
        for v in ms.volume_tags.get(zname, []):
            ntags, c, _ = ms.gmsh.model.mesh.getNodes(3, v)
            for i, t in enumerate(ntags):
                node_coords[int(t)] = (c[3 * i], c[3 * i + 1], c[3 * i + 2])
            etypes, _, enodes = ms.gmsh.model.mesh.getElements(3, v)
            if 5 not in etypes:
                continue
            hi = list(etypes).index(5)
            nodes = enodes[hi]
            for h in range(0, len(nodes), 8):
                hn = [int(x) for x in nodes[h : h + 8]]
                elements.append((5, ztag[zname], hn))
                count += 1
        zone_counts[zname] = count

    patch_names = sorted(patch_surfaces)
    patch_phy: dict[str, int] = {}
    patch_counts: dict[str, int] = {p: 0 for p in patch_names}
    for pname in patch_names:
        patch_phy[pname] = next_phy
        phy[next_phy] = (2, pname)
        next_phy += 1

    for pname, stags in patch_surfaces.items():
        for stag in stags:
            etypes, _, enodes = ms.gmsh.model.mesh.getElements(2, stag)
            if 3 not in etypes:
                continue
            qi = list(etypes).index(3)
            quads = enodes[qi]
            for q in range(0, len(quads), 4):
                fn = [int(x) for x in quads[q : q + 4]]
                for n in fn:
                    if n not in node_coords:
                        xyz = ms.gmsh.model.mesh.getNode(n)[0]
                        node_coords[n] = (float(xyz[0]), float(xyz[1]), float(xyz[2]))
                elements.append((3, patch_phy[pname], fn))
                patch_counts[pname] = patch_counts.get(pname, 0) + 1

    data = MshData(nodes=node_coords, elements=elements, physical=phy)
    write_msh(msh_path, data)
    report = {
        "zones": zone_counts,
        "patches": patch_counts,
        "n_nodes": len(node_coords),
        **(report_extra or {}),
    }
    if report_path:
        report_path.write_text(json.dumps(report, indent=2))
    print(f"Wrote {msh_path}")
    print(f"Export report: {report}")
    return report


def mesh_g2_fsi_conformal_pair(
    bi: dict[str, np.ndarray],
    fluid: dict[str, np.ndarray],
    anatomy: dict[str, np.ndarray],
    fluid_path: Path,
    solid_path: Path,
    *,
    mesh_level: str = "M1",
    merge_internals: bool = False,
) -> None:
    """Conformal FSI: `fsi_wall` (fluid) and `fsi_active` (solid) share 3D nodes on cornea + retina."""
    if mesh_level not in STRUCTURED_LEVELS:
        raise ValueError(f"unknown structured mesh_level {mesh_level}")
    cfg = STRUCTURED_LEVELS[mesh_level]
    import gmsh

    gmsh.initialize()
    gmsh.model.add("eye_g2_fsi_conformal")
    gmsh.option.setNumber("General.Terminal", 1)
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)

    ms = HexVolumeMesher()
    zone_names = _build_coat_grids(ms, bi, cfg)
    fsi_cornea = list(ms.node_grids["cornea"][-1])
    fsi_retina = list(ms.node_grids["retina"][-1])
    _build_fluid_mesh_conformal(
        ms, bi, fluid, cfg,
        fsi_cornea_row=fsi_cornea,
        fsi_retina_row=fsi_retina,
    )
    ms.revolve(zone_names + ["fluid"], n_theta=cfg["n_theta"])

    solid_vols = [v for n in zone_names for v in ms.volume_tags.get(n, [])]
    fluid_vols = ms.volume_tags.get("fluid", [])
    fsi_2d = set(fsi_cornea) | set(fsi_retina)
    solid_fsi, fluid_fsi = ms.extract_conformal_fsi_faces(
        solid_vols=solid_vols,
        fluid_vols=fluid_vols,
        fsi_2d_tags=fsi_2d,
        n_theta=cfg["n_theta"],
    )
    print(f"INFO: conformal FSI faces solid={len(solid_fsi)} fluid={len(fluid_fsi)}")
    ms.verify_conformal_fsi(solid_fsi, fluid_fsi)

    solid_patches = ms.extract_boundary_patches(
        solid_vols,
        classifier=classify_solid_patch,
        patch_names=tuple(p for p in SOLID_PATCHES if p != "fsi_active"),
    )
    solid_patches["fsi_active"] = ms._write_quad_patch(solid_fsi, "fsi_active")

    lens_rs = resample_curve(fluid["lens_half"], max(16, cfg["n_merid"] // 3) + 1)
    iris_rs = resample_curve(fluid["iris_half"], max(12, cfg["n_merid"] // 4) + 1)

    def hole_class(cx, cy, cz):
        p2 = np.array([math.hypot(cx, cz), cy])
        if point_in_poly(p2, lens_rs):
            return "lens"
        if point_in_poly(p2, iris_rs):
            return "iris"
        return None

    fluid_patches = ms.extract_boundary_patches(
        fluid_vols,
        classifier=classify_fluid_patch,
        patch_names=("symmetry_0", "symmetry_90", "lens_wall", "iris_wall"),
        hole_classifier=hole_class,
    )
    fsi_keys = {tuple(sorted(fn)) for fn in fluid_fsi}
    wall_only = [
        fn for _, fn in ms._boundary_hex_faces(fluid_vols)
        if tuple(sorted(fn)) not in fsi_keys
        and classify_fluid_patch(
            *[sum(ms._node_coords()[n][i] for n in fn) / 4.0 for i in range(3)],
            hole=hole_class(*[sum(ms._node_coords()[n][i] for n in fn) / 4.0 for i in range(3)]),
        ) == "wall"
    ]
    fluid_patches["fsi_wall"] = ms._write_quad_patch(fluid_fsi, "fsi_wall")
    fluid_patches["wall"] = ms._write_quad_patch(wall_only, "wall")

    coat_path = solid_path.parent / f"_coat_conformal_{mesh_level}.msh"
    _export_gmsh_domain(
        ms,
        volume_names=zone_names,
        patch_surfaces=solid_patches,
        msh_path=coat_path,
        report_path=None,
        report_extra={"conformal_coat": True},
    )
    _export_gmsh_domain(
        ms,
        volume_names=["fluid"],
        patch_surfaces=fluid_patches,
        msh_path=fluid_path,
        report_path=fluid_path.parent / "patch_groups_g2_fluid.json",
        report_extra={
            "conformal_fsi": True,
            "mesh_level": mesh_level,
            "n_theta": cfg["n_theta"],
            "n_merid": cfg["n_merid"],
            "fluid_tm_layers": cfg["fluid_tm_layers"],
        },
    )
    gmsh.finalize()

    if merge_internals:
        try:
            from gen_lamminsalo_g2 import mesh_g2_solid
        except ImportError:
            from brunaStuff.gen_lamminsalo_g2 import mesh_g2_solid
        with tempfile.TemporaryDirectory() as tmp:
            int_path = Path(tmp) / "internals.msh"
            mesh_g2_solid(
                anatomy, int_path, mesh_level=mesh_level,
                bands=("band_ciliary", "lens", "iris"),
            )
            report = merge_msh_files(
                solid_path,
                [
                    (coat_path, {"cornea", "sclera", "choroid", "retina"}, True),
                    (int_path, INTERNAL_ZONES, False),
                ],
            )
            report.update({"conformal_fsi_coat": True, "mesh_level": mesh_level})
            (solid_path.parent / "patch_groups_g2_solid.json").write_text(json.dumps(report, indent=2))
            print(f"Merged conformal solid → {solid_path}")
    else:
        shutil.copy2(coat_path, solid_path)
        (solid_path.parent / "patch_groups_g2_solid.json").write_text(
            json.dumps({"conformal_fsi": True, "coat_only": True, "mesh_level": mesh_level}, indent=2)
        )

    coat_path.unlink(missing_ok=True)


def mesh_g2_fluid_hex(
    bi: dict[str, np.ndarray],
    fluid: dict[str, np.ndarray],
    msh_path: Path,
    *,
    mesh_level: str = "M1",
) -> dict:
    """Structured hex fluid mesh (revolved quads) with TM radial clustering.

    Produces type-5 hexahedra with near-orthogonal faces — preferred over OCC
    prisms for checkMesh quality and transient stability.
    """
    if mesh_level not in STRUCTURED_LEVELS:
        raise ValueError(f"unknown structured mesh_level {mesh_level}")
    cfg = STRUCTURED_LEVELS[mesh_level]
    import gmsh

    gmsh.initialize()
    gmsh.model.add("eye_g2_fluid_hex")
    gmsh.option.setNumber("General.Terminal", 1)
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)

    ms = HexVolumeMesher()
    _build_coat_grids(ms, bi, cfg)
    fsi_cornea = list(ms.node_grids["cornea"][-1])
    fsi_retina = list(ms.node_grids["retina"][-1])
    _build_fluid_mesh_conformal(
        ms, bi, fluid, cfg,
        fsi_cornea_row=fsi_cornea,
        fsi_retina_row=fsi_retina,
    )
    ms.revolve(["fluid"], n_theta=cfg["n_theta"])

    fluid_vols = ms.volume_tags.get("fluid", [])
    lens_rs = resample_curve(fluid["lens_half"], max(16, cfg["n_merid"] // 3) + 1)
    iris_rs = resample_curve(fluid["iris_half"], max(12, cfg["n_merid"] // 4) + 1)

    def hole_class(cx, cy, cz):
        p2 = np.array([math.hypot(cx, cz), cy])
        if point_in_poly(p2, lens_rs):
            return "lens"
        if point_in_poly(p2, iris_rs):
            return "iris"
        return None

    fluid_patches = ms.extract_boundary_patches(
        fluid_vols,
        classifier=classify_fluid_patch,
        patch_names=("symmetry_0", "symmetry_90", "lens_wall", "iris_wall"),
        hole_classifier=hole_class,
    )
    wall_only = [
        fn for _, fn in ms._boundary_hex_faces(fluid_vols)
        if classify_fluid_patch(
            *[sum(ms._node_coords()[n][i] for n in fn) / 4.0 for i in range(3)],
            hole=hole_class(*[sum(ms._node_coords()[n][i] for n in fn) / 4.0 for i in range(3)]),
        ) == "wall"
    ]
    fluid_patches["wall"] = ms._write_quad_patch(wall_only, "wall")

    pid = 1
    gmsh.model.addPhysicalGroup(3, fluid_vols, tag=pid, name="fluid")
    pid += 1
    patch_report: dict[str, int] = {}
    for pname, stags in fluid_patches.items():
        utags = sorted(set(stags))
        if not utags:
            continue
        gmsh.model.addPhysicalGroup(2, utags, tag=pid, name=pname)
        patch_report[pname] = len(utags)
        pid += 1
    n_hex = sum(len(ms._collect_hexes(fluid_vols)) for _ in [0])
    msh_path.parent.mkdir(parents=True, exist_ok=True)
    gmsh.write(str(msh_path))
    report = {
        "zones": {"fluid": n_hex},
        "patches": patch_report,
        "mesh_level": mesh_level,
        "n_theta": cfg["n_theta"],
        "n_merid": cfg["n_merid"],
        "fluid_tm_layers": cfg["fluid_tm_layers"],
        "tm_cluster_exp": TM_CLUSTER_EXP,
        "method": "hex_revolve_tm_cluster",
    }
    (msh_path.parent / "patch_groups_g2_fluid.json").write_text(json.dumps(report, indent=2))
    print(f"Wrote {msh_path}")
    print(f"Export report: {report}")
    gmsh.finalize()
    return report


def mesh_g2_fluid_structured(
    bi: dict[str, np.ndarray],
    fluid: dict[str, np.ndarray],
    msh_path: Path,
    *,
    mesh_level: str = "M1",
    tip_refine: bool = True,
    tip_sites: str = "both",
    use_hex: bool = False,
) -> None:
    """Structured fluid mesh with TM band clustering (≥5 layers at TM).

    Default: OCC revolve + prisms (gmshToFoam-stable). use_hex=True tries revolved
    hex grid (experimental — fails checkMesh today).
    """
    if mesh_level not in STRUCTURED_LEVELS:
        raise ValueError(f"unknown structured mesh_level {mesh_level}")
    cfg = STRUCTURED_LEVELS[mesh_level]
    if tip_refine:
        try:
            from gen_lamminsalo_g2 import mesh_g2_fluid
        except ImportError:
            from brunaStuff.gen_lamminsalo_g2 import mesh_g2_fluid

        mesh_g2_fluid(
            fluid,
            msh_path,
            mesh_level=mesh_level,
            tm_markers=bi.get("tm_markers_right"),
            tm_layers=cfg["fluid_tm_layers"],
            tip_refine=True,
            tip_sites=tip_sites,
        )
        report_path = msh_path.parent / "patch_groups_g2_fluid.json"
        report = json.loads(report_path.read_text()) if report_path.exists() else {}
        report.update(
            {
                "structured": True,
                "mesh_level": mesh_level,
                "n_merid": cfg["n_merid"],
                "fluid_tm_layers": cfg["fluid_tm_layers"],
                "method": "occ_revolve_tm_refine",
            }
        )
    elif use_hex:
        report = mesh_g2_fluid_hex(bi, fluid, msh_path, mesh_level=mesh_level)
        report["structured"] = True
        report["tm_refined"] = True
    else:
        try:
            from gen_lamminsalo_g2 import mesh_g2_fluid
        except ImportError:
            from brunaStuff.gen_lamminsalo_g2 import mesh_g2_fluid

        mesh_g2_fluid(
            fluid,
            msh_path,
            mesh_level=mesh_level,
            tm_markers=bi.get("tm_markers_right"),
            tm_layers=cfg["fluid_tm_layers"],
            tip_refine=False,
            tip_sites=tip_sites,
            tm_size_field=True,
            tip_topo_refine=True,
        )
        report_path = msh_path.parent / "patch_groups_g2_fluid.json"
        report = json.loads(report_path.read_text()) if report_path.exists() else {}
        report.update(
            {
                "structured": True,
                "mesh_level": mesh_level,
                "n_merid": cfg["n_merid"],
                "fluid_tm_layers": cfg["fluid_tm_layers"],
                "method": "occ_revolve_tm_refine",
            }
        )
    report_path = msh_path.parent / "patch_groups_g2_fluid.json"
    report_path.write_text(json.dumps(report, indent=2))
    print(f"Structured fluid report: {report}")
