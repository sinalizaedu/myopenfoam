#!/usr/bin/env python3
"""Generate sweep_full/RESULTS.md from sensitivity, sweep, emulator, Claude comparison."""
from __future__ import annotations

import json
import statistics as stats
from pathlib import Path

HERE = Path(__file__).resolve().parent
SWEEP = HERE.parent
CLAUDE_RES = SWEEP.parents[1] / "claude-wp1.4-sweep" / "output_sweep_claude" / "sweep_results.json"


def main() -> None:
    sens = json.loads((SWEEP / "output_sensitivity" / "sensitivity_results.json").read_text())
    sweep = json.loads((SWEEP / "output_sweep" / "sweep_results.json").read_text())
    emu = json.loads((SWEEP / "output_emulator" / "emulator_report.json").read_text())
    claude = json.loads(CLAUDE_RES.read_text()) if CLAUDE_RES.is_file() else []

    ok = [r for r in sweep if r.get("status") == "OK"]
    v = [float(r["V_max_uL"]) for r in ok]
    k = [float(r["K_eff_mmHg_per_uL"]) for r in ok if r.get("K_eff_mmHg_per_uL")]

    lines = [
        "# WP1.4 sweep_full — RESULTS",
        "",
        "## Sensibilidade (V_max vs nominal)",
        "",
        "| case | V_max µL | Δ% vs nominal |",
        "|---|---:|---:|",
    ]
    for r in sens:
        if r.get("status") != "OK":
            lines.append(f"| {r['case_id']} | FAIL | — |")
            continue
        d = r.get("delta_pct_vs_nominal", 0)
        lines.append(f"| {r['case_id']} | {r['V_max_uL']:.1f} | {d:+.1f} |")

    lines += [
        "",
        "## Varredura (N=300)",
        "",
        f"- Convergidos: **{len(ok)}/{len(sweep)}**",
        f"- V_max: min {min(v):.1f}, max {max(v):.1f}, mean {stats.mean(v):.1f} µL",
        f"- K_eff: min {min(k):.4f}, max {max(k):.4f}, mean {stats.mean(k):.4f} mmHg/µL",
        "",
        "## Emulador GP",
        "",
    ]
    for tgt, m in emu.items():
        flag = "PASS" if m.get("passes_5pct_criterion") else "FAIL"
        lines.append(
            f"- **{tgt}**: CV erro médio {m['mean_relative_error_pct']}%, "
            f"R²={m['R2_cv_mean']} ± {m['R2_cv_std']} ({flag})"
        )

    if claude:
        cmap = {r["case_id"]: r for r in claude if r.get("status") == "OK"}
        diffs = []
        lines += ["", "## Comparação com Claude (mesma amostra)", "", "| case | V Claude | V sweep_full | Δ% |", "|---|---:|---:|---:|"]
        for r in ok[:20]:
            c = cmap.get(r["case_id"])
            if not c:
                continue
            vc, vs = float(c["V_max_uL"]), float(r["V_max_uL"])
            dp = 100 * (vs - vc) / vc
            diffs.append(dp)
            lines.append(f"| {r['case_id']} | {vc:.1f} | {vs:.1f} | {dp:+.1f} |")
        if len(ok) > 20:
            for r in ok[20:]:
                c = cmap.get(r["case_id"])
                if c:
                    vc, vs = float(c["V_max_uL"]), float(r["V_max_uL"])
                    diffs.append(100 * (vs - vc) / vc)
        if diffs:
            lines += [
                "",
                f"Resumo Δ% (V_sweep_full vs Claude): mean {stats.mean(diffs):+.2f}%, "
                f"stdev {stats.pstdev(diffs):.2f}%, |Δ| max {max(abs(x) for x in diffs):.1f}%",
                "",
                "Diferenças esperadas: espessura t(θ) por banda, R(ACD,lente), escala vitrectomia; "
                "Claude usava t uniforme (t_eq ou blend) + correções pós-FE.",
            ]
        # full table appendix
        lines.append("")
        lines.append("<details><summary>Tabela completa (300 casos)</summary>")
        lines.append("")
        lines.append("| case | V Claude | V sweep_full | Δ% |")
        lines.append("|---|---:|---:|---:|")
        for r in ok:
            c = cmap.get(r["case_id"])
            if not c:
                continue
            vc, vs = float(c["V_max_uL"]), float(r["V_max_uL"])
            dp = 100 * (vs - vc) / vc
            lines.append(f"| {r['case_id']} | {vc:.1f} | {vs:.1f} | {dp:+.1f} |")
        lines.append("</details>")

    (SWEEP / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print(f"Wrote {SWEEP / 'RESULTS.md'}")


if __name__ == "__main__":
    main()
