#!/usr/bin/env python3
"""
gauge_stress.py
===============
Metrica de tensao OBJETIVA DE MALHA para a pegada da arteria (on-caso-3).

Problema: o PICO nodal de von Mises na borda do patch de pressao imposta e' uma
SINGULARIDADE de descontinuidade de tracao -> diverge com o refino (nao converge
por definicao). Para reportar um numero convergido usa-se a pratica de
"hot-spot / gauge stress": a MEDIA PONDERADA POR VOLUME de von Mises numa regiao
de TAMANHO FISICO FIXO em torno do centro do contato. Como a singularidade de
borda e' integravel, a integral de volume / V converge com o refino (ao
contrario do pico pontual).

  gauge(R) = sum_e (vM_e * V_e) / sum_e V_e ,  centroide_e dentro do raio R

Centro do contato: no de MAIOR von Mises na faixa +x do patch contact_local.
Volume de hexaedro C3D8(I): decomposicao em 6 tetraedros em torno da diagonal
espacial (robusta p/ qualquer hex convexo).

Uso:
    python3 brunaStuff/gauge_stress.py <arquivo.frd> [--lam 0.84]
    python3 brunaStuff/gauge_stress.py --compare \
        f100=.../on-caso-3_Pc9034.frd \
        radpia2dura3=.../on-caso-3_Pc9034.frd \
        radpia3dura4=.../on-caso-3.frd  --lam 0.84
"""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

from frd_stress import parse_frd, _f

# raios de media volumetrica (mm) em torno do centro do contato
AVG_R_MM = [1.8, 2.0, 2.5, 3.0]
# faixa axial onde mora o patch contact_local (m)
Z_BAND = (0.018, 0.027)

# 6-tetra decomposition de um hex (nos 0..7) em torno da diagonal 0-6
_TETS = [(0, 1, 2, 6), (0, 2, 3, 6), (0, 3, 7, 6),
         (0, 7, 4, 6), (0, 4, 5, 6), (0, 5, 1, 6)]


def _parse_elems(path: Path):
    """{eid: [n0..n7]} apenas para elementos com 8 nos (C3D8/C3D8I)."""
    elems: dict[int, list[int]] = {}
    section = None
    pending = None
    for s in path.read_text().splitlines():
        if re.match(r"\s*3C\b", s):
            section = "elems"; continue
        st = s.strip()
        if section == "elems":
            if st.startswith("-3"):
                section = None; continue
            if s[1:3] == "-1":
                pending = int(s[3:13]); continue
            if s[1:3] == "-2" and pending is not None:
                ns = [int(s[3 + 10*k:13 + 10*k]) for k in range((len(s) - 3)//10)]
                elems.setdefault(pending, []).extend(ns)
    return {e: ns for e, ns in elems.items() if len(ns) == 8}


def _tet_vol(a, b, c, d):
    ux, uy, uz = b[0]-a[0], b[1]-a[1], b[2]-a[2]
    vx, vy, vz = c[0]-a[0], c[1]-a[1], c[2]-a[2]
    wx, wy, wz = d[0]-a[0], d[1]-a[1], d[2]-a[2]
    det = (ux*(vy*wz - vz*wy) - uy*(vx*wz - vz*wx) + uz*(vx*wy - vy*wx))
    return abs(det) / 6.0


def _hex_vol(p):
    return sum(_tet_vol(p[i], p[j], p[k], p[l]) for (i, j, k, l) in _TETS)


def _pick_step(steps, target_lam):
    cand = [s for s in steps if s["vm"]]
    if not cand:
        return None
    if target_lam is None:
        return max(cand, key=lambda s: (s["lam"] if s["lam"] is not None else -1))
    return min(cand, key=lambda s: abs((s["lam"] or 0.0) - target_lam))


def _contact_center(nodes, vm):
    best_nid, best_vm = None, -1.0
    for nid, v in vm.items():
        xyz = nodes.get(nid)
        if xyz is None or xyz[0] <= 0:
            continue
        if not (Z_BAND[0] <= xyz[2] <= Z_BAND[1]):
            continue
        if v > best_vm:
            best_vm, best_nid = v, nid
    return best_nid, best_vm


def gauge(path: Path, target_lam=None):
    nodes, _n2zone, steps = parse_frd(path)
    elems = _parse_elems(path)
    stp = _pick_step(steps, target_lam)
    if stp is None:
        raise SystemExit(f"{path}: sem passo com tensao")
    vm = stp["vm"]
    lam = stp["lam"]
    cnid, cvm = _contact_center(nodes, vm)
    if cnid is None:
        raise SystemExit(f"{path}: centro de contato nao localizado")
    center = nodes[cnid]

    # pre-computa centroide, volume e vM medio por elemento (so com tensao)
    ec = []  # (centroid, vol, vm_elem)
    for ns in elems.values():
        pts = [nodes[n] for n in ns if n in nodes]
        if len(pts) != 8:
            continue
        vms = [vm[n] for n in ns if n in vm]
        if not vms:
            continue
        cx = sum(p[0] for p in pts) / 8.0
        cy = sum(p[1] for p in pts) / 8.0
        cz = sum(p[2] for p in pts) / 8.0
        ec.append(((cx, cy, cz), _hex_vol(pts), sum(vms) / len(vms)))

    avg_vals = []
    for r_mm in AVG_R_MM:
        r2 = (r_mm * 1e-3) ** 2
        sv = sw = 0.0
        n = 0
        for (cx, cy, cz), vol, ve in ec:
            if (cx-center[0])**2 + (cy-center[1])**2 + (cz-center[2])**2 <= r2:
                sv += ve * vol
                sw += vol
                n += 1
        avg_vals.append((r_mm, (sv / sw if sw else float("nan")), n))

    return dict(lam=lam, center=center, peak=cvm, avg=avg_vals,
                nnodes=len(nodes), nelems=len(elems))


def _fmt_one(tag, g):
    print(f"\n### {tag}  (lam={g['lam']:.3f}, nos={g['nnodes']}, "
          f"hex={g['nelems']}, centro z={g['center'][2]*1e3:.1f} mm)")
    print(f"  pico nodal na pegada (NAO converge): {g['peak']/1e3:8.1f} kPa")
    print("  gauge = media von Mises PONDERADA POR VOLUME (raio fixo):")
    for r_mm, a, n in g["avg"]:
        print(f"    R={r_mm:.2f} mm -> {a/1e3:8.2f} kPa  ({n} hex)")


def _main(argv):
    if not argv:
        print(__doc__); return 2
    target_lam = None
    if "--lam" in argv:
        i = argv.index("--lam")
        target_lam = float(argv[i+1])
        argv = argv[:i] + argv[i+2:]

    if argv and argv[0] == "--compare":
        rows = {}
        for spec in argv[1:]:
            tag, _, p = spec.partition("=")
            rows[tag] = gauge(Path(p), target_lam)
        for tag, g in rows.items():
            _fmt_one(tag, g)
        print("\n=== CONVERGENCIA (mesmo lam, malhas crescentes) ===")
        tags = list(rows)
        print("metrica".ljust(20) + "".join(t.rjust(16) for t in tags))
        print("pico nodal".ljust(20) +
              "".join(f"{rows[t]['peak']/1e3:16.1f}" for t in tags))
        for k, (r_mm, *_) in enumerate(rows[tags[0]]["avg"]):
            line = f"gauge R={r_mm:.2f}mm".ljust(20)
            for t in tags:
                line += f"{rows[t]['avg'][k][1]/1e3:16.2f}"
            print(line)
        return 0

    _fmt_one(Path(argv[0]).name, gauge(Path(argv[0]), target_lam))
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
