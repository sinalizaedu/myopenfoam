#!/usr/bin/env python3
"""
gen_pic_initial_stress.py
=========================
Gera o include de *INITIAL CONDITIONS, TYPE=STRESS para impor a PIC
(pressao intracraniana) como prestress hidrostatico no SAS solido do
on-caso-2sP (rota b).

O CalculiX 2.20 exige, para TYPE=STRESS, UMA LINHA POR (elemento, ponto de
integracao): "elem, ip, s11, s22, s33, s12, s13, s23" -- nao aceita rotulo
de elset nem omitir o ponto de integracao. C3D8I tem 8 pontos de integracao.

Le os elementos do ELSET=SAS direto do mesh .inp (numeracao deterministica
gerada pelo conversor) e escreve as linhas de dados (sem o cabecalho
*INITIAL CONDITIONS, que fica no .inp principal via *INCLUDE).

Uso:
  python3 gen_pic_initial_stress.py <mesh.inp> <out_pic.inp> [P_Pa] [n_ip]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def sas_elements(mesh_inp: Path) -> list[int]:
    txt = mesh_inp.read_text()
    blocks = re.findall(r"\*ELEMENT[^\n]*ELSET=SAS\b(.*?)(?=\n\*)",
                        txt, re.IGNORECASE | re.DOTALL)
    ids: list[int] = []
    for blk in blocks:
        for line in blk.strip().splitlines():
            head = line.split(",")[0].strip()
            if head.isdigit():
                ids.append(int(head))
    return ids


def main() -> None:
    mesh_inp = Path(sys.argv[1])
    out = Path(sys.argv[2])
    P = float(sys.argv[3]) if len(sys.argv) > 3 else 1333.0   # Pa (~10 mmHg)
    n_ip = int(sys.argv[4]) if len(sys.argv) > 4 else 8       # C3D8I -> 8 IP

    els = sas_elements(mesh_inp)
    if not els:
        raise SystemExit(f"Nenhum elemento SAS encontrado em {mesh_inp}")

    s = f"{-P:.4e}"   # compressao hidrostatica (push-out)
    lines = [
        "** PIC (~10 mmHg) como prestress hidrostatico 2o Piola-Kirchhoff no SAS.",
        f"** Gerado por gen_pic_initial_stress.py: {len(els)} elementos x {n_ip} IP.",
    ]
    for e in els:
        for ip in range(1, n_ip + 1):
            lines.append(f"{e}, {ip}, {s}, {s}, {s}, 0., 0., 0.")
    out.write_text("\n".join(lines) + "\n")
    print(f"OK: {out} ({len(els)} elementos SAS x {n_ip} IP = {len(els)*n_ip} linhas, P={P} Pa)")


if __name__ == "__main__":
    main()
