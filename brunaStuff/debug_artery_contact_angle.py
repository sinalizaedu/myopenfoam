#!/usr/bin/env python3
"""debug_artery_contact_angle.py

Debug Mode: instrumenta o ESTADO atual do posicionamento da arteria oftalmica
em cases/ao-mestrado para descobrir POR QUE o contato com o cilindro do ONS
esta no eixo +Y (theta=+90 deg) em vez de no quadrante +X-Y como na anatomia
original (Geometria Mestrado.stl).

Loga (NDJSON em .cursor/debug-0586c6.log) datapoints que testam as hipoteses:
  A) Alvo hardcoded em +Y (P_CL_TARGET = (0, 3.25, 18.5)) faz contato cair em +Y.
  B) A busca "smallest |delta|" escolhe o candidato natural mais proximo de +Y.
  C) A escala 1.3x along centerline distorceu o angulo natural de contato.
  D) on-mestrado/topoSetDict_contact espera contato em +Y (conflito).
  E) Coordenada z deveria ser ~22.8 mm (anatomia original) em vez de 18.5 mm.

Para cada estado (original/escalado/atual) loga (x, y, z, r_xy, theta_deg) do
ponto da parede mais proximo do eixo z. E para varios alvos candidatos (varios
theta * varios z), loga o melhor delta achavel e o angulo final atingido.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import cKDTree
from skimage.morphology import skeletonize

LOG_PATH = Path(
    "/Users/brunaenne/Documents/repos/myopenfoam/.cursor/debug-0586c6.log"
)
SESSION_ID = "0586c6"
RUN_ID = f"run_{int(time.time())}"

REPO = Path(__file__).resolve().parents[1]
TRI = REPO / "cases" / "ao-mestrado" / "constant" / "triSurface"

R_ONS_M = 2.5e-3
R_OUTER_TUBE_M = 0.75e-3
R_TARGET_M = R_ONS_M + R_OUTER_TUBE_M
Z0_M, Z1_M = 0.0, 30.0e-3


# #region agent log
def log(hypothesisId: str, location: str, message: str, data: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "sessionId": SESSION_ID,
        "id": f"log_{int(time.time()*1000)}_{location.replace(':', '_').replace('.', '_')}",
        "timestamp": int(time.time() * 1000),
        "location": location,
        "message": message,
        "data": data,
        "runId": RUN_ID,
        "hypothesisId": hypothesisId,
    }
    with LOG_PATH.open("a") as f:
        f.write(json.dumps(entry, default=float) + "\n")
# #endregion


def closest_to_zaxis(verts_mm: np.ndarray, z_lo: float = 0.0, z_hi: float = 30.0):
    mask = (verts_mm[:, 2] >= z_lo) & (verts_mm[:, 2] <= z_hi)
    if not mask.any():
        return None
    Vb = verts_mm[mask]
    rxy = np.hypot(Vb[:, 0], Vb[:, 1])
    i = int(np.argmin(rxy))
    p = Vb[i]
    theta = float(np.degrees(np.arctan2(p[1], p[0])))
    quad = (
        "+Y axis (theta~90)" if abs(theta - 90) < 30
        else "+X-Y" if (-90 < theta < 0)
        else "+X+Y" if (0 < theta < 90)
        else "-X+Y" if (90 < theta < 180)
        else "-X-Y"
    )
    return {
        "x_mm": float(p[0]),
        "y_mm": float(p[1]),
        "z_mm": float(p[2]),
        "r_xy_mm": float(rxy[i]),
        "theta_deg": theta,
        "quadrant": quad,
    }


def extract_centerline(stl_path: Path, pitch_m: float = 0.15e-3) -> np.ndarray:
    mesh = trimesh.load_mesh(str(stl_path))
    vox = mesh.voxelized(pitch=pitch_m).fill()
    skel = skeletonize(vox.matrix.astype(bool))
    pts = vox.indices_to_points(np.argwhere(skel))
    tree = cKDTree(pts)
    counts = tree.query_ball_point(pts, r=1.8 * pitch_m, return_length=True)
    start = int(np.argmin(counts))
    n = len(pts)
    visited = np.zeros(n, dtype=bool)
    order = [start]
    visited[start] = True
    cur = start
    while len(order) < n:
        _, idxs = tree.query(pts[cur], k=min(20, n))
        nxt = None
        for i in idxs:
            if not visited[i]:
                nxt = int(i)
                break
        if nxt is None:
            break
        order.append(nxt)
        visited[nxt] = True
        cur = nxt
    return pts[order]


def main() -> None:
    print(f"[debug] log path: {LOG_PATH}")

    # ---- HIPOTESE A: estado atual do contato ----
    artery_cur = trimesh.load_mesh(str(TRI / "artery.stl"))
    info_cur = closest_to_zaxis(artery_cur.vertices * 1e3)
    log("A", "debug.py:current", "artery.stl atual: ponto de contato anatomico", info_cur)

    # ---- HIPOTESE C: anatomia original (artery_unscaled.stl) ----
    artery_orig = trimesh.load_mesh(str(TRI / "artery_unscaled.stl"))
    info_orig = closest_to_zaxis(artery_orig.vertices * 1e3)
    log("C", "debug.py:original", "artery_unscaled.stl: ponto de contato anatomico ORIGINAL",
        info_orig)

    # ---- HIPOTESE C: post-escalamento (pre_p_contact = scale 1.3x mas sem translacao) ----
    artery_pre = trimesh.load_mesh(str(TRI / "artery.stl.pre_p_contact.stl"))
    info_pre = closest_to_zaxis(artery_pre.vertices * 1e3)
    log("C", "debug.py:scaled_pre", "artery.stl pos-escala 1.3x (sem translacao): contato",
        info_pre)

    # ---- HIPOTESE D: box do on-mestrado topoSetDict_contact ----
    on_box = {
        "box_xmin_mm": -0.5, "box_xmax_mm": 0.5,
        "box_ymin_mm": 2.40, "box_ymax_mm": 3.00,
        "box_zmin_mm": 18.0, "box_zmax_mm": 19.0,
        "box_center_xyz_mm": [0.0, 2.7, 18.5],
        "box_center_theta_deg": float(np.degrees(np.arctan2(2.7, 0.0))),
        "expected_quadrant": "+Y (theta~90 deg)",
        "comentario_no_arquivo":
            "Geometria real (artoph-curva-mestrado scale 1.3x): "
            "ponto mais proximo da arteria ao eixo do nervo: "
            "(-0.42, +2.57, +18.09) mm, setor angular ~ +90° (norte, +Y)",
    }
    log("D", "debug.py:on_mestrado_box",
        "on-mestrado/system/topoSetDict_contact: box geometry", on_box)

    # ---- HIPOTESES A,B,E: explora alvos alternativos ----
    cl_pre_m = extract_centerline(TRI / "artery.stl.pre_p_contact.stl")
    log("B", "debug.py:centerline",
        "centerline extraida da artery.stl.pre_p_contact.stl (raw skeleton)", {
        "n_points": int(len(cl_pre_m)),
        "x_mm_range": [float(cl_pre_m[:, 0].min() * 1e3), float(cl_pre_m[:, 0].max() * 1e3)],
        "y_mm_range": [float(cl_pre_m[:, 1].min() * 1e3), float(cl_pre_m[:, 1].max() * 1e3)],
        "z_mm_range": [float(cl_pre_m[:, 2].min() * 1e3), float(cl_pre_m[:, 2].max() * 1e3)],
    })

    # Para varios theta_target e z_target, achar melhor delta (rigid translation)
    # tal que NENHUM ponto da centerline em z[0,30] fique r_xy < 3.25 mm.
    explore_results = []
    for theta_deg in [-60, -45, -30, -20, -10, 0, +10, +30, +45, +70, +90]:
        for z_mm in [16, 18.5, 20, 22.8, 25]:
            theta_rad = np.radians(theta_deg)
            P_target = np.array([
                R_TARGET_M * np.cos(theta_rad),
                R_TARGET_M * np.sin(theta_rad),
                z_mm * 1e-3,
            ])
            valid = []
            for k in range(len(cl_pre_m)):
                delta_k = P_target - cl_pre_m[k]
                cl_t = cl_pre_m + delta_k
                mask = (cl_t[:, 2] >= Z0_M) & (cl_t[:, 2] <= Z1_M)
                if not mask.any():
                    continue
                rxy_t = np.hypot(cl_t[mask, 0], cl_t[mask, 1])
                min_r = float(rxy_t.min())
                if min_r >= R_TARGET_M - 1e-9:
                    idx_min = int(np.argmin(rxy_t))
                    Vb = cl_t[mask]
                    p_min = Vb[idx_min]
                    valid.append({
                        "k": k,
                        "delta_norm_mm": float(np.linalg.norm(delta_k) * 1e3),
                        "delta_mm": [float(delta_k[0] * 1e3), float(delta_k[1] * 1e3),
                                     float(delta_k[2] * 1e3)],
                        "achieved_x_mm": float(p_min[0] * 1e3),
                        "achieved_y_mm": float(p_min[1] * 1e3),
                        "achieved_z_mm": float(p_min[2] * 1e3),
                        "achieved_theta_deg": float(np.degrees(np.arctan2(p_min[1], p_min[0]))),
                        "achieved_r_mm": float(min_r * 1e3),
                    })
            if valid:
                best = min(valid, key=lambda v: v["delta_norm_mm"])
                explore_results.append({
                    "target_theta_deg": theta_deg,
                    "target_z_mm": z_mm,
                    "best": best,
                    "n_valid": len(valid),
                })

    for r in explore_results:
        log("AB_E", "debug.py:explore",
            f"target theta={r['target_theta_deg']:+d} deg z={r['target_z_mm']:.1f} mm",
            r)

    # ---- Sintese: qual alvo coincide com a anatomia original (theta_orig, z_orig) ----
    if info_orig is not None:
        theta_orig = info_orig["theta_deg"]
        z_orig = info_orig["z_mm"]
        # acha o alvo explorado com angle mais proximo ao original
        same_theta = sorted(
            explore_results,
            key=lambda r: (abs(r["best"]["achieved_theta_deg"] - theta_orig)
                           + abs(r["target_z_mm"] - z_orig)),
        )[:5]
        log("C", "debug.py:closest_to_original_anatomy",
            "alvos explorados mais proximos da anatomia ORIGINAL (theta_orig, z_orig)",
            {
                "anatomy_theta_deg": theta_orig,
                "anatomy_z_mm": z_orig,
                "top5_candidates": same_theta,
            })

    print(f"[debug] {len(explore_results)} alvos explorados; logs em {LOG_PATH}")


if __name__ == "__main__":
    main()
