# 01 - Overview

## Purpose

Watchdog KOTH is a timing-focused FPGA CTF challenge. Players upload RISC-V code to a PicoRV32 softcore over UART. Their code must recover a flag from a protected memory path before watchdog logic resets the core.

The intended difficulty comes from cycle pressure, not from hiding basic interfaces. A naive C payload should be functionally correct but too slow. A solver who profiles the softcore, studies the generated assembly, and writes a compact payload should succeed.

## System Shape

The challenge has five cooperating parts:

1. A PicoRV32 softcore configured for the target ECP5 FPGA.
2. Boot firmware that receives player payloads over UART.
3. A watchdog/region-enforcement block that payloads cannot bypass.
4. A flag memory region or flag peripheral.
5. Simulation and hardware tooling that run the same payload format.

The player-visible contract must stay stable across simulation and hardware. If simulation accepts raw binary payloads at a fixed entrypoint, the GreyMecha/Army board runner should accept the same payload form.

## How To Achieve This Requirement

Start by making the challenge boring and deterministic:

1. Define the payload memory map and ABI before writing challenge logic.
2. Bring up UART TX/RX with a minimal loader banner.
3. Execute a one-instruction or LED-toggle payload from uploaded memory.
4. Add watchdog cycle expiry.
5. Add PC-region enforcement.
6. Add data-bus enforcement only after PC enforcement is stable.
7. Add flag access.
8. Tune the threshold against reference payloads.

Do not tune the watchdog until upload, reset, and status reporting are repeatable. Otherwise cycle measurements will be contaminated by loader bugs.

## Simulation Plan

Simulate at three levels:

1. Unit-level RTL simulation for the watchdog and address decoder.
2. SoC-level simulation for PicoRV32, memory, UART, watchdog, and flag path.
3. Player-flow simulation that sends a payload through the UART model instead of preloading memory.

The minimum SoC simulation should expose:

- `payload_active`
- `payload_start_cycle`
- `watchdog_counter`
- `watchdog_limit`
- `reset_reason`
- instruction address
- memory address, write enable, and read enable
- UART RX/TX bytes

Run these overview smoke simulations:

- Boot firmware reaches `READY`.
- Minimal payload uploads and writes `OK`.
- Infinite loop payload resets with `WATCHDOG_RESET`.
- Bad jump payload resets with `REGION_RESET`.
- Dummy optimized payload reaches `SUCCESS`.

## GreyMecha/Army Board Run Plan

Use the board references in this order:

1. Confirm target board revision: Greybadge25 or Greybadge26/GreyMechaArmy v2.
2. Open the matching KiCad project and verify FPGA, UART, LEDs, display, clock, and reset connectivity.
3. For Greybadge25, reuse the ECP5 flow under `firmware/ecp5`, especially the UART and OLED tests.
4. For Greybadge26, validate schematic compatibility first, then port the known ECP5 test flow if no newer Makefile exists.
5. Build the bitstream with an ECP5-25 CABGA256 flow equivalent to the discovered Greybadge25 Makefile.
6. Program the board using the existing project programmer flow.
7. Connect the UART host to the board interface documented by the schematic.
8. Run the same host upload script used by simulation and record the status log.

Board smoke pass:

- Power-on prints `READY`.
- Uploading a minimal payload changes LED state and prints `OK`.
- Reset returns the loader to `READY`.
