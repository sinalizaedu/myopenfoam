#!/usr/bin/env python3
"""Malha de octante esferico com t(theta) por faixas — espessura = media
ponderada por area do anel (corrige o defeito de amostragem pontual).

HISTORICO DO DEFEITO

  Versao do Composer (cases/wp1.4/sweep_full/scripts/gen_mesh_variable_t.py):
  o numero de faixas e igual a `ne`, e a espessura de cada faixa e t(theta)
  avaliada no CENTRO NOMINAL da faixa.

  Minha primeira versao: desacoplei n_bands de ne, mas o octante tem apenas
  `ne` aneis de elementos, entao pedir 16 ou 32 faixas com ne=8 nao cria
  faixas novas — so muda ONDE t(theta) e amostrada dentro de cada anel. O
  estudo de malha mediu isso e achou 1,3-2,6% de dispersao em K vinda de uma
  escolha puramente arbitraria (ver claude-REVISAO-WP5-WP6.md / mesh_independence.json).

CORRECAO

  Uma faixa por anel de elementos (sem faixa vazia, sem escolha arbitraria de
  quantidade), e a espessura de cada faixa e a media de t(theta) ponderada pela
  AREA do anel:

      t_barra = integral(t(theta) sin(theta) dtheta) / integral(sin(theta) dtheta)

  O peso sin(theta) e o elemento de area da esfera (dA = 2 pi R^2 sin(theta) dtheta).
  Escolhi a media ponderada por area porque este problema e dominado por
  membrana — a rigidez de membrana escala com t (confirmado pela varredura:
  expoente +1,08 em t), entao preservar a media de t por area preserva a
  rigidez de membrana total do anel. Uma media simples em theta daria peso
  igual a aneis de areas diferentes; uma media em t^3 seria a escolha certa se
  o problema fosse dominado por flexao, o que nao e o caso aqui.

  O span de theta de cada anel e lido da propria malha (coordenadas dos nos),
  nao assumido uniforme.

`thickness_mode="point"` reproduz o comportamento antigo, para o estudo
comparativo mostrar que a dispersao desaparece.

Compativel com write_deck_vt.write_deck_variable_t do Composer: mantem os
ELSETs `T_BAND_%02d` e a chave `band_thickness_mm` no .meta.json.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CASES = HERE.parents[1]
sys.path.insert(0, str(CASES / "wp1.1" / "scripts"))

from gen_sphere_shell_mesh import _nset, _surf, build_spherical_octant  # noqa: E402

from case_model_fixed import thickness_at_colatitude  # noqa: E402

_N_QUAD = 64  # pontos de quadratura por faixa (t(theta) e suave; 64 e folgado)
# numpy 1.26 (container) nao tem np.trapezoid, que e 2.0+
_trapz = getattr(np, "trapezoid", None) or np.trapz


def _colatitudes(coords: dict[int, np.ndarray], nodes: list[int]) -> np.ndarray:
    """Colatitude de TODOS os nos do elemento (inclui nos de meio de aresta)."""
    pts = np.array([coords[n] for n in nodes])
    r = np.linalg.norm(pts, axis=1)
    r = np.where(r < 1e-12, 1e-12, r)
    return np.arccos(np.clip(pts[:, 2] / r, -1.0, 1.0))


def _t_medio_por_area(
    theta_a: float, theta_b: float, t_eq: float, t_post: float, theta_min: float
) -> float:
    """Media de t(theta) ponderada pela area do anel [theta_a, theta_b]."""
    if theta_b <= theta_a:
        return thickness_at_colatitude(theta_a, t_eq, t_post, theta_min_rad=theta_min)
    th = np.linspace(theta_a, theta_b, _N_QUAD)
    t = np.array([
        thickness_at_colatitude(x, t_eq, t_post, theta_min_rad=theta_min) for x in th
    ])
    w = np.sin(th)
    num = _trapz(t * w, th)
    den = _trapz(w, th)
    return float(num / den) if den > 0 else float(t.mean())


def write_mesh_banded(
    out: Path,
    R: float,
    t_equatorial_mm: float,
    t_posterior_mm: float,
    ne: int,
    order: int,
    label: str,
    *,
    theta_min_deg: float = 3.0,
    reduced: bool = True,
    n_bands: int | None = None,
    thickness_mode: str = "area_mean",
) -> dict:
    """n_bands=None (recomendado) -> uma faixa por anel de elementos.

    thickness_mode:
      "area_mean" (padrao) -> t_barra ponderada por area do anel [CORRETO]
      "point"              -> t(theta) no centro nominal da faixa [comportamento
                              antigo, so para o estudo comparativo]
    """
    if thickness_mode not in ("area_mean", "point"):
        raise ValueError(f"thickness_mode invalido: {thickness_mode!r}")

    coords, elems, nsets, inner_pairs = build_spherical_octant(
        R, ne, order, theta_min_deg=theta_min_deg
    )
    theta_min = math.radians(theta_min_deg)
    theta_max = math.pi / 2.0

    # --- aneis de elementos lidos da propria malha --------------------------
    info = []
    for eid, nodes in elems:
        th = _colatitudes(coords, nodes)
        info.append({
            "eid": eid, "nodes": nodes,
            "th_c": float(th.mean()), "th_lo": float(th.min()), "th_hi": float(th.max()),
        })
    # agrupa por colatitude de centroide (tolerancia relativa ao passo nominal)
    tol = 0.25 * (theta_max - theta_min) / max(ne, 1)
    centros = sorted({round(e["th_c"] / tol) * tol for e in info})
    aneis: list[list[dict]] = [[] for _ in centros]
    for e in info:
        k = min(range(len(centros)), key=lambda i: abs(centros[i] - e["th_c"]))
        aneis[k].append(e)
    aneis = [a for a in aneis if a]
    n_aneis = len(aneis)

    # --- agrupa aneis em faixas -------------------------------------------
    if n_bands is None or n_bands >= n_aneis:
        grupos = [[a] for a in aneis]          # uma faixa por anel
    else:
        grupos = [[] for _ in range(n_bands)]
        for i, a in enumerate(aneis):
            grupos[min(n_bands - 1, i * n_bands // n_aneis)].append(a)
        grupos = [g for g in grupos if g]

    bands: list[list[tuple[int, list[int]]]] = []
    band_t: list[float] = []
    band_span: list[list[float]] = []
    for gi, grupo in enumerate(grupos):
        elementos = [e for anel in grupo for e in anel]
        th_lo = min(e["th_lo"] for e in elementos)
        th_hi = max(e["th_hi"] for e in elementos)
        if thickness_mode == "area_mean":
            t_band = _t_medio_por_area(th_lo, th_hi, t_equatorial_mm, t_posterior_mm, theta_min)
        else:
            u = (gi + 0.5) / len(grupos)
            t_band = thickness_at_colatitude(
                theta_min + (theta_max - theta_min) * u,
                t_equatorial_mm, t_posterior_mm, theta_min_rad=theta_min,
            )
        bands.append([(e["eid"], e["nodes"]) for e in elementos])
        band_t.append(float(t_band))
        band_span.append([math.degrees(th_lo), math.degrees(th_hi)])

    n_bands_eff = len(bands)
    etype = "S8R" if (order == 2 and reduced) else ("S8" if order == 2 else "S4")
    out.parent.mkdir(parents=True, exist_ok=True)

    with open(out, "w") as fh:
        fh.write(f"** wp1.4 corrigido — t(theta) por anel, media por area — {label}\n")
        fh.write(
            f"** R={R} mm  t_eq={t_equatorial_mm}  t_post={t_posterior_mm}  "
            f"ne={ne}  aneis={n_aneis}  faixas={n_bands_eff}  "
            f"modo={thickness_mode}  type={etype}\n"
        )
        fh.write("** mesh_kind=spherical  bc_mode=symmetry_octant  volume_scale=8\n")
        fh.write(f"** theta_min_deg={theta_min_deg}\n")
        fh.write(f"** nodes={len(nsets['NALL'])}  elements={len(elems)}\n")
        fh.write("*NODE, NSET=NALL\n")
        for nid in nsets["NALL"]:
            x, y, z = coords[nid]
            fh.write(f"{nid:8d}, {x: .8f}, {y: .8f}, {z: .8f}\n")

        for b in range(n_bands_eff):
            fh.write(f"*ELEMENT, TYPE={etype}, ELSET=T_BAND_{b:02d}\n")
            for eid, nodes in bands[b]:
                fh.write(", ".join(f"{v:8d}" for v in [eid, *nodes]) + "\n")

        fh.write("*ELSET, ELSET=SHELL\n")
        all_eids = sorted(eid for band in bands for eid, _ in band)
        for i in range(0, len(all_eids), 8):
            fh.write(", ".join(f"{e:8d}" for e in all_eids[i : i + 8]) + "\n")

        for name, ids in nsets.items():
            if name != "NALL":
                _nset(fh, name, ids)
        _surf(fh, "INNER_SURF", inner_pairs)

    # media de t ponderada por area sobre a casca inteira, para referencia
    t_global = _t_medio_por_area(
        theta_min, theta_max, t_equatorial_mm, t_posterior_mm, theta_min
    )
    meta = {
        "R_mm": R,
        "t_mm": t_global,
        "t_mean_mm": t_global,
        "t_equatorial_mm": t_equatorial_mm,
        "t_posterior_mm": t_posterior_mm,
        "band_thickness_mm": band_t,
        "band_span_deg": band_span,
        "thickness_mode": thickness_mode,
        "ne": ne,
        "n_rings": n_aneis,
        "n_bands_requested": n_bands,
        "n_bands_effective": n_bands_eff,
        "order": order,
        "etype": etype,
        "mesh_kind": "spherical",
        "bc_mode": "symmetry_octant",
        "volume_scale": 8,
        "theta_min_deg": theta_min_deg,
        "variable_thickness": True,
        "n_nodes": len(nsets["NALL"]),
        "n_elements": len(elems),
        "reduced": reduced,
    }
    out.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2))
    return meta
