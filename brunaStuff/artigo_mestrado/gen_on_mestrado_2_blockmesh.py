"""Gerador do blockMeshDict do caso on-mestrado-2.

Geometria (7 zonas + chanfro da dura entre z=27 e z=30 mm):
    on     : r=0    -1.50,  z=0   -30.0,  E=30 kPa
    pia    : r=1.50 -1.55,  z=0   -30.0,  E=3  MPa
    sas    : r=1.55 -2.35,  z=0   -30.0,  E=1  kPa
    dura   : r=2.35 -2.50,  z=0   -27.0,  E=3  MPa  (uniforme)
    dura   : r=2.35 -r(z),  z=27  -30.0,  E=3  MPa  (chanfro 2.5 -> 2.65)
    lc     : r=0    -1.50,  z=30  -30.5,  E=0.4 MPa
    sclera : r=1.50 -2.65,  z=30  -30.5,  E=5  MPa  (sub-anel 1.50-1.55-2.35-2.65)
    globo  : r=0    -2.65,  z=30.5-31.0,  E=5  MPa  (sub-anel 0-1.50-1.55-2.35-2.65)

Discretizacao radial na bainha: pia=1, sas=6, dura=2 celulas. Tangencial 8/quadrante.
Axial: 27 celulas em z=0-27, 3 celulas em z=27-30, 1 em z=30-30.5, 1 em z=30.5-31.

Continuidade nodal: TODOS os blocos compartilham vertices nos planos z=0,27,30,30.5,31.
Nada de mergePatchPairs/stitchMesh/regionCouple. Solver linearGeometryTotalDisplacement
com interpolate(impK) harmonic trata cada interface como bondeada por DOF.

Uso:
    python brunaStuff/gen_on_mestrado_2_blockmesh.py
        -> escreve cases/on-mestrado-2/solid/system/blockMeshDict
"""

from __future__ import annotations

import math
from pathlib import Path

# ---------------------------------------------------------------------------
# Parametros geometricos (em mm; scale 0.001 aplicado pelo blockMesh)
# ---------------------------------------------------------------------------

R_SQUARE = 0.75   # meio lado do quadrado central (sq corner em (+/-0.75, +/-0.75))
R_ON     = 1.50
R_PIA    = 1.55
R_SAS    = 2.35
R_DURA_LO = 2.50  # raio externo da dura no trecho cilindrico (z<=27)
R_DURA_HI = 2.65  # raio externo no chanfro/esclera/globo (z>=30)

Z_LEVELS = (0.0, 27.0, 30.0, 30.5, 31.0)
N_AXIAL  = (27, 3, 1, 1)            # celulas por segmento z

N_TANG   = 8                         # celulas tangenciais por quadrante
N_RAD_ON   = 6                       # ON quadrant (square -> ON circle)
N_RAD_CTR  = 8                       # quadrado central (j tambem 8)
N_RAD_PIA  = 1                       # pia (ON -> pia)
N_RAD_SAS  = 6                       # sas (pia -> sas)
N_RAD_DURA = 2                       # dura (sas -> dura)

CORNERS = ('NE', 'NW', 'SW', 'SE')   # ordem para o O-grid; segue o caso original

# Indice das camadas radiais
LAYER_SQUARE = 0
LAYER_ON     = 1
LAYER_PIA    = 2
LAYER_SAS    = 3
LAYER_DURA   = 4
N_LAYERS = 5

# ---------------------------------------------------------------------------
# Vertices
# ---------------------------------------------------------------------------


def diag_for_layer(layer: int, z: float) -> float:
    """Distancia diagonal (corner) para a camada radial em mm."""
    if layer == LAYER_SQUARE:
        return R_SQUARE
    if layer == LAYER_ON:
        return R_ON / math.sqrt(2.0)
    if layer == LAYER_PIA:
        return R_PIA / math.sqrt(2.0)
    if layer == LAYER_SAS:
        return R_SAS / math.sqrt(2.0)
    if layer == LAYER_DURA:
        if z <= 27.0 + 1e-9:
            r = R_DURA_LO
        elif z >= 30.0 - 1e-9:
            r = R_DURA_HI
        else:
            r = R_DURA_LO + (z - 27.0) / 3.0 * (R_DURA_HI - R_DURA_LO)
        return r / math.sqrt(2.0)
    raise ValueError(f"layer invalido: {layer}")


def corner_xy(corner: str, d: float) -> tuple[float, float]:
    if corner == 'NE': return ( d,  d)
    if corner == 'NW': return (-d,  d)
    if corner == 'SW': return (-d, -d)
    if corner == 'SE': return ( d, -d)
    raise ValueError(corner)


def vid(z_idx: int, layer: int, corner_idx: int) -> int:
    """Indice global do vertice."""
    return z_idx * (N_LAYERS * 4) + layer * 4 + corner_idx


def build_vertices() -> list[tuple[float, float, float]]:
    vs: list[tuple[float, float, float]] = []
    for z_idx, z in enumerate(Z_LEVELS):
        for layer in range(N_LAYERS):
            d = diag_for_layer(layer, z)
            for c_idx, c in enumerate(CORNERS):
                x, y = corner_xy(c, d)
                vs.append((x, y, z))
    return vs


# ---------------------------------------------------------------------------
# Helpers para arcos e blocos
# ---------------------------------------------------------------------------

def radius_for_layer_at_z(layer: int, z: float) -> float:
    if layer == LAYER_ON: return R_ON
    if layer == LAYER_PIA: return R_PIA
    if layer == LAYER_SAS: return R_SAS
    if layer == LAYER_DURA:
        if z <= 27.0 + 1e-9: return R_DURA_LO
        if z >= 30.0 - 1e-9: return R_DURA_HI
        return R_DURA_LO + (z - 27.0) / 3.0 * (R_DURA_HI - R_DURA_LO)
    raise ValueError(layer)


def arcs_for_circle(z_idx: int, z: float, layer: int) -> list[tuple[int, int, tuple[float, float, float]]]:
    """Arcos do O-grid para a camada `layer` no plano z. Retorna 4 arcos:
    NE-SE (apex +X), NE-NW (apex +Y), NW-SW (apex -X), SW-SE (apex -Y).
    Camadas do quadrado nao tem arcos.
    """
    if layer == LAYER_SQUARE:
        return []
    r = radius_for_layer_at_z(layer, z)
    NE, NW, SW, SE = (vid(z_idx, layer, i) for i in range(4))
    return [
        (NE, SE, ( r, 0.0, z)),    # arco leste (atraves de +X)
        (NE, NW, (0.0,  r, z)),    # arco norte
        (NW, SW, (-r, 0.0, z)),    # arco oeste
        (SW, SE, (0.0, -r, z)),    # arco sul
    ]


def quadrant_block(side: str, z_idx_lo: int, z_idx_hi: int,
                   layer_in: int, layer_out: int,
                   zone: str, n_radial: int, n_axial: int,
                   comment: str = "") -> str:
    """Gera string de um bloco hex de quadrante (E/N/W/S).

    side:        'E' | 'N' | 'W' | 'S'
    layer_in/out: camadas radiais (square=0, ON=1, pia=2, sas=3, dura=4)
    """
    # Mapa do side -> par (corner_inner_a, corner_inner_b) que define a "fatia"
    # angular em ordem CCW vista de cima (+z), seguindo a convencao do caso original.
    if side == 'E':
        a, b = 'SE', 'NE'   # ON_E: sq_SE -> on_SE -> on_NE -> sq_NE
    elif side == 'N':
        a, b = 'NE', 'NW'
    elif side == 'W':
        a, b = 'NW', 'SW'
    elif side == 'S':
        a, b = 'SW', 'SE'
    else:
        raise ValueError(side)

    ai = CORNERS.index(a)
    bi = CORNERS.index(b)
    # bottom face: (in_a, out_a, out_b, in_b)
    v0 = vid(z_idx_lo, layer_in,  ai)
    v1 = vid(z_idx_lo, layer_out, ai)
    v2 = vid(z_idx_lo, layer_out, bi)
    v3 = vid(z_idx_lo, layer_in,  bi)
    v4 = vid(z_idx_hi, layer_in,  ai)
    v5 = vid(z_idx_hi, layer_out, ai)
    v6 = vid(z_idx_hi, layer_out, bi)
    v7 = vid(z_idx_hi, layer_in,  bi)

    return (
        f"    hex ( {v0:3d} {v1:3d} {v2:3d} {v3:3d}  "
        f"{v4:3d} {v5:3d} {v6:3d} {v7:3d} )  "
        f"{zone:7s} ( {n_radial} {N_TANG} {n_axial} )  "
        f"simpleGrading ( 1 1 1 )"
        + (f"  // {comment}" if comment else "")
    )


def center_block(z_idx_lo: int, z_idx_hi: int, zone: str, n_axial: int,
                 comment: str = "") -> str:
    """Bloco central do O-grid (quadrado r=-0.75..0.75)."""
    # bottom: NE -> NW -> SW -> SE  (CCW de cima)
    NE, NW, SW, SE = (vid(z_idx_lo, LAYER_SQUARE, i) for i in range(4))
    NEt, NWt, SWt, SEt = (vid(z_idx_hi, LAYER_SQUARE, i) for i in range(4))
    return (
        f"    hex ( {NE:3d} {NW:3d} {SW:3d} {SE:3d}  "
        f"{NEt:3d} {NWt:3d} {SWt:3d} {SEt:3d} )  "
        f"{zone:7s} ( {N_RAD_CTR} {N_TANG} {n_axial} )  "
        f"simpleGrading ( 1 1 1 )"
        + (f"  // {comment}" if comment else "")
    )


# ---------------------------------------------------------------------------
# Faces de patch (helpers)
# ---------------------------------------------------------------------------

def k_min_face_quadrant(z_idx: int, side: str, layer_in: int, layer_out: int) -> tuple[int, int, int, int]:
    """Face k_min (z_idx) de um bloco de quadrante.
    Para um hex (v0 v1 v2 v3 v4 v5 v6 v7), k_min = (v0 v1 v2 v3) na ordem listada
    no boundary (que e a mesma sequencia do bottom face do hex).
    """
    if side == 'E': a, b = 'SE', 'NE'
    elif side == 'N': a, b = 'NE', 'NW'
    elif side == 'W': a, b = 'NW', 'SW'
    elif side == 'S': a, b = 'SW', 'SE'
    else: raise ValueError(side)
    ai, bi = CORNERS.index(a), CORNERS.index(b)
    v0 = vid(z_idx, layer_in,  ai)
    v1 = vid(z_idx, layer_out, ai)
    v2 = vid(z_idx, layer_out, bi)
    v3 = vid(z_idx, layer_in,  bi)
    return (v0, v1, v2, v3)


def k_max_face_quadrant(z_idx: int, side: str, layer_in: int, layer_out: int) -> tuple[int, int, int, int]:
    """k_max e (v4 v5 v6 v7) na ordem do hex."""
    if side == 'E': a, b = 'SE', 'NE'
    elif side == 'N': a, b = 'NE', 'NW'
    elif side == 'W': a, b = 'NW', 'SW'
    elif side == 'S': a, b = 'SW', 'SE'
    else: raise ValueError(side)
    ai, bi = CORNERS.index(a), CORNERS.index(b)
    v4 = vid(z_idx, layer_in,  ai)
    v5 = vid(z_idx, layer_out, ai)
    v6 = vid(z_idx, layer_out, bi)
    v7 = vid(z_idx, layer_in,  bi)
    return (v4, v5, v6, v7)


def k_min_face_center(z_idx: int) -> tuple[int, int, int, int]:
    """k_min do bloco central: (NE NW SW SE) no plano z_idx."""
    return tuple(vid(z_idx, LAYER_SQUARE, i) for i in range(4))


def k_max_face_center(z_idx: int) -> tuple[int, int, int, int]:
    return tuple(vid(z_idx, LAYER_SQUARE, i) for i in range(4))


def i_max_face_quadrant(z_idx_lo: int, z_idx_hi: int, side: str,
                        layer_in: int, layer_out: int) -> tuple[int, int, int, int]:
    """Face i_max (radial externa). Hex (v0 v1 v2 v3 v4 v5 v6 v7) ->
    i_max = (v1 v2 v6 v5) na ordem listada na boundary.
    """
    if side == 'E': a, b = 'SE', 'NE'
    elif side == 'N': a, b = 'NE', 'NW'
    elif side == 'W': a, b = 'NW', 'SW'
    elif side == 'S': a, b = 'SW', 'SE'
    else: raise ValueError(side)
    ai, bi = CORNERS.index(a), CORNERS.index(b)
    v1 = vid(z_idx_lo, layer_out, ai)
    v2 = vid(z_idx_lo, layer_out, bi)
    v6 = vid(z_idx_hi, layer_out, bi)
    v5 = vid(z_idx_hi, layer_out, ai)
    return (v1, v2, v6, v5)


# ---------------------------------------------------------------------------
# Renderizacao do dicionario
# ---------------------------------------------------------------------------

HEADER = """FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}

// on-mestrado-2 - bainha do nervo optico fatiada em pia/SAS/dura + chanfro da dura.
//
// Geometria (scale 0.001 -> mm; ver brunaStuff/gen_on_mestrado_2_blockmesh.py):
//   on     : r=0    -1.50, z=0   -30.0   (E=30 kPa)
//   pia    : r=1.50 -1.55, z=0   -30.0   (E=3  MPa)
//   sas    : r=1.55 -2.35, z=0   -30.0   (E=1  kPa)
//   dura   : r=2.35 -2.50, z=0   -27.0   (E=3  MPa)  trecho uniforme
//   dura   : r=2.35 -r(z), z=27  -30.0   (E=3  MPa)  chanfro 2.50 -> 2.65
//   lc     : r=0    -1.50, z=30  -30.5   (E=0.4 MPa)
//   sclera : r=1.50 -2.65, z=30  -30.5   (E=5  MPa)  3 sub-aneis bondeados
//   globo  : r=0    -2.65, z=30.5-31.0   (E=5  MPa)  4 sub-aneis bondeados
//
// Continuidade nodal: todos os blocos compartilham vertices em z=0,27,30,30.5,31.
// Nao usamos mergePatchPairs / stitchMesh / regionCouple. A malha e conforme por
// construcao -> o solver linearGeometryTotalDisplacement com impK harmonic
// trata cada interface material como bondeada por solidariedade de DOFs.
//
// Patches:
//   posterior_on    -> z=0, r<1.50              (nervo livre)
//   posterior_pia   -> z=0, r=1.50-1.55         (livre, segue ON)
//   posterior_sas   -> z=0, r=1.55-2.35         (P_CSF=2667 Pa)
//   posterior_dura  -> z=0, r=2.35-2.50         (canal optico, fixedDisplacement)
//   contact_artoph  -> r=2.5/2.65 setor +X      (renomeada para dura_outer_E)
//   ons_outer       -> r=2.5/2.65 setores N/W/S (renomeada para dura_outer)
//   sclera_outer    -> r=2.65, z=30-30.5
//   globo_outer     -> r=2.65, z=30.5-31.0
//   anterior_globo  -> z=31, todos os blocos do globo (parede orbital, fixed)

scale   0.001;
"""


def render_vertices(vs: list[tuple[float, float, float]]) -> str:
    lines = ["vertices", "("]
    for i, (x, y, z) in enumerate(vs):
        lines.append(f"    ( {x:11.6f}  {y:11.6f}  {z:6.2f} )  // {i:3d}")
    lines.append(");")
    return "\n".join(lines)


def render_blocks() -> str:
    out: list[str] = ["blocks", "("]

    # ---- Camada axial 0: z=0 -> z=27 (trecho cilindrico) -----------------
    out.append("    // ===== z=0 a 27 mm: trecho cilindrico uniforme =====")
    out.append(center_block(0, 1, "on", N_AXIAL[0], "ON central"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 0, 1, LAYER_SQUARE, LAYER_ON,
                                  "on", N_RAD_ON, N_AXIAL[0], f"ON_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 0, 1, LAYER_ON, LAYER_PIA,
                                  "pia", N_RAD_PIA, N_AXIAL[0], f"pia_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 0, 1, LAYER_PIA, LAYER_SAS,
                                  "sas", N_RAD_SAS, N_AXIAL[0], f"sas_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 0, 1, LAYER_SAS, LAYER_DURA,
                                  "dura", N_RAD_DURA, N_AXIAL[0], f"dura_{side}"))

    # ---- Camada axial 1: z=27 -> z=30 (chanfro da dura) -------------------
    out.append("")
    out.append("    // ===== z=27 a 30 mm: chanfro da dura (r 2.50 -> 2.65) =====")
    out.append(center_block(1, 2, "on", N_AXIAL[1], "ON central chanfro"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 1, 2, LAYER_SQUARE, LAYER_ON,
                                  "on", N_RAD_ON, N_AXIAL[1], f"ON_{side}_ch"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 1, 2, LAYER_ON, LAYER_PIA,
                                  "pia", N_RAD_PIA, N_AXIAL[1], f"pia_{side}_ch"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 1, 2, LAYER_PIA, LAYER_SAS,
                                  "sas", N_RAD_SAS, N_AXIAL[1], f"sas_{side}_ch"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 1, 2, LAYER_SAS, LAYER_DURA,
                                  "dura", N_RAD_DURA, N_AXIAL[1], f"dura_{side}_ch"))

    # ---- Camada axial 2: z=30 -> z=30.5 (lc + esclera) --------------------
    out.append("")
    out.append("    // ===== z=30 a 30.5 mm: lamina cribrosa + esclera =====")
    out.append(center_block(2, 3, "lc", N_AXIAL[2], "lc central"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 2, 3, LAYER_SQUARE, LAYER_ON,
                                  "lc", N_RAD_ON, N_AXIAL[2], f"lc_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 2, 3, LAYER_ON, LAYER_PIA,
                                  "sclera", N_RAD_PIA, N_AXIAL[2], f"sclera_pia_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 2, 3, LAYER_PIA, LAYER_SAS,
                                  "sclera", N_RAD_SAS, N_AXIAL[2], f"sclera_sas_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 2, 3, LAYER_SAS, LAYER_DURA,
                                  "sclera", N_RAD_DURA, N_AXIAL[2], f"sclera_dura_{side}"))

    # ---- Camada axial 3: z=30.5 -> z=31 (globo) ---------------------------
    out.append("")
    out.append("    // ===== z=30.5 a 31 mm: casca do globo =====")
    out.append(center_block(3, 4, "globo", N_AXIAL[3], "globo central"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 3, 4, LAYER_SQUARE, LAYER_ON,
                                  "globo", N_RAD_ON, N_AXIAL[3], f"globo_ON_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 3, 4, LAYER_ON, LAYER_PIA,
                                  "globo", N_RAD_PIA, N_AXIAL[3], f"globo_pia_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 3, 4, LAYER_PIA, LAYER_SAS,
                                  "globo", N_RAD_SAS, N_AXIAL[3], f"globo_sas_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 3, 4, LAYER_SAS, LAYER_DURA,
                                  "globo", N_RAD_DURA, N_AXIAL[3], f"globo_dura_{side}"))

    out.append(");")
    return "\n".join(out)


def render_edges() -> str:
    out: list[str] = ["edges", "("]
    # Para cada plano z e cada camada com curvatura, adicionar os 4 arcos.
    layer_radii = {
        LAYER_ON:   ('ON  r=1.50',  'ON'),
        LAYER_PIA:  ('pia r=1.55',  'pia'),
        LAYER_SAS:  ('sas r=2.35',  'sas'),
        LAYER_DURA: ('dura',         'dura'),
    }
    for z_idx, z in enumerate(Z_LEVELS):
        for layer, (label, _short) in layer_radii.items():
            r = radius_for_layer_at_z(layer, z)
            arcs = arcs_for_circle(z_idx, z, layer)
            out.append(f"    // ---- {label}  r={r:.3f} mm  @ z={z:.2f} mm ----")
            for a, b, mid in arcs:
                out.append(f"    arc {a:3d} {b:3d}  ( {mid[0]:9.5f}  {mid[1]:9.5f}  {mid[2]:6.2f} )")
        out.append("")
    out.append(");")
    return "\n".join(out)


def render_boundary() -> str:
    out: list[str] = ["boundary", "("]

    # ---- posterior_on (z=0) ----------------------------------------------
    out.append("    posterior_on")
    out.append("    {")
    out.append("        type wall;")
    out.append("        faces")
    out.append("        (")
    out.append(f"            {tuple_to_face(k_min_face_center(0))}   // ON central")
    for side in ('E', 'N', 'W', 'S'):
        f = k_min_face_quadrant(0, side, LAYER_SQUARE, LAYER_ON)
        out.append(f"            {tuple_to_face(f)}   // ON_{side}")
    out.append("        );")
    out.append("    }")
    out.append("")

    # ---- posterior_pia (z=0) ----------------------------------------------
    out.append("    posterior_pia")
    out.append("    {")
    out.append("        type wall;")
    out.append("        faces")
    out.append("        (")
    for side in ('E', 'N', 'W', 'S'):
        f = k_min_face_quadrant(0, side, LAYER_ON, LAYER_PIA)
        out.append(f"            {tuple_to_face(f)}   // pia_{side}")
    out.append("        );")
    out.append("    }")
    out.append("")

    # ---- posterior_sas (z=0) ----------------------------------------------
    out.append("    posterior_sas")
    out.append("    {")
    out.append("        type wall;")
    out.append("        faces")
    out.append("        (")
    for side in ('E', 'N', 'W', 'S'):
        f = k_min_face_quadrant(0, side, LAYER_PIA, LAYER_SAS)
        out.append(f"            {tuple_to_face(f)}   // sas_{side}")
    out.append("        );")
    out.append("    }")
    out.append("")

    # ---- posterior_dura (z=0) ---------------------------------------------
    out.append("    posterior_dura")
    out.append("    {")
    out.append("        type wall;")
    out.append("        faces")
    out.append("        (")
    for side in ('E', 'N', 'W', 'S'):
        f = k_min_face_quadrant(0, side, LAYER_SAS, LAYER_DURA)
        out.append(f"            {tuple_to_face(f)}   // dura_{side}")
    out.append("        );")
    out.append("    }")
    out.append("")

    # ---- contact_artoph (i_max E da dura, z=0-27 e z=27-30) --------------
    # Mantemos o nome 'contact_artoph' aqui para o createPatchDict_contact
    # renomear para 'dura_outer_E' (reuso da convencao do on-mestrado).
    out.append("    contact_artoph")
    out.append("    {")
    out.append("        type wall;")
    out.append("        faces")
    out.append("        (")
    f1 = i_max_face_quadrant(0, 1, 'E', LAYER_SAS, LAYER_DURA)
    f2 = i_max_face_quadrant(1, 2, 'E', LAYER_SAS, LAYER_DURA)
    out.append(f"            {tuple_to_face(f1)}   // dura_E z=0-27")
    out.append(f"            {tuple_to_face(f2)}   // dura_E z=27-30 (chanfro)")
    out.append("        );")
    out.append("    }")
    out.append("")

    # ---- ons_outer (i_max N/W/S da dura) ---------------------------------
    out.append("    ons_outer")
    out.append("    {")
    out.append("        type wall;")
    out.append("        faces")
    out.append("        (")
    for side in ('N', 'W', 'S'):
        f1 = i_max_face_quadrant(0, 1, side, LAYER_SAS, LAYER_DURA)
        out.append(f"            {tuple_to_face(f1)}   // dura_{side} z=0-27")
    for side in ('N', 'W', 'S'):
        f2 = i_max_face_quadrant(1, 2, side, LAYER_SAS, LAYER_DURA)
        out.append(f"            {tuple_to_face(f2)}   // dura_{side} z=27-30 (chanfro)")
    out.append("        );")
    out.append("    }")
    out.append("")

    # ---- sclera_outer (z=30-30.5, i_max do sclera_dura) ------------------
    out.append("    sclera_outer")
    out.append("    {")
    out.append("        type wall;")
    out.append("        faces")
    out.append("        (")
    for side in ('E', 'N', 'W', 'S'):
        f = i_max_face_quadrant(2, 3, side, LAYER_SAS, LAYER_DURA)
        out.append(f"            {tuple_to_face(f)}   // sclera_dura_{side}")
    out.append("        );")
    out.append("    }")
    out.append("")

    # ---- globo_outer (z=30.5-31, i_max do globo_dura) --------------------
    out.append("    globo_outer")
    out.append("    {")
    out.append("        type wall;")
    out.append("        faces")
    out.append("        (")
    for side in ('E', 'N', 'W', 'S'):
        f = i_max_face_quadrant(3, 4, side, LAYER_SAS, LAYER_DURA)
        out.append(f"            {tuple_to_face(f)}   // globo_dura_{side}")
    out.append("        );")
    out.append("    }")
    out.append("")

    # ---- anterior_globo (z=31 face de todos os blocos do globo) ----------
    out.append("    anterior_globo")
    out.append("    {")
    out.append("        type wall;")
    out.append("        faces")
    out.append("        (")
    out.append(f"            {tuple_to_face(k_max_face_center(4))}   // globo central")
    for side in ('E', 'N', 'W', 'S'):
        f = k_max_face_quadrant(4, side, LAYER_SQUARE, LAYER_ON)
        out.append(f"            {tuple_to_face(f)}   // globo_ON_{side}")
    for side in ('E', 'N', 'W', 'S'):
        f = k_max_face_quadrant(4, side, LAYER_ON, LAYER_PIA)
        out.append(f"            {tuple_to_face(f)}   // globo_pia_{side}")
    for side in ('E', 'N', 'W', 'S'):
        f = k_max_face_quadrant(4, side, LAYER_PIA, LAYER_SAS)
        out.append(f"            {tuple_to_face(f)}   // globo_sas_{side}")
    for side in ('E', 'N', 'W', 'S'):
        f = k_max_face_quadrant(4, side, LAYER_SAS, LAYER_DURA)
        out.append(f"            {tuple_to_face(f)}   // globo_dura_{side}")
    out.append("        );")
    out.append("    }")

    out.append(");")
    return "\n".join(out)


def tuple_to_face(t: tuple[int, int, int, int]) -> str:
    return f"( {t[0]:3d} {t[1]:3d} {t[2]:3d} {t[3]:3d} )"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    vs = build_vertices()
    assert len(vs) == len(Z_LEVELS) * N_LAYERS * 4, f"len(vs)={len(vs)}"

    out = []
    out.append(HEADER)
    out.append("")
    out.append(render_vertices(vs))
    out.append("")
    out.append(render_blocks())
    out.append("")
    out.append(render_edges())
    out.append("")
    out.append(render_boundary())
    out.append("")

    target = Path(__file__).resolve().parent.parent / "cases" / "on-mestrado-2" / "solid" / "system" / "blockMeshDict"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(out) + "\n")
    print(f"wrote {target}")
    print(f"  {len(vs)} vertices, {len(Z_LEVELS)} z-levels")
    # Contagem rapida de celulas
    total = 0
    for n_axial in N_AXIAL:
        center = N_RAD_CTR * N_TANG * n_axial
        on_quads = 4 * (N_RAD_ON  * N_TANG * n_axial)
        pia_quads = 4 * (N_RAD_PIA * N_TANG * n_axial)
        sas_quads = 4 * (N_RAD_SAS * N_TANG * n_axial)
        dura_quads = 4 * (N_RAD_DURA * N_TANG * n_axial)
        total += center + on_quads + pia_quads + sas_quads + dura_quads
    print(f"  cells (estimado): {total}")


if __name__ == "__main__":
    main()
