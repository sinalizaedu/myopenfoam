#!/usr/bin/env python3
"""
Generate the FULL fluid/system/blockMeshDict for the full symmetric eye model.
Mirrors the half-model fluid domain (x=[0,21mm]) about x=0 → x=[-21,+21mm].

Key new features:
  - x=0 ("sclera_left") becomes INTERIOR (removed from patches)
  - needle_* patches sit on x=±20 mm (inner sclera); x=0 is interior (merged halves)
  - ac_inlet_left at x=-20mm (left scleral spur)
  - outlet_tm_left at x=-20.5mm
  - tm_zone_left cell zone for Darcy resistance
  - FSI patches mirrored on the left side

Vertex numbering:
  Existing right half: 0-143
  New left half:
    VL(iL,j) z=0:   144 + iL + j*5,  iL=0..4, j=0..12  → 144-208
    VL(iL,j) z=1mm: 209 + iL + j*5                     → 209-273
    y=0.4mm row z=0: 274-277  (iL=0..3, x=-5,-15,-19.5,-20)
    y=0.4mm row z=1: 278-281
    TM left col:     282-285  (x=-20.5mm)

Left x positions:  iL=0→x=-5mm, 1→x=-15mm, 2→x=-19.5mm, 3→x=-20mm, 4→x=-21mm
Right x positions: i=0→x=0,      1→x=5mm,   2→x=15mm,    3→x=19.5mm, 4→x=20mm

Run: python3 brunaStuff/gen_fluid_bmd.py > cases/eye-fsi-tc0/fluid/system/blockMeshDict
"""

# ─── Coordinate tables ────────────────────────────────────────────────────────
# Right x-values (i=0..4)
xR = [0.0, 0.005, 0.015, 0.0195, 0.020]
# Left x-values (iL=0..4): mirror of right, but excluding x=0 (already exists)
xL = [-0.005, -0.015, -0.0195, -0.020, -0.021]
# y-values (j=0..12)
y = [0.0, 0.00240, 0.00300, 0.00316, 0.00480,
     0.00720, 0.00960, 0.01200, 0.01440,
     0.01800, 0.02192, 0.02208, 0.02400]

def VR(i, j):
    """Right-half vertex index (z=0)."""
    return i + j*5

def VRz(i, j):
    """Right-half vertex index (z=1mm)."""
    return i + j*5 + 65

def VL(iL, j):
    """Left-half vertex index (z=0)."""
    return 144 + iL + j*5

def VLz(iL, j):
    """Left-half vertex index (z=1mm)."""
    return 209 + iL + j*5

# Special row y=0.4mm:
# Right: v130+iR for i=0..4 (z=0), v137+iR (z=1mm)
# Left : 274+iL for iL=0..3 (z=0); x=0 y=0.4 = v130 already; iL=4 (x=-21mm) → new 286/287? No—
# Actually the left row0a blocks only go up to col3L (x=-20mm), not col4L (x=-21mm).
# col3L: x=[-20,-19.5mm] has j_max at y=0.4mm = vL133(277) on right face.
# col4L: x=[-21,-20mm]: SCLERA SOLID (not fluid), so no row0a block here.

# y=0.4mm special vertices (left):
vL130 = 274  # x=-5mm,    y=0.4mm, z=0
vL131 = 275  # x=-15mm,   y=0.4mm, z=0
vL132 = 276  # x=-19.5mm, y=0.4mm, z=0
vL133 = 277  # x=-20mm,   y=0.4mm, z=0  ← = VL(3, j=0b)
vL137 = 278  # z=1mm counterparts
vL138 = 279
vL139 = 280
vL140 = 281

# TM left column (x=-20.5mm):
TML_04_0 = 282   # x=-20.5, y=0.40mm, z=0
TML_24_0 = 283   # x=-20.5, y=2.40mm, z=0
TML_04_1 = 284   # x=-20.5, y=0.40mm, z=1mm
TML_24_1 = 285   # x=-20.5, y=2.40mm, z=1mm

lines = []
# All hex vertex rings (v0..v7) in blockMesh order — used for empty front/back (z slabs).
all_hex = []

def emit(s):
    lines.append(s)


def emit_hex(vs, nx, ny, zone_token="", comment=""):
    """Emit one hex block line and record vertices for front/back patches."""
    all_hex.append(list(vs))
    ztok = f" {zone_token} " if zone_token else " "
    cmt = f"  // {comment}" if comment else ""
    emit(
        f"    hex ( {' '.join(str(v) for v in vs)} ){ztok}({nx} {ny} 1)  simpleGrading (1 1 1){cmt}"
    )

emit(r"""FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}

// eye-fsi-tc0: FLUID domain — FULL SYMMETRIC MODEL
//
// Coordinate system:
//   x = -21 → +21 mm  (left outer sclera → right outer sclera)
//   y =   0 → 24 mm   (cornea → posterior sclera)
//   z =   0 → 1 mm    (2-D slab)
//
// x-partition (right, positive):  0, 5, 15, 19.5, 20, 20.5, 21
// x-partition (left,  negative): -5,-15,-19.5,-20,-20.5,-21  (mirror)
//
// y-partition (same both sides):
//   0, 0.40, 2.40, 3.00, 3.16, 4.80, 7.20, 9.60, 12.00,
//   14.40, 18.00, 21.92, 22.08, 24.00 mm
//
// Cell zones:
//   tm_zone      — right TM: x=[20,20.5mm], y=[0.40,2.40mm]
//   tm_zone_left — left  TM: x=[-20.5,-20mm], y=[0.40,2.40mm]
//   vitreous_zone — x=[-20,+20mm], y=[14.40,24mm] + x=[-15,+15mm], y=[9.60,14.40mm]
//                   (NB: lens solid not in fluid mesh)
//
// Vertex numbering:
//   Right half (original):  0-143
//   Left half (new):       144-285
//     VL(iL,j) z=0:   144 + iL + j*5,  iL=0..4, j=0..12  → 144-208
//     VL(iL,j) z=1mm: 209 + iL + j*5                     → 209-273
//     y=0.4mm left row z=0:  274-277
//     y=0.4mm left row z=1:  278-281
//     TM left column:        282-285
//
// Left x-index mapping:  iL=0→x=-5mm, 1→x=-15mm, 2→x=-19.5mm, 3→x=-20mm, 4→x=-21mm
// Needles (mirrored): IVI / paracentesis patches on x=±20 mm inner sclera strips;
//   x=0 is interior (no sclera_left patch). sclera_right_upper omits the IVI strip face.

scale   1;
""")

# ─── VERTICES ────────────────────────────────────────────────────────────────
emit("vertices\n(")

emit("    // ═══════════════════════════════════════════════════════════════════════")
emit("    // RIGHT HALF — original vertices 0–143 (unchanged)")
emit("    // ═══════════════════════════════════════════════════════════════════════")
emit("")
emit("    // ── z = 0 layer ────────────────────────────────────────── v0 – v64")
emit("")

yvals = [0.000000, 0.002400, 0.003000, 0.003160, 0.004800,
         0.007200, 0.009600, 0.012000, 0.014400,
         0.018000, 0.021920, 0.022080, 0.024000]
ylabels = ["y = 0", "y = 2.40 mm", "y = 3.00 mm", "y = 3.16 mm", "y = 4.80 mm",
           "y = 7.20 mm", "y = 9.60 mm", "y = 12.00 mm", "y = 14.40 mm",
           "y = 18.00 mm", "y = 21.92 mm", "y = 22.08 mm", "y = 24.00 mm"]
xvals_right = [0.00000, 0.00500, 0.01500, 0.01950, 0.02000]

for j in range(13):
    emit(f"    // j={j}  {ylabels[j]}")
    for i in range(5):
        vid = i + j*5
        emit(f"    ( {xvals_right[i]:.5f}  {yvals[j]:.6f}  0.000 )  // {vid:3d}  V({i},{j})")
emit("")

emit("    // ── z = 1 mm layer ───────────────────────────────────────── v65 – v129")
for j in range(13):
    row = "    " + "  ".join(
        f"( {xvals_right[i]:.5f}  {yvals[j]:.6f}  0.001 )" for i in range(5)
    )
    lo = 65 + j*5
    hi = lo + 4
    emit(f"{row}  // {lo}-{hi}")
emit("")

emit("    // ── New vertices: y=0.40mm row (z=0) ──────────────────────── v130 – v134")
y04 = 0.000400
for i, xr in enumerate(xvals_right):
    emit(f"    ( {xr:.5f}  {y04:.6f}  0.000 )  // {130+i}")

emit("")
emit("    // ── New vertices: x=20.5mm TM column (z=0) ───────────────── v135 – v136")
emit(f"    ( 0.02050  {y04:.6f}  0.000 )  // 135  TM bottom-right / Schlemm")
emit(f"    ( 0.02050  0.002400  0.000 )  // 136  TM top-right")
emit("")
emit("    // ── z=0.001 counterparts ──────────────────────────────────── v137 – v143")
for i, xr in enumerate(xvals_right):
    emit(f"    ( {xr:.5f}  {y04:.6f}  0.001 )  // {137+i}")
emit(f"    ( 0.02050  {y04:.6f}  0.001 )  // 142  ↔ v135")
emit(f"    ( 0.02050  0.002400  0.001 )  // 143  ↔ v136")
emit("")

# ─── LEFT HALF VERTICES ───────────────────────────────────────────────────────
emit("    // ═══════════════════════════════════════════════════════════════════════")
emit("    // LEFT HALF — new vertices 144–285")
emit("    // iL=0→x=-5mm, 1→x=-15mm, 2→x=-19.5mm, 3→x=-20mm, 4→x=-21mm")
emit("    // ═══════════════════════════════════════════════════════════════════════")
emit("")

xvals_left = [-0.00500, -0.01500, -0.01950, -0.02000, -0.02100]

emit("    // ── z = 0 layer ────────────────────────────────────────── v144 – v208")
for j in range(13):
    emit(f"    // j={j}  {ylabels[j]}")
    for iL in range(5):
        vid = 144 + iL + j*5
        emit(f"    ( {xvals_left[iL]:.5f}  {yvals[j]:.6f}  0.000 )  // {vid:3d}  VL({iL},{j})")
emit("")

emit("    // ── z = 1 mm layer ───────────────────────────────────────── v209 – v273")
for j in range(13):
    row = "    " + "  ".join(
        f"( {xvals_left[iL]:.5f}  {yvals[j]:.6f}  0.001 )" for iL in range(5)
    )
    lo = 209 + j*5
    hi = lo + 4
    emit(f"{row}  // {lo}-{hi}")
emit("")

emit("    // ── New vertices: y=0.40mm row left (z=0) ────────────────── v274 – v277")
for iL in range(4):
    emit(f"    ( {xvals_left[iL]:.5f}  {y04:.6f}  0.000 )  // {274+iL}  VL{iL}_0b x={xvals_left[iL]*1000:.1f}mm")
emit("")
emit("    // ── y=0.40mm row left (z=0.001) ──────────────────────────── v278 – v281")
for iL in range(4):
    emit(f"    ( {xvals_left[iL]:.5f}  {y04:.6f}  0.001 )  // {278+iL}")
emit("")

emit("    // ── TM left column x=-20.5mm ──────────────────────────────── v282 – v285")
emit(f"    (-0.02050  {y04:.6f}  0.000 )  // 282  TM_left bottom  y=0.40mm z=0")
emit( "    (-0.02050  0.002400  0.000 )  // 283  TM_left top     y=2.40mm z=0")
emit(f"    (-0.02050  {y04:.6f}  0.001 )  // 284  TM_left bottom  y=0.40mm z=1mm")
emit( "    (-0.02050  0.002400  0.001 )  // 285  TM_left top     y=2.40mm z=1mm")
emit(");")
emit("")

# ─── BLOCKS ──────────────────────────────────────────────────────────────────
emit("// ── Blocks ────────────────────────────────────────────────────────────────────")
emit("// x cells: col0(5mm)=10  col1(10mm)=20  col2(4.5mm)=9  col3(0.5mm)=1  TM(0.5mm)=1")
emit("// y cells: row0a=1  row0b=4  row1=2  row2=1  row3=4  row4=5  row5=5")
emit("//          row6a=5  row6b=5  row7=7  row8=8  row9=1  row10=4")
emit("")
emit("blocks\n(")

emit("    // ════════════════════════════════════════════════════════════════════")
emit("    // RIGHT HALF — original blocks (unchanged)")
emit("    // ════════════════════════════════════════════════════════════════════")
emit("")

# Helper for right blocks
def Rv(i,j): return VR(i,j)
def Rvz(i,j): return VRz(i,j)

# v130+i special row
def v0b(i): return 130+i  # y=0.4mm z=0
def v0bz(i): return 137+i # y=0.4mm z=1mm
def vTM0(): return 135
def vTM1(): return 136
def vTMz0(): return 142
def vTMz1(): return 143

emit("    // ── Row 0a: y=[0, 0.40mm] ─────────────────────────────────────────────")
right_0a = [
    ("B00a", [Rv(0,0),Rv(1,0),v0b(1),v0b(0),  Rvz(0,0),Rvz(1,0),v0bz(1),v0bz(0)], 10, 1),
    ("B01a", [Rv(1,0),Rv(2,0),v0b(2),v0b(1),  Rvz(1,0),Rvz(2,0),v0bz(2),v0bz(1)], 20, 1),
    ("B02aa",[Rv(2,0),Rv(3,0),v0b(3),v0b(2),  Rvz(2,0),Rvz(3,0),v0bz(3),v0bz(2)],  9, 1),
    ("B02ba",[Rv(3,0),Rv(4,0),v0b(4),v0b(3),  Rvz(3,0),Rvz(4,0),v0bz(4),v0bz(3)],  1, 1),
]
for name, vs, nx, ny in right_0a:
    emit_hex(vs, nx, ny, comment=name)
emit("")

emit("    // ── Row 0b: y=[0.40, 2.40mm] — TM level ─────────────────────────────")
right_0b = [
    ("B00b", [v0b(0),v0b(1),Rv(1,1),Rv(0,1),  v0bz(0),v0bz(1),Rvz(1,1),Rvz(0,1)], 10, 4),
    ("B01b", [v0b(1),v0b(2),Rv(2,1),Rv(1,1),  v0bz(1),v0bz(2),Rvz(2,1),Rvz(1,1)], 20, 4),
    ("B02ab",[v0b(2),v0b(3),Rv(3,1),Rv(2,1),  v0bz(2),v0bz(3),Rvz(3,1),Rvz(2,1)],  9, 4),
    ("B02bb",[v0b(3),v0b(4),Rv(4,1),Rv(3,1),  v0bz(3),v0bz(4),Rvz(4,1),Rvz(3,1)],  1, 4),
]
for name, vs, nx, ny in right_0b:
    emit_hex(vs, nx, ny, comment=name)
TM_vs = [v0b(4),vTM0(),vTM1(),Rv(4,1),  v0bz(4),vTMz0(),vTMz1(),Rvz(4,1)]
emit_hex(TM_vs, 1, 4, zone_token="tm_zone", comment="B_TM")
emit("")

# Rows 1-3: no special zones, all 4 right columns present
rows_simple = [
    ("Row 1: y=[2.40, 3.00mm]", 1, 2, 2),
    ("Row 2: y=[3.00, 3.16mm]", 2, 3, 1),
    ("Row 3: y=[3.16, 4.80mm]", 3, 4, 4),
]
for label, j0, j1, ny in rows_simple:
    emit(f"    // ── {label} ─────────────────")
    for i0,i1,nx in [(0,1,10),(1,2,20),(2,3,9),(3,4,1)]:
        vs = [Rv(i0,j0),Rv(i1,j0),Rv(i1,j1),Rv(i0,j1),
              Rvz(i0,j0),Rvz(i1,j0),Rvz(i1,j1),Rvz(i0,j1)]
        emit_hex(vs, nx, ny)
    emit("")

emit("    // ── Row 4: y=[4.80, 7.20mm] — iris level — col0 only ─────────────────")
j0,j1 = 4,5; ny=5
for i0,i1,nx in [(0,1,10)]:
    vs = [Rv(i0,j0),Rv(i1,j0),Rv(i1,j1),Rv(i0,j1),
          Rvz(i0,j0),Rvz(i1,j0),Rvz(i1,j1),Rvz(i0,j1)]
    emit_hex(vs, nx, ny, comment="B12  right of pupil")
emit("    // cols 1-3 (x=[5,20mm]) → IRIS SOLID")
emit("")

emit("    // ── Row 5: y=[7.20, 9.60mm] ──────────────────────────────────────────")
j0,j1 = 5,6; ny=5
for i0,i1,nx in [(0,1,10),(1,2,20),(2,3,9),(3,4,1)]:
    vs = [Rv(i0,j0),Rv(i1,j0),Rv(i1,j1),Rv(i0,j1),
          Rvz(i0,j0),Rvz(i1,j0),Rvz(i1,j1),Rvz(i0,j1)]
    emit_hex(vs, nx, ny)
emit("")

emit("    // ── Row 6a: y=[9.60, 12.00mm] — cols 0-1 = LENS SOLID ───────────────")
j0,j1 = 6,7; ny=5
for i0,i1,nx in [(2,3,9),(3,4,1)]:
    vs = [Rv(i0,j0),Rv(i1,j0),Rv(i1,j1),Rv(i0,j1),
          Rvz(i0,j0),Rvz(i1,j0),Rvz(i1,j1),Rvz(i0,j1)]
    emit_hex(vs, nx, ny)
emit("")

emit("    // ── Row 6b: y=[12.00, 14.40mm] — cols 0-1 = LENS SOLID ──────────────")
j0,j1 = 7,8; ny=5
for i0,i1,nx in [(2,3,9),(3,4,1)]:
    vs = [Rv(i0,j0),Rv(i1,j0),Rv(i1,j1),Rv(i0,j1),
          Rvz(i0,j0),Rvz(i1,j0),Rvz(i1,j1),Rvz(i0,j1)]
    emit_hex(vs, nx, ny)
emit("")

# Rows 7-10 with vitreous_zone
rows_vit = [
    ("Row 7:  y=[14.40, 18.00mm]",  8, 9,  7),
    ("Row 8:  y=[18.00, 21.92mm]",  9, 10, 8),
    ("Row 9:  y=[21.92, 22.08mm]", 10, 11, 1),
    ("Row 10: y=[22.08, 24.00mm]", 11, 12, 4),
]
for label, j0, j1, ny in rows_vit:
    emit(f"    // ── {label} ─")
    for i0,i1,nx in [(0,1,10),(1,2,20),(2,3,9),(3,4,1)]:
        vs = [Rv(i0,j0),Rv(i1,j0),Rv(i1,j1),Rv(i0,j1),
              Rvz(i0,j0),Rvz(i1,j0),Rvz(i1,j1),Rvz(i0,j1)]
        emit_hex(vs, nx, ny, zone_token="vitreous_zone")
    emit("")

# ─── LEFT HALF BLOCKS ─────────────────────────────────────────────────────────
emit("    // ════════════════════════════════════════════════════════════════════")
emit("    // LEFT HALF — mirrored blocks")
emit("    // i-direction goes from more-negative to less-negative (toward x=0).")
emit("    // x=0 vertices (i=0) are shared with right-half blocks.")
emit("    // ════════════════════════════════════════════════════════════════════")
emit("")

def Lv(iL,j): return VL(iL,j)
def Lvz(iL,j): return VLz(iL,j)
def Lv0b(iL): return 274+iL if iL<4 else 130  # iL=4 would be x=0 → use v130
# Note: x=0, y=0.4mm, z=0 = v130 (existing); iL→x: 0=-5,1=-15,2=-19.5,3=-20

emit("    // ── Row 0a left: y=[0, 0.40mm] ───────────────────────────────────────")
# Left row0a: 4 blocks, col0L-col3L (x=[-20,0])
# col0L: from VL(0,0)=144 to VR(0,0)=0  (x=-5 to x=0)
# col1L: VL(1,0) to VL(0,0) (x=-15 to x=-5)
# col2L: VL(2,0) to VL(1,0)
# col3L: VL(3,0) to VL(2,0)

col_info_left_0a = [
    ("B00aL", [Lv(0,0),VR(0,0),  130,    274,    Lvz(0,0),VRz(0,0), 137,   278],  10, 1),
    ("B01aL", [Lv(1,0),Lv(0,0),  274,    275,    Lvz(1,0),Lvz(0,0), 278,   279],  20, 1),
    ("B02aaL",[Lv(2,0),Lv(1,0),  275,    276,    Lvz(2,0),Lvz(1,0), 279,   280],   9, 1),
    ("B02baL",[Lv(3,0),Lv(2,0),  276,    277,    Lvz(3,0),Lvz(2,0), 280,   281],   1, 1),
]
for name, vs, nx, ny in col_info_left_0a:
    emit_hex(vs, nx, ny, comment=name)
emit("")

emit("    // ── Row 0b left: y=[0.40, 2.40mm] ────────────────────────────────────")
col_info_left_0b = [
    ("B00bL", [274,    130,  VR(0,1), Lv(0,1),  278,    137,   VRz(0,1),Lvz(0,1)], 10, 4),
    ("B01bL", [275,    274,  Lv(0,1), Lv(1,1),  279,    278,   Lvz(0,1),Lvz(1,1)], 20, 4),
    ("B02abL",[276,    275,  Lv(1,1), Lv(2,1),  280,    279,   Lvz(1,1),Lvz(2,1)],  9, 4),
    ("B02bbL",[277,    276,  Lv(2,1), Lv(3,1),  281,    280,   Lvz(2,1),Lvz(3,1)],  1, 4),
]
for name, vs, nx, ny in col_info_left_0b:
    emit_hex(vs, nx, ny, comment=name)
# TM left block: x=[-20.5,-20mm], y=[0.40,2.40mm]
TML_vs = [282, 277, Lv(3,1), 283, 284, 281, Lvz(3,1), 285]
emit_hex(TML_vs, 1, 4, zone_token="tm_zone_left", comment="B_TML")
emit("")

# Rows 1-3 left
rows_simple_left = [
    ("Row 1 left: y=[2.40, 3.00mm]", 1, 2, 2),
    ("Row 2 left: y=[3.00, 3.16mm]", 2, 3, 1),
    ("Row 3 left: y=[3.16, 4.80mm]", 3, 4, 4),
]
for label, j0, j1, ny in rows_simple_left:
    emit(f"    // ── {label} ─")
    for iL0, iL1, nx, r_iL, r_i, is_rightmost in [
        (0, -1, 10, False, 0, True),   # col0L: VL(0) to VR(0)
        (1, 0,  20, False, 0, False),  # col1L: VL(1) to VL(0)
        (2, 1,   9, False, 0, False),
        (3, 2,   1, False, 0, False),
    ]:
        # Build hex for colL: from iL0 toward right
        if iL0==0:  # rightmost left col: VL(0) to VR(0)
            vs = [Lv(0,j0),VR(0,j0),VR(0,j1),Lv(0,j1),
                  Lvz(0,j0),VRz(0,j0),VRz(0,j1),Lvz(0,j1)]
        else:
            vs = [Lv(iL0,j0),Lv(iL1,j0),Lv(iL1,j1),Lv(iL0,j1),
                  Lvz(iL0,j0),Lvz(iL1,j0),Lvz(iL1,j1),Lvz(iL0,j1)]
        emit_hex(vs, nx, ny)
    emit("")

emit("    // ── Row 4 left: y=[4.80, 7.20mm] — pupil region col0L only ──────────")
emit("    // col0L (x=[-5,0mm]) = fluid (pupil between two iris blocks)")
j0,j1=4,5; ny=5
vs = [Lv(0,j0),VR(0,j0),VR(0,j1),Lv(0,j1),
      Lvz(0,j0),VRz(0,j0),VRz(0,j1),Lvz(0,j1)]
emit_hex(vs, 10, ny, comment="B12L pupil-left")
emit("    // cols 1L-3L (x=[-20,-5mm]) → IRIS SOLID (not in fluid)")
emit("")

emit("    // ── Row 5 left: y=[7.20, 9.60mm] ────────────────────────────────────")
j0,j1=5,6; ny=5
for iL0, iL1, nx in [(0,-1,10),(1,0,20),(2,1,9),(3,2,1)]:
    if iL0==0:
        vs = [Lv(0,j0),VR(0,j0),VR(0,j1),Lv(0,j1),
              Lvz(0,j0),VRz(0,j0),VRz(0,j1),Lvz(0,j1)]
    else:
        vs = [Lv(iL0,j0),Lv(iL1,j0),Lv(iL1,j1),Lv(iL0,j1),
              Lvz(iL0,j0),Lvz(iL1,j0),Lvz(iL1,j1),Lvz(iL0,j1)]
    emit_hex(vs, nx, ny)
emit("")

emit("    // ── Row 6a left: y=[9.60, 12.00mm] — cols 0L-1L = LENS SOLID ────────")
j0,j1=6,7; ny=5
for iL0, iL1, nx in [(2,1,9),(3,2,1)]:
    vs = [Lv(iL0,j0),Lv(iL1,j0),Lv(iL1,j1),Lv(iL0,j1),
          Lvz(iL0,j0),Lvz(iL1,j0),Lvz(iL1,j1),Lvz(iL0,j1)]
    emit_hex(vs, nx, ny)
emit("")

emit("    // ── Row 6b left: y=[12.00, 14.40mm] — cols 0L-1L = LENS SOLID ───────")
j0,j1=7,8; ny=5
for iL0, iL1, nx in [(2,1,9),(3,2,1)]:
    vs = [Lv(iL0,j0),Lv(iL1,j0),Lv(iL1,j1),Lv(iL0,j1),
          Lvz(iL0,j0),Lvz(iL1,j0),Lvz(iL1,j1),Lvz(iL0,j1)]
    emit_hex(vs, nx, ny)
emit("")

# Rows 7-10 left with vitreous_zone
rows_vit_left = [
    ("Row 7  left: y=[14.40, 18.00mm]",  8, 9,  7),
    ("Row 8  left: y=[18.00, 21.92mm]",  9, 10, 8),
    ("Row 9  left: y=[21.92, 22.08mm]", 10, 11, 1),
    ("Row 10 left: y=[22.08, 24.00mm]", 11, 12, 4),
]
for label, j0, j1, ny in rows_vit_left:
    emit(f"    // ── {label} ─")
    for iL0, iL1, nx in [(0,-1,10),(1,0,20),(2,1,9),(3,2,1)]:
        if iL0==0:
            vs = [Lv(0,j0),VR(0,j0),VR(0,j1),Lv(0,j1),
                  Lvz(0,j0),VRz(0,j0),VRz(0,j1),Lvz(0,j1)]
        else:
            vs = [Lv(iL0,j0),Lv(iL1,j0),Lv(iL1,j1),Lv(iL0,j1),
                  Lvz(iL0,j0),Lvz(iL1,j0),Lvz(iL1,j1),Lvz(iL0,j1)]
        emit_hex(vs, nx, ny, zone_token="vitreous_zone")
    emit("")

emit(");")
emit("")
emit("edges   ();")
emit("")

# ─── BOUNDARY ─────────────────────────────────────────────────────────────────
emit("boundary\n(")

# Lateral needle_* strips at x=±20 mm (BCs usually off); IVI/paracentesis via internal
# baffles at x=0 — topoSetDict.internalNeedles + createBafflesDict in eye-fsi-tc0.
emit(f"""    // ── Lateral needle placeholders — mirrored at x=±20 mm ───────────────────
    needle_inlet_left
    {{
        type patch;
        faces ( ( {VL(3,10)} {VL(3,11)} {VLz(3,11)} {VLz(3,10)} ) );
    }}
    needle_inlet_right
    {{
        type patch;
        faces ( ( {VR(4,10)} {VR(4,11)} {VRz(4,11)} {VRz(4,10)} ) );
    }}
    needle_outlet_left
    {{
        type patch;
        faces ( ( {VL(3,2)} {VL(3,3)} {VLz(3,3)} {VLz(3,2)} ) );
    }}
    needle_outlet_right
    {{
        type patch;
        faces ( ( 14 19 84 79 ) );   // x=+20 mm outer face (col4 row2 — not col3|col4 internal)
    }}
""")

emit(f"""    // ── sclera_left_lower — x=-20 mm (mirror sclera_right); omit needle row ──
    sclera_left_lower
    {{
        type wall;
        faces
        (
            ( {VL(3,0)} 277 281 {VLz(3,0)} )
            ( {VL(3,1)} {VL(3,2)} {VLz(3,2)} {VLz(3,1)} )
            ( {VL(3,3)} {VL(3,4)} {VLz(3,4)} {VLz(3,3)} )
        );
    }}

    // ── sclera_left_upper — x=-20 mm; omit AC inlet row & needle_inlet row ─────
    sclera_left_upper
    {{
        type wall;
        faces
        (
            ( {VL(3,6)} {VL(3,7)} {VLz(3,7)} {VLz(3,6)} )
            ( {VL(3,7)} {VL(3,8)} {VLz(3,8)} {VLz(3,7)} )
            ( {VL(3,8)} {VL(3,9)} {VLz(3,9)} {VLz(3,8)} )
            ( {VL(3,9)} {VL(3,10)} {VLz(3,10)} {VLz(3,9)} )
            ( {VL(3,11)} {VL(3,12)} {VLz(3,12)} {VLz(3,11)} )
        );
    }}
""")

emit("""    // ── sclera_right — unchanged (x=+20 mm) ───────────────────────────────────
    sclera_right
    {
        type wall;
        faces
        (
            (   4 134 141  69 )
            (   9  14  79  74 )
            (  19  24  89  84 )
        );
    }

    // ── sclera_right_upper — unchanged ─────────────────────────────────────────
    sclera_right_upper
    {
        type wall;
        faces
        (
            ( 34 39 104  99 )
            ( 39 44 109 104 )
            ( 44 49 114 109 )
            ( 49 54 119 114 )
            ( 59 64 129 124 )
        );
    }

    // ── sclera_top — y=24 mm (both halves) ──────────────────────────────────────
    sclera_top
    {
        type wall;
        faces
        (
            ( 60 61 126 125 )
            ( 61 62 127 126 )
            ( 62 63 128 127 )
            ( 63 64 129 128 )
            ( 204 60 125 269 )
            ( 205 204 269 270 )
            ( 206 205 270 271 )
            ( 207 206 271 272 )
        );
    }

    // ── cornea_fsi — y=0 plane ───────────────────────────────────────────────────
    cornea_fsi
    {
        type wall;
        faces
        (
            (   0   1  66  65 )
            (   1   2  67  66 )
            (   2   3  68  67 )
            (   3   4  69  68 )
            ( 144   0  65 209 )
            ( 145 144 209 210 )
            ( 146 145 210 211 )
            ( 147 146 211 212 )
        );
    }
""")

emit(f"""    // ── Lens / iris — original right + mirrored left ───────────────────────────
    lens_bottom
    {{
        type wall;
        faces
        (
            ( 30 31  96  95 )
            ( 31 32  97  96 )
        );
    }}
    lens_bottom_left
    {{
        type wall;
        faces
        (
            ( 174 30 95 239 )
            ( 175 174 239 240 )
        );
    }}
    lens_right
    {{
        type wall;
        faces
        (
            ( 32 37 102  97 )
            ( 37 42 107 102 )
        );
    }}
    lens_left
    {{
        type wall;
        faces ();
    }}
    lens_top
    {{
        type wall;
        faces
        (
            ( 40 41 106 105 )
            ( 41 42 107 106 )
        );
    }}
    lens_top_left
    {{
        type wall;
        faces
        (
            ( 184 40 105 249 )
            ( 185 184 249 250 )
        );
    }}

    iris_bottom
    {{
        type wall;
        faces
        (
            ( 21 22  87  86 )
            ( 22 23  88  87 )
            ( 23 24  89  88 )
            ( 164 165 230 229 )
            ( 165 166 231 230 )
            ( 166 167 232 231 )
        );
    }}
    iris_pupil
    {{
        type wall;
        faces ( ( 21 26  91  86 ) );
    }}
    iris_pupil_left
    {{
        type wall;
        faces ( ( 164 169 234 229 ) );
    }}
    iris_top
    {{
        type wall;
        faces
        (
            ( 26 27  92  91 )
            ( 27 28  93  92 )
            ( 28 29  94  93 )
            ( 171 170 236 235 )
            ( 172 171 237 236 )
        );
    }}
""")

emit(f"""    // ── TM limbus caps — y=[0.40,2.40] strips x∈[±20,±20.5]mm (no AC neighbour) ──
    tm_limbus_wall
    {{
        type wall;
        faces
        (
            ( 134 135 142 141 )
            (   9  74 143 136 )
            ( 282 277 281 284 )
            ( 283 285 217 152 )
        );
    }}

    // ── Production / TM ─────────────────────────────────────────────────────────
    ac_inlet
    {{
        type patch;
        faces ( ( 29 34 99 94 ) );
    }}
    ac_inlet_left
    {{
        type patch;
        faces ( ( {VL(3,5)} {VL(3,6)} {VLz(3,6)} {VLz(3,5)} ) );
    }}
    outlet_tm
    {{
        type patch;
        faces ( ( 135 136 143 142 ) );
    }}
    outlet_tm_left
    {{
        type patch;
        faces ( ( 282 283 285 284 ) );
    }}
""")

emit("    front")
emit("    {")
emit("        type empty;")
emit("        faces")
emit("        (")
for h in all_hex:
    emit(f"            ( {h[0]} {h[1]} {h[2]} {h[3]} )")
emit("        );")
emit("    }")
emit("")
emit("    back")
emit("    {")
emit("        type empty;")
emit("        faces")
emit("        (")
for h in all_hex:
    emit(f"            ( {h[4]} {h[5]} {h[6]} {h[7]} )")
emit("        );")
emit("    }")
emit(");")

print("\n".join(lines))
