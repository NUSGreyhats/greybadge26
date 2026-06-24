#!/usr/bin/env bash
set -euo pipefail

build_dir="${1:-build/payloads/starter_led}"
mkdir -p "$build_dir"

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
  -T payloads/starter_led/linker.ld \
  payloads/starter_led/startup.S \
  payloads/starter_led/main.c \
  -o "$build_dir/starter_led.elf"

"$objcopy" -O binary "$build_dir/starter_led.elf" "$build_dir/starter_led.bin"
"$objdump" -d "$build_dir/starter_led.elf" > "$build_dir/starter_led.dis"

python3 tools/payload/pack_wdog.py "$build_dir/starter_led.bin" "$build_dir/starter_led.wdog"
python3 - "$build_dir/starter_led.wdog" "$build_dir/starter_led.wdog.hex" <<'PY'
import sys
from pathlib import Path

data = Path(sys.argv[1]).read_bytes()
Path(sys.argv[2]).write_text("\n".join(f"{byte:02x}" for byte in data) + "\n")
PY

echo "built $build_dir/starter_led.elf"
