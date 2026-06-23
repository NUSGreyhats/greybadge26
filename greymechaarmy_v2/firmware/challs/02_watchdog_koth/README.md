# Watchdog KOTH

Small PicoRV32-based FPGA challenge for GreyMecha/Army. The boot firmware receives a
packed UART payload, copies it into payload RAM, arms a watchdog, and jumps to the
uploaded code. Payloads can either beat the watchdog or intentionally disable it
through MMIO. The watchdog region is configured to cover the full 32-bit address
map, so region reset is not expected in the normal bootloader flow.

## Requirements

Most project tooling is expected to run in WSL.

- `iverilog` and `vvp`
- RISC-V bare-metal GCC tools, usually `riscv64-unknown-elf-gcc`,
  `riscv64-unknown-elf-objcopy`, and `riscv64-unknown-elf-objdump`
- Python 3
- For hardware builds: `yosys`, `nextpnr-ecp5`, and `ecppack`
- For GreyMecha upload: CircuitPython board mounted as a drive and an available COM
  port

Run commands from the repository root.

## Canonical Scripts

Use the top-level `scripts/` directory for normal build and board workflows:

```sh
wsl bash -lc "bash scripts/build_bitstream.sh"
wsl bash -lc "bash scripts/compile_payload.sh <payload>"
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\upload_greymecha.ps1 -Payload <name> -Drive D:\ -Port COM17
```

The upload script builds the named payload before upload. Add `-BuildBitstream` to
rebuild the FPGA image first:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\upload_greymecha.ps1 -Payload <name> -Drive D:\ -Port COM17 -BuildBitstream
```

Older script locations are kept as compatibility wrappers where useful. Archived
copies of old script bodies live under `old/`.

## Memory Map

```text
0x0000_0000 - 0x0000_7fff  boot firmware
0x0000_8000 - 0x0000_bfff  payload code/data RAM
0x0000_c000 - 0x0000_cfff  payload stack RAM
0x1000_0000 - 0x1000_00ff  UART MMIO
0x1000_0100 - 0x1000_01ff  LED MMIO
0x1000_0200 - 0x1000_02ff  watchdog MMIO
0x1000_0300 - 0x1000_03ff  reset/status/cycle MMIO
0x1000_1000 - 0x1000_1fff  display/SPI MMIO
0x2000_0000 - 0x2000_00ff  flag ROM/peripheral
```

More detail is in `docs/architecture/memory_map.md`.

## Run Simulation Tests

Run the main regression:

```sh
wsl bash -lc "bash sim/scripts/run_peripheral_tests.sh && bash sim/scripts/run_soc_tests.sh && bash sim/scripts/run_cpu_boot_test.sh && bash sim/scripts/run_uart_upload_led_test.sh && bash sim/scripts/run_uart_upload_flag_probe_test.sh && bash sim/scripts/run_watchdog_payload_tests.sh && bash sim/scripts/run_disable_watchdog_flag_copy_test.sh && bash sim/scripts/run_returning_payload_test.sh && python3 -m pytest tests/unit/test_payload_pack.py -q"
```

Useful individual tests:

```sh
wsl bash -lc "bash sim/scripts/run_payload_uart_test.sh starter_led --expect-led 5a"
wsl bash -lc "bash sim/scripts/run_payload_uart_test.sh flag_probe --expect-led f1 --max-cycles 500000"
wsl bash -lc "bash sim/scripts/run_payload_uart_test.sh watchdog_timeout --expect-watchdog-reset --max-cycles 500000"
```

Compatibility wrappers are also kept:

```sh
wsl bash -lc "bash sim/scripts/run_uart_upload_led_test.sh"
wsl bash -lc "bash sim/scripts/run_uart_upload_flag_probe_test.sh"
wsl bash -lc "bash sim/scripts/run_watchdog_payload_tests.sh"
wsl bash -lc "bash sim/scripts/run_disable_watchdog_flag_copy_test.sh"
wsl bash -lc "bash sim/scripts/run_returning_payload_test.sh"
```

UART output from the simulated SoC is printed directly in the `vvp` console.

To run a custom payload without a pass/fail expectation:

```sh
wsl bash -lc "bash sim/scripts/run_payload_uart_test.sh my_payload --max-cycles 500000"
```

## Build A Payload

A payload directory must contain:

```text
startup.S
main.c
linker.ld
```

Build a named payload:

```sh
wsl bash -lc "bash scripts/compile_payload.sh starter_led"
```

The script also accepts a payload directory path and an optional build directory:

```sh
wsl bash -lc "bash scripts/compile_payload.sh payloads/starter_led build/payloads/starter_led"
```

Build artifacts are written to:

```text
build/payloads/<payload_name>/
```

The important upload artifact is:

```text
build/payloads/<payload_name>/<payload_name>.wdog
```

Existing payload examples:

- `starter_led`: simple LED write payload.
- `flag_probe`: reads the flag peripheral and prints `FLAG_OK`.
- `watchdog_timeout`: intentionally times out and triggers `WATCHDOG_RESET`.
- `watchdog_disable`: disables the watchdog and keeps running.
- `watchdog_disable_bad_region`: historical region-enforcement payload. With the
  current full-map watchdog region, it is not expected to trigger `REGION_RESET`.
- `disable_watchdog_flag_copy`: disables the watchdog and prints the flag.

## Write Custom Payload Code

Create a new folder under `payloads/`, using `payloads/starter_led` or
`payloads/disable_watchdog_flag_copy` as a template.

Common MMIO addresses:

```c
#define UART_BASE      0x10000000u
#define LED_BASE       0x10000100u
#define WATCHDOG_BASE  0x10000200u
#define FLAG_BASE      0x20000000u
```

Disable the watchdog from payload code:

```c
*(volatile unsigned int *)(WATCHDOG_BASE + 0x00u) = 0u;
```

Read the flag:

```c
unsigned int word0 = *(volatile unsigned int *)(FLAG_BASE + 0x00u);
```

The current flag is:

```text
grey{mmio_fuzzz}
```

## Hardware Build

Build the GreyMecha smoke bitstream:

```sh
wsl bash -lc "bash scripts/build_bitstream.sh"
```

The bitstream is produced at:

```text
build/greymecha_smoke/watchdog_koth_smoke.bit
```

## Upload To GreyMecha

With the CircuitPython drive mounted and the serial port known:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\upload_greymecha.ps1 -Payload starter_led -Drive D:\ -Port COM17
```

Replace `starter_led`, `D:\`, and `COM17` as needed.

The uploader builds the payload, copies the board runner to the CircuitPython drive,
programs the FPGA bitstream, sends the packed payload over the RP2350-FPGA UART path,
and prints the UART transcript.

To rebuild the bitstream before upload:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\upload_greymecha.ps1 -Payload starter_led -Drive D:\ -Port COM17 -BuildBitstream
```

Known verified hardware payloads:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\upload_greymecha.ps1 -Payload watchdog_timeout -Drive D:\ -Port COM17
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\upload_greymecha.ps1 -Payload watchdog_disable -Drive D:\ -Port COM17
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\upload_greymecha.ps1 -Payload watchdog_disable_bad_region -Drive D:\ -Port COM17
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\upload_greymecha.ps1 -Payload disable_watchdog_flag_copy -Drive D:\ -Port COM17
```

Expected behavior:

- `watchdog_timeout`: reports `WATCHDOG_RESET`.
- `watchdog_disable`: runs without watchdog reset.
- `disable_watchdog_flag_copy`: prints `grey{mmio_fuzzz}`.

## CircuitPython UART Console Runner

For a lower-level board-side runner, stage these files on CIRCUITPY:

```text
/hackin7/watchdog_koth_board_test/watchdog_koth_smoke.bit
/hackin7/watchdog_koth_board_test/upload_payload.wdog
```

Then run:

```text
hardware/board_tests/greymecha_uart_console_run.py
```

The script uploads the bitstream, sends the `.wdog` file into the FPGA UART, prints
RISC-V UART output as `[RISCV]: ...`, and forwards typed USB-serial characters back
to the FPGA UART while the console loop is open.

## Notes

- Cycle-budget calibration and optimized solve payload tuning are intentionally left
  for later.
- `riscv64-unknown-elf-objdump` may abort on some valid payload ELFs. The payload
  builder still emits the binary and `.wdog` upload artifact; it writes a diagnostic
  `.dis` file if disassembly fails.
- The current simulator flow is batch-oriented. It can run custom C payloads and show
  UART output, but it is not yet an interactive UART shell.
