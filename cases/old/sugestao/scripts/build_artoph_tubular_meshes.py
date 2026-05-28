#!/usr/bin/env python3
"""
Constroi polyMesh estruturadas (extrudadas ao longo da centerline da OA) para
o caso artoph-fsi-curva-mestrado, substituindo o pipeline blockMesh+snappyHexMesh
que produzia malha de annulus degenerada para a parede fina (h=0.2 mm).

Saidas:
  cases/artoph-fsi-curva-mestrado/fluid/constant/polyMesh/   (lumen — O-grid)
  cases/artoph-fsi-curva-mestrado/solid/constant/polyMesh/   (annulus — polar)

Patches FLUIDO:
  inlet (s=s0, tampa back), outlet (s=s_end, tampa front), wall (curvada FSI)

Patches SOLIDO:
  inner_cap_back, inner_cap_front (tampas anelares)
  lumen          (sup. interna, interface FSI com fluido)
  arteria_externa (sup. externa, livre de tracao)

Etapas:
  1) Ler artery.stl, extrair centerline por slicing axial (z constante).
  2) Suavizar com spline cubica natural, reamostrar com NZ pontos uniformes.
  3) Calcular frames ortonormais (T, N, B) via parallel transport
     (estavel em pontos de inflexao, ao contrario de Frenet-Serret).
  4) Construir nuvens de pontos:
       - Lumen: O-grid (core quadrado + setores anulares) em cada secao.
       - Wall:  setores anulares puros (sem core).
  5) Conectar secoes consecutivas em hexaedros.
  6) Escrever polyMesh OpenFOAM ASCII (points, faces, owner, neighbour,
     boundary).

Parametros (linha de comando ou globais abaixo).
"""
from __future__ import annotations

import argparse
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray


def _find_src_stl() -> Path:
    """Procura artery.stl em locais conhecidos (host repo e container).

    Procura ao-mestrado primeiro (caso atual, autossuficiente), depois
    artoph-curva-mestrado (legado).
    """
    candidates = [
        Path(os.environ["ARTOPH_SRC_STL"]) if "ARTOPH_SRC_STL" in os.environ else None,
        # ao-mestrado (host)
        Path(__file__).resolve().parents[1] / "cases" / "ao-mestrado"
        / "constant" / "triSurface" / "artery.stl",
        # ao-mestrado (container)
        Path("/simulation/ao-mestrado/constant/triSurface/artery.stl"),
        # Legado artoph (host)
        Path(__file__).resolve().parents[1] / "cases" / "artoph-curva-mestrado"
        / "solid" / "constant" / "triSurface" / "artery.stl",
        # Legado artoph (container)
        Path("/simulation/artoph-curva-mestrado/solid/constant/triSurface/artery.stl"),
    ]
    for c in candidates:
        if c is not None and c.exists():
            return c
    raise FileNotFoundError("artery.stl nao encontrado. Defina ARTOPH_SRC_STL.")


def _find_out_case() -> Path:
    candidates = [
        Path(os.environ["ARTOPH_OUT_CASE"]) if "ARTOPH_OUT_CASE" in os.environ else None,
        Path(__file__).resolve().parents[1] / "cases" / "ao-mestrado",
        Path("/simulation/ao-mestrado"),
        Path(__file__).resolve().parents[1] / "cases" / "artoph-fsi-curva-mestrado",
        Path("/simulation/artoph-fsi-curva-mestrado"),
    ]
    for c in candidates:
        if c is not None and c.exists():
            return c
    raise FileNotFoundError("ao-mestrado/artoph-fsi-curva-mestrado nao encontrado. Defina ARTOPH_OUT_CASE.")


# Lazy: nao resolver no import (permite usar este modulo como biblioteca
# mesmo se o caso de destino nao existir, como faz build_teste_geom.py).
def _safe_find(fn):
    try:
        return fn()
    except FileNotFoundError:
        return None


SRC_STL = _safe_find(_find_src_stl)
OUT_CASE = _safe_find(_find_out_case)

# Parametros geometricos / numericos default --------------------------------
R_LUMEN_M = 0.55e-3            # raio luminal (= D_int / 2 = 1.1 mm / 2)
H_WALL_M = 0.20e-3             # espessura da parede arterial
NZ = 160                       # numero de secoes ao longo da centerline
NCIRC = 32                     # setores circunferenciais
NCORE = 8                      # cells por lado do quadrado central do lumen (NCORE x NCORE)
NRAD_LUMEN = 4                 # aneis radiais entre core e parede (lumen externo)
NRAD_WALL = 3                  # aneis radiais na parede (espessura)
SLICE_THICKNESS_MM = 0.4       # janela de slicing para centroide
SMOOTH_K = 1.0                 # rigidez da spline (1.0 = natural)


# ---------- 1) STL reader (ASCII) -----------------------------------------
def read_ascii_stl_vertices(path: Path) -> NDArray[np.float64]:
    pts: list[tuple[float, float, float]] = []
    with path.open() as f:
        for line in f:
            ls = line.strip()
            if ls.startswith("vertex"):
                a, b, c = ls.split()[1:4]
                pts.append((float(a), float(b), float(c)))
    return np.array(pts)


# ---------- 2) Centerline extraction --------------------------------------
def extract_centerline_marching(
    pts: NDArray[np.float64], r_search_m: float = 1.5e-3, n_seeds: int = 100,
    n_iter: int = 8,
) -> NDArray[np.float64]:
    """Extrai centerline via 'seeds-no-eixo-principal + relaxacao iterativa por
    centroide local'. Robusto para tubos curvados.

    Etapas:
      1) PCA da nuvem para descobrir o eixo principal e os extremos.
      2) n_seeds pontos uniformemente distribuidos ao longo desse eixo.
      3) Para cada seed, repete n_iter vezes:
           - busca os vertices da STL dentro de raio r_search;
           - move o seed para o centroide deles, mas restrito ao plano
             perpendicular ao tangente local (evita seeds escorregarem
             ao longo do tubo e formarem clusters).
      4) Reordena seeds por arc length ao longo do eixo principal projetado
         e remove duplicatas (que orbitam o mesmo centro).
    """
    p_mean = pts.mean(axis=0)
    C = np.cov((pts - p_mean).T)
    _, eigvecs = np.linalg.eigh(C)
    axis = eigvecs[:, -1]
    proj_all = (pts - p_mean) @ axis
    p_min, p_max = float(proj_all.min()), float(proj_all.max())

    # Seeds uniformes ao longo do eixo principal
    margin = 0.5e-3
    seeds_proj = np.linspace(p_min + margin, p_max - margin, n_seeds)
    seeds = p_mean[None, :] + seeds_proj[:, None] * axis[None, :]

    for it in range(n_iter):
        # Calcular tangentes locais a partir das seeds atuais
        tangents = np.zeros_like(seeds)
        tangents[1:-1] = seeds[2:] - seeds[:-2]
        tangents[0] = seeds[1] - seeds[0]
        tangents[-1] = seeds[-1] - seeds[-2]
        tlen = np.linalg.norm(tangents, axis=1, keepdims=True)
        tangents = tangents / np.maximum(tlen, 1e-12)

        new_seeds = seeds.copy()
        for i in range(n_seeds):
            d = np.linalg.norm(pts - seeds[i], axis=1)
            near = d < r_search_m
            if near.sum() < 6:
                continue
            sub = pts[near]
            cen = sub.mean(axis=0)
            # Restringir movimento ao plano perpendicular ao tangente local
            delta = cen - seeds[i]
            delta_perp = delta - np.dot(delta, tangents[i]) * tangents[i]
            new_seeds[i] = seeds[i] + 0.7 * delta_perp
        seeds = new_seeds

    # Remover seeds redundantes (muito proximos): merge se distancia < 0.1 mm
    keep = [0]
    for i in range(1, len(seeds)):
        if np.linalg.norm(seeds[i] - seeds[keep[-1]]) > 0.1e-3:
            keep.append(i)
    return seeds[keep]


def smooth_centerline(cl: NDArray[np.float64], nz_out: int) -> NDArray[np.float64]:
    """Reamostragem uniforme por arc length usando interpolacao linear + suavizado
    Catmull-Rom (3 passes de smoothing). NumPy puro (sem scipy)."""
    # 1) Smoothing local (media movel ponderada de 5 pontos)
    cl_s = cl.copy()
    for _ in range(3):
        new = cl_s.copy()
        for i in range(2, len(cl_s) - 2):
            new[i] = (
                0.1 * cl_s[i - 2] + 0.2 * cl_s[i - 1]
                + 0.4 * cl_s[i]
                + 0.2 * cl_s[i + 1] + 0.1 * cl_s[i + 2]
            )
        cl_s = new

    # 2) Reamostragem uniforme por arc length
    d = np.linalg.norm(np.diff(cl_s, axis=0), axis=1)
    s = np.concatenate([[0.0], np.cumsum(d)])
    s_uni = np.linspace(0, s[-1], nz_out)
    out = np.zeros((nz_out, 3))
    for k in range(3):
        out[:, k] = np.interp(s_uni, s, cl_s[:, k])

    # 3) Mais 2 passes de smoothing apos resampling
    for _ in range(2):
        new = out.copy()
        for i in range(2, len(out) - 2):
            new[i] = (
                0.1 * out[i - 2] + 0.2 * out[i - 1]
                + 0.4 * out[i]
                + 0.2 * out[i + 1] + 0.1 * out[i + 2]
            )
        out = new
    return out


# ---------- 3) Parallel-transport frames ----------------------------------
def parallel_transport_frames(
    centerline: NDArray[np.float64],
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """Retorna (T, N, B) em cada ponto da centerline. N e B sao transportadas
    paralelamente ao longo da curva (rotacao minima entre tangentes
    consecutivas), evitando o flip de Frenet-Serret em pontos de inflexao."""
    nz = len(centerline)
    T = np.zeros_like(centerline)
    # tangente por diferencas centradas
    T[1:-1] = centerline[2:] - centerline[:-2]
    T[0] = centerline[1] - centerline[0]
    T[-1] = centerline[-1] - centerline[-2]
    T /= np.linalg.norm(T, axis=1, keepdims=True)

    N = np.zeros_like(centerline)
    B = np.zeros_like(centerline)
    # vetor de referencia inicial perpendicular a T[0]
    ref = np.array([1.0, 0.0, 0.0]) if abs(T[0, 0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    N[0] = ref - np.dot(ref, T[0]) * T[0]
    N[0] /= np.linalg.norm(N[0])
    B[0] = np.cross(T[0], N[0])

    for i in range(1, nz):
        # rotacao minima T[i-1] -> T[i]
        t0, t1 = T[i - 1], T[i]
        axis = np.cross(t0, t1)
        sn = np.linalg.norm(axis)
        if sn < 1e-9:
            N[i] = N[i - 1]
            B[i] = B[i - 1]
            continue
        axis /= sn
        cs = np.clip(np.dot(t0, t1), -1, 1)
        ang = np.arccos(cs)
        # rotaciona N e B pelo angulo ang em torno do axis
        N[i] = _rot(N[i - 1], axis, ang)
        B[i] = _rot(B[i - 1], axis, ang)
    return T, N, B


def _rot(v: NDArray[np.float64], axis: NDArray[np.float64], ang: float) -> NDArray[np.float64]:
    c, s = np.cos(ang), np.sin(ang)
    return v * c + np.cross(axis, v) * s + axis * (np.dot(axis, v)) * (1 - c)


# ---------- 4) Section geometry ------------------------------------------
def lumen_section_points(R: float, ncore: int, ncirc: int, nrad: int) -> NDArray[np.float64]:
    """O-grid no plano (eta1, eta2) — coords locais 2D na secao transversal.
    Retorna pontos em ordem [core_grid (ncore+1)^2, anular (nrad+1)*ncirc]."""
    pts: list[tuple[float, float]] = []

    # Core: quadrado [-R_core, R_core]^2 com ncore+1 nos por lado
    R_core = R / np.sqrt(2.0)  # inscrito no disco de raio R/sqrt(2)
    rc = R / 2.0  # raio do contorno do core (anular comeca aqui)
    R_core = rc / np.sqrt(2.0)  # quadrado interno cujo circunscrito tem raio rc
    for j in range(ncore + 1):
        for i in range(ncore + 1):
            x = -R_core + (2 * R_core) * i / ncore
            y = -R_core + (2 * R_core) * j / ncore
            pts.append((x, y))

    # Aneis externos: ncirc setores (theta = 0 .. 2pi) x (nrad+1) anéis radiais
    # Raios: r_k = rc + (R - rc) * k / nrad,  k = 0..nrad
    # Mas o ANEL k=0 deve coincidir com a borda do core via projecao radial
    # (mapping square-to-circle ao raio rc).
    thetas = np.linspace(0, 2 * np.pi, ncirc, endpoint=False)
    for k in range(nrad + 1):
        r = rc + (R - rc) * k / nrad
        if k == 0:
            # k=0: contorno do core projetado radialmente -- nao adicionar pontos
            # novos, ja existem nos cantos do quadrado central.
            # Para simplicidade, SIM, criamos pontos no circulo de raio rc.
            # Isso significa que o O-grid tem uma transicao non-conforme entre
            # quadrado e circulo, o que NAO funciona em hex puro. SOLUCAO:
            # estender o core ate o anular com mapping radial -- gerar pontos
            # do anular tambem em k=0 e MERGEAR com pontos do core via mapping.
            for th in thetas:
                pts.append((r * np.cos(th), r * np.sin(th)))
        else:
            for th in thetas:
                pts.append((r * np.cos(th), r * np.sin(th)))
    return np.array(pts)


def annulus_section_points(R_in: float, R_out: float, ncirc: int, nrad: int) -> NDArray[np.float64]:
    """Setores polares puros em coords locais 2D."""
    thetas = np.linspace(0, 2 * np.pi, ncirc, endpoint=False)
    pts: list[tuple[float, float]] = []
    for k in range(nrad + 1):
        r = R_in + (R_out - R_in) * k / nrad
        for th in thetas:
            pts.append((r * np.cos(th), r * np.sin(th)))
    return np.array(pts)


# ---------- 5) Build 3D point cloud and explicit face/owner/neighbour ----
@dataclass
class FoamMesh:
    """Estrutura para polyMesh OpenFOAM: pontos + faces ordenadas
    (internal first, depois patches), owner/neighbour."""
    points: NDArray[np.float64]                # (NP, 3)
    n_cells: int
    faces: list[tuple[int, int, int, int]]    # ordem: internal + patch0 + patch1 + ...
    owner: list[int]                           # len == nFaces
    neighbour: list[int]                       # len == nInternalFaces
    patches: list[tuple[str, int, int]]       # (name, startFace, nFaces)


def _orient_face(
    face: tuple[int, int, int, int],
    expected_normal: NDArray[np.float64],
    points: NDArray[np.float64],
) -> tuple[int, int, int, int]:
    """Reordena vertices de uma face quad para que (p1-p0) x (p2-p0) tenha
    componente positiva ao longo de expected_normal."""
    p0, p1, p2, p3 = face
    P0, P1, P2 = points[p0], points[p1], points[p2]
    n = np.cross(P1 - P0, P2 - P0)
    if np.dot(n, expected_normal) >= 0:
        return face
    return (p0, p3, p2, p1)


def build_annulus_foam_mesh(
    centerline: NDArray[np.float64],
    N: NDArray[np.float64],
    B: NDArray[np.float64],
    R_in: float,
    R_out: float,
    ncirc: int,
    nrad: int,
    patch_names: dict[str, str],
) -> FoamMesh:
    """Constroi polyMesh anular extrudada com faces, owner, neighbour
    explicitamente listados na ordem correta (internal first, boundary depois,
    com orientacao tal que normal sai do owner).

    patch_names mapeia chaves canonicas para os nomes finais das patches:
      'cap_back'  -> nome do cap na secao 0
      'cap_front' -> nome do cap na secao nz-1
      'r_inner'   -> nome da sup. interna (k=0)
      'r_outer'   -> nome da sup. externa (k=nrad)
    """
    nz = len(centerline)
    n_per_section = ncirc * (nrad + 1)

    # ----- pontos -----
    sec_template = annulus_section_points(R_in, R_out, ncirc, nrad)  # (npts_sec, 2)
    points = np.zeros((nz * n_per_section, 3))
    for iz in range(nz):
        P = (
            centerline[iz]
            + sec_template[:, 0:1] * N[iz]
            + sec_template[:, 1:2] * B[iz]
        )
        points[iz * n_per_section:(iz + 1) * n_per_section] = P

    def pid(iz: int, k: int, t: int) -> int:
        return iz * n_per_section + k * ncirc + (t % ncirc)

    # ----- cell id -----
    nc_kt = nrad * ncirc
    n_cells = (nz - 1) * nc_kt

    def cid(iz: int, k: int, t: int) -> int:
        return iz * nc_kt + k * ncirc + (t % ncirc)

    # Vetores tangentes locais para usar como "expected normal" das faces
    # axiais. Calcular tangente forward na secao iz: T[iz] = cl[iz+1] - cl[iz]
    T_fwd = np.zeros_like(centerline)
    T_fwd[:-1] = centerline[1:] - centerline[:-1]
    T_fwd[-1] = T_fwd[-2]
    T_fwd /= np.maximum(np.linalg.norm(T_fwd, axis=1, keepdims=True), 1e-12)

    # Centroide da seccao (para normal radial = (pt_face - centro_secao))
    sec_centroid = centerline  # secao centrada na centerline

    # ----- faces internas -----
    # Categoria A: AXIAIS entre (iz, k, t) e (iz+1, k, t).
    #   4 pontos na secao iz+1 (mas vista de baixo, normal +T).
    #   Owner = cell com menor iz = (iz, k, t).
    #   Normal aponta do owner para neighbour = +T.
    #   Ordem dos pontos: CCW visto de +T no plano da secao iz+1.
    #   Em coords (theta, k): comecando em (theta_t, k), CCW visto de +T:
    #     theta_t,k -> theta_{t+1},k -> theta_{t+1},k+1 -> theta_t,k+1
    #   (CCW porque theta cresce no sentido N x B = +T pela mao direita)
    #
    # Categoria B: RADIAIS entre (iz, k, t) e (iz, k+1, t).
    #   Face em raio r_{k+1}, setor theta in [theta_t, theta_{t+1}], comprimento
    #   axial de sec iz a sec iz+1. Normal aponta +radial (de k para k+1).
    #   Owner = (iz, k, t). 4 pontos:
    #     (iz, k+1, t) -> (iz+1, k+1, t) -> (iz+1, k+1, t+1) -> (iz, k+1, t+1)
    #   Verificacao mao direita: (p1-p0) = +T*dz; (p2-p1) = +theta*ds_theta;
    #     cross = +radial. ✓
    #
    # Categoria C: ANGULARES entre (iz, k, t) e (iz, k, t+1).
    #   Face em theta = theta_{t+1}, anel radial [r_k, r_{k+1}], axial [iz, iz+1].
    #   Normal aponta +theta (CCW). Owner = (iz, k, t). 4 pontos:
    #     (iz, k, t+1) -> (iz, k+1, t+1) -> (iz+1, k+1, t+1) -> (iz+1, k, t+1)
    #   Verificacao: (p1-p0)=+radial; (p2-p1)=+T; cross = +theta. ✓
    faces: list[tuple[int, int, int, int]] = []
    owner: list[int] = []
    neighbour: list[int] = []

    def face_center(p0: int, p1: int, p2: int, p3: int) -> NDArray[np.float64]:
        return 0.25 * (points[p0] + points[p1] + points[p2] + points[p3])

    # AXIAIS (entre iz e iz+1, mesmo (k,t)) -- normal aponta de iz para iz+1
    for iz in range(nz - 2):
        for k in range(nrad):
            for t in range(ncirc):
                raw = (
                    pid(iz + 1, k, t),
                    pid(iz + 1, k, t + 1),
                    pid(iz + 1, k + 1, t + 1),
                    pid(iz + 1, k + 1, t),
                )
                expected_n = T_fwd[iz]  # +T
                f = _orient_face(raw, expected_n, points)
                faces.append(f)
                owner.append(cid(iz, k, t))
                neighbour.append(cid(iz + 1, k, t))

    # RADIAIS (entre k e k+1, mesmo (iz,t)) -- normal aponta radial out (de k para k+1)
    for iz in range(nz - 1):
        for k in range(nrad - 1):
            for t in range(ncirc):
                raw = (
                    pid(iz, k + 1, t),
                    pid(iz + 1, k + 1, t),
                    pid(iz + 1, k + 1, t + 1),
                    pid(iz, k + 1, t + 1),
                )
                fc = face_center(*raw)
                # cl_avg na metade axial da face
                cl_avg = 0.5 * (sec_centroid[iz] + sec_centroid[iz + 1])
                expected_n = fc - cl_avg  # radial out (face_center - axis)
                # remover componente axial (projetar no plano da seccao media)
                t_avg = 0.5 * (T_fwd[iz] + T_fwd[iz + 1])
                t_avg /= np.linalg.norm(t_avg) + 1e-12
                expected_n = expected_n - np.dot(expected_n, t_avg) * t_avg
                f = _orient_face(raw, expected_n, points)
                faces.append(f)
                owner.append(cid(iz, k, t))
                neighbour.append(cid(iz, k + 1, t))

    # ANGULARES (entre t e t+1, mesmo (iz,k)) -- normal aponta CCW em torno do eixo
    for iz in range(nz - 1):
        for k in range(nrad):
            for t in range(ncirc):
                t1 = (t + 1) % ncirc
                raw = (
                    pid(iz, k, t + 1),
                    pid(iz, k + 1, t + 1),
                    pid(iz + 1, k + 1, t + 1),
                    pid(iz + 1, k, t + 1),
                )
                fc = face_center(*raw)
                cl_avg = 0.5 * (sec_centroid[iz] + sec_centroid[iz + 1])
                radial = fc - cl_avg
                t_avg = 0.5 * (T_fwd[iz] + T_fwd[iz + 1])
                t_avg /= np.linalg.norm(t_avg) + 1e-12
                radial = radial - np.dot(radial, t_avg) * t_avg
                radial_n = radial / (np.linalg.norm(radial) + 1e-12)
                # tangencial CCW (visto de +T) = t_avg x radial_n
                expected_n = np.cross(t_avg, radial_n)
                f = _orient_face(raw, expected_n, points)
                faces.append(f)
                owner.append(cid(iz, k, t))
                neighbour.append(cid(iz, k, t1))

    n_internal = len(faces)

    # ----- faces boundary -----
    # Normal aponta para FORA da cell owner.
    patch_order = ["cap_back", "cap_front", "r_inner", "r_outer"]
    bnd_face_lists: dict[str, list[tuple[tuple[int, int, int, int], int]]] = {p: [] for p in patch_order}

    # cap_back: secao 0, normal -T
    for k in range(nrad):
        for t in range(ncirc):
            raw = (
                pid(0, k, t),
                pid(0, k + 1, t),
                pid(0, k + 1, t + 1),
                pid(0, k, t + 1),
            )
            expected_n = -T_fwd[0]
            f = _orient_face(raw, expected_n, points)
            bnd_face_lists["cap_back"].append((f, cid(0, k, t)))

    # cap_front: secao nz-1, normal +T
    for k in range(nrad):
        for t in range(ncirc):
            raw = (
                pid(nz - 1, k, t),
                pid(nz - 1, k, t + 1),
                pid(nz - 1, k + 1, t + 1),
                pid(nz - 1, k + 1, t),
            )
            expected_n = T_fwd[nz - 2]
            f = _orient_face(raw, expected_n, points)
            bnd_face_lists["cap_front"].append((f, cid(nz - 2, k, t)))

    # r_inner: k=0, normal -radial (saindo da cell para o eixo)
    for iz in range(nz - 1):
        for t in range(ncirc):
            raw = (
                pid(iz, 0, t),
                pid(iz, 0, t + 1),
                pid(iz + 1, 0, t + 1),
                pid(iz + 1, 0, t),
            )
            fc = face_center(*raw)
            cl_avg = 0.5 * (sec_centroid[iz] + sec_centroid[iz + 1])
            t_avg = 0.5 * (T_fwd[iz] + T_fwd[iz + 1])
            t_avg /= np.linalg.norm(t_avg) + 1e-12
            radial_out = fc - cl_avg
            radial_out = radial_out - np.dot(radial_out, t_avg) * t_avg
            expected_n = -radial_out  # saindo para o eixo
            f = _orient_face(raw, expected_n, points)
            bnd_face_lists["r_inner"].append((f, cid(iz, 0, t)))

    # r_outer: k=nrad, normal +radial
    for iz in range(nz - 1):
        for t in range(ncirc):
            raw = (
                pid(iz, nrad, t),
                pid(iz + 1, nrad, t),
                pid(iz + 1, nrad, t + 1),
                pid(iz, nrad, t + 1),
            )
            fc = face_center(*raw)
            cl_avg = 0.5 * (sec_centroid[iz] + sec_centroid[iz + 1])
            t_avg = 0.5 * (T_fwd[iz] + T_fwd[iz + 1])
            t_avg /= np.linalg.norm(t_avg) + 1e-12
            radial_out = fc - cl_avg
            radial_out = radial_out - np.dot(radial_out, t_avg) * t_avg
            expected_n = radial_out
            f = _orient_face(raw, expected_n, points)
            bnd_face_lists["r_outer"].append((f, cid(iz, nrad - 1, t)))

    # Adicionar boundary faces a lista global em ordem de patch
    patches_out: list[tuple[str, int, int]] = []
    for pkey in patch_order:
        pname = patch_names[pkey]
        start = len(faces)
        for (f, ow) in bnd_face_lists[pkey]:
            faces.append(f)
            owner.append(ow)
        patches_out.append((pname, start, len(faces) - start))

    return FoamMesh(
        points=points,
        n_cells=n_cells,
        faces=faces,
        owner=owner,
        neighbour=neighbour,
        patches=patches_out,
    )


def build_lumen_foam_mesh(
    centerline: NDArray[np.float64],
    N: NDArray[np.float64],
    B: NDArray[np.float64],
    R: float,
    ncirc: int,
    nrad: int,
    patch_names: dict[str, str],
) -> FoamMesh:
    """Lumen como cilindro polar puro com 'axis' a r=R*0.05 (evita singularidade
    no eixo, com erro de volume < 1%)."""
    return build_annulus_foam_mesh(
        centerline, N, B, R * 0.05, R, ncirc, nrad, patch_names
    )


# ---------- 6) polyMesh writer -------------------------------------------
# OpenFOAM polyMesh format ASCII v2.0
# Necessario: points, faces, owner, neighbour, boundary
# Construcao de faces (todas) a partir das cells hex e bnd_faces.

def _foam_header(obj_class: str, obj_name: str, note: str = "") -> str:
    return (
        "FoamFile\n{\n"
        "    version     2.0;\n"
        "    format      ascii;\n"
        f"    class       {obj_class};\n"
        f"    location    \"constant/polyMesh\";\n"
        f"    object      {obj_name};\n"
        f"    note        \"{note}\";\n"
        "}\n"
    )


def write_polymesh(mesh: FoamMesh, out_dir: Path, patch_types: dict[str, str]) -> dict:
    """Escreve points, faces, owner, neighbour, boundary diretamente a partir
    do FoamMesh construido. patch_types mapeia nome_patch -> tipo OpenFOAM."""
    out_dir.mkdir(parents=True, exist_ok=True)
    pts = mesh.points
    n_pts = len(pts)
    n_cells = mesh.n_cells
    n_faces = len(mesh.faces)
    n_internal = len(mesh.neighbour)

    # 1) Reordenar faces internas para satisfazer "upper triangular addressing":
    #    para faces internas, owner < neighbour, e a lista esta ordenada por
    #    (owner asc, neighbour asc).
    new_faces: list[tuple[int, int, int, int]] = []
    new_owner: list[int] = []
    new_neigh: list[int] = []
    internal_records = []
    for fi in range(n_internal):
        o = mesh.owner[fi]
        nb = mesh.neighbour[fi]
        f = mesh.faces[fi]
        if o > nb:
            o, nb = nb, o
            f = (f[0], f[3], f[2], f[1])  # inverte winding
        internal_records.append((o, nb, f))
    internal_records.sort(key=lambda r: (r[0], r[1]))
    for o, nb, f in internal_records:
        new_faces.append(f)
        new_owner.append(o)
        new_neigh.append(nb)
    # boundary faces: manter na ordem dada (por patch)
    patches_new: list[tuple[str, int, int]] = []
    cur = len(new_faces)
    bnd_start_orig = n_internal
    for name, start, count in mesh.patches:
        # copia faces & owner
        patches_new.append((name, cur, count))
        for j in range(count):
            new_faces.append(mesh.faces[start + j])
            new_owner.append(mesh.owner[start + j])
        cur += count

    # 2) Escrever points
    with (out_dir / "points").open("w") as f:
        f.write(_foam_header("vectorField", "points"))
        f.write(f"{n_pts}\n(\n")
        for p in pts:
            f.write(f"({p[0]:.10g} {p[1]:.10g} {p[2]:.10g})\n")
        f.write(")\n")

    # 3) Escrever faces
    with (out_dir / "faces").open("w") as f:
        f.write(_foam_header("faceList", "faces"))
        f.write(f"{n_faces}\n(\n")
        for face in new_faces:
            f.write(f"4({face[0]} {face[1]} {face[2]} {face[3]})\n")
        f.write(")\n")

    # 4) Escrever owner
    note = f"nPoints:{n_pts} nCells:{n_cells} nFaces:{n_faces} nInternalFaces:{n_internal}"
    with (out_dir / "owner").open("w") as f:
        f.write(_foam_header("labelList", "owner", note))
        f.write(f"{n_faces}\n(\n")
        for o in new_owner:
            f.write(f"{o}\n")
        f.write(")\n")

    # 5) Escrever neighbour
    with (out_dir / "neighbour").open("w") as f:
        f.write(_foam_header("labelList", "neighbour", note))
        f.write(f"{n_internal}\n(\n")
        for nb in new_neigh:
            f.write(f"{nb}\n")
        f.write(")\n")

    # 6) Escrever boundary
    with (out_dir / "boundary").open("w") as f:
        f.write(_foam_header("polyBoundaryMesh", "boundary"))
        f.write(f"{len(patches_new)}\n(\n")
        for name, start, count in patches_new:
            ptype = patch_types.get(name, "wall")
            f.write(f"    {name}\n    {{\n")
            f.write(f"        type            {ptype};\n")
            in_grp = ptype if ptype == "wall" else ptype
            f.write(f"        inGroups        1({in_grp});\n")
            f.write(f"        nFaces          {count};\n")
            f.write(f"        startFace       {start};\n")
            f.write(f"    }}\n")
        f.write(")\n")

    return {
        "nPoints": n_pts,
        "nCells": n_cells,
        "nFaces": n_faces,
        "nInternalFaces": n_internal,
        "patches": [(name, start, count) for name, start, count in patches_new],
    }


# ---------- main ----------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nz", type=int, default=NZ)
    ap.add_argument("--ncirc", type=int, default=NCIRC)
    ap.add_argument("--nrad-lumen", type=int, default=NRAD_LUMEN)
    ap.add_argument("--nrad-wall", type=int, default=NRAD_WALL)
    args = ap.parse_args()

    if SRC_STL is None or OUT_CASE is None:
        raise FileNotFoundError(
            "STL fonte ou caso de saida nao encontrado. "
            "Defina ARTOPH_SRC_STL / ARTOPH_OUT_CASE ou use brunaStuff/build_teste_geom.py."
        )
    print(f"Lendo STL: {SRC_STL}")
    pts = read_ascii_stl_vertices(SRC_STL)
    print(f"  {len(pts)} vertices (com repeticao)")

    print("Extraindo centerline (seeds-PCA + relax. iterativa)...")
    cl_raw = extract_centerline_marching(pts, r_search_m=1.5e-3, n_seeds=100, n_iter=8)
    print(f"  centerline raw: {len(cl_raw)} pts")
    print(f"  bounds: {cl_raw.min(axis=0)*1e3} .. {cl_raw.max(axis=0)*1e3} mm")
    arc = float(np.sum(np.linalg.norm(np.diff(cl_raw, axis=0), axis=1)))
    print(f"  comprimento de arco: {arc*1e3:.2f} mm")

    print(f"Suavizando + reamostrando para {args.nz} secoes...")
    cl = smooth_centerline(cl_raw, nz_out=args.nz)
    print(f"  comprimento de arco total: {np.sum(np.linalg.norm(np.diff(cl, axis=0), axis=1))*1e3:.2f} mm")

    print("Calculando frames com parallel transport...")
    T, N, B = parallel_transport_frames(cl)
    _ = T  # T usado implicitamente pelo parallel transport, nao precisa aqui

    # ---- FLUIDO (lumen) ----
    print(f"Construindo polyMesh LUMEN (R={R_LUMEN_M*1e3:.2f} mm, "
          f"ncirc={args.ncirc}, nrad={args.nrad_lumen})...")
    mesh_fluid = build_lumen_foam_mesh(
        cl, N, B, R_LUMEN_M, args.ncirc, args.nrad_lumen,
        patch_names={
            "cap_back":  "inlet",
            "cap_front": "outlet",
            "r_inner":   "axis",      # parede virtual no eixo (R=R*0.05)
            "r_outer":   "wall",      # interface FSI
        },
    )
    pm_dir_f = OUT_CASE / "fluid" / "constant" / "polyMesh"
    if pm_dir_f.exists():
        shutil.rmtree(pm_dir_f)
    stats_f = write_polymesh(
        mesh_fluid, pm_dir_f,
        patch_types={"inlet": "patch", "outlet": "patch", "wall": "wall", "axis": "wall"},
    )
    print(f"  FLUID: {stats_f['nPoints']} pts, {stats_f['nCells']} cells, "
          f"{stats_f['nFaces']} faces ({stats_f['nInternalFaces']} internal)")
    for name, start, count in stats_f["patches"]:
        print(f"    patch {name}: start={start} nFaces={count}")

    # ---- SOLIDO (annulus) ----
    print(f"\nConstruindo polyMesh ANNULUS (R_in={R_LUMEN_M*1e3:.2f} mm, "
          f"R_out={(R_LUMEN_M+H_WALL_M)*1e3:.2f} mm, ncirc={args.ncirc}, "
          f"nrad={args.nrad_wall})...")
    mesh_solid = build_annulus_foam_mesh(
        cl, N, B, R_LUMEN_M, R_LUMEN_M + H_WALL_M, args.ncirc, args.nrad_wall,
        patch_names={
            "cap_back":  "inner_cap_back",
            "cap_front": "inner_cap_front",
            "r_inner":   "lumen",         # interface FSI com fluido
            "r_outer":   "arteria_externa",
        },
    )
    pm_dir_s = OUT_CASE / "solid" / "constant" / "polyMesh"
    if pm_dir_s.exists():
        shutil.rmtree(pm_dir_s)
    stats_s = write_polymesh(
        mesh_solid, pm_dir_s,
        patch_types={
            "inner_cap_back": "wall", "inner_cap_front": "wall",
            "lumen": "wall", "arteria_externa": "wall",
        },
    )
    print(f"  SOLID: {stats_s['nPoints']} pts, {stats_s['nCells']} cells, "
          f"{stats_s['nFaces']} faces ({stats_s['nInternalFaces']} internal)")
    for name, start, count in stats_s["patches"]:
        print(f"    patch {name}: start={start} nFaces={count}")

    print("\nOK. polyMesh estruturadas extrudadas escritas para ambos os solvers.")


if __name__ == "__main__":
    main()
