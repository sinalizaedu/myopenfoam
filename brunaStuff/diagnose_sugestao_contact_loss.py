"""
Diagnostico: por que o contato desaparece no peak sistolico em sugestao?

Calcula, para cada timestep escrito:
  - posicao media e RMS da arteria_externa (centroide do bbox da parede)
  - posicao do face mais proximo do ONS (R_min vs Z-axis)
  - vetor de deslocamento medio em arteria_externa (decomposto em radial vs longitudinal)

Compara t=0.07 (contato firme) vs t=0.25 (sem contato).
"""
from __future__ import annotations
import re
from pathlib import Path

import numpy as np

CASE = Path("cases/sugestao/solid")
PMESH = CASE / "constant" / "polyMesh"


def read_points(pdir: Path) -> np.ndarray:
    txt = (pdir / "points").read_text()
    m = re.search(r"\(\s*((?:\([^)]+\)\s*)+)\)", txt, re.DOTALL)
    if not m:
        raise RuntimeError("nao achou points")
    body = m.group(1)
    vals = re.findall(
        r"\(([-+]?[0-9.eE+-]+)\s+([-+]?[0-9.eE+-]+)\s+([-+]?[0-9.eE+-]+)\)",
        body,
    )
    return np.array(vals, dtype=float)


def read_boundary(pdir: Path) -> dict:
    """Retorna dict[patchName] = (startFace, nFaces)."""
    txt = (pdir / "boundary").read_text()
    m = re.search(
        r"^\s*\d+\s*\(\s*(.*?)\s*\)\s*$",
        txt,
        re.DOTALL | re.MULTILINE,
    )
    if not m:
        raise RuntimeError("nao achou boundary list")
    body = m.group(1)
    out: dict[str, tuple[int, int]] = {}
    for pm in re.finditer(
        r"(\w+)\s*\{[^}]*?nFaces\s+(\d+)\s*;\s*startFace\s+(\d+)\s*;",
        body,
        re.DOTALL,
    ):
        out[pm.group(1)] = (int(pm.group(3)), int(pm.group(2)))
    return out


def read_faces(pdir: Path):
    txt = (pdir / "faces").read_text()
    rows = []
    for m in re.finditer(r"(\d+)\(\s*([\d\s]+)\)", txt):
        nv = int(m.group(1))
        ids = [int(x) for x in m.group(2).split()]
        if len(ids) == nv:
            rows.append(ids)
    return rows


def read_d_arteria_externa(time_dir: Path):
    """Retorna array (n_faces, 3) com traction da arteria_externa em D."""
    txt = (time_dir / "D").read_text()
    m = re.search(
        r"arteria_externa\s*\{[^}]*?value\s+nonuniform List<vector>\s+(\d+)\s*\((.*?)\)\s*;",
        txt,
        re.DOTALL,
    )
    if not m:
        return None
    body = m.group(2)
    vals = re.findall(
        r"\(([-+]?[0-9.eE+-]+)\s+([-+]?[0-9.eE+-]+)\s+([-+]?[0-9.eE+-]+)\)",
        body,
    )
    return np.array(vals, dtype=float)


def main() -> None:
    points = read_points(PMESH)
    bnd = read_boundary(PMESH)
    faces = read_faces(PMESH)
    s, n = bnd["arteria_externa"]
    ae_faces = faces[s : s + n]

    centroids = np.array(
        [points[ids].mean(axis=0) for ids in ae_faces],
        dtype=float,
    )
    r_init = np.hypot(centroids[:, 0], centroids[:, 1])
    R_ons = 2.5e-3

    print(f"arteria_externa: n_faces={n}, n_points unique aprox={n*4}")
    print(f"INICIAL  r_min={r_init.min()*1e3:.4f} mm  r_max={r_init.max()*1e3:.4f} mm")
    print(f"INICIAL  gap_min={(r_init.min()-R_ons)*1e6:.1f} um (centroide vs cyl ONS)")

    times = sorted(
        [p for p in CASE.iterdir() if p.is_dir() and re.match(r"0\.\d", p.name)],
        key=lambda p: float(p.name),
    )

    print(f"\n{'time(s)':>8s}  {'|D|max':>9s}  {'|D|mean':>9s}  {'D_rad_mean':>11s}  {'D_z_mean':>9s}  {'r_min_def':>11s}  {'gap_def':>9s}")
    print("-" * 95)
    for t in times:
        D_face = read_d_arteria_externa(t)
        if D_face is None or len(D_face) != n:
            continue
        magn = np.linalg.norm(D_face, axis=1)

        unit_r = centroids[:, :2] / np.maximum(r_init[:, None], 1e-12)
        D_rad = D_face[:, 0] * unit_r[:, 0] + D_face[:, 1] * unit_r[:, 1]
        D_z = D_face[:, 2]

        deformed = centroids + D_face
        r_def = np.hypot(deformed[:, 0], deformed[:, 1])
        gap_def_min_um = (r_def.min() - R_ons) * 1e6

        print(
            f"{t.name:>8s}  "
            f"{magn.max()*1e6:>9.2f}  "
            f"{magn.mean()*1e6:>9.2f}  "
            f"{D_rad.mean()*1e6:>11.2f}  "
            f"{D_z.mean()*1e6:>9.2f}  "
            f"{r_def.min()*1e3:>11.4f}  "
            f"{gap_def_min_um:>9.1f}"
        )

    print("\nUnidades: |D| em um. r_min em mm. gap em um (positivo=fora do cyl ONS).")


if __name__ == "__main__":
    main()
