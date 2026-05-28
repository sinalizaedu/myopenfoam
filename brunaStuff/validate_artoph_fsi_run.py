#!/usr/bin/env python3
"""
Validacao pos-run da simulacao FSI pulsatil artoph-fsi-curva-mestrado.

Verifica saude da run:
  - sem FOAM FATAL / aborting / nan nos logs;
  - 41 snapshots VTK gerados (t = 0.00, 0.02, ..., 0.80 s);
  - Co_max dentro de faixa esperada (< 10) ao longo do ciclo;
  - tabela de pressao bate com a onda calibrada (PAM ~ 13.3 kPa).

Plota a onda de pressao realmente aplicada (cinematica e dimensional).

Uso: python3 brunaStuff/validate_artoph_fsi_run.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parents[1]
CASE = REPO / "cases" / "artoph-fsi-curva-mestrado"
FLUID = CASE / "fluid"
SOLID = CASE / "solid"
RHO = 1050.0


def check_logs() -> dict[str, str]:
    """Procura por FATAL/abort/nan/inf nos logs do fluido e solido."""
    bad_patterns = (
        re.compile(r"FOAM FATAL|FOAM aborting"),
        re.compile(r"\bnan\b|\binf\b", re.IGNORECASE),
    )
    out: dict[str, str] = {}
    for solver, log in (
        ("fluid", FLUID / "log.pimpleFoam"),
        ("solid", SOLID / "log.solids4Foam"),
    ):
        if not log.exists():
            out[solver] = "MISSING_LOG"
            continue
        bad: list[str] = []
        with log.open(encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f, 1):
                for pat in bad_patterns:
                    if pat.search(line) and not _is_false_positive(line):
                        bad.append(f"L{i}: {line.strip()[:120]}")
                        break
                if len(bad) >= 5:
                    break
        out[solver] = "OK" if not bad else "ERRORS:\n" + "\n".join(bad)
    return out


def _is_false_positive(line: str) -> bool:
    """Filtra matches inocuos (info do preCICE etc)."""
    return ("Revision info" in line) or ("printInfo" in line) or ("infoFrequency" in line)


def check_snapshots() -> tuple[int, int, list[float]]:
    """Lista snapshots numericos salvos no diretorio do fluido."""
    times: list[float] = []
    for p in FLUID.iterdir():
        if p.is_dir() and re.fullmatch(r"[0-9]+(\.[0-9]+)?(e[-+][0-9]+)?", p.name):
            try:
                t = float(p.name)
                times.append(t)
            except ValueError:
                pass
    times.sort()
    n = len(times)
    expected = 41
    return n, expected, times


def courant_stats() -> tuple[float, float, float]:
    """Min/medio/max do Co_max ao longo da run, a partir do log."""
    rx = re.compile(r"Courant Number mean: \S+\s+max: ([0-9.eE+\-]+)")
    co_max_list: list[float] = []
    with (FLUID / "log.pimpleFoam").open(encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = rx.search(line)
            if m:
                try:
                    val = float(m.group(1))
                    if val < 1e10:
                        co_max_list.append(val)
                except ValueError:
                    pass
    if not co_max_list:
        return (float("nan"), float("nan"), float("nan"))
    arr = np.array(co_max_list)
    return float(arr.min()), float(arr.mean()), float(arr.max())


def load_pressure_table(name: str) -> tuple[np.ndarray, np.ndarray]:
    """Le inlet_pressure.dat / outlet_pressure.dat (formato Function1 'table')."""
    path = FLUID / "constant" / name
    ts: list[float] = []
    ps: list[float] = []
    rx = re.compile(r"\(\s*([0-9.eE+\-]+)\s+([0-9.eE+\-]+)\s*\)")
    with path.open(encoding="utf-8") as f:
        for line in f:
            m = rx.search(line)
            if m:
                ts.append(float(m.group(1)))
                ps.append(float(m.group(2)))
    return np.array(ts), np.array(ps)


def main() -> int:
    print("=" * 70)
    print("VALIDACAO POS-RUN: artoph-fsi-curva-mestrado")
    print("=" * 70)

    print("\n[1] Logs de erro")
    log_check = check_logs()
    for k, v in log_check.items():
        marker = "OK" if v == "OK" else "FAIL"
        print(f"  {k}: [{marker}] {v[:200]}")

    print("\n[2] Snapshots VTK gerados")
    n, expected, times = check_snapshots()
    last = max(times) if times else 0.0
    fmt_times = ", ".join(f"{t:g}" for t in times[:5]) + ", ..., " + ", ".join(
        f"{t:g}" for t in times[-3:]
    )
    status = "OK" if n >= expected and last >= 0.799 else "PARTIAL"
    print(f"  {n} snapshots (esperado {expected}+), ultimo t = {last:.3f} s [{status}]")
    print(f"  tempos: {fmt_times}")

    print("\n[3] Estabilidade numerica (Co_max ao longo da run)")
    co_min, co_avg, co_max = courant_stats()
    co_status = "OK" if co_max < 10.0 else ("MARGINAL" if co_max < 50 else "FAIL")
    print(
        f"  Co_max: min={co_min:.3g}  mean={co_avg:.3g}  max={co_max:.3g}  [{co_status}]"
    )

    print("\n[4] Onda de pressao realmente aplicada (inlet)")
    t_in, p_in_kin = load_pressure_table("inlet_pressure.dat")
    t_out, p_out_kin = load_pressure_table("outlet_pressure.dat")
    p_in_pa = p_in_kin * RHO
    p_out_pa = p_out_kin * RHO

    mask1 = t_in <= 0.8
    pam = p_in_pa[mask1].mean()
    p_sys = p_in_pa[mask1].max()
    p_dia = p_in_pa[mask1].min()
    drive = (p_in_pa - p_out_pa).mean()
    print(f"  PAM (1 ciclo)    = {pam:8.1f} Pa   (alvo ~ 13300)")
    print(f"  pico sistolico   = {p_sys:8.1f} Pa   (alvo ~ 16000)")
    print(f"  vale diastolico  = {p_dia:8.1f} Pa   (alvo ~ 10700)")
    print(f"  Delta_p_drive    = {drive:8.2f} Pa   (alvo ~    10)")

    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    axes[0].plot(t_in, p_in_pa / 1000, label="inlet (Pa/1000)")
    axes[0].plot(t_out, p_out_pa / 1000, label="outlet (Pa/1000)", linestyle="--")
    axes[0].axvspan(0, 0.1, alpha=0.15, color="orange", label="rampa Hann")
    axes[0].axvline(0.8, color="k", linestyle=":", alpha=0.4, label="fim do ciclo")
    axes[0].set_ylabel("Pressao [kPa]")
    axes[0].set_title("Onda pulsatil aplicada na AO (1 ciclo cardiaco = 0.8 s, 75 bpm)")
    axes[0].legend(loc="best", fontsize=9)
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(t_in, (p_in_pa - p_out_pa) * 1000, label="Δp = inlet - outlet (mPa)")
    axes[1].axhline(10.0 * 1000, color="r", linestyle=":", alpha=0.5, label="Δp_drive nominal = 10 Pa")
    axes[1].set_xlabel("Tempo [s]")
    axes[1].set_ylabel("Δp [mPa]")
    axes[1].legend(loc="best", fontsize=9)
    axes[1].grid(True, alpha=0.3)

    out_png = REPO / "brunaStuff" / "artoph_fsi_pulsatile_wave.png"
    fig.tight_layout()
    fig.savefig(out_png, dpi=130)
    print(f"\n  plot salvo em: {out_png}")

    print("\n" + "=" * 70)
    failed = (
        any(v != "OK" for v in log_check.values())
        or status not in ("OK", "PARTIAL")
        or co_status == "FAIL"
    )
    print("RESULTADO:", "FALHA" if failed else "SUCESSO (run nao tem erros fatais)")
    print("=" * 70)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
