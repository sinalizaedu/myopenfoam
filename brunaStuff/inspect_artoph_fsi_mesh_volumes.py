#!/usr/bin/env python3
"""
Plot volumetrico dos dominios FSI gerados (apos as correcoes 2026-05-23):
  - fluido: lumen real (interior de artery_inner.stl), volume ~5.3e-8 m3
  - solido: arteria cheia (interior de artery_outer.stl), volume ~9.6e-8 m3

Amostragem dos pontos das malhas via OpenFOAM polyMesh/points (ASCII).
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parents[1]
CASE_HOST = REPO / "cases" / "artoph-fsi-curva-mestrado"
CASE_DOCKER = "/simulation/artoph-fsi-curva-mestrado"
CONTAINER = "myopenfoam-fsi-run-e725dcbcdf70"


def read_points_from_docker(side: str, max_points: int = 30000) -> np.ndarray:
    """Le constant/polyMesh/points (formato OpenFOAM ASCII binary-fallback)."""
    path = f"{CASE_DOCKER}/{side}/constant/polyMesh/points"
    out = subprocess.check_output([
        "docker", "exec", CONTAINER, "bash", "-lc",
        f"head -c 200 {path} | tr -d '\\0' | head -1; echo '---'; "
        f"awk '/^\\(/{{p=1;next}}/^\\)/{{exit}}p' {path}"
    ], text=True, errors="ignore")
    txt = out.split("---", 1)[-1]
    rx = re.compile(r"\(\s*(-?[\d.eE+\-]+)\s+(-?[\d.eE+\-]+)\s+(-?[\d.eE+\-]+)\s*\)")
    pts = [tuple(map(float, m.groups())) for m in rx.finditer(txt)]
    arr = np.array(pts)
    if len(arr) > max_points:
        idx = np.random.default_rng(0).choice(len(arr), max_points, replace=False)
        arr = arr[idx]
    return arr


def main() -> None:
    print("=" * 72)
    print("VISUALIZACAO POS-FIX: dominios FSI artoph-fsi-curva-mestrado")
    print("=" * 72)

    pts_f = read_points_from_docker("fluid", max_points=20000)
    pts_s = read_points_from_docker("solid", max_points=20000)
    print(f"\nPontos do fluido (amostra): {len(pts_f)}")
    print(f"  bbox: {pts_f.min(axis=0)*1e3} .. {pts_f.max(axis=0)*1e3} mm")
    print(f"Pontos do solido (amostra): {len(pts_s)}")
    print(f"  bbox: {pts_s.min(axis=0)*1e3} .. {pts_s.max(axis=0)*1e3} mm")

    fig = plt.figure(figsize=(16, 7))

    ax1 = fig.add_subplot(121, projection="3d")
    ax1.scatter(pts_f[:, 0], pts_f[:, 1], pts_f[:, 2], s=0.3, c="#0066cc", alpha=0.4)
    ax1.set_title(f"FLUIDO — lumen ({len(pts_f)} pts amostrados)", fontsize=11)
    ax1.set_xlabel("x [m]"); ax1.set_ylabel("y [m]"); ax1.set_zlabel("z [m]")
    bx = pts_f.max(axis=0) - pts_f.min(axis=0)
    ax1.set_box_aspect((bx[0], bx[1], bx[2]))

    ax2 = fig.add_subplot(122, projection="3d")
    ax2.scatter(pts_s[:, 0], pts_s[:, 1], pts_s[:, 2], s=0.3, c="#cc4400", alpha=0.4)
    ax2.set_title(f"SOLIDO — arteria cheia ({len(pts_s)} pts amostrados)", fontsize=11)
    ax2.set_xlabel("x [m]"); ax2.set_ylabel("y [m]"); ax2.set_zlabel("z [m]")
    bx = pts_s.max(axis=0) - pts_s.min(axis=0)
    ax2.set_box_aspect((bx[0], bx[1], bx[2]))

    fig.suptitle("Dominios FSI apos correcao de locationInMesh (2026-05-23)\n"
                 "Fluido = lumen real (NAO mais a caixa giga); Solido = arteria cheia",
                 fontsize=12)

    out_png = REPO / "brunaStuff" / "inspect_artoph_fsi_mesh_volumes.png"
    fig.tight_layout()
    fig.savefig(out_png, dpi=140)
    print(f"\nPlot salvo: {out_png}")


if __name__ == "__main__":
    main()
