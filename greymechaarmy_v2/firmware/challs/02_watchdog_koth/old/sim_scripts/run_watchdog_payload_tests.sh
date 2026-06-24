#!/usr/bin/env bash
set -euo pipefail

build_dir="${1:-build/sim}"

bash sim/scripts/run_payload_uart_test.sh watchdog_timeout \
  --expect-watchdog-reset \
  --build-dir "$build_dir" \
  --max-cycles 500000

bash sim/scripts/run_payload_uart_test.sh watchdog_disable \
  --expect-led d1 \
  --build-dir "$build_dir" \
  --max-cycles 500000
