#!/usr/bin/env python3
"""debug_overlap_diagnostic.py

Diagnostico runtime: encontra TODOS os pontos de proximidade/invasao da
arteria com o cilindro ONS (R=2.5 mm, z[0,30] mm).

- Lista os 10 vertices mais proximos ao eixo z em z[0,30] de:
    * artery.stl
    * artery_outer.stl
    * artery_inner.stl (se existir)
- Lista os 10 pontos mais proximos da centerline (skel) ao eixo z em z[0,30]
- Reporta posicoes que invadem r_xy < R_ONS
- Salva tudo no log de debug
"""
from __future__ import annotations
import json
import time
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial import cKDTree
from skimage.morphology import skeletonize

REPO = Path(__file__).resolve().parents[1]
TRI = REPO / "cases" / "ao-mestrado" / "constant" / "triSurface"

R_ONS_MM = 2.5
R_OUTER_TUBE_MM = 0.75
Z0_MM, Z1_MM = 0.0, 30.0
TARGET_R_CENTERLINE = R_ONS_MM + R_OUTER_TUBE_MM  # 3.25 mm

DEBUG_LOG = Path("/Users/brunaenne/Documents/repos/myopenfoam/.cursor/debug-0586c6.log")
SESSION = "0586c6"
RUN = f"run_{int(time.time())}_overlap_diag"


def log(hyp, loc, msg, data):
    DEBUG_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "sessionId": SESSION,
        "id": f"log_{int(time.time()*1000)}_{loc.replace(':', '_').replace('.', '_')}",
        "timestamp": int(time.time() * 1000),
        "location": loc,
        "message": msg,
        "data": data,
        "runId": RUN,
        "hypothesisId": hyp,
    }
    with DEBUG_LOG.open("a") as f:
        f.write(json.dumps(entry, default=float) + "\n")


def closest_on_mesh(name: str, mesh_path: Path) -> dict:
    if not mesh_path.exists():
        return {"missing": True, "path": str(mesh_path)}
    m = trimesh.load_mesh(str(mesh_path))
    V_mm = m.vertices * 1e3 if m.vertices.max() < 1.0 else m.vertices.copy()
    # confirm units (m if max < 1)
    units_m = m.vertices.max() < 1.0
    V_mm = m.vertices * (1e3 if units_m else 1.0)
    mask = (V_mm[:, 2] >= Z0_MM) & (V_mm[:, 2] <= Z1_MM)
    if not mask.any():
        return {"empty_in_z_band": True}
    Vb = V_mm[mask]
    rxy = np.hypot(Vb[:, 0], Vb[:, 1])
    idx_sorted = np.argsort(rxy)
    top10 = []
    for k in idx_sorted[:10]:
        x, y, z = Vb[k]
        theta = float(np.degrees(np.arctan2(y, x)))
        top10.append({
            "x_mm": float(x), "y_mm": float(y), "z_mm": float(z),
            "r_xy_mm": float(rxy[k]),
            "theta_deg": theta,
            "inside_ONS": bool(rxy[k] < R_ONS_MM),
        })
    n_inside = int((rxy < R_ONS_MM).sum())
    n_close = int((rxy < R_ONS_MM + 0.1).sum())
    bounds = [V_mm.min(axis=0).tolist(), V_mm.max(axis=0).tolist()]
    return {
        "n_vertices_total": int(len(V_mm)),
        "n_vertices_in_z_band": int(mask.sum()),
        "min_r_xy_mm_in_z_band": float(rxy.min()),
        "n_inside_ONS_in_z_band": n_inside,
        "n_within_100um_of_ONS_in_z_band": n_close,
        "bounds_mm": bounds,
        "top10_closest_to_z_axis": top10,
    }


def centerline_diagnostic(stl_path: Path) -> dict:
    if not stl_path.exists():
        return {"missing": True}
    m = trimesh.load_mesh(str(stl_path))
    pitch_m = 0.15e-3
    vox = m.voxelized(pitch=pitch_m).fill()
    skel = skeletonize(vox.matrix.astype(bool))
    pts = vox.indices_to_points(np.argwhere(skel))  # m
    pts_mm = pts * 1e3
    mask = (pts_mm[:, 2] >= Z0_MM) & (pts_mm[:, 2] <= Z1_MM)
    P = pts_mm[mask]
    rxy = np.hypot(P[:, 0], P[:, 1])
    idx_sorted = np.argsort(rxy)
    top10 = []
    for k in idx_sorted[:10]:
        x, y, z = P[k]
        theta = float(np.degrees(np.arctan2(y, x)))
        top10.append({
            "x_mm": float(x), "y_mm": float(y), "z_mm": float(z),
            "r_xy_mm": float(rxy[k]),
            "theta_deg": theta,
            "below_target_3.25": bool(rxy[k] < TARGET_R_CENTERLINE - 1e-6),
            "tube_invades_ONS": bool(rxy[k] - R_OUTER_TUBE_MM < R_ONS_MM - 1e-6),
        })
    n_below_target = int((rxy < TARGET_R_CENTERLINE - 1e-6).sum())
    n_tube_invades = int((rxy - R_OUTER_TUBE_MM < R_ONS_MM - 1e-6).sum())
    return {
        "n_centerline_in_z_band": int(mask.sum()),
        "min_r_xy_mm": float(rxy.min()),
        "n_below_3.25mm": n_below_target,
        "n_tube_invades_ONS": n_tube_invades,
        "top10_closest": top10,
    }


def main():
    print("=== debug_overlap_diagnostic ===")

    # 1) artery.stl
    d_art = closest_on_mesh("artery.stl", TRI / "artery.stl")
    log("F1_F2_F3", "diag.py:artery_stl",
        "Diagnostico artery.stl: top10 vertices mais proximos do eixo z em z[0,30]",
        d_art)
    print(f"\nartery.stl: min r_xy = {d_art.get('min_r_xy_mm_in_z_band', '?')} mm  "
          f"({d_art.get('n_inside_ONS_in_z_band', '?')} verts dentro ONS)")
    for t in d_art.get("top10_closest_to_z_axis", [])[:5]:
        print(f"  ({t['x_mm']:+.3f}, {t['y_mm']:+.3f}, {t['z_mm']:+.3f}) "
              f"r_xy={t['r_xy_mm']:.4f} theta={t['theta_deg']:+.1f} "
              f"inside_ONS={t['inside_ONS']}")

    # 2) artery_outer.stl
    d_outer = closest_on_mesh("artery_outer.stl", TRI / "artery_outer.stl")
    log("F1_F2_F3", "diag.py:artery_outer_stl",
        "Diagnostico artery_outer.stl: top10 vertices proximos eixo z",
        d_outer)
    print(f"\nartery_outer.stl: min r_xy = {d_outer.get('min_r_xy_mm_in_z_band', '?')} mm  "
          f"({d_outer.get('n_inside_ONS_in_z_band', '?')} verts dentro ONS)")
    for t in d_outer.get("top10_closest_to_z_axis", [])[:5]:
        print(f"  ({t['x_mm']:+.3f}, {t['y_mm']:+.3f}, {t['z_mm']:+.3f}) "
              f"r_xy={t['r_xy_mm']:.4f} theta={t['theta_deg']:+.1f} "
              f"inside_ONS={t['inside_ONS']}")

    # 3) artery_inner.stl
    d_inner = closest_on_mesh("artery_inner.stl", TRI / "artery_inner.stl")
    log("F1_F2_F3", "diag.py:artery_inner_stl",
        "Diagnostico artery_inner.stl: top10 vertices proximos eixo z",
        d_inner)
    print(f"\nartery_inner.stl: min r_xy = {d_inner.get('min_r_xy_mm_in_z_band', '?')} mm  "
          f"({d_inner.get('n_inside_ONS_in_z_band', '?')} verts dentro ONS)")

    # 4) Centerline diagnostic from artery.stl (FSI tube extruded around it)
    d_cl = centerline_diagnostic(TRI / "artery.stl")
    log("F1", "diag.py:centerline",
        "Centerline da artery.stl em z[0,30]: distribuicao de r_xy e tube-invade-ONS",
        d_cl)
    print(f"\ncenterline.skel: min r_xy = {d_cl.get('min_r_xy_mm', '?')} mm  "
          f"({d_cl.get('n_tube_invades_ONS', '?')} pontos onde tubo FSI invadiria ONS)")
    for t in d_cl.get("top10_closest", [])[:5]:
        print(f"  ({t['x_mm']:+.3f}, {t['y_mm']:+.3f}, {t['z_mm']:+.3f}) "
              f"r_xy={t['r_xy_mm']:.4f} theta={t['theta_deg']:+.1f} "
              f"tube_invades_ONS={t['tube_invades_ONS']}")


if __name__ == "__main__":
    main()
