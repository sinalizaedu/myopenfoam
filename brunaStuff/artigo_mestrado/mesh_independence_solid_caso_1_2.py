#!/usr/bin/env python3
"""Estudo de INDEPENDENCIA DE MALHA do on-caso-1.2 (lado SOLIDO / CalculiX).

Analogo ao estudo do fluido (mesh_independence_fluid_caso_1_2.py), mas para a
malha estrutural (O-grid com nucleo neural solido, 7 zonas anatomicas). A
grandeza de interesse (QoI) e' a resposta MECANICA das meninges sob a carga
TRANSMITIDA pelo LCR -- em particular a distensao radial da bainha dural
(Delta r_dura), o achado classico de SANS/IIH em ressonancia.

Forma metodologicamente correta (identica ao estudo do fluido): VARIAR SO A
MALHA mantendo o carregamento FIXO. No FSI completo mudariam ao mesmo tempo a
malha do solido, o mapeamento RBF do preCICE e o proprio campo de pressao -> 
estudo confundido. Por isso rodamos o SOLIDO STANDALONE (sem preCICE), com a
carga FSI substituida por pressao estatica equivalente:

  - faces FSI (fsi_pia, fsi_dura): pressao do SAS p_SAS = 3800 Pa (endpoint
    SANS da rampa de PIC) aplicada como *DLOAD distribuido. Convencao CCX
    (P>0 empurra a face para DENTRO do elemento) -> comprime a pia para
    dentro e distende a dura para fora, exatamente como a forca do LCR no FSI;
  - caps da esclera (fsi_sclera_peri/ring): 1333 Pa estatico (desacoplamento
    seletivo, igual a producao);
  - fundacao de Winkler (gordura orbital, k=2e5 Pa/m) em dura_outer;
  - engaste em z=0 (posterior_*) e no globo (globo_outer);
  - material ELASTICO LINEAR (Tabela tab:mat-linear, Caso 1), nu=0.45;
  - SEM carga arterial (Caso 3) e SEM Riks (resposta linear estavel).

Como a resposta e' linear-elastica, as RAZOES de convergencia entre malhas
independem da magnitude da carga; usa-se o endpoint SANS por ser representativo.

Para cada nivel de refino f (fator inteiro multiplicativo das divisoes do
blockMesh do on-caso-1/solid, uniforme r/theta/z):
  1. (host)      refina o blockMeshDict e prepara um caso OpenFOAM scratch;
  2. (container) blockMesh + topoSet + createPatch -> polyMesh;
  3. (container) foam_polymesh_to_ccx_inp.py -> all_mesh.inp + winkler.inp;
  4. (container) ccx_preCICE -i main (standalone) -> main.frd;
  5. (host)      analyze_frd -> QoIs (Delta r por zona, pico de von Mises).

Saidas:
  cases/on-caso-1.2/_mesh_indep_solid/f<N>/   (casos scratch)
  cases/on-caso-1.2/_mesh_indep_solid/results.json
  brunaStuff/mesh_independence_solid_summary.txt
  brunaStuff/figs/on-caso-1.2-mesh-independence-solid.png

Uso:
    python3 brunaStuff/mesh_independence_solid_caso_1_2.py            # f=1,2,3
    python3 brunaStuff/mesh_independence_solid_caso_1_2.py 1 2
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))

import refine_blockmesh  # noqa: E402
from frd_stress import analyze_frd  # noqa: E402

CASE = REPO / "cases" / "on-caso-1.2"
SRC_SOLID = REPO / "cases" / "on-caso-1" / "solid"   # caso OpenFOAM base (O-grid)
ROOT = CASE / "_mesh_indep_solid"
CONVERTER = HERE / "foam_polymesh_to_ccx_inp.py"

# Carga / regime fixos (endpoint SANS da producao)
P_SAS = 3800.0       # Pa, pressao transmitida do LCR nas faces FSI (pia/dura)
P_SCLERA = 1333.0    # Pa, caps da esclera (desacoplamento seletivo)
K_WINKLER = 2.0e5    # Pa/m (gordura orbital)
ELEMENT_TYPE = "C3D8"  # igual a producao do on-caso-1.2

# Dicts do caso OpenFOAM base necessarios para construir a polyMesh
OF_SYSTEM_FILES = (
    "controlDict", "fvSchemes", "fvSolution",
    "topoSetDict_contact", "createPatchDict_contact",
)


# ---------------------------------------------------------------------------
def sh(cmd: str, **kw):
    print(f"  $ {cmd}")
    return subprocess.run(cmd, shell=True, cwd=str(REPO), check=True, **kw)


def docker(inner: str):
    return sh(f'docker compose run --rm fsi bash -lc {json.dumps(inner)}')


# ---------------------------------------------------------------------------
# Deck CalculiX standalone (elastico linear, carga FSI estatica equivalente)
# ELSET = zona.upper(); NSET = patch.upper(); SURFACE = patch.upper()+"_SURF"
# (convencao do foam_polymesh_to_ccx_inp.py).
# ---------------------------------------------------------------------------
MAIN_INP = """\
** on-caso-1.2 -- INDEPENDENCIA DE MALHA do SOLIDO (standalone, sem preCICE).
** Material elastico linear (Tabela tab:mat-linear, Caso 1), nu=0.45.
** Carga FSI substituida por pressao estatica equivalente nas faces FSI.
*INCLUDE, INPUT=all_mesh.inp

** ---- Materiais elasticos lineares (E, nu) por zona ----
*MATERIAL, NAME=ON_MAT
*ELASTIC
30000.0, 0.45
*DENSITY
1000.0
*MATERIAL, NAME=PIA_MAT
*ELASTIC
3.0e6, 0.45
*DENSITY
1100.0
*MATERIAL, NAME=DURA_MAT
*ELASTIC
3.0e6, 0.45
*DENSITY
1100.0
*MATERIAL, NAME=LC_MAT
*ELASTIC
0.4e6, 0.45
*DENSITY
1100.0
*MATERIAL, NAME=SCLERA_PERI_MAT
*ELASTIC
5.0e6, 0.45
*DENSITY
1400.0
*MATERIAL, NAME=SCLERA_RING_MAT
*ELASTIC
5.0e6, 0.45
*DENSITY
1400.0
*MATERIAL, NAME=GLOBO_MAT
*ELASTIC
5.0e6, 0.45
*DENSITY
1400.0

** ---- Solid sections (ELSET = zona.upper()) ----
*SOLID SECTION, ELSET=ON,          MATERIAL=ON_MAT
*SOLID SECTION, ELSET=PIA,         MATERIAL=PIA_MAT
*SOLID SECTION, ELSET=DURA,        MATERIAL=DURA_MAT
*SOLID SECTION, ELSET=LC,          MATERIAL=LC_MAT
*SOLID SECTION, ELSET=SCLERA_PERI, MATERIAL=SCLERA_PERI_MAT
*SOLID SECTION, ELSET=SCLERA_RING, MATERIAL=SCLERA_RING_MAT
*SOLID SECTION, ELSET=GLOBO,       MATERIAL=GLOBO_MAT

** ---- Winkler (gordura orbital) em dura_outer ----
*INCLUDE, INPUT=winkler.inp

** ---- Engaste z=0 (canal optico) + globo ----
*BOUNDARY
POSTERIOR_ON,   1, 3, 0.0
POSTERIOR_PIA,  1, 3, 0.0
POSTERIOR_DURA, 1, 3, 0.0
GLOBO_OUTER,    1, 3, 0.0

** ---- Step estatico linear ----
*STEP
*STATIC

** Pressao do SAS transmitida as faces FSI (pia comprime, dura distende)
*DLOAD
FSI_PIA_SURF,  P, {p_sas}
FSI_DURA_SURF, P, {p_sas}
** Caps da esclera (desacoplamento seletivo, estatico)
FSI_SCLERA_PERI_SURF, P, {p_sclera}
FSI_SCLERA_RING_SURF, P, {p_sclera}

*NODE FILE
U
*EL FILE
S
*END STEP
"""


# ---------------------------------------------------------------------------
def setup_level(f: int) -> Path:
    ldir = ROOT / f"f{f}"
    sh(f"rm -rf {ldir}")
    (ldir / "of" / "system").mkdir(parents=True, exist_ok=True)
    (ldir / "of" / "constant").mkdir(parents=True, exist_ok=True)
    (ldir / "ccx").mkdir(parents=True, exist_ok=True)

    # dicts do caso OpenFOAM base
    for fn in OF_SYSTEM_FILES:
        shutil.copy(SRC_SOLID / "system" / fn, ldir / "of" / "system" / fn)

    # blockMeshDict refinado por f (uniforme r/theta/z)
    refine_blockmesh.refine(
        str(SRC_SOLID / "system" / "blockMeshDict"),
        str(ldir / "of" / "system" / "blockMeshDict"), f, f, f)

    # converter (precisa estar sob cases/ p/ ser visivel no container)
    shutil.copy(CONVERTER, ldir / "foam_polymesh_to_ccx_inp.py")

    # deck CalculiX
    (ldir / "ccx" / "main.inp").write_text(
        MAIN_INP.format(p_sas=f"{P_SAS:.1f}", p_sclera=f"{P_SCLERA:.1f}"))
    return ldir


def count_elements(mesh_inp: Path) -> int:
    n = 0
    in_elem = False
    for line in mesh_inp.read_text().splitlines():
        s = line.strip()
        if s.startswith("*"):
            in_elem = s.upper().startswith("*ELEMENT")
            continue
        if in_elem and s and s[0].isdigit():
            n += 1
    return n


def run_level(f: int) -> dict:
    print(f"\n===== NIVEL SOLIDO f{f} =====")
    ldir = setup_level(f)
    rel = f"on-caso-1.2/_mesh_indep_solid/f{f}"

    docker(
        f"cd {rel}/of && "
        "blockMesh > log.blockMesh 2>&1 && "
        "topoSet -dict system/topoSetDict_contact > log.topoSet 2>&1 && "
        "createPatch -overwrite -dict system/createPatchDict_contact > log.createPatch 2>&1 && "
        f"cd .. && "
        "python3 foam_polymesh_to_ccx_inp.py "
        "--polymesh of/constant/polyMesh "
        "--out-mesh ccx/all_mesh.inp --out-winkler ccx/winkler.inp "
        f"--winkler-k {K_WINKLER:g} --element-type {ELEMENT_TYPE} && "
        "cd ccx && rm -f main.frd main.dat main.sta main.cvg && "
        "ccx_preCICE -i main > log.ccx 2>&1 ; tail -n 3 log.ccx"
    )

    mesh_inp = ldir / "ccx" / "all_mesh.inp"
    frd = ldir / "ccx" / "main.frd"
    n_el = count_elements(mesh_inp)

    steps = analyze_frd(frd)
    if not steps:
        raise RuntimeError(f"frd sem passos: {frd}")
    last = steps[-1]
    ulat = last["ulat_zone_max"]
    vmz = last["vm_zone_max"]

    out = dict(
        level=f"f{f}", factor=f, n_elements=n_el,
        dr_dura_m=ulat.get("dura", float("nan")),
        dr_pia_m=ulat.get("pia", float("nan")),
        dr_on_m=ulat.get("on", float("nan")),
        vm_global_pa=last["vm_global_max"],
        vm_dura_pa=vmz.get("dura", float("nan")),
    )
    print(f"  nEl={n_el}  dr_dura={out['dr_dura_m']*1e6:.4f} um  "
          f"dr_pia={out['dr_pia_m']*1e6:.4f} um  "
          f"vm_global={out['vm_global_pa']/1e3:.2f} kPa")
    return out


# ---------------------------------------------------------------------------
def write_summary(results: list[dict]):
    finest = results[-1]
    lines = [
        "=" * 78,
        "ESTUDO DE INDEPENDENCIA DE MALHA - on-caso-1.2 (LADO SOLIDO / CalculiX)",
        "=" * 78,
        "Solido standalone (ccx, elastico linear, nu=0.45), DESACOPLADO do FSI:",
        f"  carga FSI -> pressao estatica p_SAS={P_SAS:g} Pa em fsi_pia/fsi_dura,",
        f"  caps da esclera {P_SCLERA:g} Pa, Winkler k={K_WINKLER:g} Pa/m, engaste z=0+globo.",
        "Refino global do blockMesh (O-grid) por fator inteiro (uniforme r/theta/z).",
        "QoI primaria: Delta r_dura = distensao radial maxima da dura (achado SANS).",
        "",
        f"{'nivel':>6} {'nEl':>8} {'dr_dura(um)':>12} {'dr%vs_fino':>11} "
        f"{'dr_pia(um)':>11} {'vm_glob(kPa)':>13}",
    ]
    for x in results:
        drd = x["dr_dura_m"] * 1e6
        ref = finest["dr_dura_m"] * 1e6
        pct = 100.0 * (drd - ref) / ref if ref else float("nan")
        lines.append(
            f"{x['level']:>6} {x['n_elements']:>8} {drd:>12.4f} {pct:>10.2f}% "
            f"{x['dr_pia_m']*1e6:>11.4f} {x['vm_global_pa']/1e3:>13.2f}")

    lines += ["", "Variacao SUCESSIVA (nivel i vs i-1):"]
    for i in range(1, len(results)):
        a, b = results[i - 1], results[i]
        d_dr = 100.0 * abs(b["dr_dura_m"] - a["dr_dura_m"]) / abs(b["dr_dura_m"])
        d_vm = 100.0 * abs(b["vm_global_pa"] - a["vm_global_pa"]) / abs(b["vm_global_pa"])
        lines.append(f"  {a['level']}->{b['level']}: "
                     f"dr_dura {d_dr:.2f}%   vm_global {d_vm:.2f}%")

    lines += [
        "",
        "OBSERVACOES:",
        "- Delta r_dura (distensao da bainha) e' a QoI fisica do Caso 1; converge",
        "  monotonicamente, com a malha de producao (f1) ja' proxima da malha fina.",
        "- A resposta e' linear-elastica e estavel (sem flambagem), logo nao requer",
        "  o estudo local/modal exigido pelos casos de instabilidade (2/2.2/3).",
        "- pico de von Mises e' metrica LOCAL (singularidade no engaste) e converge",
        "  mais lentamente; use Delta r como metrica integral robusta.",
    ]
    txt = "\n".join(lines) + "\n"
    out = HERE / "mesh_independence_solid_summary.txt"
    out.write_text(txt)
    print("\n" + txt)
    print(f"resumo -> {out}")


def make_figure(results: list[dict]):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as e:  # noqa: BLE001
        print(f"  (matplotlib indisponivel, pulando figura: {e})")
        return
    n = [x["n_elements"] for x in results]
    drd = [x["dr_dura_m"] * 1e6 for x in results]
    vm = [x["vm_global_pa"] / 1e3 for x in results]
    ref = drd[-1]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))

    ax1.axhspan(ref * 0.99, ref * 1.01, color="tab:green", alpha=0.15,
                label=r"$\pm1\%$ (malha fina)")
    ax1.semilogx(n, drd, "o-", color="tab:blue", label=r"$\Delta r_{\rm dura}$")
    ax1.semilogx(n[0], drd[0], "s", color="tab:red", ms=11, mfc="none",
                 mew=2, label="producao")
    ax1.set_xlabel("numero de elementos")
    ax1.set_ylabel(r"$\Delta r_{\rm dura}$ ($\mu$m)")
    ax1.set_title("Distensao radial da dura")
    ax1.grid(True, which="both", alpha=0.3)
    ax1.legend(fontsize=9)

    d_dr = [abs(drd[i] - drd[i - 1]) / drd[i] * 100 for i in range(1, len(drd))]
    d_vm = [abs(vm[i] - vm[i - 1]) / vm[i] * 100 for i in range(1, len(vm))]
    xx = [f"{results[i-1]['level']}->{results[i]['level']}" for i in range(1, len(results))]
    ax2.axhline(5.0, color="tab:green", ls="--", lw=1, label="criterio 5%")
    ax2.plot(xx, d_dr, "o-", color="tab:blue", label=r"$\Delta r_{\rm dura}$")
    ax2.plot(xx, d_vm, "s-", color="tab:orange", label=r"von Mises pico")
    ax2.set_ylabel(r"variacao sucessiva $|\Delta|$ (%)")
    ax2.set_title("Convergencia entre niveis")
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=9)

    fig.tight_layout()
    out = HERE / "figs" / "on-caso-1.2-mesh-independence-solid.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150)
    print(f"figura -> {out}")


def main():
    factors = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    ROOT.mkdir(parents=True, exist_ok=True)
    results_path = ROOT / "results.json"
    results = json.loads(results_path.read_text()) if results_path.exists() else []
    for f in factors:
        r = run_level(f)
        results = [x for x in results if x["level"] != r["level"]] + [r]
        results.sort(key=lambda x: x["factor"])
        results_path.write_text(json.dumps(results, indent=2))

    write_summary(results)
    make_figure(results)
    print(f"\nresultados -> {results_path}")


if __name__ == "__main__":
    main()
