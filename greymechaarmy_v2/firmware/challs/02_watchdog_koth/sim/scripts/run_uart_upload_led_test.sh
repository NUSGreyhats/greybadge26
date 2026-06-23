#!/usr/bin/env bash
set -euo pipefail

build_dir="${1:-build/sim}"
bash sim/scripts/run_payload_uart_test.sh starter_led \
  --expect-led 5a \
  --build-dir "$build_dir"
