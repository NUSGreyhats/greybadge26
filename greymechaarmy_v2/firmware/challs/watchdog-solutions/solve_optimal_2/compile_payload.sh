#!/usr/bin/env bash
set -euo pipefail

payload_dir="${1:-payload}"
out_dir="${2:-build}"
payload_name="${PAYLOAD_NAME:-payload}"

if [[ ! -d "$payload_dir" ]]; then
  echo "payload directory not found: $payload_dir" >&2
  exit 1
fi

for required in startup.S main.c linker.ld; do
  if [[ ! -f "$payload_dir/$required" ]]; then
    echo "missing $payload_dir/$required" >&2
    exit 1
  fi
done

mkdir -p "$out_dir"

cc="${RISCV_CC:-riscv64-unknown-elf-gcc}"
objcopy="${RISCV_OBJCOPY:-riscv64-unknown-elf-objcopy}"
objdump="${RISCV_OBJDUMP:-riscv64-unknown-elf-objdump}"

elf="$out_dir/$payload_name.elf"
bin="$out_dir/$payload_name.bin"
wdog="$out_dir/$payload_name.wdog"
wdog_hex="$out_dir/$payload_name.wdog.hex"
dis="$out_dir/$payload_name.dis"

"$cc" \
  -march=rv32i \
  -mabi=ilp32 \
  -nostdlib \
  -ffreestanding \
  -fno-builtin \
  -Wall \
  -Wextra \
  -O3 \
  -T "$payload_dir/linker.ld" \
  "$payload_dir/startup.S" \
  "$payload_dir/main.c" \
  -o "$elf"

"$objcopy" -O binary "$elf" "$bin"

python3 pack_wdog.py "$bin" "$wdog"
python3 - "$wdog" "$wdog_hex" <<'PY'
import sys
from pathlib import Path

data = Path(sys.argv[1]).read_bytes()
Path(sys.argv[2]).write_text("\n".join(f"{byte:02x}" for byte in data) + "\n")
PY

if [[ "${PAYLOAD_OBJDUMP:-1}" == "1" ]]; then
  if ! python3 - "$objdump" "$elf" "$dis" <<'PY'
import subprocess
import sys
from pathlib import Path

objdump, elf_path, dis_path = sys.argv[1:]
with Path(dis_path).open("wb") as out:
    result = subprocess.run([objdump, "-d", elf_path], stdout=out, stderr=subprocess.PIPE)
if result.returncode != 0:
    Path(dis_path).write_text(
        f"objdump failed for {elf_path}\n"
        "ELF, binary, and WDOG packet were still produced.\n"
    )
PY
  then
    {
      echo "objdump wrapper failed for $elf"
      echo "ELF, binary, and WDOG packet were still produced."
    } > "$dis"
  fi
else
  {
    echo "disassembly skipped"
    echo "Set PAYLOAD_OBJDUMP=1 to generate this file with $objdump."
  } > "$dis"
fi

echo "$wdog"
