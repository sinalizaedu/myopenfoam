"""Gerador MINIMO: cilindro de UMA zona apenas (dura) para teste de sanidade.

Geometria simples: cilindro solido, uma unica zona, com mesma malha O-grid.
"""

from __future__ import annotations

import math
from pathlib import Path

R_SQUARE = 0.75
R_OUTER  = 2.50
L        = 30.0

N_AXIAL  = 30
N_TANG   = 8
N_RAD_OUTER = 9
N_RAD_CTR   = 8

CORNERS = ('NE', 'NW', 'SW', 'SE')


def vid(z_idx, layer, corner_idx):
    return z_idx * 8 + layer * 4 + corner_idx


def corner_xy(corner, d):
    if corner == 'NE': return (d, d)
    if corner == 'NW': return (-d, d)
    if corner == 'SW': return (-d, -d)
    if corner == 'SE': return (d, -d)


def quadrant_block(side, z_lo, z_hi):
    if side == 'E': a, b = 'SE', 'NE'
    elif side == 'N': a, b = 'NE', 'NW'
    elif side == 'W': a, b = 'NW', 'SW'
    else: a, b = 'SW', 'SE'
    ai, bi = CORNERS.index(a), CORNERS.index(b)
    v0 = vid(z_lo, 0, ai); v1 = vid(z_lo, 1, ai)
    v2 = vid(z_lo, 1, bi); v3 = vid(z_lo, 0, bi)
    v4 = vid(z_hi, 0, ai); v5 = vid(z_hi, 1, ai)
    v6 = vid(z_hi, 1, bi); v7 = vid(z_hi, 0, bi)
    return f"    hex ( {v0:3d} {v1:3d} {v2:3d} {v3:3d}  {v4:3d} {v5:3d} {v6:3d} {v7:3d} )  outer ( {N_RAD_OUTER} {N_TANG} {N_AXIAL} )  simpleGrading ( 1 1 1 )"


def center_block(z_lo, z_hi):
    NE, NW, SW, SE = (vid(z_lo, 0, i) for i in range(4))
    NEt, NWt, SWt, SEt = (vid(z_hi, 0, i) for i in range(4))
    return f"    hex ( {NE:3d} {NW:3d} {SW:3d} {SE:3d}  {NEt:3d} {NWt:3d} {SWt:3d} {SEt:3d} )  outer ( {N_RAD_CTR} {N_TANG} {N_AXIAL} )  simpleGrading ( 1 1 1 )"


def build():
    vs = []
    for z_idx, z in enumerate([0.0, L]):
        for layer in [0, 1]:
            d = R_SQUARE if layer == 0 else R_OUTER / math.sqrt(2.0)
            for c in CORNERS:
                x, y = corner_xy(c, d)
                vs.append((x, y, z))

    out = []
    out.append("FoamFile\n{\n    version 2.0;\n    format ascii;\n    class dictionary;\n    object blockMeshDict;\n}\n\nscale 0.001;\n")
    out.append("vertices\n(")
    for i, v in enumerate(vs):
        out.append(f"    ( {v[0]:.5f} {v[1]:.5f} {v[2]:.2f} )  // {i}")
    out.append(");\n")

    out.append("blocks\n(")
    out.append(center_block(0, 1))
    for side in ('E', 'N', 'W', 'S'):
        out.append(quadrant_block(side, 0, 1))
    out.append(");\n")

    out.append("edges\n(")
    for z_idx, z in enumerate([0.0, L]):
        NE, NW, SW, SE = (vid(z_idx, 1, i) for i in range(4))
        r = R_OUTER
        out.append(f"    arc {NE:3d} {SE:3d} ( {r:.3f} 0.0 {z:.2f} )")
        out.append(f"    arc {NE:3d} {NW:3d} ( 0.0 {r:.3f} {z:.2f} )")
        out.append(f"    arc {NW:3d} {SW:3d} ( {-r:.3f} 0.0 {z:.2f} )")
        out.append(f"    arc {SW:3d} {SE:3d} ( 0.0 {-r:.3f} {z:.2f} )")
    out.append(");\n")

    out.append("boundary\n(")
    out.append("    posterior\n    {\n        type wall;\n        faces\n        (")
    out.append(f"            ( {vid(0,0,0)} {vid(0,0,1)} {vid(0,0,2)} {vid(0,0,3)} )")
    for side in ('E','N','W','S'):
        if side == 'E': a,b = 'SE','NE'
        elif side == 'N': a,b = 'NE','NW'
        elif side == 'W': a,b = 'NW','SW'
        else: a,b = 'SW','SE'
        ai,bi = CORNERS.index(a), CORNERS.index(b)
        out.append(f"            ( {vid(0,0,ai)} {vid(0,1,ai)} {vid(0,1,bi)} {vid(0,0,bi)} )")
    out.append("        );\n    }")

    out.append("    anterior\n    {\n        type wall;\n        faces\n        (")
    out.append(f"            ( {vid(1,0,0)} {vid(1,0,1)} {vid(1,0,2)} {vid(1,0,3)} )")
    for side in ('E','N','W','S'):
        if side == 'E': a,b = 'SE','NE'
        elif side == 'N': a,b = 'NE','NW'
        elif side == 'W': a,b = 'NW','SW'
        else: a,b = 'SW','SE'
        ai,bi = CORNERS.index(a), CORNERS.index(b)
        out.append(f"            ( {vid(1,0,ai)} {vid(1,1,ai)} {vid(1,1,bi)} {vid(1,0,bi)} )")
    out.append("        );\n    }")

    out.append("    outer_wall\n    {\n        type wall;\n        faces\n        (")
    for side in ('E','N','W','S'):
        if side == 'E': a,b = 'SE','NE'
        elif side == 'N': a,b = 'NE','NW'
        elif side == 'W': a,b = 'NW','SW'
        else: a,b = 'SW','SE'
        ai,bi = CORNERS.index(a), CORNERS.index(b)
        out.append(f"            ( {vid(0,1,ai)} {vid(0,1,bi)} {vid(1,1,bi)} {vid(1,1,ai)} )")
    out.append("        );\n    }")

    out.append(");\n")

    target = Path("/Users/brunaenne/Documents/repos/myopenfoam/cases/on-mestrado-2-min/solid/system/blockMeshDict")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(out))
    print("wrote", target)


if __name__ == "__main__":
    build()
