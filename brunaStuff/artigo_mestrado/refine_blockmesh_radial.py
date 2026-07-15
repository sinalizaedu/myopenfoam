#!/usr/bin/env python3
"""
refine_blockmesh_radial.py
==========================
Refino RADIAL DIRIGIDO (through-thickness) das laminas meningeas pia e dura,
para o estudo de independencia de malha do on-caso-2. Aumenta APENAS a contagem
radial (n1) dos blocos das laminas finas, deixando tudo o mais intacto.

Motivacao: a critica mais sensivel a malha de producao e' que a pia tem 1 celula
radial e a dura 2 -- pobre para resolver a FLEXAO das laminas (que governa o modo
S e a razao kink pia/dura). Este script isola esse eixo de refino: em vez de
refinar a malha inteira (refine_blockmesh.py), so' adensa a espessura da pia/dura.

Compatibilidade de malha: nos blocos de anel a tripla "( n1 n2 n3 )" tem
n1=radial, n2=tangencial, n3=axial. As faces que a pia/dura compartilham com os
vizinhos internos (on/sas) e externos (sas/sclera) estao no plano tangencial x
axial (n2 x n3), que NAO e' tocado -> nenhum vizinho precisa mudar. Ja' os blocos
da MESMA lamina empilhados em z (pia em z=0-30, sclera_peri_pia em z=30-30.3,
globo_pia em z=30.3-30.8; idem dura) compartilham faces no plano r x theta, logo
TODOS recebem o mesmo n1 -- por isso casamos por TAG de comentario do bloco
(qualquer bloco cujo comentario contenha "pia" ou "dura").

Identificacao: cada bloco "hex ( ... ) ZONA ( n1 n2 n3 ) simpleGrading (...) // TAG".
  - TAG contendo "pia"  (pia_*, sclera_peri_pia_*, globo_pia_*)  -> n1 = --pia
  - TAG contendo "dura" (dura_*, sclera_ring_dura_*, globo_dura_*)-> n1 = --dura
Nenhum outro bloco contem "pia"/"dura" no comentario (sas/on/lc/globo/sclera_ring
sasOut, etc.), entao o casamento e' inequivoco.

Uso:
    python3 refine_blockmesh_radial.py --in DICT --out DICT --pia 2 --dura 3
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

# bloco com tripla + simpleGrading + comentario "// tag"
_BLOCK = re.compile(
    r"(\(\s*)(\d+)(\s+\d+\s+\d+\s*\)\s*simpleGrading\s*\([^)]*\)\s*//\s*)(\S+)"
)


def refine_radial(in_path: Path, out_path: Path, pia_r: int, dura_r: int):
    n_pia = n_dura = 0

    def repl(m):
        nonlocal n_pia, n_dura
        tag = m.group(4).lower()
        n1 = m.group(2)
        if "pia" in tag:
            n1 = str(pia_r); n_pia += 1
        elif "dura" in tag:
            n1 = str(dura_r); n_dura += 1
        return m.group(1) + n1 + m.group(3) + m.group(4)

    txt = in_path.read_text()
    new_txt, _ = _BLOCK.subn(repl, txt)
    out_path.write_text(new_txt)
    print(f"refine_blockmesh_radial: pia n1->{pia_r} ({n_pia} blocos), "
          f"dura n1->{dura_r} ({n_dura} blocos) -> {out_path}")
    if n_pia == 0 or n_dura == 0:
        raise SystemExit("AVISO: nenhum bloco pia/dura casado (verifique os "
                         "comentarios // tag do blockMeshDict).")


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True, type=Path)
    ap.add_argument("--out", dest="out", required=True, type=Path)
    ap.add_argument("--pia", type=int, required=True, help="celulas radiais na pia")
    ap.add_argument("--dura", type=int, required=True, help="celulas radiais na dura")
    args = ap.parse_args()
    refine_radial(args.inp, args.out, args.pia, args.dura)


if __name__ == "__main__":
    main()
