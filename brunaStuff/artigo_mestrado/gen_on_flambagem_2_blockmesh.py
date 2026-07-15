"""Gerador do blockMeshDict do caso on-flambagem-2.

Versao tubular SIMPLES: 4 zonas concentricas (on, pia, sas, dura) de z=0 a z=30 mm.
Sem esclera, sem LC, sem globo, sem contact_local. CSF como solido soft com
propriedades identicas as do on-mestrado-2 (E=100 kPa, nu=0.30).

Geometria (mm; scale 0.001 aplicado pelo blockMesh):
    on   : r=0    -1.50, z=0-30, E=30  kPa, nu=0.45
    pia  : r=1.50 -1.55, z=0-30, E=3   MPa, nu=0.45
    sas  : r=1.55 -2.35, z=0-30, E=100 kPa, nu=0.30   (CSF, igual on-mestrado-2)
    dura : r=2.35 -2.50, z=0-30, E=3   MPa, nu=0.45

Discretizacao radial: pia=1, sas=6, dura=2 celulas. Tangencial 8/quadrante.
Axial: 30 celulas (1 mm/celula).

Patches:
    posterior_on    : z=0,  ON central + 4 quadrantes ON
    posterior_pia   : z=0,  4 quadrantes pia
    posterior_sas   : z=0,  4 quadrantes sas
    posterior_dura  : z=0,  4 quadrantes dura
    anterior_on     : z=L,  ON central + 4 quadrantes ON
    anterior_pia    : z=L,  4 quadrantes pia
    anterior_sas    : z=L,  4 quadrantes sas
    anterior_dura   : z=L,  4 quadrantes dura
    dura_outer      : i_max de todos os blocos dura (parede lateral)

Continuidade nodal: blocos compartilham vertices em z=0 e z=L. Bonded por DOF.

Uso:
    python brunaStuff/gen_on_flambagem_2_blockmesh.py
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
R_SAS    = 2.35
R_DURA   = 2.50
L        = 30.0

Z_LEVELS = (0.0, L)
N_AXIAL  = 30

N_TANG   = 8
N_RAD_ON   = 6
N_RAD_CTR  = 8
N_RAD_PIA  = 1
N_RAD_SAS  = 6
N_RAD_DURA = 2

CORNERS = ('NE', 'NW', 'SW', 'SE')

LAYER_SQUARE = 0
LAYER_ON     = 1
LAYER_PIA    = 2
LAYER_SAS    = 3
LAYER_DURA   = 4
N_LAYERS = 5


# ---------------------------------------------------------------------------
# Vertices
# ---------------------------------------------------------------------------

def diag_for_layer(layer: int) -> float:
    if layer == LAYER_SQUARE: return R_SQUARE
    if layer == LAYER_ON:     return R_ON   / math.sqrt(2.0)
    if layer == LAYER_PIA:    return R_PIA  / math.sqrt(2.0)
    if layer == LAYER_SAS:    return R_SAS  / math.sqrt(2.0)
    if layer == LAYER_DURA:   return R_DURA / math.sqrt(2.0)
    raise ValueError(layer)


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
    if layer == LAYER_ON:   return R_ON
    if layer == LAYER_PIA:  return R_PIA
    if layer == LAYER_SAS:  return R_SAS
    if layer == LAYER_DURA: return R_DURA
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

    ai = CORNERS.index(a)
    bi = CORNERS.index(b)
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
        f"{zone:5s} ( {n_radial} {N_TANG} {n_axial} )  "
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
        f"{zone:5s} ( {N_RAD_CTR} {N_TANG} {n_axial} )  "
        f"simpleGrading ( 1 1 1 )"
        + (f"  // {comment}" if comment else "")
    )


# ---------------------------------------------------------------------------
# Faces
# ---------------------------------------------------------------------------

def k_min_face_quadrant(z_idx: int, side: str, layer_in: int, layer_out: int):
    if side == 'E': a, b = 'SE', 'NE'
    elif side == 'N': a, b = 'NE', 'NW'
    elif side == 'W': a, b = 'NW', 'SW'
    elif side == 'S': a, b = 'SW', 'SE'
    else: raise ValueError(side)
    ai, bi = CORNERS.index(a), CORNERS.index(b)
    return (vid(z_idx, layer_in, ai), vid(z_idx, layer_out, ai),
            vid(z_idx, layer_out, bi), vid(z_idx, layer_in,  bi))


def k_max_face_quadrant(z_idx: int, side: str, layer_in: int, layer_out: int):
    return k_min_face_quadrant(z_idx, side, layer_in, layer_out)


def k_face_center(z_idx: int):
    return tuple(vid(z_idx, LAYER_SQUARE, i) for i in range(4))


def i_max_face_quadrant(z_idx_lo: int, z_idx_hi: int, side: str,
                        layer_in: int, layer_out: int):
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
# Render
# ---------------------------------------------------------------------------

HEADER = """FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}

// on-flambagem-2 - tubo simples nervo + bainha (4 zonas concentricas), z=0-30 mm.
//
// Geometria (scale 0.001 -> mm; ver brunaStuff/gen_on_flambagem_2_blockmesh.py):
//   on   : r=0    -1.50, z=0-30   (E=30  kPa, nu=0.45)
//   pia  : r=1.50 -1.55, z=0-30   (E=3   MPa, nu=0.45)
//   sas  : r=1.55 -2.35, z=0-30   (E=100 kPa, nu=0.30)   CSF soft solid igual on-mestrado-2
//   dura : r=2.35 -2.50, z=0-30   (E=3   MPa, nu=0.45)
//
// Sem esclera, sem LC, sem globo, sem contact_local. Base do estudo de flambagem.
//
// Continuidade nodal: blocos compartilham vertices em z=0 e z=30 (bonded por DOF).
//
// Patches (9):
//   posterior_on    -> z=0,  ON central + 4 quadrantes ON     (fixedDisplacement)
//   posterior_pia   -> z=0,  4 quadrantes pia                 (fixedDisplacement)
//   posterior_sas   -> z=0,  4 quadrantes sas                 (solidTraction P_CSF=1333)
//   posterior_dura  -> z=0,  4 quadrantes dura                (fixedDisplacement)
//   anterior_on     -> z=30, ON central + 4 quadrantes ON     (fixedDisplacement)
//   anterior_pia    -> z=30, 4 quadrantes pia                 (fixedDisplacement)
//   anterior_sas    -> z=30, 4 quadrantes sas                 (fixedDisplacement)
//   anterior_dura   -> z=30, 4 quadrantes dura                (fixedDisplacement)
//   dura_outer      -> r=2.50, z=0-30 (4 quadrantes)          (Winkler 200 kPa/m)

scale   0.001;
"""


def tuple_to_face(t):
    return f"( {t[0]:3d} {t[1]:3d} {t[2]:3d} {t[3]:3d} )"


def render_vertices(vs):
    lines = ["vertices", "("]
    for i, (x, y, z) in enumerate(vs):
        lines.append(f"    ( {x:11.6f}  {y:11.6f}  {z:6.2f} )  // {i:3d}")
    lines.append(");")
    return "\n".join(lines)


def render_blocks():
    out = ["blocks", "("]
    out.append("    // ===== z=0 a 30 mm: 4 zonas cilindricas concentricas =====")
    out.append(center_block(0, 1, "on", N_AXIAL, "ON central"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 0, 1, LAYER_SQUARE, LAYER_ON,
                                  "on", N_RAD_ON, N_AXIAL, f"ON_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 0, 1, LAYER_ON, LAYER_PIA,
                                  "pia", N_RAD_PIA, N_AXIAL, f"pia_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 0, 1, LAYER_PIA, LAYER_SAS,
                                  "sas", N_RAD_SAS, N_AXIAL, f"sas_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 0, 1, LAYER_SAS, LAYER_DURA,
                                  "dura", N_RAD_DURA, N_AXIAL, f"dura_{side}"))
    out.append(");")
    return "\n".join(out)


def render_edges():
    out = ["edges", "("]
    layer_radii = {
        LAYER_ON:   ('ON   r=1.50',  'on'),
        LAYER_PIA:  ('pia  r=1.55',  'pia'),
        LAYER_SAS:  ('sas  r=2.35',  'sas'),
        LAYER_DURA: ('dura r=2.50',  'dura'),
    }
    for z_idx, z in enumerate(Z_LEVELS):
        for layer, (label, _) in layer_radii.items():
            r = radius_for_layer(layer)
            arcs = arcs_for_circle(z_idx, z, layer)
            out.append(f"    // ---- {label}  @ z={z:.2f} mm ----")
            for a, b, mid in arcs:
                out.append(f"    arc {a:3d} {b:3d}  ( {mid[0]:9.5f}  {mid[1]:9.5f}  {mid[2]:6.2f} )")
        out.append("")
    out.append(");")
    return "\n".join(out)


def render_boundary():
    out = ["boundary", "("]

    def block_section(name: str, faces: list, comment_each: list):
        out.append(f"    {name}")
        out.append("    {")
        out.append("        type wall;")
        out.append("        faces")
        out.append("        (")
        for f, c in zip(faces, comment_each):
            out.append(f"            {tuple_to_face(f)}   // {c}")
        out.append("        );")
        out.append("    }")
        out.append("")

    faces = [k_face_center(0)]
    comments = ["ON central"]
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_min_face_quadrant(0, side, LAYER_SQUARE, LAYER_ON))
        comments.append(f"ON_{side}")
    block_section("posterior_on", faces, comments)

    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_min_face_quadrant(0, side, LAYER_ON, LAYER_PIA))
        comments.append(f"pia_{side}")
    block_section("posterior_pia", faces, comments)

    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_min_face_quadrant(0, side, LAYER_PIA, LAYER_SAS))
        comments.append(f"sas_{side}")
    block_section("posterior_sas", faces, comments)

    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_min_face_quadrant(0, side, LAYER_SAS, LAYER_DURA))
        comments.append(f"dura_{side}")
    block_section("posterior_dura", faces, comments)

    faces = [k_face_center(1)]
    comments = ["ON central"]
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_max_face_quadrant(1, side, LAYER_SQUARE, LAYER_ON))
        comments.append(f"ON_{side}")
    block_section("anterior_on", faces, comments)

    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_max_face_quadrant(1, side, LAYER_ON, LAYER_PIA))
        comments.append(f"pia_{side}")
    block_section("anterior_pia", faces, comments)

    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_max_face_quadrant(1, side, LAYER_PIA, LAYER_SAS))
        comments.append(f"sas_{side}")
    block_section("anterior_sas", faces, comments)

    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_max_face_quadrant(1, side, LAYER_SAS, LAYER_DURA))
        comments.append(f"dura_{side}")
    block_section("anterior_dura", faces, comments)

    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(i_max_face_quadrant(0, 1, side, LAYER_SAS, LAYER_DURA))
        comments.append(f"dura_outer_{side}")
    block_section("dura_outer", faces, comments)

    out.append(");")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    vs = build_vertices()
    assert len(vs) == len(Z_LEVELS) * N_LAYERS * 4

    out = [HEADER, ""]
    out.append(render_vertices(vs)); out.append("")
    out.append(render_blocks());      out.append("")
    out.append(render_edges());       out.append("")
    out.append(render_boundary());    out.append("")

    target = Path(__file__).resolve().parent.parent / "cases" / "on-flambagem-2" / "solid" / "system" / "blockMeshDict"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(out) + "\n")
    print(f"wrote {target}")
    print(f"  {len(vs)} vertices, {len(Z_LEVELS)} z-levels")
    n_total = (
        N_RAD_CTR * N_TANG * N_AXIAL
        + 4 * N_RAD_ON   * N_TANG * N_AXIAL
        + 4 * N_RAD_PIA  * N_TANG * N_AXIAL
        + 4 * N_RAD_SAS  * N_TANG * N_AXIAL
        + 4 * N_RAD_DURA * N_TANG * N_AXIAL
    )
    print(f"  cells (estimado): {n_total}")


if __name__ == "__main__":
    main()
