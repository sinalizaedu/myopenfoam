#!/usr/bin/env python3
"""Estudo de INDEPENDENCIA DE MALHA do on-caso-1.2 (lado SOLIDO / CalculiX).

A grandeza de interesse (QoI) e' a resposta estrutural da bainha sob a carga de
compartimentalizacao do SANS: uma pressao ~uniforme de PIC na parede da SAS. A
forma metodologicamente correta de avaliar independencia de malha e' VARIAR SO A
MALHA mantendo a carga fixa (no FSI completo mudariam ao mesmo tempo a malha do
fluido, o mapeamento RBF e a propria carga -> estudo confundido).

Para cada nivel de refino r (fator multiplicativo das resolucoes do blockMesh):
  1. (host)      gera o blockMeshDict do solido com as resolucoes escaladas;
  2. (container) blockMesh + topoSet + createPatch -> polyMesh redondo;
  3. (host)      converte polyMesh -> CalculiX (all.msh/all.nam/winkler.inp),
                 agora exportando tambem *SURFACE de fsi_pia e fsi_dura;
  4. (host)      escreve um deck CalculiX STANDALONE (sem preCICE) com a carga
                 SANS-equivalente: P=3800 Pa em Sfsi_pia/Sfsi_dura (PIC na
                 bainha) + 1333 Pa nas caps de esclera + 9034 Pa na arteria;
  5. (container) ccx_preCICE -i main  (sem -precice-participant = ccx puro,
                 com incrementacao automatica que rampa a carga e converge);
  6. (host)      extrai o deslocamento RADIAL medio do anel da dura (r=2.35) e
                 da pia (r=1.55) em z=30 mm -> expansao da bainha / compressao
                 do nervo.

Saidas: cases/on-caso-1.2/_mesh_indep/r<level>/  e  _mesh_indep/results.json
Uso:
    python3 brunaStuff/mesh_independence_caso_1_2.py 1 2 3
"""
from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))

import gen_on_caso_1_blockmesh as gen1          # noqa: E402
import gen_on_caso_1_2_from_blockmesh as gen2   # noqa: E402

CASE = REPO / "cases" / "on-caso-1.2"
ROOT = CASE / "_mesh_indep"
SCRATCH = ROOT / "_scratch_solid"          # case OpenFOAM efemero (geracao da malha)
SRC_SYS = REPO / "cases" / "on-caso-1" / "solid" / "system"

# Carga SANS-equivalente (Pa). Convencao CCX *DLOAD: P>0 empurra a face p/ dentro
# do elemento. Em Sfsi_pia (face da pia voltada p/ SAS) -> pia p/ DENTRO (-r).
# Em Sfsi_dura (face da dura voltada p/ SAS) -> dura p/ FORA (+r). Identico ao
# efeito do FSI compartimentalizado (ICP na parede da SAS).
P_ICP    = 3800.0    # PIC SANS na parede da SAS (fsi_pia + fsi_dura)
P_SCLERA = 1333.0    # caps de esclera (desacoplamento seletivo)
P_ARTERY = 9034.0    # arteria oftalmica (contact_local)

# Solver do CalculiX. spooles (direto) e' exato e robusto para o material quase-
# incompressivel (nu=0.45). O ITERATIVE CHOLESKY (CG pre-condicionado) bate com o
# spooles na malha grossa mas ESTAGNA (mal condicionamento de nu->0.5) ao refinar,
# entao usamos spooles. Docker aqui tem ~7.6 GB -> spooles cabe ate' ~1.5e5 eq;
# por isso o refino global vai ate' fator 1.5 (malha x1.5 em cada direcao).
SOLVER = "SPOOLES"

# Tipo de elemento CalculiX. C3D8 (integracao completa) sofre travamento
# volumetrico/cisalhante em camadas finas quase-incompressiveis (a pia, 0.05 mm,
# nu=0.45). C3D8I (modos incompativeis) elimina esse locking. O sweep e' rodado
# com ambos para separar erro de MALHA de erro de FORMULACAO do elemento.
ELEM = "C3D8"

R_PIA  = 1.55e-3     # raio do anel da pia  (parede interna da SAS)
R_DURA = 2.35e-3     # raio do anel da dura (parede externa da SAS, lado fluido)
Z_TOP  = 30.0e-3     # cota peripapilar (z=30 mm) onde ficam os watchpoints FSI


# ---------------------------------------------------------------------------
def sh(cmd: str, **kw):
    print(f"  $ {cmd}")
    return subprocess.run(cmd, shell=True, cwd=str(REPO), check=True, **kw)


def docker(inner: str):
    """Executa 'inner' dentro do container (cases montado em /simulation)."""
    return sh(f'docker compose run --rm fsi bash -lc {json.dumps(inner)}')


def scaled_res(f: float) -> dict:
    s = lambda v: max(1, int(round(v * f)))
    return dict(
        N_TANG=s(8), N_RAD_ON=s(6), N_RAD_CTR=s(8), N_RAD_PIA=s(1),
        N_RAD_SAS_IN=s(3), N_RAD_SAS_OUT=s(3), N_RAD_DURA=s(2),
        N_AXIAL_SOLID=(s(30), s(1), s(1)),
    )


def write_solid_blockmeshdict(res: dict, out: Path):
    for k, v in res.items():
        setattr(gen1, k, v)
    vs = gen1.build_vertices(gen1.Z_LEVELS_SOLID)
    txt = "\n".join([
        gen1.HEADER_SOLID, "",
        gen1.render_vertices(vs), "",
        gen1.render_solid_blocks(), "",
        gen1.render_edges_solid(), "",
        gen1.render_solid_boundary(), "",
    ]) + "\n"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(txt)


def setup_scratch_case():
    (SCRATCH / "system").mkdir(parents=True, exist_ok=True)
    (SCRATCH / "constant").mkdir(parents=True, exist_ok=True)
    for fn in ("controlDict", "fvSchemes", "fvSolution",
               "topoSetDict_contact", "createPatchDict_contact"):
        shutil.copy(SRC_SYS / fn, SCRATCH / "system" / fn)


def parse_nodes(all_msh: Path) -> dict[int, tuple[float, float, float]]:
    nodes = {}
    in_node = False
    for ln in all_msh.read_text().splitlines():
        s = ln.strip()
        if s.startswith("*"):
            in_node = s.upper().startswith("*NODE")
            continue
        if in_node and s and not s.startswith("**"):
            p = s.split(",")
            nodes[int(p[0])] = (float(p[1]), float(p[2]), float(p[3]))
    return nodes


def ring_nset(nodes, r_target, z_target, name, r_tol=2e-5, z_tol=1e-5):
    ids = []
    for nid, (x, y, z) in nodes.items():
        r = math.hypot(x, y)
        if abs(r - r_target) < r_tol and abs(z - z_target) < z_tol:
            ids.append(nid)
    lines = [f"*NSET, NSET={name}"]
    for i in range(0, len(ids), 8):
        lines.append(", ".join(str(v) for v in ids[i:i + 8]))
    return ids, "\n".join(lines)


DECK = """** on-caso-1.2 -- deck STANDALONE para independencia de malha (sem preCICE).
*HEADING
on-caso-1.2 mesh-independence (solid, SANS-equivalent load)
*INCLUDE, INPUT=all.msh
*INCLUDE, INPUT=all.nam
*INCLUDE, INPUT=rings.nam

*MATERIAL, NAME=ON_MAT
*HYPERELASTIC, NEO HOOKE
5.172e3, 2.000e-5
*DENSITY
1000.0
*MATERIAL, NAME=PIA_MAT
*HYPERELASTIC, NEO HOOKE
5.172e5, 2.000e-7
*DENSITY
1100.0
*MATERIAL, NAME=DURA_MAT
*HYPERELASTIC, NEO HOOKE
5.172e5, 2.000e-7
*DENSITY
1100.0
*MATERIAL, NAME=LC_MAT
*HYPERELASTIC, NEO HOOKE
6.897e4, 1.500e-6
*DENSITY
1100.0
*MATERIAL, NAME=SCLERA_PERI_MAT
*HYPERELASTIC, NEO HOOKE
8.621e5, 1.200e-7
*DENSITY
1400.0
*MATERIAL, NAME=SCLERA_RING_MAT
*HYPERELASTIC, NEO HOOKE
8.621e5, 1.200e-7
*DENSITY
1400.0
*MATERIAL, NAME=GLOBO_MAT
*HYPERELASTIC, NEO HOOKE
8.621e5, 1.200e-7
*DENSITY
1400.0

*SOLID SECTION, ELSET=EALL_ON,          MATERIAL=ON_MAT
*SOLID SECTION, ELSET=EALL_PIA,         MATERIAL=PIA_MAT
*SOLID SECTION, ELSET=EALL_DURA,        MATERIAL=DURA_MAT
*SOLID SECTION, ELSET=EALL_LC,          MATERIAL=LC_MAT
*SOLID SECTION, ELSET=EALL_SCLERA_PERI, MATERIAL=SCLERA_PERI_MAT
*SOLID SECTION, ELSET=EALL_SCLERA_RING, MATERIAL=SCLERA_RING_MAT
*SOLID SECTION, ELSET=EALL_GLOBO,       MATERIAL=GLOBO_MAT

*BOUNDARY
Nposterior_on,   1, 3, 0.0
Nposterior_pia,  1, 3, 0.0
Nposterior_dura, 1, 3, 0.0
*BOUNDARY
Nglobo_outer, 1, 3, 0.0
*INCLUDE, INPUT=winkler.inp

*STEP, NLGEOM, INC=1000
*STATIC, SOLVER={SOLVER}
0.1, 1.0, 1e-5, 0.25

** PIC SANS na parede da SAS (= efeito do FSI compartimentalizado)
*DLOAD
Sfsi_pia,  P, {P_ICP}
Sfsi_dura, P, {P_ICP}
** caps de esclera (desacoplamento seletivo)
*DLOAD
Sfsi_sclera_peri, P, {P_SCLERA}
Sfsi_sclera_ring, P, {P_SCLERA}
** arteria oftalmica
*DLOAD
Scontact_local, P, {P_ARTERY}

*NODE FILE
U
*EL FILE
S, E
*NODE PRINT, NSET=Npia_z30
U
*NODE PRINT, NSET=Ndura_z30
U
*END STEP
"""


def parse_dat_last(dat: Path, setname: str) -> dict[int, tuple]:
    txt = dat.read_text()
    blocks = list(re.finditer(
        rf"displacements.*?for set {setname.upper()}.*?\n", txt, re.IGNORECASE))
    if not blocks:
        return {}
    start = blocks[-1].end()
    out = {}
    for ln in txt[start:].splitlines():
        s = ln.strip()
        if not s:
            if out:
                break
            continue
        if s.lower().startswith("node") or "vx" in s.lower():
            continue
        p = s.split()
        if len(p) >= 4:
            try:
                out[int(p[0])] = (float(p[1]), float(p[2]), float(p[3]))
            except ValueError:
                break
    return out


def mean_radial(nodes, disp, ids):
    vals = []
    for nid in ids:
        if nid not in disp:
            continue
        x, y, _ = nodes[nid]
        ux, uy, _ = disp[nid]
        r = math.hypot(x, y)
        if r > 0:
            vals.append((x * ux + y * uy) / r)
    if not vals:
        return (float("nan"), float("nan"), float("nan"), 0)
    return (float(np.mean(vals)), float(np.min(vals)), float(np.max(vals)),
            len(vals))


def n_eq_from_log(log: Path) -> int:
    m = re.search(r"number of equations\s*\n\s*(\d+)", log.read_text())
    return int(m.group(1)) if m else -1


def run_level(f: float) -> dict:
    tag = f"r{f:g}".replace(".", "p") + ("" if ELEM == "C3D8" else "_i")
    ldir = ROOT / tag
    sdir = ldir  # all.msh etc. ficam direto no level dir
    sdir.mkdir(parents=True, exist_ok=True)
    res = scaled_res(f)
    print(f"\n===== NIVEL {tag}  resolucoes={res} =====")

    # 1) blockMeshDict do solido
    write_solid_blockmeshdict(res, SCRATCH / "system" / "blockMeshDict")

    # 2) malha (container)
    docker(
        "cd on-caso-1.2/_mesh_indep/_scratch_solid && rm -rf constant/polyMesh 0 log.* && "
        "blockMesh > log.blockMesh 2>&1 && "
        "topoSet -dict system/topoSetDict_contact > log.topoSet 2>&1 && "
        "createPatch -overwrite -dict system/createPatchDict_contact > log.createPatch 2>&1 && "
        "echo OK_MESH"
    )

    # 3) converte polyMesh -> CalculiX
    gen2.ELEMENT_TYPE = ELEM
    gen2.POLYMESH = SCRATCH / "constant" / "polyMesh"
    gen2.OUT_DIR = sdir
    gen2.SURFACE_PATCHES = ("contact_local", "fsi_sclera_peri", "fsi_sclera_ring",
                            "fsi_pia", "fsi_dura")
    gen2.main()

    # 4) deck + rings
    nodes = parse_nodes(sdir / "all.msh")
    pia_ids, pia_ns = ring_nset(nodes, R_PIA, Z_TOP, "Npia_z30")
    dura_ids, dura_ns = ring_nset(nodes, R_DURA, Z_TOP, "Ndura_z30")
    (sdir / "rings.nam").write_text(
        f"** aneis z=30mm p/ QoI\n{pia_ns}\n**\n{dura_ns}\n")
    (sdir / "main.inp").write_text(
        DECK.format(P_ICP=P_ICP, P_SCLERA=P_SCLERA, P_ARTERY=P_ARTERY, SOLVER=SOLVER))
    n_nodes = len(nodes)
    print(f"  nodes={n_nodes}  anel pia={len(pia_ids)}  anel dura={len(dura_ids)}")

    # 5) ccx standalone (container)
    docker(
        f"cd on-caso-1.2/_mesh_indep/{tag} && rm -f main.frd main.dat main.sta main.cvg && "
        "export OMP_NUM_THREADS=8 && "
        "ccx_preCICE -i main > log.ccx 2>&1 ; tail -3 log.ccx"
    )

    # 6) extrai QoI
    disp_pia = parse_dat_last(sdir / "main.dat", "Npia_z30")
    disp_dura = parse_dat_last(sdir / "main.dat", "Ndura_z30")
    pia = mean_radial(nodes, disp_pia, pia_ids)
    dura = mean_radial(nodes, disp_dura, dura_ids)
    neq = n_eq_from_log(sdir / "log.ccx")
    out = dict(level=tag, factor=f, n_nodes=n_nodes, n_eq=neq,
               n_pia=len(pia_ids), n_dura=len(dura_ids),
               dura_mean_um=dura[0] * 1e6, dura_min_um=dura[1] * 1e6,
               dura_max_um=dura[2] * 1e6,
               pia_mean_um=pia[0] * 1e6, pia_min_um=pia[1] * 1e6,
               pia_max_um=pia[2] * 1e6)
    print(f"  n_eq={neq}  dura_mean={out['dura_mean_um']:+.4f} um  "
          f"pia_mean={out['pia_mean_um']:+.4f} um")
    return out


def main():
    global ELEM
    args = sys.argv[1:]
    if args and args[0].upper() in ("C3D8", "C3D8I"):
        ELEM = args.pop(0).upper()
    factors = [float(a) for a in args] or [1.0, 1.25, 1.5]
    setup_scratch_case()
    results_path = ROOT / f"results_{ELEM}.json"
    results = []
    if results_path.exists():
        results = json.loads(results_path.read_text())
    for f in factors:
        r = run_level(f)
        results = [x for x in results if x["level"] != r["level"]] + [r]
        results.sort(key=lambda x: x["factor"])
        results_path.write_text(json.dumps(results, indent=2))
    print("\n===== RESUMO =====")
    print(f"{'nivel':>6} {'n_eq':>8} {'dura_mean(um)':>14} {'pia_mean(um)':>13}")
    for x in results:
        print(f"{x['level']:>6} {x['n_eq']:>8} {x['dura_mean_um']:>14.4f} "
              f"{x['pia_mean_um']:>13.4f}")
    print(f"\nresultados -> {results_path}")


if __name__ == "__main__":
    main()
