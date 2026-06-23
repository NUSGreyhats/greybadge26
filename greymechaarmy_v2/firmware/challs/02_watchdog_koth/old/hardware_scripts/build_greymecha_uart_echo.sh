#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT_DIR="${1:-$ROOT/build/greymecha_uart_echo}"
PINOUT="${PINOUT:-/mnt/c/Users/zunmun/Documents/Stuff/Github/WORK/GreyHats/greybadge25/firmware/ecp5/main/pinout.lpf}"

mkdir -p "$OUT_DIR/log"
cp "$PINOUT" "$OUT_DIR/pinout.lpf"

cd "$ROOT"

yosys -p "
read_verilog \
  rtl/peripherals/uart_serial_bridge.v \
  rtl/top/greymecha_uart_echo_top.v
synth_ecp5 -top greymecha_uart_echo_top -json $OUT_DIR/greymecha_uart_echo.json
" 2>&1 | tee "$OUT_DIR/log/yosys.log"

nextpnr-ecp5 \
  --json "$OUT_DIR/greymecha_uart_echo.json" \
  --textcfg "$OUT_DIR/greymecha_uart_echo.config" \
  --25k \
  --package CABGA256 \
  --lpf "$OUT_DIR/pinout.lpf" \
  2>&1 | tee "$OUT_DIR/log/nextpnr-ecp5.log"

ecppack \
  --svf "$OUT_DIR/greymecha_uart_echo.svf" \
  "$OUT_DIR/greymecha_uart_echo.config" \
  "$OUT_DIR/greymecha_uart_echo.bit" \
  2>&1 | tee "$OUT_DIR/log/ecppack.log"

ls -lh "$OUT_DIR/greymecha_uart_echo.bit"
