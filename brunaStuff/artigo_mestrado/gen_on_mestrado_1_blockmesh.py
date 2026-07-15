"""Gerador do blockMeshDict do caso on-mestrado-1 (SEM SAS, com LC + sclera + globo).

Versao expandida: nervo + pia lumped + LC + sclera + cap do globo. Mantem a
filosofia de fundir pia+SAS+dura num unico anel pia (Sigal 2004), e agora
inclui o globo de -2 (z=30.30-30.80, disco completo r=0-2.50, E=5 MPa).
A ancoragem se move para o equador (globo_outer) e a face anterior do
globo (anterior_globo) fica livre - exatamente como em -2.

Geometria (mm; scale 0.001 aplicado pelo blockMesh):
    on     : r=0    -1.50, z=0     -30.00, E=30  kPa
    pia    : r=1.50 -2.50, z=0     -30.00, E=3   MPa  (pia expandida, Sigal 2004)
    lc     : r=0    -1.50, z=30.00 -30.30, E=0.4 MPa  (lamina cribrosa)
    sclera : r=1.50 -2.50, z=30.00 -30.30, E=5   MPa  (anel escleral lumped)
    globo  : r=0    -2.50, z=30.30 -30.80, E=5   MPa  (cap do globo, igual -2)

Discretizacao radial: on=6 cells, pia=9 cells, lc=6 cells, sclera=9 cells,
globo (4 sub-aneis: square+on+pia bondeados). Tangencial 8/quadrante.
Axial: 30 cells em z=0-30 (1 mm/cell), 1 em z=30-30.30, 1 em z=30.30-30.80.

Continuidade nodal: blocos compartilham vertices em z=0, 30, 30.30, 30.80.
Bonded por DOF (sem mergePatchPairs).

Patches:
    posterior_on     : z=0, r=0-1.50              (canal optico, fixed)
    posterior_pia    : z=0, r=1.50-2.50           (P_CSF=1333 Pa, analog do
                                                   posterior_sas de -2)
    pia_outer        : r=2.50, z=0-30             (Winkler 200 kPa/m;
                                                   contact_local sera carved
                                                   a partir daqui)
    sclera_outer     : r=2.50, z=30-30.30         (livre, analog do
                                                   sclera_ring_outer de -2)
    globo_outer      : r=2.50, z=30.30-30.80      (EQUADOR fixedDisplacement,
                                                   analog do globo_outer de -2:
                                                   ancoragem Tenon + EOMs)
    anterior_globo   : z=30.80, r=0-2.50          (livre, lado vitreo,
                                                   analog do anterior_globo de -2)

Uso:
    python brunaStuff/gen_on_mestrado_1_blockmesh.py
        -> escreve cases/on-mestrado-1/solid/system/blockMeshDict
"""

from __future__ import annotations

import math
from pathlib import Path

R_SQUARE = 0.75
R_ON     = 1.50
R_PIA    = 2.50
L_NERVE  = 30.00
T_LC     = 0.30
T_GLOBO  = 0.50   # cap do globo (igual on-mestrado-2)

Z_LEVELS = (0.0, L_NERVE, L_NERVE + T_LC, L_NERVE + T_LC + T_GLOBO)
N_AXIAL  = (30, 1, 1)

N_TANG    = 8
N_RAD_ON  = 6
N_RAD_CTR = 8
N_RAD_PIA = 9

CORNERS = ('NE', 'NW', 'SW', 'SE')

LAYER_SQUARE = 0
LAYER_ON     = 1
LAYER_PIA    = 2
N_LAYERS = 3


def diag_for_layer(layer: int) -> float:
    if layer == LAYER_SQUARE: return R_SQUARE
    if layer == LAYER_ON:     return R_ON  / math.sqrt(2.0)
    if layer == LAYER_PIA:    return R_PIA / math.sqrt(2.0)
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
    if layer == LAYER_ON:  return R_ON
    if layer == LAYER_PIA: return R_PIA
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
        f"{zone:7s} ( {n_radial} {N_TANG} {n_axial} )  "
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
        f"{zone:7s} ( {N_RAD_CTR} {N_TANG} {n_axial} )  "
        f"simpleGrading ( 1 1 1 )"
        + (f"  // {comment}" if comment else "")
    )


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


HEADER = """FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}

// on-mestrado-1 - 5 zonas (on + pia + lc + sclera + globo).
//
// Pia expandida (Sigal 2004): pia + SAS + dura fundidas num unico anel
// a E=3 MPa, nu=0.49. SAS sem materializacao geometrica, mas P_CSF
// aplicada em posterior_pia (analog do posterior_sas de -2).
// LC + sclera replicam o cap anterior do -2 (mas com sclera lumped:
// sclera_peri + sclera_ring -> sclera unico a E=5 MPa).
// Globo: copiado integralmente de on-mestrado-2 (disco r=0-2.50,
// z=30.30-30.80, E=5 MPa). Mesma BC: globo_outer fixed (equador,
// Tenon + EOMs), anterior_globo livre (lado vitreo).
//
// Geometria (scale 0.001 -> mm; ver brunaStuff/gen_on_mestrado_1_blockmesh.py):
//   on     : r=0    -1.50, z=0     -30.00   (E=30  kPa)
//   pia    : r=1.50 -2.50, z=0     -30.00   (E=3   MPa)
//   lc     : r=0    -1.50, z=30.00 -30.30   (E=0.4 MPa)  lamina cribrosa
//   sclera : r=1.50 -2.50, z=30.00 -30.30   (E=5   MPa)  anel escleral lumped
//   globo  : r=0    -2.50, z=30.30 -30.80   (E=5   MPa)  cap do globo (igual -2)
//
// Continuidade nodal: blocos compartilham vertices em z=0, 30, 30.30, 30.80.
// Bonded por DOF (sem mergePatchPairs).
//
// Patches:
//   posterior_on   : z=0, r=0-1.50         (fixedDisplacement - canal optico)
//   posterior_pia  : z=0, r=1.50-2.50      (solidTraction P_CSF=1333 Pa)
//   pia_outer      : r=2.50, z=0-30        (Winkler 200 kPa/m;
//                                           contact_local carved-out depois)
//   sclera_outer   : r=2.50, z=30-30.30    (livre, analog sclera_ring_outer)
//   globo_outer    : r=2.50, z=30.30-30.80 (fixedDisplacement - EQUADOR Tenon)
//   anterior_globo : z=30.80, r=0-2.50     (solidTraction P=0 - lado vitreo)

scale   0.001;
"""


def tuple_to_face(t):
    return f"( {t[0]:3d} {t[1]:3d} {t[2]:3d} {t[3]:3d} )"


def render_vertices(vs):
    lines = ["vertices", "("]
    for i, (x, y, z) in enumerate(vs):
        lines.append(f"    ( {x:11.6f}  {y:11.6f}  {z:7.3f} )  // {i:3d}")
    lines.append(");")
    return "\n".join(lines)


def render_blocks():
    out = ["blocks", "("]

    out.append("    // ===== z=0 a 30 mm: nervo + pia expandida =====")
    out.append(center_block(0, 1, "on", N_AXIAL[0], "ON central"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 0, 1, LAYER_SQUARE, LAYER_ON,
                                  "on", N_RAD_ON, N_AXIAL[0], f"ON_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 0, 1, LAYER_ON, LAYER_PIA,
                                  "pia", N_RAD_PIA, N_AXIAL[0], f"pia_{side}"))

    out.append("")
    out.append("    // ===== z=30 a 30.30 mm: LC + sclera =====")
    out.append(center_block(1, 2, "lc", N_AXIAL[1], "LC central"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 1, 2, LAYER_SQUARE, LAYER_ON,
                                  "lc", N_RAD_ON, N_AXIAL[1], f"LC_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 1, 2, LAYER_ON, LAYER_PIA,
                                  "sclera", N_RAD_PIA, N_AXIAL[1], f"sclera_{side}"))

    out.append("")
    out.append("    // ===== z=30.30 a 30.80 mm: cap do globo (igual -2) =====")
    out.append(center_block(2, 3, "globo", N_AXIAL[2], "globo central"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 2, 3, LAYER_SQUARE, LAYER_ON,
                                  "globo", N_RAD_ON, N_AXIAL[2], f"globo_ON_{side}"))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 2, 3, LAYER_ON, LAYER_PIA,
                                  "globo", N_RAD_PIA, N_AXIAL[2], f"globo_pia_{side}"))

    out.append(");")
    return "\n".join(out)


def render_edges():
    out = ["edges", "("]
    layer_radii = {
        LAYER_ON:  ('ON   r=1.50', 'on'),
        LAYER_PIA: ('pia  r=2.50', 'pia'),
    }
    for z_idx, z in enumerate(Z_LEVELS):
        for layer, (label, _) in layer_radii.items():
            arcs = arcs_for_circle(z_idx, z, layer)
            out.append(f"    // ---- {label}  @ z={z:.3f} mm ----")
            for a, b, mid in arcs:
                out.append(f"    arc {a:3d} {b:3d}  ( {mid[0]:9.5f}  {mid[1]:9.5f}  {mid[2]:7.3f} )")
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
        faces.append(i_max_face_quadrant(0, 1, side, LAYER_ON, LAYER_PIA))
        comments.append(f"pia_outer_{side}")
    block_section("pia_outer", faces, comments)

    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(i_max_face_quadrant(1, 2, side, LAYER_ON, LAYER_PIA))
        comments.append(f"sclera_outer_{side}")
    block_section("sclera_outer", faces, comments)

    # globo_outer: face cilindrica lateral do globo (r=2.50, z=30.30-30.80)
    # Em -2 e fixedDisplacement (equador anchor, Tenon + EOMs).
    faces = []; comments = []
    for side in ('E', 'N', 'W', 'S'):
        faces.append(i_max_face_quadrant(2, 3, side, LAYER_ON, LAYER_PIA))
        comments.append(f"globo_outer_{side}")
    block_section("globo_outer", faces, comments)

    # anterior_globo: face do disco completo em z=30.80 (todos os sub-aneis)
    faces = [k_face_center(3)]
    comments = ["globo central"]
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_max_face_quadrant(3, side, LAYER_SQUARE, LAYER_ON))
        comments.append(f"globo_ON_{side}")
    for side in ('E', 'N', 'W', 'S'):
        faces.append(k_max_face_quadrant(3, side, LAYER_ON, LAYER_PIA))
        comments.append(f"globo_pia_{side}")
    block_section("anterior_globo", faces, comments)

    out.append(");")
    return "\n".join(out)


def main():
    vs = build_vertices()
    assert len(vs) == len(Z_LEVELS) * N_LAYERS * 4

    out = [HEADER, ""]
    out.append(render_vertices(vs)); out.append("")
    out.append(render_blocks());     out.append("")
    out.append(render_edges());      out.append("")
    out.append(render_boundary());   out.append("")

    target = Path(__file__).resolve().parent.parent / "cases" / "on-mestrado-1" / "solid" / "system" / "blockMeshDict"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(out) + "\n")
    print(f"wrote {target}")
    print(f"  {len(vs)} vertices, {len(Z_LEVELS)} z-levels (z = {Z_LEVELS})")
    total = 0
    z_pairs = [(Z_LEVELS[i], Z_LEVELS[i+1]) for i in range(len(N_AXIAL))]
    for ax_idx, n_axial in enumerate(N_AXIAL):
        center = N_RAD_CTR * N_TANG * n_axial
        inner_quads = 4 * N_RAD_ON  * N_TANG * n_axial
        outer_quads = 4 * N_RAD_PIA * N_TANG * n_axial
        per_layer = center + inner_quads + outer_quads
        total += per_layer
        z_lo, z_hi = z_pairs[ax_idx]
        print(f"  axial {ax_idx} z={z_lo:.2f}->{z_hi:.2f} mm (n_axial={n_axial}): {per_layer} cells")
    print(f"  cells total (estimado): {total}")


if __name__ == "__main__":
    main()
