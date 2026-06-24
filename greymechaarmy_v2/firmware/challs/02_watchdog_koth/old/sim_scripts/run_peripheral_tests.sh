#!/usr/bin/env bash
set -euo pipefail

build_dir="${1:-build/sim}"
mkdir -p "$build_dir"

iverilog \
  -I rtl/core \
  -o "$build_dir/tb_peripherals.vvp" \
  sim/tb/tb_peripherals.v \
  rtl/peripherals/uart_mmio.v \
  rtl/peripherals/led_mmio.v \
  rtl/peripherals/watchdog.v \
  rtl/peripherals/flag_rom.v

vvp "$build_dir/tb_peripherals.vvp"
