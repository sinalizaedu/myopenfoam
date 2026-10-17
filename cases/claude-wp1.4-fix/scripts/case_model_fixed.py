"""WP1.4 — mapeamento LHS → geometria/material, SEM constantes inventadas.

Corrige tres defeitos de cases/wp1.4/sweep_full/scripts/case_model.py:

  1. `vit_dv_scale = 1.085`  — REMOVIDO.
     Multiplicador de complacencia sem fonte. Contradiz a H4 corrigida do plano
     de tese ("Gel vitreo e BSS sao ambos praticamente incompressiveis... Nao ha
     razao para o pico elastico diferir"; K_vitrectomizado ~ K_controle, com a
     diferenca em R_ref). Vitrectomia NAO tem via mecanica num modelo de casca de
     uma camada; entra no WP0 via R_ref, nao aqui.

  2. `dr_acd = -0.11 * (ACD - 3.25)` — REMOVIDO.
     Coeficiente e nominal sem fonte. ACD nao enrijece nem amolece uma casca de
     uma camada. Como K ~ R^-4, o deslocamento inventado de raio produzia ate
     ~18% em K. ACD volta no WP5, como a restricao ACD_min medida no Ensaio D.

  3. `LENS_DR_MM = {0, -0.22, +0.35}` — REMOVIDO.
     Mesma natureza: sem fonte e sem mecanismo nesta geometria.

Consequencia declarada: ACD, estado do cristalino e vitrectomia sao registrados
no resultado (sao entradas da calculadora clinica) mas tem
`mechanical_pathway = "none"` e NAO afetam K nem V. Responder a esses tres exigiria
o segmento anterior, que e o WP1.5 (excluido do escopo).

Mantido do pipeline do Composer porque esta correto:
  - t(theta) com transicao cosseno entre polo e equador, via secoes de casca por faixa.
  - P0 = 16,9 mmHg e teto de 50 mmHg (WP0/WP1.2; teto justificado pelos picos
    clinicos de Knecht et al. 2009 / Sharei et al. 2010 / Kotliar et al. 2007).
  - mu1/alpha1 nominais do ajuste Ogden contra Friedenwald recalibrada (WP1.2).
"""
from __future__ import annotations

import math
from typing import Any

# --- WP0 / WP1.2 ---------------------------------------------------------------
P0_MMHG = 16.9          # basal recalibrada no WP0
P_FINAL_MMHG = 50.0     # teto: picos clinicos pos-IVI (Knecht 2009 et al.), via WP1.2
N_STEPS = 16

# Ajuste Ogden N=1 contra Friedenwald recalibrada (WP1.2, Tabela de ajuste)
MU1_NOMINAL = 2.2708230587169704
ALPHA1_NOMINAL = 1.05617628707085


def p_targets(
    p_final: float = P_FINAL_MMHG,
    n_steps: int = N_STEPS,
    p0: float = P0_MMHG,
) -> list[float]:
    return [p0 + (p_final - p0) * i / n_steps for i in range(1, n_steps + 1)]


def thickness_at_colatitude(
    theta_rad: float,
    t_equatorial_mm: float,
    t_posterior_mm: float,
    *,
    theta_min_rad: float,
    theta_max_rad: float = math.pi / 2.0,
) -> float:
    """Transicao cosseno: t_posterior em theta->theta_min, t_equatorial em 90 graus.

    ATENCAO (limitacao declarada): o octante cobre theta em [theta_min, 90] — um
    polo so — e z=0 e plano de simetria. Ao espelhar, t_posterior e aplicada
    TAMBEM no polo anterior, onde anatomicamente estaria a cornea. A geometria de
    octante com simetria equatorial nao consegue ter polo anterior diferente do
    posterior. A sensibilidade de t_posterior deve ser lida com essa ressalva.
    """
    denom = max(theta_max_rad - theta_min_rad, 1e-9)
    u = (float(theta_rad) - theta_min_rad) / denom
    u = min(1.0, max(0.0, u))
    blend = 0.5 * (1.0 - math.cos(math.pi * u))
    return float(t_posterior_mm + (t_equatorial_mm - t_posterior_mm) * blend)


def _parse_bool(v: Any) -> bool:
    return v in (True, "True", "true", "sim", "Sim", 1, "1")


def resolve_case(row: dict, *, theta_min_deg: float = 3.0, n_bands: int | None = None) -> dict:
    """Parametros resolvidos para malha, deck e pos-processamento.

    R = AL/2 e a unica relacao geometrica usada (aproximacao esferica, declarada
    no plano: "R proporcional ao comprimento axial e aproximacao... o escalonamento
    R^4 e uma primeira ordem, nao uma lei").
    """
    al = float(row["comprimento_axial_mm"])
    t_eq = float(row["t_equatorial_mm"])
    t_post = float(row["t_posterior_mm"])
    mu1 = MU1_NOMINAL * float(row["mu1_factor"])
    alpha1 = ALPHA1_NOMINAL * float(row["alpha1_factor"])

    # Registrados, sem via mecanica nesta geometria (ver docstring do modulo)
    acd = float(row["ACD_mm"])
    lens = str(row.get("lens_status", "phakic")).lower()
    if lens not in ("phakic", "pseudophakic", "aphakic"):
        lens = "phakic"
    vit = _parse_bool(row.get("vitrectomy", False))

    r_mm = al / 2.0

    theta_min = math.radians(theta_min_deg)
    n_s = 32
    ts = [
        thickness_at_colatitude(
            theta_min + (math.pi / 2.0 - theta_min) * k / (n_s - 1),
            t_eq,
            t_post,
            theta_min_rad=theta_min,
        )
        for k in range(n_s)
    ]
    t_mean_mm = sum(ts) / len(ts)

    return {
        "R_mm": round(r_mm, 4),
        "t_equatorial_mm": t_eq,
        "t_posterior_mm": t_post,
        "t_mean_mm": round(t_mean_mm, 5),
        "mu1_MPa": mu1,
        "alpha1": alpha1,
        # entradas da calculadora clinica, inertes no FE:
        "ACD_mm": acd,
        "lens_status": lens,
        "vitrectomy": vit,
        "theta_min_deg": theta_min_deg,
        "n_bands": n_bands,
        "modeling": {
            "R": "AL/2 (aproximacao esferica; sem deslocamentos por ACD/cristalino)",
            "thickness": "t(theta) cosseno equador<->polo, secoes de casca por faixa",
            "mechanical_pathway_ACD": "none",
            "mechanical_pathway_lens": "none",
            "mechanical_pathway_vitrectomy": "none (vai para R_ref no WP0, conforme H4)",
            "prestress": "sem MULF; justificado pelo WP1.3 (efeito <1% no Ogden)",
        },
    }


def nominal_row() -> dict:
    """Caso nominal: centro das faixas do plano de tese (Secao WP1.4)."""
    return {
        "case_id": "NOMINAL",
        "comprimento_axial_mm": 25.0,   # centro de 20-30 mm (plano, biometria da coorte)
        "t_equatorial_mm": 0.55,        # centro de 0,3-0,8 mm (plano)
        "t_posterior_mm": 0.9,          # centro de 0,6-1,2 mm (plano)
        "mu1_factor": 1.0,
        "alpha1_factor": 1.0,
        "ACD_mm": 3.25,                 # centro de 2,0-4,5 mm (plano)
        "lens_status": "phakic",
        "vitrectomy": False,
    }
