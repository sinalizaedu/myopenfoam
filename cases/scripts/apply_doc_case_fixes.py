#!/usr/bin/env python3
"""Apply shared doc-baseline / doc-run hygiene fixes (text + bash one-liners)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PROTOCOL_README = """## Protocol (pimpleFoam 0–30 s)

| Phase | Time [s] | Plateau [s] | IVI | ACP | Wall (volume-matched flux) |
|-------|----------|-------------|-----|-----|----------------------------|
| Baseline | 0–5 | — | off | off | 0 |
| IVI | 5–12 | 6–11 | +Q | off | −Q |
| Gap | 12–15 | — | off | off | 0 |
| ACP | 15–22 | 16–21 | off | −Q | +Q |
| Recovery | 22–30 | — | off | off | 0 |

Every phase has a **1.0 s linear ramp** at each end (the `volumetricFlowRate table`
entries in `fluid/initial/U.experiment`), so the IVI window is 5–12 s, not 5–11 s.
Plateau 5 s + two half-ramps = **6 s effective** delivery.

`Q = 2.08325×10⁻⁹ m³/s` ≈ (50 µL / 6 s) / 4 — already the quarter-symmetry rate,
so IVI/ACP use `±Q`, not `±Q/4`. Delivered volume `Q × 6 s = 12.5 µL` per quarter
= 50 µL for the full eye.

The `wall` patch is **not** a Robin/compliance condition: it is a
`flowRateInletVelocity` Dirichlet flux prescribed as the exact negative of the
IVI/ACP rate, so the intraocular volume is held constant. Nothing in it responds
to pressure.
"""

VOLUME_PROTOCOL_README = """## Protocol (pimpleFoam 0–30 s)

| Phase | Time [s] | Plateau [s] | IVI (fvOptions) | ACP (fvOptions) | Wall (volume-matched flux) |
|-------|----------|-------------|-----------------|-----------------|----------------------------|
| Baseline | 0–5 | — | off | off | 0 |
| IVI | 5–12 | 6–11 | +Q | off | −Q |
| Gap | 12–15 | — | off | off | 0 |
| ACP | 15–22 | 16–21 | off | −Q | +Q |
| Recovery | 22–30 | — | off | off | 0 |

Every phase has a **1.0 s linear ramp** at each end (see `fluid/system/fvOptions.experiment`
and `fluid/initial/U.experiment` wall table). Effective IVI window: 5–12 s; ACP: 15–22 s.

`Q = 2.08325×10⁻⁹ m³/s` ≈ (50 µL / 6 s) / 4 — already the quarter-symmetry rate.
IVI/ACP volumetric sources in `fvOptions` use `±Q`; the wall flux is the matching
`flowRateInletVelocity` Dirichlet table (not a Robin/compliance BC).
"""

FVOPTIONS_TM_COMMENT = {
    "O1": ("1.645058e+15", "15.199", "O1"),
    "O2": ("1.645058e+15", "15.893", "O2"),
    "O3": ("1.645058e+15", "14.896", "O3"),
    "F1": ("1.983790e+15", "14.896", "F1"),
}

U_EXPERIMENT_HEADER = """// Fast stable experiment: 1.0 s linear ramp at each IVI/ACP edge (avoids step blow-up).
// Effective windows: IVI 5–12 s (plateau 6–11), ACP 15–22 s (plateau 16–21).
// Rate is already the quarter-symmetry value: ±Q, not ±Q/4.
"""


def case_meta(name: str) -> dict:
    m = re.match(r"doc-(baseline|run)-(f1|o1|o2|o3)-(patch|volume)-fluid", name)
    if not m:
        return {}
    kind, mesh, tip = m.groups()
    return {
        "kind": kind,
        "mesh": mesh.upper(),
        "tip": tip,
        "patch": tip == "patch",
        "volume": tip == "volume",
    }


def fix_allrun(path: Path, meta: dict) -> bool:
    text = path.read_text()
    orig = text
    mesh = meta["mesh"]
    tip_word = "patch" if meta["patch"] else "volume"
    case = path.parent.name

    if f'export MESH_LEVEL="${{MESH_LEVEL:-{mesh}}}"' not in text:
        text = re.sub(
            rf'export MESH_LEVEL="{mesh}"',
            f'export MESH_LEVEL="${{MESH_LEVEL:-{mesh}}}"',
            text,
        )

    if meta["kind"] == "baseline":
        old_echo = f'echo "=== {case} MODE=baseline MESH_LEVEL={mesh}'
        new_echo = f'echo "=== {case} MODE=baseline MESH_LEVEL=$MESH_LEVEL'
        if old_echo in text:
            text = text.replace(old_echo, new_echo)
    else:
        old_echo = f'echo "=== {case} MODE=$MODE MESH_LEVEL={mesh} ({tip_word})'
        new_echo = f'echo "=== {case} MODE=$MODE MESH_LEVEL=$MESH_LEVEL ({tip_word})'
        if old_echo in text:
            text = text.replace(old_echo, new_echo)

    if meta["kind"] == "run" and "WARNING: reusing the seeded" not in text:
        warn = f"""# REUSE_MESH=1 never re-meshes, so MESH_LEVEL only relabels output here.
if [ "$REUSE_MESH" = "1" ] && [ "$MESH_LEVEL" != "{mesh}" ]; then
  echo "WARNING: reusing the seeded {mesh} polyMesh but labelling output as ${{MESH_LEVEL}}." >&2
  echo "         Re-seed from a ${{MESH_LEVEL}} baseline first, or results will be mislabelled." >&2
fi

"""
        marker = '  exit 1\nfi\n\n'
        idx = text.find('if [ "$MODE" = "baseline" ]; then')
        if idx != -1:
            end = text.find(marker, idx)
            if end != -1:
                insert_at = end + len(marker)
                text = text[:insert_at] + warn + text[insert_at:]

    if text != orig:
        path.write_text(text)
        return True
    return False


def fix_allrun_sim4(path: Path) -> bool:
    text = path.read_text()
    orig = text
    if "CASE_NAME=" not in text:
        text = text.replace(
            "# doc-g2-sim4 — G2 Sim 4: IVI + ACP combined + Robin wall\n#\n",
            "# G2 Sim 4 protocol: IVI + ACP combined + volume-matched wall flux.\n"
            "# Banner name is taken from the case directory (see CASE_NAME below).\n#\n",
            1,
        )
        text = text.replace(
            "# Experiment uses volume-matched Robin only (rigid comparison is doc-g2-sim2).\n"
            "set -e\nset -o pipefail\ncd \"$(dirname \"$0\")\"\n",
            "# Experiment prescribes a volume-matched wall flux (rigid comparison is doc-g2-sim2).\n"
            "set -e\nset -o pipefail\ncd \"$(dirname \"$0\")\"\nCASE_NAME=\"$(basename \"$PWD\")\"\n",
            1,
        )
    text = text.replace(
        'echo "=== doc-g2-sim4 MODE=${MODE} MESH_LEVEL=${MESH_LEVEL}',
        'echo "=== ${CASE_NAME} MODE=${MODE} MESH_LEVEL=${MESH_LEVEL}',
    )
    text = text.replace(
        'echo "=== doc-g2-sim4 done (MODE=${MODE}, ${MESH_LEVEL}) ==="',
        'echo "=== ${CASE_NAME} done (MODE=${MODE}, ${MESH_LEVEL}) ==="',
    )
    text = re.sub(
        r"(N_IVI=\$\(grep -E \"cellSet ivi_tip_cells now size\"[^\n]+\|\s*awk '\{print \$NF\}')(\s*\))",
        r"\1 || true\2",
        text,
    )
    text = re.sub(
        r"(N_ACP=\$\(grep -E \"cellSet acp_tip_cells now size\"[^\n]+\|\s*awk '\{print \$NF\}')(\s*\))",
        r"\1 || true\2",
        text,
    )
    if text != orig:
        path.write_text(text)
        return True
    return False


def fix_allrun_sim5(path: Path) -> bool:
    text = path.read_text()
    orig = text
    if "CASE_NAME=" not in text:
        text = text.replace(
            "# doc-g2-sim5 — G2 Sim 5: IVI + ACP via volumetric fvOptions (no subsetMesh)\n#\n",
            "# G2 Sim 5 protocol: IVI + ACP via volumetric fvOptions (no subsetMesh).\n"
            "# Banner name is taken from the case directory (see CASE_NAME below).\n#\n",
            1,
        )
        text = text.replace(
            'cd "$(dirname "$0")"\nMODE="${MODE:-baseline}"\n',
            'cd "$(dirname "$0")"\nCASE_NAME="$(basename "$PWD")"\nMODE="${MODE:-baseline}"\n',
            1,
        )
    text = text.replace(
        'echo "=== doc-g2-sim5 MODE=${MODE} MESH_LEVEL=${MESH_LEVEL}',
        'echo "=== ${CASE_NAME} MODE=${MODE} MESH_LEVEL=${MESH_LEVEL}',
    )
    text = text.replace(
        'echo "=== doc-g2-sim5 done (MODE=${MODE}, ${MESH_LEVEL}) ==="',
        'echo "=== ${CASE_NAME} done (MODE=${MODE}, ${MESH_LEVEL}) ==="',
    )
    text = re.sub(
        r"(N_IVI=\$\(grep -E \"cellSet ivi_tip_cells now size\"[^\n]+\|\s*awk '\{print \$NF\}')(\s*\))",
        r"\1 || true\2",
        text,
    )
    text = re.sub(
        r"(N_ACP=\$\(grep -E \"cellSet acp_tip_cells now size\"[^\n]+\|\s*awk '\{print \$NF\}')(\s*\))",
        r"\1 || true\2",
        text,
    )
    if text != orig:
        path.write_text(text)
        return True
    return False


def fix_fvoptions(path: Path, mesh: str) -> bool:
    if mesh not in FVOPTIONS_TM_COMMENT:
        return False
    text = path.read_text()
    if "TM: d_TM = 8.156268e14" not in text and "TM: d_TM = 1.645058e+15" in text:
        return False
    d_tm, iop, label = FVOPTIONS_TM_COMMENT[mesh]
    new_block = (
        f"// Vitreous: k = 5.8×10⁻¹⁴ m²  →  d_vit = 1.724×10¹³ m⁻²\n"
        f"// TM: d_TM = {d_tm} → IOP₀ = {iop} mmHg (AC probe) on {label}, steady simpleFoam\n"
        f"//     outlet_tm stays at P_TM = 10 Torr.\n"
        f"//     Change d_TM via D_TM= env or scripts/set_d_tm.py, then re-run the baseline.\n"
    )
    if "TM: d_TM = 8.156268e14" in text:
        text = re.sub(
            r"// Vitreous:.*?\n// TM:.*?\n//     outlet_tm.*?\n\n",
            new_block + "\n",
            text,
            count=1,
            flags=re.S,
        )
    elif re.search(r"^// G2-fluid porous zones", text, re.M) and "TM: d_TM =" not in text:
        text = text.replace(
            "// G2-fluid porous zones — baseline (no IVI/ACP volumetric sources)\n\n",
            "// G2-fluid porous zones — AC / vitreous / TM (1/4 eye calotte)\n//\n"
            + new_block
            + "\n",
            1,
        )
    else:
        return False
    path.write_text(text)
    return True


def fix_readme_run(path: Path, meta: dict) -> bool:
    text = path.read_text()
    block = VOLUME_PROTOCOL_README if meta["volume"] else PROTOCOL_README
    new_text, n = re.subn(
        r"## Protocol \(pimpleFoam 0–30 s\)\n\n.*?\n\n## Setup",
        block + "\n## Setup",
        text,
        count=1,
        flags=re.S,
    )
    if n:
        path.write_text(new_text)
        return True
    return False


def fix_run_experiment_1h(path: Path, meta: dict) -> bool:
    text = path.read_text()
    orig = text

    # Patch (sim4): remove backwards robin copy; ensure plot after archive.
    if meta["patch"]:
        text = re.sub(
            r"\n    cp -f fluid/initial/U\.experiment fluid/initial/U\.experiment\.robin\n",
            "\n",
            text,
        )
        if "archive first:" not in text:
            text = text.replace(
                "python3 scripts/extract_metrics.py --protocol ivi_acp || true\n"
                "python3 scripts/archive_experiment_results.py || true\n",
                "python3 scripts/extract_metrics.py --protocol ivi_acp || true\n"
                "# archive first: plot_iop_acp.py prefers results/iop_probe_p.txt (stage1+stage2),\n"
                "# else it falls back to iop_probe/0/p, which is stage1 only (0-2 s).\n"
                "python3 scripts/archive_experiment_results.py || true\n",
            )
        if "plot_iop_acp.py" not in text:
            text = text.replace(
                "python3 scripts/archive_experiment_results.py || true\n",
                "python3 scripts/archive_experiment_results.py || true\n"
                "python3 scripts/plot_iop_acp.py || true\n",
            )
    else:
        # Volume (sim5): keep create-if-missing for .robin; ensure archive-before-plot comment.
        text = re.sub(
            r"    # U\.experiment already carries Robin wall BC; robin may be a symlink to the same file\.\n"
            r"    if \[ ! -e fluid/initial/U\.experiment\.robin \]; then\n"
            r"        cp -f fluid/initial/U\.experiment fluid/initial/U\.experiment\.robin\n"
            r"    fi\n",
            "    # U.experiment.robin is read-only template; create once if missing.\n"
            "    if [ ! -e fluid/initial/U.experiment.robin ]; then\n"
            "        cp -f fluid/initial/U.experiment.1h fluid/initial/U.experiment.robin 2>/dev/null || "
            "cp -f fluid/initial/U.experiment fluid/initial/U.experiment.robin\n"
            "    fi\n",
            text,
        )
        if "archive first:" not in text and "plot_iop_acp.py" in text:
            text = text.replace(
                "python3 scripts/extract_metrics.py --protocol ivi_acp || true\n"
                "python3 scripts/archive_experiment_results.py || true\n"
                "python3 scripts/plot_iop_acp.py || true\n",
                "python3 scripts/extract_metrics.py --protocol ivi_acp || true\n"
                "# archive first: plot_iop_acp.py prefers results/iop_probe_p.txt (stage1+stage2).\n"
                "python3 scripts/archive_experiment_results.py || true\n"
                "python3 scripts/plot_iop_acp.py || true\n",
            )

    if text != orig:
        path.write_text(text)
        return True
    return False


def fix_u_experiment_comments(case_dir: Path) -> bool:
    initial = case_dir / "fluid" / "initial"
    if not initial.is_dir():
        return False
    changed = False
    old = "// Fast stable experiment: 0.5 s ramp at IVI/ACP onset (avoids step blow-up at t≈5/15).\n"
    for name in ("U.experiment", "U.experiment.1h", "U.experiment.robin"):
        p = initial / name
        if not p.is_file():
            continue
        text = p.read_text()
        if old in text:
            p.write_text(text.replace(old, U_EXPERIMENT_HEADER))
            changed = True
    return changed


def main() -> None:
    changed: list[str] = []
    for case_dir in sorted(ROOT.glob("doc-*-fluid")):
        name = case_dir.name
        if name == "doc-baseline-2d-fluid":
            continue
        meta = case_meta(name)
        if not meta:
            continue

        allrun = case_dir / "Allrun"
        if allrun.is_file() and fix_allrun(allrun, meta):
            changed.append(f"{name}/Allrun")

        sim4 = case_dir / "Allrun.sim4"
        if sim4.is_file() and fix_allrun_sim4(sim4):
            changed.append(f"{name}/Allrun.sim4")

        sim5 = case_dir / "Allrun.sim5"
        if sim5.is_file() and fix_allrun_sim5(sim5):
            changed.append(f"{name}/Allrun.sim5")

        fvo = case_dir / "fluid/system/fvOptions"
        if fvo.is_file() and fix_fvoptions(fvo, meta["mesh"]):
            changed.append(f"{name}/fluid/system/fvOptions")

        if meta["kind"] == "run":
            readme = case_dir / "README.md"
            if readme.is_file() and fix_readme_run(readme, meta):
                changed.append(f"{name}/README.md")
            re1h = case_dir / "scripts/run_experiment_1h.sh"
            if re1h.is_file() and fix_run_experiment_1h(re1h, meta):
                changed.append(f"{name}/scripts/run_experiment_1h.sh")
            if meta["patch"] and fix_u_experiment_comments(case_dir):
                changed.append(f"{name}/fluid/initial/U.experiment*")

    print("Updated:")
    for c in changed:
        print(f"  {c}")
    if not changed:
        print("  (nothing changed — already up to date)")


if __name__ == "__main__":
    main()
