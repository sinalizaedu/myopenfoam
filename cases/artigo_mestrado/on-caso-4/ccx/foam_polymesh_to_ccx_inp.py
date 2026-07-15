#!/usr/bin/env python3
"""
foam_polymesh_to_ccx_inp.py
============================
Converte um polyMesh OpenFOAM (hex puro, ASCII) em malha CalculiX .inp:
- *NODE com todos os pontos
- *ELEMENT, TYPE=C3D8 com hex C3D8 por cellZone (ELSETs ON, PIA, SAS, DURA)
- *NSET por patch de boundary (POSTERIOR_ON, ANTERIOR_PIA, etc.)
- *SURFACE, TYPE=ELEMENT por patch (necessario p/ *DSLOAD pressao)
- Adicionalmente: *ELEMENT, TYPE=SPRINGA + *SPRING para fundacao Winkler
  em todos os nos do dura_outer (excluindo perturbation_strip).

Uso:
    python3 foam_polymesh_to_ccx_inp.py \\
        --polymesh path/to/constant/polyMesh \\
        --out-mesh   on-caso-2_mesh.inp \\
        --out-winkler on-caso-2_winkler.inp \\
        --winkler-k 200000

Geometria reconstruida assumindo C3D8 (so hex). Se a malha tiver outros tipos,
o script aborta. Para os patches, mapeamos (face_global -> elemento, face_local)
para emitir o *SURFACE no formato canonico CCX (S1..S6).
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np


# =============================================================================
# Parser de polyMesh ASCII
# =============================================================================

def _strip_header(text: str) -> str:
    """Remove apenas o bloco FoamFile { ... } e comentarios. Preserva o resto."""
    # Remove block comments /* ... */
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    # Remove line comments //
    text = re.sub(r"//[^\n]*", "", text)
    # Remove apenas o bloco FoamFile { ... }
    m = re.search(r"\bFoamFile\s*\{", text)
    if m is not None:
        depth = 1
        i = m.end()
        while i < len(text) and depth > 0:
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
            i += 1
        if depth == 0:
            text = text[:m.start()] + text[i:]
    return text


def _read_count_list(text: str, item_parser):
    """Parseia '<count>(<item> <item> ...)'. item_parser recebe o texto cru
    de um item (sem espaco); retorna lista de items."""
    # Match: number followed by (
    m = re.search(r"(\d+)\s*\(", text)
    if not m:
        raise ValueError("Lista nao encontrada (count + parentesis)")
    count = int(m.group(1))
    start = m.end()  # position after '('
    # Find matching ')'
    depth = 1
    i = start
    while i < len(text) and depth > 0:
        if text[i] == '(':
            depth += 1
        elif text[i] == ')':
            depth -= 1
        i += 1
    if depth != 0:
        raise ValueError("Parentesis sem fechamento")
    body = text[start:i - 1]
    items = item_parser(body, count)
    return items


def parse_points(path: Path) -> np.ndarray:
    text = _strip_header(path.read_text())

    def parse(body: str, count: int) -> np.ndarray:
        floats = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", body)
        arr = np.array(floats, dtype=np.float64).reshape(-1, 3)
        if arr.shape[0] != count:
            raise ValueError(f"points: esperado {count}, lido {arr.shape[0]}")
        return arr

    return _read_count_list(text, parse)


def parse_faces(path: Path) -> List[List[int]]:
    text = _strip_header(path.read_text())

    def parse(body: str, count: int) -> List[List[int]]:
        # Cada face: N(v0 v1 v2 ... vN-1)
        face_re = re.compile(r"(\d+)\s*\(([^)]*)\)")
        faces = []
        for m in face_re.finditer(body):
            n = int(m.group(1))
            verts = [int(x) for x in m.group(2).split()]
            if len(verts) != n:
                raise ValueError(f"face com {n} declarado, {len(verts)} encontrado")
            faces.append(verts)
        if len(faces) != count:
            raise ValueError(f"faces: esperado {count}, lido {len(faces)}")
        return faces

    return _read_count_list(text, parse)


def parse_label_list(path: Path) -> np.ndarray:
    text = _strip_header(path.read_text())

    def parse(body: str, count: int) -> np.ndarray:
        ints = [int(x) for x in re.findall(r"-?\d+", body)]
        if len(ints) != count:
            raise ValueError(f"labelList: esperado {count}, lido {len(ints)}")
        return np.asarray(ints, dtype=np.int32)

    return _read_count_list(text, parse)


def parse_boundary(path: Path) -> Dict[str, Tuple[int, int]]:
    """Retorna {patch_name: (start_face, n_faces)}."""
    text = _strip_header(path.read_text())
    # Top-level: <count>(name { ... } name { ... } ... )
    m = re.search(r"(\d+)\s*\(", text)
    if not m:
        raise ValueError("boundary: lista nao encontrada")
    body = text[m.end():]
    # Match: name {  type ... ;  nFaces N;  startFace S;  ...  }
    patches: Dict[str, Tuple[int, int]] = {}
    pos = 0
    name_re = re.compile(r"\b([A-Za-z_][\w]*)\s*\{")
    while True:
        nm = name_re.search(body, pos)
        if not nm:
            break
        name = nm.group(1)
        depth = 1
        i = nm.end()
        while i < len(body) and depth > 0:
            if body[i] == '{':
                depth += 1
            elif body[i] == '}':
                depth -= 1
            i += 1
        block = body[nm.end():i - 1]
        nf = re.search(r"nFaces\s+(\d+)", block)
        sf = re.search(r"startFace\s+(\d+)", block)
        if nf and sf:
            patches[name] = (int(sf.group(1)), int(nf.group(1)))
        pos = i
    return patches


def parse_cell_zones(path: Path) -> Dict[str, np.ndarray]:
    """Retorna {zone_name: array of cell labels}."""
    text = _strip_header(path.read_text())
    # Cada zona: name { type cellZone; cellLabels List<label> N (...) }
    m = re.search(r"(\d+)\s*\(", text)
    if not m:
        raise ValueError("cellZones: lista nao encontrada")
    body = text[m.end():]
    zones: Dict[str, np.ndarray] = {}
    pos = 0
    name_re = re.compile(r"\b([A-Za-z_][\w]*)\s*\{")
    while True:
        nm = name_re.search(body, pos)
        if not nm:
            break
        name = nm.group(1)
        depth = 1
        i = nm.end()
        while i < len(body) and depth > 0:
            if body[i] == '{':
                depth += 1
            elif body[i] == '}':
                depth -= 1
            i += 1
        block = body[nm.end():i - 1]
        # cellLabels List<label> N (...)
        cl = re.search(r"cellLabels\s+List\s*<\s*label\s*>\s*(\d+)\s*\(([^)]*)\)", block)
        if cl:
            n = int(cl.group(1))
            labels = np.asarray(re.findall(r"\d+", cl.group(2)), dtype=np.int32)
            if labels.size != n:
                raise ValueError(f"zona {name}: esperado {n} labels, lido {labels.size}")
            zones[name] = labels
        pos = i
    return zones


# =============================================================================
# Reconstrucao de hex C3D8
# =============================================================================

def build_cell_faces(owner: np.ndarray, neighbour: np.ndarray, n_cells: int) -> List[List[int]]:
    cell_faces: List[List[int]] = [[] for _ in range(n_cells)]
    for f, c in enumerate(owner):
        cell_faces[int(c)].append(f)
    for f, c in enumerate(neighbour):
        cell_faces[int(c)].append(f + 0)  # neighbour file indexes only internal faces but they share global numbering
    # Wait — neighbour file has same length as nInternalFaces, indexed 0..nInternalFaces-1,
    # mapping face_global → neighbour_cell. So face f_neighbour_idx == f.
    return cell_faces


def reconstruct_hex_connectivity(
    points: np.ndarray,
    faces: List[List[int]],
    owner: np.ndarray,
    neighbour: np.ndarray,
    n_cells: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """Retorna (conn[n_cells, 8], cell_centroid[n_cells, 3])."""
    # Build cell -> faces (correct: owner para todas as faces, neighbour so internas)
    cell_faces: List[List[int]] = [[] for _ in range(n_cells)]
    n_int = neighbour.size
    for f, c in enumerate(owner):
        cell_faces[int(c)].append(f)
    for f, c in enumerate(neighbour):
        cell_faces[int(c)].append(f)

    conn = np.empty((n_cells, 8), dtype=np.int32)
    centroids = np.empty((n_cells, 3), dtype=np.float64)

    for c in range(n_cells):
        cf = cell_faces[c]
        if len(cf) != 6:
            raise ValueError(f"celula {c} tem {len(cf)} faces (esperado 6 para hex)")
        # Verifica que todas sao quads
        for f in cf:
            if len(faces[f]) != 4:
                raise ValueError(f"celula {c} face {f} tem {len(faces[f])} vertices (esperado 4)")
        # Vertices unicos
        all_v = set()
        for f in cf:
            all_v.update(faces[f])
        if len(all_v) != 8:
            raise ValueError(f"celula {c} tem {len(all_v)} vertices unicos (esperado 8)")

        # Centroide da celula
        v_list = list(all_v)
        centroid = points[v_list].mean(axis=0)
        centroids[c] = centroid

        # Face A = primeira face. Face B = unica face com 0 vertices em comum.
        face_a_idx = cf[0]
        face_a = faces[face_a_idx]
        face_a_set = set(face_a)
        face_b_idx = None
        for f in cf[1:]:
            if not (set(faces[f]) & face_a_set):
                face_b_idx = f
                break
        if face_b_idx is None:
            raise ValueError(f"celula {c}: nao achei face oposta a face A")
        face_b = faces[face_b_idx]

        # Ordena face_a CCW vista do interior da celula:
        # Calcula normal da face A no sentido do polygon dado (v0->v1->v2 cross).
        v0, v1, v2, v3 = [points[v] for v in face_a]
        normal_a = np.cross(v1 - v0, v3 - v0)  # quad: usa diagonal
        # Face centroid
        fc_a = (v0 + v1 + v2 + v3) / 4.0
        # Direcao do interior: centroid - fc_a deve apontar PARA dentro da celula.
        # Queremos v1,v2,v3,v4 CCW vistos do interior, ou seja, normal apontando p/ INTERIOR.
        # Se normal_a · (centroid - fc_a) > 0, entao normal_a aponta p/ interior: ok manter ordem.
        # Senao: reverter.
        if np.dot(normal_a, centroid - fc_a) > 0:
            face_a_ord = list(face_a)
        else:
            face_a_ord = list(face_a)[::-1]

        # Para cada v_i de face_a_ord, achar v_{i+4} em face_b adjacente via face lateral.
        # Faces laterais: cf - {face_a_idx, face_b_idx}
        side_faces = [f for f in cf if f != face_a_idx and f != face_b_idx]
        # Para cada v_a, encontra side face contendo v_a, depois o vertice da face_b naquela side face.
        face_b_set = set(face_b)
        v_top: List[int] = [-1, -1, -1, -1]
        for i, va in enumerate(face_a_ord):
            for sf_idx in side_faces:
                sf_verts = faces[sf_idx]
                if va not in sf_verts:
                    continue
                # Side face: 4 vertices, 2 em face_a, 2 em face_b. Pegamos o adjacente a va na face_b.
                # Adjacencia: na lista ciclica de sf_verts, encontre va, vizinhos sao sf_verts[(j-1)%4] e sf_verts[(j+1)%4].
                # Um deles esta em face_b.
                j = sf_verts.index(va)
                for nb in (sf_verts[(j - 1) % 4], sf_verts[(j + 1) % 4]):
                    if nb in face_b_set:
                        v_top[i] = nb
                        break
                if v_top[i] != -1:
                    break
            if v_top[i] == -1:
                raise ValueError(f"celula {c} v_top[{i}] nao encontrado")

        # CCX C3D8: nodes 1-4 face inferior CCW visto do top (i.e., normal vai do bottom ao top).
        # Nossa face_a_ord tem normal apontando p/ interior. Queremos normal apontando p/ face_b
        # (do bottom ao top). face_b esta no interior do nosso vetor "para dentro"? Sim:
        # face_a_ord tem normal apontando p/ centroid; centroid esta entre face_a e face_b.
        # Logo normal vai de face_a -> centroid -> face_b. OK: face_a_ord ja esta na ordem certa
        # (CCW vista do top, ou seja, vista de face_b).
        conn[c, 0:4] = face_a_ord
        conn[c, 4:8] = v_top

    return conn, centroids


def find_face_in_hex(face_verts_set, conn_cell):
    """Dada uma face (set de 4 ints) e a conectividade de uma celula (8 ints na ordem CCX),
    retorna o numero de face local CCX (1-6) ou None.

    CCX C3D8 face nodes (1-based reference):
      F1: 1-2-3-4 (bottom, indices 0-3)
      F2: 5-8-7-6 (top reverso, indices 4,7,6,5)
      F3: 1-2-6-5 (indices 0,1,5,4)
      F4: 2-3-7-6 (indices 1,2,6,5)
      F5: 3-4-8-7 (indices 2,3,7,6)
      F6: 4-1-5-8 (indices 3,0,4,7)
    """
    f1 = {conn_cell[0], conn_cell[1], conn_cell[2], conn_cell[3]}
    f2 = {conn_cell[4], conn_cell[5], conn_cell[6], conn_cell[7]}
    f3 = {conn_cell[0], conn_cell[1], conn_cell[5], conn_cell[4]}
    f4 = {conn_cell[1], conn_cell[2], conn_cell[6], conn_cell[5]}
    f5 = {conn_cell[2], conn_cell[3], conn_cell[7], conn_cell[6]}
    f6 = {conn_cell[3], conn_cell[0], conn_cell[4], conn_cell[7]}
    for k, fset in enumerate((f1, f2, f3, f4, f5, f6), start=1):
        if face_verts_set == fset:
            return k
    return None


# =============================================================================
# Emissao .inp
# =============================================================================

def write_nodes(fh, points: np.ndarray, nset_name: str = "NALL"):
    fh.write(f"*NODE, NSET={nset_name}\n")
    for i, (x, y, z) in enumerate(points, start=1):
        fh.write(f"{i:8d}, {x: .8e}, {y: .8e}, {z: .8e}\n")


def write_elements(fh, conn: np.ndarray, cell_zones: Dict[str, np.ndarray],
                   element_type: str = "C3D8I"):
    """Emite *ELEMENT, TYPE=<element_type>, ELSET=zone para cada cellZone.

    Default C3D8I (hex 8-node com modos incompativeis): bem mais robusto
    para problemas de bending e quase-incompressibilidade (nu>=0.49) que
    o C3D8 puro, sem precisar montar elementos quadraticos C3D20R. Tambem
    suportado: C3D8 (linear puro, sofre locking volumetrico) e C3D8R
    (integracao reduzida, precisa de hourglass control).
    """
    for zname, zcells in cell_zones.items():
        fh.write(f"*ELEMENT, TYPE={element_type}, ELSET={zname.upper()}\n")
        for c in zcells:
            v = conn[int(c)] + 1  # CCX e 1-based
            eid = int(c) + 1
            fh.write(f"{eid:8d}, {v[0]:8d}, {v[1]:8d}, {v[2]:8d}, {v[3]:8d}, "
                     f"{v[4]:8d}, {v[5]:8d}, {v[6]:8d}, {v[7]:8d}\n")


def write_nset_from_faces(fh, name: str, face_indices, faces, dedup=True):
    """*NSET, NSET=name com os vertices unicos de um intervalo de faces."""
    verts = set()
    for f in face_indices:
        verts.update(faces[f])
    fh.write(f"*NSET, NSET={name.upper()}\n")
    sorted_verts = sorted(verts)
    # CCX limita ~16 entradas por linha
    for i in range(0, len(sorted_verts), 8):
        chunk = sorted_verts[i:i + 8]
        line = ", ".join(f"{v + 1:7d}" for v in chunk)
        fh.write(line + "\n")


def write_surface(fh, name: str, face_indices, faces, owner, conn):
    """*SURFACE, NAME=name, TYPE=ELEMENT com (elemento, face_local) para cada face do patch."""
    fh.write(f"*SURFACE, NAME={name.upper()}, TYPE=ELEMENT\n")
    for f in face_indices:
        c = int(owner[f])
        face_set = set(faces[f])
        loc = find_face_in_hex(face_set, conn[c])
        if loc is None:
            raise ValueError(f"face {f} (cell {c}) nao casou com nenhuma face local CCX")
        fh.write(f"{c + 1:8d}, S{loc}\n")


def collect_interface_faces(owner, neighbour, faces, conn, cell2zone,
                            zone_keep: str, zone_other: str):
    """Encontra as faces INTERNAS na interface entre dois cellZones e retorna
    a lista de (elemento_do_zone_keep, face_local_CCX). Usada para expor a
    parede interna da dura (interface dura<->sas) como superficie para *DSLOAD,
    apontando para o elemento da DURA -> pressao positiva empurra a dura para
    FORA (radialmente), pressurizando o lumen como a PIC do LCR."""
    pairs = []
    n_int = int(neighbour.size)
    for f in range(n_int):
        o = int(owner[f])
        nb = int(neighbour[f])
        zo, zn = cell2zone[o], cell2zone[nb]
        if {zo, zn} == {zone_keep, zone_other}:
            dcell = o if zo == zone_keep else nb
            loc = find_face_in_hex(set(faces[f]), conn[dcell])
            if loc is None:
                raise ValueError(f"interface face {f} (cell {dcell}) sem face local CCX")
            pairs.append((dcell, loc))
    return pairs


def write_surface_pairs(fh, name: str, pairs):
    """*SURFACE a partir de pares explicitos (elemento, face_local)."""
    fh.write(f"*SURFACE, NAME={name.upper()}, TYPE=ELEMENT\n")
    for c, loc in pairs:
        fh.write(f"{c + 1:8d}, S{loc}\n")


# =============================================================================
# Winkler springs
# =============================================================================

def compute_node_areas(face_indices, faces, points) -> Dict[int, float]:
    """Soma de 1/4 da area das faces incidentes a cada no, sobre o conjunto face_indices."""
    node_area: Dict[int, float] = {}
    for f in face_indices:
        verts = faces[f]
        # area do quad: 0.5 * |d1 × d2| (diagonais)
        p0, p1, p2, p3 = [points[v] for v in verts]
        area = 0.5 * np.linalg.norm(np.cross(p2 - p0, p3 - p1))
        per_node = area / 4.0
        for v in verts:
            node_area[v] = node_area.get(v, 0.0) + per_node
    return node_area


def write_winkler_inp(
    out_path: Path,
    dura_outer_face_indices,
    perturbation_face_indices,
    faces,
    points: np.ndarray,
    n_existing_nodes: int,
    n_existing_elements: int,
    k_winkler: float,
):
    """Cria nos fantasmas + elementos SPRINGA para Winkler em dura_outer (excluindo perturbation_strip).

    Cada no real do dura_outer (que NAO esta tambem no perturbation_strip) ganha:
     - um no fantasma coincidente, com posicao = posicao do no real
     - um elemento SPRINGA conectando os dois
     - o no fantasma fica engastado (*BOUNDARY 1,3,0)
     - rigidez: k_node = k_winkler * area_nodal

    Nota: SPRINGA usa direcao definida pela geometria inicial (vetor entre os 2 nos).
    Para garantir Winkler radial, deslocamos ligeiramente o no fantasma na direcao
    radial-externa (1 micrometro) -- o spring fica essencialmente alinhado radialmente.
    """
    # Conjunto de nos do dura_outer minus perturbation_strip
    pert_nodes = set()
    for f in perturbation_face_indices:
        pert_nodes.update(faces[f])
    dura_nodes = set()
    for f in dura_outer_face_indices:
        dura_nodes.update(faces[f])
    spring_nodes = sorted(dura_nodes - pert_nodes)

    # Areas nodais (usando so faces de dura_outer)
    node_area = compute_node_areas(dura_outer_face_indices, faces, points)

    GHOST_OFFSET = 1.0e-6  # 1 um radial outward
    ghost_id_start = n_existing_nodes + 1
    elem_id_start = n_existing_elements + 1

    with open(out_path, "w") as fh:
        fh.write("** Winkler foundation springs em dura_outer (excluindo perturbation_strip)\n")
        fh.write("** Gerado automaticamente por foam_polymesh_to_ccx_inp.py\n")
        fh.write(f"** k_winkler = {k_winkler:.3e} Pa/m, {len(spring_nodes)} springs\n")

        # 1) Cria nos fantasmas, NSET=GHOST_WINKLER
        fh.write("*NODE, NSET=GHOST_WINKLER\n")
        ghost_map: Dict[int, int] = {}
        for i, real_v in enumerate(spring_nodes):
            ghost_id = ghost_id_start + i
            ghost_map[real_v] = ghost_id
            x, y, z = points[real_v]
            r = np.hypot(x, y)
            if r < 1e-12:
                # Vertex no eixo: usar +x como fallback (nao ocorre em dura_outer)
                xg, yg = x + GHOST_OFFSET, y
            else:
                # Empurra radialmente (sem alterar z)
                xg = x + GHOST_OFFSET * x / r
                yg = y + GHOST_OFFSET * y / r
            zg = z
            fh.write(f"{ghost_id:8d}, {xg: .8e}, {yg: .8e}, {zg: .8e}\n")

        # 2) Elementos SPRINGA, ELSET=WINKLER (1 por nó, na direção radial)
        # Como cada elemento pode ter k diferente, criaremos 1 ELSET por k unico.
        # Para simplicidade: 1 ELSET por elemento (nao ideal mas robusto).
        # Melhor: agrupar por discretizacao de k. Mas com 948 nos, agrupar por valor exato fica mediocre.
        # Solucao: 1 *ELEMENT por linha, 1 *SPRING block por elemento (cada um com seu k).
        # Para reduzir tamanho do arquivo, escrevemos:
        #   *ELEMENT, TYPE=SPRINGA, ELSET=WK_<i>
        #   eid, real_node, ghost_node
        #   *SPRING, ELSET=WK_<i>
        #   ,  <-- linha em branco obrigatoria (sem orientacao)
        #   k_i
        # Mas isso replica blocos *SPRING. Aceitavel para 948 nos.
        for i, real_v in enumerate(spring_nodes):
            eid = elem_id_start + i
            ghost_id = ghost_map[real_v]
            k_i = k_winkler * node_area.get(real_v, 0.0)
            fh.write(f"*ELEMENT, TYPE=SPRINGA, ELSET=WK_{i}\n")
            fh.write(f"{eid:8d}, {real_v + 1:8d}, {ghost_id:8d}\n")
            fh.write(f"*SPRING, ELSET=WK_{i}\n")
            fh.write("\n")  # blank line (no DOF for SPRINGA)
            fh.write(f"{k_i:.6e}\n")

        # 3) BC: engasta os nos fantasmas em 1,2,3
        fh.write("*BOUNDARY\n")
        fh.write("GHOST_WINKLER, 1, 3, 0\n")


# =============================================================================
# main
# =============================================================================

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--polymesh", required=True, type=Path,
                    help="Diretorio constant/polyMesh do OpenFOAM")
    ap.add_argument("--out-mesh", required=True, type=Path,
                    help="Saida do .inp da malha (NODE+ELEMENT+NSET+SURFACE)")
    ap.add_argument("--out-winkler", required=True, type=Path,
                    help="Saida do .inp dos springs Winkler")
    ap.add_argument("--winkler-k", type=float, default=200000.0,
                    help="Rigidez de Winkler em Pa/m (default 200 kPa/m)")
    ap.add_argument("--element-type", default="C3D8I",
                    choices=["C3D8", "C3D8I", "C3D8R"],
                    help="Tipo de elemento CCX (default C3D8I, recomendado p/ NLGEOM + nu>=0.49)")
    ap.add_argument("--no-winkler", action="store_true",
                    help="Pula geracao de Winkler (caso dura_outer nao precise de molas)")
    args = ap.parse_args()

    pm = args.polymesh
    print(f"[1/5] Lendo polyMesh em {pm}")
    points = parse_points(pm / "points")
    faces = parse_faces(pm / "faces")
    owner = parse_label_list(pm / "owner")
    neighbour = parse_label_list(pm / "neighbour")
    boundary = parse_boundary(pm / "boundary")
    cell_zones = parse_cell_zones(pm / "cellZones")
    n_cells = int(owner.max()) + 1
    print(f"      nodes={len(points)}, faces={len(faces)}, cells={n_cells}, "
          f"patches={len(boundary)}, zones={list(cell_zones.keys())}")

    print(f"[2/5] Reconstruindo conectividade C3D8 ({n_cells} celulas)")
    conn, centroids = reconstruct_hex_connectivity(points, faces, owner, neighbour, n_cells)
    print(f"      OK")

    # Identifica patches de interesse (perturbation pode nao existir)
    if "perturbation_strip" in boundary:
        pert_start, pert_n = boundary["perturbation_strip"]
        perturbation_faces = list(range(pert_start, pert_start + pert_n))
    else:
        perturbation_faces = []
    if "dura_outer" in boundary:
        dura_start, dura_n = boundary["dura_outer"]
        dura_outer_faces = list(range(dura_start, dura_start + dura_n))
    else:
        dura_outer_faces = []

    print(f"[3/5] Escrevendo malha em {args.out_mesh}")
    args.out_mesh.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_mesh, "w") as fh:
        fh.write(f"** Malha {args.element_type} gerada por foam_polymesh_to_ccx_inp.py\n")
        fh.write(f"** Origem: {pm}\n")
        write_nodes(fh, points, nset_name="NALL")
        write_elements(fh, conn, cell_zones, element_type=args.element_type)

        # NSETs por patch
        for pname, (start, n) in boundary.items():
            face_indices = list(range(start, start + n))
            write_nset_from_faces(fh, pname, face_indices, faces)

        # SURFACEs por patch (necessario p/ DSLOAD)
        for pname, (start, n) in boundary.items():
            face_indices = list(range(start, start + n))
            write_surface(fh, f"{pname}_SURF", face_indices, faces, owner, conn)

        # SURFACE interna: parede interna da dura (interface dura<->sas), para
        # aplicar a PIC como *DSLOAD diretamente na parede dural (rota iii).
        cell2zone = [""] * n_cells
        for zname, zcells in cell_zones.items():
            for c in zcells:
                cell2zone[int(c)] = zname
        if "dura" in cell_zones and "sas" in cell_zones:
            inner_pairs = collect_interface_faces(
                owner, neighbour, faces, conn, cell2zone,
                zone_keep="dura", zone_other="sas")
            write_surface_pairs(fh, "DURA_INNER_SURF", inner_pairs)
            print(f"      DURA_INNER_SURF: {len(inner_pairs)} faces (interface dura<->sas)")

    if args.no_winkler or not dura_outer_faces:
        if not args.no_winkler:
            print(f"[4/5] dura_outer ausente -> sem Winkler")
        else:
            print(f"[4/5] --no-winkler: sem Winkler")
        # cria arquivo vazio para o include nao quebrar
        args.out_winkler.write_text(f"** Sem Winkler (--no-winkler ou patch ausente)\n")
    else:
        print(f"[4/5] Escrevendo Winkler em {args.out_winkler}")
        write_winkler_inp(
            args.out_winkler,
            dura_outer_face_indices=dura_outer_faces,
            perturbation_face_indices=perturbation_faces,
            faces=faces,
            points=points,
            n_existing_nodes=len(points),
            n_existing_elements=n_cells,
            k_winkler=args.winkler_k,
        )

    print(f"[5/5] Concluido. Total: {len(points)} nodes, {n_cells} hex {args.element_type}.")


if __name__ == "__main__":
    main()
