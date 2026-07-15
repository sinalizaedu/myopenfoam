"""Gerador unificado dos blockMeshDicts do caso on-fsi-2 (FSI two-way LCR).

Espelha gen_on_mestrado_2_full.py mas:
  - SOLIDO: mesma geometria, MAS sem os 8 blocos sas_in/sas_out.
            8 patches "antigos" + 4 NOVOS patches FSI (na fronteira que era
            interna entre SAS e os outros solidos):
              fsi_pia          - r=1.55, z=0-30   (lateral, 4 quadrantes)
              fsi_dura         - r=2.35, z=0-30   (lateral, 4 quadrantes)
              fsi_sclera_peri  - z=30, r=1.55-2.00 (top da sclera_peri inner)
              fsi_sclera_ring  - z=30, r=2.00-2.35 (top da sclera_ring inner)
              posterior_sas REMOVIDO (a face z=0 r=1.55-2.35 agora pertence
              ao fluido como inlet do LCR).
  - FLUIDO: APENAS os 8 blocos sas_in/sas_out, com 5 patches:
              fsi_pia          - r=1.55  (face interna do anular, encosta no solido)
              fsi_dura         - r=2.35  (face externa do anular)
              fsi_sclera_peri  - z=30 r=1.55-2.00 (tampa peripapilar inner)
              fsi_sclera_ring  - z=30 r=2.00-2.35 (tampa peripapilar outer)
              inlet            - z=0 r=1.55-2.35 (entrada do LCR cisterna)

Os vertices das interfaces FSI (3 layers radiais: PIA, SAS_MID, SAS) sao
posicionados nas mesmas coordenadas em ambas as malhas - a malha e' CONFORME.
Permite mapeamento nearest-projection no preCICE (preserva area sem RBF).

Materiais:
  Solid: 7 zonas (on, pia, dura, lc, sclera_peri, sclera_ring, globo).
         A zona 'sas' do on-mestrado-2 deixa de existir como solido.
  Fluid: 1 zona (sas) com rho=1000 kg/m^3, nu=1e-6 m^2/s (CSF water-like).

Uso:
    python brunaStuff/gen_on_fsi_2_blockmesh.py
        -> escreve cases/on-fsi-2/solid/system/blockMeshDict
        -> escreve cases/on-fsi-2/fluid/system/blockMeshDict
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
R_SAS_MID = 2.00       # divisor SAS_inner/SAS_outer e sclera_peri/sclera_ring
R_SAS     = 2.35
R_DURA    = 2.50

L_NERVE   = 30.00
T_LC      = 0.30
T_GLOBO   = 0.50

Z_LEVELS = (0.0, L_NERVE, L_NERVE + T_LC, L_NERVE + T_LC + T_GLOBO)
N_AXIAL  = (30, 1, 1)

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
# Vertices (mesma indexacao para solid e fluid; conformidade nas interfaces)
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
# Block builders
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
# Face helpers
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
    """Face radial externa (r=layer_out)."""
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


def i_min_face_quadrant(z_idx_lo, z_idx_hi, side, layer_in, layer_out):
    """Face radial interna (r=layer_in)."""
    if side == 'E': a, b = 'SE', 'NE'
    elif side == 'N': a, b = 'NE', 'NW'
    elif side == 'W': a, b = 'NW', 'SW'
    else: a, b = 'SW', 'SE'
    ai, bi = CORNERS.index(a), CORNERS.index(b)
    v0 = vid(z_idx_lo, layer_in, ai)
    v3 = vid(z_idx_lo, layer_in, bi)
    v7 = vid(z_idx_hi, layer_in, bi)
    v4 = vid(z_idx_hi, layer_in, ai)
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

// on-fsi-2 SOLIDO - 7 zonas (on, pia, dura, lc, sclera_peri, sclera_ring, globo).
// Sem zona SAS: o anular r=1.55-2.35 esta vazio aqui (e' o dominio fluido).
//
// Patches solidos:
//   Antigos (sao do on-mestrado-2):
//     posterior_on        z=0, r=0-1.50    fixedDisplacement (canal optico)
//     posterior_pia       z=0, r=1.50-1.55 fixedDisplacement
//     posterior_dura      z=0, r=2.35-2.50 fixedDisplacement
//     dura_outer          r=2.50, z=0-30   Winkler 200 kPa/m (gordura orbital)
//     sclera_ring_outer   r=2.50, z=30-30.30 livre
//     globo_outer         r=2.50, z=30.30-30.80 fixedDisplacement (EQUADOR)
//     anterior_globo      z=30.80          livre (lado vitreo)
//   Novos (FSI - antes eram faces internas vs SAS solido):
//     fsi_pia             r=1.55, z=0-30   solidForce (preCICE, do fluido)
//     fsi_dura            r=2.35, z=0-30   solidForce
//     fsi_sclera_peri     z=30, r=1.55-2.00 solidForce (tampa peripapilar inner)
//     fsi_sclera_ring     z=30, r=2.00-2.35 solidForce (tampa peripapilar outer)
//
// O contact_local sera carved-out de dura_outer via topoSet+createPatch
// (mesma logica do on-mestrado-2, em z=22.5mm eixo +X).

scale   0.001;
"""

HEADER_FLUID = """FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}

// on-fsi-2 FLUIDO - 1 zona (CSF water-like, rho=1000, nu=1e-6).
// Anular do SAS r=1.55-2.35 mm, z=0-30 mm. 8 blocos hex (sas_in + sas_out).
// 5 patches:
//   inlet              z=0,  r=1.55-2.35  pressao P_CSF=1333 Pa (cisterna quiasmatica)
//   fsi_pia            r=1.55, z=0-30     noSlip movingWallVelocity (encosta na pia)
//   fsi_dura           r=2.35, z=0-30     noSlip movingWallVelocity (encosta na dura)
//   fsi_sclera_peri    z=30, r=1.55-2.00  noSlip movingWallVelocity (tampa peri)
//   fsi_sclera_ring    z=30, r=2.00-2.35  noSlip movingWallVelocity (tampa ring)
//
// Mesma indexacao de vertices do solid (4 z-levels, 6 layers) garantindo
// conformidade de malha nas 4 interfaces FSI.

scale   0.001;
"""


# ---------------------------------------------------------------------------
# Render solid mesh
# ---------------------------------------------------------------------------

def render_vertices(vs):
    lines = ["vertices", "("]
    for i, (x, y, z) in enumerate(vs):
        lines.append(f"    ( {x:11.6f}  {y:11.6f}  {z:7.3f} )  // {i:3d}")
    lines.append(");")
    return "\n".join(lines)


def render_solid_blocks():
    out = ["blocks", "("]

    # ---- z=0-30 mm: nervo + bainha (sem SAS) -----------------------------
    out.append("    // ===== z=0 a 30 mm: nervo + bainha (SEM SAS = vazio fluido) =====")
    out.append(center_block(0, 1, "on", N_AXIAL[0], "ON central"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 0, 1, LAYER_SQUARE, LAYER_ON,
                                  "on", N_RAD_ON, N_AXIAL[0], f"ON_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 0, 1, LAYER_ON, LAYER_PIA,
                                  "pia", N_RAD_PIA, N_AXIAL[0], f"pia_{side}"))
    # Bloco SAS_in/out OMITIDOS (agora pertencem ao fluido).
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
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 1, 2, LAYER_ON, LAYER_PIA,
                                  "sclera_peri", N_RAD_PIA, N_AXIAL[1], f"sclera_peri_pia_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 1, 2, LAYER_PIA, LAYER_SAS_MID,
                                  "sclera_peri", N_RAD_SAS_IN, N_AXIAL[1], f"sclera_peri_sasIn_{side}"))
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


def render_fluid_blocks():
    out = ["blocks", "("]
    out.append("    // ===== SAS annulus z=0-30 (8 blocos: sas_in + sas_out) =====")
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 0, 1, LAYER_PIA, LAYER_SAS_MID,
                                  "sas", N_RAD_SAS_IN, N_AXIAL[0], f"sas_in_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 0, 1, LAYER_SAS_MID, LAYER_SAS,
                                  "sas", N_RAD_SAS_OUT, N_AXIAL[0], f"sas_out_{side}"))
    out.append(");")
    return "\n".join(out)


def render_edges_solid():
    """Edges para o solid. Skipa SAS_MID em z=0 porque os blocos SAS_in/out
    foram dropados; SAS_MID em z=30 ainda e' usado pela sclera_peri inner."""
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
            # SAS_MID em z=0 (z_idx=0) eh orphaned no solid (so blocos SAS o usavam)
            if z_idx == 0 and layer == LAYER_SAS_MID:
                continue
            arcs = arcs_for_circle(z_idx, z, layer)
            out.append(f"    // ---- {label}  @ z={z:.3f} mm ----")
            for a, b, mid in arcs:
                out.append(f"    arc {a:3d} {b:3d}  ( {mid[0]:9.5f}  {mid[1]:9.5f}  {mid[2]:7.3f} )")
        out.append("")
    out.append(");")
    return "\n".join(out)


def render_edges_fluid():
    """Edges para apenas os z=0 e z=30 nas layers PIA, SAS_MID, SAS (3 circulos)."""
    out = ["edges", "("]
    layer_radii = {
        LAYER_PIA:     'pia     r=1.55',
        LAYER_SAS_MID: 'sas_mid r=2.00',
        LAYER_SAS:     'sas     r=2.35',
    }
    for z_idx in (0, 1):  # apenas z=0 e z=30
        z = Z_LEVELS[z_idx]
        for layer, label in layer_radii.items():
            arcs = arcs_for_circle(z_idx, z, layer)
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

    # ----- posterior_on -----
    faces = [k_face_center(0)]
    comments = ["ON central"]
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_min_face_quadrant(0, side, LAYER_SQUARE, LAYER_ON))
        comments.append(f"ON_{side}")
    block_section("posterior_on", faces, comments)

    # ----- posterior_pia -----
    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_min_face_quadrant(0, side, LAYER_ON, LAYER_PIA))
        comments.append(f"pia_{side}")
    block_section("posterior_pia", faces, comments)

    # posterior_sas REMOVIDO (face z=0 r=1.55-2.35 nao existe mais no solido)

    # ----- posterior_dura -----
    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_min_face_quadrant(0, side, LAYER_SAS, LAYER_DURA))
        comments.append(f"dura_{side}")
    block_section("posterior_dura", faces, comments)

    # ----- dura_outer (lateral z=0-30) -----
    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(i_max_face_quadrant(0, 1, side, LAYER_SAS, LAYER_DURA))
        comments.append(f"dura_outer_{side}")
    block_section("dura_outer", faces, comments)

    # ----- sclera_ring_outer -----
    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(i_max_face_quadrant(1, 2, side, LAYER_SAS, LAYER_DURA))
        comments.append(f"sclera_ring_outer_{side}")
    block_section("sclera_ring_outer", faces, comments)

    # ----- globo_outer -----
    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(i_max_face_quadrant(2, 3, side, LAYER_SAS, LAYER_DURA))
        comments.append(f"globo_outer_{side}")
    block_section("globo_outer", faces, comments)

    # ----- anterior_globo -----
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

    # ----- fsi_pia (lateral interna do anel da pia, r=1.55, z=0-30) -------
    # Esta face e' a face EXTERNA do bloco pia (i_max), do ponto de vista
    # do solido. Recebe Force do fluido.
    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(i_max_face_quadrant(0, 1, side, LAYER_ON, LAYER_PIA))
        comments.append(f"fsi_pia_{side}")
    block_section("fsi_pia", faces, comments)

    # ----- fsi_dura (lateral interna do anel da dura, r=2.35, z=0-30) -----
    # Face INTERNA do bloco dura (i_min).
    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(i_min_face_quadrant(0, 1, side, LAYER_SAS, LAYER_DURA))
        comments.append(f"fsi_dura_{side}")
    block_section("fsi_dura", faces, comments)

    # ----- fsi_sclera_peri (z=30, r=1.55-2.00, bottom da sclera_peri inner)
    # Face INFERIOR (k_min em z_idx=1) dos blocos sclera_peri_sasIn.
    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_min_face_quadrant(1, side, LAYER_PIA, LAYER_SAS_MID))
        comments.append(f"fsi_sclera_peri_{side}")
    block_section("fsi_sclera_peri", faces, comments)

    # ----- fsi_sclera_ring (z=30, r=2.00-2.35, bottom da sclera_ring inner)
    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_min_face_quadrant(1, side, LAYER_SAS_MID, LAYER_SAS))
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

    # ----- inlet (z=0 r=1.55-2.35, 8 quadrantes sas_in + sas_out) -----
    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_min_face_quadrant(0, side, LAYER_PIA, LAYER_SAS_MID))
        comments.append(f"sas_in_{side}")
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_min_face_quadrant(0, side, LAYER_SAS_MID, LAYER_SAS))
        comments.append(f"sas_out_{side}")
    block_section("inlet", faces, comments, ptype="patch")

    # ----- fsi_pia (r=1.55, z=0-30, face INTERNA do anular sas_in: i_min)
    # Do ponto de vista do fluido, esta e' a parede inner (encosta na pia
    # externa do solido). Conforme com fsi_pia do solido (mesmos vertices).
    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(i_min_face_quadrant(0, 1, side, LAYER_PIA, LAYER_SAS_MID))
        comments.append(f"fsi_pia_{side}")
    block_section("fsi_pia", faces, comments)

    # ----- fsi_dura (r=2.35, z=0-30, face EXTERNA do anular sas_out: i_max)
    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(i_max_face_quadrant(0, 1, side, LAYER_SAS_MID, LAYER_SAS))
        comments.append(f"fsi_dura_{side}")
    block_section("fsi_dura", faces, comments)

    # ----- fsi_sclera_peri (z=30, r=1.55-2.00, top de sas_in)
    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_max_face_quadrant(1, side, LAYER_PIA, LAYER_SAS_MID))
        comments.append(f"fsi_sclera_peri_{side}")
    block_section("fsi_sclera_peri", faces, comments)

    # ----- fsi_sclera_ring (z=30, r=2.00-2.35, top de sas_out)
    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_max_face_quadrant(1, side, LAYER_SAS_MID, LAYER_SAS))
        comments.append(f"fsi_sclera_ring_{side}")
    block_section("fsi_sclera_ring", faces, comments)

    out.append(");")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    vs = build_vertices()
    expected_n_verts = len(Z_LEVELS) * N_LAYERS * 4
    assert len(vs) == expected_n_verts, f"len(vs)={len(vs)} != {expected_n_verts}"

    repo_root = Path(__file__).resolve().parent.parent
    case_root = repo_root / "cases" / "on-fsi-2"

    # ---- SOLID ----
    out_solid = [HEADER_SOLID, ""]
    out_solid.append(render_vertices(vs)); out_solid.append("")
    out_solid.append(render_solid_blocks()); out_solid.append("")
    out_solid.append(render_edges_solid()); out_solid.append("")
    out_solid.append(render_solid_boundary()); out_solid.append("")
    target_solid = case_root / "solid" / "system" / "blockMeshDict"
    target_solid.parent.mkdir(parents=True, exist_ok=True)
    target_solid.write_text("\n".join(out_solid) + "\n")
    print(f"wrote {target_solid}")

    # ---- FLUID ----
    out_fluid = [HEADER_FLUID, ""]
    out_fluid.append(render_vertices(vs)); out_fluid.append("")
    out_fluid.append(render_fluid_blocks()); out_fluid.append("")
    out_fluid.append(render_edges_fluid()); out_fluid.append("")
    out_fluid.append(render_fluid_boundary()); out_fluid.append("")
    target_fluid = case_root / "fluid" / "system" / "blockMeshDict"
    target_fluid.parent.mkdir(parents=True, exist_ok=True)
    target_fluid.write_text("\n".join(out_fluid) + "\n")
    print(f"wrote {target_fluid}")

    # contagem de celulas (estimativa)
    print()
    print(f"  {len(vs)} vertices em ambos os meshes (conformes nas interfaces FSI)")
    print()

    # solid
    total_solid = 0
    for ax_idx, n_axial in enumerate(N_AXIAL):
        center = N_RAD_CTR * N_TANG * n_axial
        on_quads      = 4 * (N_RAD_ON      * N_TANG * n_axial)
        pia_quads     = 4 * (N_RAD_PIA     * N_TANG * n_axial)
        sas_in_quads  = 4 * (N_RAD_SAS_IN  * N_TANG * n_axial) if ax_idx != 0 else 0
        sas_out_quads = 4 * (N_RAD_SAS_OUT * N_TANG * n_axial) if ax_idx != 0 else 0
        dura_quads    = 4 * (N_RAD_DURA    * N_TANG * n_axial)
        per_layer = center + on_quads + pia_quads + sas_in_quads + sas_out_quads + dura_quads
        total_solid += per_layer
        print(f"  SOLID  axial layer {ax_idx} (n_axial={n_axial}): {per_layer} cells")
    print(f"  SOLID  total: {total_solid} cells (vs 17408 do on-mestrado-2)")
    print()

    # fluid: 8 blocos (4 sas_in + 4 sas_out) x N_AXIAL[0]
    sas_in  = 4 * N_RAD_SAS_IN  * N_TANG * N_AXIAL[0]
    sas_out = 4 * N_RAD_SAS_OUT * N_TANG * N_AXIAL[0]
    total_fluid = sas_in + sas_out
    print(f"  FLUID  sas_in:  {sas_in} cells  (4 quadrantes x 3 radial x 8 tang x 30 axial)")
    print(f"  FLUID  sas_out: {sas_out} cells")
    print(f"  FLUID  total: {total_fluid} cells")


if __name__ == "__main__":
    main()
