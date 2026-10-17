#!/usr/bin/env python3
"""
convert_gmsh_to_ccx.py
----------------------
Converte malha Gmsh 2.2 do olho anatômico Lamminsalo (.msh)
para formato CalculiX (.inp).

Entrada:  eye_g2_solid_lamminsalo_M1.msh  (hex8 + quad4, coat-only)
Saída:    eye_anatomical.inp  (mesh only: nodes, elements, sets, surfaces)

Uso dentro do Docker:
    docker compose run --rm fsi bash -lc \
      'pip install numpy --break-system-packages && \
       cd /simulation/<PASTA>/scripts && python3 convert_gmsh_to_ccx.py'

Referências:
    Geometria: Lamminsalo et al. 2018, Pharm Res (ESM Tables SI-SII),
               baseado em Missel 2012.
    Formato Gmsh 2.2: https://gmsh.info/doc/texinfo/gmsh.html#MSH-file-format
    Faces C3D8 CalculiX: CCX documentation, section *SURFACE
"""

import sys
import os
import json
import shutil
import subprocess
import tempfile
import itertools
from pathlib import Path
from collections import defaultdict
import numpy as np

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
# Caminhos relativos ao Docker (/simulation/ = raiz do repo cases/)
MESH_DIR = Path("../../doc-g3-sim1/geometry")
MESH_FILE = MESH_DIR / "eye_g2_solid_lamminsalo_M1.msh"
OUTPUT_FILE = Path("../mesh") / "eye_anatomical.inp"

# Mapeamento Physical Group ID -> nome (definido no .msh)
VOLUME_GROUPS = {1: "CORNEA", 2: "SCLERA", 3: "CHOROID", 4: "RETINA"}
SURFACE_GROUPS = {
    5: "FSI_ACTIVE",
    6: "FSI_IRIS",
    7: "FSI_LENS",
    8: "OUTER",
    9: "SYMMETRY_0",
    10: "SYMMETRY_90",
}

# Faces do C3D8 no CalculiX (1-indexed, ordem CCX)
# S1: 1,2,3,4   S2: 5,8,7,6   S3: 1,5,6,2
# S4: 2,6,7,3   S5: 3,7,8,4   S6: 4,8,5,1
C3D8_FACES = {
    "S1": (0, 1, 2, 3),      # node indices 0-based
    "S2": (4, 7, 6, 5),
    "S3": (0, 4, 5, 1),
    "S4": (1, 5, 6, 2),
    "S5": (2, 6, 7, 3),
    "S6": (3, 7, 4, 0),
}

# Gmsh hex8 (type 5) node order differs from CalculiX C3D8; try these
# local renumberings until the element Jacobian is positive (CCX convention).
# Gmsh hex8 type 5 -> intermediate winding (Lamminsalo M1)
_GMSH_TO_CCX_PERM = (1, 0, 3, 2, 5, 4, 7, 6)
# Second pass: CCX 2.20 rejects some Jacobians that pass a volume test alone
# (checked on element 1 with ccx_preCICE, one_elem.inp, 2026-10-02)
_CCX_JACOBIAN_FIX_PERM = (3, 2, 1, 0, 7, 6, 5, 4)
# Some M1 hexes need a local face swap before the two-step map (CCX 2.20 probe)
_RAW_PRE_PERMUTATIONS = (
    (0, 1, 2, 3, 4, 5, 6, 7),
    (0, 1, 2, 4, 3, 5, 6, 7),
)


def _ccx_executable() -> str | None:
    for name in ("ccx_preCICE", "ccx", "ccx_2.23"):
        p = shutil.which(name)
        if p:
            return p
    for p in ("/opt/calculix/bin/ccx_preCICE",):
        if Path(p).is_file():
            return p
    return None


def _pipeline_gmsh_nodes(enodes, pre_perm):
    en = [enodes[i] for i in pre_perm]
    en = [en[i] for i in _GMSH_TO_CCX_PERM]
    return [en[i] for i in _CCX_JACOBIAN_FIX_PERM]


def _ccx_positive_jacobian(enodes8, nodes, ccx_exe: str, work: Path) -> bool:
    """True if CCX accepts the 8-node C3D8I (elastic smoke step)."""
    lines = ["*NODE"]
    for nid in enodes8:
        x, y, z = nodes[nid]
        lines.append(f"{nid:8d}, {x:16.9f}, {y:16.9f}, {z:16.9f}")
    lines.append("*ELEMENT, TYPE=C3D8I, ELSET=E1")
    lines.append("1, " + ", ".join(str(n) for n in enodes8))
    lines += [
        "*MATERIAL, NAME=M",
        "*ELASTIC",
        "1e6, 0.3",
        "*SOLID SECTION, ELSET=E1, MATERIAL=M",
        "*STEP",
        "*STATIC",
        "1",
        "*END STEP",
    ]
    deck = work / "probe.inp"
    deck.write_text("\n".join(lines) + "\n")
    for ext in (".frd", ".sta", ".cvg", ".12d"):
        p = work / f"probe{ext}"
        if p.exists():
            p.unlink()
    result = subprocess.run(
        [ccx_exe, "-i", "probe"],
        cwd=work,
        capture_output=True,
        text=True,
        timeout=30,
    )
    out = result.stdout + result.stderr
    return result.returncode == 0 and "Job finished" in out and "nonpositive jacobian" not in out


def _hex_signed_volume(coords8) -> float:
    """Signed volume for CCX/VTK C3D8 node order."""
    n = np.asarray(coords8, dtype=float)

    def vol(a, b, c, d):
        return float(np.dot(a - d, np.cross(b - d, c - d)) / 6.0)

    total = 0.0
    for tet in ((0, 1, 3, 4), (1, 2, 3, 4), (1, 2, 5, 4), (2, 5, 6, 4), (2, 6, 7, 4), (2, 7, 3, 4)):
        total += vol(n[tet[0]], n[tet[1]], n[tet[2]], n[tet[3]])
    return total


def orient_hex_elements(hex_elements, nodes, quad_elements):
    """Return hex list with node IDs permuted to CalculiX C3D8 winding."""
    del quad_elements  # surface matching uses oriented connectivity + CCX faces
    ccx_exe = _ccx_executable()
    work = Path(tempfile.mkdtemp(prefix="ccx_orient_")) if ccx_exe else None
    oriented = []
    n_alt = 0
    for eid, et, phys, enodes in hex_elements:
        chosen = None
        for pre in _RAW_PRE_PERMUTATIONS:
            candidate = _pipeline_gmsh_nodes(enodes, pre)
            if ccx_exe and work:
                if _ccx_positive_jacobian(candidate, nodes, ccx_exe, work):
                    chosen = candidate
                    if pre != _RAW_PRE_PERMUTATIONS[0]:
                        n_alt += 1
                    break
            elif pre == _RAW_PRE_PERMUTATIONS[0]:
                chosen = candidate
                break
        if chosen is None and ccx_exe and work:
            for perm in itertools.permutations(range(8)):
                candidate = [enodes[i] for i in perm]
                candidate = [candidate[i] for i in _GMSH_TO_CCX_PERM]
                candidate = [candidate[i] for i in _CCX_JACOBIAN_FIX_PERM]
                if _ccx_positive_jacobian(candidate, nodes, ccx_exe, work):
                    chosen = candidate
                    n_alt += 1
                    break
        if chosen is None:
            raise RuntimeError(
                f"Hex {eid}: no CCX-valid orientation (run converter inside Docker)"
            )
        oriented.append((eid, et, phys, chosen))
    if work and work.exists():
        shutil.rmtree(work, ignore_errors=True)
    if ccx_exe:
        print(f"  CCX Jacobian probe: {len(hex_elements)} elements ({n_alt} alt pre-perm)")
    else:
        print("  AVISO: ccx nao encontrado — orientacao sem probe (use Docker)")
    return oriented


# ---------------------------------------------------------------------------
# PARSER Gmsh 2.2
# ---------------------------------------------------------------------------
def parse_gmsh22(filepath):
    """Parse Gmsh 2.2 ASCII mesh file.

    Returns
    -------
    nodes : dict {node_id: (x, y, z)}
    elements : list of (elem_id, gmsh_type, phys_group, [node_ids])
    phys_names : dict {(dim, tag): name}
    """
    nodes = {}
    elements = []
    phys_names = {}

    with open(filepath) as f:
        section = None
        for line in f:
            line = line.strip()
            if line.startswith("$"):
                if line.startswith("$End"):
                    section = None
                else:
                    section = line[1:]
                    if section in ("Nodes", "Elements", "PhysicalNames"):
                        next_line = next(f).strip()  # count line
                        if section == "PhysicalNames":
                            n = int(next_line)
                            for _ in range(n):
                                parts = next(f).strip().split()
                                dim = int(parts[0])
                                tag = int(parts[1])
                                name = parts[2].strip('"')
                                phys_names[(dim, tag)] = name
                            section = None
                continue

            if section == "Nodes":
                parts = line.split()
                nid = int(parts[0])
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                nodes[nid] = (x, y, z)

            elif section == "Elements":
                parts = line.split()
                eid = int(parts[0])
                etype = int(parts[1])
                ntags = int(parts[2])
                phys = int(parts[3]) if ntags >= 1 else 0
                enodes = [int(p) for p in parts[3 + ntags:]]
                elements.append((eid, etype, phys, enodes))

    return nodes, elements, phys_names


# ---------------------------------------------------------------------------
# FACE MATCHING: quad4 surface -> hex8 element face
# ---------------------------------------------------------------------------
def build_face_map(hex_elements):
    """Build a map from frozenset(4 nodes) -> (elem_id, face_label).

    For each hex8 element, register all 6 faces.
    """
    face_map = {}
    for eid, _, _, enodes in hex_elements:
        for face_label, local_ids in C3D8_FACES.items():
            face_nodes = frozenset(enodes[i] for i in local_ids)
            face_map[face_nodes] = (eid, face_label)
    return face_map


def match_surfaces(quad_elements, face_map):
    """Match each quad4 surface element to a hex8 element face.

    Returns dict {phys_group: [(hex_eid, face_label), ...]}
    """
    surfaces = defaultdict(list)
    unmatched = 0
    for _, _, phys, qnodes in quad_elements:
        key = frozenset(qnodes)
        if key in face_map:
            surfaces[phys].append(face_map[key])
        else:
            unmatched += 1
    if unmatched > 0:
        print(f"  AVISO: {unmatched} quad4 sem hex8 correspondente")
    return surfaces


# ---------------------------------------------------------------------------
# WRITER CalculiX .inp
# ---------------------------------------------------------------------------
def write_inp(filepath, nodes, hex_elements, quad_elements, surfaces_matched):
    """Write CalculiX .inp with nodes, elements, sets, and surfaces."""

    os.makedirs(filepath.parent, exist_ok=True)

    # Gmsh M1 uses node labels 1537..5316 (contiguous). CalculiX requires the
    # first *NODE label to be 1 — renumber to 1..N for CCX, keep element IDs.
    sorted_old = sorted(nodes)
    old_to_new = {old: i + 1 for i, old in enumerate(sorted_old)}
    gmsh_node_min, gmsh_node_max = sorted_old[0], sorted_old[-1]

    def rn(nid: int) -> int:
        return old_to_new[nid]

    # Build node sets from surface elements
    nsets = defaultdict(set)
    for _, _, phys, qnodes in quad_elements:
        name = SURFACE_GROUPS.get(phys)
        if name:
            nsets[name].update(rn(n) for n in qnodes)

    # Build element sets from volume elements
    elsets = defaultdict(list)
    for eid, _, phys, _ in hex_elements:
        name = VOLUME_GROUPS.get(phys)
        if name:
            elsets[name].append(eid)

    with open(filepath, "w") as f:
        f.write("** ============================================================\n")
        f.write("** Malha anatomica Lamminsalo M1 (coat-only, coelho)\n")
        f.write("** Convertida de Gmsh 2.2 por convert_gmsh_to_ccx.py\n")
        f.write("** Fonte geometria: Lamminsalo et al. 2018 / Missel 2012\n")
        f.write("** Coordenadas em METROS, pressao em Pa\n")
        f.write(
            f"** Nos Gmsh {gmsh_node_min}..{gmsh_node_max} renumerados para 1..{len(nodes)} (CCX)\n"
        )
        f.write("** ============================================================\n")
        f.write("**\n")

        # --- NODES ---
        f.write(f"** {len(nodes)} nos\n")
        f.write("*NODE, NSET=NALL\n")
        for old_id in sorted_old:
            x, y, z = nodes[old_id]
            # Fixed-width fields (same convention as wp1.4 sphere meshes)
            nid = old_to_new[old_id]
            f.write(f"{nid:8d}, {x:16.9f}, {y:16.9f}, {z:16.9f}\n")

        # --- ELEMENTS ---
        n_hex = len(hex_elements)
        f.write(f"**\n** {n_hex} elementos C3D8I (hex linear, incompatible modes)\n")
        f.write("*ELEMENT, TYPE=C3D8I, ELSET=EALL\n")
        for eid, _, _, enodes in sorted(hex_elements, key=lambda e: e[0]):
            node_str = ", ".join(str(rn(n)) for n in enodes)
            f.write(f"{eid}, {node_str}\n")

        # --- ELSETS by tissue zone ---
        f.write("**\n** ELSETs por zona de tecido\n")
        for name in ["CORNEA", "SCLERA", "CHOROID", "RETINA"]:
            if name in elsets:
                eids = elsets[name]
                f.write(f"**\n*ELSET, ELSET={name}\n")
                for i, eid in enumerate(eids):
                    if i > 0 and i % 16 == 0:
                        f.write("\n")
                    f.write(f"{eid}")
                    if i < len(eids) - 1:
                        f.write(", ")
                f.write("\n")

        # Combined ELSET for all coat
        f.write("**\n*ELSET, ELSET=COAT\n")
        f.write("CORNEA, SCLERA, CHOROID, RETINA\n")

        # --- NSETS by surface patch ---
        f.write("**\n** NSETs por patch de superficie\n")
        for name in ["FSI_ACTIVE", "FSI_IRIS", "FSI_LENS",
                      "OUTER", "SYMMETRY_0", "SYMMETRY_90"]:
            if name in nsets:
                ns = sorted(nsets[name])
                f.write(f"**\n*NSET, NSET=N{name}\n")
                for i, nid in enumerate(ns):
                    if i > 0 and i % 16 == 0:
                        f.write("\n")
                    f.write(f"{nid}")
                    if i < len(ns) - 1:
                        f.write(", ")
                f.write("\n")

        # Combined NSET for all inner surface nodes
        f.write("**\n*NSET, NSET=NINNER\n")
        f.write("NFSI_ACTIVE, NFSI_IRIS, NFSI_LENS\n")

        # Axis + posterior pole (same pattern as fea-sim / o1_solid_to_ccx.py)
        if "SYMMETRY_0" in nsets and "SYMMETRY_90" in nsets:
            axis_ns = sorted(nsets["SYMMETRY_0"] & nsets["SYMMETRY_90"])
            if axis_ns:
                f.write("**\n*NSET, NSET=NAXIS\n")
                for i, nid in enumerate(axis_ns):
                    if i > 0 and i % 16 == 0:
                        f.write("\n")
                    f.write(f"{nid}")
                    if i < len(axis_ns) - 1:
                        f.write(", ")
                f.write("\n")
        pole_old = max(sorted_old, key=lambda oid: nodes[oid][1])
        pole_new = old_to_new[pole_old]
        f.write("**\n*NSET, NSET=NPOSTERIOR_POLE\n")
        f.write(f"{pole_new}\n")

        # --- SURFACES (element-face based) for pressure ---
        f.write("**\n** SURFACEs para carga de pressao (faces de elementos)\n")

        # Individual surfaces
        for phys_id, surf_name in [(5, "SFSI_ACTIVE"), (6, "SFSI_IRIS"),
                                    (7, "SFSI_LENS")]:
            if phys_id in surfaces_matched:
                faces = surfaces_matched[phys_id]
                f.write(f"**\n*SURFACE, NAME={surf_name}, TYPE=ELEMENT\n")
                for hex_eid, face_label in faces:
                    f.write(f"{hex_eid}, {face_label}\n")

        # Combined inner surface for pressure
        f.write("**\n*SURFACE, NAME=SINNER, TYPE=ELEMENT\n")
        for phys_id in [5, 6, 7]:
            if phys_id in surfaces_matched:
                for hex_eid, face_label in surfaces_matched[phys_id]:
                    f.write(f"{hex_eid}, {face_label}\n")

        # Outer surface (for reference)
        if 8 in surfaces_matched:
            f.write("**\n*SURFACE, NAME=SOUTER, TYPE=ELEMENT\n")
            for hex_eid, face_label in surfaces_matched[8]:
                f.write(f"{hex_eid}, {face_label}\n")

        f.write("**\n** FIM DA MALHA\n")
        f.write("** Para usar: *INCLUDE, INPUT=eye_anatomical.inp\n")

    return filepath, old_to_new


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    mesh_path = MESH_FILE
    if not mesh_path.exists():
        # Try absolute Docker path
        mesh_path = Path("/simulation/doc-g3-sim1/geometry/eye_g2_solid_lamminsalo_M1.msh")
    if not mesh_path.exists():
        print(f"ERRO: malha nao encontrada em {MESH_FILE} nem {mesh_path}")
        sys.exit(1)

    print(f"Lendo malha: {mesh_path}")
    nodes, elements, phys_names = parse_gmsh22(mesh_path)
    print(f"  Nos: {len(nodes)}")
    print(f"  Elementos totais: {len(elements)}")
    print(f"  Physical Names: {phys_names}")

    # Separate hex8 (type=5) and quad4 (type=3)
    hex_elements = [(eid, et, ph, en) for eid, et, ph, en in elements if et == 5]
    quad_elements = [(eid, et, ph, en) for eid, et, ph, en in elements if et == 3]
    print("Orientando hex8 Gmsh -> CCX C3D8...")
    hex_elements = orient_hex_elements(hex_elements, nodes, quad_elements)
    print(f"  Hex8 (volume): {len(hex_elements)}")
    print(f"  Quad4 (superficie): {len(quad_elements)}")

    # Count per zone
    vol_counts = defaultdict(int)
    for _, _, ph, _ in hex_elements:
        vol_counts[VOLUME_GROUPS.get(ph, f"unknown_{ph}")] += 1
    print(f"  Zonas de volume: {dict(vol_counts)}")

    surf_counts = defaultdict(int)
    for _, _, ph, _ in quad_elements:
        surf_counts[SURFACE_GROUPS.get(ph, f"unknown_{ph}")] += 1
    print(f"  Patches de superficie: {dict(surf_counts)}")

    # Build face map and match surfaces
    print("Construindo mapa de faces hex8...")
    face_map = build_face_map(hex_elements)
    print(f"  Faces registradas: {len(face_map)}")

    print("Matching quad4 -> hex8 faces...")
    surfaces_matched = match_surfaces(quad_elements, face_map)
    for phys_id, faces in surfaces_matched.items():
        name = SURFACE_GROUPS.get(phys_id, f"unknown_{phys_id}")
        print(f"  {name}: {len(faces)} faces matched")

    # Write .inp
    out_path = OUTPUT_FILE
    print(f"\nEscrevendo .inp: {out_path}")
    out_path, node_remap = write_inp(
        out_path, nodes, hex_elements, quad_elements, surfaces_matched
    )
    gmsh_ids = sorted(nodes)
    print(
        f"  Renumeracao nos: Gmsh {gmsh_ids[0]}..{gmsh_ids[-1]} -> CCX 1..{len(nodes)}"
    )

    # Summary JSON
    summary = {
        "source_mesh": str(mesh_path),
        "output_inp": str(out_path),
        "n_nodes": len(nodes),
        "n_hex8": len(hex_elements),
        "n_quad4": len(quad_elements),
        "element_type": "C3D8I",
        "volume_zones": dict(vol_counts),
        "surface_patches": dict(surf_counts),
        "surfaces_matched": {
            SURFACE_GROUPS.get(k, str(k)): len(v)
            for k, v in surfaces_matched.items()
        },
        "symmetry": {
            "SYMMETRY_0": "plano z=0, restringir DOF 3 (uz=0)",
            "SYMMETRY_90": "plano x=0, restringir DOF 1 (ux=0)",
        },
        "units": {"coordinates": "metros", "pressure": "Pa"},
        "geometry_source": "Lamminsalo et al. 2018 / Missel 2012 (coelho)",
        "node_renumbering": {
            "gmsh_min": gmsh_ids[0],
            "gmsh_max": gmsh_ids[-1],
            "ccx_min": 1,
            "ccx_max": len(nodes),
            "reason": "CalculiX requires first *NODE label to be 1",
        },
    }
    summary_path = Path("../mesh") / "mesh_conversion_summary.json"
    os.makedirs(summary_path.parent, exist_ok=True)
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Resumo salvo em: {summary_path}")

    print("\nConversao concluida com sucesso!")
    print(f"  Nodes: {len(nodes)}")
    print(f"  Elements C3D8: {len(hex_elements)}")
    print(f"  Surface SINNER: {sum(len(surfaces_matched[k]) for k in [5,6,7] if k in surfaces_matched)} faces")


if __name__ == "__main__":
    main()
