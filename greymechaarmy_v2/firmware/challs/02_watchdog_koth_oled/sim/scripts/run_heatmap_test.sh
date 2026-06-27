#!/usr/bin/env bash
set -euo pipefail

build_dir="${1:-build/sim_oled}"
mkdir -p "$build_dir"

iverilog \
  -o "$build_dir/tb_cpu_heatmap_pixels.vvp" \
  sim/tb/tb_cpu_heatmap_pixels.v \
  rtl/visual/cpu_heatmap_pixels.v

vvp "$build_dir/tb_cpu_heatmap_pixels.vvp"
