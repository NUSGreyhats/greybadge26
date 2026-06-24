#!/usr/bin/env bash
set -euo pipefail

build_dir="${1:-build/payloads/led_counter}"
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
  -T payloads/led_counter/linker.ld \
  payloads/led_counter/startup.S \
  payloads/led_counter/main.c \
  -o "$build_dir/led_counter.elf"

"$objcopy" -O binary "$build_dir/led_counter.elf" "$build_dir/led_counter.bin"
"$objdump" -d "$build_dir/led_counter.elf" > "$build_dir/led_counter.dis"

python3 tools/payload/pack_wdog.py "$build_dir/led_counter.bin" "$build_dir/led_counter.wdog"
python3 - "$build_dir/led_counter.wdog" "$build_dir/led_counter.wdog.hex" <<'PY'
import sys
from pathlib import Path

data = Path(sys.argv[1]).read_bytes()
Path(sys.argv[2]).write_text("\n".join(f"{byte:02x}" for byte in data) + "\n")
PY

echo "built $build_dir/led_counter.elf"
