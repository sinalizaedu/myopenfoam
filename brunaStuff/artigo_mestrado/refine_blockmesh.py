#!/usr/bin/env python3
"""
refine_blockmesh.py
===================
Gera um blockMeshDict refinado multiplicando TODAS as contagens de celulas dos
blocos por um fator inteiro N (uniforme em r, theta, z). Usado no estudo de
independencia de malha do on-caso-4.

Por que multiplicar uniformemente: blocos que compartilham uma face precisam ter
contagens compativeis na direcao compartilhada. A malha base ja' e' consistente;
multiplicar TODAS as triplas pelo mesmo N preserva essa compatibilidade.

Identificacao robusta da tripla de celulas: em cada bloco a tripla "( a b c )"
aparece IMEDIATAMENTE antes de "simpleGrading". A lista de vertices "hex ( ... )"
tem 8 numeros e nao e' seguida por simpleGrading -> sem ambiguidade.

Refino UNIFORME (1 fator) ou POR DIRECAO (3 fatores fr ft fz):
  python3 brunaStuff/refine_blockmesh.py <in_dict> <out_dict> <fator>
  python3 brunaStuff/refine_blockmesh.py <in_dict> <out_dict> <fr> <ft> <fz>

Convencao da tripla "( n1 n2 n3 )": n1=radial, n2=tangencial, n3=axial(z) nos
blocos de anel. No NUCLEO (bloco quadrado, n1==n2) NAO ha radial/tangencial: as
duas direcoes no plano conectam-se ao tangencial dos aneis, entao ambas seguem ft.
Isso preserva a compatibilidade de divisoes entre blocos vizinhos do O-grid.
"""
import re
import sys


def refine(in_path: str, out_path: str, fr: int, ft: int, fz: int):
    txt = open(in_path).read()

    pat = re.compile(r"\(\s*(\d+)\s+(\d+)\s+(\d+)\s*\)(\s*simpleGrading)")

    def repl(m):
        a, b, c = int(m.group(1)), int(m.group(2)), int(m.group(3))
        c2 = c * fz                       # axial (z): sempre
        if a == b:                        # nucleo: ambas no plano seguem tangencial
            a2, b2 = a * ft, b * ft
        else:                             # anel: n1=radial (fr), n2=tangencial (ft)
            a2, b2 = a * fr, b * ft
        return f"( {a2} {b2} {c2} ){m.group(4)}"

    new_txt, n = pat.subn(repl, txt)
    open(out_path, "w").write(new_txt)
    print(f"refine_blockmesh: {n} blocos escalados (fr={fr}, ft={ft}, fz={fz}) "
          f"-> {out_path}")
    if n == 0:
        print("AVISO: nenhum bloco casado (verifique o formato do dict)")
        sys.exit(1)


def coarsen(in_path: str, out_path: str, fr: float, ft: float, fz: float):
    """Como refine(), mas com fatores FRACIONARIOS (<1) para ENGROSSAR a malha.

    Arredonda para inteiro e clampa em >=1. NUNCA reduz uma direcao que ja' tem
    1 celula (preserva os blocos axiais de 1 celula -- LC/globo -- e laminas
    radiais finas quando fr mantem >=1). Mantem a compatibilidade do O-grid:
    o nucleo (a==b) segue o fator tangencial.
    """
    txt = open(in_path).read()
    pat = re.compile(r"\(\s*(\d+)\s+(\d+)\s+(\d+)\s*\)(\s*simpleGrading)")

    def repl(m):
        a, b, c = int(m.group(1)), int(m.group(2)), int(m.group(3))
        c2 = c if c == 1 else max(1, round(c * fz))
        if a == b:
            a2 = b2 = max(1, round(a * ft))
        else:
            a2 = max(1, round(a * fr))
            b2 = max(1, round(b * ft))
        return f"( {a2} {b2} {c2} ){m.group(4)}"

    new_txt, n = pat.subn(repl, txt)
    open(out_path, "w").write(new_txt)
    print(f"coarsen_blockmesh: {n} blocos escalados (fr={fr}, ft={ft}, fz={fz}) "
          f"-> {out_path}")
    if n == 0:
        print("AVISO: nenhum bloco casado (verifique o formato do dict)")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) == 4:
        f = int(sys.argv[3])
        refine(sys.argv[1], sys.argv[2], f, f, f)
    elif len(sys.argv) == 6:
        refine(sys.argv[1], sys.argv[2],
               int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
    else:
        print(__doc__)
        sys.exit(2)
