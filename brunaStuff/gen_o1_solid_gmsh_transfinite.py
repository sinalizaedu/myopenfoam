#!/usr/bin/env python3
"""O1 Lamminsalo solid: Gmsh transfinite 2D quads + 90° Extrude revolve.

Three geometry groupings (g1/g2/g3):
  g1 — one fused solid volume (all tissues)
  g2 — coat + iris (iris separate)
  g3 — coat + ciliary + iris (three solids)

Uses the same H1 strip layout as ``o1_solid_export.py`` / D1.
Writes ``.geo``, runs ``gmsh -3``, produces OpenFOAM msh2.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from o1_solid_anatomy import N_THETA_TOTAL, Point
from o1_solid_export import build_mesh_from_kwargs

try:
    from g2_structured_mesh import HEX_FACES, classify_solid_patch, read_msh, write_msh
except ImportError:  # pragma: no cover
    HEX_FACES = read_msh = write_msh = classify_solid_patch = None  # type: ignore

REVOLVE_RAD = 0.5 * 3.14159265358979323846


@dataclass
class GeoBuilder:
    scale: float = 0.001
    lines: list[str] = field(default_factory=list)
    pid: int = 1
    lid: int = 1
    sid: int = 1
    clid: int = 1
    points: dict[tuple[float, float], int] = field(default_factory=dict)
    lines_by_edge: dict[tuple[int, int], int] = field(default_factory=dict)
    line_dir: dict[tuple[int, int], tuple[int, int]] = field(default_factory=dict)
    surfaces: list[int] = field(default_factory=list)
    surface_zone: dict[int, str] = field(default_factory=dict)
    curve_patches: dict[int, str] = field(default_factory=dict)

    def pt(self, p: Point) -> int:
        key = (round(p.r, 8), round(p.y, 8))
        if key not in self.points:
            x, y = p.r * self.scale, p.y * self.scale
            self.lines.append(f"Point({self.pid}) = {{{x:.16e}, {y:.16e}, 0}};")
            self.points[key] = self.pid
            self.pid += 1
        return self.points[key]

    def line(self, a: int, b: int) -> int:
        if a == b:
            raise ValueError(f"degenerate line {a}-{b}")
        key = (min(a, b), max(a, b))
        if key not in self.lines_by_edge:
            self.lines.append(f"Line({self.lid}) = {{{a}, {b}}};")
            self.lines_by_edge[key] = self.lid
            self.line_dir[key] = (a, b)
            self.lid += 1
        return self.lines_by_edge[key]

    def oriented_line(self, a: int, b: int) -> int:
        """Return signed line id for traversal a → b."""
        key = (min(a, b), max(a, b))
        lid = self.line(a, b)
        fwd = self.line_dir[key]
        if (a, b) == fwd:
            return lid
        if (b, a) == fwd:
            return -lid
        raise RuntimeError(f"line {lid} direction mismatch {a}→{b}")

    def transfinite_line(self, lid: int, n: int) -> None:
        self.lines.append(f"Transfinite Line {{{lid}}} = {n};")

    def add_surface(self, p_bl: int, p_br: int, p_tr: int, p_tl: int, *, zone: str) -> int:
        """Quad surface: bottom-left → bottom-right → top-right → top-left (CCW)."""
        l_bot = self.oriented_line(p_bl, p_br)
        l_right = self.oriented_line(p_br, p_tr)
        l_top = self.oriented_line(p_tr, p_tl)
        l_left = self.oriented_line(p_tl, p_bl)
        self.lines.append(
            f"Curve Loop({self.clid}) = {{{l_bot}, {l_right}, {l_top}, {l_left}}};"
        )
        loop = self.clid
        self.clid += 1
        self.lines.append(f"Plane Surface({self.sid}) = {{{loop}}};")
        sid = self.sid
        self.surfaces.append(sid)
        self.surface_zone[sid] = zone
        self.sid += 1
        return sid

    def tag_curve_patch(self, p_a: int, p_b: int, name: str) -> None:
        lid = self.line(p_a, p_b)
        self.curve_patches[lid] = name


def volume_group(zone: str, geometry: str) -> str:
    if geometry == "g1":
        return "solid"
    if geometry == "g2":
        return "iris" if zone == "iris" else "coat"
    if geometry == "g3":
        if zone == "iris":
            return "iris"
        if zone == "ciliary":
            return "ciliary"
        return "coat"
    raise ValueError(f"unknown geometry {geometry}")


def strip_segment_grid(strip, seg: int, nr: int):
    p0, p1 = strip.inner[seg], strip.inner[seg + 1]
    q0, q1 = strip.outer[seg], strip.outer[seg + 1]
    nt = max(1, strip.counts[seg])
    grid: list[list[Point]] = []
    for j in range(nr + 1):
        fj = j / nr
        a = Point((1 - fj) * p0.r + fj * q0.r, (1 - fj) * p0.y + fj * q0.y)
        b = Point((1 - fj) * p1.r + fj * q1.r, (1 - fj) * p1.y + fj * q1.y)
        row = []
        for i in range(nt + 1):
            fi = i / nt
            row.append(Point((1 - fi) * a.r + fi * b.r, (1 - fi) * a.y + fi * b.y))
        grid.append(row)
    return grid, nt, nr


def write_geo(
    strips,
    out_geo: Path,
    *,
    geometry: str = "g1",
    n_theta: int = N_THETA_TOTAL,
    scale: float = 0.001,
    radial_scale: int = 1,
    tangential_scale: int = 1,
) -> dict:
    g = GeoBuilder(scale=scale)
    g.lines.extend(
        [
            f"// O1 solid transfinite + Extrude revolve — geometry {geometry}",
            "// Generated by brunaStuff/gen_o1_solid_gmsh_transfinite.py",
            f"n_theta = {n_theta};",
            "Mesh.RecombineAll = 1;",
            "Mesh.SubdivisionAlgorithm = 1;",
            "",
        ]
    )

    n_surf = 0
    for strip in strips:
        for seg in range(len(strip.counts)):
            nr = max(1, strip.radial * radial_scale)
            grid, nt, nr = strip_segment_grid(strip, seg, nr)
            nt = max(1, nt * tangential_scale)
            if tangential_scale != 1:
                # Rebuild grid with scaled tangential resolution.
                p0, p1 = strip.inner[seg], strip.inner[seg + 1]
                q0, q1 = strip.outer[seg], strip.outer[seg + 1]
                grid = []
                for j in range(nr + 1):
                    fj = j / nr
                    a = Point((1 - fj) * p0.r + fj * q0.r, (1 - fj) * p0.y + fj * q0.y)
                    b = Point((1 - fj) * p1.r + fj * q1.r, (1 - fj) * p1.y + fj * q1.y)
                    row = []
                    for i in range(nt + 1):
                        fi = i / nt
                        row.append(Point((1 - fi) * a.r + fi * b.r, (1 - fi) * a.y + fi * b.y))
                    grid.append(row)

            bl = g.pt(grid[0][0])
            br = g.pt(grid[0][-1])
            tr = g.pt(grid[-1][-1])
            tl = g.pt(grid[-1][0])
            sid = g.add_surface(bl, br, tr, tl, zone=strip.zone)
            n_surf += 1

            l_bot = abs(g.oriented_line(bl, br))
            l_right = abs(g.oriented_line(br, tr))
            l_top = abs(g.oriented_line(tr, tl))
            l_left = abs(g.oriented_line(tl, bl))
            g.transfinite_line(l_bot, nt + 1)
            g.transfinite_line(l_top, nt + 1)
            g.transfinite_line(l_right, nr + 1)
            g.transfinite_line(l_left, nr + 1)
            g.lines.append(f"Transfinite Surface {{{sid}}} = {{{bl}, {br}, {tr}, {tl}}};")
            g.lines.append(f"Recombine Surface {{{sid}}};")

            if strip.inner_patch and seg == 0:
                for i in range(nt):
                    g.tag_curve_patch(g.pt(grid[0][i]), g.pt(grid[0][i + 1]), strip.inner_patch)
            if strip.outer_patch:
                for i in range(nt):
                    g.tag_curve_patch(g.pt(grid[-1][i]), g.pt(grid[-1][i + 1]), strip.outer_patch)
            if strip.start_patch and seg == 0:
                for j in range(nr):
                    g.tag_curve_patch(g.pt(grid[j][0]), g.pt(grid[j + 1][0]), strip.start_patch)
            if strip.end_patch and seg == len(strip.counts) - 1:
                for j in range(nr):
                    g.tag_curve_patch(g.pt(grid[j][-1]), g.pt(grid[j + 1][-1]), strip.end_patch)

    # 2D physical curves (patches before revolve).
    patch_curves: dict[str, list[int]] = {}
    for lid, pname in g.curve_patches.items():
        patch_curves.setdefault(pname, []).append(lid)
    next_phy = 1
    for pname, lids in sorted(patch_curves.items()):
        g.lines.append(f"Physical Curve(\"{pname}\") = {{{', '.join(map(str, lids))}}};")
        next_phy += 1

    # 2D physical surfaces (tissue tags for volume grouping after extrude).
    zone_surfaces: dict[str, list[int]] = {}
    for sid, zname in g.surface_zone.items():
        zone_surfaces.setdefault(zname, []).append(sid)
    for zname, sids in sorted(zone_surfaces.items()):
        g.lines.append(f"Physical Surface(\"{zname}_2d\") = {{{', '.join(map(str, sids))}}};")

    # Revolve each structured surface separately (out[1] = volume for Layers extrude).
    vol_refs: dict[str, list[str]] = {}
    for sid in g.surfaces:
        zname = g.surface_zone[sid]
        gname = volume_group(zname, geometry)
        g.lines.extend(
            [
                f"v{sid}[] = Extrude {{ {{0, 1, 0}}, {{0, 0, 0}}, {REVOLVE_RAD} }} {{",
                f"  Surface{{{sid}}};",
                f"  Layers {{ {n_theta} }};",
                "  Recombine;",
                "};",
            ]
        )
        vol_refs.setdefault(gname, []).append(f"v{sid}[1]")

    for gname, vids in sorted(vol_refs.items()):
        g.lines.append(f"Physical Volume(\"{gname}\") = {{{', '.join(vids)}}};")

    out_geo.parent.mkdir(parents=True, exist_ok=True)
    out_geo.write_text("\n".join(g.lines) + "\n")
    groups = {k: len(v) for k, v in vol_refs.items()}
    return {
        "geometry": geometry,
        "n_surfaces": n_surf,
        "n_theta": n_theta,
        "volume_groups": groups,
        "geo": str(out_geo),
    }


def postprocess_extruded_msh(msh_path: Path) -> dict:
    """Re-tag 3D boundary quads by position (Gmsh Extrude leaves 1D curve tags)."""
    if read_msh is None:
        raise RuntimeError("g2_structured_mesh not importable")

    from collections import defaultdict

    data = read_msh(msh_path)
    vol_elems = [(etype, phy, nodes) for etype, phy, nodes in data.elements if etype == 5]
    if not vol_elems:
        raise RuntimeError(f"no hex volumes in {msh_path}")

    vol_phy: dict[int, str] = {}
    next_phy = 1
    new_physical: dict[int, tuple[int, str]] = {}

    def vol_tag(old: int) -> int:
        if old not in vol_phy:
            nonlocal next_phy
            name = data.physical.get(old, (3, f"zone_{old}"))[1]
            vol_phy[old] = next_phy
            new_physical[next_phy] = (3, name)
            next_phy += 1
        return vol_phy[old]

    remapped_vols = [(5, vol_tag(phy), nodes) for _, phy, nodes in vol_elems]

    face_count: dict[tuple[int, ...], int] = defaultdict(int)
    face_orient: dict[tuple[int, ...], tuple[int, ...]] = {}

    for _, _, conn in remapped_vols:
        for fn_idx in HEX_FACES:
            fn = tuple(conn[i] for i in fn_idx)
            key = tuple(sorted(fn))
            face_count[key] += 1
            if key not in face_orient:
                face_orient[key] = fn

    patch_phy: dict[str, int] = {}
    patch_counts: dict[str, int] = defaultdict(int)

    def patch_tag(name: str) -> int:
        if name not in patch_phy:
            nonlocal next_phy
            patch_phy[name] = next_phy
            new_physical[next_phy] = (2, name)
            next_phy += 1
        return patch_phy[name]

    boundary = []
    for key, cnt in face_count.items():
        if cnt != 1:
            continue
        fn = face_orient[key]
        if len(set(fn)) != len(fn):
            continue
        coords = [data.nodes[n] for n in fn]
        cx = sum(p[0] for p in coords) / len(coords)
        cy = sum(p[1] for p in coords) / len(coords)
        cz = sum(p[2] for p in coords) / len(coords)
        pname = classify_solid_patch(cx, cy, cz)
        boundary.append((3, patch_tag(pname), list(fn)))
        patch_counts[pname] += 1

    out = type(data)(nodes=data.nodes, elements=remapped_vols + boundary, physical=new_physical)
    write_msh(msh_path, out)
    return {
        "n_hex": len(remapped_vols),
        "n_boundary_quads": len(boundary),
        "patches": dict(patch_counts),
        "volumes": {v: new_physical[v][1] for v in sorted(new_physical) if new_physical[v][0] == 3},
    }


def run_gmsh(geo: Path, msh: Path, *, verbose: bool = True) -> None:
    cmd = [
        "gmsh",
        str(geo),
        "-3",
        "-format",
        "msh2",
        "-o",
        str(msh),
    ]
    if verbose:
        print("RUN:", " ".join(cmd))
    result = subprocess.run(cmd, check=False)
    if not msh.is_file():
        raise RuntimeError(f"gmsh did not write {msh} (exit {result.returncode})")
    if result.returncode != 0:
        print(f"WARN: gmsh exited {result.returncode} (mesh written)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--geometry", choices=("g1", "g2", "g3"), default="g1")
    ap.add_argument("--out-geo", type=Path, required=True)
    ap.add_argument("--out-msh", type=Path, default=None)
    ap.add_argument("--mesh", action="store_true", help="run gmsh -3 after writing .geo")
    ap.add_argument("--n-theta", type=int, default=N_THETA_TOTAL)
    ap.add_argument("--variant", choices=("O1", "H1", "G1"), default="H1")
    ap.add_argument("--n-retina", type=int, default=5)
    ap.add_argument("--n-choroid", type=int, default=5)
    ap.add_argument("--n-sclera", type=int, default=5)
    ap.add_argument("--n-iris", type=int, default=5)
    ap.add_argument("--radial-scale", type=int, default=1)
    ap.add_argument("--tangential-scale", type=int, default=1)
    args = ap.parse_args()

    mesh = build_mesh_from_kwargs(
        variant=args.variant,
        n_retina=args.n_retina,
        n_choroid=args.n_choroid,
        n_sclera=args.n_sclera,
        n_iris=args.n_iris,
    )
    info = write_geo(
        mesh.strips,
        args.out_geo,
        geometry=args.geometry,
        n_theta=args.n_theta,
        radial_scale=args.radial_scale,
        tangential_scale=args.tangential_scale,
    )
    print(f"Wrote {args.out_geo}: {info}")

    if args.mesh:
        msh = args.out_msh or args.out_geo.with_suffix(".msh")
        run_gmsh(args.out_geo, msh)
        rep = postprocess_extruded_msh(msh)
        print(f"Post-processed {msh}: {rep}")
        print(f"Wrote {msh}")


if __name__ == "__main__":
    main()
