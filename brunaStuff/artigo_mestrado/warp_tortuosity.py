#!/usr/bin/env python3
"""
warp_tortuosity.py
==================
Aplica uma TORTUOSIDADE INICIAL (curvatura geometrica embutida) ao nervo+pia
de uma malha CalculiX .inp, in-place.

Motivacao (item 2 - "folga"/slack natural do nervo optico):
    O nervo optico saudavel NAO e um cilindro perfeitamente esticado; ele e
    mais longo que a distancia orbita->globo (folga ~8.4 mm). Na microgravidade,
    com o achatamento do globo, essa folga e exacerbada e atua como a
    imperfeicao geometrica que guia o nervo a serpentear dentro do espaco
    subaracnoide dilatado.

    Em vez de "semear" o modo de flambagem com uma carga pontual artificial
    (CLOAD +-15 mN na pia, como em on-caso-2), embutimos uma leve excentricidade
    senoidal na propria malha. O solver de Riks usa essa excentricidade natural
    como imperfeicao guia -> snap-through muito mais estavel e fisicamente
    motivado, sem perturbar quantitativamente a carga critica.

Geometria-alvo (malha 8 zonas com SAS solido):
    Desloca em X o nucleo nervo+pia (r <= --r-core) com amplitude plena, e faz
    a amplitude decair LINEARMENTE atraves do SAS ate ZERO na dura (r >= --r-dura).
    Assim:
      - nervo+pia "serpenteiam" rigidamente (folga/slack);
      - o SAS solido fluid-like absorve o deslocamento por cisalhamento suave
        (sem concentrar distorcao numa unica camada de elementos);
      - a dura (r >= r-dura) permanece RETA -> tubo pressurizado/ortotropico e
        os springs Winkler (ancorados na dura reta) ficam consistentes.

    Perfil axial de deslocamento:
        modo 2 (default): dx(z) = amp * sin(2*pi*z/L)   -> "S" antissimetrico
        modo 1          : dx(z) = amp * sin(  pi*z/L)   -> "C" simetrico
    Perfil radial (taper):
        f(r) = 1                          , r <= r_core
        f(r) = (r_dura - r)/(r_dura-r_core), r_core < r < r_dura
        f(r) = 0                          , r >= r_dura

    dx(z, r) = amp * sin(k*z) * f(r)

    Ambos os modos sao 0 em z=0 (engaste posterior, canal optico) e em z=L
    (juncao com a lamina cribrosa / globo) -> preserva a continuidade da malha
    nas interfaces.

Uso:
    python3 warp_tortuosity.py \\
        --mesh on-caso-2.2_mesh.inp \\
        --amp 1.5e-4 \\
        --length 30.0e-3 \\
        --r-core 1.55e-3 \\
        --r-dura 2.35e-3 \\
        --mode 2
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path


def radial_taper(r: float, r_core: float, r_dura: float) -> float:
    if r <= r_core:
        return 1.0
    if r >= r_dura:
        return 0.0
    return (r_dura - r) / (r_dura - r_core)


def axial_profile(z: float, length: float, k: float, profile: str) -> float:
    """Deslocamento lateral normalizado (pico ~1) ao longo de z."""
    if profile == "anterior":
        # curvatura concentrada perto do globo (z=L): reto no apice, "hook"
        # retrobulbar. sin(pi z/L) ancorado nas 2 pontas, ponderado por (z/L)^1.5.
        s = math.sin(math.pi * z / length) * (z / length) ** 1.5
        return s / 0.62  # normaliza p/ pico ~1 (max de sin*(.)^1.5 ~0.62)
    # default: senoide pura (modo/waves)
    return math.sin(k * z)


def warp_mesh(mesh_path: Path, amp: float, length: float,
              r_core: float, r_dura: float, mode: int,
              bend_all: bool = False, waves: float | None = None,
              profile: str = "sine") -> None:
    lines = mesh_path.read_text().splitlines()
    out: list[str] = []

    in_node_block = False
    n_core = 0      # nos do nucleo (nervo+pia) deslocados em amplitude plena
    n_taper = 0     # nos do SAS deslocados parcialmente
    n_all = 0       # nos deslocados no modo bend-all
    max_dx = 0.0

    n_half = waves if waves is not None else (2.0 if mode == 2 else 1.0)
    k = n_half * math.pi / length

    for line in lines:
        stripped = line.strip()

        if stripped.upper().startswith("*NODE"):
            in_node_block = True
            out.append(line)
            continue
        if in_node_block and stripped.startswith("*"):
            in_node_block = False
            out.append(line)
            continue

        if in_node_block and stripped and not stripped.startswith("**"):
            parts = [p.strip() for p in line.split(",")]
            if len(parts) == 4:
                nid = parts[0]
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                r = math.hypot(x, y)
                if 1e-9 < z < length - 1e-9:
                    g = axial_profile(z, length, k, profile)
                    if bend_all:
                        # bainha inteira ondula (nervo+pia+SAS+dura), como na RM:
                        # cada secao transversal translada rigidamente -> tubo
                        # tortuoso. Sem taper radial; dura acompanha.
                        dx = amp * g
                        x = x + dx
                        n_all += 1
                        if abs(dx) > max_dx:
                            max_dx = abs(dx)
                    elif r < r_dura - 1e-12:
                        # so' o nucleo nervo+pia flamba; dura fica reta (SANS)
                        f = radial_taper(r, r_core, r_dura)
                        dx = amp * g * f
                        x = x + dx
                        if r <= r_core:
                            n_core += 1
                        else:
                            n_taper += 1
                        if abs(dx) > max_dx:
                            max_dx = abs(dx)
                out.append(f"{nid:>8s}, {x: .8e}, {y: .8e}, {z: .8e}")
                continue

        out.append(line)

    mesh_path.write_text("\n".join(out) + "\n")
    if bend_all:
        print(f"[warp_tortuosity] BEND-ALL: bainha inteira ondula ({n_all} nos), "
              f"{n_half:.1f} meio-periodos.")
        print(f"[warp_tortuosity] amplitude pico = {max_dx * 1e3:.4f} mm "
              f"(amp nominal = {amp * 1e3:.4f} mm); dura ACOMPANHA (tortuosa).")
    else:
        shape = "S (modo 2, antissimetrico)" if mode == 2 else "C (modo 1, simetrico)"
        print(f"[warp_tortuosity] nucleo nervo+pia: {n_core} nos (amplitude plena); "
              f"SAS (taper): {n_taper} nos; perfil {shape}.")
        print(f"[warp_tortuosity] amplitude pico = {max_dx * 1e3:.4f} mm "
              f"(amp nominal = {amp * 1e3:.4f} mm); dura (r>={r_dura * 1e3:.2f} mm) reta.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mesh", required=True, type=Path,
                    help="Arquivo .inp da malha (bloco *NODE sera reescrito in-place)")
    ap.add_argument("--amp", type=float, default=1.5e-4,
                    help="Amplitude pico da curvatura inicial em metros (default 1.5e-4 = 0.15 mm, "
                         "~10%% do raio do nervo: imperfeicao guia, nao perturba P_cr)")
    ap.add_argument("--length", type=float, default=30.0e-3,
                    help="Comprimento do nervo em metros (z em [0, L]) (default 30e-3)")
    ap.add_argument("--r-core", type=float, default=1.55e-3,
                    help="Raio do nucleo nervo+pia (amplitude plena ate aqui) (default 1.55e-3 = pia outer)")
    ap.add_argument("--r-dura", type=float, default=2.35e-3,
                    help="Raio interno da dura (amplitude -> 0 aqui; dura fica reta) (default 2.35e-3)")
    ap.add_argument("--mode", type=int, default=2, choices=[1, 2],
                    help="Modo de flambagem guia: 2=S antissimetrico (default, casa com "
                         "on-caso-2), 1=C simetrico")
    ap.add_argument("--bend-all", action="store_true",
                    help="Curva a BAINHA INTEIRA (nervo+pia+SAS+dura) ao longo de uma "
                         "linha de centro tortuosa, como na RM (tortuosidade anatomica de "
                         "repouso). Sem taper; a dura acompanha. Use p/ geometria realista; "
                         "para o mecanismo SANS (dura reta + nucleo flamba) NAO use.")
    ap.add_argument("--waves", type=float, default=None,
                    help="Numero de meio-periodos senoidais ao longo de L (sobrepoe --mode). "
                         "Ex: 2=um 'S' completo, 3=uma onda e meia, 4=duas ondas.")
    ap.add_argument("--profile", default="sine", choices=["sine", "anterior"],
                    help="Perfil axial da curvatura: 'sine' (senoide pura, default) ou "
                         "'anterior' (curvatura concentrada perto do globo z=L, reto no "
                         "apice -> 'hook' retrobulbar).")
    args = ap.parse_args()

    warp_mesh(args.mesh, args.amp, args.length, args.r_core, args.r_dura, args.mode,
              bend_all=args.bend_all, waves=args.waves, profile=args.profile)


if __name__ == "__main__":
    main()
