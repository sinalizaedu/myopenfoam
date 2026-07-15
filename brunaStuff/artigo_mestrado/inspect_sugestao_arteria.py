#!/usr/bin/env python3
"""Compara visualmente a artéria sólida no caso `sugestao` com a do
`ao-mestrado`. Renderiza:
  - artery.stl (anatomica, lida do triSurface)
  - solid polyMesh extrudada (do constant/polyMesh)
  - nervo+ONS (do sugestao para contexto)

Imagem salva em brunaStuff/inspect_sugestao_arteria.png.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


REPO = Path(__file__).resolve().parents[1]


def read_stl_tris(fp: Path) -> np.ndarray:
    """Le STL ASCII e retorna (N, 3, 3) array de triangulos."""
    tris = []
    cur = []
    with fp.open() as f:
        for ln in f:
            m = re.match(r"\s*vertex\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)", ln)
            if m:
                cur.append([float(m.group(i)) for i in (1, 2, 3)])
                if len(cur) == 3:
                    tris.append(cur)
                    cur = []
    return np.array(tris)


def read_polymesh_points(pm: Path) -> np.ndarray:
    pts = []
    with (pm / "points").open() as f:
        in_list = False
        for ln in f:
            ls = ln.strip()
            if not in_list:
                if ls.startswith("("):
                    in_list = True
                continue
            if ls.startswith(")"):
                break
            m = re.match(r"\(([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\)", ls)
            if m:
                pts.append([float(m.group(i)) for i in (1, 2, 3)])
    return np.array(pts)


def read_polymesh_boundary_patch_points(pm: Path, patch: str) -> np.ndarray:
    """Le pontos das faces do patch <patch>."""
    bnd_txt = (pm / "boundary").read_text()
    m = re.search(
        rf"\b{re.escape(patch)}\s*\{{[^{{}}]*?nFaces\s+(\d+)[^{{}}]*?startFace\s+(\d+)",
        bnd_txt, re.DOTALL,
    )
    if not m:
        return np.empty((0, 3))
    nF = int(m.group(1))
    sF = int(m.group(2))

    faces = []
    with (pm / "faces").open() as f:
        in_list = False
        idx = 0
        for ln in f:
            ls = ln.strip()
            if not in_list:
                if ls.startswith("("):
                    in_list = True
                continue
            if ls.startswith(")"):
                break
            mm = re.match(r"\d+\(([\d ]+)\)", ls)
            if mm:
                if sF <= idx < sF + nF:
                    faces.append([int(x) for x in mm.group(1).split()])
                idx += 1

    pts = read_polymesh_points(pm)
    coords = []
    for face in faces:
        coords.append(pts[face])
    return coords  # type: ignore[return-value]


def main() -> None:
    # === Lê STL anatomica (sugestao) ===
    stl_sug = REPO / "cases/sugestao/constant/triSurface/artery.stl"
    stl_ao = REPO / "cases/ao-mestrado/constant/triSurface/artery.stl"
    pm_sug_full = REPO / "cases/sugestao/solid/constant/polyMesh"
    pm_sug_arteria = (
        REPO / "cases/sugestao/solid/staging/arteria/constant/polyMesh"
    )
    pm_ao_arteria = REPO / "cases/ao-mestrado/solid/constant/polyMesh"

    print(f"[inspect] STL sugestao: {stl_sug}")
    print(f"[inspect] STL ao-mestrado: {stl_ao}")
    print(f"[inspect] PolyMesh full sugestao (depois merge+baffles): {pm_sug_full}")
    print(f"[inspect] PolyMesh arteria sugestao (staging): {pm_sug_arteria}")
    print(f"[inspect] PolyMesh ao-mestrado: {pm_ao_arteria}")

    fig = plt.figure(figsize=(15, 10))

    # Painel 1: STL artery.stl do sugestao
    ax1 = fig.add_subplot(2, 3, 1, projection="3d")
    if stl_sug.exists():
        tris = read_stl_tris(stl_sug)
        coll = Poly3DCollection(tris, alpha=0.6, facecolor="tomato",
                                edgecolor="black", linewidth=0.05)
        ax1.add_collection3d(coll)
        all_v = tris.reshape(-1, 3)
        ax1.set_xlim(all_v[:, 0].min(), all_v[:, 0].max())
        ax1.set_ylim(all_v[:, 1].min(), all_v[:, 1].max())
        ax1.set_zlim(all_v[:, 2].min(), all_v[:, 2].max())
        ax1.set_title(f"(a) STL artery.stl em sugestao\n"
                      f"({len(tris)} tris)", fontsize=10)
        ax1.set_xlabel("x"); ax1.set_ylabel("y"); ax1.set_zlabel("z")

    # Painel 2: STL artery.stl do ao-mestrado
    ax2 = fig.add_subplot(2, 3, 2, projection="3d")
    if stl_ao.exists():
        tris = read_stl_tris(stl_ao)
        coll = Poly3DCollection(tris, alpha=0.6, facecolor="cornflowerblue",
                                edgecolor="black", linewidth=0.05)
        ax2.add_collection3d(coll)
        all_v = tris.reshape(-1, 3)
        ax2.set_xlim(all_v[:, 0].min(), all_v[:, 0].max())
        ax2.set_ylim(all_v[:, 1].min(), all_v[:, 1].max())
        ax2.set_zlim(all_v[:, 2].min(), all_v[:, 2].max())
        ax2.set_title(f"(b) STL artery.stl em ao-mestrado\n"
                      f"({len(tris)} tris)", fontsize=10)
        ax2.set_xlabel("x"); ax2.set_ylabel("y"); ax2.set_zlabel("z")

    # Painel 3: ambos sobrepostos
    ax3 = fig.add_subplot(2, 3, 3, projection="3d")
    if stl_sug.exists() and stl_ao.exists():
        ts = read_stl_tris(stl_sug)
        ta = read_stl_tris(stl_ao)
        ax3.add_collection3d(Poly3DCollection(
            ts, alpha=0.4, facecolor="tomato", edgecolor="none"))
        ax3.add_collection3d(Poly3DCollection(
            ta, alpha=0.4, facecolor="cornflowerblue", edgecolor="none"))
        all_v = np.concatenate([ts.reshape(-1, 3), ta.reshape(-1, 3)])
        ax3.set_xlim(all_v[:, 0].min(), all_v[:, 0].max())
        ax3.set_ylim(all_v[:, 1].min(), all_v[:, 1].max())
        ax3.set_zlim(all_v[:, 2].min(), all_v[:, 2].max())
        ax3.set_title("(c) STLs sobrepostos\n"
                      "(vermelho=sugestao, azul=ao-mestrado)", fontsize=10)
        ax3.set_xlabel("x"); ax3.set_ylabel("y"); ax3.set_zlabel("z")

    # Painel 4: polyMesh staging arteria (sugestao) - patch arteria_externa
    ax4 = fig.add_subplot(2, 3, 4, projection="3d")
    if pm_sug_arteria.exists():
        try:
            faces = read_polymesh_boundary_patch_points(
                pm_sug_arteria, "arteria_externa")
            print(f"[inspect] sugestao staging arteria_externa: {len(faces)} faces")
            coll = Poly3DCollection(faces, alpha=0.6, facecolor="orange",
                                    edgecolor="black", linewidth=0.05)
            ax4.add_collection3d(coll)
            allp = np.concatenate([np.array(f) for f in faces])
            ax4.set_xlim(allp[:, 0].min(), allp[:, 0].max())
            ax4.set_ylim(allp[:, 1].min(), allp[:, 1].max())
            ax4.set_zlim(allp[:, 2].min(), allp[:, 2].max())
            ax4.set_title(f"(d) sugestao staging/arteria\n"
                          f"patch arteria_externa "
                          f"({len(faces)} faces)", fontsize=10)
        except Exception as e:
            ax4.text(0.5, 0.5, f"erro: {e}", ha="center", va="center")

    # Painel 5: polyMesh ao-mestrado - patch arteria_externa
    ax5 = fig.add_subplot(2, 3, 5, projection="3d")
    if pm_ao_arteria.exists():
        try:
            faces = read_polymesh_boundary_patch_points(
                pm_ao_arteria, "arteria_externa")
            print(f"[inspect] ao-mestrado arteria_externa: {len(faces)} faces")
            coll = Poly3DCollection(faces, alpha=0.6, facecolor="dodgerblue",
                                    edgecolor="black", linewidth=0.05)
            ax5.add_collection3d(coll)
            allp = np.concatenate([np.array(f) for f in faces])
            ax5.set_xlim(allp[:, 0].min(), allp[:, 0].max())
            ax5.set_ylim(allp[:, 1].min(), allp[:, 1].max())
            ax5.set_zlim(allp[:, 2].min(), allp[:, 2].max())
            ax5.set_title(f"(e) ao-mestrado solid mesh\n"
                          f"patch arteria_externa "
                          f"({len(faces)} faces)", fontsize=10)
        except Exception as e:
            ax5.text(0.5, 0.5, f"erro: {e}", ha="center", va="center")

    # Painel 6: arteria sugestao (extrudada) + STL overlay (sanity)
    ax6 = fig.add_subplot(2, 3, 6, projection="3d")
    if pm_sug_arteria.exists() and stl_sug.exists():
        try:
            faces = read_polymesh_boundary_patch_points(
                pm_sug_arteria, "arteria_externa")
            tris = read_stl_tris(stl_sug)
            ax6.add_collection3d(Poly3DCollection(
                tris, alpha=0.3, facecolor="tomato", edgecolor="none"))
            ax6.add_collection3d(Poly3DCollection(
                faces, alpha=0.6, facecolor="orange",
                edgecolor="black", linewidth=0.05))
            t_v = tris.reshape(-1, 3)
            f_v = np.concatenate([np.array(f) for f in faces])
            allp = np.concatenate([t_v, f_v])
            ax6.set_xlim(allp[:, 0].min(), allp[:, 0].max())
            ax6.set_ylim(allp[:, 1].min(), allp[:, 1].max())
            ax6.set_zlim(allp[:, 2].min(), allp[:, 2].max())
            ax6.set_title("(f) STL (transp) + polyMesh extrudada\n"
                          "(sugestao staging)", fontsize=10)
        except Exception as e:
            ax6.text(0.5, 0.5, f"erro: {e}", ha="center", va="center")

    plt.tight_layout()
    out = REPO / "brunaStuff/inspect_sugestao_arteria.png"
    plt.savefig(out, dpi=120)
    print(f"[inspect] PNG salvo: {out}")


if __name__ == "__main__":
    main()
