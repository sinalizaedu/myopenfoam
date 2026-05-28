#!/usr/bin/env python3
"""Verifica se um ponto candidato esta dentro do lumen (raycast)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
CASE = REPO / "cases" / "artoph-fsi-curva-mestrado"


def read_stl_facets(path: Path) -> tuple[np.ndarray, np.ndarray]:
    verts: list[tuple[float, float, float]] = []
    faces: list[list[int]] = []
    key_to_idx: dict[tuple[float, float, float], int] = {}

    def add(p: tuple[float, float, float]) -> int:
        k = (round(p[0], 9), round(p[1], 9), round(p[2], 9))
        if k in key_to_idx:
            return key_to_idx[k]
        i = len(verts)
        verts.append(p)
        key_to_idx[k] = i
        return i

    buf: list[tuple[float, float, float]] = []
    with path.open() as f:
        for line in f:
            ls = line.strip()
            if ls.startswith("vertex"):
                parts = ls.split()
                buf.append((float(parts[1]), float(parts[2]), float(parts[3])))
                if len(buf) == 3:
                    faces.append([add(buf[0]), add(buf[1]), add(buf[2])])
                    buf.clear()
    return np.array(verts), np.array(faces)


def ray_triangle_intersect(
    origin: np.ndarray, direction: np.ndarray, V: np.ndarray, F: np.ndarray
) -> int:
    """Conta numero de triangulos cruzados por raio (origin -> +inf*direction).
    Mollerâ€“Trumbore."""
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
    """Ray casting: hits impar => dentro."""
    direction = np.array([1.0, 0.337, 0.781])
    direction /= np.linalg.norm(direction)
    n = ray_triangle_intersect(point, direction, V, F)
    return n % 2 == 1


def main() -> None:
    inner = CASE / "constant" / "triSurface" / "artery_inner.stl"
    outer = CASE / "constant" / "triSurface" / "artery_outer.stl"
    V_in, F_in = read_stl_facets(inner)
    V_out, F_out = read_stl_facets(outer)

    candidates: dict[str, np.ndarray] = {}

    # 1) Atual fluid_locationInMesh
    meshhints = json.loads((CASE / "constant" / "meshHints.json").read_text())
    candidates["meshHints.fluid_locationInMesh"] = np.array(meshhints["fluid_locationInMesh"])
    candidates["meshHints.solid_locationInMesh"] = np.array(meshhints["solid_locationInMesh"])

    # 2) artoph-curva-mestrado/_artery_scaled_summary.json
    summary = json.loads(
        (REPO / "cases" / "artoph-curva-mestrado" / "solid" / "constant" / "triSurface"
         / "_artery_scaled_summary.json").read_text()
    )
    candidates["scaled_summary.locationInMesh_m"] = np.array(summary["locationInMesh_m"])

    # 3) Vertice de V_in deslocado para o lumen (- normal vai pra dentro do lumen, normais apontam pra fora)
    fn = np.zeros((len(F_in), 3))
    for fi, (i0, i1, i2) in enumerate(F_in):
        p0, p1, p2 = V_in[i0], V_in[i1], V_in[i2]
        c = np.cross(p1 - p0, p2 - p0)
        n = np.linalg.norm(c)
        fn[fi] = c / n if n > 1e-30 else np.array([0, 0, 1.0])
    # vertex normals
    vn = np.zeros_like(V_in)
    cnt = np.zeros(len(V_in))
    for fi, (i0, i1, i2) in enumerate(F_in):
        for j in (i0, i1, i2):
            vn[j] += fn[fi]
            cnt[j] += 1
    vn /= np.maximum(cnt[:, None], 1)
    vn /= np.maximum(np.linalg.norm(vn, axis=1, keepdims=True), 1e-30)
    # Pega vertice no meio do tubo (índice mediano em z)
    z_med_idx = np.argsort(V_in[:, 2])[len(V_in) // 2]
    v_mid = V_in[z_med_idx]
    n_mid = vn[z_med_idx]
    # Move ao longo de -normal por 0.3 mm (interior do lumen, raio ~0.55 mm)
    candidates["vertex_minus_normal_300um"] = v_mid - 3e-4 * n_mid
    # Para o anular (parede): vertice + normal * h/2 (= 0.1 mm para fora)
    candidates["vertex_plus_normal_100um (annulus)"] = v_mid + 1e-4 * n_mid

    print(f"{'candidato':50s} | {'pt (mm)':40s} | dentro_inner | dentro_outer | classificacao")
    print("-" * 140)
    for name, pt in candidates.items():
        in_inner = is_inside(pt, V_in, F_in)
        in_outer = is_inside(pt, V_out, F_out)
        classif = (
            "LUMEN" if in_inner and in_outer
            else "PAREDE (annulus)" if (not in_inner) and in_outer
            else "EXTERIOR" if (not in_inner) and (not in_outer)
            else "??? (impossivel)"
        )
        pt_mm = pt * 1e3
        print(f"{name:50s} | ({pt_mm[0]:7.3f}, {pt_mm[1]:7.3f}, {pt_mm[2]:7.3f}) | "
              f"{'SIM' if in_inner else 'nao':12s} | "
              f"{'SIM' if in_outer else 'nao':12s} | {classif}")


if __name__ == "__main__":
    main()
