#!/usr/bin/env python3
"""
Extrai P_contact(t, x) da interface arteria-ONS no caso `cases/sugestao/`.

P_contact eh a pressao normal de contato exercida pelo solidContact MASTER
(arteria_externa) sobre o SLAVE (ons_outer). E o ingrediente principal que
queremos validar com este caso (objetivo cientifico primario).

Estrategia (FONTE DIRETA):
  - solids4Foam/solidContact escreve `normalTraction_<patch>` (volVectorField)
    em cada timestep. Eh a tracao normal de contato face-a-face no patch
    SLAVE, em Pa, ja calculada pelo solver (penalty * gap).
  - Modulo da tracao = P_contact local; sinal negativo na normal = compressao
    (contato real).
  - areaInContact_<patch> (volScalarField) marca quais faces estao em contato.

Saida:
  - sugestao_p_contact_summary.csv : por timestep (t, P_max, P_mean, A_contact)
  - sugestao_p_contact_per_face.csv: cada face com contato em cada timestep

Uso:
    python3 extract_p_contact_from_sugestao.py [--case CASE_DIR]
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


def read_polymesh_points(polymesh_dir: Path) -> np.ndarray:
    pts = []
    with (polymesh_dir / "points").open() as f:
        in_list = False
        for line in f:
            ls = line.strip()
            if not in_list:
                if ls.startswith("("):
                    in_list = True
                continue
            if ls.startswith(")"):
                break
            m = re.match(r"\(([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\)", ls)
            if m:
                pts.append([float(m.group(1)), float(m.group(2)), float(m.group(3))])
    return np.array(pts)


def read_polymesh_faces(polymesh_dir: Path) -> list[list[int]]:
    faces: list[list[int]] = []
    with (polymesh_dir / "faces").open() as f:
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
    return faces


def read_polymesh_boundary(polymesh_dir: Path) -> dict[str, tuple[int, int]]:
    bnd: dict[str, tuple[int, int]] = {}
    txt = (polymesh_dir / "boundary").read_text()
    pat = re.compile(
        r"(\w+)\s*\{[^{}]*?nFaces\s+(\d+)[^{}]*?startFace\s+(\d+)",
        re.DOTALL,
    )
    for m in pat.finditer(txt):
        bnd[m.group(1)] = (int(m.group(3)), int(m.group(2)))
    return bnd


def face_centres_and_areas(
    pts: np.ndarray, faces: list[list[int]], start: int, count: int,
) -> tuple[np.ndarray, np.ndarray]:
    cents = np.zeros((count, 3))
    areas = np.zeros(count)
    for i in range(count):
        face = faces[start + i]
        v = pts[face]
        c = v.mean(axis=0)
        cents[i] = c
        sf = np.zeros(3)
        for k in range(len(face)):
            a = v[k] - c
            b = v[(k + 1) % len(face)] - c
            sf += 0.5 * np.cross(a, b)
        areas[i] = np.linalg.norm(sf)
    return cents, areas


def parse_patch_field_vector(fpath: Path, patch: str, n_faces: int) -> np.ndarray:
    """Extrai o boundary patch <patch> de um volVectorField como (n_faces, 3).

    Trata `uniform (vx vy vz)` e `nonuniform List<vector> N (...)`."""
    arr = np.zeros((n_faces, 3))
    txt = fpath.read_text()
    # Encontra o bloco do patch
    pat_block = re.search(
        rf"\b{re.escape(patch)}\s*\{{(.*?)\}}", txt, re.DOTALL
    )
    if not pat_block:
        return arr
    block = pat_block.group(1)
    # uniform
    m_u = re.search(
        r"value\s+uniform\s*\(([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\)",
        block,
    )
    if m_u:
        v = np.array([float(m_u.group(i)) for i in (1, 2, 3)])
        arr[:] = v
        return arr
    # nonuniform
    m_n = re.search(
        r"value\s+nonuniform\s+List<vector>\s*(\d+)\s*\((.*?)\)\s*;",
        block, re.DOTALL,
    )
    if not m_n:
        return arr
    n_decl = int(m_n.group(1))
    if n_decl != n_faces:
        # ainda assim copiamos o que for possivel
        pass
    body = m_n.group(2)
    rows = re.findall(
        r"\(([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\)", body
    )
    for i, r in enumerate(rows[: n_faces]):
        arr[i] = [float(r[0]), float(r[1]), float(r[2])]
    return arr


def parse_patch_field_scalar(fpath: Path, patch: str, n_faces: int) -> np.ndarray:
    arr = np.zeros(n_faces)
    txt = fpath.read_text()
    pat_block = re.search(
        rf"\b{re.escape(patch)}\s*\{{(.*?)\}}", txt, re.DOTALL
    )
    if not pat_block:
        return arr
    block = pat_block.group(1)
    m_u = re.search(r"value\s+uniform\s+([-\d.eE+]+)", block)
    if m_u:
        arr[:] = float(m_u.group(1))
        return arr
    m_n = re.search(
        r"value\s+nonuniform\s+List<scalar>\s*(\d+)\s*\((.*?)\)\s*;",
        block, re.DOTALL,
    )
    if not m_n:
        return arr
    body = m_n.group(2)
    vals = [float(x) for x in body.split() if x.strip()]
    for i, v in enumerate(vals[: n_faces]):
        arr[i] = v
    return arr


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", default=None)
    ap.add_argument("--slave-patch", default="ons_outer")
    ap.add_argument("--threshold-pa", type=float, default=1.0,
                    help="pressao minima (Pa) para considerar face em contato. "
                         "default 1 Pa (apenas para excluir ruido numerico)")
    ap.add_argument("--out-csv-summary", default=None)
    ap.add_argument("--out-csv-faces", default=None)
    args = ap.parse_args()

    case = Path(args.case) if args.case else find_case_default()
    solid_dir = case / "solid"
    polymesh_dir = solid_dir / "constant" / "polyMesh"

    print(f"[p_contact] caso: {case}")
    pts = read_polymesh_points(polymesh_dir)
    faces = read_polymesh_faces(polymesh_dir)
    bnd = read_polymesh_boundary(polymesh_dir)

    if args.slave_patch not in bnd:
        print(f"ERROR: patch '{args.slave_patch}' nao existe.")
        sys.exit(1)
    start, count = bnd[args.slave_patch]
    cents_s, areas_s = face_centres_and_areas(pts, faces, start, count)
    print(f"[p_contact] patch slave='{args.slave_patch}' faces={count} "
          f"area_total={areas_s.sum()*1e6:.2f} mm^2")

    times = list_time_dirs(solid_dir)
    if not times:
        print("ERROR: nenhum timestep no solid/.")
        sys.exit(1)
    print(f"[p_contact] {len(times)} timesteps")

    summary_rows: list[tuple[float, float, float, float, float]] = []
    face_rows: list[tuple[float, int, float, float, float, float]] = []
    n_active_total = 0
    for t in times:
        time_dir = solid_dir / f"{t:g}"
        if not time_dir.exists():
            time_dir = solid_dir / str(t)
        nt_file = time_dir / f"normalTraction_{args.slave_patch}"
        ac_file = time_dir / f"areaInContact_{args.slave_patch}"
        if not nt_file.exists():
            continue
        nt = parse_patch_field_vector(nt_file, args.slave_patch, count)
        if ac_file.exists():
            ac = parse_patch_field_scalar(ac_file, args.slave_patch, count)
        else:
            ac = np.zeros(count)
        # P_contact = ||normalTraction|| (compressao positiva)
        p_face = np.linalg.norm(nt, axis=1)
        active = p_face > args.threshold_pa

        area_contact = float(areas_s[active].sum())
        if active.any():
            p_mean = float(np.average(p_face[active], weights=areas_s[active]))
            p_max = float(p_face[active].max())
            n_active_total += int(active.sum())
        else:
            p_mean = 0.0
            p_max = 0.0
        summary_rows.append((t, p_max, p_mean, area_contact, areas_s.sum()))

        for fi in range(count):
            if active[fi]:
                face_rows.append((
                    t, fi, cents_s[fi, 0], cents_s[fi, 1],
                    cents_s[fi, 2], p_face[fi]
                ))

        # Imprime so timesteps com contato
        if active.any():
            print(f"[p_contact]   t={t:.4f}  faces_ativas={int(active.sum())}/{count}  "
                  f"P_max={p_max:.1f} Pa  P_mean={p_mean:.1f} Pa  "
                  f"A_c={area_contact*1e6:.4f} mm^2")

    print(f"[p_contact] total face-events com contato: {n_active_total}")

    out_summary = Path(args.out_csv_summary) if args.out_csv_summary else (
        Path(__file__).resolve().parent / "sugestao_p_contact_summary.csv"
    )
    with out_summary.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t_s", "P_max_Pa", "P_mean_Pa",
                    "A_contact_m2", "A_patch_total_m2"])
        w.writerows(summary_rows)
    print(f"[p_contact] summary CSV: {out_summary}")

    out_faces = Path(args.out_csv_faces) if args.out_csv_faces else (
        Path(__file__).resolve().parent / "sugestao_p_contact_per_face.csv"
    )
    with out_faces.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t_s", "face_idx", "x_m", "y_m", "z_m", "P_Pa"])
        w.writerows(face_rows)
    print(f"[p_contact] per-face CSV: {out_faces} ({len(face_rows)} entradas)")


if __name__ == "__main__":
    main()
