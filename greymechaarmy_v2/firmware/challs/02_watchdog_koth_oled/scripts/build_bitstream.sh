#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OLD_ROOT="$ROOT/../02_watchdog_koth"
OUT_DIR="${1:-$ROOT/build/greymecha_watchdog_oled}"
PINOUT="${PINOUT:-$ROOT/pinout.lpf}"

mkdir -p "$OUT_DIR/log" "$ROOT/build/firmware"
cp "$PINOUT" "$OUT_DIR/pinout.lpf"

cd "$ROOT"

cc="${RISCV_CC:-riscv64-unknown-elf-gcc}"
objcopy="${RISCV_OBJCOPY:-riscv64-unknown-elf-objcopy}"
objdump="${RISCV_OBJDUMP:-riscv64-unknown-elf-objdump}"

"$cc" \
  -march=rv32i \
  -mabi=ilp32 \
  -nostdlib \
  -ffreestanding \
  -fno-builtin \
  -Wall \
  -Wextra \
  -Os \
  -I "$OLD_ROOT/firmware/include" \
  -I "$OLD_ROOT/firmware/bootloader" \
  -T "$OLD_ROOT/firmware/bootloader/linker.ld" \
  "$OLD_ROOT/firmware/bootloader/startup.S" \
  "$OLD_ROOT/firmware/bootloader/main.c" \
  "$OLD_ROOT/firmware/bootloader/uart.c" \
  "$OLD_ROOT/firmware/bootloader/loader.c" \
  "$OLD_ROOT/firmware/bootloader/selftest.c" \
  -o "$ROOT/build/firmware/bootloader.elf"
"$objcopy" -O binary "$ROOT/build/firmware/bootloader.elf" "$ROOT/build/firmware/bootloader.bin"
"$objdump" -d "$ROOT/build/firmware/bootloader.elf" > "$ROOT/build/firmware/bootloader.dis"
python3 - "$ROOT/build/firmware/bootloader.bin" "$ROOT/build/firmware/bootloader.hex" <<'PY'
import sys
from pathlib import Path

src = Path(sys.argv[1])
dst = Path(sys.argv[2])
data = src.read_bytes()
if len(data) > 0x8000:
    raise SystemExit(f"bootloader image too large: {len(data)} bytes")

lines = []
for offset in range(0, 0x8000, 4):
    chunk = data[offset:offset + 4].ljust(4, b"\x00")
    lines.append(f"{int.from_bytes(chunk, 'little'):08x}")
dst.write_text("\n".join(lines) + "\n")
PY
cat > "$ROOT/build/firmware/bootloader_path.vh" <<EOF
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
read_verilog -I $OLD_ROOT/rtl/core -I $ROOT/build/firmware -I $ROOT/rtl/oled -DSYNTH_BOOT_PATH_VH -DSYNTH_BOOT_CASE_VH \
  $OLD_ROOT/rtl/core/picorv32.v \
  $OLD_ROOT/rtl/core/soc_bus.v \
  $OLD_ROOT/rtl/peripherals/uart_mmio.v \
  $OLD_ROOT/rtl/peripherals/led_mmio.v \
  $OLD_ROOT/rtl/peripherals/display_mmio.v \
  $OLD_ROOT/rtl/peripherals/simple_spi_master.v \
  $OLD_ROOT/rtl/peripherals/uart_serial_bridge.v \
  $OLD_ROOT/rtl/peripherals/watchdog.v \
  $OLD_ROOT/rtl/peripherals/reset_reason.v \
  $OLD_ROOT/rtl/peripherals/flag_rom.v \
  rtl/oled/ecp5_oled_pll.v \
  rtl/oled/oled_init.v \
  rtl/oled/oled_stream.v \
  rtl/oled/oled_gc9a01.v \
  rtl/visual/cpu_fetch_cdc.v \
  rtl/visual/cpu_heatmap_pixels.v \
  rtl/top/watchdog_koth_oled_soc.v \
  rtl/top/greymecha_watchdog_oled_top.v
synth_ecp5 -top greymecha_watchdog_oled_top -json $OUT_DIR/watchdog_koth_oled.json
" 2>&1 | tee "$OUT_DIR/log/yosys.log"

nextpnr-ecp5 \
  --json "$OUT_DIR/watchdog_koth_oled.json" \
  --textcfg "$OUT_DIR/watchdog_koth_oled.config" \
  --25k \
  --package CABGA256 \
  --lpf "$OUT_DIR/pinout.lpf" \
  2>&1 | tee "$OUT_DIR/log/nextpnr-ecp5.log"

ecppack \
  --svf "$OUT_DIR/watchdog_koth_oled.svf" \
  "$OUT_DIR/watchdog_koth_oled.config" \
  "$OUT_DIR/watchdog_koth_oled.bit" \
  2>&1 | tee "$OUT_DIR/log/ecppack.log"

ls -lh "$OUT_DIR/watchdog_koth_oled.bit"
