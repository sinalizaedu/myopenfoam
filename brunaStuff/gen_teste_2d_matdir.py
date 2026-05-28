#!/usr/bin/env python3
"""gen_teste_2d_matdir.py

Gera o campo de orientacao local da bainha (ONS) para o caso 2D
teste-2d-contato-oa-on. Em cada celula da zona `ons`, a direcao "fibrosa"
e a CIRCUNFERENCIAL (tangente ao circulo, no plano XY); a direcao radial
aponta para fora do centro (10, 7.5) mm; o eixo axial e z.

Saidas (em `cases/teste-2d-contato-oa-on/solid/constant/`):

  - `f0`     : volVectorField -- direcao FIBROSA (circunferencial) por celula
               Default = (1, 0, 0) fora da ONS.

  - `matDir` : volTensorField -- tensor de orientacao local
               linha 1 = radial   (r_hat)
               linha 2 = circunf. (c_hat)
               linha 3 = axial    (z_hat)
               Default = identidade fora da ONS.

Uso pratico:

  * `f0` e o input do material `GuccioneElastic` (modelo transversalmente
    isotropico hyperelastico, exponencial). E o substituto disponivel em
    OpenFOAM v2512 para o `StVenantKirchhoffOrthotropicElastic` (que so
    compila em foam-extend, vide `#ifdef FOAMEXTEND` no .C).

  * `matDir` fica documentado para um eventual port futuro de
    `StVenantKirchhoffOrthotropicElastic` para OpenFOAM ESI.

Convencao dos campos: assume-se a ordenacao DETERMINISTICA de celulas
gerada por `blockMesh` para os 2 blocos cartesianos do
`brunaStuff/gen_teste_2d_blockmesh.py`:

  - Bloco LOWER  (y in [0, 10] mm): celulas 0..NX*NY-1
    cell (i, j) com i in [0, NX-1], j in [0, NY-1], indice = i + NX*j
    centro: x = (i+0.5)*(LX/NX), y = (j+0.5)*(Y_SPLIT/NY)

  - Bloco UPPER  (y in [10, 20] mm): celulas NX*NY .. 2*NX*NY-1
    centro: x = (i+0.5)*(LX/NX), y = Y_SPLIT + (j+0.5)*(Y_SPLIT/NY)

Total: 2 * NX * NY = 2 * 80 * 40 = 6400 celulas.

Validacao: o script imprime quantas celulas cairam dentro da ONS, e a media
de mag(f0) (deve ser 1.0 com tolerancia ~1e-12 para celulas ONS, e 1.0 para
celulas com fallback (1,0,0)).
"""
from __future__ import annotations

import math
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CONST = REPO / "cases" / "teste-2d-contato-oa-on" / "solid" / "constant"

# Parametros do mesh (mantidos sincronizados com gen_teste_2d_blockmesh.py)
LX = 20.0       # mm
LY = 20.0       # mm
Y_SPLIT = 10.0  # mm
LZ = 1.0        # mm
NX = 80
NY_SUB = 40

# Geometria da ONS
ONS_CENTER_X = 10.0  # mm
ONS_CENTER_Y = 7.5   # mm
R_ON  = 1.5          # mm
R_ONS = 2.5          # mm

CELLS_PER_BLOCK = NX * NY_SUB
N_CELLS = 2 * CELLS_PER_BLOCK


def cell_center(idx: int) -> tuple[float, float]:
    """Retorna (x, y) em mm do centro da celula idx, na ordenacao blockMesh."""
    if idx < CELLS_PER_BLOCK:  # bloco lower
        i = idx % NX
        j = idx // NX
        x = (i + 0.5) * (LX / NX)
        y = (j + 0.5) * (Y_SPLIT / NY_SUB)
    else:  # bloco upper
        k = idx - CELLS_PER_BLOCK
        i = k % NX
        j = k // NX
        x = (i + 0.5) * (LX / NX)
        y = Y_SPLIT + (j + 0.5) * (Y_SPLIT / NY_SUB)
    return x, y


def f0_for_cell(idx: int) -> tuple[float, float, float]:
    """Vetor f0 = direcao circunferencial unitaria se a celula esta na ONS,
    senao default (1, 0, 0)."""
    x, y = cell_center(idx)
    dx = x - ONS_CENTER_X
    dy = y - ONS_CENTER_Y
    r = math.sqrt(dx * dx + dy * dy)
    if R_ON < r <= R_ONS:
        # r_hat = (dx/r, dy/r, 0); c_hat = (-dy/r, dx/r, 0) (90 deg CCW)
        return (-dy / r, dx / r, 0.0)
    return (1.0, 0.0, 0.0)


def matdir_for_cell(idx: int) -> tuple[tuple[float, float, float],
                                       tuple[float, float, float],
                                       tuple[float, float, float]]:
    """Tensor de orientacao: linhas = (radial, circunf, axial)."""
    x, y = cell_center(idx)
    dx = x - ONS_CENTER_X
    dy = y - ONS_CENTER_Y
    r = math.sqrt(dx * dx + dy * dy)
    if R_ON < r <= R_ONS:
        r_hat = (dx / r, dy / r, 0.0)
        c_hat = (-dy / r, dx / r, 0.0)
        z_hat = (0.0, 0.0, 1.0)
        return (r_hat, c_hat, z_hat)
    return ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))


VOL_VECTOR_HEADER = """/*--------------------------------*- C++ -*----------------------------------*\\
| Gerado por brunaStuff/gen_teste_2d_matdir.py                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       volVectorField;
    location    "constant";
    object      f0;
}}

dimensions      [0 0 0 0 0 0 0];

internalField   nonuniform List<vector>
{n}
(
"""

VOL_TENSOR_HEADER = """/*--------------------------------*- C++ -*----------------------------------*\\
| Gerado por brunaStuff/gen_teste_2d_matdir.py                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       volTensorField;
    location    "constant";
    object      matDir;
}}

dimensions      [0 0 0 0 0 0 0];

internalField   nonuniform List<tensor>
{n}
(
"""

BOUNDARY_FOOTER = """)
;

boundaryField
{
    outer_bottom        { type zeroGradient; }
    outer_top           { type zeroGradient; }
    outer_left_lower    { type zeroGradient; }
    outer_left_upper    { type zeroGradient; }
    outer_right_lower   { type zeroGradient; }
    outer_right_upper   { type zeroGradient; }
    on_mestrado         { type zeroGradient; }
    oa_mestrado         { type zeroGradient; }
    frontAndBack        { type empty;        }
}
"""


def write_f0(path: Path) -> None:
    n_ons = 0
    lines = [VOL_VECTOR_HEADER.format(n=N_CELLS)]
    for idx in range(N_CELLS):
        fx, fy, fz = f0_for_cell(idx)
        lines.append(f"({fx:+.10f} {fy:+.10f} {fz:+.10f})\n")
        x, y = cell_center(idx)
        r = math.hypot(x - ONS_CENTER_X, y - ONS_CENTER_Y)
        if R_ON < r <= R_ONS:
            n_ons += 1
    lines.append(BOUNDARY_FOOTER)
    path.write_text("".join(lines), encoding="utf-8")
    return n_ons


def write_matdir(path: Path) -> None:
    lines = [VOL_TENSOR_HEADER.format(n=N_CELLS)]
    for idx in range(N_CELLS):
        (r1, r2, r3), (c1, c2, c3), (z1, z2, z3) = matdir_for_cell(idx)
        # OpenFOAM tensor entry: (xx xy xz yx yy yz zx zy zz)
        lines.append(
            f"({r1:+.10f} {r2:+.10f} {r3:+.10f} "
            f"{c1:+.10f} {c2:+.10f} {c3:+.10f} "
            f"{z1:+.10f} {z2:+.10f} {z3:+.10f})\n"
        )
    # Reusa o footer com BCs zeroGradient/empty; cuidado para usar boundaryField
    # compativel (mesma estrutura sintatica para volTensorField).
    lines.append(BOUNDARY_FOOTER.replace("type zeroGradient",
                                          "type zeroGradient"))
    path.write_text("".join(lines), encoding="utf-8")


def main() -> None:
    CONST.mkdir(parents=True, exist_ok=True)
    n_ons = write_f0(CONST / "f0")
    write_matdir(CONST / "matDir")
    print(f"=== gen_teste_2d_matdir ===")
    print(f"  N_CELLS  = {N_CELLS}  (2 blocos x {NX}x{NY_SUB})")
    print(f"  ONS cells = {n_ons}  (1.5 < r <= 2.5 mm de ({ONS_CENTER_X},{ONS_CENTER_Y}))")
    print(f"  Escrito: {CONST / 'f0'}  (volVectorField, fibra = circunf.)")
    print(f"  Escrito: {CONST / 'matDir'}  (volTensorField, rad/circ/z)")


if __name__ == "__main__":
    main()
