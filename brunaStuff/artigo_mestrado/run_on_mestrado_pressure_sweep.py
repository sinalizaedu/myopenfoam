#!/usr/bin/env python3
"""
Sweep on-mestrado: 5 (ou N) pressões FIXAS na patch contact_local, sem pulsatilidade.

- Salva backup de contact_pressure.dat e system/controlDict na 1ª execução.
- Para cada pressão: escreve tabela constante, reduz endTime a um passo quasi-estático,
  limpa pastas de tempo (exceto 0/), roda solids4Foam (opcional), mede u_n médio.
- Restaura controlDict + contact_pressure do backup ao final.
- Gráficos: P × deslocamento normal (m), P × força resultante (N), e barras Δ% vs P0.

Pressões default: P0=9000 Pa e +20% absoluto (1800 Pa) cinco vezes:
  9000, 10800, 12600, 14400, 16200 Pa

Uso (no ambiente com OpenFOAM + solids4Foam no PATH):
  cd /Users/.../myopenfoam
  python3 brunaStuff/run_on_mestrado_pressure_sweep.py --run

Só gerar CSV/PNG a partir de resultados já colados em sweep_cache (avançado):
  python3 brunaStuff/run_on_mestrado_pressure_sweep.py --plot-only brunaStuff/on_mestrado_sweep_results.csv
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

# Reutiliza leitura de malha / patch do script de gráfico
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import plot_on_mestrado_force_displacement_contact as pm  # noqa: E402
import on_mestrado_centerline_metrics as clm  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
SOLID = REPO / "cases" / "on-mestrado" / "solid"
MESH = SOLID / "constant" / "polyMesh"
D0 = SOLID / "0" / "D"
CP = SOLID / "constant" / "contact_pressure.dat"
CD = SOLID / "system" / "controlDict"
BACKUP_DIR = SOLID / ".sweep_backup_on_mestrado"
RESULT_CSV = _SCRIPT_DIR / "on_mestrado_sweep_results.csv"
OUT_PNG_PU = _SCRIPT_DIR / "on_mestrado_sweep_pressure_vs_disp.png"
OUT_PNG_PF = _SCRIPT_DIR / "on_mestrado_sweep_pressure_vs_force.png"
OUT_PNG_BAR = _SCRIPT_DIR / "on_mestrado_sweep_disp_bars_pct.png"
OUT_PNG_DEV = _SCRIPT_DIR / "on_mestrado_sweep_pressure_vs_deviation_mm.png"
OUT_PNG_ONT = _SCRIPT_DIR / "on_mestrado_sweep_pressure_vs_ont.png"

# Referência clínica (Lee et al., npj Microgravity 2020 — desvio pré-voo)
CLINICAL_DEV_MM_LO = 1.10
CLINICAL_DEV_MM_HI = 1.72
CLINICAL_DEV_MM_MEAN = 1.41
CLINICAL_ONT_TYPICAL = 1.02

# +20% de 9000 Pa em termos absolutos: +1800 Pa por nível (5 pontos)
P0 = 9000.0
STEP_PA = 0.20 * P0
DEFAULT_PRESSURES = [P0 + k * STEP_PA for k in range(5)]


def write_constant_pressure(path: Path, p_pa: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""// constante — sweep on-mestrado
(
  ( 0    {p_pa:.6g} )
  ( 1    {p_pa:.6g} )
);
""",
        encoding="utf-8",
    )


def backup_if_needed() -> None:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    bcp = BACKUP_DIR / "contact_pressure.dat.orig"
    bcd = BACKUP_DIR / "controlDict.orig"
    if not bcp.is_file():
        shutil.copy2(CP, bcp)
        print(f"Backup: {bcp}")
    if not bcd.is_file():
        shutil.copy2(CD, bcd)
        print(f"Backup: {bcd}")


def restore_from_backup() -> None:
    bcp = BACKUP_DIR / "contact_pressure.dat.orig"
    bcd = BACKUP_DIR / "controlDict.orig"
    if bcp.is_file():
        shutil.copy2(bcp, CP)
    if bcd.is_file():
        shutil.copy2(bcd, CD)
    print("Restaurados contact_pressure.dat e controlDict a partir do backup.")


def set_control_single_step(cd_path: Path, end_time: float, delta_t: float) -> None:
    t = cd_path.read_text(encoding="utf-8")
    t = re.sub(r"(?m)^(\s*endTime\s+)\S+;", rf"\g<1>{end_time};", t)
    t = re.sub(r"(?m)^(\s*deltaT\s+)\S+;", rf"\g<1>{delta_t};", t)
    cd_path.write_text(t, encoding="utf-8")


def clean_solution_times(solid_dir: Path) -> None:
    for p in solid_dir.iterdir():
        if not p.is_dir():
            continue
        name = p.name
        if name == "0":
            continue
        try:
            float(name)
        except ValueError:
            continue
        shutil.rmtree(p, ignore_errors=True)
    for pat in ("log.solids4Foam", "log.solids4Foam.start"):
        lp = solid_dir / pat
        if lp.is_file():
            lp.unlink()


def mesh_area_factor() -> tuple[str, int, int, float, np.ndarray, np.ndarray]:
    patch_name = pm.detect_pressure_patch_name(D0)
    sizes = pm.read_boundary_patch_sizes(MESH / "boundary")
    n_faces, start_face = sizes[patch_name]
    pts = pm.read_points(MESH / "points")
    faces = pm.read_faces(MESH / "faces")
    s_sum = np.zeros(3)
    areas: list[float] = []
    normals: list[np.ndarray] = []
    for fi in range(start_face, start_face + n_faces):
        svec = pm.quad_area_vector(pts, faces[fi])
        a = float(np.linalg.norm(svec))
        areas.append(a)
        normals.append(svec / a if a > 1e-30 else np.array([1.0, 0.0, 0.0]))
        s_sum += svec
    areas_np = np.array(areas)
    normals_np = np.stack(normals)
    s_norm = float(np.linalg.norm(s_sum))
    return patch_name, n_faces, start_face, s_norm, areas_np, normals_np


def latest_time_dir(solid_dir: Path) -> Path | None:
    best: tuple[float, Path] | None = None
    for p in solid_dir.iterdir():
        if not p.is_dir() or p.name == "0":
            continue
        try:
            t = float(p.name)
        except ValueError:
            continue
        if (p / "D").is_file():
            if best is None or t > best[0]:
                best = (t, p)
    return best[1] if best else None


def measure_u_n(d_path: Path, patch: str, n_faces: int, areas_np: np.ndarray, normals_np: np.ndarray) -> float:
    dvecs = np.array(pm.extract_patch_value_vectors(d_path, patch, n_faces), dtype=float)
    return float(np.sum(areas_np[:, None] * np.sum(dvecs * normals_np, axis=1)) / np.sum(areas_np))


def run_solid() -> None:
    r = subprocess.run(
        ["solids4Foam"],
        cwd=str(SOLID),
        env=os.environ.copy(),
        check=False,
    )
    if r.returncode != 0:
        raise RuntimeError(f"solids4Foam saiu com código {r.returncode}")


def plot_results(rows: list[dict]) -> None:
    import matplotlib.pyplot as plt

    p_arr = np.array([r["pressure_Pa"] for r in rows])
    f_arr = np.array([r["force_N"] for r in rows])
    u_arr = np.array([r["u_normal_m"] for r in rows])
    dev_mm = np.array([r["deviation_max_mm"] for r in rows])
    ont = np.array([r["ont_index"] for r in rows])

    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.plot(p_arr / 1000.0, u_arr * 1e6, "s-", color="steelblue", lw=1.2, ms=7)
    ax.set_xlabel("Pressão de contato (kPa)")
    ax.set_ylabel(r"Deslocamento normal médio na patch (µm)")
    ax.set_title("Patch contact_local — $u_n$ (não usar como tortuosidade clínica)")
    ax.grid(True, alpha=0.35)
    fig.tight_layout()
    fig.savefig(OUT_PNG_PU, dpi=150)
    plt.close(fig)

    fig_cl, ax_cl = plt.subplots(figsize=(6.5, 4.2))
    ax_cl.plot(p_arr / 1000.0, dev_mm, "o-", color="crimson", lw=1.2, ms=8)
    ax_cl.axhspan(CLINICAL_DEV_MM_LO, CLINICAL_DEV_MM_HI, color="lightgray", alpha=0.5, label="RM pré-voo (Lee 2020)")
    ax_cl.axhline(CLINICAL_DEV_MM_MEAN, color="gray", ls="--", lw=1, label=f"Média clínica ≈ {CLINICAL_DEV_MM_MEAN:.2f} mm")
    for p, d in zip(p_arr, dev_mm):
        ax_cl.annotate(f"{p:.0f} Pa", (p / 1000.0, d), textcoords="offset points", xytext=(4, 4), fontsize=8)
    ax_cl.set_xlabel("Pressão de contato (kPa)")
    ax_cl.set_ylabel("Desvio máximo da centerline ON (mm)")
    ax_cl.set_title("Tortuosidade clínica (trecho 20 mm) — desvio máximo à corda")
    ax_cl.legend(loc="best", fontsize=8)
    ax_cl.grid(True, alpha=0.35)
    fig_cl.tight_layout()
    fig_cl.savefig(OUT_PNG_DEV, dpi=150)
    plt.close(fig_cl)

    fig_ont, ax_ont = plt.subplots(figsize=(6.5, 4.2))
    ax_ont.plot(p_arr / 1000.0, ont, "s-", color="purple", lw=1.2, ms=7)
    ax_ont.axhline(CLINICAL_ONT_TYPICAL, color="gray", ls="--", lw=1, label=f"ONT típico ≈ {CLINICAL_ONT_TYPICAL}")
    ax_ont.set_xlabel("Pressão de contato (kPa)")
    ax_ont.set_ylabel("ONT (comprimento curvo / corda)")
    ax_ont.set_title("Índice ONT na centerline ON (20 mm)")
    ax_ont.legend(loc="best", fontsize=8)
    ax_ont.grid(True, alpha=0.35)
    fig_ont.tight_layout()
    fig_ont.savefig(OUT_PNG_ONT, dpi=150)
    plt.close(fig_ont)

    fig2, ax2 = plt.subplots(figsize=(6.5, 4.2))
    ax2.plot(p_arr / 1000.0, f_arr * 1000.0, "D-", color="darkorange", lw=1.2, ms=7)
    ax2.set_xlabel("Pressão de contato (kPa)")
    ax2.set_ylabel("Força resultante $|p\\sum\\vec{S}_f|$ (mN)")
    ax2.set_title("on-mestrado — sweep: pressão × força na patch")
    ax2.grid(True, alpha=0.35)
    fig2.tight_layout()
    fig2.savefig(OUT_PNG_PF, dpi=150)
    plt.close(fig2)

    u0 = u_arr[0]
    pct = (u_arr / u0 - 1.0) * 100.0 if abs(u0) > 1e-20 else np.zeros_like(u_arr)
    fig3, ax3 = plt.subplots(figsize=(7, 4.2))
    x = np.arange(len(p_arr))
    ax3.bar(x, pct, color="seagreen", edgecolor="black", linewidth=0.6)
    ax3.set_xticks(x)
    ax3.set_xticklabels([f"{p:.0f}\nPa" for p in p_arr], fontsize=9)
    ax3.set_ylabel(r"$\Delta u_n$ relativo ao 1º nível (%)")
    ax3.set_title(f"Patch $u_n$ relativo (P₀ = {p_arr[0]:.0f} Pa)")
    ax3.axhline(0, color="gray", lw=0.8)
    ax3.grid(True, axis="y", alpha=0.35)
    fig3.tight_layout()
    fig3.savefig(OUT_PNG_BAR, dpi=150)
    plt.close(fig3)


def write_results_csv(rows: list[dict]) -> None:
    with RESULT_CSV.open("w", encoding="utf-8") as f:
        f.write(
            "pressure_Pa,force_resultant_N,u_normal_m,deviation_max_mm,ont_index,deviation_geom_mm\n"
        )
        for r in rows:
            f.write(
                f"{r['pressure_Pa']:.8g},{r['force_N']:.8g},{r['u_normal_m']:.8g},"
                f"{r['deviation_max_mm']:.8g},{r['ont_index']:.8g},{r['deviation_geom_mm']:.8g}\n"
            )
    print(f"CSV: {RESULT_CSV}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Sweep de pressão fixa no on-mestrado.")
    ap.add_argument(
        "--pressures",
        type=str,
        default=",".join(str(p) for p in DEFAULT_PRESSURES),
        help="Lista separada por vírgula (Pa). Default: 9000 + k*1800, k=0..4",
    )
    ap.add_argument(
        "--run",
        action="store_true",
        help="Executa solids4Foam em cada nível (sem isso, só gera tabelas .dat em brunaStuff/)",
    )
    ap.add_argument(
        "--plot-only",
        type=Path,
        default=None,
        help="Só lê CSV existente e gera PNGs (sem simulação)",
    )
    ap.add_argument("--end-time", type=float, default=0.05, help="endTime no controlDict durante o sweep")
    ap.add_argument("--delta-t", type=float, default=0.05, help="deltaT no controlDict durante o sweep")
    args = ap.parse_args()

    if args.plot_only is not None:
        path = args.plot_only
        if not path.is_file():
            print(f"Arquivo não encontrado: {path}", file=sys.stderr)
            return 1
        rows = []
        for line in path.read_text(encoding="utf-8").splitlines()[1:]:
            parts = line.strip().split(",")
            if len(parts) >= 3:
                rows.append(
                    {
                        "pressure_Pa": float(parts[0]),
                        "force_N": float(parts[1]),
                        "u_normal_m": float(parts[2]),
                        "deviation_max_mm": float(parts[3]) if len(parts) > 3 else float("nan"),
                        "ont_index": float(parts[4]) if len(parts) > 4 else float("nan"),
                        "deviation_geom_mm": float(parts[5]) if len(parts) > 5 else float("nan"),
                    }
                )
        plot_results(rows)
        print(
            f"PNG: {OUT_PNG_PU}\nPNG: {OUT_PNG_DEV}\nPNG: {OUT_PNG_ONT}\n"
            f"PNG: {OUT_PNG_PF}\nPNG: {OUT_PNG_BAR}"
        )
        return 0

    pressures = [float(x.strip()) for x in args.pressures.split(",") if x.strip()]
    if not pressures:
        print("Lista --pressures vazia.", file=sys.stderr)
        return 1

    if not D0.is_file():
        print(f"Falta {D0}", file=sys.stderr)
        return 1

    if not args.run:
        out_dir = _SCRIPT_DIR / "on_mestrado_sweep_tables"
        out_dir.mkdir(parents=True, exist_ok=True)
        for p_pa in pressures:
            outp = out_dir / f"contact_pressure_P{int(round(p_pa))}.dat"
            write_constant_pressure(outp, p_pa)
        print(f"Tabelas de pressão CONSTANTE (sem pulsatil) em:\n  {out_dir}/")
        print("Para cada simulação manual: copie um arquivo para")
        print(f"  {CP}")
        print("e rode um passo quasi-estático (ex.: endTime=deltaT=0.05 s) + solids4Foam.")
        print("Automação completa (5 runs + gráficos): adicione --run no ambiente com OpenFOAM.")
        return 0

    if not (MESH / "boundary").is_file():
        print(f"Malha ausente em {MESH}. Rode o Allrun do on-mestrado antes.", file=sys.stderr)
        return 1

    patch_name, n_faces, _start, s_norm, areas_np, normals_np = mesh_area_factor()
    print(f"Patch de carga: {patch_name}, nFaces={n_faces}, ||ΣS_f||={s_norm:.6e} m²")

    backup_if_needed()
    set_control_single_step(CD, args.end_time, args.delta_t)

    rows: list[dict] = []
    try:
        for p_pa in pressures:
            write_constant_pressure(CP, p_pa)
            clean_solution_times(SOLID)
            print(f"\n=== Pressão fixa {p_pa:.1f} Pa ===")
            run_solid()
            tdir = latest_time_dir(SOLID)
            if tdir is None or not (tdir / "D").is_file():
                raise RuntimeError(f"Sem pasta de tempo com D após P={p_pa} Pa.")
            u_n = measure_u_n(tdir / "D", patch_name, n_faces, areas_np, normals_np)
            f_n = p_pa * s_norm
            cl = clm.centerline_metrics_from_case(SOLID, time_name=tdir.name)
            rows.append(
                {
                    "pressure_Pa": p_pa,
                    "force_N": f_n,
                    "u_normal_m": u_n,
                    "deviation_max_mm": cl["deviation_max_mm"],
                    "ont_index": cl["ont_index"],
                    "deviation_geom_mm": cl["deviation_max_ref_mm"],
                }
            )
            print(f"  u_n patch = {u_n*1e3:.3f} mm   |F| = {f_n*1e3:.3f} mN")
            print(
                f"  desvio centerline = {cl['deviation_max_mm']:.3f} mm   "
                f"ONT = {cl['ont_index']:.4f}   (geom. malha D=0: {cl['deviation_max_ref_mm']:.3f} mm)"
            )
    finally:
        restore_from_backup()

    write_results_csv(rows)
    plot_results(rows)
    print(
        f"\nPNG: {OUT_PNG_PU}\nPNG: {OUT_PNG_DEV}\nPNG: {OUT_PNG_ONT}\n"
        f"PNG: {OUT_PNG_PF}\nPNG: {OUT_PNG_BAR}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
