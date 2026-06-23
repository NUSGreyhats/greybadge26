#!/usr/bin/env bash
set -euo pipefail

build_dir="${1:-build/firmware}"
mkdir -p "$build_dir"

cc="${RISCV_CC:-riscv64-unknown-elf-gcc}"
objcopy="${RISCV_OBJCOPY:-riscv64-unknown-elf-objcopy}"
objdump="${RISCV_OBJDUMP:-riscv64-unknown-elf-objdump}"

cflags=(
  -march=rv32i
  -mabi=ilp32
  -nostdlib
  -ffreestanding
  -fno-builtin
  -Wall
  -Wextra
  -Os
  -I firmware/include
  -I firmware/bootloader
  -T firmware/bootloader/linker.ld
)

"$cc" "${cflags[@]}" \
  firmware/bootloader/startup.S \
  firmware/bootloader/main.c \
  firmware/bootloader/uart.c \
  firmware/bootloader/loader.c \
  firmware/bootloader/selftest.c \
  -o "$build_dir/bootloader.elf"

"$objcopy" -O binary "$build_dir/bootloader.elf" "$build_dir/bootloader.bin"
"$objdump" -d "$build_dir/bootloader.elf" > "$build_dir/bootloader.dis"
python3 - "$build_dir/bootloader.bin" "$build_dir/bootloader.hex" <<'PY'
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

echo "built $build_dir/bootloader.elf"
