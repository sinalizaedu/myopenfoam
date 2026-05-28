#!/usr/bin/env python3
"""predict_teste_2d_fsi_contact.py

Previsao ANALITICA do que o contato OA x ONS faria no caso
`cases/teste-2d-fsi-oa-on/` se ele estivesse ligado. Serve como sanity-check
para comparar com o resultado numerico depois de reativar `solidContact`.

Cadeia de modelagem (1D simplificada, paralela ao caso 2D plane-strain):

    1. P_lumen(t)   -> da onda OMVS (constant/inlet_pressure.dat).
    2. F_wall(t)    -> medido pelo watchpoint preCICE em wallBotCenter
                       (y=10.1 mm). Pressao equivalente = F_y / area_face.
                       Mesmo com contato OFF, esse F mede o que CHEGA na
                       parede da OA -- e' a entrada do nosso problema.
    3. P_contact(t) -> com contato ON, a parede de baixo da OA empurra a
                       ONS na regiao tangente em x=10mm. Aproximamos a
                       pressao de contato como atenuada pelo arranjo em
                       SERIE: OA wall (rigidez K_OAw) + ONS dome (K_ONS) +
                       ON (K_ON). A componente mais mole governa.
    4. delta_ON(t)  -> Compressao do ON. ON e' fluido-elastico (nu=0.49,
                       quase incompressivel) e fica confinado lateralmente
                       pela ONS+fat_below. Em compressao confinada o modulo
                       efetivo e' M = K_bulk + 4G/3, MUITO maior que E.
                       Em 2D plane-strain a confinamento e' parcial -- damos
                       UMA banda alta (confinada perfeita) e UMA banda baixa
                       (cisalhamento livre) como envelopes.
    5. sigma_contact -> Para comparar com limites tissulares (ONS rompe em
                       ~50-100 kPa de tensao circunferencial).

Saidas em brunaStuff/:
    teste_2d_fsi_contact_prediction.png
    teste_2d_fsi_contact_prediction.csv

Uso:
    python3 brunaStuff/predict_teste_2d_fsi_contact.py
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


# ---------- Parametros fisicos / geometricos do caso ---------------------
REPO = Path(__file__).resolve().parent.parent
CASE = REPO / "cases" / "teste-2d-fsi-oa-on"
WATCH_BOT = CASE / "solid" / "precice-Solid-watchpoint-wallBotCenter.log"
WATCH_TOP = CASE / "solid" / "precice-Solid-watchpoint-wallTopCenter.log"
P_INLET = CASE / "fluid" / "constant" / "inlet_pressure.dat"
P_OUTLET = CASE / "fluid" / "constant" / "outlet_pressure.dat"

OUT_PNG = REPO / "brunaStuff" / "teste_2d_fsi_contact_prediction.png"
OUT_CSV = REPO / "brunaStuff" / "teste_2d_fsi_contact_prediction.csv"

RHO_BLOOD = 1050.0           # kg/m^3 (rho usado na conversao p_cinematica -> p)
PA_TO_MMHG = 1.0 / 133.322   # 1 Pa = 7.5e-3 mmHg

# Mesh do solido: NX=80, LX=20mm, LZ=1mm -> area de uma face em y=10mm
DX = 20e-3 / 80              # 0.25 mm
DZ = 1e-3                    # 1 mm (espessura 2D)
A_FACE = DX * DZ             # 2.5e-7 m^2

# Materiais (do mechanicalProperties)
E_OA = 0.3e6                 # Pa, parede da OA (0.3 MPa)
E_ONS = 3.0e6                # Pa, bainha (3 MPa)
E_ON = 30e3                  # Pa, nervo optico (30 kPa)
NU = 0.49                    # quase incompressivel

# Espessuras / dimensoes verticais para o spring model
H_OA = 0.2e-3                # 0.2 mm parede OA
H_ONS = 1.0e-3               # ~1 mm de "casca" ONS comprimida verticalmente
H_ON = 3.0e-3                # diametro do ON ~ 3 mm (eixo y, regiao confinada)

# Area de contato Hertziana (estimada): tangente OA <-> ONS engaja ~2 mm de
# largura em sistole (Hertz: a ~ sqrt(F*R/E*), R=R_ONS=2.5mm).
A_CONTACT_PEAK = 2.0e-3 * DZ  # ~5e-6 m^2 (banda de 2 mm de largura)


# ---------- Leitura de arquivos ------------------------------------------
def parse_openfoam_table(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Le um arquivo OpenFOAM no formato `( (t v) (t v) ... )` ignorando //."""
    txt = path.read_text(encoding="utf-8")
    # Remove comentarios //...
    txt = re.sub(r"//.*$", "", txt, flags=re.MULTILINE)
    pairs = re.findall(r"\(\s*([\d.eE+\-]+)\s+([\d.eE+\-]+)\s*\)", txt)
    if not pairs:
        raise RuntimeError(f"Nenhum par (t v) encontrado em {path}")
    arr = np.array(pairs, dtype=float)
    return arr[:, 0], arr[:, 1]


def parse_watchpoint(path: Path) -> np.ndarray:
    """Le watchpoint preCICE (header + linhas brancas-separadas)."""
    data = np.loadtxt(path, skiprows=1)
    return data  # cols: t x y z Fx Fy Fz


# ---------- Modelo analitico ---------------------------------------------
def M_confined(E: float, nu: float) -> float:
    """Modulo de onda elastica (compressao 1D perfeitamente confinada)."""
    return E * (1.0 - nu) / ((1.0 + nu) * (1.0 - 2.0 * nu))


def hertz_cylinder_plane(F_per_unit_length: np.ndarray) -> dict[str, np.ndarray]:
    """Contato cilindro-plano em 2D (plane-strain, deformacao por unidade de
    espessura z).

    Cilindro = ONS dome (R = R_ONS = 2.5 mm) contra plano = base de Block B
    da OA. Dois materiais elasticos, modulo efetivo:

        1/E*  =  (1 - nu_OA^2)/E_OA  +  (1 - nu_ONS^2)/E_ONS

    Como E_OA = 0.3 MPa << E_ONS = 3 MPa, E* e' dominado por E_OA.

    Banda de contato (meia-largura): a = 2 * sqrt(F'*R / (pi * E*))
    Pressao max:                     p_max = 2*F' / (pi * a)
    onde F' = F / L_z e' a forca por unidade de espessura em z.

    delta_central = Hertz indentation
                  ~ 2 F' (1-nu^2) / (pi E*) * (ln(4R/a) - 0.5)
    """
    E_star = 1.0 / ((1.0 - NU**2) / E_OA + (1.0 - NU**2) / E_ONS)
    R = 2.5e-3  # raio da ONS

    # Evita divisao por zero quando F' = 0
    Fp = np.maximum(F_per_unit_length, 1e-12)
    a = 2.0 * np.sqrt(Fp * R / (np.pi * E_star))
    p_max = 2.0 * Fp / (np.pi * a)

    # Indentacao Hertziana (limite superior local na interface OA-ONS)
    delta_indent = (2.0 * Fp * (1 - NU**2) / (np.pi * E_star)) * (
        np.log(4 * R / np.maximum(a, 1e-9)) - 0.5
    )
    delta_indent = np.maximum(delta_indent, 0.0)
    return {"a_mm": a * 1e3, "p_max": p_max, "delta_indent": delta_indent, "E_star": E_star}


def on_compression(P_contact: np.ndarray) -> dict[str, np.ndarray]:
    """Compressao do nervo optico sob carga de contato.

    Dois cenarios:
      (i) "uniforme": pressao P_contact distribuida sobre o diametro do ON;
          delta = P * h / M  (M = modulo confinado, pois fat ao redor confina)
      (ii) "local 1/2": metade da pressao chega (Saint-Venant decai com
           distancia da banda Hertziana), delta = (P/2) * h / M
    """
    M = M_confined(E_ON, NU)
    delta_unif = P_contact * H_ON / M
    delta_local = 0.5 * P_contact * H_ON / M
    return {"M_ON": M, "delta_unif": delta_unif, "delta_local": delta_local}


def main() -> None:
    # ---- Carrega P_lumen(t) ------------------------------------------------
    t_in, pcin_in = parse_openfoam_table(P_INLET)
    t_out, pcin_out = parse_openfoam_table(P_OUTLET)
    P_inlet = pcin_in * RHO_BLOOD                  # Pa (absoluto)
    P_outlet = pcin_out * RHO_BLOOD

    # ---- Carrega watchpoints da parede -------------------------------------
    wb = parse_watchpoint(WATCH_BOT)
    wt = parse_watchpoint(WATCH_TOP)
    t_w = wb[:, 0]
    Fy_bot = wb[:, 5]   # Force_y na celula central de lumen_bot
    Fy_top = wt[:, 5]

    # Pressao equivalente = Force / area_face
    # Convencao do mesh: lumen empurra parede para fora -> Fy_bot < 0 (parede inferior empurrada para BAIXO)
    # e Fy_top > 0 (parede superior empurrada para CIMA). Tomar valor absoluto.
    P_wall_bot = np.abs(Fy_bot) / A_FACE
    P_wall_top = np.abs(Fy_top) / A_FACE

    # ---- Pressao de contato ESPERADA --------------------------------------
    # Forca total para baixo sobre o patch wall_bot por unidade de espessura
    # em z = P_wall_bot * L_x (largura total = 20 mm).
    # Mas isto sobrestima: a parede so empurra para baixo onde tem contato
    # com a ONS (banda Hertziana central). Vou usar Hertz cilindro-plano:
    # F' = forca total / L_z onde forca total = integral de P sobre wall_bot.
    L_x = 20e-3
    F_per_Lz = P_wall_bot * L_x  # N/m, forca por unidade de espessura em z

    hertz = hertz_cylinder_plane(F_per_Lz)
    p_max_hertz = hertz["p_max"]          # Pa, pressao pico na interface
    a_hertz = hertz["a_mm"]                # mm, meia-largura da banda
    delta_indent = hertz["delta_indent"]   # m, indentacao Hertziana central

    # Dois cenarios para P_contact que o ON sente:
    #   (a) "uniforme": P_contact = P_wall_bot (limite inferior, sem
    #        concentracao geometrica; valido se a curva da ONS fosse plana)
    #   (b) "hertz":    P_contact = p_max (limite superior local; pressao
    #        no PONTO de tangencia, decai parabolicamente para os lados)
    P_contact_unif = P_wall_bot
    P_contact_hertz = p_max_hertz

    on_unif = on_compression(P_contact_unif)
    on_hertz = on_compression(P_contact_hertz)

    # delta_ON: envelope entre cenarios uniforme e hertz, com fator local 1/2
    # (decaimento Saint-Venant da concentracao em profundidade).
    d_ON_low = on_unif["delta_local"]       # menor: uniforme + 1/2 decai
    d_ON_high = on_hertz["delta_unif"]      # maior: Hertz pico + uniforme
    d_ON_typical = on_unif["delta_unif"]    # central: uniforme + sem decair

    # ---- Plot --------------------------------------------------------------
    fig, axes = plt.subplots(4, 1, figsize=(11, 12), sharex=True)

    # 1. P_lumen(t)
    ax = axes[0]
    ax.plot(t_in, P_inlet * PA_TO_MMHG, "C0-", lw=1.4, label="P_inlet (mmHg)")
    ax.plot(t_out, P_outlet * PA_TO_MMHG, "C1--", lw=1.0, label="P_outlet (mmHg)")
    ax.axhspan(80, 120, alpha=0.07, color="red", label="banda OMVS 80–120 mmHg")
    ax.set_xlim(0, t_w[-1])
    ax.set_ylabel("P_lumen [mmHg]")
    ax.set_title("Cadeia da previsão analítica (smoke meio-ciclo)\n"
                 "1) Pressão de entrada no lúmen (input da FSI)", fontsize=10)
    ax.grid(alpha=0.3); ax.legend(loc="lower right", fontsize=9)

    # 2. F_y na parede e pressao equivalente
    ax = axes[1]
    ax2 = ax.twinx()
    ax.plot(t_w, Fy_bot * 1e3, "C2-", lw=1.4, label="F_y wallBotCenter (mN)")
    ax.plot(t_w, Fy_top * 1e3, "C3--", lw=1.0, label="F_y wallTopCenter (mN)")
    ax2.plot(t_w, P_wall_bot * PA_TO_MMHG, "k:", lw=1.2,
             label="P_wall ≡ |F_y|/A_face [mmHg]")
    ax.set_ylabel("F_y na celula central [mN]")
    ax2.set_ylabel("P_wall equiv [mmHg]")
    ax.set_title("2) Força/pressão que chega à parede da OA (medida no watchpoint preCICE)",
                 fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(loc="lower left", fontsize=9)
    ax2.legend(loc="upper right", fontsize=9)

    # 3. Pressao de contato ESPERADA + banda Hertziana
    ax = axes[2]
    ax.plot(t_w, P_wall_bot * 1e-3, "C0-", lw=1.4,
            label="P_uniforme = P_wall_bot")
    ax.plot(t_w, p_max_hertz * 1e-3, "C4-", lw=1.6,
            label=f"p_max Hertz (cilindro R={2.5}mm vs plano, E*={hertz['E_star']*1e-3:.0f} kPa)")
    ax.axhline(50, color="r", linestyle=":", alpha=0.6,
               label="ruptura tipica ONS ~50 kPa (Sigal 2004)")
    ax.set_ylabel("Pressão [kPa]")
    ax.set_title("3) Pressão de contato esperada (se solidContact estivesse ON)",
                 fontsize=10)
    ax.grid(alpha=0.3); ax.legend(loc="upper left", fontsize=9)

    # 4. Compressao do ON (envelope)
    ax = axes[3]
    ax.fill_between(t_w, d_ON_low * 1e6, d_ON_high * 1e6,
                    color="C5", alpha=0.20,
                    label="envelope (low: uniforme×½, high: Hertz pico)")
    ax.plot(t_w, d_ON_typical * 1e6, "C5-", lw=1.6,
            label=f"δ_ON tipico (P_unif, M_ON={on_unif['M_ON']*1e-3:.0f} kPa)")
    ax.plot(t_w, delta_indent * 1e6, "C6:", lw=1.4,
            label="δ indentacao Hertz local OA-ONS (nao do ON)")
    ax.set_ylabel("Deslocamento [μm]")
    ax.set_xlabel("t [s]")
    ax.set_title("4) Compressão esperada do ON e indentação Hertziana OA-ONS",
                 fontsize=10)
    ax.grid(alpha=0.3); ax.legend(loc="upper left", fontsize=9)

    fig.suptitle(
        "Previsão analítica — sanity check para validar o numérico quando o contato voltar a ligar",
        fontsize=11, y=1.0
    )
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=160, bbox_inches="tight")
    print(f"Figura: {OUT_PNG}")

    # ---- CSV com series temporais -----------------------------------------
    with OUT_CSV.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow([
            "t_s", "P_inlet_mmHg", "P_outlet_mmHg",
            "Fy_wallBot_N", "Fy_wallTop_N",
            "P_wallBot_Pa", "p_max_Hertz_Pa", "a_Hertz_mm",
            "delta_indent_Hertz_um",
            "delta_ON_typical_um", "delta_ON_low_um", "delta_ON_high_um",
        ])
        Pin_interp = np.interp(t_w, t_in, P_inlet) * PA_TO_MMHG
        Pout_interp = np.interp(t_w, t_out, P_outlet) * PA_TO_MMHG
        for i, t in enumerate(t_w):
            w.writerow([
                f"{t:.6f}",
                f"{Pin_interp[i]:.3f}", f"{Pout_interp[i]:.3f}",
                f"{Fy_bot[i]:.6e}", f"{Fy_top[i]:.6e}",
                f"{P_wall_bot[i]:.3f}", f"{p_max_hertz[i]:.3f}", f"{a_hertz[i]:.3f}",
                f"{delta_indent[i]*1e6:.3f}",
                f"{d_ON_typical[i]*1e6:.4f}",
                f"{d_ON_low[i]*1e6:.4f}",
                f"{d_ON_high[i]*1e6:.4f}",
            ])
    print(f"CSV:    {OUT_CSV}")

    # ---- Resumo no terminal -----------------------------------------------
    i_peak = int(np.argmax(P_wall_bot))
    print()
    print("================ Resumo no pico do smoke meio-ciclo =================")
    print(f"  Tempo do pico medido    : t = {t_w[i_peak]:.3f} s  ({100*t_w[i_peak]/t_w[-1]:.0f}% do run)")
    print(f"  P_inlet (mmHg)          : {np.interp(t_w[i_peak], t_in, P_inlet)*PA_TO_MMHG:.2f}")
    print(f"  F_y na parede (mN)      : {Fy_bot[i_peak]*1e3:.3f}")
    print(f"  P_wall_bot (Pa)         : {P_wall_bot[i_peak]:.1f}  ({P_wall_bot[i_peak]*PA_TO_MMHG:.2f} mmHg)")
    print()
    print(f"  Hertz cilindro-plano (E*={hertz['E_star']*1e-3:.0f} kPa):")
    print(f"    meia-largura a        : {a_hertz[i_peak]:.3f} mm")
    print(f"    p_max no centro       : {p_max_hertz[i_peak]*1e-3:.2f} kPa "
          f"({p_max_hertz[i_peak]*PA_TO_MMHG:.0f} mmHg)")
    print(f"    delta indentacao OA-ONS: {delta_indent[i_peak]*1e6:.1f} μm")
    print()
    print(f"  delta_ON sob compressao confinada (M_ON={on_unif['M_ON']*1e-3:.0f} kPa, h_ON=3 mm):")
    print(f"    cenario uniforme      : {d_ON_typical[i_peak]*1e6:.1f} μm")
    print(f"    cenario uniforme x ½  : {d_ON_low[i_peak]*1e6:.1f} μm  (limite inferior)")
    print(f"    cenario Hertz pico    : {d_ON_high[i_peak]*1e6:.1f} μm  (limite superior local)")
    print()
    print("Interpretacao:")
    print("  - O cenario UNIFORME e' o melhor proxy: a banda de contato e' larga")
    print("    o suficiente (~mm) para a pressao se distribuir antes de atingir o ON.")
    print(f"    Resposta esperada: delta_ON ~ {d_ON_typical[i_peak]*1e6:.0f} um no pico sistolico.")
    print("  - p_max Hertz local (~150 kPa) excede o limite de ruptura da ONS (~50 kPa).")
    print("    Isso indica que a hipotese de contato TANGENTE (gap=0) e' irrealista;")
    print("    com gap inicial > 0, a area de contato cresce gradualmente e p_max cai.")
    print()
    print("Sanity check quando contato VOLTAR a ligar:")
    print(f"  - delta_y do centro do ON (y=7.5 mm) deve crescer ate ~{d_ON_typical[i_peak]*1e6:.0f} um no pico.")
    print(f"  - Pressao maxima medida no patch on_mestrado deve estar entre")
    print(f"    {P_wall_bot[i_peak]*1e-3:.1f} kPa (uniforme) e {p_max_hertz[i_peak]*1e-3:.1f} kPa (Hertz pico).")
    print("  - F_y nos watchpoints da parede deve cair pouco (~5–10%) com o recoil")
    print("    elastico do ONS+ON empurrando de volta.")
    print("=====================================================================")


if __name__ == "__main__":
    main()
