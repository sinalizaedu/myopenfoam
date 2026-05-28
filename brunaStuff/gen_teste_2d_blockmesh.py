#!/usr/bin/env python3
"""gen_teste_2d_blockmesh.py

Gera o `blockMeshDict` do caso `cases/teste-2d-contato-oa-on/`.

Layout (plano XY, espessura 1 celula em z; scale = 0.001 -> vertices em mm):

    Quadrado 20 x 20 mm dividido em DUAS sub-malhas DESCONECTADAS no plano y=10:

        Sub-malha SUPERIOR  (y in [10, 20]) -- "Corpo A" (OA + fat acima)
        Sub-malha INFERIOR  (y in [ 0, 10]) -- "Corpo B" (ON + ONS + fat abaixo)

    Geometria interna do Corpo B (definida via `topoSet` depois, NAO aqui):
        ON   : disco       r <= 1.5 mm em torno de (10, 7.5)
        ONS  : annulus     1.5 mm < r <= 2.5 mm em torno de (10, 7.5)
        fat  : complemento dentro de y in [0, 10]

    Topo da ONS toca y = 10 em (10, 10) -- tangencia inicial pontual.

Os dois blocos usam VERTICES DISJUNTOS no plano y=10 (8 vertices cada bloco,
sem compartilhamento), de modo que blockMesh produz DUAS faces de contorno
nessa altura (uma do bloco superior, outra do bloco inferior). Essas duas
faces sao os patches `oa_mestrado` (inferior do bloco superior) e
`on_mestrado` (superior do bloco inferior), que serao acoplados por
`solidContact` no `0/D` (frictionless sliding).

Patches gerados:
    outer_top         : y = 20  (carga de pressao prescrita)
    outer_bottom      : y =  0  (fixedDisplacement = 0)
    outer_left_upper  : x =  0, y in [10, 20]    (symmetryPlane)
    outer_left_lower  : x =  0, y in [ 0, 10]    (symmetryPlane)
    outer_right_upper : x = 20, y in [10, 20]    (symmetryPlane)
    outer_right_lower : x = 20, y in [ 0, 10]    (symmetryPlane)
    oa_mestrado       : y = 10  (face inferior do bloco SUPERIOR)
    on_mestrado       : y = 10  (face superior do bloco INFERIOR)
    frontAndBack      : todas as faces z=const (empty -- 2D)

Resolucao: nx = 80, ny_per_sub = 40 -> celulas de ~0.25 mm; total ~6400 cels.

Saida: cases/teste-2d-contato-oa-on/solid/system/blockMeshDict
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "cases" / "teste-2d-contato-oa-on" / "solid" / "system" / "blockMeshDict"

# Dominio
LX = 20.0       # mm
LY = 20.0       # mm
Y_SPLIT = 10.0  # mm -- plano de contato (NAO mergeado)
LZ = 1.0        # mm (espessura 2D, 1 celula)

# Resolucao
NX = 80
NY_SUB = 40     # por sub-malha (lower e upper, cada uma)
NZ = 1


HEADER = """/*--------------------------------*- C++ -*----------------------------------*\\
| Gerado por brunaStuff/gen_teste_2d_blockmesh.py                              |
| Caso: teste-2d-contato-oa-on (validacao de contato OA x ONS sem atrito)      |
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


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)

    # Vertices: 16 no total (8 por bloco, sem compartilhamento no plano y=Y_SPLIT)
    # Bloco INFERIOR  (y in [0, Y_SPLIT]):     ids 0..7
    # Bloco SUPERIOR  (y in [Y_SPLIT, LY]):    ids 8..15
    vertices = [
        # --- Bloco INFERIOR (ids 0..7) ---
        (0.0,    0.0,    0.0),    # 0
        (LX,     0.0,    0.0),    # 1
        (LX,     Y_SPLIT, 0.0),   # 2 (lower top, y=Y_SPLIT)
        (0.0,    Y_SPLIT, 0.0),   # 3 (lower top, y=Y_SPLIT)
        (0.0,    0.0,    LZ),     # 4
        (LX,     0.0,    LZ),     # 5
        (LX,     Y_SPLIT, LZ),    # 6
        (0.0,    Y_SPLIT, LZ),    # 7

        # --- Bloco SUPERIOR (ids 8..15) -- duplica o plano y=Y_SPLIT ---
        (0.0,    Y_SPLIT, 0.0),   # 8  (upper bottom, mesma posicao do 3)
        (LX,     Y_SPLIT, 0.0),   # 9  (mesma posicao do 2)
        (LX,     LY,      0.0),   # 10
        (0.0,    LY,      0.0),   # 11
        (0.0,    Y_SPLIT, LZ),    # 12 (mesma posicao do 7)
        (LX,     Y_SPLIT, LZ),    # 13 (mesma posicao do 6)
        (LX,     LY,      LZ),    # 14
        (0.0,    LY,      LZ),    # 15
    ]

    lines = [HEADER, "vertices\n(\n"]
    for i, (x, y, z) in enumerate(vertices):
        lines.append(f"{fmt_v(x, y, z)}   // {i}\n")
    lines.append(");\n\n")

    # Blocos
    lines.append("blocks\n(\n")
    # Inferior: hex (0 1 2 3 4 5 6 7)
    lines.append(
        f"    hex ( 0 1 2 3   4 5 6 7 )  lower  "
        f"( {NX} {NY_SUB} {NZ} )  simpleGrading ( 1 1 1 )\n"
    )
    # Superior: hex (8 9 10 11 12 13 14 15)
    lines.append(
        f"    hex ( 8 9 10 11   12 13 14 15 )  upper  "
        f"( {NX} {NY_SUB} {NZ} )  simpleGrading ( 1 1 1 )\n"
    )
    lines.append(");\n\n")

    # Sem arestas curvas (mesh puramente cartesiano; circulos vem por topoSet)
    lines.append("edges\n(\n);\n\n")

    # Boundaries
    lines.append(
        "boundary\n"
        "(\n"
        "    outer_bottom\n"
        "    {\n"
        "        type wall;\n"
        "        faces\n"
        "        (\n"
        "            ( 0 1 5 4 )   // y = 0  (lower bottom)\n"
        "        );\n"
        "    }\n"
        "\n"
        "    outer_top\n"
        "    {\n"
        "        type wall;\n"
        "        faces\n"
        "        (\n"
        "            ( 11 10 14 15 )   // y = LY (upper top)\n"
        "        );\n"
        "    }\n"
        "\n"
        # Nota: type 'symmetry' (NAO 'symmetryPlane') eh exigido pelo BC
        # solidSymmetry em OpenFOAM v2512 (vide README do projeto / gotchas).
        "    outer_left_lower\n"
        "    {\n"
        "        type symmetry;\n"
        "        faces\n"
        "        (\n"
        "            ( 0 4 7 3 )   // x = 0 (lower)\n"
        "        );\n"
        "    }\n"
        "\n"
        "    outer_left_upper\n"
        "    {\n"
        "        type symmetry;\n"
        "        faces\n"
        "        (\n"
        "            ( 8 12 15 11 )   // x = 0 (upper)\n"
        "        );\n"
        "    }\n"
        "\n"
        "    outer_right_lower\n"
        "    {\n"
        "        type symmetry;\n"
        "        faces\n"
        "        (\n"
        "            ( 1 2 6 5 )   // x = LX (lower)\n"
        "        );\n"
        "    }\n"
        "\n"
        "    outer_right_upper\n"
        "    {\n"
        "        type symmetry;\n"
        "        faces\n"
        "        (\n"
        "            ( 9 13 14 10 )   // x = LX (upper)\n"
        "        );\n"
        "    }\n"
        "\n"
        "    on_mestrado\n"
        "    {\n"
        "        type wall;\n"
        "        faces\n"
        "        (\n"
        "            ( 3 7 6 2 )   // y = Y_SPLIT (topo do bloco INFERIOR)\n"
        "        );\n"
        "    }\n"
        "\n"
        "    oa_mestrado\n"
        "    {\n"
        "        type wall;\n"
        "        faces\n"
        "        (\n"
        "            ( 8 9 13 12 )   // y = Y_SPLIT (base do bloco SUPERIOR)\n"
        "        );\n"
        "    }\n"
        "\n"
        "    frontAndBack\n"
        "    {\n"
        "        type empty;\n"
        "        faces\n"
        "        (\n"
        "            ( 0 3 2 1 )       // z = 0  (lower)\n"
        "            ( 8 11 10 9 )     // z = 0  (upper)\n"
        "            ( 4 5 6 7 )       // z = LZ (lower)\n"
        "            ( 12 13 14 15 )   // z = LZ (upper)\n"
        "        );\n"
        "    }\n"
        ");\n\n"
    )

    # Sem mergePatchPairs -- queremos que oa_mestrado e on_mestrado FIQUEM
    # como faces de contorno separadas (par de contato).
    lines.append("mergePatchPairs\n(\n);\n")

    OUT.write_text("".join(lines), encoding="utf-8")
    print(f"Escrito: {OUT}")
    print(f"  Dominio: {LX} x {LY} mm, sub-malhas em y in [0,{Y_SPLIT}] e [{Y_SPLIT},{LY}]")
    print(f"  Resolucao: {NX} x {NY_SUB} celulas por sub-malha "
          f"-> {NX*NY_SUB*2} celulas total (~{LX/NX:.2f} mm por celula)")
    print(f"  Espessura z: {LZ} mm (1 celula, frontAndBack empty)")
    print(f"  Patches oa_mestrado/on_mestrado: nao-mergeados em y={Y_SPLIT} mm")


if __name__ == "__main__":
    main()
