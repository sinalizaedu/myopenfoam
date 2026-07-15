#!/usr/bin/env python3
"""Gera a malha CalculiX (.inp) do on-caso-1.2 CONVERTENDO o blockMesh redondo
do on-caso-1 (O-grid, nucleo central solido, 32 divisoes tangenciais).

Substitui o gerador analitico antigo (gen_on_caso_1_2_ccx_inp.py), que produzia
uma malha anelar OCTOGONAL com furo central. Aqui a malha do solido e' a MESMA
do on-caso-1 (mesmo polyMesh), garantindo:
  - secao CIRCULAR (arestas `arc` do blockMesh seguem o raio real)
  - nucleo neural (`on`) SOLIDO, em contato continuo com o resto da estrutura
  - mesmas 7 zonas (on, pia, dura, lc, sclera_peri, sclera_ring, globo)
  - mesmos patches (posterior_*, fsi_*, dura_outer, contact_local, globo_outer...)

Reutiliza as rotinas de parsing/reconstrucao de foam_polymesh_to_ccx_inp.py.

Nomenclatura (compativel com o main.inp + adapter ccx_preCICE v2.20.1):
  - NSETs   : N<patch>   (ex.: Nfsi_pia, Nposterior_on, Ndura_outer)
  - SURFACEs: S<patch>   (ex.: Scontact_local, Sfsi_sclera_peri)
  - ELSETs  : EALL_<ZONA> (ex.: EALL_ON, EALL_DURA)
  - Nfsi_all: uniao de Nfsi_pia + Nfsi_dura (placeholder *CLOAD do adapter)

Saidas (em cases/on-caso-1.2/solid/):
  all.msh     -> *NODE (NALL) + *ELEMENT por zona
  all.nam     -> *NSET por patch + *SURFACE dos patches carregados + Nfsi_all
  winkler.inp -> SPRINGA radiais p/ ghost fixo em dura_outer (k=2e5 Pa/m)

Uso:
    python3 brunaStuff/gen_on_caso_1_2_from_blockmesh.py
Pre-requisito: cases/on-caso-1/solid/constant/polyMesh deve existir
(gerado por blockMesh+topoSet+createPatch no on-caso-1).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

# Reaproveita o parser/reconstrutor do conversor generico.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import foam_polymesh_to_ccx_inp as fp  # noqa: E402

# ---------------------------------------------------------------------------
# Configuracao
# ---------------------------------------------------------------------------

REPO = Path(__file__).resolve().parent.parent
POLYMESH = REPO / "cases" / "on-caso-1" / "solid" / "constant" / "polyMesh"
OUT_DIR = REPO / "cases" / "on-caso-1.2" / "solid"

ELEMENT_TYPE = "C3D8"     # igual ao deck FSI ja' validado (nu=0.45 Neo-Hooke)
K_WINKLER = 2.0e5         # Pa/m (gordura orbital), igual ao on-caso-1

# Patches que recebem *SURFACE (para *DLOAD de pressao no main.inp).
SURFACE_PATCHES = ("contact_local", "fsi_sclera_peri", "fsi_sclera_ring")


# ---------------------------------------------------------------------------
# Helpers de escrita
# ---------------------------------------------------------------------------

def nodes_of_faces(face_indices, faces) -> list[int]:
    verts: set[int] = set()
    for f in face_indices:
        verts.update(faces[f])
    return sorted(verts)


def render_nset(name: str, node_ids_0based: list[int]) -> str:
    lines = [f"*NSET, NSET={name}"]
    for i in range(0, len(node_ids_0based), 8):
        chunk = node_ids_0based[i:i + 8]
        lines.append(", ".join(f"{v + 1}" for v in chunk))  # CCX e' 1-based
    return "\n".join(lines)


def render_surface(name: str, face_indices, faces, owner, conn) -> str:
    lines = [f"*SURFACE, NAME={name}, TYPE=ELEMENT"]
    for f in face_indices:
        c = int(owner[f])
        loc = fp.find_face_in_hex(set(faces[f]), conn[c])
        if loc is None:
            raise ValueError(f"face {f} (cell {c}) nao casou com face local CCX")
        lines.append(f"{c + 1}, S{loc}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if not (POLYMESH / "points").exists():
        raise SystemExit(
            f"polyMesh nao encontrado em {POLYMESH}.\n"
            "Gere primeiro o solido do on-caso-1 (blockMesh + topoSet + createPatch)."
        )

    print(f"[1/4] Lendo polyMesh redondo do on-caso-1: {POLYMESH}")
    points = fp.parse_points(POLYMESH / "points")
    faces = fp.parse_faces(POLYMESH / "faces")
    owner = fp.parse_label_list(POLYMESH / "owner")
    neighbour = fp.parse_label_list(POLYMESH / "neighbour")
    boundary = fp.parse_boundary(POLYMESH / "boundary")
    cell_zones = fp.parse_cell_zones(POLYMESH / "cellZones")
    n_cells = int(owner.max()) + 1
    print(f"      nodes={len(points)}, cells={n_cells}, "
          f"patches={len(boundary)}, zones={list(cell_zones.keys())}")

    print(f"[2/4] Reconstruindo conectividade {ELEMENT_TYPE} ({n_cells} celulas)")
    conn, _ = fp.reconstruct_hex_connectivity(points, faces, owner, neighbour, n_cells)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ---- all.msh: NODE + ELEMENT por zona (ELSET=EALL_<ZONA>) ----
    print(f"[3/4] Escrevendo all.msh / all.nam / winkler.inp em {OUT_DIR}")
    msh_lines = [
        "** Mesh on-caso-1.2 (CONVERTIDA do blockMesh redondo do on-caso-1)",
        "** Gerada por gen_on_caso_1_2_from_blockmesh.py.",
        "** 7 zonas: on, pia, dura, lc, sclera_peri, sclera_ring, globo.",
        "** Seccao circular (O-grid) com nucleo neural solido.",
        "**",
        "*NODE, NSET=NALL",
    ]
    for i, (x, y, z) in enumerate(points, start=1):
        msh_lines.append(f"{i}, {x:.10e}, {y:.10e}, {z:.10e}")
    for zname, zcells in cell_zones.items():
        msh_lines.append(f"** ---- Zona '{zname}': {len(zcells)} hexaedros ----")
        msh_lines.append(f"*ELEMENT, TYPE={ELEMENT_TYPE}, ELSET=EALL_{zname.upper()}")
        for c in zcells:
            v = conn[int(c)] + 1
            msh_lines.append(
                f"{int(c) + 1}, {v[0]}, {v[1]}, {v[2]}, {v[3]}, "
                f"{v[4]}, {v[5]}, {v[6]}, {v[7]}"
            )
    (OUT_DIR / "all.msh").write_text("\n".join(msh_lines) + "\n")

    # ---- all.nam: NSETs por patch + SURFACEs carregadas + Nfsi_all ----
    nam_lines = [
        "** NSETs e SURFACEs on-caso-1.2 (gerado por gen_on_caso_1_2_from_blockmesh.py)",
        "** NSET = N<patch>, SURFACE = S<patch>. Adapter ccx_preCICE le Nfsi_pia/Nfsi_dura.",
        "**",
    ]
    patch_faces: dict[str, list[int]] = {}
    for pname, (start, n) in boundary.items():
        patch_faces[pname] = list(range(start, start + n))

    for pname, fidx in patch_faces.items():
        nam_lines.append(render_nset(f"N{pname}", nodes_of_faces(fidx, faces)))
        nam_lines.append("**")

    # Nfsi_all = uniao plana de fsi_pia + fsi_dura (placeholder *CLOAD do adapter)
    fsi_all_nodes = nodes_of_faces(
        patch_faces.get("fsi_pia", []) + patch_faces.get("fsi_dura", []), faces)
    nam_lines.append(render_nset("Nfsi_all", fsi_all_nodes))
    nam_lines.append("**")

    # SURFACEs para *DLOAD (contato arterial + pressao estatica da esclera)
    for pname in SURFACE_PATCHES:
        if pname in patch_faces:
            nam_lines.append(
                render_surface(f"S{pname}", patch_faces[pname], faces, owner, conn))
            nam_lines.append("**")

    (OUT_DIR / "all.nam").write_text("\n".join(nam_lines) + "\n")

    # ---- winkler.inp: SPRINGA radiais em dura_outer ----
    dura_start, dura_n = boundary["dura_outer"]
    dura_faces = list(range(dura_start, dura_start + dura_n))
    fp.write_winkler_inp(
        out_path=OUT_DIR / "winkler.inp",
        dura_outer_face_indices=dura_faces,
        perturbation_face_indices=[],
        faces=faces,
        points=points,
        n_existing_nodes=len(points),
        n_existing_elements=n_cells,
        k_winkler=K_WINKLER,
    )

    # ---- Stats ----
    n_wink = len(nodes_of_faces(dura_faces, faces))
    print(f"[4/4] Concluido.")
    print(f"      {len(points)} nodes, {n_cells} hex {ELEMENT_TYPE}")
    for zname, zcells in cell_zones.items():
        print(f"        EALL_{zname.upper():12s}: {len(zcells):5d} elementos")
    print(f"      Nfsi_all: {len(fsi_all_nodes)} nodes")
    print(f"      Winkler : {n_wink} SPRINGA em dura_outer (k={K_WINKLER:.1e} Pa/m)")
    print(f"      SURFACEs: {', '.join('S' + p for p in SURFACE_PATCHES if p in patch_faces)}")


if __name__ == "__main__":
    main()
