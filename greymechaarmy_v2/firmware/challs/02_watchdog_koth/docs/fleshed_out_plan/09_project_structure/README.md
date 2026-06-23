# 09 - Project Structure

This structure keeps the project aligned with the implementation order in [03 - Implementation Roadmap](../03_implementation_roadmap/README.md): update and simulate the softcore first, then test firmware and uploads in simulation, then move to GreyMecha/Army board automation.

## Recommended Directory Layout

```text
02_watchdog_koth/
  README.md
  Makefile

  docs/
    plan.md
    fleshed_out_plan/
    architecture/
      memory_map.md
      payload_abi.md
      uart_protocol.md
      watchdog_contract.md
      board_notes.md

  rtl/
    top/
      watchdog_koth_top.v
      board_greymecha_top.v
      sim_top.v
    core/
      picorv32.v
      soc_bus.v
      memory_map.vh
    peripherals/
      uart_mmio.v
      led_mmio.v
      display_mmio.v
      watchdog.v
      region_guard.v
      reset_reason.v
      flag_rom.v

  firmware/
    bootloader/
      main.c
      linker.ld
      startup.S
      uart.c
      uart.h
      loader.c
      loader.h
      selftest.c
      selftest.h
    include/
      mmio.h
      memory_map.h
      status_codes.h

  payloads/
    starter_ok/
      main.S
      linker.ld
    naive_c_flag_copy/
      main.c
      linker.ld
    optimized_asm_flag_copy/
      main.S
      linker.ld
    microbench/
      branch.S
      memory.S
      uart.S

  sim/
    tb/
      tb_peripherals.v
      tb_soc_boot.v
      tb_uart_upload.v
      tb_watchdog.v
      tb_region_guard.v
      tb_reference_payloads.v
    models/
      uart_model.v
      display_sink.v
      flag_model.v
    scripts/
      run_peripheral_tests.ps1
      run_soc_tests.ps1
      run_payload_tests.ps1
      collect_cycles.py

  tools/
    payload/
      build_payload.py
      pack_wdog.py
      disasm_payload.py
    host/
      upload_payload.py
      serial_expect.py
    board/
      run_greymecha_harness.ps1
      make_hardware_tests.py

  hardware/
    constraints/
      greybadge25.lpf
      greybadge26.lpf
    greymecha_tests/
      fpga_ready/
        run.py
      peripheral_selftest/
        run.py
      starter_upload/
        run.py
      watchdog_timeout/
        run.py
      region_reset/
        run.py
      naive_c_fails/
        run.py
      optimized_succeeds/
        run.py
      repeatability/
        run.py

  tests/
    unit/
      test_payload_pack.py
      test_serial_expect.py
    integration/
      test_sim_statuses.py
      test_cycle_budget.py
      test_board_harness_layout.py

  build/
    # generated, gitignored
```

## Directory Responsibilities

### `docs/`

Stores the planning and interface contracts. Keep `docs/plan.md` as the original rough plan. Keep the expanded plan under `docs/fleshed_out_plan/`.

The proposed `docs/architecture/` folder should hold implementation-facing contracts:

- `memory_map.md`: final address ranges and register offsets.
- `payload_abi.md`: entrypoint, stack pointer, payload limits, and success path.
- `uart_protocol.md`: `WDOG` upload format, status strings, and timeout behavior.
- `watchdog_contract.md`: cycle counting, reset reasons, and region rules.
- `board_notes.md`: Greybadge25/Greybadge26 schematic references, constraints, and board revision notes.

### `rtl/`

Contains the hardware design. Keep softcore integration and peripherals split by responsibility.

- `rtl/top/` owns board and simulation wrappers.
- `rtl/core/` owns PicoRV32 integration, bus decode, and shared memory-map constants.
- `rtl/peripherals/` owns memory-mapped devices and challenge enforcement blocks.

This split lets peripheral simulation happen before firmware exists.

### `firmware/`

Contains trusted bootloader code that runs before player payloads.

The bootloader should:

- Print `READY`.
- Run peripheral self-tests.
- Receive UART uploads.
- Clear payload memory.
- Arm the watchdog.
- Set `sp`.
- Jump to the payload entrypoint.
- Report reset reasons after failed attempts.

Do not put security-critical watchdog or region enforcement only in firmware, because player payloads may bypass firmware logic once execution starts.

### `payloads/`

Contains programs that use the same ABI players will use.

- `starter_ok/` should be public and prove upload/execution.
- `naive_c_flag_copy/` should be private and fail by watchdog timeout.
- `optimized_asm_flag_copy/` should be private and pass.
- `microbench/` should measure branch, memory, flag, and UART behavior.

Keep each payload independently buildable so cycle measurements are easy to reproduce.

### `sim/`

Contains testbenches, hardware models, and simulation runners.

Simulation should be layered:

1. Peripheral tests without firmware.
2. SoC boot tests with firmware.
3. UART upload tests.
4. Watchdog and region tests.
5. Reference payload cycle tests.

The UART model should drive the same byte stream as the host upload tool. This prevents simulation from testing a shortcut path that players cannot use.

### `tools/`

Contains host-side scripts.

- `tools/payload/` builds, packs, and disassembles payloads.
- `tools/host/` uploads payloads to simulator or board serial ports.
- `tools/board/` wraps GreyMecha/Army harness runs and generates board-test payload directories.

The board wrapper should call the existing autorun harness at:

```text
C:\Users\zunmun\Documents\Stuff\GitLab\school-work\Workspace\2026\challenge_creation_greyctf_finals\greymechaarmy_autorun_harness\harness\tools\badge_harness.py
```

### `hardware/`

Contains board-specific constraints and CircuitPython hardware-test drivers.

- `hardware/constraints/` should store LPF files derived from the verified target board schematic.
- `hardware/greymecha_tests/` should store one `run.py` directory per automated board test.

Each `run.py` should print exactly one final result line:

```text
RESULT PASS <test_name>
```

or:

```text
RESULT FAIL <test_name> <reason>
```

This makes harness output easy to parse in CI-like scripts or event validation logs.

### `tests/`

Contains Python-level tests for host tools and test-layout sanity.

Suggested responsibilities:

- Validate `WDOG` payload packing.
- Validate serial transcript matching.
- Validate expected simulation statuses.
- Validate cycle-budget summaries.
- Validate every hardware harness test directory has a `run.py`.

### `build/`

Generated artifacts only. This directory should be gitignored.

Expected contents:

- firmware objects and binaries
- payload binaries
- disassemblies
- simulation logs
- waveform dumps
- bitstreams
- board-test logs

## Build And Test Flow

Use the top-level `Makefile` as the main entrypoint.

Recommended targets:

```text
make sim-peripherals
make sim-boot
make sim-upload
make sim-watchdog
make sim-payloads
make payloads
make bitstream BOARD=greybadge25
make bitstream BOARD=greybadge26
make board-test TEST=fpga_ready DRIVE=E:\ PORT=COM7
make board-test-all DRIVE=E:\ PORT=COM7
```

The flow should enforce the intended order:

1. `sim-peripherals`
2. `sim-boot`
3. `sim-upload`
4. `sim-watchdog`
5. `sim-payloads`
6. `bitstream`
7. `board-test-all`

## Why This Structure Works

This layout keeps each concern isolated:

- RTL peripherals can be tested before firmware.
- Firmware can be tested before player payloads.
- Payloads can be tuned before hardware.
- Hardware tests can reuse the same payloads and status strings.
- GreyMecha/Army autorun tests live close to board constraints and board logs.

It also keeps public and private artifacts easier to separate. Starter payloads and public docs can be released, while optimized reference payloads, real flags, final threshold notes, and event logs can stay private.
