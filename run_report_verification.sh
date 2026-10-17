#!/usr/bin/env bash
# Verify brunaStuff/latex/report numbers against case outputs (needs full repo mount in Docker).
set -euo pipefail
cd "$(dirname "$0")"
exec docker compose run --rm -v "$PWD:/repo" -w /repo fsi bash -lc 'cases/scripts/run_report_verification.sh'
