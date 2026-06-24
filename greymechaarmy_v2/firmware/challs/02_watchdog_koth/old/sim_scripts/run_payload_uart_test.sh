#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
usage: sim/scripts/run_payload_uart_test.sh <payload-dir-or-name> [options]

Options:
  --expect-led <hex>          Require final LED value, e.g. f1 or 0xf1
  --expect-watchdog-reset     Require WATCHDOG_RESET in UART output
  --expect-region-reset       Require REGION_RESET in UART output
  --max-cycles <cycles>       Cycles to run after upload, default 300000
  --build-dir <dir>           Simulation output directory, default build/sim
  --firmware-dir <dir>        Firmware output directory, default build/firmware

Examples:
  sim/scripts/run_payload_uart_test.sh starter_led --expect-led 5a
  sim/scripts/run_payload_uart_test.sh flag_probe --expect-led f1
  sim/scripts/run_payload_uart_test.sh watchdog_timeout --expect-watchdog-reset --max-cycles 500000
EOF
}

if [[ $# -lt 1 ]]; then
  usage
  exit 2
fi

payload_arg="$1"
shift

build_dir="build/sim"
firmware_dir="build/firmware"
max_cycles="300000"
expect_led=""
expect_watchdog_reset=0
expect_region_reset=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --expect-led)
      [[ $# -ge 2 ]] || { usage; exit 2; }
      expect_led="${2#0x}"
      shift 2
      ;;
    --expect-watchdog-reset)
      expect_watchdog_reset=1
      shift
      ;;
    --expect-region-reset)
      expect_region_reset=1
      shift
      ;;
    --max-cycles)
      [[ $# -ge 2 ]] || { usage; exit 2; }
      max_cycles="$2"
      shift 2
      ;;
    --build-dir)
      [[ $# -ge 2 ]] || { usage; exit 2; }
      build_dir="$2"
      shift 2
      ;;
    --firmware-dir)
      [[ $# -ge 2 ]] || { usage; exit 2; }
      firmware_dir="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown option: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if [[ -d "$payload_arg" ]]; then
  payload_name="$(basename "$payload_arg")"
elif [[ -d "payloads/$payload_arg" ]]; then
  payload_name="$payload_arg"
else
  echo "payload directory not found: $payload_arg" >&2
  exit 1
fi

mkdir -p "$build_dir"

bash firmware/scripts/build_bootloader.sh "$firmware_dir"
bash tools/payload/build_payload.sh "$payload_arg" "build/payloads/$payload_name" >/dev/null

common_sources=(
  sim/tb/tb_uart_upload_payload.v
  rtl/top/watchdog_koth_top.v
  rtl/core/soc_bus.v
  rtl/core/picorv32.v
  rtl/peripherals/uart_mmio.v
  rtl/peripherals/led_mmio.v
  rtl/peripherals/display_mmio.v
  rtl/peripherals/simple_spi_master.v
  rtl/peripherals/watchdog.v
  rtl/peripherals/reset_reason.v
  rtl/peripherals/flag_rom.v
)

vvp_path="$build_dir/tb_uart_upload_payload.vvp"
upload_hex="build/payloads/$payload_name/$payload_name.wdog.hex"

iverilog \
  -I rtl/core \
  -I "$firmware_dir" \
  -DBOOT_HEX=\"$firmware_dir/bootloader.hex\" \
  -o "$vvp_path" \
  "${common_sources[@]}"

vvp_args=(
  "$vvp_path"
  "+UPLOAD_HEX=$upload_hex"
  "+MAX_CYCLES=$max_cycles"
)

if [[ -n "$expect_led" ]]; then
  vvp_args+=("+EXPECT_LED=$expect_led")
fi
if [[ "$expect_watchdog_reset" -eq 1 ]]; then
  vvp_args+=("+EXPECT_WATCHDOG_RESET")
fi
if [[ "$expect_region_reset" -eq 1 ]]; then
  vvp_args+=("+EXPECT_REGION_RESET")
fi

vvp "${vvp_args[@]}"
