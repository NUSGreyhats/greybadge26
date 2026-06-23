#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: $0 <payload-dir-or-name> [build-dir]" >&2
  exit 2
fi

payload_arg="$1"
if [[ -d "$payload_arg" ]]; then
  payload_dir="$payload_arg"
  payload_name="$(basename "$payload_dir")"
elif [[ -d "payloads/$payload_arg" ]]; then
  payload_dir="payloads/$payload_arg"
  payload_name="$payload_arg"
else
  echo "payload directory not found: $payload_arg" >&2
  exit 1
fi

build_dir="${2:-build/payloads/$payload_name}"
mkdir -p "$build_dir"

for required in startup.S main.c linker.ld; do
  if [[ ! -f "$payload_dir/$required" ]]; then
    echo "missing $payload_dir/$required" >&2
    exit 1
  fi
done

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
  -T "$payload_dir/linker.ld" \
  "$payload_dir/startup.S" \
  "$payload_dir/main.c" \
  -o "$build_dir/$payload_name.elf"

"$objcopy" -O binary "$build_dir/$payload_name.elf" "$build_dir/$payload_name.bin"
if [[ "${PAYLOAD_OBJDUMP:-1}" == "1" ]]; then
  if ! python3 - "$objdump" "$build_dir/$payload_name.elf" "$build_dir/$payload_name.dis" <<'PY'
import subprocess
import sys
from pathlib import Path

objdump, elf_path, dis_path = sys.argv[1:]
with Path(dis_path).open("wb") as out:
    result = subprocess.run([objdump, "-d", elf_path], stdout=out, stderr=subprocess.PIPE)
if result.returncode != 0:
    Path(dis_path).write_text(
        f"objdump failed for {elf_path}\n"
        "ELF and binary were still produced; use readelf/nm or another disassembler to inspect this payload.\n"
    )
    sys.exit(0)
PY
  then
    {
      echo "objdump wrapper failed for $build_dir/$payload_name.elf"
      echo "ELF and binary were still produced; use readelf/nm or another disassembler to inspect this payload."
    } > "$build_dir/$payload_name.dis"
  fi
else
  {
    echo "disassembly skipped"
    echo "Set PAYLOAD_OBJDUMP=1 to generate this file with $objdump."
  } > "$build_dir/$payload_name.dis"
fi

python3 tools/payload/pack_wdog.py "$build_dir/$payload_name.bin" "$build_dir/$payload_name.wdog"
python3 - "$build_dir/$payload_name.wdog" "$build_dir/$payload_name.wdog.hex" <<'PY'
import sys
from pathlib import Path

data = Path(sys.argv[1]).read_bytes()
Path(sys.argv[2]).write_text("\n".join(f"{byte:02x}" for byte in data) + "\n")
PY

echo "$build_dir/$payload_name.wdog"
