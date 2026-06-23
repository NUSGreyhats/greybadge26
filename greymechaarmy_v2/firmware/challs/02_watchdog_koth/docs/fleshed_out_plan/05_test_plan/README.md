# 05 - Test Plan

## Test Layers

Use four layers:

1. Unit simulation for watchdog, address decoder, and UART loader primitives.
2. SoC simulation with PicoRV32 and memory-mapped peripherals.
3. Host-driven simulation that sends real UART upload streams.
4. GreyMecha/Army board runs using the final bitstream and host upload script.

The later layers should reuse the same payload binaries wherever possible.

## What To Simulate

Simulate these payload classes:

- `starter_ok`: writes a status byte and returns success.
- `bad_magic`: invalid header, no payload execution.
- `oversized`: payload larger than allowed range.
- `bad_jump_low`: jumps below payload base.
- `bad_jump_high`: jumps above payload limit.
- `infinite_loop`: watchdog timeout.
- `stack_probe`: writes within stack bounds.
- `stack_underflow`: violates stack bounds if enforced.
- `naive_c_flag_copy`: correct but too slow.
- `optimized_asm_flag_copy`: fast enough.

For each payload, the testbench should check terminal status and cycle count.

## How To Simulate

Build a self-checking testbench that models:

- clock and reset
- firmware ROM/RAM
- payload RAM
- UART RX byte injection
- UART TX capture
- flag memory
- watchdog and reset reason registers

Recommended testbench flow:

1. Reset the SoC.
2. Wait for UART `READY`.
3. Send `WDOG` header, length, payload bytes, and checksum if enabled.
4. Wait for terminal status.
5. Fail the test if status or cycle count differs from expected.
6. Dump trace only on failure or when profiling reference payloads.

Profiling simulations should additionally produce:

- instruction trace
- cycle count summary
- branch count
- load/store count
- flag-read count

## Board Run Procedure

Use the Greybadge25 ECP5 flow as the known-good reference:

1. Build Verilog into a bitstream using the Yosys, nextpnr-ecp5, and ecppack sequence used by the existing Makefiles.
2. Use `--25k --package CABGA256` unless the target board revision requires a different device.
3. Use the challenge LPF derived from the board schematic and verified against Greybadge26 if targeting the newer board.
4. Program the board using the existing GreyHats programming method.
5. Open the UART device.
6. Wait for `READY`.
7. Upload payloads through the host script.
8. Save UART transcript for every run.

Board test order:

1. LED blink bitstream.
2. UART TX boot banner.
3. UART RX echo or upload acknowledgement.
4. Minimal payload execution.
5. Watchdog timeout.
6. Region reset.
7. Naive C failure.
8. Optimized assembly success.

## Pass/Fail Evidence

Keep these artifacts:

- simulation logs
- waveform snapshots for first failing case in each category
- payload binaries and disassemblies
- reference cycle-count table
- board UART transcripts
- final LPF/constraint file used for the event build
- KiCad project path and board revision used for pin verification
