#!/usr/bin/env python3
"""
frd_stress.py
=============
Parser do .frd do CalculiX 2.20 para EXTRAIR campos nodais (DISP e STRESS) e
agrega-los por ZONA anatomica, sem depender do .vtu nem do .inp.

Por que o .frd basta: o bloco de elementos (3C) ja' carrega, por elemento, o
NUMERO do material; o cabecalho (linhas "1UMAT  <id><NOME>") mapeia esse numero
para o nome do material (ON_MAT, PIA_MAT, DURA_MAT, ...). Logo conseguimos
no->zona diretamente do proprio .frd, de forma robusta a refino de malha (o
conversor foam_polymesh_to_ccx_inp.py mantem a numeracao de materiais).

Saida principal (funcao analyze_frd):
  dict com, por passo de carga (load factor lambda do Riks):
    - lam           : load factor (= tempo do *STATIC,RIKS)
    - vm_global_max : pico de von Mises sobre TODOS os nos com tensao (Pa)
    - vm_zone_max   : {zona -> pico de von Mises nos nos daquela zona} (Pa)
    - ulat_zone_max : {zona -> max |U_lat|=sqrt(Ux^2+Uy^2) dos nos da zona} (m)

Formato de coluna (fixo) das linhas de dado " -1":
    coln 1-3  : ' -1'
    coln 4-13 : numero do no (I10)
    coln 14.. : valores em E12.5 (12 chars cada; negativos colam, por isso o
                parsing e' por LARGURA FIXA e nao por split()).

Uso como modulo:
    from frd_stress import analyze_frd
    steps = analyze_frd(Path("cases/on-caso-2/ccx/on-caso-2.frd"))

Uso como script (debug):
    python3 brunaStuff/frd_stress.py cases/on-caso-2/ccx/on-caso-2.frd
"""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

# materiais que NAO sao zonas estruturais (molas Winkler etc.)
_NON_ZONE = {"spring", "springa"}


def _zone_key(mat_name: str) -> str:
    """ON_MAT -> on, SCLERA_PERI_MAT -> sclera_peri, SPRING -> spring."""
    k = mat_name.strip().lower()
    if k.endswith("_mat"):
        k = k[:-4]
    return k


def _f(s: str) -> float:
    """Float robusto de um campo E12.5 (pode vir vazio/espacos)."""
    s = s.strip()
    return float(s) if s else 0.0


def parse_frd(path: Path):
    """Le o .frd uma vez. Retorna:

        nodes  : nao usado a jusante, mantido p/ completude {nid: (x,y,z)}
        n2zone : {nid -> set(zonas)} (no pode tocar varias zonas nas interfaces)
        steps  : list de dicts {lam, disp:{nid:(ux,uy,uz)}, vm:{nid:vmises}}
    """
    text_lines = path.read_text().splitlines()

    mat_name: dict[int, str] = {}
    nodes: dict[int, tuple] = {}
    elem_mat: dict[int, int] = {}
    elem_nodes: dict[int, list] = {}

    steps: list[dict] = []
    cur_lam = None
    cur_field = None          # 'DISP' | 'STRESS' | None
    cur_step: dict | None = None

    section = None            # 'nodes' | 'elems' | 'result' | None
    pending_elem = None       # eid aguardando linha -2 (connectividade)

    re_mat = re.compile(r"1UMAT\s+(\d+)\s*(\S.*)$")

    for raw in text_lines:
        # --- cabecalho de materiais ---
        if "1UMAT" in raw:
            m = re_mat.search(raw)
            if m:
                mat_name[int(m.group(1))] = m.group(2).strip()
            continue

        s = raw.rstrip("\n")
        st = s.strip()
        if not st:
            continue

        # --- abertura de blocos ---
        # node block:  "    2C   <nnodes> ... "
        if re.match(r"\s*2C\b", s):
            section = "nodes"
            continue
        # element block: "    3C   <nelem> ... "
        if re.match(r"\s*3C\b", s):
            section = "elems"
            continue
        # result header: " -4  DISP ..." / " -4  STRESS ..."
        if st.startswith("-4"):
            name = st.split()[1].upper() if len(st.split()) > 1 else ""
            if name in ("DISP", "STRESS"):
                cur_field = name
                section = "result"
                # garante um step para o lambda corrente
                if cur_step is None or cur_step.get("lam") != cur_lam:
                    # procura step ja' existente com este lambda
                    found = None
                    for stp in steps:
                        if stp["lam"] == cur_lam:
                            found = stp
                            break
                    if found is None:
                        found = {"lam": cur_lam, "disp": {}, "vm": {}}
                        steps.append(found)
                    cur_step = found
            else:
                cur_field = None
                section = None
            continue
        # " -5 ..." sao definicoes de componente; ignorar
        if st.startswith("-5"):
            continue
        # fim de bloco
        if st.startswith("-3"):
            section = None
            cur_field = None
            continue

        # linha 100CL define o lambda do passo corrente
        if st.startswith("100CL"):
            parts = st.split()
            try:
                cur_lam = float(parts[2])
            except (IndexError, ValueError):
                cur_lam = None
            continue

        # --- linhas de dado ---
        if section == "nodes" and s[1:3] == "-1":
            nid = int(s[3:13])
            nodes[nid] = (_f(s[13:25]), _f(s[25:37]), _f(s[37:49]))
            continue

        if section == "elems":
            if s[1:3] == "-1":
                eid = int(s[3:13])
                # campos I5 apos o I10: type(5) grp(5) mat(5)
                mat = int(s[23:28]) if len(s) >= 28 else 0
                elem_mat[eid] = mat
                pending_elem = eid
                continue
            if s[1:3] == "-2" and pending_elem is not None:
                ns = [int(s[3 + 10 * k:13 + 10 * k])
                      for k in range((len(s) - 3) // 10)]
                elem_nodes.setdefault(pending_elem, []).extend(ns)
                continue

        if section == "result" and s[1:3] == "-1" and cur_step is not None:
            nid = int(s[3:13])
            if cur_field == "DISP":
                cur_step["disp"][nid] = (_f(s[13:25]), _f(s[25:37]), _f(s[37:49]))
            elif cur_field == "STRESS":
                sxx = _f(s[13:25]); syy = _f(s[25:37]); szz = _f(s[37:49])
                sxy = _f(s[49:61]); syz = _f(s[61:73]); szx = _f(s[73:85])
                vm = math.sqrt(
                    0.5 * ((sxx - syy) ** 2 + (syy - szz) ** 2 + (szz - sxx) ** 2)
                    + 3.0 * (sxy ** 2 + syz ** 2 + szx ** 2)
                )
                cur_step["vm"][nid] = vm
            continue

    # --- no -> zonas (via elemento -> material -> nome) ---
    n2zone: dict[int, set] = {}
    for eid, mat in elem_mat.items():
        zname = _zone_key(mat_name.get(mat, str(mat)))
        if zname in _NON_ZONE:
            continue
        for nid in elem_nodes.get(eid, []):
            n2zone.setdefault(nid, set()).add(zname)

    return nodes, n2zone, steps


def analyze_frd(path: Path):
    """Reduz o .frd a uma lista de passos com picos por zona.

    Cada passo: {lam, dz_mm, vm_global_max, vm_zone_max{}, ulat_zone_max{}}.
    dz_mm assume rampa DZRAMP linear de 1.5 mm (lam=1 -> 1.5 mm).
    """
    nodes, n2zone, steps = parse_frd(path)

    DZ_NOMINAL_MM = 1.5
    out = []
    for stp in sorted(steps, key=lambda d: (d["lam"] if d["lam"] is not None else 0)):
        lam = stp["lam"] if stp["lam"] is not None else float("nan")
        vm = stp["vm"]
        disp = stp["disp"]

        vm_global = max(vm.values()) if vm else float("nan")

        vm_zone: dict[str, float] = {}
        ulat_zone: dict[str, float] = {}
        # acumula por zona
        for nid, zones in n2zone.items():
            v = vm.get(nid)
            u = disp.get(nid)
            ulat = math.hypot(u[0], u[1]) if u else None
            for z in zones:
                if v is not None and (z not in vm_zone or v > vm_zone[z]):
                    vm_zone[z] = v
                if ulat is not None and (z not in ulat_zone or ulat > ulat_zone[z]):
                    ulat_zone[z] = ulat

        out.append(dict(
            lam=lam,
            dz_mm=DZ_NOMINAL_MM * lam if lam == lam else float("nan"),
            vm_global_max=vm_global,
            vm_zone_max=vm_zone,
            ulat_zone_max=ulat_zone,
        ))
    return out


def _main(argv):
    if not argv:
        print(__doc__)
        return 2
    path = Path(argv[0])
    steps = analyze_frd(path)
    print(f"{path}: {len(steps)} passos de carga\n")
    hdr = (f"{'lam':>8s} {'dz[mm]':>8s} {'vm_glob[kPa]':>13s} "
           f"{'vm_pia[kPa]':>12s} {'vm_dura[kPa]':>13s} "
           f"{'kink_pia[mm]':>13s} {'kink_dura[mm]':>14s} {'pia/dura':>9s}")
    print(hdr)
    for s in steps:
        vmz = s["vm_zone_max"]; uz = s["ulat_zone_max"]
        kp = uz.get("pia", float("nan")) * 1e3
        kd = uz.get("dura", float("nan")) * 1e3
        ratio = kp / kd if kd else float("nan")
        print(f"{s['lam']:8.4f} {s['dz_mm']:8.3f} "
              f"{s['vm_global_max']/1e3:13.2f} "
              f"{vmz.get('pia', float('nan'))/1e3:12.2f} "
              f"{vmz.get('dura', float('nan'))/1e3:13.2f} "
              f"{kp:13.4f} {kd:14.4f} {ratio:9.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
