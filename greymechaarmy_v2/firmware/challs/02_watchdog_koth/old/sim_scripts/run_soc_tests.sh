#!/usr/bin/env bash
set -euo pipefail

build_dir="${1:-build/sim}"
mkdir -p "$build_dir"

iverilog \
  -I rtl/core \
  -o "$build_dir/tb_soc_bus.vvp" \
  sim/tb/tb_soc_bus.v \
  rtl/top/watchdog_koth_top.v \
  rtl/core/soc_bus.v \
  rtl/core/picorv32.v \
  rtl/peripherals/uart_mmio.v \
  rtl/peripherals/led_mmio.v \
  rtl/peripherals/display_mmio.v \
  rtl/peripherals/simple_spi_master.v \
  rtl/peripherals/watchdog.v \
  rtl/peripherals/reset_reason.v \
  rtl/peripherals/flag_rom.v

vvp "$build_dir/tb_soc_bus.vvp"
