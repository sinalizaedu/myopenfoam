#!/usr/bin/env python3
"""
analyze_on-caso-2_ccx.py
========================
Analise do on-caso-2 v2 (CalculiX NLGEOM + Riks) - flambagem axial anatomica
do complexo nervo optico + bainhas + globo (7 zonas).

Le cases/on-caso-2/ccx/on-caso-2.dat:
  - *NODE PRINT TOTALS=ONLY RF para POSTERIOR_{DURA,PIA,ON} -> reacao no
    engaste (canal optico, z=0)
  - *NODE PRINT TOTALS=ONLY RF para ANTERIOR_GLOBO -> reacao na "tampa"
  - *NODE PRINT U para ANTERIOR_GLOBO -> deslocamento real Dz_z (varia
    com lambda do Riks)

Saidas:
  brunaStuff/on-caso-2_ccx_F_vs_dz.png
  brunaStuff/on-caso-2_ccx_summary.txt
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parent.parent
DAT_PATH = REPO / "cases" / "on-caso-2" / "ccx" / "on-caso-2.dat"
OUT_DIR = REPO / "brunaStuff"
PNG = OUT_DIR / "on-caso-2_ccx_F_vs_dz.png"
SUMMARY = OUT_DIR / "on-caso-2_ccx_summary.txt"

# Zonas anatomicas, por completude. As 3 posteriores compoem o engaste (z=0):
NSETS_RF_TOTAL = ["POSTERIOR_DURA", "POSTERIOR_PIA", "POSTERIOR_ON",
                  "ANTERIOR_GLOBO"]

# Parametros geometricos (= on-caso-2.inp)
L = 0.030            # m, comprimento do nervo (z=0 ao apice da LC)
DZ_REF = -1.5e-3     # m, rampa imposta de referencia (Riks escala via lambda); -Z = globo encosta no apice (V10/V12 SANS)
E_DURA = 3e6
R_INNER_DURA = 2.35e-3
R_OUTER_DURA = 2.50e-3


# --------------------------------------------------------------------------
# Parsing do .dat (CalculiX 2.20)
# --------------------------------------------------------------------------

def parse_ccx_dat(path: Path):
    """Retorna dois dicts:

      totals[nset] = list[(time, fx, fy, fz)]
      disp_z[nset]   = list[(time, vz_avg)]   # z-disp medio dos nos do nset

    Formato CCX:
      total force (fx,fy,fz) for set NAME and time T
        FX FY FZ

      displacements (vx,vy,vz) for set NAME and time T
        node1 vx vy vz
        node2 vx vy vz
        ...
    """
    totals: dict[str, list] = {n: [] for n in NSETS_RF_TOTAL}
    disp_z: dict[str, list] = {"ANTERIOR_GLOBO": [], "POSTERIOR_PIA": [],
                               "POSTERIOR_DURA": [], "POSTERIOR_ON": []}

    text = path.read_text()

    # 1) blocos "total force ... for set NAME and time T\n  FX FY FZ"
    pat_force = re.compile(
        r"total\s+force.*?for\s+set\s+(\w+)\s+and\s+time\s+([\-+\d\.E]+)"
        r"\s+([\-+\d\.E]+)\s+([\-+\d\.E]+)\s+([\-+\d\.E]+)",
        re.IGNORECASE | re.DOTALL,
    )
    for m in pat_force.finditer(text):
        nset, t, fx, fy, fz = m.groups()
        if nset.upper() in totals:
            totals[nset.upper()].append(
                (float(t), float(fx), float(fy), float(fz))
            )

    # 2) blocos "displacements ... for set NAME and time T" + N linhas "node vx vy vz"
    pat_disp_block = re.compile(
        r"displacements.*?for\s+set\s+(\w+)\s+and\s+time\s+([\-+\d\.E]+)\n([^*]*?)(?=\n\s*\n|\Z)",
        re.IGNORECASE | re.DOTALL,
    )
    for m in pat_disp_block.finditer(text):
        nset, t, body = m.groups()
        if nset.upper() not in disp_z:
            continue
        vzs = []
        for line in body.splitlines():
            parts = line.split()
            if len(parts) >= 4:
                try:
                    vzs.append(float(parts[3]))
                except ValueError:
                    pass
        if vzs:
            disp_z[nset.upper()].append((float(t), float(np.mean(vzs))))

    return totals, disp_z


# --------------------------------------------------------------------------

def measure_lateral_kink(ccx_dir):
    """Le os .vtu gerados por ccx2paraview e retorna (timesteps_idx, |Ux|max em metros).

    Usa o python do venv /tmp/ccx2pv que tem vtk instalado, via subprocess.
    Se vtk nao estiver disponivel, retorna arrays vazios (skip o painel C).
    """
    import subprocess
    py = "/tmp/ccx2pv/bin/python3"
    if not Path(py).exists():
        return np.array([]), np.array([])
    code = '''
import sys, vtk
import numpy as np
from pathlib import Path
from vtk.util.numpy_support import vtk_to_numpy
cdir = Path(sys.argv[1])
vtus = sorted(cdir.glob("on-caso-2.*.vtu"), key=lambda p: int(p.stem.split(".")[-1]))
out = []
for f in vtus:
    rdr = vtk.vtkXMLUnstructuredGridReader(); rdr.SetFileName(str(f)); rdr.Update()
    g = rdr.GetOutput()
    U = vtk_to_numpy(g.GetPointData().GetArray("U"))
    Ulat = np.sqrt(U[:,0]**2 + U[:,1]**2)
    out.append((int(f.stem.split(".")[-1]), Ulat.max(), abs(U[:,0]).max(), abs(U[:,1]).max()))
for inc, ulat, ux, uy in out:
    print(f"{inc} {ulat} {ux} {uy}")
'''
    try:
        r = subprocess.run([py, "-c", code, str(ccx_dir)], capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            return np.array([]), np.array([])
        rows = [line.split() for line in r.stdout.strip().splitlines() if line.strip()]
        idx = np.array([int(row[0]) for row in rows])
        ulat = np.array([float(row[1]) for row in rows])
        return idx, ulat
    except Exception:
        return np.array([]), np.array([])


# --------------------------------------------------------------------------

def main():
    if not DAT_PATH.exists():
        raise SystemExit(
            f"Nao encontrei {DAT_PATH}. Rode primeiro:\n"
            f"  docker compose run --rm fsi bash -lc "
            f"'cd /simulation/on-caso-2/ccx && ./Allrun'"
        )

    totals, disp_z = parse_ccx_dat(DAT_PATH)
    nblocks = {n: len(v) for n, v in totals.items()}
    print(f"Blocos RF totals encontrados: {nblocks}")
    print(f"Blocos U medio ANTERIOR_GLOBO: {len(disp_z['ANTERIOR_GLOBO'])}")
    print(f"Blocos U medio POSTERIOR_PIA : {len(disp_z['POSTERIOR_PIA'])}")

    # --- Constroi arrays alinhados por timestamp -----------------------------
    # Detecta automaticamente qual extremidade tem o Dz prescrito (ramping).
    # Em on-caso-2 com BC invertida (SANS), POSTERIOR e que recebe Dz=+1.5mm
    # e ANTERIOR_GLOBO esta engastado.
    dz_globo_max = max((abs(v) for _, v in disp_z["ANTERIOR_GLOBO"]), default=0)
    dz_post_max  = max((abs(v) for _, v in disp_z["POSTERIOR_PIA"]),  default=0)
    if dz_post_max > dz_globo_max:
        # BC invertida: empurrao posterior (modo SANS-fisiologico)
        loaded_set = "POSTERIOR_PIA"
        Dz_label   = "Dz_post (canal optico empurrado)"
    else:
        loaded_set = "ANTERIOR_GLOBO"
        Dz_label   = "Dz_globo"
    print(f"Lado carregado axialmente: {loaded_set}  (max |U_z|={max(dz_globo_max, dz_post_max)*1e3:.3f} mm)")

    times = np.array([t for t, _ in disp_z[loaded_set]])
    Dz_globo = np.array([vz for _, vz in disp_z[loaded_set]])
    if times.size == 0:
        raise SystemExit("Nenhum timestamp lido do .dat - run nao gerou dados.")

    def fz_for(nset: str) -> np.ndarray:
        d = dict([(t, fz) for t, _, _, fz in totals[nset]])
        return np.array([d.get(float(f"{t:.7g}"), d.get(t, np.nan)) for t in times])

    Fz_dura_post  = fz_for("POSTERIOR_DURA")
    Fz_pia_post   = fz_for("POSTERIOR_PIA")
    Fz_on_post    = fz_for("POSTERIOR_ON")
    Fz_anterior   = fz_for("ANTERIOR_GLOBO")

    # Reacao TOTAL no engaste posterior (canal optico, z=0):
    #   F_eng = sum(F_z postero), positiva = empurra de volta o nervo p/ +z
    F_eng_total = Fz_dura_post + Fz_pia_post + Fz_on_post

    # Verificacao de equilibrio: |F_eng| ~ |F_anterior| (devera empatar exceto
    # pela contribuicao das molas Winkler + perturbacao lateral)
    imbalance = np.abs(F_eng_total + Fz_anterior)  # soma deve ser ~0 em equilibrio

    # Pico GLOBAL de |F_eng| (engaste total) - geralmente sera o ultimo ponto
    # se F_eng for monotonico crescente
    idx_peak = int(np.argmax(np.abs(F_eng_total)))
    Dz_cr = Dz_globo[idx_peak]
    P_cr_sim = abs(F_eng_total[idx_peak])
    flambou = idx_peak < len(F_eng_total) - 1

    # ESSENCIAL: detectar flambagem POR CAMADA. A dura pode flambar localmente
    # antes que F_eng_total desabe; basta a sua contribuicao individual cair.
    # Pico de cada camada da uma estimativa do P_cr_LOCAL daquela camada.
    layers = {
        "dura": Fz_dura_post,
        "pia":  Fz_pia_post,
        "on":   Fz_on_post,
    }
    peaks = {}
    for name, F in layers.items():
        i = int(np.argmax(np.abs(F)))
        peaks[name] = {
            "idx": i,
            "Dz_mm": Dz_globo[i] * 1e3,
            "F_mN": abs(F[i]) * 1e3,
            "buckled": (i < len(F) - 1) and (abs(F[-1]) < 0.85 * abs(F[i])),
        }

    # Rigidez axial pre-flambagem: ajuste linear nos primeiros pontos com
    # |Dz| <= 0.2 mm (regime quase-linear)
    pre_mask = np.abs(Dz_globo) <= 0.2e-3
    if pre_mask.sum() >= 2:
        slope = np.polyfit(Dz_globo[pre_mask], F_eng_total[pre_mask], 1)[0]
        k_axial = abs(slope)
    elif len(Dz_globo) >= 2:
        slope = np.polyfit(Dz_globo[:2], F_eng_total[:2], 1)[0]
        k_axial = abs(slope)
    else:
        k_axial = float("nan")

    # Estimativa Euler (so dura_outer, comparacao academica)
    I_dura = math.pi / 4 * (R_OUTER_DURA ** 4 - R_INNER_DURA ** 4)
    EI_dura = E_DURA * I_dura
    P_cr_euler = {
        K: math.pi ** 2 * EI_dura / (K * L) ** 2
        for K in (0.5, 0.7, 1.0)
    }

    # K_efetivo da simulacao (back-out)
    K_ef = math.sqrt(EI_dura * math.pi ** 2 / (L ** 2 * P_cr_sim)) if P_cr_sim > 0 else float("nan")

    # ---------- mede kink lateral via .vtu (se disponivel) ----------
    kink_idx, kink_ulat = measure_lateral_kink(DAT_PATH.parent)
    if len(kink_ulat) > 0:
        # alinhar com timestamps Riks: vtus sao numerados 1..N na ordem dos saves;
        # se N == len(times), assume mapping direto
        if len(kink_ulat) >= len(times):
            kink_to_use = kink_ulat[: len(times)]
        else:
            kink_to_use = np.full(len(times), np.nan)
            kink_to_use[: len(kink_ulat)] = kink_ulat
        kink_max_mm = float(np.nanmax(kink_to_use)) * 1e3
    else:
        kink_to_use = None
        kink_max_mm = float("nan")

    # ---------- imprime e salva sumario ----------
    lines = []
    p = lines.append
    p("=" * 72)
    p("on-caso-2 v2 (CCX 2.20 NLGEOM + Riks) - flambagem axial anatomica")
    p("Geometria: 7 zonas (on, pia, dura, lc, sclera_peri, sclera_ring, globo)")
    p("Material : NEO HOOKE compressivel, nu=0.49 (E_rigido=3MPa, E_LC=300kPa, E_nervo=30kPa)")
    p("=" * 72)
    if not np.isnan(kink_max_mm):
        p(f"\n--- Kink lateral (deslocamento radial max) ---")
        p(f"  max |U_lat| = {kink_max_mm:.2f} mm")
        if kink_max_mm > 1.5:
            p(f"  >>> KINK LATERAL VISIVEL (>1.5 mm = >1/2 raio do nervo).")
            p(f"      Estrutura flambou em modo flexural.")
    p(f"\nTimestamps lidos do Riks: {len(times)}")
    p(f"Range Dz no globo: {Dz_globo.min()*1e3:+.3f} a {Dz_globo.max()*1e3:+.3f} mm")
    p(f"Lambda (load factor) range: {times.min():.3f} a {times.max():.3f}")
    p(f"\n--- Reacao no engaste posterior (z=0, canal optico) ---")
    p(f"  F_eng_max  = {abs(F_eng_total).max()*1e3:8.2f} mN @ Dz_globo = {Dz_globo[idx_peak]*1e3:+.3f} mm")
    p(f"  Decomposicao no pico (% de F_eng):")
    pct = lambda x: f"{x/F_eng_total[idx_peak]*100:6.1f}%"
    p(f"     dura : {Fz_dura_post[idx_peak]*1e3:+8.3f} mN  ({pct(Fz_dura_post[idx_peak])})")
    p(f"     pia  : {Fz_pia_post[idx_peak]*1e3:+8.3f} mN  ({pct(Fz_pia_post[idx_peak])})")
    p(f"     on   : {Fz_on_post[idx_peak]*1e3:+8.3f} mN  ({pct(Fz_on_post[idx_peak])})")

    p(f"\n--- Equilibrio axial (sanity check) ---")
    p(f"  F_anterior_globo = {Fz_anterior[idx_peak]*1e3:+8.3f} mN")
    p(f"  F_eng_posterior  = {F_eng_total[idx_peak]*1e3:+8.3f} mN")
    p(f"  |imbalance| max  = {imbalance.max()*1e3:.3f} mN  (springs Winkler + perturbacao)")

    p(f"\n--- Rigidez axial pre-flambagem (regime |Dz| <= 0.2 mm) ---")
    p(f"  k_axial = {k_axial:.2f} N/m")

    if flambou:
        p(f"\n--- PONTO CRITICO P_cr (queda de F_eng apos pico) ---")
        p(f"  Dz_cr     = {Dz_cr*1e3:+.3f} mm")
        p(f"  P_cr_CCX  = {P_cr_sim*1e3:.2f} mN")
    else:
        p(f"\n--- F_eng_total monotonico (pico = ultimo ponto) ---")
        p(f"  max |F_eng| = {P_cr_sim*1e3:.2f} mN @ Dz_globo = {Dz_cr*1e3:+.3f} mm")
        p(f"  K_ef estimado = {K_ef:.3f} (back-out de Euler dura sozinha)")

    # Por camada: detecta flambagem LOCAL (carga transferida para o nervo)
    p(f"\n--- Pico de cada camada (P_cr_local) ---")
    for name, info in peaks.items():
        flag = "*** FLAMBOU (queda >15%) ***" if info["buckled"] else ""
        p(f"  {name:5s}: F_max = {info['F_mN']:7.2f} mN @ Dz = {info['Dz_mm']:+6.2f} mm  {flag}")
    if peaks["dura"]["buckled"]:
        p(f"\n  >>> DURA FLAMBOU PRIMEIRO em Dz = {peaks['dura']['Dz_mm']:+.2f} mm.")
        p(f"      P_cr_dura = {peaks['dura']['F_mN']:.2f} mN.")
        p(f"      Ao flambar, redirecionou carga para o nervo: F_on saltou de")
        p(f"      {abs(layers['on'][peaks['dura']['idx']])*1e3:.1f} mN p/ {abs(layers['on'][-1])*1e3:.1f} mN.")
        p(f"      ESTE E O MECANISMO SANS: dura-mater hiper-rigida flamba,")
        p(f"      transfere a carga axial para o miolo neural macio que e")
        p(f"      esmagado lateralmente (kinking induzindo isquemia).")

    p(f"\n--- Comparacao com Euler analitico (so dura_outer, EI={EI_dura:.3e} Nm^2) ---")
    for K, Pcr in P_cr_euler.items():
        ratio = P_cr_sim / Pcr if Pcr > 0 else float("nan")
        p(f"  K={K}: P_cr_Euler = {Pcr*1e3:7.2f} mN   (CCX/Euler = {ratio:.2f})")

    text = "\n".join(lines) + "\n"
    print(text)
    SUMMARY.write_text(text)
    print(f"Sumario salvo em {SUMMARY}")

    # ---------- plot ----------
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Painel A: F_eng_total e suas componentes
    ax = axes[0]
    Dz_mm = Dz_globo * 1e3
    ax.plot(Dz_mm, np.abs(F_eng_total) * 1e3, "ko-", lw=2, ms=5,
            label="|F_eng| total (engaste z=0)")
    ax.plot(Dz_mm, np.abs(Fz_dura_post) * 1e3, "r-",  lw=1.5, alpha=0.9,
            label="|F_z| dura (posterior)")
    ax.plot(Dz_mm, np.abs(Fz_pia_post) * 1e3, "g-",  lw=1.5, alpha=0.9,
            label="|F_z| pia (posterior)")
    ax.plot(Dz_mm, np.abs(Fz_on_post) * 1e3, "m-",  lw=1.5, alpha=0.9,
            label="|F_z| on (posterior)")
    # Painel B compara: |F_anterior_globo| (deve mais ou menos casar com |F_eng|)
    ax.plot(Dz_mm, np.abs(Fz_anterior) * 1e3, "b--", lw=1, alpha=0.6,
            label="|F_z| globo (anterior)")
    # Marca pico GLOBAL
    label_pico = (f"P_cr global = {P_cr_sim*1e3:.1f} mN @ Dz={Dz_cr*1e3:.2f} mm"
                  if flambou
                  else f"max |F_eng| = {P_cr_sim*1e3:.1f} mN")
    ax.plot([Dz_cr * 1e3], [P_cr_sim * 1e3], "k*", ms=18, zorder=5,
            label=label_pico)
    # Marca pico de cada camada
    color_layer = {"dura": "r", "pia": "g", "on": "m"}
    for name, info in peaks.items():
        marker_label = (f"P_cr_{name} = {info['F_mN']:.1f} mN @ Dz={info['Dz_mm']:.2f} mm"
                        if info["buckled"] else None)
        ax.plot([info["Dz_mm"]], [info["F_mN"]], color_layer[name] + "*",
                ms=14, zorder=5, label=marker_label)
    # Linhas Euler
    for K, Pcr in P_cr_euler.items():
        ax.axhline(Pcr * 1e3, ls="--", color="grey", alpha=0.4, lw=0.7)
        x_text = Dz_mm.min() * 0.95 if Dz_mm.min() < 0 else Dz_mm.min() * 1.05
        ax.text(x_text, Pcr * 1e3 * 1.02, f"Euler K={K}", fontsize=7, color="grey")
    ax.set_xlabel(r"$\Delta z$ globo (mm)")
    ax.set_ylabel(r"$|F_z|$ (mN)")
    ax.set_title("Curva F-d (Riks) - reacao engaste z=0 + decomposicao por camada")
    ax.legend(loc="upper left", fontsize=7)
    ax.grid(alpha=0.3)
    ax.invert_xaxis()  # Dz negativo cresce p/ direita

    # Painel B: lambda (load factor) vs incremento + kink lateral vs Dz
    ax = axes[1]
    Dz_mm = Dz_globo * 1e3
    if kink_to_use is not None and not np.all(np.isnan(kink_to_use)):
        ax.plot(Dz_mm, kink_to_use * 1e3, "ro-", lw=2, ms=6, label="|U_lat| max (kink)")
        ax.axhline(2.5, ls="--", color="k", alpha=0.4, lw=0.8)
        ax.text(Dz_mm.min() * 0.95 if Dz_mm.min() < 0 else Dz_mm.min() * 1.05,
                2.6, "raio externo da dura (2.5 mm)", fontsize=7, color="k", alpha=0.6)
        ax.set_xlabel(r"$\Delta z$ globo (mm)")
        ax.set_ylabel(r"$|U_{lat}|$ max (mm)")
        ax.set_title(f"Kink lateral (max ${{U_{{lat}}}}$ = $\\sqrt{{U_x^2+U_y^2}}$) - max = {kink_max_mm:.2f} mm")
        ax.invert_xaxis()
        ax.legend(loc="upper left", fontsize=8)
    else:
        # Fallback antigo: lambda vs incremento
        inc_idx = np.arange(1, len(times) + 1)
        ax2 = ax.twinx()
        ax.plot(inc_idx, times, "b-o", lw=1.5, ms=4, label="lambda (load factor)")
        ax2.plot(inc_idx, Dz_mm, "r-s", lw=1.5, ms=4, label="Dz globo (mm)")
        ax.set_xlabel("Incremento Riks")
        ax.set_ylabel("lambda", color="b")
        ax2.set_ylabel("Dz globo (mm)", color="r")
        ax.tick_params(axis="y", labelcolor="b")
        ax2.tick_params(axis="y", labelcolor="r")
        ax.set_title("Riks arc-length: lambda e Dz vs incremento")
    ax.grid(alpha=0.3)

    fig.suptitle("on-caso-2 v2 CCX NLGEOM Riks - 7 zonas anatomicas, NeoHooke nu=0.49\n"
                 "(MAT_RIGIDO=3MPa para pia/dura/sclera/globo, MAT_LC=300kPa, MAT_NERVO=30kPa)",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(PNG, dpi=130)
    print(f"Plot salvo em {PNG}")


if __name__ == "__main__":
    main()
