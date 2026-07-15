"""Gerador do blockMeshDict do caso on-mestrado-2 ANATOMICO.

8 zonas + 4 niveis em z. BCs anatomicas: engaste total no canal optico (z=0),
ancoragem so no equador do globo, junções por continuidade nodal.

Geometria (mm; scale 0.001 aplicado pelo blockMesh):
    on          : r=0    -1.50, z=0     -30.00,   E=30  kPa
    pia         : r=1.50 -1.55, z=0     -30.00,   E=3   MPa
    sas         : r=1.55 -2.35, z=0     -30.00,   E=100 kPa  (split em r=2.0)
    dura        : r=2.35 -2.50, z=0     -30.00,   E=3   MPa
    lc          : r=0    -1.50, z=30.00 -30.30,   E=0.4 MPa  (lamina cribrosa)
    sclera_peri : r=1.50 -2.00, z=30.00 -30.30,   E=5   MPa  (peripapilar inner)
    sclera_ring : r=2.00 -2.50, z=30.00 -30.30,   E=5   MPa  (anel escleral outer)
    globo       : r=0    -2.50, z=30.30 -30.80,   E=5   MPa  (casca do globo)

Layers radiais (6, novo divisor em r=2.00):
    0 SQUARE  (corner=0.75)
    1 ON      (r=1.50)
    2 PIA     (r=1.55)
    3 SAS_MID (r=2.00)  <- NOVO, divide a SAS em duas e a sclera em peri/ring
    4 SAS     (r=2.35)
    5 DURA    (r=2.50)

Discretizacao radial: 1 cell pia, 3 cells sas_inner (r=1.55-2.00), 3 cells
sas_outer (r=2.00-2.35), 2 cells dura. Tangencial 8/quadrante. Axial:
30 celulas em z=0-30 (1 mm/cell), 1 celula em z=30-30.30 e em z=30.30-30.80.

Continuidade nodal: TODOS os blocos compartilham vertices em z=0,30,30.30,30.80.
Bonded por DOF (sem mergePatchPairs).

Patches (9 antes do topoSet+createPatch):
    posterior_on, posterior_pia, posterior_sas, posterior_dura  (z=0)
    dura_outer                                                  (lateral z=0-30)
    sclera_ring_outer                                           (lateral z=30-30.30)
    globo_outer                                                 (lateral z=30.30-30.80, EQUADOR)
    anterior_globo                                              (z=30.80)
    (contact_local sera carved-out de dura_outer via topoSet)

Uso:
    python brunaStuff/gen_on_mestrado_2_full.py
        -> escreve cases/on-mestrado-2/solid/system/blockMeshDict
"""

from __future__ import annotations

import math
from pathlib import Path

# ---------------------------------------------------------------------------
# Parametros geometricos (em mm; scale 0.001 aplicado pelo blockMesh)
# ---------------------------------------------------------------------------

R_SQUARE = 0.75
R_ON     = 1.50
R_PIA    = 1.55
R_SAS_MID = 2.00      # NOVO: divisor para split de sclera (peri/ring)
R_SAS    = 2.35
R_DURA   = 2.50

L_NERVE  = 30.00
T_LC     = 0.30       # espessura LC + sclera (lit. 0.28-0.30 mm)
T_GLOBO  = 0.50       # espessura casca do globo

Z_LEVELS = (0.0, L_NERVE, L_NERVE + T_LC, L_NERVE + T_LC + T_GLOBO)
N_AXIAL  = (30, 1, 1)            # nervo, sclera/lc, globo

N_TANG       = 8                 # tangenciais por quadrante
N_RAD_ON     = 6                 # square -> ON
N_RAD_CTR    = 8                 # quadrado central
N_RAD_PIA    = 1                 # ON -> pia
N_RAD_SAS_IN  = 3                # pia -> sas_mid
N_RAD_SAS_OUT = 3                # sas_mid -> sas
N_RAD_DURA   = 2                 # sas -> dura

CORNERS = ('NE', 'NW', 'SW', 'SE')

# Indice das camadas radiais
LAYER_SQUARE  = 0
LAYER_ON      = 1
LAYER_PIA     = 2
LAYER_SAS_MID = 3
LAYER_SAS     = 4
LAYER_DURA    = 5
N_LAYERS = 6


# ---------------------------------------------------------------------------
# Vertices
# ---------------------------------------------------------------------------

def diag_for_layer(layer: int) -> float:
    """Distancia diagonal (corner) para a camada radial em mm."""
    if layer == LAYER_SQUARE:  return R_SQUARE
    if layer == LAYER_ON:      return R_ON     / math.sqrt(2.0)
    if layer == LAYER_PIA:     return R_PIA    / math.sqrt(2.0)
    if layer == LAYER_SAS_MID: return R_SAS_MID / math.sqrt(2.0)
    if layer == LAYER_SAS:     return R_SAS    / math.sqrt(2.0)
    if layer == LAYER_DURA:    return R_DURA   / math.sqrt(2.0)
    raise ValueError(f"layer invalido: {layer}")


def corner_xy(corner: str, d: float) -> tuple[float, float]:
    if corner == 'NE': return ( d,  d)
    if corner == 'NW': return (-d,  d)
    if corner == 'SW': return (-d, -d)
    if corner == 'SE': return ( d, -d)
    raise ValueError(corner)


def vid(z_idx: int, layer: int, corner_idx: int) -> int:
    return z_idx * (N_LAYERS * 4) + layer * 4 + corner_idx


def build_vertices() -> list[tuple[float, float, float]]:
    vs = []
    for z_idx, z in enumerate(Z_LEVELS):
        for layer in range(N_LAYERS):
            d = diag_for_layer(layer)
            for c_idx, c in enumerate(CORNERS):
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


def arcs_for_circle(z_idx: int, z: float, layer: int):
    if layer == LAYER_SQUARE:
        return []
    r = radius_for_layer(layer)
    NE, NW, SW, SE = (vid(z_idx, layer, i) for i in range(4))
    return [
        (NE, SE, ( r, 0.0, z)),
        (NE, NW, (0.0,  r, z)),
        (NW, SW, (-r, 0.0, z)),
        (SW, SE, (0.0, -r, z)),
    ]


# ---------------------------------------------------------------------------
# Blocks
# ---------------------------------------------------------------------------

def quadrant_block(side: str, z_idx_lo: int, z_idx_hi: int,
                   layer_in: int, layer_out: int,
                   zone: str, n_radial: int, n_axial: int,
                   comment: str = "") -> str:
    if side == 'E': a, b = 'SE', 'NE'
    elif side == 'N': a, b = 'NE', 'NW'
    elif side == 'W': a, b = 'NW', 'SW'
    elif side == 'S': a, b = 'SW', 'SE'
    else: raise ValueError(side)

    ai = CORNERS.index(a); bi = CORNERS.index(b)
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
        f"{zone:12s} ( {n_radial} {N_TANG} {n_axial} )  "
        f"simpleGrading ( 1 1 1 )"
        + (f"  // {comment}" if comment else "")
    )


def center_block(z_idx_lo: int, z_idx_hi: int, zone: str, n_axial: int,
                 comment: str = "") -> str:
    NE, NW, SW, SE = (vid(z_idx_lo, LAYER_SQUARE, i) for i in range(4))
    NEt, NWt, SWt, SEt = (vid(z_idx_hi, LAYER_SQUARE, i) for i in range(4))
    return (
        f"    hex ( {NE:3d} {NW:3d} {SW:3d} {SE:3d}  "
        f"{NEt:3d} {NWt:3d} {SWt:3d} {SEt:3d} )  "
        f"{zone:12s} ( {N_RAD_CTR} {N_TANG} {n_axial} )  "
        f"simpleGrading ( 1 1 1 )"
        + (f"  // {comment}" if comment else "")
    )


# ---------------------------------------------------------------------------
# Faces (helpers para boundary)
# ---------------------------------------------------------------------------

def k_min_face_quadrant(z_idx, side, layer_in, layer_out):
    if side == 'E': a, b = 'SE', 'NE'
    elif side == 'N': a, b = 'NE', 'NW'
    elif side == 'W': a, b = 'NW', 'SW'
    else: a, b = 'SW', 'SE'
    ai, bi = CORNERS.index(a), CORNERS.index(b)
    return (vid(z_idx, layer_in, ai), vid(z_idx, layer_out, ai),
            vid(z_idx, layer_out, bi), vid(z_idx, layer_in,  bi))


def k_max_face_quadrant(z_idx, side, layer_in, layer_out):
    return k_min_face_quadrant(z_idx, side, layer_in, layer_out)


def k_face_center(z_idx):
    return tuple(vid(z_idx, LAYER_SQUARE, i) for i in range(4))


def i_max_face_quadrant(z_idx_lo, z_idx_hi, side, layer_in, layer_out):
    if side == 'E': a, b = 'SE', 'NE'
    elif side == 'N': a, b = 'NE', 'NW'
    elif side == 'W': a, b = 'NW', 'SW'
    else: a, b = 'SW', 'SE'
    ai, bi = CORNERS.index(a), CORNERS.index(b)
    v1 = vid(z_idx_lo, layer_out, ai)
    v2 = vid(z_idx_lo, layer_out, bi)
    v6 = vid(z_idx_hi, layer_out, bi)
    v5 = vid(z_idx_hi, layer_out, ai)
    return (v1, v2, v6, v5)


def tuple_to_face(t):
    return f"( {t[0]:3d} {t[1]:3d} {t[2]:3d} {t[3]:3d} )"


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

HEADER = """FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}

// on-mestrado-2 ANATOMICO - 8 zonas (4 nervo/bainha + LC + 2 sub-zonas sclera + globo).
//
// Geometria (scale 0.001 -> mm; gerado por brunaStuff/gen_on_mestrado_2_full.py):
//   on          : r=0    -1.50, z=0     -30.00   (E=30  kPa)
//   pia         : r=1.50 -1.55, z=0     -30.00   (E=3   MPa)
//   sas         : r=1.55 -2.35, z=0     -30.00   (E=100 kPa) split @ r=2.00
//   dura        : r=2.35 -2.50, z=0     -30.00   (E=3   MPa)
//   lc          : r=0    -1.50, z=30.00 -30.30   (E=0.4 MPa)  lamina cribrosa
//   sclera_peri : r=1.50 -2.00, z=30.00 -30.30   (E=5   MPa)  peripapilar
//   sclera_ring : r=2.00 -2.50, z=30.00 -30.30   (E=5   MPa)  anel escleral
//   globo       : r=0    -2.50, z=30.30 -30.80   (E=5   MPa)  casca do globo
//
// Continuidade nodal: blocos compartilham vertices em z=0, 30, 30.30, 30.80.
// Bonded por DOF (sem mergePatchPairs).
//
// Patches (9 antes do topoSet+createPatch):
//   posterior_on    -> z=0, r=0-1.50    (canal optico, fixedDisplacement)
//   posterior_pia   -> z=0, r=1.50-1.55 (canal optico, fixedDisplacement)
//   posterior_sas   -> z=0, r=1.55-2.35 (canal optico, fixedDisplacement)
//   posterior_dura  -> z=0, r=2.35-2.50 (canal optico, fixedDisplacement)
//   dura_outer      -> r=2.50, z=0-30   (Winkler 200 kPa/m)  contact_local sai daqui
//   sclera_ring_outer -> r=2.50, z=30-30.30 (livre, transicao p/ globo)
//   globo_outer     -> r=2.50, z=30.30-30.80 (EQUADOR, fixedDisplacement)
//   anterior_globo  -> z=30.80           (livre, lado vitreo sem IOP)
//
// Continuidade no plano z=30 (nervo<->LC/sclera) e z=30.30 (sclera<->globo) e
// no plano z=0 entre as 4 zonas posteriores: tudo via vertices compartilhados.

scale   0.001;
"""


def render_vertices(vs):
    lines = ["vertices", "("]
    for i, (x, y, z) in enumerate(vs):
        lines.append(f"    ( {x:11.6f}  {y:11.6f}  {z:7.3f} )  // {i:3d}")
    lines.append(");")
    return "\n".join(lines)


def render_blocks():
    out = ["blocks", "("]

    # ---- z=0 a 30 mm: nervo + bainha (4 zonas mecanicas, 6 layers radiais)
    out.append("    // ===== z=0 a 30 mm: nervo + bainha =====")
    out.append(center_block(0, 1, "on", N_AXIAL[0], "ON central"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 0, 1, LAYER_SQUARE, LAYER_ON,
                                  "on", N_RAD_ON, N_AXIAL[0], f"ON_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 0, 1, LAYER_ON, LAYER_PIA,
                                  "pia", N_RAD_PIA, N_AXIAL[0], f"pia_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 0, 1, LAYER_PIA, LAYER_SAS_MID,
                                  "sas", N_RAD_SAS_IN, N_AXIAL[0], f"sas_in_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 0, 1, LAYER_SAS_MID, LAYER_SAS,
                                  "sas", N_RAD_SAS_OUT, N_AXIAL[0], f"sas_out_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 0, 1, LAYER_SAS, LAYER_DURA,
                                  "dura", N_RAD_DURA, N_AXIAL[0], f"dura_{side}"))

    # ---- z=30 a 30.30 mm: LC + sclera_peri + sclera_ring -----------------
    out.append("")
    out.append("    // ===== z=30 a 30.30 mm: LC + sclera (peri + ring) =====")
    out.append(center_block(1, 2, "lc", N_AXIAL[1], "LC central"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 1, 2, LAYER_SQUARE, LAYER_ON,
                                  "lc", N_RAD_ON, N_AXIAL[1], f"LC_{side}"))
    # sclera_peri: r=1.50-2.00 (atravessa pia layer e sas_inner layer)
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 1, 2, LAYER_ON, LAYER_PIA,
                                  "sclera_peri", N_RAD_PIA, N_AXIAL[1], f"sclera_peri_pia_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 1, 2, LAYER_PIA, LAYER_SAS_MID,
                                  "sclera_peri", N_RAD_SAS_IN, N_AXIAL[1], f"sclera_peri_sasIn_{side}"))
    # sclera_ring: r=2.00-2.50 (atravessa sas_outer layer e dura layer)
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 1, 2, LAYER_SAS_MID, LAYER_SAS,
                                  "sclera_ring", N_RAD_SAS_OUT, N_AXIAL[1], f"sclera_ring_sasOut_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 1, 2, LAYER_SAS, LAYER_DURA,
                                  "sclera_ring", N_RAD_DURA, N_AXIAL[1], f"sclera_ring_dura_{side}"))

    # ---- z=30.30 a 30.80 mm: globo (1 zona, malha completa) --------------
    out.append("")
    out.append("    // ===== z=30.30 a 30.80 mm: casca do globo =====")
    out.append(center_block(2, 3, "globo", N_AXIAL[2], "globo central"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 2, 3, LAYER_SQUARE, LAYER_ON,
                                  "globo", N_RAD_ON, N_AXIAL[2], f"globo_ON_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 2, 3, LAYER_ON, LAYER_PIA,
                                  "globo", N_RAD_PIA, N_AXIAL[2], f"globo_pia_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 2, 3, LAYER_PIA, LAYER_SAS_MID,
                                  "globo", N_RAD_SAS_IN, N_AXIAL[2], f"globo_sasIn_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 2, 3, LAYER_SAS_MID, LAYER_SAS,
                                  "globo", N_RAD_SAS_OUT, N_AXIAL[2], f"globo_sasOut_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 2, 3, LAYER_SAS, LAYER_DURA,
                                  "globo", N_RAD_DURA, N_AXIAL[2], f"globo_dura_{side}"))

    out.append(");")
    return "\n".join(out)


def render_edges():
    out = ["edges", "("]
    layer_radii = {
        LAYER_ON:      'ON      r=1.50',
        LAYER_PIA:     'pia     r=1.55',
        LAYER_SAS_MID: 'sas_mid r=2.00',
        LAYER_SAS:     'sas     r=2.35',
        LAYER_DURA:    'dura    r=2.50',
    }
    for z_idx, z in enumerate(Z_LEVELS):
        for layer, label in layer_radii.items():
            arcs = arcs_for_circle(z_idx, z, layer)
            out.append(f"    // ---- {label}  @ z={z:.3f} mm ----")
            for a, b, mid in arcs:
                out.append(f"    arc {a:3d} {b:3d}  ( {mid[0]:9.5f}  {mid[1]:9.5f}  {mid[2]:7.3f} )")
        out.append("")
    out.append(");")
    return "\n".join(out)


def render_boundary():
    out = ["boundary", "("]

    def block_section(name, faces, comments):
        out.append(f"    {name}")
        out.append("    {")
        out.append("        type wall;")
        out.append("        faces")
        out.append("        (")
        for f, c in zip(faces, comments):
            out.append(f"            {tuple_to_face(f)}   // {c}")
        out.append("        );")
        out.append("    }")
        out.append("")

    # ----- posterior_on (z=0, central + 4 ON quads) -----------------------
    faces = [k_face_center(0)]
    comments = ["ON central"]
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_min_face_quadrant(0, side, LAYER_SQUARE, LAYER_ON))
        comments.append(f"ON_{side}")
    block_section("posterior_on", faces, comments)

    # ----- posterior_pia (z=0, 4 pia quads) -------------------------------
    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_min_face_quadrant(0, side, LAYER_ON, LAYER_PIA))
        comments.append(f"pia_{side}")
    block_section("posterior_pia", faces, comments)

    # ----- posterior_sas (z=0, sas_inner + sas_outer quads) ---------------
    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_min_face_quadrant(0, side, LAYER_PIA, LAYER_SAS_MID))
        comments.append(f"sas_in_{side}")
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_min_face_quadrant(0, side, LAYER_SAS_MID, LAYER_SAS))
        comments.append(f"sas_out_{side}")
    block_section("posterior_sas", faces, comments)

    # ----- posterior_dura (z=0, 4 dura quads) -----------------------------
    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_min_face_quadrant(0, side, LAYER_SAS, LAYER_DURA))
        comments.append(f"dura_{side}")
    block_section("posterior_dura", faces, comments)

    # ----- dura_outer (lateral z=0-30, todos os 4 dura quadrantes) --------
    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(i_max_face_quadrant(0, 1, side, LAYER_SAS, LAYER_DURA))
        comments.append(f"dura_outer_{side}")
    block_section("dura_outer", faces, comments)

    # ----- sclera_ring_outer (lateral z=30-30.30) -------------------------
    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(i_max_face_quadrant(1, 2, side, LAYER_SAS, LAYER_DURA))
        comments.append(f"sclera_ring_outer_{side}")
    block_section("sclera_ring_outer", faces, comments)

    # ----- globo_outer (lateral z=30.30-30.80, EQUADOR) -------------------
    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(i_max_face_quadrant(2, 3, side, LAYER_SAS, LAYER_DURA))
        comments.append(f"globo_outer_{side}")
    block_section("globo_outer", faces, comments)

    # ----- anterior_globo (z=30.80, todas as faces do globo) --------------
    faces = [k_face_center(3)]
    comments = ["globo central"]
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_max_face_quadrant(3, side, LAYER_SQUARE, LAYER_ON))
        comments.append(f"globo_ON_{side}")
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_max_face_quadrant(3, side, LAYER_ON, LAYER_PIA))
        comments.append(f"globo_pia_{side}")
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_max_face_quadrant(3, side, LAYER_PIA, LAYER_SAS_MID))
        comments.append(f"globo_sasIn_{side}")
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_max_face_quadrant(3, side, LAYER_SAS_MID, LAYER_SAS))
        comments.append(f"globo_sasOut_{side}")
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_max_face_quadrant(3, side, LAYER_SAS, LAYER_DURA))
        comments.append(f"globo_dura_{side}")
    block_section("anterior_globo", faces, comments)

    out.append(");")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    vs = build_vertices()
    expected_n_verts = len(Z_LEVELS) * N_LAYERS * 4
    assert len(vs) == expected_n_verts, f"len(vs)={len(vs)} != {expected_n_verts}"

    out = [HEADER, ""]
    out.append(render_vertices(vs)); out.append("")
    out.append(render_blocks());      out.append("")
    out.append(render_edges());       out.append("")
    out.append(render_boundary());    out.append("")

    target = Path(__file__).resolve().parent.parent / "cases" / "on-mestrado-2" / "solid" / "system" / "blockMeshDict"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(out) + "\n")
    print(f"wrote {target}")
    print(f"  {len(vs)} vertices, {len(Z_LEVELS)} z-levels (z = {Z_LEVELS})")
    # contagem de celulas
    total = 0
    for ax_idx, n_axial in enumerate(N_AXIAL):
        center = N_RAD_CTR * N_TANG * n_axial
        on_quads      = 4 * (N_RAD_ON      * N_TANG * n_axial)
        pia_quads     = 4 * (N_RAD_PIA     * N_TANG * n_axial)
        sas_in_quads  = 4 * (N_RAD_SAS_IN  * N_TANG * n_axial)
        sas_out_quads = 4 * (N_RAD_SAS_OUT * N_TANG * n_axial)
        dura_quads    = 4 * (N_RAD_DURA    * N_TANG * n_axial)
        per_layer = center + on_quads + pia_quads + sas_in_quads + sas_out_quads + dura_quads
        total += per_layer
        print(f"  axial layer {ax_idx} (n_axial={n_axial}): {per_layer} cells")
    print(f"  cells total (estimado): {total}")


if __name__ == "__main__":
    main()
