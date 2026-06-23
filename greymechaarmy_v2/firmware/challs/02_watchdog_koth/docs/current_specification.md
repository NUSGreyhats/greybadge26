# Watchdog KOTH Current Specification

This document specifies the current codebase implementation. It is organized around
the same five cooperating parts as `docs/plan_sectioned/`, but describes the present
design state instead of the target plan.

## 1. Softcore

### Concept

The system uses PicoRV32 as the challenge CPU. The CPU fetches boot firmware from
the boot memory region, receives a UART payload into payload RAM, and jumps to that
payload with the stack pointer placed at the top of stack RAM.

The SoC can also be driven directly by simulation testbenches. This is controlled by
the `cpu_enable` input on `watchdog_koth_top`: when disabled, the external test bus
drives `soc_bus`; when enabled, PicoRV32 owns the bus.

### Implementation Details

- Real PicoRV32 source lives in `rtl/core/picorv32.v`.
- CPU integration lives in `rtl/top/watchdog_koth_top.v`.
- The CPU reset vector is `0x0000_0000`.
- The configured stack address is `0x0000_d000`, which is immediately above the
  `0x0000_c000` to `0x0000_cfff` stack RAM window.
- The bus uses a single-cycle accepted-transaction pulse:
  - `accept = valid && !ready_reg`
  - RAM writes occur only on `accept`.
  - MMIO peripherals receive `accept && sel_*`.
- This handshake follows the proven wiring style inspected from the existing
  `custom_fpga_spi` PicoRV32 project and prevents repeated peripheral writes while
  PicoRV32 holds `mem_valid` until `mem_ready`.

### Memory Map

```text
0x0000_0000 - 0x0000_7fff  boot firmware memory
0x0000_8000 - 0x0000_bfff  payload code/data RAM
0x0000_c000 - 0x0000_cfff  payload stack RAM
0x1000_0000 - 0x1000_00ff  UART MMIO
0x1000_0100 - 0x1000_01ff  LED/status MMIO
0x1000_0200 - 0x1000_02ff  watchdog MMIO
0x1000_0300 - 0x1000_03ff  reset/status MMIO
0x1000_1000 - 0x1000_1fff  display/SPI bridge MMIO
0x2000_0000 - 0x2000_00ff  flag ROM/peripheral
```

Unmapped reads return `0xbad0_add5` and assert the bus `fault` signal.

### Acceptance Criteria

- PicoRV32 boots real compiled firmware from the simulated boot image.
- Direct bus tests can read and write RAM and MMIO without enabling the CPU.
- Peripheral writes occur once per CPU store.
- The UART boot log is not duplicated.
- The uploaded starter payload runs on the simulated PicoRV32 core and updates LEDs.

### Test Plan

Run the current regression under WSL:

```sh
bash sim/scripts/run_peripheral_tests.sh
bash sim/scripts/run_soc_tests.sh
bash sim/scripts/run_cpu_boot_test.sh
bash sim/scripts/run_uart_upload_led_test.sh
python3 -m pytest tests/unit/test_payload_pack.py -q
```

Expected current result:

```text
PASS: tb_peripherals
PASS: tb_soc_bus
PASS: tb_cpu_boot
PASS: tb_uart_upload_led
3 passed
```

### Final Hardware Implementation

`rtl/top/board_greymecha_top.v` instantiates `watchdog_koth_top` with
`cpu_enable=1`. Board LED outputs are wired to the LED MMIO register output. OLED SPI
signals are exposed as `oled_scl`, `oled_sda`, `oled_dc`, `oled_cs`, and `oled_rst`.

The GreyMecha smoke top uses a real serial UART bridge between the RP2350
interconnect pins and the byte-level SoC UART interface. The verified board wiring
is:

```text
RP2350 GP8  -> FPGA interconnect[0]  UART RX into FPGA
FPGA interconnect[1] -> RP2350 GP9   UART TX from FPGA
interconnect[7:2] are tri-stated
```

The same packed `WDOG` payload format is used in simulation and on hardware.

## 2. Boot Firmware Over UART

### Concept

The boot firmware provides a small monitor that reports reset state, runs self-tests,
waits for a packed UART payload, copies the payload into RAM, arms the watchdog, and
jumps to the payload entry address.

### Implementation Details

Boot firmware sources are in `firmware/bootloader/`:

- `main.c` reports reset reason, runs self-test, prints readiness/status strings, and
  loops waiting for uploads.
- `loader.c` implements the UART upload parser and payload copy.
- `startup.S` provides reset/startup and payload jump assembly.
- `linker.ld` places firmware into the boot region.
- `firmware/scripts/build_bootloader.sh` builds the bootloader image.

The upload format is:

```text
offset  size  meaning
0x00    4     ASCII magic "WDOG"
0x04    4     little-endian payload length
0x08    N     raw payload bytes
```

The firmware rejects empty payloads and payloads larger than the 16 KiB payload RAM
region.

Current boot status strings:

```text
BOOT: SELFTEST_OK
BOOT: SELFTEST_FAIL
BOOT: READY
BOOT: UPLOAD_ERROR
BOOT: LOADED
BOOT: CYCLE_START <hex64>
BOOT: RUNNING
BOOT: CYCLE_END <hex64>
BOOT: CYCLE_DELTA <hex64>
BOOT: DONE
BOOT: WATCHDOG_RESET
BOOT: REGION_RESET
BOOT: PAYLOAD_FAULT
BOOT: SUCCESS
BOOT: RESET_UNKNOWN
```

After a returning payload, the bootloader prints cycle end, cycle delta, `BOOT: DONE`,
and then loops back to `BOOT: READY` for the next upload. Cycle values are 64-bit
hexadecimal values.

### Acceptance Criteria

- Boot firmware builds into an ELF/HEX image loadable by simulation.
- The CPU boot test prints `SELFTEST_OK` and `READY`.
- The UART upload path accepts a valid `WDOG` packet.
- After upload, firmware prints `BOOT: LOADED`, `BOOT: CYCLE_START <hex64>`,
  and `BOOT: RUNNING`.
- The payload is written into payload RAM and executed by PicoRV32.
- A returning payload produces `BOOT: CYCLE_END <hex64>`, `BOOT: CYCLE_DELTA <hex64>`,
  `BOOT: DONE`, and another `BOOT: READY`.

### Test Plan

Build and boot firmware only:

```sh
bash sim/scripts/run_cpu_boot_test.sh
```

Simulate the full upload path:

```sh
bash sim/scripts/run_uart_upload_led_test.sh
```

The UART upload test builds the bootloader, builds the starter LED C payload, packs
the payload, feeds it through the simulated UART receive interface, waits for the
boot status strings, and checks that the payload writes the expected LED values.

### Final Hardware Implementation

The board implementation uses the UART bridge in `rtl/peripherals/uart_serial_bridge.v`
and the host-side uploader `tools/upload_payload_uart.ps1`. The uploader builds the
payload, packs it as `WDOG`, programs the GreyMecha smoke bitstream through the
CircuitPython harness, sends the payload over the RP2350-FPGA UART path, and captures
the UART transcript.

## 3. Watchdog

### Concept

The watchdog is a CPU-controlled MMIO peripheral. Firmware or payload code can enable
or disable it. This deliberately creates a solve path where the participant disables
the watchdog from software before meeting the timeout condition.

### Implementation Details

The watchdog RTL is `rtl/peripherals/watchdog.v`.

Register map relative to `WATCHDOG_BASE = 0x1000_0200`:

```text
0x00  CTRL     bit 0 enable, bit 1 arm, bit 2 clear counter on write
0x04  LIMIT    timeout limit
0x08  COUNTER  current counter, writable for tests/firmware
0x0c  STATUS   bit 0 enabled, bit 1 armed, bit 2 timeout
0x10  BASE     payload base address
0x14  END      payload end address
```

On reset:

- `enabled = 0`
- `armed = 0`
- `timeout = 0`
- `counter = 0`
- `limit = 0x0010_0000`
- `payload_base = PAYLOAD_BASE`
- `payload_end = PAYLOAD_END`

Firmware currently writes a full 32-bit address-space region:

```text
WATCHDOG_BASE + 0x10 = 0x00000000
WATCHDOG_BASE + 0x14 = 0xffffffff
WATCHDOG_BASE + 0x00 = WATCHDOG_ENABLE | WATCHDOG_ARM | WATCHDOG_CLEAR
```

`soc_bus.v` marks payload execution active on the first accepted instruction fetch
inside the configured region. Once active, the watchdog increments once per
FPGA clock cycle while armed and enabled. A timeout records `RESET_WATCHDOG` and
requests a soft CPU reset.

Region enforcement is part of watchdog enforcement. Once payload execution is
active, instruction fetches outside the configured region record `RESET_REGION` and
request a soft CPU reset only while the watchdog is enabled and armed. Because the
bootloader configures the region as `0x00000000..0xffffffff`, region reset is not
expected in the normal bootloader flow. Timeout counting remains active. If payload
code disables the watchdog through `CTRL.enable=0`, timeout counting and
region-reset enforcement both stop, while the watchdog MMIO registers remain
readable and writable.

### Acceptance Criteria

Current acceptance:

- Watchdog registers are readable/writable over MMIO.
- CPU can set and clear `enabled` and `armed`.
- The counter can be cleared by writing CTRL bit 2.
- The design preserves the intended software solve path: writing CTRL with bit 0
  cleared disables the watchdog.

- Payload execution activates true cycle counting.
- Timeout updates reset reason to `RESET_WATCHDOG`.
- Timeout produces the intended board-visible reset/restart behavior.
- The bootloader's full-map region configuration prevents watchdog-owned region resets.
- Disabling the watchdog suppresses timeout resets.

### Test Plan

Current simulation:

```sh
bash sim/scripts/run_peripheral_tests.sh
bash sim/scripts/run_soc_tests.sh
bash sim/scripts/run_watchdog_payload_tests.sh
```

These tests should cover direct MMIO writes and reads for watchdog state.

`run_watchdog_payload_tests.sh` currently covers:

- Payload times out and reports `WATCHDOG_RESET`.
- Payload disables watchdog and continues without reset.

### Final Hardware Implementation

On the GreyMecha/Army board, the watchdog has been proven with payloads covering:

- A timeout payload that does not disable or service the watchdog and should produce
  `WATCHDOG_RESET`.
- A solve-path payload that disables the watchdog through MMIO and continues running.

The current uploader path is:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\upload_payload_uart.ps1 -Payload <name> -Drive D:\ -Port COM17
```

## 4. Flag Memory Peripheral

### Concept

The flag peripheral is a memory-mapped ROM-style device at `0x2000_0000`. It provides
the current challenge flag through a stable address range.

### Implementation Details

The current implementation is `rtl/peripherals/flag_rom.v`.

Current 32-bit little-endian words:

```text
0x2000_0000  0x7965_7267
0x2000_0004  0x696d_6d7b
0x2000_0008  0x7566_5f6f
0x2000_000c  0x7d7a_7a7a
```

These encode the text:

```text
grey{mmio_fuzzz}
```

### Acceptance Criteria

- Reads inside the flag window return deterministic data.
- Reads outside defined flag words return zero.
- The flag address range does not overlap RAM or MMIO peripherals.
- Firmware and payload code can reference the same flag base address from shared
  headers.

### Test Plan

Current direct bus testing:

```sh
bash sim/scripts/run_soc_tests.sh
```

Additional payload tests now present:

- `payloads/flag_probe` reads all public flag words and reports `FLAG_OK`.
- `payloads/disable_watchdog_flag_copy` disables the watchdog, reads the flag
  peripheral, prints the flag over UART, and sets LED `0xf2`.

### Final Hardware Implementation

If access should depend on watchdog state, payload behavior,
or a success register, that gate should be implemented in RTL and tested in
simulation before board deployment. The current implementation keeps the flag
readable so payload execution and watchdog behavior can be tested end to end.

## 5. Hardware Tooling

### Concept

The project is currently simulation-first. WSL hosts the working Icarus Verilog,
RISC-V firmware build, and Python unit test flow. Hardware integration should only
follow once the simulated CPU, bootloader, upload protocol, watchdog, flag path, and
display/SPI wiring are stable.

### Implementation Details

Current simulation/test assets:

- `sim/tb/tb_peripherals.v`
- `sim/tb/tb_soc_bus.v`
- `sim/tb/tb_cpu_boot.v`
- `sim/tb/tb_uart_upload_led.v`
- `sim/models/uart_model.v`
- `sim/models/display_sink.v`
- `sim/models/flag_model.v`
- `sim/scripts/run_peripheral_tests.sh`
- `sim/scripts/run_soc_tests.sh`
- `sim/scripts/run_cpu_boot_test.sh`
- `sim/scripts/run_uart_upload_led_test.sh`
- `sim/scripts/run_uart_upload_flag_probe_test.sh`
- `sim/scripts/run_watchdog_payload_tests.sh`
- `sim/scripts/run_disable_watchdog_flag_copy_test.sh`

Payload tooling:

- `tools/payload/pack_wdog.py` creates the `WDOG` upload packet.
- `tools/payload/build_payload.sh` builds payload ELF/bin/WDOG artifacts.
- `tools/upload_payload_uart.ps1` builds and uploads a named payload to the
  connected GreyMecha board.
- `tests/unit/test_payload_pack.py` verifies packet header, length, empty-payload
  rejection, and oversize-payload rejection.

Display/SPI implementation:

- `rtl/peripherals/simple_spi_master.v` was integrated from the proven
  `custom_fpga_spi` project.
- `rtl/peripherals/display_mmio.v` wraps the SPI master and exposes simulation
  strobe outputs plus physical SPI-style OLED pins.
- Board top maps SPI to `oled_scl`, `oled_sda`, `oled_dc`, `oled_cs`, and `oled_rst`.

### Acceptance Criteria

- All simulation scripts pass under WSL.
- The starter C payload is compiled, packed, uploaded through the simulated UART
  path, executed on the real PicoRV32 core, and observed through LED writes.
- The SPI master is included in all relevant simulation build scripts.
- The board top exposes the intended OLED SPI pins.

### Test Plan

Full current regression:

```sh
bash sim/scripts/run_peripheral_tests.sh
bash sim/scripts/run_soc_tests.sh
bash sim/scripts/run_cpu_boot_test.sh
bash sim/scripts/run_uart_upload_led_test.sh
python3 -m pytest tests/unit/test_payload_pack.py -q
```

Hardware tests already exercised:

- Build synthesis for the GreyMecha/Army FPGA target.
- Upload starter/LED payload.
- Upload flag probe payload.
- Upload watchdog timeout payload and observe `WATCHDOG_RESET`.
- Upload watchdog disabled payload and observe no reset.
- Upload watchdog-disabled payload and observe no watchdog reset.
- Upload disable-watchdog flag-copy payload and observe `grey{mmio_fuzzz}`.

### Final Hardware Implementation

The final hardware flow should use the GreyMecha/Army board wrapper, board pin
constraints, and the existing autorun harness. The harness should automate payload
upload, UART log capture, board reset, and expected LED/display observations. The
hardware flow should not be treated as accepted until the same behavior already
passes in simulation.

## Current Known Gaps

- Final cycle-budget calibration is intentionally not complete.
- Optimized timing-solve reference payload is intentionally left for later tuning.
- Flag ROM is a public static flag.
- Public/private/event flag profile separation still needs final release policy.
- Display SPI is wired and simulation-visible, but there is not yet a full OLED
  initialization payload or hardware display test.
- The RISC-V `objdump` tool can abort on at least one valid payload ELF; the payload
  builder now preserves the upload artifact and writes a diagnostic disassembly file
  in that case.

## Current Passing Verification

The following regression has passed in WSL with the current implementation:

```text
PASS: tb_peripherals
PASS: tb_soc_bus
SELFTEST_OK
READY
PASS: tb_cpu_boot
SELFTEST_OK
READY
LOADED
RUNNING
PASS: tb_uart_upload_led
3 passed
WATCHDOG_RESET
PASS: tb_uart_upload_watchdog
REGION_RESET
PASS: tb_uart_upload_watchdog
FLAG_BEGIN
grey{mmio_fuzzz}
FLAG_END
PASS: tb_uart_upload_led
```

The updated GreyMecha hardware image also passed UART payload tests for watchdog
timeout, watchdog disable, flag probe, and disable-watchdog flag copy.
