#!/usr/bin/env python3
"""
Gera constant/contact_pressure.dat com pressão CONSTANTE no tempo (sem pulsatil).

Dois pontos (t=0 e t=1 s) com o mesmo valor — o pressureSeries faz clamp fora do
intervalo, então o equilíbrio quasi-estático vê pressão uniforme.

Uso:
  python3 brunaStuff/gen_contact_pressure_constant.py 9000
  python3 brunaStuff/gen_contact_pressure_constant.py 10800 --out /caminho/dat
"""
from __future__ import annotations

import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "cases" / "on-mestrado" / "solid" / "constant" / "contact_pressure.dat"


def write_constant(path: Path, p_pa: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    txt = f"""// on-mestrado — pressão de contato CONSTANTE (sem ciclo cardíaco)
// Gerado por brunaStuff/gen_contact_pressure_constant.py
//
// Valor fixo: {p_pa:.6g} Pa em todo o intervalo de tempo da tabela.
//
// Formato: ( tempo[s]   pressao[Pa] )
(
  ( 0    {p_pa:.6g} )
  ( 1    {p_pa:.6g} )
);
"""
    path.write_text(txt, encoding="utf-8")
    print(f"Escrito: {path}  (P = {p_pa:.6g} Pa constante)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pressure_Pa", type=float, help="Pressão de contato (Pa)")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Arquivo de saída")
    args = ap.parse_args()
    write_constant(args.out, args.pressure_Pa)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
