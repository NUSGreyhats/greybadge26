#!/usr/bin/env bash
set -euo pipefail

build_dir="${1:-build/sim}"
bash sim/scripts/run_payload_uart_test.sh flag_probe \
  --expect-led f1 \
  --build-dir "$build_dir" \
  --max-cycles 500000
