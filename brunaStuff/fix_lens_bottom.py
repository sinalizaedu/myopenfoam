#!/usr/bin/env python3
"""
Fix fluid blockMeshDict: extend fluid lens cavity bottom from y=9.6mm to y=8.2mm.
Strategy:
  1. Add 18 new vertices at y=8.2mm (row "5.5")
  2. Split row5 (y=[7.2,9.6mm]) into row5a (y=[7.2,8.2mm]) + row5b (y=[8.2,9.6mm])
  3. Remove row5b blocks for lens body cols (col0,col1 right; col0L,col1L left)
  4. Update lens_bottom patch to y=8.2mm
  5. Update lens_right / lens_left to include new lower face at y=[8.2,9.6mm]
  6. Update front/back patches
  7. Split ac_inlet / ac_inlet_left (now span two row5 sub-blocks)
"""

import re

SRC = "cases/eye-fsi-tc0/fluid/system/blockMeshDict"

with open(SRC, "r") as f:
    txt = f.read()

# ── 1. NEW VERTICES (append before closing ");") of the vertices section ──────
NEW_VERTS = """
    // ── y=8.20mm: fundo real da lente sólida — vértices da row "5.5" ─────────
    // Lado direito z=0 (front)
    ( 0.00000  0.008200  0.000 )  // 286  V(0,5.5)  x=  0mm
    ( 0.00500  0.008200  0.000 )  // 287  V(1,5.5)  x=  5mm
    ( 0.01500  0.008200  0.000 )  // 288  V(2,5.5)  x= 15mm
    ( 0.01950  0.008200  0.000 )  // 289  V(3,5.5)  x= 19.5mm
    ( 0.02000  0.008200  0.000 )  // 290  V(4,5.5)  x= 20mm
    // Lado direito z=1mm (back)
    ( 0.00000  0.008200  0.001 )  // 291  V(0,5.5)b
    ( 0.00500  0.008200  0.001 )  // 292  V(1,5.5)b
    ( 0.01500  0.008200  0.001 )  // 293  V(2,5.5)b
    ( 0.01950  0.008200  0.001 )  // 294  V(3,5.5)b
    ( 0.02000  0.008200  0.001 )  // 295  V(4,5.5)b
    // Lado esquerdo z=0 (front)  — V(0,5.5)=286 é compartilhado com o direito
    (-0.00500  0.008200  0.000 )  // 296  VL(0,5.5) x= -5mm
    (-0.01500  0.008200  0.000 )  // 297  VL(1,5.5) x=-15mm
    (-0.01950  0.008200  0.000 )  // 298  VL(2,5.5) x=-19.5mm
    (-0.02000  0.008200  0.000 )  // 299  VL(3,5.5) x=-20mm
    // Lado esquerdo z=1mm (back)
    (-0.00500  0.008200  0.001 )  // 300  VL(0,5.5)b
    (-0.01500  0.008200  0.001 )  // 301  VL(1,5.5)b
    (-0.01950  0.008200  0.001 )  // 302  VL(2,5.5)b
    (-0.02000  0.008200  0.001 )  // 303  VL(3,5.5)b
"""

# The last vertex in the git file is 285; insert new vertices before the closing ");"
# of the vertices section (which is followed by a blank line and then "blocks")
txt = txt.replace(
    "    (-0.02050  0.002400  0.001 )  // 285  TM_left top     y=2.40mm z=1mm\n);",
    "    (-0.02050  0.002400  0.001 )  // 285  TM_left top     y=2.40mm z=1mm\n" + NEW_VERTS + ");"
)

# ── 2. REPLACE ROW 5 BLOCKS ───────────────────────────────────────────────────
OLD_ROW5 = """    // ── Row 5: y=[7.20, 9.60mm] ──────────────────────────────────────────
    hex ( 25 26 31 30 90 91 96 95 ) (10 5 1)  simpleGrading (1 1 1)
    hex ( 26 27 32 31 91 92 97 96 ) (20 5 1)  simpleGrading (1 1 1)
    hex ( 27 28 33 32 92 93 98 97 ) (9 5 1)  simpleGrading (1 1 1)
    hex ( 28 29 34 33 93 94 99 98 ) (1 5 1)  simpleGrading (1 1 1)"""

NEW_ROW5 = """    // ── Row 5a: y=[7.20, 8.20mm] — TODOS os cols (câmara posterior) ────────
    hex ( 25 26 287 286  90 91 292 291 ) (10 2 1)  simpleGrading (1 1 1)  // col 0
    hex ( 26 27 288 287  91 92 293 292 ) (20 2 1)  simpleGrading (1 1 1)  // col 1
    hex ( 27 28 289 288  92 93 294 293 ) (9 2 1)   simpleGrading (1 1 1)  // col 2
    hex ( 28 29 290 289  93 94 295 294 ) (1 2 1)   simpleGrading (1 1 1)  // col 3
    // ── Row 5b: y=[8.20, 9.60mm] — cols 0-1 = LENTE (void); cols 2-3 = fluido
    hex ( 288 289 33 32  293 294 98 97 ) (9 3 1)   simpleGrading (1 1 1)  // col 2
    hex ( 289 290 34 33  294 295 99 98 ) (1 3 1)   simpleGrading (1 1 1)  // col 3"""

txt = txt.replace(OLD_ROW5, NEW_ROW5)

OLD_ROW5L = """    // ── Row 5 left: y=[7.20, 9.60mm] ────────────────────────────────────
    hex ( 169 25 30 174 234 90 95 239 ) (10 5 1)  simpleGrading (1 1 1)
    hex ( 170 169 174 175 235 234 239 240 ) (20 5 1)  simpleGrading (1 1 1)
    hex ( 171 170 175 176 236 235 240 241 ) (9 5 1)  simpleGrading (1 1 1)
    hex ( 172 171 176 177 237 236 241 242 ) (1 5 1)  simpleGrading (1 1 1)"""

NEW_ROW5L = """    // ── Row 5a left: y=[7.20, 8.20mm] — TODOS os cols ──────────────────────
    hex ( 169 25 286 296  234 90 291 300 ) (10 2 1)  simpleGrading (1 1 1)  // col 0L
    hex ( 170 169 296 297  235 234 300 301 ) (20 2 1)  simpleGrading (1 1 1)  // col 1L
    hex ( 171 170 297 298  236 235 301 302 ) (9 2 1)   simpleGrading (1 1 1)  // col 2L
    hex ( 172 171 298 299  237 236 302 303 ) (1 2 1)   simpleGrading (1 1 1)  // col 3L
    // ── Row 5b left: y=[8.20, 9.60mm] — cols 0L-1L = LENTE (void); cols 2L-3L = fluido
    hex ( 298 297 175 176  302 301 240 241 ) (9 3 1)   simpleGrading (1 1 1)  // col 2L
    hex ( 299 298 176 177  303 302 241 242 ) (1 3 1)   simpleGrading (1 1 1)  // col 3L"""

txt = txt.replace(OLD_ROW5L, NEW_ROW5L)

# ── 3. LENS_BOTTOM patches ────────────────────────────────────────────────────
txt = txt.replace(
    """    lens_bottom
    {
        type wall;
        faces
        (
            ( 30 31  96  95 )
            ( 31 32  97  96 )
        );
    }""",
    """    lens_bottom
    {
        // y=8.2mm — fundo da cavidade da lente (row5b cols 0-1 ausentes)
        type wall;
        faces
        (
            ( 286 287 292 291 )  // x=[0,5mm]
            ( 287 288 293 292 )  // x=[5,15mm]
        );
    }"""
)

txt = txt.replace(
    """    lens_bottom_left
    {
        type wall;
        faces
        (
            ( 174 30 95 239 )
            ( 175 174 239 240 )
        );
    }""",
    """    lens_bottom_left
    {
        type wall;
        faces
        (
            ( 296 286 291 300 )  // x=[-5,0mm]
            ( 297 296 300 301 )  // x=[-15,-5mm]
        );
    }"""
)

# ── 4. LENS_RIGHT / LENS_LEFT — add new lower face ───────────────────────────
txt = txt.replace(
    """    lens_right
    {
        type wall;
        faces
        (
            ( 32 37 102  97 )
            ( 37 42 107 102 )
        );
    }""",
    """    lens_right
    {
        // x=+15mm, y=[8.2mm,14.4mm]
        type wall;
        faces
        (
            ( 288 32  97 293 )   // y=[8.2,9.6mm]  — nova face inferior
            ( 32 37 102  97 )    // y=[9.6,12mm]
            ( 37 42 107 102 )    // y=[12,14.4mm]
        );
    }"""
)

txt = txt.replace(
    """    // x=-15 mm strip — mirror of lens_right (32 37 102 97) / (37 42 107 102).
    lens_left
    {
        type wall;
        faces
        (
            ( 175 180 245 240 )
            ( 180 185 250 245 )
        );
    }""",
    """    lens_left
    {
        // x=-15mm, y=[8.2mm,14.4mm]
        type wall;
        faces
        (
            ( 297 175 240 301 )  // y=[8.2,9.6mm]  — nova face inferior
            ( 175 180 245 240 )  // y=[9.6,12mm]
            ( 180 185 250 245 )  // y=[12,14.4mm]
        );
    }"""
)

# ── 5. AC_INLET — split into row5a + row5b sub-faces ─────────────────────────
txt = txt.replace(
    "    ac_inlet\n    {\n        type patch;\n        faces ( ( 29 34 99 94 ) );\n    }",
    "    ac_inlet\n    {\n        type patch;\n        faces ( ( 29 290 295 94 ) ( 290 34 99 295 ) );\n    }"
)

txt = txt.replace(
    "    ac_inlet_left\n    {\n        type patch;\n        faces ( ( 172 177 242 237 ) );\n    }",
    "    ac_inlet_left\n    {\n        type patch;\n        faces ( ( 172 299 303 237 ) ( 299 177 242 303 ) );\n    }"
)

# ── 6. FRONT patch — replace row5 faces with row5a + row5b faces ──────────────
# Right side
txt = txt.replace(
    "            ( 25 26 31 30 )\n"
    "            ( 26 27 32 31 )\n"
    "            ( 27 28 33 32 )\n"
    "            ( 28 29 34 33 )\n",
    "            ( 25 26 287 286 )\n"
    "            ( 26 27 288 287 )\n"
    "            ( 27 28 289 288 )\n"
    "            ( 28 29 290 289 )\n"
    "            ( 288 289 33 32 )\n"
    "            ( 289 290 34 33 )\n"
)
# Left side
txt = txt.replace(
    "            ( 169 25 30 174 )\n"
    "            ( 170 169 174 175 )\n"
    "            ( 171 170 175 176 )\n"
    "            ( 172 171 176 177 )\n",
    "            ( 169 25 286 296 )\n"
    "            ( 170 169 296 297 )\n"
    "            ( 171 170 297 298 )\n"
    "            ( 172 171 298 299 )\n"
    "            ( 298 297 175 176 )\n"
    "            ( 299 298 176 177 )\n"
)

# ── 7. BACK patch — same structure ────────────────────────────────────────────
# Right side
txt = txt.replace(
    "            ( 90 91 96 95 )\n"
    "            ( 91 92 97 96 )\n"
    "            ( 92 93 98 97 )\n"
    "            ( 93 94 99 98 )\n",
    "            ( 90 91 292 291 )\n"
    "            ( 91 92 293 292 )\n"
    "            ( 92 93 294 293 )\n"
    "            ( 93 94 295 294 )\n"
    "            ( 293 294 98 97 )\n"
    "            ( 294 295 99 98 )\n"
)
# Left side
txt = txt.replace(
    "            ( 234 90 95 239 )\n"
    "            ( 235 234 239 240 )\n"
    "            ( 236 235 240 241 )\n"
    "            ( 237 236 241 242 )\n",
    "            ( 234 90 291 300 )\n"
    "            ( 235 234 300 301 )\n"
    "            ( 236 235 301 302 )\n"
    "            ( 237 236 302 303 )\n"
    "            ( 302 301 240 241 )\n"
    "            ( 303 302 241 242 )\n"
)

with open(SRC, "w") as f:
    f.write(txt)

print("blockMeshDict updated successfully.")
