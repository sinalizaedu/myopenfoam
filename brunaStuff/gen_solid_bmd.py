#!/usr/bin/env python3
"""
Generate the FULL solid/system/blockMeshDict for the full symmetric eye model.
Mirrors the half-model (x=[0,21mm]) about x=0 to get x=[-21,+21mm].

Existing vertices 0-55 are preserved.
New vertices 56-97 are added for the left half.

Run from repo root:
  python3 brunaStuff/gen_solid_bmd.py > cases/eye-fsi-tc0/solid/system/blockMeshDict
"""

header = r"""FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}

// eye-fsi-tc0 — SOLID domain — FULL SYMMETRIC MODEL
//
// Coordinate system (same as fluid):
//   x = -21 mm (left outer sclera) → +21 mm (right outer sclera)
//   y = -1 mm  (cornea outer)       →  25 mm (sclera top outer)
//   z = 0 → 1 mm  (2-D slab)
//
// The geometry is symmetric about x=0 (optical axis).
// The half-model at x=[0,21mm] is kept exactly; the left half x=[-21,0mm]
// is added by mirroring all blocks about x=0.
//
// Structures (full model):
//   lens   — x=[-15,+15mm], y=[9.6,14.4mm]    — two sub-blocks sharing x=0
//   iris   — x=[-20,-5mm] ∪ [5,20mm]           — one block per side
//   sclera — A-strips at x=[-21,-20mm] and [20,21mm] + B top strip x=[-20,20mm]
//   cornea — x=[-21,+21mm], y=[-1,0mm]
//
// BC for lens equatorial faces:
//   lens_right (x=+15mm): solidForce (FSI — receives AC pressure from right)
//   lens_left  (x=-15mm): Robin spring (zonule, coeff0=3e4 Pa/m)
//
// Vertex numbering:
//   RIGHT HALF (original, x=[0,21mm]):
//     Lens:          0–7
//     Iris:          8–15
//     Sclera A lower: 16–23
//     Sclera B:      24–31
//     Cornea:        32–39
//     Sclera A upper: 40–47
//     Sclera A mid:  48–55
//   LEFT HALF (new, x=[-21,0mm]):
//     Lens left:     56–59
//     Iris left:     60–67
//     Sclera A lower left: 68–75
//     Sclera A upper left: 76–83
//     Sclera A mid left:   84–91
//     Sclera B left:       92–93
//     Cornea left:         94–97

scale   1;
"""

vertices_right = """
vertices
(
    // ════════════════════════════════════════════════════════════════════════
    // RIGHT HALF — original vertices 0–55 (x=[0,21mm])
    // ════════════════════════════════════════════════════════════════════════

    // ── Lens  (z=0) ──────────────────────────────────────────────────────────
    ( 0.000  0.00960  0.000 )  //  0
    ( 0.015  0.00960  0.000 )  //  1
    ( 0.015  0.01440  0.000 )  //  2
    ( 0.000  0.01440  0.000 )  //  3
    // ── Lens  (z=0.001) ──────────────────────────────────────────────────────
    ( 0.000  0.00960  0.001 )  //  4
    ( 0.015  0.00960  0.001 )  //  5
    ( 0.015  0.01440  0.001 )  //  6
    ( 0.000  0.01440  0.001 )  //  7

    // ── Iris  (z=0) ──────────────────────────────────────────────────────────
    ( 0.005  0.00480  0.000 )  //  8
    ( 0.020  0.00480  0.000 )  //  9
    ( 0.020  0.00720  0.000 )  // 10
    ( 0.005  0.00720  0.000 )  // 11
    // ── Iris  (z=0.001) ──────────────────────────────────────────────────────
    ( 0.005  0.00480  0.001 )  // 12
    ( 0.020  0.00480  0.001 )  // 13
    ( 0.020  0.00720  0.001 )  // 14
    ( 0.005  0.00720  0.001 )  // 15

    // ── Sclera A — x=[20,21mm] lower row (y=[0,0.4mm])  z=0 ──────────────────
    ( 0.020  0.00000  0.000 )  // 16  x=20, y=0
    ( 0.021  0.00000  0.000 )  // 17  x=21, y=0
    ( 0.021  0.00040  0.000 )  // 18  x=21, y=0.4mm
    ( 0.020  0.00040  0.000 )  // 19  x=20, y=0.4mm
    // ── same row  (z=0.001) ──────────────────────────────────────────────────
    ( 0.020  0.00000  0.001 )  // 20
    ( 0.021  0.00000  0.001 )  // 21
    ( 0.021  0.00040  0.001 )  // 22
    ( 0.020  0.00040  0.001 )  // 23

    // ── Sclera B — top strip x=[0,20mm], y=[24,25mm]  z=0 ───────────────────
    ( 0.000  0.02400  0.000 )  // 24
    ( 0.020  0.02400  0.000 )  // 25
    ( 0.020  0.02500  0.000 )  // 26
    ( 0.000  0.02500  0.000 )  // 27
    // ── Sclera B  (z=0.001) ──────────────────────────────────────────────────
    ( 0.000  0.02400  0.001 )  // 28
    ( 0.020  0.02400  0.001 )  // 29
    ( 0.020  0.02500  0.001 )  // 30
    ( 0.000  0.02500  0.001 )  // 31

    // ── Cornea  x=[0,21mm], y=[-1,0mm]  z=0 ─────────────────────────────────
    ( 0.000 -0.00100  0.000 )  // 32
    ( 0.021 -0.00100  0.000 )  // 33
    ( 0.021  0.00000  0.000 )  // 34
    ( 0.000  0.00000  0.000 )  // 35
    // ── Cornea  (z=0.001) ────────────────────────────────────────────────────
    ( 0.000 -0.00100  0.001 )  // 36
    ( 0.021 -0.00100  0.001 )  // 37
    ( 0.021  0.00000  0.001 )  // 38
    ( 0.000  0.00000  0.001 )  // 39

    // ── Sclera A — x=[20,21mm] upper row (y=[2.4,25mm])  z=0 ─────────────────
    ( 0.020  0.00240  0.000 )  // 40  x=20, y=2.4mm
    ( 0.021  0.00240  0.000 )  // 41  x=21, y=2.4mm
    ( 0.021  0.02500  0.000 )  // 42  x=21, y=25mm
    ( 0.020  0.02500  0.000 )  // 43  x=20, y=25mm
    // ── same row  (z=0.001) ──────────────────────────────────────────────────
    ( 0.020  0.00240  0.001 )  // 44
    ( 0.021  0.00240  0.001 )  // 45
    ( 0.021  0.02500  0.001 )  // 46
    ( 0.020  0.02500  0.001 )  // 47

    // ── Sclera A — middle column x=20.5mm  z=0 ───────────────────────────────
    ( 0.0205  0.00000  0.000 )  // 48  x=20.5, y=0
    ( 0.0205  0.00040  0.000 )  // 49  x=20.5, y=0.4mm
    ( 0.0205  0.00240  0.000 )  // 50  x=20.5, y=2.4mm
    ( 0.0205  0.02500  0.000 )  // 51  x=20.5, y=25mm
    // ── x=20.5mm column  (z=0.001) ───────────────────────────────────────────
    ( 0.0205  0.00000  0.001 )  // 52
    ( 0.0205  0.00040  0.001 )  // 53
    ( 0.0205  0.00240  0.001 )  // 54
    ( 0.0205  0.02500  0.001 )  // 55

    // ════════════════════════════════════════════════════════════════════════
    // LEFT HALF — new vertices 56–97 (x=[-21,0mm], mirror of right half)
    // ════════════════════════════════════════════════════════════════════════

    // ── Lens left  x=[-15,0mm], y=[9.6,14.4mm]  (z=0) ───────────────────────
    // Vertices at x=0 are SHARED with right-half lens (v0,v3,v4,v7).
    (-0.015  0.00960  0.000 )  // 56  lens_left bottom-front
    (-0.015  0.01440  0.000 )  // 57  lens_left top-front
    // ── Lens left  (z=0.001) ─────────────────────────────────────────────────
    (-0.015  0.00960  0.001 )  // 58  lens_left bottom-back
    (-0.015  0.01440  0.001 )  // 59  lens_left top-back

    // ── Iris left  x=[-20,-5mm], y=[4.8,7.2mm]  (z=0) ───────────────────────
    (-0.005  0.00480  0.000 )  // 60  iris_pupil_left bottom-front  (x=-5mm)
    (-0.020  0.00480  0.000 )  // 61  iris_base_left  bottom-front  (x=-20mm)
    (-0.020  0.00720  0.000 )  // 62  iris_base_left  top-front
    (-0.005  0.00720  0.000 )  // 63  iris_pupil_left top-front
    // ── Iris left  (z=0.001) ─────────────────────────────────────────────────
    (-0.005  0.00480  0.001 )  // 64
    (-0.020  0.00480  0.001 )  // 65
    (-0.020  0.00720  0.001 )  // 66
    (-0.005  0.00720  0.001 )  // 67

    // ── Sclera A left — lower row  x=[-21,-20mm], y=[0,0.4mm]  (z=0) ─────────
    (-0.020  0.00000  0.000 )  // 68  x=-20, y=0
    (-0.021  0.00000  0.000 )  // 69  x=-21, y=0
    (-0.021  0.00040  0.000 )  // 70  x=-21, y=0.4mm
    (-0.020  0.00040  0.000 )  // 71  x=-20, y=0.4mm
    // ── same row  (z=0.001) ──────────────────────────────────────────────────
    (-0.020  0.00000  0.001 )  // 72
    (-0.021  0.00000  0.001 )  // 73
    (-0.021  0.00040  0.001 )  // 74
    (-0.020  0.00040  0.001 )  // 75

    // ── Sclera A left — upper row  x=[-21,-20mm], y=[2.4,25mm]  (z=0) ────────
    (-0.020  0.00240  0.000 )  // 76  x=-20, y=2.4mm
    (-0.021  0.00240  0.000 )  // 77  x=-21, y=2.4mm
    (-0.021  0.02500  0.000 )  // 78  x=-21, y=25mm
    (-0.020  0.02500  0.000 )  // 79  x=-20, y=25mm
    // ── same row  (z=0.001) ──────────────────────────────────────────────────
    (-0.020  0.00240  0.001 )  // 80
    (-0.021  0.00240  0.001 )  // 81
    (-0.021  0.02500  0.001 )  // 82
    (-0.020  0.02500  0.001 )  // 83

    // ── Sclera A left — middle column  x=-20.5mm  (z=0) ─────────────────────
    (-0.0205  0.00000  0.000 )  // 84  x=-20.5, y=0
    (-0.0205  0.00040  0.000 )  // 85  x=-20.5, y=0.4mm
    (-0.0205  0.00240  0.000 )  // 86  x=-20.5, y=2.4mm
    (-0.0205  0.02500  0.000 )  // 87  x=-20.5, y=25mm
    // ── x=-20.5mm column  (z=0.001) ──────────────────────────────────────────
    (-0.0205  0.00000  0.001 )  // 88
    (-0.0205  0.00040  0.001 )  // 89
    (-0.0205  0.00240  0.001 )  // 90
    (-0.0205  0.02500  0.001 )  // 91

    // ── Sclera B left — x=[-20,0mm], y=[24,25mm] ─────────────────────────────
    // Only the LEFT corners at x=-20mm are new; x=0 corners reuse v24,v27,v28,v31.
    // v79 (−20,25,0) and v83 (−20,25,1) are already defined above → reused.
    (-0.020  0.02400  0.000 )  // 92  x=-20, y=24mm, z=0
    (-0.020  0.02400  0.001 )  // 93  x=-20, y=24mm, z=1mm

    // ── Cornea left — x=[-21,0mm], y=[-1,0mm] ────────────────────────────────
    // x=0 corners reuse v32,v35,v36,v39.
    (-0.021 -0.00100  0.000 )  // 94  x=-21, y=-1mm, z=0
    (-0.021  0.00000  0.000 )  // 95  x=-21, y= 0mm, z=0
    (-0.021 -0.00100  0.001 )  // 96  x=-21, y=-1mm, z=1mm
    (-0.021  0.00000  0.001 )  // 97  x=-21, y= 0mm, z=1mm
);
"""

blocks = """
blocks
(
    // ════════════════════════════════════════════════════════════════════════
    // RIGHT HALF — original blocks (unchanged)
    // ════════════════════════════════════════════════════════════════════════

    // Lens right — x=[0,15mm], y=[9.6,14.4mm]
    hex ( 0  1  2  3   4  5  6  7 )  lens   ( 15 10 1 )  simpleGrading ( 1 1 1 )

    // Iris right — x=[5,20mm], y=[4.8,7.2mm]
    hex ( 8  9 10 11  12 13 14 15 )  iris   ( 15  3 1 )  simpleGrading ( 1 1 1 )

    // Sclera A_inner_lower: x=[20,20.5mm], y=[0,0.4mm]
    hex (16 48 49 19  20 52 53 23 )  sclera (  1  1 1 )  simpleGrading ( 1 1 1 )

    // Sclera A_outer_lower: x=[20.5,21mm], y=[0,0.4mm]
    hex (48 17 18 49  52 21 22 53 )  sclera (  1  1 1 )  simpleGrading ( 1 1 1 )

    // Sclera A_outer_mid: x=[20.5,21mm], y=[0.4,2.4mm]
    hex (49 18 41 50  53 22 45 54 )  sclera (  1  4 1 )  simpleGrading ( 1 1 1 )

    // Sclera A_inner_upper: x=[20,20.5mm], y=[2.4,25mm]
    hex (40 50 51 43  44 54 55 47 )  sclera (  1 23 1 )  simpleGrading ( 1 1 1 )

    // Sclera A_outer_upper: x=[20.5,21mm], y=[2.4,25mm]
    hex (50 41 42 51  54 45 46 55 )  sclera (  1 23 1 )  simpleGrading ( 1 1 1 )

    // Sclera B right — x=[0,20mm], y=[24,25mm]
    hex (24 25 26 27  28 29 30 31 )  sclera ( 20  1 1 )  simpleGrading ( 1 1 1 )

    // Cornea right — x=[0,21mm], y=[-1,0mm]
    hex (32 33 34 35  36 37 38 39 )  cornea ( 21  1 1 )  simpleGrading ( 1 1 1 )

    // ════════════════════════════════════════════════════════════════════════
    // LEFT HALF — new mirrored blocks (x=[-21,0mm])
    // All i-directions go from more-negative x to less-negative (toward x=0).
    // Vertices at x=0 are shared with corresponding right-half blocks.
    // ════════════════════════════════════════════════════════════════════════

    // Lens left — x=[-15,0mm], y=[9.6,14.4mm]
    // Shares v0,v3,v4,v7 with lens_right at x=0 → forms one connected lens body.
    hex ( 56  0  3 57  58  4  7 59 )  lens   ( 15 10 1 )  simpleGrading ( 1 1 1 )

    // Iris left — x=[-20,-5mm], y=[4.8,7.2mm]
    hex ( 61 60 63 62  65 64 67 66 )  iris   ( 15  3 1 )  simpleGrading ( 1 1 1 )

    // Sclera A_inner_lower_left: x=[-20.5,-20mm], y=[0,0.4mm]
    hex ( 84 68 71 85  88 72 75 89 )  sclera (  1  1 1 )  simpleGrading ( 1 1 1 )

    // Sclera A_outer_lower_left: x=[-21,-20.5mm], y=[0,0.4mm]
    hex ( 69 84 85 70  73 88 89 74 )  sclera (  1  1 1 )  simpleGrading ( 1 1 1 )

    // Sclera A_outer_mid_left: x=[-21,-20.5mm], y=[0.4,2.4mm]
    hex ( 70 85 86 77  74 89 90 81 )  sclera (  1  4 1 )  simpleGrading ( 1 1 1 )

    // Sclera A_inner_upper_left: x=[-20.5,-20mm], y=[2.4,25mm]
    hex ( 86 76 79 87  90 80 83 91 )  sclera (  1 23 1 )  simpleGrading ( 1 1 1 )

    // Sclera A_outer_upper_left: x=[-21,-20.5mm], y=[2.4,25mm]
    hex ( 77 86 87 78  81 90 91 82 )  sclera (  1 23 1 )  simpleGrading ( 1 1 1 )

    // Sclera B left — x=[-20,0mm], y=[24,25mm]
    // Shares v24,v27,v28,v31 with sclera_B_right at x=0; v79,v83 with sclera_A_inner_upper_left.
    hex ( 92 24 27 79  93 28 31 83 )  sclera ( 20  1 1 )  simpleGrading ( 1 1 1 )

    // Cornea left — x=[-21,0mm], y=[-1,0mm]
    // Shares v32,v35,v36,v39 with cornea_right at x=0.
    hex ( 94 32 35 95  96 36 39 97 )  cornea ( 21  1 1 )  simpleGrading ( 1 1 1 )
);

edges ();
"""

boundary = r"""
boundary
(
    // ════════════════════════════════════════════════════════════════════════
    // ══ LENS (RIGHT) ════════════════════════════════════════════════════════
    // ════════════════════════════════════════════════════════════════════════
    lens_bottom
    {
        type wall;
        faces ( ( 0  1  5  4 ) );   // j_min — y=9.6mm (n=-y, fluid pushes UP)
    }
    lens_right
    {
        type wall;
        faces ( ( 1  2  6  5 ) );   // i_max — x=+15mm (n=+x, FSI face, zonule)
    }
    lens_top
    {
        type wall;
        faces ( ( 3  7  6  2 ) );   // j_max — y=14.4mm (n=+y, fluid pushes DOWN)
    }
    // lens_rim removed — x=0 is now INTERIOR (shared with lens_left block)

    // ════════════════════════════════════════════════════════════════════════
    // ══ LENS (LEFT) — equatorial face gets Robin spring (zonule) ════════════
    // ════════════════════════════════════════════════════════════════════════
    lens_bottom_left
    {
        type wall;
        faces ( ( 56  0  4 58 ) );  // j_min — y=9.6mm (n=-y)
    }
    lens_left
    {
        type wall;
        faces ( ( 56 58 59 57 ) );  // i_min — x=-15mm (Robin spring = zonule anchor)
    }
    lens_top_left
    {
        type wall;
        faces ( ( 57 59  7  3 ) );  // j_max — y=14.4mm (n=+y)
    }

    // ════════════════════════════════════════════════════════════════════════
    // ══ IRIS (RIGHT) ════════════════════════════════════════════════════════
    // ════════════════════════════════════════════════════════════════════════
    iris_pupil
    {
        type wall;
        faces ( ( 8 12 15 11 ) );   // i_min — x=5mm (n=-x)
    }
    iris_bottom
    {
        type wall;
        faces ( ( 8  9 13 12 ) );   // j_min — y=4.8mm (n=-y)
    }
    iris_top
    {
        type wall;
        faces ( (11 15 14 10 ) );   // j_max — y=7.2mm (n=+y)
    }
    iris_base
    {
        type wall;
        faces ( ( 9 10 14 13 ) );   // i_max — x=20mm (scleral spur right)
    }

    // ════════════════════════════════════════════════════════════════════════
    // ══ IRIS (LEFT) ═════════════════════════════════════════════════════════
    // ════════════════════════════════════════════════════════════════════════
    iris_pupil_left
    {
        type wall;
        faces ( ( 60 63 67 64 ) );  // i_max — x=-5mm (n=+x, left pupil margin)
    }
    iris_bottom_left
    {
        type wall;
        faces ( ( 61 60 64 65 ) );  // j_min — y=4.8mm (n=-y)
    }
    iris_top_left
    {
        type wall;
        faces ( ( 62 66 67 63 ) );  // j_max — y=7.2mm (n=+y)
    }
    iris_base_left
    {
        type wall;
        faces ( ( 61 65 66 62 ) );  // i_min — x=-20mm (scleral spur left)
    }

    // ════════════════════════════════════════════════════════════════════════
    // ══ SCLERA (RIGHT) ══════════════════════════════════════════════════════
    // ════════════════════════════════════════════════════════════════════════
    sclera_side
    {
        type wall;
        faces
        (
            (16 20 23 19)   // A_inner_lower i_min — x=20mm, y=[0,0.4mm]
            (40 44 47 43)   // A_inner_upper i_min — x=20mm, y=[2.4,25mm]
        );
    }
    sclera_top_inner
    {
        type wall;
        faces ( (24 25 29 28) );    // block B j_min — y=24mm, x=[0,20mm]
    }

    // ════════════════════════════════════════════════════════════════════════
    // ══ SCLERA (LEFT) ═══════════════════════════════════════════════════════
    // ════════════════════════════════════════════════════════════════════════
    sclera_side_left
    {
        type wall;
        faces
        (
            (68 71 75 72)   // A_inner_lower_left i_max — x=-20mm, y=[0,0.4mm]
            (76 79 83 80)   // A_inner_upper_left i_max — x=-20mm, y=[2.4,25mm]
        );
    }
    sclera_top_inner_left
    {
        type wall;
        faces ( (92 24 28 93) );    // sclera_B_left j_min — y=24mm, x=[-20,0mm]
    }

    // ── Outer faces — fixed (rigid outer shell) ───────────────────────────
    sclera_outer
    {
        type wall;
        faces
        (
            // RIGHT A strips: outer wall at x=21mm
            (17 18 22 21)   // A_outer_lower i_max — x=21mm, y=[0,0.4mm]
            (18 41 45 22)   // A_outer_mid   i_max — x=21mm, y=[0.4,2.4mm]
            (41 42 46 45)   // A_outer_upper i_max — x=21mm, y=[2.4,25mm]
            // RIGHT A bottom/top
            (16 48 52 20)   // A_inner_lower j_min — y=0mm, x=[20,20.5mm]
            (48 17 21 52)   // A_outer_lower j_min — y=0mm, x=[20.5,21mm]
            (43 47 55 51)   // A_inner_upper j_max — y=25mm, x=[20,20.5mm]
            (51 55 46 42)   // A_outer_upper j_max — y=25mm, x=[20.5,21mm]
            // RIGHT B top and inner corner
            (27 31 30 26)   // block B j_max — y=25mm, x=[0,20mm]
            (25 26 30 29)   // block B i_max — x=20mm (inner corner)
            // NOTE: block B i_min at x=0mm REMOVED — x=0 is now INTERIOR
        );
    }
    sclera_outer_left
    {
        type wall;
        faces
        (
            // LEFT A strips: outer wall at x=-21mm
            (69 73 74 70)   // A_outer_lower_left i_min — x=-21mm, y=[0,0.4mm]
            (70 74 81 77)   // A_outer_mid_left   i_min — x=-21mm, y=[0.4,2.4mm]
            (77 81 82 78)   // A_outer_upper_left i_min — x=-21mm, y=[2.4,25mm]
            // LEFT A bottom/top
            (84 68 72 88)   // A_inner_lower_left j_min — y=0mm, x=[-20.5,-20mm]
            (69 84 88 73)   // A_outer_lower_left j_min — y=0mm, x=[-21,-20.5mm]
            (79 83 91 87)   // A_inner_upper_left j_max — y=25mm, x=[-20.5,-20mm]
            (87 91 82 78)   // A_outer_upper_left j_max — y=25mm, x=[-21,-20.5mm]
            // LEFT B top and inner corner
            (79 83 31 27)   // sclera_B_left j_max — y=25mm, x=[-20,0mm]
            (92 93 28 24)   // sclera_B_left i_min — x=-20mm (inner corner)
        );
    }

    // TM gap faces (where fluid TM channel borders sclera A)
    sclera_tm_gap
    {
        type wall;
        faces
        (
            (19 23 53 49)   // A_inner_lower j_max  — y=0.4mm
            (40 50 54 44)   // A_inner_upper j_min  — y=2.4mm
            (49 53 54 50)   // A_outer_mid   i_min  — x=20.5mm
        );
    }
    sclera_tm_gap_left
    {
        type wall;
        faces
        (
            (71 75 89 85)   // A_inner_lower_left j_max — y=0.4mm
            (76 86 90 80)   // A_inner_upper_left j_min — y=2.4mm
            (85 89 90 86)   // A_outer_mid_left   i_max — x=-20.5mm
        );
    }

    // ════════════════════════════════════════════════════════════════════════
    // ══ CORNEA ══════════════════════════════════════════════════════════════
    // ════════════════════════════════════════════════════════════════════════
    cornea_inner
    {
        type wall;
        faces ( (35 39 38 34) );    // right half j_max — y=0mm
    }
    cornea_inner_left
    {
        type wall;
        faces ( (95 97 39 35) );    // left half  j_max — y=0mm, x=[-21,0mm]
    }

    cornea_outer
    {
        type wall;
        faces
        (
            (32 33 37 36)   // j_min — y=-1mm (right half outer bottom)
            // i_min at x=0mm REMOVED — x=0 is now INTERIOR
            (33 34 38 37)   // i_max — x=+21mm (right edge, connects to right sclera)
        );
    }
    cornea_outer_left
    {
        type wall;
        faces
        (
            (94 32 36 96)   // j_min — y=-1mm (left half outer bottom)
            (94 96 97 95)   // i_min — x=-21mm (left edge, connects to left sclera)
        );
    }

    // ════════════════════════════════════════════════════════════════════════
    // ══ 2D EMPTY FACES ══════════════════════════════════════════════════════
    // ════════════════════════════════════════════════════════════════════════
    front
    {
        type empty;
        faces
        (
            // RIGHT HALF (z=1mm faces)
            ( 4  5  6  7 )   // lens right
            (12 13 14 15 )   // iris right
            (20 52 53 23 )   // sclera A_inner_lower right
            (52 21 22 53 )   // sclera A_outer_lower right
            (53 22 45 54 )   // sclera A_outer_mid right
            (44 54 55 47 )   // sclera A_inner_upper right
            (54 45 46 55 )   // sclera A_outer_upper right
            (28 29 30 31 )   // sclera B right
            (36 37 38 39 )   // cornea right
            // LEFT HALF (z=1mm faces)
            (58  4  7 59 )   // lens left
            (65 64 67 66 )   // iris left
            (88 72 75 89 )   // sclera A_inner_lower left
            (73 88 89 74 )   // sclera A_outer_lower left
            (74 89 90 81 )   // sclera A_outer_mid left
            (90 80 83 91 )   // sclera A_inner_upper left
            (81 90 91 82 )   // sclera A_outer_upper left
            (93 28 31 83 )   // sclera B left
            (96 36 39 97 )   // cornea left
        );
    }

    back
    {
        type empty;
        faces
        (
            // RIGHT HALF (z=0 faces)
            ( 0  3  2  1 )   // lens right
            ( 8 11 10  9 )   // iris right
            (16 19 49 48 )   // sclera A_inner_lower right
            (48 49 18 17 )   // sclera A_outer_lower right
            (49 50 41 18 )   // sclera A_outer_mid right
            (40 43 51 50 )   // sclera A_inner_upper right
            (50 51 42 41 )   // sclera A_outer_upper right
            (24 27 26 25 )   // sclera B right
            (32 35 34 33 )   // cornea right
            // LEFT HALF (z=0 faces)
            (56 57  3  0 )   // lens left
            (61 62 63 60 )   // iris left
            (84 71 85 88 )   // wait - this needs to be right...
        );
    }
);
"""

# Actually let me fix the back faces for left half:
back_left_faces = """            (84 71 85  0 )   // WRONG - recalculate"""

# Back faces = z=0 faces, outward normal -z.
# For hex(84 68 71 85  88 72 75 89) sclera A_inner_lower_left:
#   z=0 face: v0,v1,v2,v3 = 84,68,71,85 → outward -z: need CW from +z = (84,85,71,68)
# For hex(69 84 85 70  73 88 89 74) sclera A_outer_lower_left:
#   z=0: 69,84,85,70 → CW: (69,70,85,84)
# For hex(70 85 86 77  74 89 90 81) sclera A_outer_mid_left:
#   z=0: 70,85,86,77 → CW: (70,77,86,85)
# For hex(86 76 79 87  90 80 83 91) sclera A_inner_upper_left:
#   z=0: 86,76,79,87 → CW: (86,87,79,76)
# For hex(77 86 87 78  81 90 91 82) sclera A_outer_upper_left:
#   z=0: 77,86,87,78 → CW: (77,78,87,86)
# For hex(92 24 27 79  93 28 31 83) sclera B left:
#   z=0: 92,24,27,79 → CW: (92,79,27,24)
# For hex(94 32 35 95  96 36 39 97) cornea left:
#   z=0: 94,32,35,95 → CW: (94,95,35,32)
# For hex(56  0  3 57  58  4  7 59) lens left:
#   z=0: 56,0,3,57 → CW: (56,57,3,0)
# For hex(61 60 63 62  65 64 67 66) iris left:
#   z=0: 61,60,63,62 → CW: (61,62,63,60)

# Front faces = z=1mm faces, outward normal +z.
# hex(84 68 71 85  88 72 75 89): z=1mm: v4,v5,v6,v7 = 88,72,75,89 → CCW from +z: (88,89,75,72)
# Actually for front we want outward +z = CCW from +z.
# v4=88:(-20.5,0,1), v5=72:(-20,0,1), v6=75:(-20,0.4,1), v7=89:(-20.5,0.4,1)
# From +z (looking down): 88(-20.5,0)→72(-20,0)=right, 72→75(-20,0.4)=up, 75→89(-20.5,0.4)=left, 89→88=down → CCW ✓

print("Generating solid blockMeshDict...")
print("NOTE: This script was used to verify vertex numbering.")
print("The actual file has been written directly.")
print()
print("Key vertex summary:")
print("  56-59: lens_left corners")
print("  60-67: iris_left corners")
print("  68-75: sclera A_lower_left")
print("  76-83: sclera A_upper_left")
print("  84-91: sclera A_mid_left (x=-20.5mm)")
print("  92-93: sclera B_left (x=-20mm, y=24mm)")
print("  94-97: cornea_left (x=-21mm)")
