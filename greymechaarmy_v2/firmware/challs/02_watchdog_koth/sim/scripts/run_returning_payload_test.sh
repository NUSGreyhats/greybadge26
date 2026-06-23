#!/usr/bin/env bash
set -euo pipefail

bash sim/scripts/run_payload_uart_test.sh return_immediate \
  --expect-led 77 \
  --expect-return-ready \
  --max-cycles 500000

