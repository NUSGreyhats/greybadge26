#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT_DIR="${1:-$ROOT/build/greymecha_smoke}"
PINOUT="${PINOUT:-/mnt/c/Users/zunmun/Documents/Stuff/Github/WORK/GreyHats/greybadge25/firmware/ecp5/main/pinout.lpf}"

mkdir -p "$OUT_DIR/log"
cp "$PINOUT" "$OUT_DIR/pinout.lpf"

cd "$ROOT"

bash firmware/scripts/build_bootloader.sh build/firmware
cat > build/firmware/bootloader_path.vh <<EOF
\`define BOOT_HEX "$ROOT/build/firmware/bootloader.hex"
EOF
python3 - <<'PY'
from pathlib import Path

hex_path = Path("build/firmware/bootloader.hex")
case_path = Path("build/firmware/boot_rom_case.vh")
lines = [
    "    function [31:0] boot_rom_word;\n",
    "        input [12:0] word_addr;\n",
    "        begin\n",
    "            case (word_addr)\n",
]
for index, raw in enumerate(hex_path.read_text().splitlines()):
    word = raw.strip()
    if word and word != "00000000":
        lines.append(f"                13'd{index}: boot_rom_word = 32'h{word};\n")
lines.extend([
    "                default: boot_rom_word = 32'h0000_0000;\n",
    "            endcase\n",
    "        end\n",
    "    endfunction\n",
])
case_path.write_text("".join(lines))
PY

yosys -p "
read_verilog -I rtl/core -I build/firmware -DSYNTH_BOOT_PATH_VH -DSYNTH_BOOT_CASE_VH \
  rtl/core/picorv32.v \
  rtl/core/soc_bus.v \
  rtl/peripherals/uart_mmio.v \
  rtl/peripherals/led_mmio.v \
  rtl/peripherals/display_mmio.v \
  rtl/peripherals/simple_spi_master.v \
  rtl/peripherals/uart_serial_bridge.v \
  rtl/peripherals/watchdog.v \
  rtl/peripherals/reset_reason.v \
  rtl/peripherals/flag_rom.v \
  rtl/top/watchdog_koth_top.v \
  rtl/top/greymecha_smoke_top.v
synth_ecp5 -top greymecha_smoke_top -json $OUT_DIR/watchdog_koth_smoke.json
" 2>&1 | tee "$OUT_DIR/log/yosys.log"

nextpnr-ecp5 \
  --json "$OUT_DIR/watchdog_koth_smoke.json" \
  --textcfg "$OUT_DIR/watchdog_koth_smoke.config" \
  --25k \
  --package CABGA256 \
  --lpf "$OUT_DIR/pinout.lpf" \
  2>&1 | tee "$OUT_DIR/log/nextpnr-ecp5.log"

ecppack \
  --svf "$OUT_DIR/watchdog_koth_smoke.svf" \
  "$OUT_DIR/watchdog_koth_smoke.config" \
  "$OUT_DIR/watchdog_koth_smoke.bit" \
  2>&1 | tee "$OUT_DIR/log/ecppack.log"

ls -lh "$OUT_DIR/watchdog_koth_smoke.bit"
