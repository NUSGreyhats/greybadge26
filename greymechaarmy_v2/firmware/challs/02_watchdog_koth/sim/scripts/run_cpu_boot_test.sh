#!/usr/bin/env bash
set -euo pipefail

build_dir="${1:-build/sim}"
firmware_dir="${2:-build/firmware}"
mkdir -p "$build_dir"

bash firmware/scripts/build_bootloader.sh "$firmware_dir"

iverilog \
  -I rtl/core \
  -DBOOT_HEX=\"${firmware_dir}/bootloader.hex\" \
  -o "$build_dir/tb_cpu_boot.vvp" \
  sim/tb/tb_cpu_boot.v \
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

vvp "$build_dir/tb_cpu_boot.vvp"
