#!/usr/bin/env python3
"""
build_3sf_force_decks.py
========================
Gera, para cada nivel de malha do estudo de independencia do 3F, um deck
'on-caso-3-sf_F.inp' que aplica uma FORCA arterial TOTAL FIXA (em vez da pressao
fixa do baseline). Motivacao: o patch CONTACT_LOCAL_SURF e' uma caixa topoSet
geometrica cujo nº de faces (logo a area, logo F=P*A) varia com a malha; isso
impedia a convergencia no refino GLOBAL. Fixando a FORCA total a carga arterial
passa a ser ~invariante a' malha.

Implementacao: mantem a carga DISTRIBUIDA (pressao na face -> sem singularidade
de carga pontual), porem ESCALA a pressao por malha de modo que a resultante
lateral seja a mesma F_TARGET:
    P_malha = P_REF * F_TARGET / F_lat_malha(P_REF)
onde F_lat_malha(P_REF) e' a resultante lateral medida no run baseline (P_REF=
9034 Pa) lida do .dat. Substitui o valor do
    *DSLOAD
    CONTACT_LOCAL_SURF, P, 9034
por P_malha. A PIC (DURA_INNER_SURF, P=1333) e' mantida. F_TARGET = resultante
lateral da malha de PRODUCAO sob p_c=9034 Pa (preserva a ancora do artigo).

(Tentou-se *CLOAD nodal puro -X, mas concentrar a forca em ~6 nos gera indentacao
local irreal de ~1.8 mm e divergencia do Riks perto da carga plena; a pressao
escalada mantem o campo distribuido e converge.)

Uso (HOST): python3 brunaStuff/build_3sf_force_decks.py
Depois rode os decks _F no container (ccx_preCICE -i on-caso-3-sf_F).
"""
from __future__ import annotations

import math
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DECK = "on-caso-3-sf"
P_REF = 9034.0      # Pa, pressao baseline do sweep (1.0x)

LEVELS = [
    ("f100", REPO / "cases" / DECK / "ccx"),
    ("f150", REPO / "cases/_mi" / f"{DECK}__f150" / "ccx"),
    ("radpia2dura3", REPO / "cases/_mi" / f"{DECK}__radpia2dura3" / "ccx"),
    ("radpia3dura4", REPO / "cases/_mi" / f"{DECK}__radpia3dura4" / "ccx"),
]


def lateral_force_N(dat: Path) -> float:
    """Resultante lateral |F_x,y| no engaste posterior no ultimo tempo do run baseline."""
    if not dat.exists():
        return float("nan")
    txt = dat.read_text(errors="ignore").splitlines()
    NUM = r"-?\d+\.\d+(?:[Ee][+\-]?\d+)?"
    rec: dict[float, dict[str, list[float]]] = {}
    for i, L in enumerate(txt):
        m = re.match(r"\s*total force.*for set (\S+) and time\s+([\d.E+\-]+)", L, re.I)
        if not m:
            continue
        nset, t = m.group(1).upper(), float(m.group(2))
        j = i + 1
        while j < len(txt) and not txt[j].strip():
            j += 1
        nums = [float(x) for x in re.findall(NUM, txt[j])] if j < len(txt) else []
        if len(nums) >= 3:
            rec.setdefault(round(t, 6), {})[nset] = nums[:3]
    if not rec:
        return float("nan")
    d = rec[max(rec)]
    fx = sum(d.get(n, [0, 0, 0])[0] for n in ("POSTERIOR_DURA", "POSTERIOR_PIA", "POSTERIOR_ON"))
    fy = sum(d.get(n, [0, 0, 0])[1] for n in ("POSTERIOR_DURA", "POSTERIOR_PIA", "POSTERIOR_ON"))
    return math.hypot(fx, fy)


def main():
    # F_TARGET = resultante lateral da producao (f100) sob P_REF
    f_target = lateral_force_N(REPO / "cases" / DECK / "ccx" / f"{DECK}.dat")
    print(f"F_TARGET = {f_target*1e3:.2f} mN (resultante lateral da producao f100 sob P_REF={P_REF:.0f} Pa)")
    for level, ccx in LEVELS:
        src = ccx / f"{DECK}.inp"
        dat = ccx / f"{DECK}.dat"
        if not src.exists() or not dat.exists():
            print(f"[SKIP] {level}: deck/.dat ausente em {ccx}")
            continue
        flat = lateral_force_N(dat)
        if not (flat > 0):
            print(f"[SKIP] {level}: F_lat baseline invalida ({flat})")
            continue
        p_mesh = P_REF * f_target / flat
        txt = src.read_text()
        new, k = re.subn(r"(CONTACT_LOCAL_SURF,\s*P,\s*)[^\n]+",
                         rf"\g<1>{p_mesh:.1f}", txt, count=1, flags=re.I)
        if k != 1:
            print(f"[WARN] {level}: nao casou o DSLOAD do contato (k={k})")
            continue
        (ccx / f"{DECK}_F.inp").write_text(new)
        print(f"  {level:14s} F_lat(P_REF)={flat*1e3:6.2f} mN  ->  P_malha={p_mesh:8.1f} Pa")


if __name__ == "__main__":
    main()
