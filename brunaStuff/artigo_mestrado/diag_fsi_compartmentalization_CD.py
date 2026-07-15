"""TESTES C e D da bateria 'compartimentalizacao FSI':

C) Sweep de contact_local: 0/9034/18068 Pa em FSI fechado
   - Pc=0 foi excluido (solver IQN-ILS diverge sem carga assimetrica
     suficiente para ancorar a aceleracao; achado metodologico relatado
     em comentario)
   - testa LINEARIDADE da resposta direcional do nervo sob carga arterial:
     se delta_perp_perp escala 1:1 com Pc => resposta linear elastica
     'transmitida' (sem amortecimento); se delta_perp ~ constante
     independente de Pc => compartimentalizacao TOTAL.

D) Cul-de-sac aberto: fsi_sclera_peri vira outlet (p=p_inlet)
   - testa se o cul-de-sac fechado e' o agente da compartimentalizacao
   - esperado: delta_perp_openSAS > delta_perp_fsi-2 (compartimento aberto
     deixa a carga propagar lateralmente sem retorno pascal isotropico).

Pos-processamento:
   - le solid/1/D (campo deslocamento)
   - le solid/0/Cx,Cy,Cz (cell centres -- ja' gerados pelo Teste A ou
     pelo postProcess writeCellCentres)
   - calcula delta_perp(z) = ||<x_cell + D_cell>|| na zona 'on'
     (centroide do nervo deslocado)
   - reporta delta_perp_max = max_z delta_perp(z)

Saidas:
   - sans_outputs/diag_testCD_delta_perp.csv
   - sans_outputs/diag_testCD_delta_perp.png (2 paineis: barra-C e barra-D)
"""

from __future__ import annotations

import math
import subprocess
from pathlib import Path

import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from diag_fsi_compartmentalization_A import (
    parse_scalar_field, parse_vector_field,
)

ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = ROOT / "cases"
OUT_DIR = Path(__file__).resolve().parent / "sans_outputs"
OUT_DIR.mkdir(exist_ok=True)

# Zona 'on' (nervo) na malha FSI: cells 0..7680  (mesma de measure_sans_effects.py)
ON_RANGE = (0, 7680)


def find_running_fsi_container() -> str | None:
    try:
        out = subprocess.check_output(
            ["docker", "ps", "--filter", "ancestor=fsi-openfoam:latest",
             "--format", "{{.Names}}"],
            text=True,
        ).strip()
    except subprocess.CalledProcessError:
        return None
    if not out:
        return None
    return out.split("\n")[0]


def get_solid_cell_centres(case_name: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    cd = CASES_DIR / case_name / "solid"
    cx_path = cd / "0" / "Cx"
    if not cx_path.exists():
        cont = find_running_fsi_container()
        if cont is None:
            raise RuntimeError(f"sem container FSI ativo; nao posso gerar Cx para {case_name}")
        subprocess.check_call(
            ["docker", "exec", cont, "bash", "-lc",
             f"cd /simulation/{case_name}/solid && postProcess -func writeCellCentres -time 0 -case . 2>&1 | tail -2"],
        )
    cx = parse_scalar_field((cd / "0" / "Cx").read_text())
    cy = parse_scalar_field((cd / "0" / "Cy").read_text())
    cz = parse_scalar_field((cd / "0" / "Cz").read_text())
    return cx, cy, cz


def delta_perp_profile(case_name: str, dz_bin_mm: float = 1.0
                        ) -> tuple[np.ndarray, np.ndarray, float, dict]:
    """Devolve (z_bin_mm, delta_perp_um, delta_perp_max_um, extras).

    delta_perp(z) = ||centroid_xy_deformado(z)||   na zona 'on'.
    extras: dict com Dz_avg na face anterior do globo (z proximo ao max),
            sigma_max etc. (so' delta_perp por enquanto).
    """
    cd = CASES_DIR / case_name / "solid"
    D = parse_vector_field((cd / "1" / "D").read_text())
    cx, cy, cz = get_solid_cell_centres(case_name)

    a, b = ON_RANGE
    if D.shape[0] < b:
        raise RuntimeError(f"{case_name}: D tem {D.shape[0]} cells, esperava >={b}")
    if cx.size < b:
        raise RuntimeError(f"{case_name}: Cxyz tem {cx.size} cells, esperava >={b}")

    Dx = D[a:b, 0]; Dy = D[a:b, 1]
    cxz = cx[a:b];  cyz = cy[a:b];  czz = cz[a:b]
    z_mm = czz * 1000.0
    x_def = cxz + Dx
    y_def = cyz + Dy

    z_lo = math.floor(z_mm.min())
    z_hi = math.ceil(z_mm.max())
    bins = np.arange(z_lo, z_hi + dz_bin_mm, dz_bin_mm)
    centers = 0.5 * (bins[:-1] + bins[1:])
    delta = np.full(centers.size, np.nan)
    for i in range(centers.size):
        m = (z_mm >= bins[i]) & (z_mm < bins[i+1])
        if m.any():
            xc = x_def[m].mean()
            yc = y_def[m].mean()
            delta[i] = math.hypot(xc, yc) * 1e6  # mm -> um

    return centers, delta, float(np.nanmax(delta)), {}


def main():
    # Casos a analisar:
    cases_C = [
        ("on-fsi-2",         9034,  "FSI baseline (Pc=9034)"),
        ("on-fsi-2-Pc9034",  9034,  "C: Pc=9034 (replicacao)"),
        ("on-fsi-2-Pc18068", 18068, "C: Pc=18068 (dobro)"),
    ]
    cases_D = [
        ("on-fsi-2",         "FSI baseline (cul-de-sac fechado)"),
        ("on-fsi-2-openSAS", "D: cul-de-sac ABERTO em fsi_sclera_peri"),
    ]

    rows = []
    profiles = {}

    print("="*72 + "\n  Teste C: sweep contact_local\n" + "="*72)
    for name, Pc, label in cases_C:
        case_dir = CASES_DIR / name / "solid" / "1" / "D"
        if not case_dir.exists():
            print(f"  [SKIP] {name}: solid/1/D nao existe (caso nao rodou).")
            continue
        try:
            z, dp, dp_max, _ = delta_perp_profile(name)
        except Exception as exc:
            print(f"  [ERROR] {name}: {exc}")
            continue
        rows.append({"test": "C", "case": name, "Pc": Pc, "label": label,
                     "delta_perp_max_um": dp_max})
        profiles[name] = (z, dp)
        print(f"  {name:<22} Pc={Pc:>6}  delta_perp_max = {dp_max:7.3f} um")

    print("\n" + "="*72 + "\n  Teste D: cul-de-sac aberto vs fechado\n" + "="*72)
    for name, label in cases_D:
        case_dir = CASES_DIR / name / "solid" / "1" / "D"
        if not case_dir.exists():
            print(f"  [SKIP] {name}: solid/1/D nao existe (caso nao rodou).")
            continue
        try:
            z, dp, dp_max, _ = delta_perp_profile(name)
        except Exception as exc:
            print(f"  [ERROR] {name}: {exc}")
            continue
        if name == "on-fsi-2":
            label_extra = ""
        else:
            label_extra = ""
        rows.append({"test": "D", "case": name, "Pc": 9034, "label": label,
                     "delta_perp_max_um": dp_max})
        if name not in profiles:
            profiles[name] = (z, dp)
        print(f"  {name:<22}  delta_perp_max = {dp_max:7.3f} um   ({label})")

    # ----------------- CSV --------------------
    csv_path = OUT_DIR / "diag_testCD_delta_perp.csv"
    with open(csv_path, "w") as f:
        f.write("test,case,Pc_Pa,delta_perp_max_um,label\n")
        for r in rows:
            f.write(f"{r['test']},{r['case']},{r['Pc']},"
                    f"{r['delta_perp_max_um']:.4f},\"{r['label']}\"\n")
    print(f"\n  CSV: {csv_path}")

    # ----------------- FIG --------------------
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

    # painel 1: Teste C - barra delta_perp vs Pc
    ax = axes[0]
    rowsC = [r for r in rows if r["test"] == "C"]
    if rowsC:
        xs = [r["Pc"] for r in rowsC]
        ys = [r["delta_perp_max_um"] for r in rowsC]
        labels = [r["case"].replace("on-fsi-2", "fsi-2") for r in rowsC]
        # ordena por Pc
        order = np.argsort(xs)
        xs = [xs[i] for i in order]; ys = [ys[i] for i in order]
        labels = [labels[i] for i in order]
        bars = ax.bar(range(len(xs)), ys, color=["#2980b9", "#27ae60", "#c0392b"][:len(xs)],
                       edgecolor="black", linewidth=0.5)
        for b, y in zip(bars, ys):
            ax.text(b.get_x()+b.get_width()/2, y, f"{y:.2f}", ha="center", va="bottom",
                    fontsize=9, fontweight="bold")
        # linha de resposta linear esperada (delta_perp ~ Pc/Pc_ref * delta_baseline)
        if len(rowsC) >= 2:
            ref_idx = next((i for i,r in enumerate(rowsC) if r["Pc"] == 9034), 0)
            y_ref = ys[next(i for i,p in enumerate(xs) if p == 9034)] if 9034 in xs else ys[0]
            P_ref = 9034
            y_linear = [y_ref * (p / P_ref) for p in xs]
            ax.plot(range(len(xs)), y_linear, "ko--", lw=1.2, alpha=0.6,
                    label="resposta linear (Pc-proporcional)")
        ax.set_xticks(range(len(xs)))
        ax.set_xticklabels([f"Pc={p}" for p in xs], rotation=15, fontsize=9)
        ax.set_ylabel("delta_perp_max [um]")
        ax.set_title(f"Teste C - sweep contact_local\n"
                     f"se delta_perp(2*Pc)/delta_perp(Pc)~2 => linear; ~1 => compartmentalizado")
        ax.legend(fontsize=8, loc="upper left")
        ax.grid(alpha=0.3)

    # painel 2: Teste D - barra openSAS vs baseline
    ax = axes[1]
    rowsD = [r for r in rows if r["test"] == "D"]
    if rowsD:
        labels = [r["case"].replace("on-fsi-2", "baseline").replace("baseline-openSAS", "openSAS")
                  for r in rowsD]
        ys = [r["delta_perp_max_um"] for r in rowsD]
        colors = ["#3498db" if "openSAS" not in lbl else "#e67e22" for lbl in labels]
        bars = ax.bar(range(len(ys)), ys, color=colors,
                       edgecolor="black", linewidth=0.5)
        for b, y in zip(bars, ys):
            ax.text(b.get_x()+b.get_width()/2, y, f"{y:.2f}", ha="center", va="bottom",
                    fontsize=9, fontweight="bold")
        ax.set_xticks(range(len(ys)))
        ax.set_xticklabels(labels, fontsize=9)
        ax.set_ylabel("delta_perp_max [um]")
        ax.set_title("Teste D - cul-de-sac aberto vs fechado\n"
                     "se openSAS >> baseline => cul-de-sac e' agente da compartmentalizacao")
        ax.grid(alpha=0.3)

    # painel 3: perfis delta_perp(z) - todos os casos rodados
    ax = axes[2]
    for name, (z, dp) in profiles.items():
        ax.plot(z, dp, marker=".", lw=1.2, label=name)
    ax.axvline(22.5, color="red", ls="--", lw=1.0, label="z = contact_local")
    ax.set_xlabel("z [mm]")
    ax.set_ylabel("delta_perp(z) [um]")
    ax.set_title("perfil delta_perp(z) - centroide do nervo")
    ax.legend(fontsize=8, loc="best")
    ax.grid(alpha=0.3)

    fig.suptitle("Testes C & D - direcionalidade da carga arterial via FSI",
                  fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(OUT_DIR / "diag_testCD_delta_perp.png", dpi=150)
    plt.close(fig)
    print(f"  figura: {OUT_DIR / 'diag_testCD_delta_perp.png'}")


if __name__ == "__main__":
    main()
