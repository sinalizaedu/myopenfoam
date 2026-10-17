#!/usr/bin/env python3
"""Compare O1 patch vs volume during active IVI + volume-matched wall cheat.

Uses the finished 30 s experiments. t=0–1 s in those cases is idle baseline;
the equivalent 1 s window with injection on is t=6→7 s (IVI plateau).
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "brunaStuff"))
from g2_needle import IVI_TIP_ORIGIN_M, TOPOSET_TIP_RADIUS_M  # noqa: E402
from plot_o1_mesh import read_faces, read_points  # noqa: E402

RHO = 1000.0
MMHG = 133.322
TIP = np.array(IVI_TIP_ORIGIN_M)
R_NEAR = 1.5e-3  # 1.5 mm ball around IVI tip
R_CORE = TOPOSET_TIP_RADIUS_M * 1.5  # ~0.825 mm


def p_to_mmhg(p):
    return np.asarray(p) * RHO / MMHG


def read_int_list(path: Path) -> np.ndarray:
    text = path.read_text()
    m = re.search(r"(\d+)\s*\(", text)
    if not m:
        raise ValueError(f"no list in {path}")
    count = int(m.group(1))
    start = m.end()
    end = text.rfind(")")
    vals = np.fromstring(text[start:end], sep=" ", dtype=np.int64)
    if vals.size != count:
        raise ValueError(f"{path}: expected {count}, got {vals.size}")
    return vals


def read_label_set(path: Path) -> np.ndarray:
    text = path.read_text()
    m = re.search(r"(\d+)\s*\(", text)
    if not m:
        raise ValueError(f"no set list in {path}")
    count = int(m.group(1))
    start = m.end()
    end = text.rfind(")")
    vals = np.fromstring(text[start:end], sep=" ", dtype=np.int64)
    if vals.size != count:
        raise ValueError(f"{path}: expected {count} labels, got {vals.size}")
    return vals


def cell_centres(mesh: Path) -> np.ndarray:
    points = read_points(mesh / "points")
    faces = read_faces(mesh / "faces")
    owner = read_int_list(mesh / "owner")
    neigh_path = mesh / "neighbour"
    neighbour = read_int_list(neigh_path)
    n_cells = int(owner.max()) + 1
    acc = np.zeros((n_cells, 3), dtype=np.float64)
    w = np.zeros(n_cells, dtype=np.float64)
    n_int = neighbour.size
    for fi, verts in enumerate(faces):
        fc = points[np.asarray(verts, dtype=np.int64)].mean(axis=0)
        c = int(owner[fi])
        acc[c] += fc
        w[c] += 1.0
        if fi < n_int:
            c2 = int(neighbour[fi])
            acc[c2] += fc
            w[c2] += 1.0
    if np.any(w == 0):
        raise RuntimeError("empty cell weight")
    return acc / w[:, None]


def read_internal_field(path: Path, ncomp: int) -> np.ndarray:
    text = path.read_text()
    m = re.search(r"internalField\s+nonuniform\s+List<(?:scalar|vector)>\s*\n(\d+)\s*\(", text)
    if not m:
        m2 = re.search(r"internalField\s+uniform\s+\(([^)]+)\)", text)
        if m2 and ncomp == 3:
            v = np.fromstring(m2.group(1), sep=" ")
            n = int(re.search(r"nCells|", text) and 0)
            raise ValueError(f"uniform vector in {path}")
        m3 = re.search(r"internalField\s+uniform\s+([^\s;]+)", text)
        if m3 and ncomp == 1:
            raise ValueError(f"uniform scalar in {path}")
        raise ValueError(f"cannot parse {path}")
    n = int(m.group(1))
    start = m.end()
    depth = 1
    i = start
    while i < len(text) and depth:
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
        i += 1
    body = text[start : i - 1]
    if ncomp == 1:
        vals = np.fromstring(body, sep=" ", dtype=np.float64)
    else:
        nums = np.fromstring(re.sub(r"[()]", " ", body), sep=" ", dtype=np.float64)
        vals = nums.reshape(-1, ncomp)
    if vals.shape[0] != n:
        raise ValueError(f"{path}: expected {n}, got {vals.shape[0]}")
    return vals


def phase_of(t: float) -> str:
    if t < 5.0:
        return "baseline (no IVI)"
    if t < 6.0:
        return "IVI ramp-up"
    if t <= 11.0:
        return "IVI plateau"
    if t < 12.0:
        return "IVI ramp-down"
    if t < 15.0:
        return "gap"
    if t < 16.0:
        return "ACP ramp-up"
    if t <= 21.0:
        return "ACP plateau"
    if t < 22.0:
        return "ACP ramp-down"
    return "recovery"


def parse_log(path: Path) -> dict:
    time_re = re.compile(r"^Time = ([0-9.]+)\s*$")
    gamg_re = re.compile(
        r"GAMG:\s+Solving for p, Initial residual = ([0-9.eE+-]+), "
        r"Final residual = ([0-9.eE+-]+), No Iterations (\d+)"
    )
    exec_re = re.compile(r"^ExecutionTime = ([0-9.]+) s\s+ClockTime = ([0-9.]+) s")
    cour_re = re.compile(r"Courant Number mean: ([0-9.eE+-]+) max: ([0-9.eE+-]+)")

    t = None
    per_t = {}
    gamg_buf = []
    cour = None
    with path.open() as f:
        for line in f:
            mt = time_re.match(line)
            if mt:
                if t is not None:
                    per_t[t] = {
                        "gamg": gamg_buf,
                        "courant_max": cour,
                    }
                t = float(mt.group(1))
                gamg_buf = []
                cour = None
                continue
            mg = gamg_re.search(line)
            if mg:
                gamg_buf.append(
                    {
                        "niter": int(mg.group(3)),
                        "init": float(mg.group(1)),
                        "final": float(mg.group(2)),
                    }
                )
                continue
            mc = cour_re.search(line)
            if mc:
                cour = float(mc.group(2))
                continue
            me = exec_re.match(line)
            if me and t is not None:
                per_t.setdefault(t, {"gamg": gamg_buf, "courant_max": cour})
                per_t[t]["exec"] = float(me.group(1))
                per_t[t]["clock"] = float(me.group(2))

    if t is not None:
        per_t.setdefault(t, {"gamg": gamg_buf, "courant_max": cour})

    rows = []
    for tt, d in sorted(per_t.items()):
        iters = [g["niter"] for g in d.get("gamg", [])]
        pfinal = [g for g in d.get("gamg", []) if g["niter"] >= 400]
        rows.append(
            {
                "t": tt,
                "phase": phase_of(tt),
                "n_gamg": len(iters),
                "sum_iter": int(sum(iters)),
                "mean_iter": float(np.mean(iters)) if iters else 0.0,
                "max_iter": int(max(iters)) if iters else 0,
                "n_hit_100": int(sum(1 for n in iters if n == 100)),
                "n_hit_500": int(sum(1 for n in iters if n == 500)),
                "pfinal_max_init": max((g["init"] for g in pfinal), default=None),
                "pfinal_min_final": min((g["final"] for g in pfinal), default=None),
                "courant_max": d.get("courant_max"),
                "exec": d.get("exec"),
                "clock": d.get("clock"),
            }
        )
    return {"steps": rows, "end_clock": rows[-1]["clock"] if rows else None}


def summarize_phases(steps: list[dict]) -> dict:
    by = defaultdict(list)
    for s in steps:
        by[s["phase"]].append(s)
    out = {}
    for ph, xs in by.items():
        out[ph] = {
            "n_steps": len(xs),
            "mean_sum_iter": float(np.mean([x["sum_iter"] for x in xs])),
            "mean_iter_per_gamg": float(np.mean([x["mean_iter"] for x in xs])),
            "mean_hit_500": float(np.mean([x["n_hit_500"] for x in xs])),
            "frac_steps_hit_500": float(np.mean([x["n_hit_500"] > 0 for x in xs])),
            "mean_courant_max": float(
                np.nanmean([x["courant_max"] if x["courant_max"] is not None else np.nan for x in xs])
            ),
        }
    return out


def window_stats(steps: list[dict], t0: float, t1: float) -> dict:
    xs = [s for s in steps if t0 - 1e-12 <= s["t"] <= t1 + 1e-12]
    if not xs:
        return {}
    clocks = [s["clock"] for s in xs if s.get("clock") is not None]
    dt_clock = (max(clocks) - min(clocks)) if len(clocks) >= 2 else None
    return {
        "n_steps": len(xs),
        "t0": xs[0]["t"],
        "t1": xs[-1]["t"],
        "mean_sum_iter": float(np.mean([x["sum_iter"] for x in xs])),
        "mean_iter_per_gamg": float(np.mean([x["mean_iter"] for x in xs])),
        "mean_hit_500": float(np.mean([x["n_hit_500"] for x in xs])),
        "frac_hit_500": float(np.mean([x["n_hit_500"] > 0 for x in xs])),
        "clock_span_s": dt_clock,
        "mean_courant_max": float(
            np.nanmean([x["courant_max"] if x["courant_max"] is not None else np.nan for x in xs])
        ),
    }


def field_stats(cc: np.ndarray, p: np.ndarray, U: np.ndarray) -> dict:
    mag = np.linalg.norm(U, axis=1)
    d = np.linalg.norm(cc - TIP, axis=1)
    near = d < R_NEAR
    core = d < R_CORE
    pmm = p_to_mmhg(p)
    umm_s = mag * 1e3

    def pack(mask, name):
        if not np.any(mask):
            return {name: {"n": 0}}
        pv = pmm[mask]
        uv = umm_s[mask]
        i_pmax = int(np.argmax(pv))
        i_umax = int(np.argmax(uv))
        idx = np.where(mask)[0]
        return {
            name: {
                "n": int(mask.sum()),
                "p_min_mmHg": float(pv.min()),
                "p_max_mmHg": float(pv.max()),
                "p_p50_mmHg": float(np.percentile(pv, 50)),
                "p_p95_mmHg": float(np.percentile(pv, 95)),
                "p_p99_mmHg": float(np.percentile(pv, 99)),
                "p_hotspot_ratio_max_p99": float(pv.max() / max(np.percentile(pv, 99), 1e-12)),
                "p_spread_max_minus_p50": float(pv.max() - np.percentile(pv, 50)),
                "U_max_mm_s": float(uv.max()),
                "U_p95_mm_s": float(np.percentile(uv, 95)),
                "U_p99_mm_s": float(np.percentile(uv, 99)),
                "pmax_r_mm": float(d[idx[i_pmax]] * 1e3),
                "Umax_r_mm": float(d[idx[i_umax]] * 1e3),
            }
        }

    glob = pack(np.ones(p.size, dtype=bool), "global")
    out = {}
    out.update(glob)
    out.update(pack(near, "near_1p5mm"))
    out.update(pack(core, "core_0p825mm"))
    n_hot = int(((pmm > np.percentile(pmm, 99.9)) & near).sum())
    out["n_near_cells_above_global_p999"] = n_hot
    return out


def plot_slice(cc, p, U, title, out_png, p_clim=None, u_clim=None):
    mag = np.linalg.norm(U, axis=1)
    pmm = p_to_mmhg(p)
    slab = np.abs(cc[:, 0]) < 2.5e-4
    z = cc[slab, 2] * 1e3
    y = cc[slab, 1] * 1e3
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.2), dpi=140)
    sc0 = axes[0].scatter(
        z, y, c=pmm[slab], s=8, cmap="magma", linewidths=0,
        vmin=None if p_clim is None else p_clim[0],
        vmax=None if p_clim is None else p_clim[1],
    )
    sc1 = axes[1].scatter(
        z, y, c=mag[slab] * 1e3, s=8, cmap="viridis", linewidths=0,
        vmin=None if u_clim is None else u_clim[0],
        vmax=None if u_clim is None else u_clim[1],
    )
    for ax, sc, lab in (
        (axes[0], sc0, "p (mmHg)"),
        (axes[1], sc1, "|U| (mm/s)"),
    ):
        ax.set_aspect("equal")
        ax.set_xlim(-1.6, 1.6)
        ax.set_ylim(1.4, 4.6)
        ax.set_xlabel("z (mm)")
        ax.set_ylabel("y (mm)")
        circ = plt.Circle((0.0, 3.0), TOPOSET_TIP_RADIUS_M * 1e3, fill=False, ls="--", color="white", lw=1.0)
        ax.add_patch(circ)
        ax.plot(0.0, 3.0, "x", color="white", ms=6)
        fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.04, label=lab)
    axes[0].set_title("Pressure near IVI tip")
    axes[1].set_title("Speed near IVI tip")
    fig.suptitle(title, fontsize=11)
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png)
    plt.close(fig)


def plot_gamg(patch_steps, vol_steps, out_png):
    fig, ax = plt.subplots(figsize=(10.5, 4.2), dpi=140)
    tp = [s["t"] for s in patch_steps]
    tv = [s["t"] for s in vol_steps]
    ax.plot(tp, [s["sum_iter"] for s in patch_steps], lw=1.1, label="O1 Patch · GAMG iters / step")
    ax.plot(tv, [s["sum_iter"] for s in vol_steps], lw=1.1, label="O1 Volume · GAMG iters / step")
    ax.axvspan(5, 12, color="0.85", zorder=0, label="IVI window (cheat on)")
    ax.axvspan(15, 22, color="0.92", zorder=0)
    ax.set_xlabel("t (s)")
    ax.set_ylabel("sum of GAMG iterations per time step")
    ax.set_title("Pressure-solver effort (stage 2 log, t=2–30 s, dt=0.02 s)")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_png)
    plt.close(fig)


def main():
    cases = {
        "patch": REPO / "cases/doc-run-o1-patch-fluid",
        "volume": REPO / "cases/T1: Volume vs Patch/doc-run-o1-volume-fluid",
    }
    outdir = REPO / "cases/figures/o1_patch_vs_volume_ivi"
    outdir.mkdir(parents=True, exist_ok=True)

    report = {}
    centres = {}
    for name, root in cases.items():
        print(f"mesh centres {name}...", flush=True)
        centres[name] = cell_centres(root / "fluid/constant/polyMesh")
        ivi_set = root / "fluid/constant/polyMesh/sets/ivi_tip_cells"
        ivi_ids = read_label_set(ivi_set) if ivi_set.exists() else None
        log = parse_log(root / "fluid/log.pimpleFoam")
        report[name] = {
            "n_cells": int(centres[name].shape[0]),
            "n_ivi_set": int(ivi_ids.size) if ivi_ids is not None else None,
            "end_clock_s": log["end_clock"],
            "phases": summarize_phases(log["steps"]),
            "window_ivi_1s_t6_7": window_stats(log["steps"], 6.0, 7.0),
            "window_ivi_plateau_t6_11": window_stats(log["steps"], 6.0, 11.0),
            "window_baseline_t2_5": window_stats(log["steps"], 2.0, 5.0),
            "fields": {},
        }
        report[name]["_steps"] = log["steps"]
        if ivi_ids is not None and ivi_ids.size:
            d = np.linalg.norm(centres[name][ivi_ids] - TIP, axis=1)
            report[name]["ivi_set_r_mm"] = {
                "min": float(d.min() * 1e3),
                "max": float(d.max() * 1e3),
                "mean": float(d.mean() * 1e3),
            }

    p_all_near = []
    u_all_near = []
    for name, root in cases.items():
        cc = centres[name]
        for tdir in ("2", "6", "10"):
            print(f"fields {name} t={tdir}...", flush=True)
            p = read_internal_field(root / "fluid" / tdir / "p", 1)
            U = read_internal_field(root / "fluid" / tdir / "U", 3)
            if p.size != cc.shape[0] or U.shape[0] != cc.shape[0]:
                raise RuntimeError(
                    f"{name} t={tdir}: n_cells mesh={cc.shape[0]} p={p.size} U={U.shape[0]}"
                )
            st = field_stats(cc, p, U)
            report[name]["fields"][tdir] = st
            d = np.linalg.norm(cc - TIP, axis=1)
            near = d < R_NEAR
            p_all_near.append(p_to_mmhg(p[near]))
            u_all_near.append(np.linalg.norm(U[near], axis=1) * 1e3)
            if tdir in ("6", "10"):
                plot_slice(
                    cc, p, U,
                    f"O1 {name} · t={tdir} s · IVI on · wall cheat on",
                    outdir / f"{name}_t{tdir}_ivi_zoom.png",
                )

    # Shared color limits for t=6 comparison
    p6 = {}
    U6 = {}
    for name, root in cases.items():
        p6[name] = read_internal_field(root / "fluid/6/p", 1)
        U6[name] = read_internal_field(root / "fluid/6/U", 3)
    p_clim = (
        min(p_to_mmhg(p6["patch"]).min(), p_to_mmhg(p6["volume"]).min()),
        max(p_to_mmhg(p6["patch"]).max(), p_to_mmhg(p6["volume"]).max()),
    )
    u_clim = (
        0.0,
        max(np.linalg.norm(U6["patch"], axis=1).max(), np.linalg.norm(U6["volume"], axis=1).max()) * 1e3,
    )
    for name in cases:
        plot_slice(
            centres[name], p6[name], U6[name],
            f"O1 {name} · t=6 s · shared color scale",
            outdir / f"{name}_t6_shared_scale.png",
            p_clim=p_clim,
            u_clim=u_clim,
        )

    plot_gamg(report["patch"]["_steps"], report["volume"]["_steps"], outdir / "gamg_iters_vs_time.png")

    # drop bulky steps from json
    for name in report:
        steps = report[name].pop("_steps")
        report[name]["n_log_steps"] = len(steps)

    json_path = outdir / "comparison.json"
    json_path.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    print(f"wrote {json_path}")
    print(f"p_clim_mmHg={p_clim} u_clim_mm_s={u_clim}")


if __name__ == "__main__":
    main()
