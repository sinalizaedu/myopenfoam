#!/usr/bin/env python3
"""Apply Level 3 fixes: propagate canonical scripts and patch Allrun/run_experiment."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / "scripts"

EXTRACT_TARGETS = [
    "doc-g2-sim4/scripts/extract_metrics.py",
    "T1: Volume vs Patch/doc-g2-sim5/scripts/extract_metrics.py",
    "doc-run-o1-patch-fluid/scripts/extract_metrics.py",
    "doc-run-o1-volume-fluid/scripts/extract_metrics.py",
    "doc-run-f1-volume-fluid/scripts/extract_metrics.py",
]

PLOT_TARGETS = [
    "doc-g2-sim4/scripts/plot_iop_acp.py",
    "T1: Volume vs Patch/doc-g2-sim5/scripts/plot_iop_acp.py",
    "doc-run-o1-patch-fluid/scripts/plot_iop_acp.py",
    "doc-run-o1-volume-fluid/scripts/plot_iop_acp.py",
    "doc-run-f1-volume-fluid/scripts/plot_iop_acp.py",
]

SYNC_GLOB = "doc-*/scripts/sync_field_boundaries.py"

SIM4_EXPERIMENT_CLEANUP = """        find fluid -maxdepth 1 -type d -regex '.*/[0-9]+\\.[0-9]+' -exec rm -rf {} +
        for d in fluid/[0-9]*; do
            [ -e "$d" ] || continue
            base="$(basename "$d")"
            [[ "$base" == "0" ]] && continue
            if [[ "$base" =~ ^[0-9]+$ ]] && [ "$base" -lt 50 ]; then
                rm -rf "$d"
            fi
        done
        rm -rf fluid/processor*"""

HAS_BASELINE_OLD = """has_baseline_times() {
    for d in fluid/[0-9]*; do
        [ -e "$d" ] || continue
        base="$(basename "$d")"
        [[ "$base" == "0" ]] && continue
        [[ "$base" =~ ^[0-9]+$ ]] && return 0
    done
    return 1
}"""

HAS_BASELINE_NEW = """has_baseline_times() {
    for d in fluid/[0-9]*; do
        [ -e "$d" ] || continue
        base="$(basename "$d")"
        [[ "$base" == "0" ]] && continue
        if [[ "$base" =~ ^[0-9]+$ ]] && [ "$base" -ge 50 ]; then
            return 0
        fi
    done
    return 1
}"""


def propagate_canonical(name: str, targets: list[str]) -> None:
    src = CANON / name
    for rel in targets:
        dst = ROOT / rel
        dst.write_text(src.read_text())
        dst.chmod(0o755)
        print(f"  copied {name} -> {rel}")


def patch_allrun_sim4(path: Path) -> bool:
    text = path.read_text()
    old = """        find fluid -maxdepth 1 -type d -regex '.*/[0-9]+\\.[0-9]+' -exec rm -rf {} +
        rm -rf fluid/postProcessing/iop_probe fluid/postProcessing/flowRateIVI \\
               fluid/postProcessing/flowRateACP fluid/postProcessing/flowRateWall \\
               fluid/postProcessing/flowRateTM fluid/postProcessing/pressureACinlet \\
               2>/dev/null || true
        rm -rf fluid/dynamicCode fluid/codeStream 2>/dev/null || true"""
    new = SIM4_EXPERIMENT_CLEANUP + """
        rm -rf fluid/postProcessing/iop_probe fluid/postProcessing/flowRateIVI \\
               fluid/postProcessing/flowRateACP fluid/postProcessing/flowRateWall \\
               fluid/postProcessing/flowRateTM fluid/postProcessing/pressureACinlet \\
               2>/dev/null || true
        rm -rf fluid/dynamicCode fluid/codeStream 2>/dev/null || true"""
    if old not in text:
        return False
    path.write_text(text.replace(old, new, 1))
    return True


def patch_allrun_sim5(path: Path) -> bool:
    text = path.read_text()
    old = """        find fluid -maxdepth 1 -type d -regex '.*/[0-9]+\\.[0-9]+' -exec rm -rf {} +
        rm -rf fluid/postProcessing/iop_probe fluid/postProcessing/flowRateWall \\
               fluid/postProcessing/flowRateTM fluid/postProcessing/pressureACinlet \\
               2>/dev/null || true
        rm -rf fluid/dynamicCode fluid/codeStream 2>/dev/null || true"""
    new = SIM4_EXPERIMENT_CLEANUP + """
        rm -rf fluid/postProcessing/iop_probe fluid/postProcessing/flowRateWall \\
               fluid/postProcessing/flowRateTM fluid/postProcessing/pressureACinlet \\
               2>/dev/null || true
        rm -rf fluid/dynamicCode fluid/codeStream 2>/dev/null || true"""
    if old not in text:
        return False
    path.write_text(text.replace(old, new, 1))
    return True


def main() -> None:
    print("=== propagate extract_metrics.py ===")
    propagate_canonical("extract_metrics.py", EXTRACT_TARGETS)
    print("=== propagate plot_iop_acp.py ===")
    propagate_canonical("plot_iop_acp.py", PLOT_TARGETS)
    print("=== propagate sync_field_boundaries.py ===")
    sync_targets = list(ROOT.glob("doc-*/scripts/sync_field_boundaries.py"))
    sync_targets += [
        ROOT / "doc-g2-sim4/scripts/sync_field_boundaries.py",
        ROOT / "T1: Volume vs Patch/doc-g2-sim5/scripts/sync_field_boundaries.py",
    ]
    for p in sorted(set(sync_targets)):
        if not p.is_file():
            continue
        p.write_text((CANON / "sync_field_boundaries.py").read_text())
        p.chmod(0o755)
        print(f"  copied sync_field_boundaries.py -> {p.relative_to(ROOT.parent)}")

    print("=== patch Allrun.sim4 experiment cleanup ===")
    sim4_targets = list(ROOT.glob("doc-*/Allrun.sim4")) + [ROOT / "doc-g2-sim4/Allrun.sim4"]
    for p in sorted(set(sim4_targets)):
        if p.is_file() and patch_allrun_sim4(p):
            print(f"  patched {p.relative_to(ROOT.parent)}")

    print("=== patch Allrun.sim5 experiment cleanup ===")
    sim5_targets = list(ROOT.glob("doc-*/Allrun.sim5")) + [ROOT / "T1: Volume vs Patch/doc-g2-sim5/Allrun.sim5"]
    for p in sorted(set(sim5_targets)):
        if p.is_file() and patch_allrun_sim5(p):
            print(f"  patched {p.relative_to(ROOT.parent)}")

    print("=== patch has_baseline_times in run_experiment scripts ===")
    run_scripts = list(ROOT.glob("doc-*/scripts/run_experiment_1h.sh"))
    run_scripts += list(ROOT.glob("doc-*/scripts/run_experiment_until_done.sh"))
    run_scripts += [
        ROOT / "doc-g2-sim4/scripts/run_experiment_1h.sh",
        ROOT / "doc-g2-sim4/scripts/run_experiment_until_done.sh",
        ROOT / "T1: Volume vs Patch/doc-g2-sim5/scripts/run_experiment_1h.sh",
    ]
    for p in sorted(set(run_scripts)):
        if not p.is_file():
            continue
        text = p.read_text()
        if HAS_BASELINE_OLD in text:
            p.write_text(text.replace(HAS_BASELINE_OLD, HAS_BASELINE_NEW, 1))
            print(f"  patched {p.relative_to(ROOT.parent)}")


if __name__ == "__main__":
    main()
