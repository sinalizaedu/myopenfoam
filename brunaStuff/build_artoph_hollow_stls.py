#!/usr/bin/env python3
"""
Build hollow-wall STLs for artoph-fsi-curva-mestrado from the read-only
artoph-curva-mestrado artery surface (no edits to that case).

  - artery_outer.stl  — copy of cases/artoph-curva-mestrado/.../artery.stl
  - artery_inner.stl  — inward offset of outer surface by wall thickness h

Also writes meshHints.json (locationInMesh for fluid/solid snappy) and
_hollow_geometry_summary.json.

Uses NumPy only (no trimesh). Wall thickness h default 0.20 mm (plan).
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np


def _cases_root() -> Path:
    p = Path(__file__).resolve()
    if p.parent.name == "scripts":
        return p.parents[2]
    return p.parents[1] / "cases"


CASES = _cases_root()
SRC_ARTERY = (
    CASES
    / "artoph-curva-mestrado"
    / "solid"
    / "constant"
    / "triSurface"
    / "artery.stl"
)
OUT_DIR = CASES / "artoph-fsi-curva-mestrado" / "constant" / "triSurface"
H_MM = 0.20  # literature-range nominal wall (mestrado pipeline target)


def read_ascii_stl_facets(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Return (vertices Nx3, faces Mx3) with merged vertices."""
    verts_list: list[tuple[float, float, float]] = []
    key_to_idx: dict[tuple[float, float, float], int] = {}
    faces_list: list[tuple[int, int, int]] = []

    def add_v(x: float, y: float, z: float) -> int:
        key = (round(x, 9), round(y, 9), round(z, 9))
        if key in key_to_idx:
            return key_to_idx[key]
        i = len(verts_list)
        verts_list.append((x, y, z))
        key_to_idx[key] = i
        return i

    buf: list[tuple[float, float, float]] = []
    with path.open() as f:
        for line in f:
            ls = line.strip()
            if ls.startswith("vertex"):
                parts = ls.split()
                buf.append((float(parts[1]), float(parts[2]), float(parts[3])))
                if len(buf) == 3:
                    i0 = add_v(*buf[0])
                    i1 = add_v(*buf[1])
                    i2 = add_v(*buf[2])
                    faces_list.append((i0, i1, i2))
                    buf.clear()
    V = np.array(verts_list, dtype=np.float64)
    F = np.array(faces_list, dtype=np.int64)
    return V, F


def write_ascii_stl(
    path: Path, vertices: np.ndarray, faces: np.ndarray, solid_name: str
) -> None:
    with path.open("w") as fp:
        fp.write(f"solid {solid_name}\n")
        for i0, i1, i2 in faces:
            p0, p1, p2 = vertices[i0], vertices[i1], vertices[i2]
            n = np.cross(p1 - p0, p2 - p0)
            ln = np.linalg.norm(n)
            if ln < 1e-30:
                n = np.array([0.0, 0.0, 1.0])
            else:
                n = n / ln
            fp.write(
                f"  facet normal {n[0]:.6e} {n[1]:.6e} {n[2]:.6e}\n"
                "    outer loop\n"
            )
            for p in (p0, p1, p2):
                fp.write(
                    f"      vertex {p[0]:.6e} {p[1]:.6e} {p[2]:.6e}\n"
                )
            fp.write("    endloop\n  endfacet\n")
        fp.write(f"endsolid {solid_name}\n")


def mesh_volume_and_fix_winding(V: np.ndarray, F: np.ndarray) -> float:
    """Signed volume; if negative, flip face winding."""
    vol = 0.0
    for i0, i1, i2 in F:
        p0, p1, p2 = V[i0], V[i1], V[i2]
        vol += np.dot(p0, np.cross(p1, p2)) / 6.0
    if vol < 0:
        F[:, [1, 2]] = F[:, [2, 1]]
        vol = -vol
    return float(vol)


def face_normals_out(V: np.ndarray, F: np.ndarray) -> np.ndarray:
    """Per-face outward normals (3,) each — assumes consistent outward winding."""
    fn = np.zeros((len(F), 3))
    for fi, (i0, i1, i2) in enumerate(F):
        p0, p1, p2 = V[i0], V[i1], V[i2]
        c = np.cross(p1 - p0, p2 - p0)
        ln = np.linalg.norm(c)
        fn[fi] = c / ln if ln > 1e-30 else np.array([0.0, 0.0, 1.0])
    return fn


def vertex_normals(V: np.ndarray, F: np.ndarray, fn: np.ndarray) -> np.ndarray:
    vn = np.zeros_like(V)
    cnt = np.zeros(len(V))
    for fi, (i0, i1, i2) in enumerate(F):
        for j in (i0, i1, i2):
            vn[j] += fn[fi]
            cnt[j] += 1.0
    nz = cnt > 0
    vn[nz] /= cnt[nz, None]
    ln = np.linalg.norm(vn, axis=1, keepdims=True)
    ln[ln < 1e-30] = 1.0
    vn /= ln
    return vn


def ray_cast_hits(
    origin: np.ndarray, direction: np.ndarray, V: np.ndarray, F: np.ndarray
) -> int:
    """Conta interseccoes do raio com a superficie (Moller-Trumbore vetorizado).

    Usado para classificar se um ponto esta dentro de uma superficie fechada
    (numero impar de hits ao longo de uma direcao aleatoria => interior).
    """
    v0 = V[F[:, 0]]
    v1 = V[F[:, 1]]
    v2 = V[F[:, 2]]
    e1 = v1 - v0
    e2 = v2 - v0
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
    """Raycast com 3 direcoes diferentes; majoritaria define classificacao
    (mais robusto a hits em arestas)."""
    dirs = [
        np.array([1.0, 0.337, 0.781]),
        np.array([0.612, 1.0, 0.234]),
        np.array([0.823, 0.516, 1.0]),
    ]
    votes = 0
    for d in dirs:
        d = d / np.linalg.norm(d)
        if ray_cast_hits(point, d, V, F) % 2 == 1:
            votes += 1
    return votes >= 2


def find_lumen_point(
    V_inner: np.ndarray, F_inner: np.ndarray, vn_inner: np.ndarray, h_m: float
) -> np.ndarray:
    """Acha um ponto provadamente DENTRO do lumen.

    Estrategia: pega vertices na regiao mediana do tubo (z proximo a centroide),
    desloca cada um ao longo de -normal por offset = max(0.3 mm, 2*h), testa
    inside. Retorna o primeiro que passar.
    """
    z_sorted = np.argsort(V_inner[:, 2])
    candidates_idx = z_sorted[len(z_sorted) // 4 : 3 * len(z_sorted) // 4]
    offset = max(3e-4, 2.0 * h_m)  # 0.3 mm ou 2h
    for idx in candidates_idx:
        pt = V_inner[idx] - offset * vn_inner[idx]
        if is_inside(pt, V_inner, F_inner):
            return pt
    # Fallback: tenta offsets menores
    for off_mm in (0.20, 0.10, 0.05):
        off = off_mm * 1e-3
        for idx in candidates_idx:
            pt = V_inner[idx] - off * vn_inner[idx]
            if is_inside(pt, V_inner, F_inner):
                return pt
    raise RuntimeError("Nao foi possivel achar ponto interior ao lumen.")


def find_annulus_point(
    V_outer: np.ndarray,
    F_outer: np.ndarray,
    V_inner: np.ndarray,
    F_inner: np.ndarray,
    vn_inner: np.ndarray,
    h_m: float,
) -> np.ndarray:
    """Acha um ponto DENTRO da parede anular (entre inner e outer)."""
    z_sorted = np.argsort(V_inner[:, 2])
    candidates_idx = z_sorted[len(z_sorted) // 4 : 3 * len(z_sorted) // 4]
    offset = 0.5 * h_m  # meio da espessura
    for idx in candidates_idx:
        pt = V_inner[idx] + offset * vn_inner[idx]
        if (not is_inside(pt, V_inner, F_inner)) and is_inside(pt, V_outer, F_outer):
            return pt
    raise RuntimeError("Nao foi possivel achar ponto interior ao annulus.")


def main() -> None:
    if not SRC_ARTERY.is_file():
        raise SystemExit(f"Missing source STL: {SRC_ARTERY}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outer_path = OUT_DIR / "artery_outer.stl"
    shutil.copyfile(SRC_ARTERY, outer_path)

    V, F = read_ascii_stl_facets(SRC_ARTERY)
    vol0 = mesh_volume_and_fix_winding(V, F)
    fn = face_normals_out(V, F)
    vn = vertex_normals(V, F, fn)
    h = H_MM * 1e-3
    V_inner = V - h * vn
    F_inner = F.copy()
    mesh_volume_and_fix_winding(V_inner, F_inner)
    inner_path = OUT_DIR / "artery_inner.stl"
    write_ascii_stl(inner_path, V_inner, F_inner, "artery_inner_surface")

    b_outer = np.stack([V.min(axis=0), V.max(axis=0)], axis=0)
    b_inner = np.stack([V_inner.min(axis=0), V_inner.max(axis=0)], axis=0)

    # locationInMesh validados por raycast em superficies fechadas.
    # Importante: a arteria e CURVA, entao centroide dos vertices cai FORA
    # do lumen — bug historico que produzia snappy meshando "tudo menos
    # arteria". Use vertice-deslocado + raycast.
    fn_inner = face_normals_out(V_inner, F_inner)
    vn_inner = vertex_normals(V_inner, F_inner, fn_inner)

    loc_fluid = find_lumen_point(V_inner, F_inner, vn_inner, h)
    loc_solid = find_annulus_point(V, F, V_inner, F_inner, vn_inner, h)

    # Validacao final
    assert is_inside(loc_fluid, V_inner, F_inner), "loc_fluid fora do lumen!"
    assert not is_inside(loc_solid, V_inner, F_inner), "loc_solid dentro do lumen!"
    assert is_inside(loc_solid, V, F), "loc_solid fora do annulus!"

    hints = {
        "wall_thickness_mm": H_MM,
        "solid_locationInMesh": loc_solid.tolist(),
        "fluid_locationInMesh": loc_fluid.tolist(),
        "z_end_back_m": float(b_outer[0, 2] - 0.0003),
        "z_end_front_m": float(b_outer[1, 2] + 0.0003),
        "bounds_outer_m": b_outer.tolist(),
        "bounds_inner_m": b_inner.tolist(),
        "signed_volume_outer_m3": vol0,
        "locationInMesh_validation": "raycast-verified inside lumen (fluid) / annulus (solid)",
    }
    (OUT_DIR.parent / "meshHints.json").write_text(json.dumps(hints, indent=2))

    summary = {
        "source_stl": str(SRC_ARTERY.relative_to(CASES)),
        "operation": "hollow_wall_offset_vertex_normals",
        "wall_thickness_m": h,
        "n_vertices": int(len(V)),
        "n_faces": int(len(F)),
        "outputs": {
            "artery_outer": str(outer_path.relative_to(CASES)),
            "artery_inner": str(inner_path.relative_to(CASES)),
        },
        "meshHints": str((OUT_DIR.parent / "meshHints.json").relative_to(CASES)),
    }
    (OUT_DIR / "_hollow_geometry_summary.json").write_text(
        json.dumps(summary, indent=2)
    )
    print(f"[ok] wrote {outer_path.relative_to(CASES)}")
    print(f"[ok] wrote {inner_path.relative_to(CASES)}")
    print(f"[ok] meshHints.json solid locationInMesh = {hints['solid_locationInMesh']}")
    print(f"[ok] meshHints.json fluid locationInMesh = {hints['fluid_locationInMesh']}")


if __name__ == "__main__":
    main()
