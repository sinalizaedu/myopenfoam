"""Gerador da malha CalculiX (.inp) para on-caso-1.2 (FSI ONSAS com lid poroso).

Variante de gen_on_caso_1_blockmesh.py: mantem o FLUIDO OpenFOAM identico,
mas substitui o solido solids4Foam por um solido CalculiX com 7 ZONAS ANATOMICAS
completas (on, pia, dura, lc, sclera_peri, sclera_ring, globo) + Neo-Hookean.

Estrategia de discretizacao:
  - Topologia anelar concentrica (sem O-grid central). O nervo `on` ocupa
    o anel r=[R_INNER, R_ON] em vez de incluir o ponto central (r=0). Como
    o nervo e' muito macio (E~30 kPa) e quase nao contribui estruturalmente
    para os indicadores SANS, essa simplificacao e' aceitavel; o caminho
    de carga essencial (engaste z=0 -> pia/dura -> sclera/globo -> globo_outer)
    permanece intacto.
  - 7 layers radiais: R_INNER, R_ON, R_PIA, R_SAS_MID, R_SAS, R_DURA_MID, R_DURA
  - 6 cells radiais (entre layers consecutivas)
  - N_TANG=8 cells em theta (anel completo, periodico)
  - 32 cells em z: 30 no nervo z=[0,30] mm (dz=1mm), 1 no cap LC z=[30,30.3]
    e 1 no globo z=[30.3,30.8] (espelhando blockMesh do on-caso-1).
  - Total: 1056 hexaedros C3D8 (anel SAS r=[R_PIA, R_SAS] em z=[0,30] e' VAZIO,
    pois e' o dominio fluido peri_porous).

Zonas (ELSETs) gerados:
  EALL_ON          anel R_INNER-R_ON, z=[0,30]      (nervo neural macio)
  EALL_PIA         anel R_ON-R_PIA, z=[0,30]        (pia-mater)
  EALL_DURA        anel R_SAS-R_DURA, z=[0,30]      (dura-mater)
  EALL_LC          anel R_INNER-R_ON, z=[30,30.3]   (lamina cribrosa)
  EALL_SCLERA_PERI anel R_ON-R_SAS, z=[30,30.3]     (esclera peripapilar)
  EALL_SCLERA_RING anel R_SAS-R_DURA, z=[30,30.3]   (anel scleral)
  EALL_GLOBO       anel R_INNER-R_DURA, z=[30.3,30.8] (calota anterior)

NSETs (em all.nam):
  Nposterior_on     z=0, layers 0-1 (R_INNER, R_ON): engaste do nervo
  Nposterior_pia    z=0, layer 2 (R_PIA):           engaste da pia
  Nposterior_dura   z=0, layers 4-6 (R_SAS, ..., R_DURA): engaste da dura
  Nfsi_pia          layer 2, z in [0,30]:           interface FSI pia (preCICE)
  Nfsi_dura         layer 4, z in [0,30]:           interface FSI dura (preCICE)
  Ndura_outer       layer 6, z in [0,30]:           Winkler 200 kPa/m (gordura orbital)
  Ncontact_local    subset de Ndura_outer em z~22.5, theta=0: arteria oftalmica
  Nglobo_outer      layer 6, z in [30.3, 30.8]:     engaste do globo (musculos)
  Nfsi_all          uniao de Nfsi_pia + Nfsi_dura:  placeholder *CLOAD do adapter

SURFACEs (em all.nam, para *DLOAD pressao estatica nas faces internas da esclera):
  Sfsi_sclera_peri_inner  faces lateralmente internas (r=R_PIA) dos elementos
                          do anel R_PIA-R_SAS_MID em z=[30,30.3]
  Sfsi_sclera_peri_outer  faces lateralmente externas (r=R_SAS) dos elementos
                          do anel R_SAS_MID-R_SAS em z=[30,30.3]

Uso:
    python brunaStuff/gen_on_caso_1_2_ccx_inp.py
        -> escreve cases/on-caso-1.2/solid/all.msh  (nodes + elements + elsets)
        -> escreve cases/on-caso-1.2/solid/all.nam  (NSETs + SURFACEs)
"""

from __future__ import annotations

import math
from pathlib import Path

# ---------------------------------------------------------------------------
# Geometria (em metros - CalculiX usa SI direto)
# ---------------------------------------------------------------------------

R_INNER     = 0.75e-3    # raio interno do anel `on` (evita centro pontual)
R_ON        = 1.50e-3
R_PIA       = 1.55e-3
R_SAS_MID   = 2.00e-3
R_SAS       = 2.35e-3
R_DURA_MID  = 2.425e-3   # = (R_SAS + R_DURA) / 2
R_DURA      = 2.50e-3

L_NERVE     = 30.00e-3
T_LC        = 0.30e-3
T_GLOBO     = 0.50e-3

# Layers radiais (7 niveis, 6 cells radiais)
R_LAYERS = (R_INNER, R_ON, R_PIA, R_SAS_MID, R_SAS, R_DURA_MID, R_DURA)
N_LAYERS = len(R_LAYERS)            # 7

# Indices simbolicos
LAYER_INNER     = 0
LAYER_ON        = 1
LAYER_PIA       = 2
LAYER_SAS_MID   = 3
LAYER_SAS       = 4
LAYER_DURA_MID  = 5
LAYER_DURA      = 6

# Discretizacao
N_TANG  = 8                         # cells em theta (= 8 nodes por layer)
NZ_NERVE_CELLS = 30                 # cells em z=[0, L_NERVE]
NZ_LC_CELLS    = 1                  # cells em z=[L_NERVE, L_NERVE+T_LC]
NZ_GLOBO_CELLS = 1                  # cells em z=[L_NERVE+T_LC, L_NERVE+T_LC+T_GLOBO]
NZ_TOTAL_CELLS = NZ_NERVE_CELLS + NZ_LC_CELLS + NZ_GLOBO_CELLS  # 32
NZ_TOTAL_NODES = NZ_TOTAL_CELLS + 1                             # 33

# Indices em z para os boundaries das regioes
IZ_NERVE_TOP = NZ_NERVE_CELLS                       # 30 (= z=L_NERVE)
IZ_LC_TOP    = NZ_NERVE_CELLS + NZ_LC_CELLS         # 31 (= z=L_NERVE+T_LC)
IZ_GLOBO_TOP = NZ_TOTAL_CELLS                       # 32 (= z=L_NERVE+T_LC+T_GLOBO)

# Coordenadas axiais dos niveis em z
Z_NODES = (
    [L_NERVE * i / NZ_NERVE_CELLS for i in range(NZ_NERVE_CELLS + 1)]   # 0, 1, ..., 30
    + [L_NERVE + T_LC]                                                   # 30.3 mm
    + [L_NERVE + T_LC + T_GLOBO]                                         # 30.8 mm
)
assert len(Z_NODES) == NZ_TOTAL_NODES, f"{len(Z_NODES)} != {NZ_TOTAL_NODES}"


# ---------------------------------------------------------------------------
# Mapeamento (i_z, i_layer) -> zona (None = vazio = dominio fluido)
# ---------------------------------------------------------------------------

def cell_zone(i_z: int, i_layer: int) -> str | None:
    """Retorna o nome da zona para a celula (i_z, i_layer)->(i_z+1, i_layer+1).

    None significa que a celula NAO existe (e' dominio fluido SAS).
    """
    # z=[0, L_NERVE]: nervo + bainha (anel SAS = vazio fluido)
    if i_z < IZ_NERVE_TOP:
        if i_layer == LAYER_INNER:    return "on"
        if i_layer == LAYER_ON:       return "pia"
        if i_layer == LAYER_PIA:      return None  # SAS (fluido)
        if i_layer == LAYER_SAS_MID:  return None  # SAS (fluido)
        if i_layer == LAYER_SAS:      return "dura"
        if i_layer == LAYER_DURA_MID: return "dura"
        raise ValueError(f"i_layer fora do range: {i_layer}")

    # z=[L_NERVE, L_NERVE+T_LC]: cap peripapilar
    if i_z < IZ_LC_TOP:
        if i_layer == LAYER_INNER:    return "lc"
        if i_layer == LAYER_ON:       return "sclera_peri"
        if i_layer == LAYER_PIA:      return "sclera_peri"
        if i_layer == LAYER_SAS_MID:  return "sclera_peri"
        if i_layer == LAYER_SAS:      return "sclera_ring"
        if i_layer == LAYER_DURA_MID: return "sclera_ring"
        raise ValueError(f"i_layer fora do range: {i_layer}")

    # z=[L_NERVE+T_LC, L_NERVE+T_LC+T_GLOBO]: calota anterior do globo
    if i_z < IZ_GLOBO_TOP:
        return "globo"  # tudo o globo (todos os anéis radiais)

    raise ValueError(f"i_z fora do range: {i_z}")


# ---------------------------------------------------------------------------
# IDs de nodes e elementos
# ---------------------------------------------------------------------------

def node_id(i_z: int, i_layer: int, i_t: int) -> int:
    """Global node ID, periodico em theta."""
    i_t = i_t % N_TANG
    return 1 + i_z * (N_LAYERS * N_TANG) + i_layer * N_TANG + i_t


def node_coords(i_z: int, i_layer: int, i_t: int) -> tuple[float, float, float]:
    r = R_LAYERS[i_layer]
    z = Z_NODES[i_z]
    theta = 2.0 * math.pi * i_t / N_TANG
    return (r * math.cos(theta), r * math.sin(theta), z)


# ---------------------------------------------------------------------------
# Render mesh (nodes + elements + ELSETs)
# ---------------------------------------------------------------------------

def render_nodes() -> str:
    """Render *NODE block com todos os nodes da malha."""
    lines = [f"** Nodes: {NZ_TOTAL_NODES} z levels x {N_LAYERS} radial layers x {N_TANG} tang"]
    lines.append("*NODE, NSET=NALL")
    for i_z in range(NZ_TOTAL_NODES):
        for i_layer in range(N_LAYERS):
            for i_t in range(N_TANG):
                nid = node_id(i_z, i_layer, i_t)
                x, y, z = node_coords(i_z, i_layer, i_t)
                lines.append(f"{nid}, {x:.10e}, {y:.10e}, {z:.10e}")
    return "\n".join(lines)


def render_elements_and_elsets() -> tuple[str, dict[str, list[int]], dict[tuple[int, int], int]]:
    """Render *ELEMENT por zona com ELSETs nominais.

    Retorna (texto, elements_by_zone, cell_to_eid):
        elements_by_zone: dict zona -> lista de eids
        cell_to_eid: dict (i_z, i_layer) -> dict (i_t -> eid) para mapeamento
                     reverso (necessario para gerar SURFACEs).

    Convencao C3D8 (right-hand rule):
        Bottom face (z=z_lo): n0..n3 visitados na ordem
            n0=(layer_lo, t),   n1=(layer_hi, t),
            n2=(layer_hi, t+1), n3=(layer_lo, t+1)
        Top face (z=z_hi):    n4..n7 mesma ordem em i_z+1.

    Essa ordem produz Jacobiano POSITIVO (validado no MVP de 2 cilindros);
    a face S1 (bottom) tem normal externa em -z e a S2 (top) em +z.
    """
    elements_by_zone: dict[str, list[int]] = {}
    cell_to_eid: dict[tuple[int, int, int], int] = {}    # (i_z, i_layer, i_t) -> eid
    cells_by_zone: dict[str, list[tuple[int, int, int]]] = {}

    eid = 1
    # Primeira passagem: enumerar todas as cells nao-vazias e atribuir eids
    for i_z in range(NZ_TOTAL_CELLS):
        for i_layer in range(N_LAYERS - 1):
            zone = cell_zone(i_z, i_layer)
            if zone is None:
                continue
            for i_t in range(N_TANG):
                cell_to_eid[(i_z, i_layer, i_t)] = eid
                cells_by_zone.setdefault(zone, []).append((i_z, i_layer, i_t))
                elements_by_zone.setdefault(zone, []).append(eid)
                eid += 1

    # Render: um *ELEMENT block por zona com ELSET=EALL_<ZONE>
    lines = [f"** Elements: {eid - 1} hexaedros C3D8 distribuidos em 7 zonas anatomicas"]
    for zone, cells in cells_by_zone.items():
        elset_name = f"EALL_{zone.upper()}"
        lines.append(f"** ---- Zona '{zone}': {len(cells)} hexaedros ----")
        lines.append(f"*ELEMENT, TYPE=C3D8, ELSET={elset_name}")
        for (i_z, i_layer, i_t) in cells:
            this_eid = cell_to_eid[(i_z, i_layer, i_t)]
            n0 = node_id(i_z,     i_layer,     i_t)
            n1 = node_id(i_z,     i_layer + 1, i_t)
            n2 = node_id(i_z,     i_layer + 1, i_t + 1)
            n3 = node_id(i_z,     i_layer,     i_t + 1)
            n4 = node_id(i_z + 1, i_layer,     i_t)
            n5 = node_id(i_z + 1, i_layer + 1, i_t)
            n6 = node_id(i_z + 1, i_layer + 1, i_t + 1)
            n7 = node_id(i_z + 1, i_layer,     i_t + 1)
            lines.append(f"{this_eid}, {n0}, {n1}, {n2}, {n3}, {n4}, {n5}, {n6}, {n7}")

    # ELSET unificado EALL para sanity check
    lines.append("**")
    lines.append("*ELSET, ELSET=EALL")
    elset_names = [f"EALL_{z.upper()}" for z in cells_by_zone]
    for chunk_start in range(0, len(elset_names), 8):
        lines.append(", ".join(elset_names[chunk_start:chunk_start + 8]))

    return "\n".join(lines), elements_by_zone, cell_to_eid


# ---------------------------------------------------------------------------
# NSETs e SURFACEs
# ---------------------------------------------------------------------------

def render_nset(name: str, node_ids: list[int]) -> str:
    if not node_ids:
        return f"** WARNING: NSET {name} esta vazio!"
    lines = [f"*NSET, NSET={name}"]
    for chunk_start in range(0, len(node_ids), 8):
        chunk = node_ids[chunk_start:chunk_start + 8]
        lines.append(", ".join(str(n) for n in chunk))
    return "\n".join(lines)


def collect_nodes(predicate) -> list[int]:
    """Coleta IDs dos nodes que satisfazem o predicado (i_z, i_layer, i_t)."""
    seen = set()
    out = []
    for i_z in range(NZ_TOTAL_NODES):
        for i_layer in range(N_LAYERS):
            for i_t in range(N_TANG):
                if predicate(i_z, i_layer, i_t):
                    nid = node_id(i_z, i_layer, i_t)
                    if nid not in seen:
                        seen.add(nid)
                        out.append(nid)
    return out


def render_surface(name: str, faces: list[tuple[int, str]]) -> str:
    """Render *SURFACE element-based.

    `faces` e' uma lista de (eid, face_label) onde face_label in {S1..S6}.
    """
    if not faces:
        return f"** WARNING: SURFACE {name} esta vazia!"
    lines = [f"*SURFACE, NAME={name}, TYPE=ELEMENT"]
    for eid, face_label in faces:
        lines.append(f"{eid}, {face_label}")
    return "\n".join(lines)


def gen_sclera_peri_surfaces(cell_to_eid: dict) -> tuple[list[tuple[int, str]], list[tuple[int, str]]]:
    """Gera as SURFACEs Sfsi_sclera_peri_inner e Sfsi_sclera_peri_outer.

    Para os elementos anelares do nosso layout:
      - cells (i_z=30, layer=2 -> 3) [anel R_PIA-R_SAS_MID]: face INTERNA r=R_PIA
        e' a face entre nodes (n0, n3, n7, n4) = layer 2, theta=t..t+1, z=lo..hi.
        Convencao C3D8 do CalculiX: a face entre nodes (n0, n3, n7, n4) e' S6.
      - cells (i_z=30, layer=3 -> 4) [anel R_SAS_MID-R_SAS]: face EXTERNA r=R_SAS
        e' a face entre nodes (n1, n2, n6, n5) = layer 4, theta=t..t+1, z=lo..hi.
        Essa face e' S5.

    Convencao das faces no C3D8 do CalculiX (CCX user manual 2.20):
      S1: face com nodes 1-2-3-4    (bottom, k_lo)
      S2: face com nodes 5-8-7-6    (top, k_hi)
      S3: face com nodes 1-2-6-5    (j+ ?)
      S4: face com nodes 2-3-7-6    (i+ ?)
      S5: face com nodes 3-4-8-7    (j-)
      S6: face com nodes 4-1-5-8    (i-)

    Como no nosso ordering n0-n3 e' a face inferior CW vista de +z e n4-n7 e'
    a face superior na mesma orientacao, e como a sequencia interna-externa
    e' n0->n1 (radial out) na bottom, n4->n5 (radial out) na top:
      Face com nodes (n0=interior_t, n3=interior_t+1, n7=interior_top_t+1, n4=interior_top_t):
        em CCX = ?
    Vou empiricamente usar S6 para inner e S4 para outer, e checkar no smoke.

    NOTA: a convencao CCX para C3D8 e' :
      face 1 (S1): nodes 1, 2, 3, 4
      face 2 (S2): nodes 5, 6, 7, 8
      face 3 (S3): nodes 1, 2, 6, 5
      face 4 (S4): nodes 2, 3, 7, 6
      face 5 (S5): nodes 3, 4, 8, 7
      face 6 (S6): nodes 4, 1, 5, 8

    No nosso ordering (n0=lo,t; n1=lo+1,t; n2=lo+1,t+1; n3=lo,t+1;
                       n4=hi,t; n5=hi+1,t; n6=hi+1,t+1; n7=hi,t+1):
      - Face com r interno (layer i_layer constante): nodes (n0, n3, n7, n4)
        = (1-base): nodes 1, 4, 8, 5 -> CCW rotated = 4, 1, 5, 8 = S6
      - Face com r externo (layer i_layer+1 constante): nodes (n1, n2, n6, n5)
        = (1-base): nodes 2, 3, 7, 6 = S4
    """
    inner_faces: list[tuple[int, str]] = []
    outer_faces: list[tuple[int, str]] = []

    # Sfsi_sclera_peri_inner: face r=R_PIA dos elementos do anel R_PIA-R_SAS_MID
    for i_t in range(N_TANG):
        eid = cell_to_eid.get((IZ_NERVE_TOP, LAYER_PIA, i_t))
        if eid is not None:
            inner_faces.append((eid, "S6"))

    # Sfsi_sclera_peri_outer: face r=R_SAS dos elementos do anel R_SAS_MID-R_SAS
    for i_t in range(N_TANG):
        eid = cell_to_eid.get((IZ_NERVE_TOP, LAYER_SAS_MID, i_t))
        if eid is not None:
            outer_faces.append((eid, "S4"))

    return inner_faces, outer_faces


def gen_contact_local_surface(cell_to_eid: dict) -> list[tuple[int, str]]:
    """Gera a SURFACE Scontact_local para *DLOAD da arteria oftalmica (9034 Pa).

    Patch ~1mm x setor centrada em z=22.5 mm, theta=0 (+x): a face EXTERNA
    (r=R_DURA) do elemento da dura em (i_z=22, layer=LAYER_DURA_MID, i_t=0),
    que abrange z=[22,23] mm. Convencao do nosso ordering: a face de r externo
    de um elemento anelar e' a S4 (cf. gen_sclera_peri_surfaces).
    """
    faces: list[tuple[int, str]] = []
    eid = cell_to_eid.get((22, LAYER_DURA_MID, 0))
    if eid is not None:
        faces.append((eid, "S4"))
    return faces


# ---------------------------------------------------------------------------
# Winkler foundation (SPRINGA radiais ligando dura_outer a ghost nodes fixos)
# ---------------------------------------------------------------------------

K_WINKLER       = 2.0e5      # Pa/m (gordura orbital) -- igual ao on-caso-1
GHOST_NODE_BASE = 100000     # offset dos ghost nodes (evita colisao com reais)
SPRING_EID_BASE = 100000     # offset dos elementos SPRINGA
GHOST_RADIAL_EPS = 1.0e-6    # deslocamento radial do ghost (define direcao radial da mola)


def render_winkler() -> str:
    """Gera ghost nodes + SPRINGA + *SPRING para o Winkler em dura_outer.

    Espelha a abordagem do on-caso-2: cada no' de dura_outer (layer R_DURA,
    z=[0, L_NERVE]) e' ligado por uma SPRINGA a um ghost node coincidente,
    deslocado +1um radialmente (assim a direcao da SPRINGA fica radial). O
    ghost e' engastado (NSET GHOST_WINKLER). A rigidez de cada mola e'
    k_node = K_WINKLER * A_tributaria, com A = arco_tangencial * dz_axial
    (dz pela metade nas bordas z=0 e z=L_NERVE).
    """
    arc = 2.0 * math.pi * R_DURA / N_TANG    # arco tangencial por no'
    dz_full = L_NERVE / NZ_NERVE_CELLS       # 1 mm no segmento do nervo

    ghost_lines = ["*NODE, NSET=GHOST_WINKLER"]
    spring_blocks: list[str] = []
    eid = SPRING_EID_BASE
    gid = GHOST_NODE_BASE
    wk = 0

    for i_z in range(IZ_NERVE_TOP + 1):      # z = 0 .. 30 (31 niveis)
        dz_trib = dz_full * (0.5 if i_z in (0, IZ_NERVE_TOP) else 1.0)
        k_node = K_WINKLER * arc * dz_trib
        for i_t in range(N_TANG):
            real = node_id(i_z, LAYER_DURA, i_t)
            theta = 2.0 * math.pi * i_t / N_TANG
            r_ghost = R_DURA + GHOST_RADIAL_EPS
            gx = r_ghost * math.cos(theta)
            gy = r_ghost * math.sin(theta)
            gz = Z_NODES[i_z]
            ghost_lines.append(f"{gid}, {gx:.10e}, {gy:.10e}, {gz:.10e}")
            spring_blocks.append(
                f"*ELEMENT, TYPE=SPRINGA, ELSET=WK_{wk}\n"
                f"{eid}, {real}, {gid}\n"
                f"*SPRING, ELSET=WK_{wk}\n\n{k_node:.6e}"
            )
            eid += 1
            gid += 1
            wk += 1

    lines = [
        "** Winkler foundation em dura_outer (z=[0, L_NERVE]) -- gerado por",
        "** gen_on_caso_1_2_ccx_inp.py. Espelha o on-caso-1 (k=2e5 Pa/m).",
        f"** {wk} SPRINGA radiais para ghost nodes fixos (NSET GHOST_WINKLER).",
        "**",
        "\n".join(ghost_lines),
        "**",
        "\n".join(spring_blocks),
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    out_dir = repo_root / "cases" / "on-caso-1.2" / "solid"
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---- all.msh: nodes + elements + ELSETs ----
    msh_lines = [
        "** Mesh on-caso-1.2 (gerado por gen_on_caso_1_2_ccx_inp.py)",
        "** 7 zonas anatomicas: on, pia, dura, lc, sclera_peri, sclera_ring, globo",
        "** Topologia anelar concentrica com 7 layers radiais e 32 cells em z.",
        "**",
        render_nodes(),
        "**",
    ]
    elements_text, elements_by_zone, cell_to_eid = render_elements_and_elsets()
    msh_lines.append(elements_text)

    msh_target = out_dir / "all.msh"
    msh_target.write_text("\n".join(msh_lines) + "\n")

    # ---- all.nam: NSETs + SURFACEs ----
    nam_lines = [
        "** NSETs e SURFACEs on-caso-1.2 (gerado por gen_on_caso_1_2_ccx_inp.py)",
        "**",
        "** Convencao do calculix-adapter v2.20.1: NSET storage interno e' 'N'+NAME+'N',",
        "** e o adapter constroi 'N'+UPPER(patch_yml)+'N'. Para match, definimos",
        "** NSETs com prefixo 'N' (Nfsi_pia, Nfsi_dura) e no config.yml referenciamos",
        "** sem prefixo (patch: fsi_pia, fsi_dura).",
        "**",
    ]

    # ---- Engastes em z=0 (3 NSETs separados para clareza) ----
    posterior_on_nodes = collect_nodes(
        lambda iz, il, it: iz == 0 and il in (LAYER_INNER, LAYER_ON))
    posterior_pia_nodes = collect_nodes(
        lambda iz, il, it: iz == 0 and il == LAYER_PIA)
    posterior_dura_nodes = collect_nodes(
        lambda iz, il, it: iz == 0 and il in (LAYER_SAS, LAYER_DURA_MID, LAYER_DURA))

    nam_lines.append(render_nset("Nposterior_on",   posterior_on_nodes))
    nam_lines.append("**")
    nam_lines.append(render_nset("Nposterior_pia",  posterior_pia_nodes))
    nam_lines.append("**")
    nam_lines.append(render_nset("Nposterior_dura", posterior_dura_nodes))
    nam_lines.append("**")

    # ---- Interfaces FSI dinamicas ----
    fsi_pia_nodes = collect_nodes(
        lambda iz, il, it: il == LAYER_PIA and 0 <= iz <= IZ_NERVE_TOP)
    fsi_dura_nodes = collect_nodes(
        lambda iz, il, it: il == LAYER_SAS and 0 <= iz <= IZ_NERVE_TOP)

    nam_lines.append(render_nset("Nfsi_pia",  fsi_pia_nodes))
    nam_lines.append("**")
    nam_lines.append(render_nset("Nfsi_dura", fsi_dura_nodes))
    nam_lines.append("**")

    # ---- Winkler em dura_outer (gordura orbital) ----
    # Aplicado apenas nas faces externas da dura no segmento z=[0, L_NERVE].
    dura_outer_nodes = collect_nodes(
        lambda iz, il, it: il == LAYER_DURA and 0 <= iz <= IZ_NERVE_TOP)
    nam_lines.append(render_nset("Ndura_outer", dura_outer_nodes))
    nam_lines.append("**")

    # ---- contact_local: artéria oftalmica ----
    # Patch ~1mm x 0.5mm centrada em z=22.5 mm, theta=0 (+x). Como dz=1 mm
    # no nervo, pegamos os nodes em z=22 mm e z=23 mm (i_z=22 e 23) com
    # i_t=0 (theta=0). Total: 2 nodes (no MVP). Em iteracoes futuras pode
    # refinar com mais theta nodes.
    contact_local_nodes = collect_nodes(
        lambda iz, il, it: il == LAYER_DURA and iz in (22, 23) and it == 0)
    nam_lines.append(render_nset("Ncontact_local", contact_local_nodes))
    nam_lines.append("**")

    # ---- Engaste do globo (musculatura extraocular) ----
    # globo_outer = face externa do globo (r=R_DURA, z=[L_NERVE+T_LC, ...]).
    globo_outer_nodes = collect_nodes(
        lambda iz, il, it: il == LAYER_DURA and IZ_LC_TOP <= iz <= IZ_GLOBO_TOP)
    nam_lines.append(render_nset("Nglobo_outer", globo_outer_nodes))
    nam_lines.append("**")

    # ---- Nfsi_all: placeholder *CLOAD do adapter ccx_preCICE ----
    # Conforme tutorial perpendicular-flap (Nsurface): o adapter exige que
    # cargas existam nos NSETs declarados nas interfaces para alocar sim->nforc.
    fsi_all_nodes = list(dict.fromkeys(fsi_pia_nodes + fsi_dura_nodes))
    nam_lines.append(render_nset("Nfsi_all", fsi_all_nodes))
    nam_lines.append("**")

    # ---- SURFACEs para *DLOAD pressao estatica nas faces internas da esclera ----
    inner_faces, outer_faces = gen_sclera_peri_surfaces(cell_to_eid)
    nam_lines.append(render_surface("Sfsi_sclera_peri_inner", inner_faces))
    nam_lines.append("**")
    nam_lines.append(render_surface("Sfsi_sclera_peri_outer", outer_faces))
    nam_lines.append("**")

    # ---- SURFACE para *DLOAD da carga arterial (contact_local, 9034 Pa) ----
    # Espelha o on-caso-1: pressao distribuida na face externa da dura, em vez
    # da aproximacao por forcas nodais. Face S4 (r=R_DURA) do elemento da dura
    # em z=[22,23] mm, setor +x.
    contact_faces = gen_contact_local_surface(cell_to_eid)
    nam_lines.append(render_surface("Scontact_local", contact_faces))
    nam_lines.append("**")

    nam_target = out_dir / "all.nam"
    nam_target.write_text("\n".join(nam_lines) + "\n")

    # ---- winkler.inp: ghost nodes + SPRINGA radiais (gordura orbital) ----
    wink_target = out_dir / "winkler.inp"
    wink_target.write_text(render_winkler() + "\n")

    # ---- Stats ----
    total_elems = sum(len(v) for v in elements_by_zone.values())
    total_nodes = NZ_TOTAL_NODES * N_LAYERS * N_TANG

    n_wink = (IZ_NERVE_TOP + 1) * N_TANG
    print(f"wrote {msh_target}")
    print(f"wrote {nam_target}")
    print(f"wrote {wink_target}  ({n_wink} SPRINGA Winkler, k={K_WINKLER:.1e} Pa/m)")
    print(f"  Scontact_local: {len(contact_faces):5d} face(s) (DLOAD 9034 Pa)")
    print()
    print(f"Mesh stats:")
    print(f"  Nodes:    {total_nodes} ({NZ_TOTAL_NODES} z x {N_LAYERS} radial x {N_TANG} tang)")
    print(f"  Elements: {total_elems} hexaedros C3D8")
    print()
    print(f"Zonas (ELSETs):")
    for zone, eids in elements_by_zone.items():
        print(f"  EALL_{zone.upper():12s}: {len(eids):5d} elementos")
    print()
    print(f"NSETs:")
    print(f"  Nposterior_on    : {len(posterior_on_nodes):5d} nodes")
    print(f"  Nposterior_pia   : {len(posterior_pia_nodes):5d} nodes")
    print(f"  Nposterior_dura  : {len(posterior_dura_nodes):5d} nodes")
    print(f"  Nfsi_pia         : {len(fsi_pia_nodes):5d} nodes")
    print(f"  Nfsi_dura        : {len(fsi_dura_nodes):5d} nodes")
    print(f"  Ndura_outer      : {len(dura_outer_nodes):5d} nodes (Winkler)")
    print(f"  Ncontact_local   : {len(contact_local_nodes):5d} nodes (arteria oftalmica)")
    print(f"  Nglobo_outer     : {len(globo_outer_nodes):5d} nodes (engaste globo)")
    print(f"  Nfsi_all         : {len(fsi_all_nodes):5d} nodes (placeholder *CLOAD)")
    print()
    print(f"SURFACEs (para *DLOAD pressao estatica 1333 Pa):")
    print(f"  Sfsi_sclera_peri_inner: {len(inner_faces):5d} faces (r=R_PIA)")
    print(f"  Sfsi_sclera_peri_outer: {len(outer_faces):5d} faces (r=R_SAS)")


if __name__ == "__main__":
    main()
