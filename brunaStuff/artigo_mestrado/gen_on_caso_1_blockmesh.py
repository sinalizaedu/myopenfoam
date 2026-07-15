"""Gerador unificado dos blockMeshDicts do caso on-caso-1 (FSI ONSAS com lid poroso).

Variante de gen_on_fsi_2_blockmesh.py:
  - SOLIDO: IDENTICO ao on-fsi-2 (mesma malha, mesmas 7 zonas, mesmas patches).
  - FLUIDO: estendido em z para incluir um LID POROSO de 0.5 mm em z=[30, 30.5].
            O lid e' um cellZone 'peri_porous' (alvo do fvOptions DarcyForchheimer).
            Patches do fluido:
              inlet            z=0,  r=1.55-2.35  fixedValue p=P_CSF (cisterna)
              fsi_pia          r=1.55, z=0-30     FSI conformal com solido
              fsi_dura         r=2.35, z=0-30     FSI conformal com solido
              lid_wall_inner   r=1.55, z=30-30.5  wall parado (pos-cribrosa rigida)
              lid_wall_outer   r=2.35, z=30-30.5  wall parado
              outlet_peri      z=30.5, r=1.55-2.35 fixedValue p=0 (referencia venosa)

            As patches fsi_sclera_peri e fsi_sclera_ring (que eram walls do
            cul-de-sac em on-fsi-2) deixam de existir no fluido: as faces em
            z=30 viram INTERNAS entre o SAS regular e o lid poroso.

Conformidade FSI:
  - fsi_pia e fsi_dura usam exatamente os mesmos vertices do solido nos
    niveis z=0 e z=30 (LAYER_PIA, LAYER_SAS_MID, LAYER_SAS).
  - O lid poroso adiciona um novo nivel z=30.5 (z_idx_fluid=2) exclusivamente
    para o fluido. O solido NAO ve esse nivel.

Materiais:
  Solid: 7 zonas (on, pia, dura, lc, sclera_peri, sclera_ring, globo).
  Fluid: 2 zonas:
    sas         - SAS regular z=[0, 30],   CSF water-like
    peri_porous - lid poroso  z=[30, 30.5], CSF + Darcy resistance (via fvOptions)

Uso:
    python brunaStuff/gen_on_caso_1_blockmesh.py
        -> escreve cases/on-caso-1/solid/system/blockMeshDict
        -> escreve cases/on-caso-1/fluid/system/blockMeshDict
"""

from __future__ import annotations

import math
from pathlib import Path

# ---------------------------------------------------------------------------
# Parametros geometricos (em mm; scale 0.001 aplicado pelo blockMesh)
# ---------------------------------------------------------------------------

R_SQUARE  = 0.75
R_ON      = 1.50
R_PIA     = 1.55
R_SAS_MID = 2.00
R_SAS     = 2.35
R_DURA    = 2.50

L_NERVE   = 30.00
T_LC      = 0.30
T_GLOBO   = 0.50
T_PERI_POROUS = 0.50    # espessura do lid poroso, em mm

# Niveis z do SOLIDO (igual ao on-fsi-2)
Z_LEVELS_SOLID = (0.0, L_NERVE, L_NERVE + T_LC, L_NERVE + T_LC + T_GLOBO)
N_AXIAL_SOLID  = (30, 1, 1)

# Niveis z do FLUIDO: SAS regular ate z=30, depois lid poroso ate z=30.5
Z_LEVELS_FLUID = (0.0, L_NERVE, L_NERVE + T_PERI_POROUS)
N_AXIAL_FLUID  = (30, 2)     # 30 ao longo do SAS, 2 ao longo do lid (0.25 mm/cell)

N_TANG       = 8
N_RAD_ON     = 6
N_RAD_CTR    = 8
N_RAD_PIA    = 1
N_RAD_SAS_IN  = 3
N_RAD_SAS_OUT = 3
N_RAD_DURA   = 2

CORNERS = ('NE', 'NW', 'SW', 'SE')

LAYER_SQUARE  = 0
LAYER_ON      = 1
LAYER_PIA     = 2
LAYER_SAS_MID = 3
LAYER_SAS     = 4
LAYER_DURA    = 5
N_LAYERS = 6


# ---------------------------------------------------------------------------
# Vertices: dois conjuntos independentes (solid e fluid), com x,y identicos
# para as layers PIA, SAS_MID, SAS nos niveis z=0 e z=30 garantindo
# conformidade FSI.
# ---------------------------------------------------------------------------

def diag_for_layer(layer: int) -> float:
    if layer == LAYER_SQUARE:  return R_SQUARE
    if layer == LAYER_ON:      return R_ON      / math.sqrt(2.0)
    if layer == LAYER_PIA:     return R_PIA     / math.sqrt(2.0)
    if layer == LAYER_SAS_MID: return R_SAS_MID / math.sqrt(2.0)
    if layer == LAYER_SAS:     return R_SAS     / math.sqrt(2.0)
    if layer == LAYER_DURA:    return R_DURA    / math.sqrt(2.0)
    raise ValueError(f"layer invalido: {layer}")


def corner_xy(corner: str, d: float) -> tuple[float, float]:
    if corner == 'NE': return ( d,  d)
    if corner == 'NW': return (-d,  d)
    if corner == 'SW': return (-d, -d)
    if corner == 'SE': return ( d, -d)
    raise ValueError(corner)


def vid_solid(z_idx: int, layer: int, corner_idx: int) -> int:
    return z_idx * (N_LAYERS * 4) + layer * 4 + corner_idx


def vid_fluid(z_idx: int, layer: int, corner_idx: int) -> int:
    return z_idx * (N_LAYERS * 4) + layer * 4 + corner_idx


def build_vertices(z_levels) -> list[tuple[float, float, float]]:
    vs = []
    for z in z_levels:
        for layer in range(N_LAYERS):
            d = diag_for_layer(layer)
            for c in CORNERS:
                x, y = corner_xy(c, d)
                vs.append((x, y, z))
    return vs


def radius_for_layer(layer: int) -> float:
    if layer == LAYER_ON:      return R_ON
    if layer == LAYER_PIA:     return R_PIA
    if layer == LAYER_SAS_MID: return R_SAS_MID
    if layer == LAYER_SAS:     return R_SAS
    if layer == LAYER_DURA:    return R_DURA
    raise ValueError(layer)


def arcs_for_circle(vid_fn, z_idx: int, z: float, layer: int):
    if layer == LAYER_SQUARE:
        return []
    r = radius_for_layer(layer)
    NE, NW, SW, SE = (vid_fn(z_idx, layer, i) for i in range(4))
    return [
        (NE, SE, ( r, 0.0, z)),
        (NE, NW, (0.0,  r, z)),
        (NW, SW, (-r, 0.0, z)),
        (SW, SE, (0.0, -r, z)),
    ]


# ---------------------------------------------------------------------------
# Block builders (genericos: recebem a funcao vid apropriada)
# ---------------------------------------------------------------------------

def quadrant_block(vid_fn, side: str, z_idx_lo: int, z_idx_hi: int,
                   layer_in: int, layer_out: int,
                   zone: str, n_radial: int, n_axial: int,
                   comment: str = "") -> str:
    if side == 'E': a, b = 'SE', 'NE'
    elif side == 'N': a, b = 'NE', 'NW'
    elif side == 'W': a, b = 'NW', 'SW'
    elif side == 'S': a, b = 'SW', 'SE'
    else: raise ValueError(side)

    ai = CORNERS.index(a); bi = CORNERS.index(b)
    v0 = vid_fn(z_idx_lo, layer_in,  ai)
    v1 = vid_fn(z_idx_lo, layer_out, ai)
    v2 = vid_fn(z_idx_lo, layer_out, bi)
    v3 = vid_fn(z_idx_lo, layer_in,  bi)
    v4 = vid_fn(z_idx_hi, layer_in,  ai)
    v5 = vid_fn(z_idx_hi, layer_out, ai)
    v6 = vid_fn(z_idx_hi, layer_out, bi)
    v7 = vid_fn(z_idx_hi, layer_in,  bi)

    return (
        f"    hex ( {v0:3d} {v1:3d} {v2:3d} {v3:3d}  "
        f"{v4:3d} {v5:3d} {v6:3d} {v7:3d} )  "
        f"{zone:12s} ( {n_radial} {N_TANG} {n_axial} )  "
        f"simpleGrading ( 1 1 1 )"
        + (f"  // {comment}" if comment else "")
    )


def center_block(vid_fn, z_idx_lo: int, z_idx_hi: int, zone: str, n_axial: int,
                 comment: str = "") -> str:
    NE, NW, SW, SE = (vid_fn(z_idx_lo, LAYER_SQUARE, i) for i in range(4))
    NEt, NWt, SWt, SEt = (vid_fn(z_idx_hi, LAYER_SQUARE, i) for i in range(4))
    return (
        f"    hex ( {NE:3d} {NW:3d} {SW:3d} {SE:3d}  "
        f"{NEt:3d} {NWt:3d} {SWt:3d} {SEt:3d} )  "
        f"{zone:12s} ( {N_RAD_CTR} {N_TANG} {n_axial} )  "
        f"simpleGrading ( 1 1 1 )"
        + (f"  // {comment}" if comment else "")
    )


# ---------------------------------------------------------------------------
# Face helpers
# ---------------------------------------------------------------------------

def k_min_face_quadrant(vid_fn, z_idx, side, layer_in, layer_out):
    if side == 'E': a, b = 'SE', 'NE'
    elif side == 'N': a, b = 'NE', 'NW'
    elif side == 'W': a, b = 'NW', 'SW'
    else: a, b = 'SW', 'SE'
    ai, bi = CORNERS.index(a), CORNERS.index(b)
    return (vid_fn(z_idx, layer_in, ai), vid_fn(z_idx, layer_out, ai),
            vid_fn(z_idx, layer_out, bi), vid_fn(z_idx, layer_in,  bi))


def k_max_face_quadrant(vid_fn, z_idx, side, layer_in, layer_out):
    return k_min_face_quadrant(vid_fn, z_idx, side, layer_in, layer_out)


def k_face_center(vid_fn, z_idx):
    return tuple(vid_fn(z_idx, LAYER_SQUARE, i) for i in range(4))


def i_max_face_quadrant(vid_fn, z_idx_lo, z_idx_hi, side, layer_in, layer_out):
    if side == 'E': a, b = 'SE', 'NE'
    elif side == 'N': a, b = 'NE', 'NW'
    elif side == 'W': a, b = 'NW', 'SW'
    else: a, b = 'SW', 'SE'
    ai, bi = CORNERS.index(a), CORNERS.index(b)
    v1 = vid_fn(z_idx_lo, layer_out, ai)
    v2 = vid_fn(z_idx_lo, layer_out, bi)
    v6 = vid_fn(z_idx_hi, layer_out, bi)
    v5 = vid_fn(z_idx_hi, layer_out, ai)
    return (v1, v2, v6, v5)


def i_min_face_quadrant(vid_fn, z_idx_lo, z_idx_hi, side, layer_in, layer_out):
    if side == 'E': a, b = 'SE', 'NE'
    elif side == 'N': a, b = 'NE', 'NW'
    elif side == 'W': a, b = 'NW', 'SW'
    else: a, b = 'SW', 'SE'
    ai, bi = CORNERS.index(a), CORNERS.index(b)
    v0 = vid_fn(z_idx_lo, layer_in, ai)
    v3 = vid_fn(z_idx_lo, layer_in, bi)
    v7 = vid_fn(z_idx_hi, layer_in, bi)
    v4 = vid_fn(z_idx_hi, layer_in, ai)
    return (v0, v3, v7, v4)


def tuple_to_face(t):
    return f"( {t[0]:3d} {t[1]:3d} {t[2]:3d} {t[3]:3d} )"


# ---------------------------------------------------------------------------
# Headers
# ---------------------------------------------------------------------------

HEADER_SOLID = """FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}

// on-caso-1 SOLIDO - identico ao on-fsi-2 (7 zonas, sem zona SAS).
// O anular r=1.55-2.35 esta vazio aqui (dominio fluido).
//
// Patches FSI conformes com o fluido (apenas 2 agora, fsi_pia e fsi_dura).
// As patches fsi_sclera_peri e fsi_sclera_ring continuam existindo no solido
// (z=30, r=1.55-2.35) mas NAO sao mais FSI: recebem BC livre (solidTraction
// pressure 0), pois o lid poroso do fluido absorve a carga distal.

scale   0.001;
"""

HEADER_FLUID = """FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}

// on-caso-1 FLUIDO - 2 zonas:
//   sas         - SAS regular z=[0, 30], 8 blocos hex (5760 cells), CSF
//   peri_porous - lid poroso  z=[30, 30.5], 8 blocos hex (384 cells), CSF + Darcy
//
// Patches:
//   inlet            z=0,    r=1.55-2.35  fixedValue p=P_CSF (cisterna)
//   fsi_pia          r=1.55, z=[0,30]     FSI conformal (preCICE + solid)
//   fsi_dura         r=2.35, z=[0,30]     FSI conformal
//   lid_wall_inner   r=1.55, z=[30,30.5]  wall parado (pos-cribrosa rigida)
//   lid_wall_outer   r=2.35, z=[30,30.5]  wall parado
//   outlet_peri      z=30.5, r=1.55-2.35  fixedValue p=0 (drenagem venosa)
//
// As faces em z=30 sao INTERNAS entre sas e peri_porous (continuidade).
// A indexacao de vertices: z_idx_fluid=0 (z=0), 1 (z=30), 2 (z=30.5).
// FSI conformity: vertices nas layers PIA, SAS_MID, SAS em z=0 e z=30 tem
// coordenadas identicas as do solido (mesmas formulas em diag_for_layer).

scale   0.001;
"""


# ---------------------------------------------------------------------------
# Render solid mesh (identico ao gen_on_fsi_2_blockmesh.py)
# ---------------------------------------------------------------------------

def render_vertices(vs):
    lines = ["vertices", "("]
    for i, (x, y, z) in enumerate(vs):
        lines.append(f"    ( {x:11.6f}  {y:11.6f}  {z:7.3f} )  // {i:3d}")
    lines.append(");")
    return "\n".join(lines)


def render_solid_blocks():
    out = ["blocks", "("]
    out.append("    // ===== z=0 a 30 mm: nervo + bainha (SEM SAS = vazio fluido) =====")
    out.append(center_block(vid_solid, 0, 1, "on", N_AXIAL_SOLID[0], "ON central"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(vid_solid, side, 0, 1, LAYER_SQUARE, LAYER_ON,
                                  "on", N_RAD_ON, N_AXIAL_SOLID[0], f"ON_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(vid_solid, side, 0, 1, LAYER_ON, LAYER_PIA,
                                  "pia", N_RAD_PIA, N_AXIAL_SOLID[0], f"pia_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(vid_solid, side, 0, 1, LAYER_SAS, LAYER_DURA,
                                  "dura", N_RAD_DURA, N_AXIAL_SOLID[0], f"dura_{side}"))

    out.append("")
    out.append("    // ===== z=30 a 30.30 mm: LC + sclera (peri + ring) =====")
    out.append(center_block(vid_solid, 1, 2, "lc", N_AXIAL_SOLID[1], "LC central"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(vid_solid, side, 1, 2, LAYER_SQUARE, LAYER_ON,
                                  "lc", N_RAD_ON, N_AXIAL_SOLID[1], f"LC_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(vid_solid, side, 1, 2, LAYER_ON, LAYER_PIA,
                                  "sclera_peri", N_RAD_PIA, N_AXIAL_SOLID[1], f"sclera_peri_pia_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(vid_solid, side, 1, 2, LAYER_PIA, LAYER_SAS_MID,
                                  "sclera_peri", N_RAD_SAS_IN, N_AXIAL_SOLID[1], f"sclera_peri_sasIn_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(vid_solid, side, 1, 2, LAYER_SAS_MID, LAYER_SAS,
                                  "sclera_ring", N_RAD_SAS_OUT, N_AXIAL_SOLID[1], f"sclera_ring_sasOut_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(vid_solid, side, 1, 2, LAYER_SAS, LAYER_DURA,
                                  "sclera_ring", N_RAD_DURA, N_AXIAL_SOLID[1], f"sclera_ring_dura_{side}"))

    out.append("")
    out.append("    // ===== z=30.30 a 30.80 mm: casca do globo =====")
    out.append(center_block(vid_solid, 2, 3, "globo", N_AXIAL_SOLID[2], "globo central"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(vid_solid, side, 2, 3, LAYER_SQUARE, LAYER_ON,
                                  "globo", N_RAD_ON, N_AXIAL_SOLID[2], f"globo_ON_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(vid_solid, side, 2, 3, LAYER_ON, LAYER_PIA,
                                  "globo", N_RAD_PIA, N_AXIAL_SOLID[2], f"globo_pia_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(vid_solid, side, 2, 3, LAYER_PIA, LAYER_SAS_MID,
                                  "globo", N_RAD_SAS_IN, N_AXIAL_SOLID[2], f"globo_sasIn_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(vid_solid, side, 2, 3, LAYER_SAS_MID, LAYER_SAS,
                                  "globo", N_RAD_SAS_OUT, N_AXIAL_SOLID[2], f"globo_sasOut_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(vid_solid, side, 2, 3, LAYER_SAS, LAYER_DURA,
                                  "globo", N_RAD_DURA, N_AXIAL_SOLID[2], f"globo_dura_{side}"))

    out.append(");")
    return "\n".join(out)


def render_fluid_blocks():
    """Fluido: 16 blocos.
       8 blocos SAS regular  z=[0, 30]    (zone 'sas')
       8 blocos lid poroso   z=[30, 30.5] (zone 'peri_porous')
    """
    out = ["blocks", "("]
    out.append("    // ===== SAS regular annulus z=0-30 (8 blocos: sas_in + sas_out) =====")
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(vid_fluid, side, 0, 1, LAYER_PIA, LAYER_SAS_MID,
                                  "sas", N_RAD_SAS_IN, N_AXIAL_FLUID[0], f"sas_in_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(vid_fluid, side, 0, 1, LAYER_SAS_MID, LAYER_SAS,
                                  "sas", N_RAD_SAS_OUT, N_AXIAL_FLUID[0], f"sas_out_{side}"))
    out.append("")
    out.append("    // ===== Peri-porous lid annulus z=30-30.5 (8 blocos, cellZone Darcy) =====")
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(vid_fluid, side, 1, 2, LAYER_PIA, LAYER_SAS_MID,
                                  "peri_porous", N_RAD_SAS_IN, N_AXIAL_FLUID[1], f"lid_in_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(vid_fluid, side, 1, 2, LAYER_SAS_MID, LAYER_SAS,
                                  "peri_porous", N_RAD_SAS_OUT, N_AXIAL_FLUID[1], f"lid_out_{side}"))
    out.append(");")
    return "\n".join(out)


def render_edges_solid():
    out = ["edges", "("]
    layer_radii = {
        LAYER_ON:      'ON      r=1.50',
        LAYER_PIA:     'pia     r=1.55',
        LAYER_SAS_MID: 'sas_mid r=2.00',
        LAYER_SAS:     'sas     r=2.35',
        LAYER_DURA:    'dura    r=2.50',
    }
    for z_idx, z in enumerate(Z_LEVELS_SOLID):
        for layer, label in layer_radii.items():
            if z_idx == 0 and layer == LAYER_SAS_MID:
                continue
            arcs = arcs_for_circle(vid_solid, z_idx, z, layer)
            out.append(f"    // ---- {label}  @ z={z:.3f} mm ----")
            for a, b, mid in arcs:
                out.append(f"    arc {a:3d} {b:3d}  ( {mid[0]:9.5f}  {mid[1]:9.5f}  {mid[2]:7.3f} )")
        out.append("")
    out.append(");")
    return "\n".join(out)


def render_edges_fluid():
    """Edges para z=0, z=30 e z=30.5 nas layers PIA, SAS_MID, SAS."""
    out = ["edges", "("]
    layer_radii = {
        LAYER_PIA:     'pia     r=1.55',
        LAYER_SAS_MID: 'sas_mid r=2.00',
        LAYER_SAS:     'sas     r=2.35',
    }
    for z_idx, z in enumerate(Z_LEVELS_FLUID):
        for layer, label in layer_radii.items():
            arcs = arcs_for_circle(vid_fluid, z_idx, z, layer)
            out.append(f"    // ---- {label}  @ z={z:.3f} mm ----")
            for a, b, mid in arcs:
                out.append(f"    arc {a:3d} {b:3d}  ( {mid[0]:9.5f}  {mid[1]:9.5f}  {mid[2]:7.3f} )")
        out.append("")
    out.append(");")
    return "\n".join(out)


def render_solid_boundary():
    out = ["boundary", "("]

    def block_section(name, faces, comments, ptype="wall"):
        out.append(f"    {name}")
        out.append("    {")
        out.append(f"        type {ptype};")
        out.append("        faces")
        out.append("        (")
        for f, c in zip(faces, comments):
            out.append(f"            {tuple_to_face(f)}   // {c}")
        out.append("        );")
        out.append("    }")
        out.append("")

    faces = [k_face_center(vid_solid, 0)]
    comments = ["ON central"]
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_min_face_quadrant(vid_solid, 0, side, LAYER_SQUARE, LAYER_ON))
        comments.append(f"ON_{side}")
    block_section("posterior_on", faces, comments)

    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_min_face_quadrant(vid_solid, 0, side, LAYER_ON, LAYER_PIA))
        comments.append(f"pia_{side}")
    block_section("posterior_pia", faces, comments)

    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_min_face_quadrant(vid_solid, 0, side, LAYER_SAS, LAYER_DURA))
        comments.append(f"dura_{side}")
    block_section("posterior_dura", faces, comments)

    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(i_max_face_quadrant(vid_solid, 0, 1, side, LAYER_SAS, LAYER_DURA))
        comments.append(f"dura_outer_{side}")
    block_section("dura_outer", faces, comments)

    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(i_max_face_quadrant(vid_solid, 1, 2, side, LAYER_SAS, LAYER_DURA))
        comments.append(f"sclera_ring_outer_{side}")
    block_section("sclera_ring_outer", faces, comments)

    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(i_max_face_quadrant(vid_solid, 2, 3, side, LAYER_SAS, LAYER_DURA))
        comments.append(f"globo_outer_{side}")
    block_section("globo_outer", faces, comments)

    faces = [k_face_center(vid_solid, 3)]
    comments = ["globo central"]
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_max_face_quadrant(vid_solid, 3, side, LAYER_SQUARE, LAYER_ON))
        comments.append(f"globo_ON_{side}")
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_max_face_quadrant(vid_solid, 3, side, LAYER_ON, LAYER_PIA))
        comments.append(f"globo_pia_{side}")
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_max_face_quadrant(vid_solid, 3, side, LAYER_PIA, LAYER_SAS_MID))
        comments.append(f"globo_sasIn_{side}")
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_max_face_quadrant(vid_solid, 3, side, LAYER_SAS_MID, LAYER_SAS))
        comments.append(f"globo_sasOut_{side}")
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_max_face_quadrant(vid_solid, 3, side, LAYER_SAS, LAYER_DURA))
        comments.append(f"globo_dura_{side}")
    block_section("anterior_globo", faces, comments)

    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(i_max_face_quadrant(vid_solid, 0, 1, side, LAYER_ON, LAYER_PIA))
        comments.append(f"fsi_pia_{side}")
    block_section("fsi_pia", faces, comments)

    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(i_min_face_quadrant(vid_solid, 0, 1, side, LAYER_SAS, LAYER_DURA))
        comments.append(f"fsi_dura_{side}")
    block_section("fsi_dura", faces, comments)

    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_min_face_quadrant(vid_solid, 1, side, LAYER_PIA, LAYER_SAS_MID))
        comments.append(f"fsi_sclera_peri_{side}")
    block_section("fsi_sclera_peri", faces, comments)

    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_min_face_quadrant(vid_solid, 1, side, LAYER_SAS_MID, LAYER_SAS))
        comments.append(f"fsi_sclera_ring_{side}")
    block_section("fsi_sclera_ring", faces, comments)

    out.append(");")
    return "\n".join(out)


def render_fluid_boundary():
    out = ["boundary", "("]

    def block_section(name, faces, comments, ptype="wall"):
        out.append(f"    {name}")
        out.append("    {")
        out.append(f"        type {ptype};")
        out.append("        faces")
        out.append("        (")
        for f, c in zip(faces, comments):
            out.append(f"            {tuple_to_face(f)}   // {c}")
        out.append("        );")
        out.append("    }")
        out.append("")

    # inlet: z=0, anel r=1.55-2.35 (sas_in + sas_out)
    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_min_face_quadrant(vid_fluid, 0, side, LAYER_PIA, LAYER_SAS_MID))
        comments.append(f"sas_in_{side}")
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_min_face_quadrant(vid_fluid, 0, side, LAYER_SAS_MID, LAYER_SAS))
        comments.append(f"sas_out_{side}")
    block_section("inlet", faces, comments, ptype="patch")

    # fsi_pia: r=1.55, z=[0, 30] (lateral interna do SAS regular, i_min)
    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(i_min_face_quadrant(vid_fluid, 0, 1, side, LAYER_PIA, LAYER_SAS_MID))
        comments.append(f"fsi_pia_{side}")
    block_section("fsi_pia", faces, comments)

    # fsi_dura: r=2.35, z=[0, 30] (lateral externa do SAS regular, i_max)
    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(i_max_face_quadrant(vid_fluid, 0, 1, side, LAYER_SAS_MID, LAYER_SAS))
        comments.append(f"fsi_dura_{side}")
    block_section("fsi_dura", faces, comments)

    # lid_wall_inner: r=1.55, z=[30, 30.5]
    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(i_min_face_quadrant(vid_fluid, 1, 2, side, LAYER_PIA, LAYER_SAS_MID))
        comments.append(f"lid_in_inner_{side}")
    block_section("lid_wall_inner", faces, comments)

    # lid_wall_outer: r=2.35, z=[30, 30.5]
    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(i_max_face_quadrant(vid_fluid, 1, 2, side, LAYER_SAS_MID, LAYER_SAS))
        comments.append(f"lid_out_outer_{side}")
    block_section("lid_wall_outer", faces, comments)

    # outlet_peri: z=30.5, anel r=1.55-2.35 (top dos blocos lid)
    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_max_face_quadrant(vid_fluid, 2, side, LAYER_PIA, LAYER_SAS_MID))
        comments.append(f"lid_in_top_{side}")
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_max_face_quadrant(vid_fluid, 2, side, LAYER_SAS_MID, LAYER_SAS))
        comments.append(f"lid_out_top_{side}")
    block_section("outlet_peri", faces, comments, ptype="patch")

    out.append(");")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    vs_solid = build_vertices(Z_LEVELS_SOLID)
    vs_fluid = build_vertices(Z_LEVELS_FLUID)
    assert len(vs_solid) == len(Z_LEVELS_SOLID) * N_LAYERS * 4 == 96
    assert len(vs_fluid) == len(Z_LEVELS_FLUID) * N_LAYERS * 4 == 72

    repo_root = Path(__file__).resolve().parent.parent
    case_root = repo_root / "cases" / "on-caso-1"

    out_solid = [HEADER_SOLID, ""]
    out_solid.append(render_vertices(vs_solid)); out_solid.append("")
    out_solid.append(render_solid_blocks()); out_solid.append("")
    out_solid.append(render_edges_solid()); out_solid.append("")
    out_solid.append(render_solid_boundary()); out_solid.append("")
    target_solid = case_root / "solid" / "system" / "blockMeshDict"
    target_solid.parent.mkdir(parents=True, exist_ok=True)
    target_solid.write_text("\n".join(out_solid) + "\n")
    print(f"wrote {target_solid}")

    out_fluid = [HEADER_FLUID, ""]
    out_fluid.append(render_vertices(vs_fluid)); out_fluid.append("")
    out_fluid.append(render_fluid_blocks()); out_fluid.append("")
    out_fluid.append(render_edges_fluid()); out_fluid.append("")
    out_fluid.append(render_fluid_boundary()); out_fluid.append("")
    target_fluid = case_root / "fluid" / "system" / "blockMeshDict"
    target_fluid.parent.mkdir(parents=True, exist_ok=True)
    target_fluid.write_text("\n".join(out_fluid) + "\n")
    print(f"wrote {target_fluid}")

    print()
    print(f"  SOLID  {len(vs_solid)} vertices  (z_levels = {Z_LEVELS_SOLID})")
    print(f"  FLUID  {len(vs_fluid)} vertices  (z_levels = {Z_LEVELS_FLUID})")
    print()

    total_solid = 0
    for ax_idx, n_axial in enumerate(N_AXIAL_SOLID):
        center = N_RAD_CTR * N_TANG * n_axial
        on_quads      = 4 * (N_RAD_ON      * N_TANG * n_axial)
        pia_quads     = 4 * (N_RAD_PIA     * N_TANG * n_axial)
        sas_in_quads  = 4 * (N_RAD_SAS_IN  * N_TANG * n_axial) if ax_idx != 0 else 0
        sas_out_quads = 4 * (N_RAD_SAS_OUT * N_TANG * n_axial) if ax_idx != 0 else 0
        dura_quads    = 4 * (N_RAD_DURA    * N_TANG * n_axial)
        per_layer = center + on_quads + pia_quads + sas_in_quads + sas_out_quads + dura_quads
        total_solid += per_layer
        print(f"  SOLID  axial layer {ax_idx} (n_axial={n_axial}): {per_layer} cells")
    print(f"  SOLID  total: {total_solid} cells")
    print()

    sas_in_cells   = 4 * N_RAD_SAS_IN  * N_TANG * N_AXIAL_FLUID[0]
    sas_out_cells  = 4 * N_RAD_SAS_OUT * N_TANG * N_AXIAL_FLUID[0]
    lid_in_cells   = 4 * N_RAD_SAS_IN  * N_TANG * N_AXIAL_FLUID[1]
    lid_out_cells  = 4 * N_RAD_SAS_OUT * N_TANG * N_AXIAL_FLUID[1]
    total_fluid = sas_in_cells + sas_out_cells + lid_in_cells + lid_out_cells
    print(f"  FLUID  sas_in:  {sas_in_cells} cells  (zone 'sas',         z=[0,30])")
    print(f"  FLUID  sas_out: {sas_out_cells} cells  (zone 'sas',         z=[0,30])")
    print(f"  FLUID  lid_in:  {lid_in_cells} cells   (zone 'peri_porous', z=[30,30.5])")
    print(f"  FLUID  lid_out: {lid_out_cells} cells   (zone 'peri_porous', z=[30,30.5])")
    print(f"  FLUID  total: {total_fluid} cells")


if __name__ == "__main__":
    main()
