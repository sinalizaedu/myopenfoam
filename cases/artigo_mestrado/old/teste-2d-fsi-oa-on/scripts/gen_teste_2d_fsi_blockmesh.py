#!/usr/bin/env python3
"""gen_teste_2d_fsi_blockmesh.py

Gera os DOIS `blockMeshDict` do caso `cases/teste-2d-fsi-oa-on/`:

    cases/teste-2d-fsi-oa-on/solid/system/blockMeshDict   (sólido, 4 blocos)
    cases/teste-2d-fsi-oa-on/fluid/system/blockMeshDict   (fluido, 1 bloco)

Layout (plano XY, espessura 1 cell em z; scale = 0.001 -> vertices em mm):

    Quadrado 20 x 20 mm com a OA modelada como ARTÉRIA OCA:

        y=20.00  ┌────────────────────────────────────────────┐ outer_top
                 │  Block D  (fat_above)                       │
        y=11.50  ├────────────────────────────────────────────┤
                 │  Block C  (wall_sup)  -- oa_wall sup        │
        y=11.30  ├────────────────────────────────────────────┤ lumen_top  <-- FSI
                 │  (LUMEN -- so no fluido)                    │
        y=10.20  ├────────────────────────────────────────────┤ lumen_bot  <-- FSI
                 │  Block B  (wall_inf)  -- oa_wall inf        │
        y=10.00  ├────────────────────────────────────────────┤ on/oa_mestrado <-- CONTATO
                 │  Block A  (fat_below + ON + ONS via topoSet)│
        y= 0.00  └────────────────────────────────────────────┘ outer_bottom
                 x=0                                           x=20

    Blocos A e B: DESCONECTADOS em y=10 (vertices disjuntos) ->
                  patches `on_mestrado` (topo de A) e `oa_mestrado` (base de B)
                  acoplados via solidContact frictionless.

    Blocos B e C: DESCONECTADOS na regiao do lumen
                  (B termina em y=10.2, C comeca em y=11.3, lumen entre eles).
                  Patches `lumen_bot` (topo de B) e `lumen_top` (base de C) sao
                  as interfaces FSI com o fluido via preCICE.

    Blocos C e D: CONECTADOS em y=11.5 (vertices compartilhados, mesma celula).

Resolucao (PERF v2: malha engrossada ~3x; mantem NY paredes em 2 cells;
mantem NX consistente entre fluido e solido para mapping preCICE 1:1):
    NX = 40 (mesma em todos os blocos para casar com fluido na interface FSI)
    NY_A = 20 (Block A, 10mm -> dy=0.5)
    NY_B = 2  (Block B,  0.2mm -> dy=0.10)   [parede fina: manter resolucao]
    NY_C = 2  (Block C,  0.2mm -> dy=0.10)   [parede fina: manter resolucao]
    NY_D = 17 (Block D,  8.5mm -> dy=0.5)
    NY_F = 6  (Fluid lumen, 1.1mm -> dy~0.18) [perfil parabolico OK c/ 6 cells]
    NZ = 1

    Total solido: 40 * (20+2+2+17) = 1640 celulas (~3.8x menos que 6240)
    Total fluido: 40 * 6           = 240  celulas (~3.7x menos que 880)

Trade-offs em relacao a versao original (80x40):
    - disco de ON (raio 1.5 mm) representado por ~3 celulas de altura
      (era ~6). Suficiente pra TESTE de acoplamento FSI+contato.
    - Para producao (figuras finais), restaurar NX=80, NY_A=40, NY_D=34.
"""
from __future__ import annotations

from pathlib import Path

# Detecta automaticamente o local: copia em cases/<x>/scripts/ ou brunaStuff/.
SCRIPT_DIR = Path(__file__).resolve().parent
if SCRIPT_DIR.name == "scripts":
    CASE = SCRIPT_DIR.parent
else:
    REPO = SCRIPT_DIR.parent
    CASE = REPO / "cases" / "teste-2d-fsi-oa-on"

SOLID_OUT = CASE / "solid" / "system" / "blockMeshDict"
FLUID_OUT = CASE / "fluid" / "system" / "blockMeshDict"

# Dominio (mm)
LX = 20.0
LZ = 1.0  # espessura 2D
Y_CONTACT = 10.0   # base da parede inferior da OA (= topo do contato)
Y_WALL_BOT = 10.2  # topo da parede inferior = base do lumen
Y_WALL_TOP = 11.3  # base da parede superior = topo do lumen
Y_OA_TOP = 11.5    # topo da parede superior da OA
Y_TOP = 20.0       # topo do dominio

# Resolucao (PERF v2 -- engrossada ~3x para teste rapido FSI+contato)
NX = 40
NY_A = 20   # Block A: y in [0, 10]
NY_B = 2    # Block B: y in [10, 10.2]    [parede fina: nao mexer]
NY_C = 2    # Block C: y in [11.3, 11.5]  [parede fina: nao mexer]
NY_D = 17   # Block D: y in [11.5, 20]
NY_FLUID = 6  # Fluid block: y in [10.2, 11.3]
NZ = 1


HEADER_SOLID = """/*--------------------------------*- C++ -*----------------------------------*\\
| Gerado por brunaStuff/gen_teste_2d_fsi_blockmesh.py                          |
| Caso: teste-2d-fsi-oa-on (FSI + contato OA x ONS, lado SOLIDO)               |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}

scale   0.001;   // vertices em mm

"""

HEADER_FLUID = """/*--------------------------------*- C++ -*----------------------------------*\\
| Gerado por brunaStuff/gen_teste_2d_fsi_blockmesh.py                          |
| Caso: teste-2d-fsi-oa-on (FSI + contato OA x ONS, lado FLUIDO -- lumen)      |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}

scale   0.001;   // vertices em mm

"""


def fmt_v(x: float, y: float, z: float) -> str:
    return f"    ({x:>8.3f}  {y:>8.3f}  {z:>6.3f})"


def write_solid() -> None:
    SOLID_OUT.parent.mkdir(parents=True, exist_ok=True)

    # 28 vertices: Block A (0-7), Block B (8-15), Block C (16-23), Block D usa
    # 19,18,23,22 de C + 4 novos (24-27). Blocks B e C sao disjoint (lumen entre
    # eles). Blocks A e B sao disjoint (contato). Blocks C e D sao conectados.
    vertices = [
        # --- Block A (lower, y=0..Y_CONTACT) ids 0..7 ---
        (0.0,  0.0,        0.0),   # 0
        (LX,   0.0,        0.0),   # 1
        (LX,   Y_CONTACT,  0.0),   # 2  topo A (sera disjoint do B)
        (0.0,  Y_CONTACT,  0.0),   # 3  topo A
        (0.0,  0.0,        LZ),    # 4
        (LX,   0.0,        LZ),    # 5
        (LX,   Y_CONTACT,  LZ),    # 6
        (0.0,  Y_CONTACT,  LZ),    # 7

        # --- Block B (wall_inf, y=Y_CONTACT..Y_WALL_BOT) ids 8..15 ---
        (0.0,  Y_CONTACT,  0.0),   # 8  base B (DUP de 3)
        (LX,   Y_CONTACT,  0.0),   # 9  base B (DUP de 2)
        (LX,   Y_WALL_BOT, 0.0),   # 10 topo B (= lumen_bot)
        (0.0,  Y_WALL_BOT, 0.0),   # 11
        (0.0,  Y_CONTACT,  LZ),    # 12 (DUP de 7)
        (LX,   Y_CONTACT,  LZ),    # 13 (DUP de 6)
        (LX,   Y_WALL_BOT, LZ),    # 14
        (0.0,  Y_WALL_BOT, LZ),    # 15

        # --- Block C (wall_sup, y=Y_WALL_TOP..Y_OA_TOP) ids 16..23 ---
        (0.0,  Y_WALL_TOP, 0.0),   # 16 base C (= lumen_top)
        (LX,   Y_WALL_TOP, 0.0),   # 17
        (LX,   Y_OA_TOP,   0.0),   # 18 topo C (compartilhado c/ D)
        (0.0,  Y_OA_TOP,   0.0),   # 19 topo C (compartilhado c/ D)
        (0.0,  Y_WALL_TOP, LZ),    # 20
        (LX,   Y_WALL_TOP, LZ),    # 21
        (LX,   Y_OA_TOP,   LZ),    # 22 (compartilhado c/ D)
        (0.0,  Y_OA_TOP,   LZ),    # 23 (compartilhado c/ D)

        # --- Block D (fat_above, y=Y_OA_TOP..Y_TOP) ids 24..27 ---
        # (Block D reusa 19,18,23,22 como base; aqui sao apenas os topos)
        (LX,   Y_TOP,      0.0),   # 24
        (0.0,  Y_TOP,      0.0),   # 25
        (LX,   Y_TOP,      LZ),    # 26
        (0.0,  Y_TOP,      LZ),    # 27
    ]

    lines = [HEADER_SOLID, "vertices\n(\n"]
    for i, (x, y, z) in enumerate(vertices):
        lines.append(f"{fmt_v(x, y, z)}   // {i}\n")
    lines.append(");\n\n")

    # Blocks
    lines.append("blocks\n(\n")
    lines.append(
        f"    hex ( 0 1 2 3   4 5 6 7 )  lower  "
        f"( {NX} {NY_A} {NZ} )  simpleGrading ( 1 1 1 )\n"
    )
    lines.append(
        f"    hex ( 8 9 10 11   12 13 14 15 )  wall_inf  "
        f"( {NX} {NY_B} {NZ} )  simpleGrading ( 1 1 1 )\n"
    )
    lines.append(
        f"    hex ( 16 17 18 19   20 21 22 23 )  wall_sup  "
        f"( {NX} {NY_C} {NZ} )  simpleGrading ( 1 1 1 )\n"
    )
    lines.append(
        f"    hex ( 19 18 24 25   23 22 26 27 )  fat_above  "
        f"( {NX} {NY_D} {NZ} )  simpleGrading ( 1 1 1 )\n"
    )
    lines.append(");\n\n")

    lines.append("edges\n(\n);\n\n")

    # Boundary patches
    lines.append(
        "boundary\n"
        "(\n"
        "    outer_bottom\n"
        "    {\n"
        "        type wall;\n"
        "        faces\n"
        "        (\n"
        "            ( 0 1 5 4 )       // y = 0  (base Block A)\n"
        "        );\n"
        "    }\n"
        "\n"
        "    outer_top\n"
        "    {\n"
        "        type wall;\n"
        "        faces\n"
        "        (\n"
        "            ( 25 24 26 27 )   // y = Y_TOP  (topo Block D)\n"
        "        );\n"
        "    }\n"
        "\n"
        "    on_mestrado\n"
        "    {\n"
        "        type wall;\n"
        "        faces\n"
        "        (\n"
        "            ( 3 7 6 2 )       // y = Y_CONTACT  (topo Block A) -- contact slave\n"
        "        );\n"
        "    }\n"
        "\n"
        "    oa_mestrado\n"
        "    {\n"
        "        type wall;\n"
        "        faces\n"
        "        (\n"
        "            ( 8 9 13 12 )     // y = Y_CONTACT  (base Block B) -- contact master\n"
        "        );\n"
        "    }\n"
        "\n"
        "    lumen_bot\n"
        "    {\n"
        "        type wall;\n"
        "        faces\n"
        "        (\n"
        "            ( 11 15 14 10 )   // y = Y_WALL_BOT (topo Block B) -- FSI interface inferior\n"
        "        );\n"
        "    }\n"
        "\n"
        "    lumen_top\n"
        "    {\n"
        "        type wall;\n"
        "        faces\n"
        "        (\n"
        "            ( 16 17 21 20 )   // y = Y_WALL_TOP (base Block C) -- FSI interface superior\n"
        "        );\n"
        "    }\n"
        "\n"
        # Side patches -- TODOS symmetry (slice infinita lateralmente)
        "    outer_left_lower\n"
        "    {\n"
        "        type symmetry;\n"
        "        faces\n"
        "        (\n"
        "            ( 0 4 7 3 )       // x = 0 (Block A)\n"
        "        );\n"
        "    }\n"
        "\n"
        "    outer_left_wall_inf\n"
        "    {\n"
        "        type symmetry;\n"
        "        faces\n"
        "        (\n"
        "            ( 8 12 15 11 )    // x = 0 (Block B)\n"
        "        );\n"
        "    }\n"
        "\n"
        "    outer_left_wall_sup\n"
        "    {\n"
        "        type symmetry;\n"
        "        faces\n"
        "        (\n"
        "            ( 16 20 23 19 )   // x = 0 (Block C)\n"
        "        );\n"
        "    }\n"
        "\n"
        "    outer_left_fat_above\n"
        "    {\n"
        "        type symmetry;\n"
        "        faces\n"
        "        (\n"
        "            ( 19 23 27 25 )   // x = 0 (Block D)\n"
        "        );\n"
        "    }\n"
        "\n"
        "    outer_right_lower\n"
        "    {\n"
        "        type symmetry;\n"
        "        faces\n"
        "        (\n"
        "            ( 1 2 6 5 )       // x = LX (Block A)\n"
        "        );\n"
        "    }\n"
        "\n"
        "    outer_right_wall_inf\n"
        "    {\n"
        "        type symmetry;\n"
        "        faces\n"
        "        (\n"
        "            ( 9 10 14 13 )    // x = LX (Block B)\n"
        "        );\n"
        "    }\n"
        "\n"
        "    outer_right_wall_sup\n"
        "    {\n"
        "        type symmetry;\n"
        "        faces\n"
        "        (\n"
        "            ( 17 18 22 21 )   // x = LX (Block C)\n"
        "        );\n"
        "    }\n"
        "\n"
        "    outer_right_fat_above\n"
        "    {\n"
        "        type symmetry;\n"
        "        faces\n"
        "        (\n"
        "            ( 18 24 26 22 )   // x = LX (Block D)\n"
        "        );\n"
        "    }\n"
        "\n"
        "    frontAndBack\n"
        "    {\n"
        "        type empty;\n"
        "        faces\n"
        "        (\n"
        "            ( 0 3 2 1 )       // z = 0  (Block A)\n"
        "            ( 8 11 10 9 )     // z = 0  (Block B)\n"
        "            ( 16 19 18 17 )   // z = 0  (Block C)\n"
        "            ( 19 25 24 18 )   // z = 0  (Block D)\n"
        "            ( 4 5 6 7 )       // z = LZ (Block A)\n"
        "            ( 12 13 14 15 )   // z = LZ (Block B)\n"
        "            ( 20 21 22 23 )   // z = LZ (Block C)\n"
        "            ( 23 22 26 27 )   // z = LZ (Block D)\n"
        "        );\n"
        "    }\n"
        ");\n\n"
    )

    lines.append("mergePatchPairs\n(\n);\n")

    SOLID_OUT.write_text("".join(lines), encoding="utf-8")
    print(f"Escrito: {SOLID_OUT}")
    n_cells = NX * (NY_A + NY_B + NY_C + NY_D) * NZ
    print(f"  Solido: 4 blocos disjoint em y=10 (contato) e em [10.2,11.3] (lumen)")
    print(f"  Total: {n_cells} celulas (dy parede = {(Y_WALL_BOT-Y_CONTACT)/NY_B:.3f} mm)")


def write_fluid() -> None:
    FLUID_OUT.parent.mkdir(parents=True, exist_ok=True)

    # 8 vertices, 1 bloco retangular = lumen
    vertices = [
        (0.0,  Y_WALL_BOT, 0.0),   # 0
        (LX,   Y_WALL_BOT, 0.0),   # 1
        (LX,   Y_WALL_TOP, 0.0),   # 2
        (0.0,  Y_WALL_TOP, 0.0),   # 3
        (0.0,  Y_WALL_BOT, LZ),    # 4
        (LX,   Y_WALL_BOT, LZ),    # 5
        (LX,   Y_WALL_TOP, LZ),    # 6
        (0.0,  Y_WALL_TOP, LZ),    # 7
    ]

    lines = [HEADER_FLUID, "vertices\n(\n"]
    for i, (x, y, z) in enumerate(vertices):
        lines.append(f"{fmt_v(x, y, z)}   // {i}\n")
    lines.append(");\n\n")

    lines.append("blocks\n(\n")
    lines.append(
        f"    hex ( 0 1 2 3   4 5 6 7 )  lumen  "
        f"( {NX} {NY_FLUID} {NZ} )  simpleGrading ( 1 1 1 )\n"
    )
    lines.append(");\n\n")

    lines.append("edges\n(\n);\n\n")

    lines.append(
        "boundary\n"
        "(\n"
        "    inlet\n"
        "    {\n"
        "        type patch;\n"
        "        faces\n"
        "        (\n"
        "            ( 0 4 7 3 )       // x = 0\n"
        "        );\n"
        "    }\n"
        "\n"
        "    outlet\n"
        "    {\n"
        "        type patch;\n"
        "        faces\n"
        "        (\n"
        "            ( 1 2 6 5 )       // x = LX\n"
        "        );\n"
        "    }\n"
        "\n"
        "    wall_bot\n"
        "    {\n"
        "        type wall;\n"
        "        faces\n"
        "        (\n"
        "            ( 0 1 5 4 )       // y = Y_WALL_BOT  (FSI inferior)\n"
        "        );\n"
        "    }\n"
        "\n"
        "    wall_top\n"
        "    {\n"
        "        type wall;\n"
        "        faces\n"
        "        (\n"
        "            ( 3 7 6 2 )       // y = Y_WALL_TOP  (FSI superior)\n"
        "        );\n"
        "    }\n"
        "\n"
        "    frontAndBack\n"
        "    {\n"
        "        type empty;\n"
        "        faces\n"
        "        (\n"
        "            ( 0 3 2 1 )       // z = 0\n"
        "            ( 4 5 6 7 )       // z = LZ\n"
        "        );\n"
        "    }\n"
        ");\n\n"
    )

    lines.append("mergePatchPairs\n(\n);\n")

    FLUID_OUT.write_text("".join(lines), encoding="utf-8")
    print(f"Escrito: {FLUID_OUT}")
    n_cells = NX * NY_FLUID * NZ
    print(f"  Fluido: 1 bloco lumen ({NX}x{NY_FLUID}={n_cells} celulas)")


def main() -> None:
    write_solid()
    write_fluid()


if __name__ == "__main__":
    main()
