#!/usr/bin/env python3
"""
Força × deslocamento normal na patch de contato pulsátil (on-mestrado).

Detecta automaticamente a patch com pressureSeries em 0/D (ex.: contact_local
ou contact_artoph) e lê nFaces/startFace em constant/polyMesh/boundary.

- Força: |F| = p(t) * ||Σ S_f||  (pressão uniforme na patch em cada instante).

- Deslocamento: média ponderada por área de D·n̂ em cada face da patch.

Saída: PNG + CSV em brunaStuff/.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
CASE = REPO / "cases" / "on-mestrado" / "solid"
MESH = CASE / "constant" / "polyMesh"
PRESSURE_TABLE = CASE / "constant" / "contact_pressure.dat"
OUT_DIR = Path(__file__).resolve().parent


def read_points(path: Path) -> np.ndarray:
    text = path.read_text()
    m = re.search(r"(\d+)\s*\(\s*", text)
    n = int(m.group(1))
    vecs = re.findall(r"\(([^)]+)\)", text[m.end() - 1 :])
    pts = []
    for s in vecs[:n]:
        pts.append([float(x) for x in s.split()])
    return np.array(pts, dtype=float)


def read_faces(path: Path) -> list[list[int]]:
    out: list[list[int]] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line.startswith("4("):
            continue
        inner = line[2:-1]
        parts = inner.split()
        out.append([int(x) for x in parts])
    return out


def quad_area_vector(p: np.ndarray, ids: list[int]) -> np.ndarray:
    a, b, c, d = (p[i] for i in ids)
    return 0.5 * np.cross(b - a, c - a) + 0.5 * np.cross(c - a, d - a)


def parse_pressure_table(path: Path) -> tuple[np.ndarray, np.ndarray]:
    times: list[float] = []
    pressures: list[float] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith("(") and line.endswith(")"):
            inner = line[1:-1].split()
            if len(inner) == 2:
                try:
                    times.append(float(inner[0]))
                    pressures.append(float(inner[1]))
                except ValueError:
                    pass
    return np.array(times), np.array(pressures)


def pressure_at(t: float, tp: np.ndarray, pp: np.ndarray) -> float:
    return float(np.interp(t, tp, pp, left=pp[0], right=pp[-1]))


def read_boundary_patch_sizes(boundary_path: Path) -> dict[str, tuple[int, int]]:
    """patch_name -> (nFaces, startFace) como no boundary."""
    text = boundary_path.read_text()
    patches: dict[str, tuple[int, int]] = {}
    i = 0
    lines = text.splitlines()
    while i < len(lines):
        m = re.match(r"^\s{4}([a-zA-Z0-9_]+)\s*$", lines[i])
        if m and i + 1 < len(lines) and lines[i + 1].strip() == "{":
            name = m.group(1)
            depth = 1
            j = i + 2
            chunk: list[str] = []
            while j < len(lines) and depth > 0:
                depth += lines[j].count("{") - lines[j].count("}")
                chunk.append(lines[j])
                j += 1
            block = "\n".join(chunk)
            mf = re.search(r"nFaces\s+(\d+)\s*;", block)
            ms = re.search(r"startFace\s+(\d+)\s*;", block)
            if mf and ms:
                patches[name] = (int(mf.group(1)), int(ms.group(1)))
            i = j
            continue
        i += 1
    return patches


def detect_pressure_patch_name(d0: Path) -> str:
    """Nome da boundary patch que usa pressureSeries (carga pulsátil)."""
    lines = d0.read_text().splitlines()
    for i, line in enumerate(lines):
        if "pressureSeries" not in line:
            continue
        for j in range(i, max(-1, i - 25), -1):
            mj = re.match(r"^\s{4}([a-zA-Z0-9_]+)\s*$", lines[j])
            if mj and j + 1 < len(lines) and lines[j + 1].strip() == "{":
                return mj.group(1)
    raise RuntimeError(f"{d0}: não achei nenhuma patch com pressureSeries")


def patch_body_lines(lines: list[str], patch_name: str) -> list[str]:
    for i, line in enumerate(lines):
        if line.strip() != patch_name:
            continue
        if i + 1 >= len(lines) or lines[i + 1].strip() != "{":
            continue
        depth = 1
        body: list[str] = []
        k = i + 2
        while k < len(lines) and depth > 0:
            depth += lines[k].count("{") - lines[k].count("}")
            body.append(lines[k])
            k += 1
        return body[:-1] if body and body[-1].strip() == "}" else body
    raise RuntimeError(f"patch {patch_name!r} não encontrada no arquivo")


def _vectors_from_paren_groups(s: str) -> list[tuple[float, float, float]]:
    out: list[tuple[float, float, float]] = []
    for m in re.finditer(r"\(\s*([-\d.eE+\s]+)\s*\)", s):
        parts = m.group(1).split()
        if len(parts) == 3:
            out.append(tuple(map(float, parts)))
    return out


def extract_patch_value_vectors(d_path: Path, patch_name: str, n_expect: int) -> list[tuple[float, float, float]]:
    """Campo D / boundaryField / patch / value (uniform ou nonuniform)."""
    lines = d_path.read_text().splitlines()
    body = patch_body_lines(lines, patch_name)
    block = "\n".join(body)

    mu = re.search(
        r"value\s+uniform\s*\(\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s*\)",
        block,
    )
    if mu:
        u = tuple(map(float, mu.groups()))
        return [u] * n_expect

    # Formato compacto OpenFOAM: value  nonuniform List<vector> N((v1)(v2)...));
    mi2 = re.search(
        r"value\s+nonuniform\s+List<vector>\s+(\d+)\s*\(\((.*)\)\)\s*;",
        block,
        re.DOTALL,
    )
    if mi2:
        n = int(mi2.group(1))
        inner = mi2.group(2)
        buf = _vectors_from_paren_groups(inner)
        if len(buf) == n and n == n_expect:
            return buf

    mstart = re.search(r"value\s+nonuniform\s+List<vector>\s*$", block, re.MULTILINE)
    if not mstart:
        mstart = re.search(r"value\s+nonuniform\s+List<vector>\s*\n", block, re.MULTILINE)
    if mstart:
        rest = block[mstart.end() :]
        lines_r = rest.strip().splitlines()
        if not lines_r:
            raise RuntimeError(f"{d_path}: List<vector> multilinha vazia")
        count_line = 0
        while count_line < len(lines_r) and not lines_r[count_line].strip().isdigit():
            count_line += 1
        if count_line >= len(lines_r):
            raise RuntimeError(f"{d_path}: sem contagem após nonuniform List<vector>")
        n = int(lines_r[count_line].strip())
        joined = "\n".join(lines_r[count_line + 1 :])
        p0 = joined.find("(")
        p1 = joined.rfind(")")
        if p0 == -1 or p1 == -1:
            raise RuntimeError(f"{d_path}: lista de vetores sem parênteses")
        inner = joined[p0 : p1 + 1]
        buf = _vectors_from_paren_groups(inner)
        if len(buf) != n_expect or n != n_expect:
            raise RuntimeError(
                f"{d_path}: patch {patch_name}: esperado {n_expect} vetores (header n={n}), obtido {len(buf)}"
            )
        return buf

    raise RuntimeError(f"{d_path}: patch {patch_name}: campo value não reconhecido")


def main() -> int:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Instale matplotlib: pip install matplotlib", file=sys.stderr)
        return 1

    d0 = CASE / "0" / "D"
    if not d0.is_file():
        print(f"Falta {d0}", file=sys.stderr)
        return 1

    patch_name = detect_pressure_patch_name(d0)
    bpath = MESH / "boundary"
    patch_sizes = read_boundary_patch_sizes(bpath)
    if patch_name not in patch_sizes:
        raise RuntimeError(f"Patch {patch_name!r} não está em {bpath}")
    n_faces, start_face = patch_sizes[patch_name]

    points = read_points(MESH / "points")
    faces = read_faces(MESH / "faces")

    tp, pp = parse_pressure_table(PRESSURE_TABLE)

    s_sum = np.zeros(3)
    areas: list[float] = []
    normals: list[np.ndarray] = []
    for fi in range(start_face, start_face + n_faces):
        svec = quad_area_vector(points, faces[fi])
        a = float(np.linalg.norm(svec))
        areas.append(a)
        if a > 1e-30:
            normals.append(svec / a)
        else:
            normals.append(np.array([1.0, 0.0, 0.0]))
        s_sum += svec

    areas_np = np.array(areas)
    normals_np = np.stack(normals)
    s_sum_norm = float(np.linalg.norm(s_sum))

    time_dirs = sorted(
        [p for p in CASE.iterdir() if p.is_dir() and p.name.replace(".", "", 1).isdigit() and (p / "D").is_file()],
        key=lambda p: float(p.name),
    )

    rows: list[tuple[float, float, float, float]] = []
    for tdir in time_dirs:
        t = float(tdir.name)
        p = pressure_at(t, tp, pp)
        dvecs = np.array(extract_patch_value_vectors(tdir / "D", patch_name, n_faces), dtype=float)
        u_n = float(np.sum(areas_np[:, None] * np.sum(dvecs * normals_np, axis=1)) / np.sum(areas_np))
        f_mag = p * s_sum_norm
        rows.append((t, p, f_mag, u_n))

    csv_path = OUT_DIR / "on_mestrado_contact_force_vs_disp_normal.csv"
    with csv_path.open("w", encoding="utf-8") as f:
        f.write("time_s,pressure_Pa,force_resultant_N,u_normal_m\n")
        for r in rows:
            f.write(f"{r[0]:.8g},{r[1]:.8g},{r[2]:.8g},{r[3]:.8g}\n")

    u_arr = np.array([r[3] for r in rows])
    f_arr = np.array([r[2] for r in rows])

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(u_arr * 1e6, f_arr, "o-", ms=3, lw=1.0, color="steelblue")
    ax.set_xlabel(r"Deslocamento normal médio na patch (µm)")
    ax.set_ylabel(r"Força resultante da pressão $|p\,\sum \vec{S}_f|$ (N)")
    ax.set_title(f"on-mestrado — {patch_name}: força × deslocamento normal")
    ax.grid(True, alpha=0.35)
    fig.tight_layout()
    png_path = OUT_DIR / "on_mestrado_contact_force_vs_disp_normal.png"
    fig.savefig(png_path, dpi=150)
    plt.close(fig)

    print(f"Patch de carga: {patch_name}  (nFaces={n_faces}, startFace={start_face})")
    print(f"CSV:  {csv_path}")
    print(f"PNG:  {png_path}")
    print(f"||ΣS_f|| na patch = {s_sum_norm:.6e} m²")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
