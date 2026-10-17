#!/usr/bin/env bash
# Regenerate WP0 figures/metrics and verify LaTeX report numbers against JSON.
# Usage (repo root):
#   docker compose run --rm -v "$PWD:/repo" -w /repo fsi bash -lc 'cases/scripts/run_report_verification.sh'
#
# Overnight FEA (optional, long):
#   RUN_WP11=1 RUN_WP12=1 RUN_WP12_MULTISTART=1 RUN_WP13=1 \
#     docker compose run --rm -v "$PWD:/repo" -w /repo fsi bash -lc 'cases/scripts/run_report_verification.sh'
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LATEX_REPORT="$ROOT/brunaStuff/latex/report/wp1.tex"
if [[ ! -f "$LATEX_REPORT" ]]; then
  echo "ERROR: relatório LaTeX não encontrado em:" >&2
  echo "  $LATEX_REPORT" >&2
  echo "" >&2
  echo "Este script precisa da raiz do repositório (não só ./cases em /simulation)." >&2
  echo "Na raiz do repo no Mac:" >&2
  echo '  ./run_report_verification.sh' >&2
  echo "ou:" >&2
  echo '  docker compose run --rm -v "$PWD:/repo" -w /repo fsi bash -lc '"'"'cases/scripts/run_report_verification.sh'"'" >&2
  echo "" >&2
  echo "Dentro do container com volume padrão (cwd /simulation), o caminho correto NÃO é cases/scripts/…" >&2
  echo "  use scripts/… só para casos em /simulation — o audit exige montagem /repo." >&2
  exit 1
fi
cd "$ROOT"

if [[ "${SKIP_WP0:-0}" != "1" ]]; then
  echo "=== WP0 Allrun (figures + report_metrics.json) ==="
  cd cases/wp0
  ./Allrun
  cd "$ROOT"
else
  echo "SKIP WP0 (SKIP_WP0=1)"
fi

if [[ "${RUN_WP11:-0}" == "1" ]]; then
  echo "=== WP1.1 Allrun (octant mesh study) ==="
  cd cases/wp1.1 && ./Allrun
  cd "$ROOT"
fi

if [[ "${RUN_WP12:-0}" == "1" ]]; then
  echo "=== WP1.2 literature matrix (Tabelas 7–8) ==="
  cd cases/wp1.2 && ./Allrun_literature_p50
  cd "$ROOT"
fi

if [[ "${RUN_WP12_MULTISTART:-0}" == "1" ]]; then
  echo "=== WP1.2 Ogden multistart (wide α + local C clusters) ==="
  cd cases/wp1.2
  python3 scripts/run_ogden_multistart_matrix.py \
    --targets friedenwald \
    --out output_multistart_friedenwald_alpha100 \
    --alpha-lo 0.5 --alpha-hi 100
  python3 scripts/run_ogden_multistart_matrix.py \
    --targets friedenwald \
    --out output_ogden_multistart_p50 \
    --alpha-lo 0.5 --alpha-hi 6
  cd "$ROOT"
fi

if [[ "${RUN_WP13:-0}" == "1" ]]; then
  echo "=== WP1.3 backward displacement (Tabela 10) ==="
  cd cases/wp1.3 && ./Allrun_backward_displacement_6
  cd "$ROOT"
fi

echo "=== WP1.1 verify (requires existing output_octant or Allrun) ==="
if [[ -f cases/wp1.1/output_octant/summary.json ]]; then
  python3 cases/wp1.1/scripts/verify_wp1_octant_report.py || true
else
  echo "SKIP wp1.1 — no summary.json (run: cd cases/wp1.1 && ./Allrun or RUN_WP11=1)"
fi

echo "=== LaTeX ↔ JSON audit ==="
python3 cases/scripts/audit_latex_report_numbers.py \
  --write-methodology-audit methodology_audit_wp12_wp13.json \
  --write-methodology-audit-root methodology_audit.json

echo "DONE report verification"
