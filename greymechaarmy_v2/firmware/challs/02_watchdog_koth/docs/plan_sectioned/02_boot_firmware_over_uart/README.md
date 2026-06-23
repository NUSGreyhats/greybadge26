# 02 - Boot Firmware Over UART

## Concept

The boot firmware is the trusted loader. It starts after reset, reports status over UART, receives player payloads, places them into the payload region, arms the watchdog, and jumps to the payload entrypoint.

The firmware should not be the security boundary for watchdog or region enforcement. It prepares execution, but the watchdog and region guard must still work if payload code behaves maliciously.

## Implementation Details

Firmware responsibilities:

- Initialize UART.
- Initialize LED/status output.
- Optionally initialize display status.
- Read and print the previous reset reason.
- Run a peripheral self-test.
- Wait for a payload upload.
- Validate payload header.
- Clear payload memory before receiving new payload bytes.
- Copy payload bytes into payload RAM.
- Optionally verify checksum or CRC.
- Print `LOADED`.
- Set payload stack pointer.
- Arm watchdog.
- Jump to payload entrypoint.

Default UART status strings:

```text
READY
SELFTEST_OK
UPLOAD_ERROR
LOADED
RUNNING
WATCHDOG_RESET
REGION_RESET
PAYLOAD_FAULT
NO_SUCCESS
SUCCESS
```

Default upload format:

```text
magic:   4 bytes, "WDOG"
length:  4 bytes, little endian
payload: length bytes
crc:     optional 4 bytes, add after basic upload works
```

Suggested firmware files:

- `firmware/bootloader/main.c`
- `firmware/bootloader/startup.S`
- `firmware/bootloader/linker.ld`
- `firmware/bootloader/uart.c`
- `firmware/bootloader/loader.c`
- `firmware/bootloader/selftest.c`
- `firmware/include/mmio.h`
- `firmware/include/memory_map.h`
- `firmware/include/status_codes.h`

## Acceptance Criteria

- Firmware prints `READY` after clean reset.
- Firmware reports previous reset reason after watchdog or region reset.
- Firmware rejects bad magic.
- Firmware rejects oversized payloads.
- Firmware recovers from partial upload timeout.
- Firmware clears payload memory before each attempt.
- Firmware sets stack pointer before jumping.
- Firmware arms watchdog immediately before payload execution.
- Firmware emits machine-readable UART status strings.

## Test Plan

### Simulation

Simulate firmware only after softcore peripheral tests pass.

Run:

- Clean boot reaches `READY`.
- Self-test reaches `SELFTEST_OK`.
- Bad magic returns `UPLOAD_ERROR`.
- Oversized length returns `UPLOAD_ERROR`.
- Partial upload times out and returns to `READY`.
- Valid `starter_ok` payload reaches `RUNNING` then success.
- Repeated uploads do not reuse stale payload bytes.
- Forced reset reason is printed on next boot.

Drive UART RX in simulation using the exact byte stream produced by `tools/payload/pack_wdog.py` or equivalent. Capture UART TX and compare status lines.

### Hardware

Start with firmware-only board tests:

1. Program bitstream.
2. Open serial connection.
3. Reset board.
4. Expect `READY`.
5. Send bad header and expect `UPLOAD_ERROR`.
6. Send oversized header and expect `UPLOAD_ERROR`.
7. Send minimal payload and expect `LOADED`, `RUNNING`, and terminal status.

## Final Hardware Implementation

Automate firmware-over-UART tests using:

```text
C:\Users\zunmun\Documents\Stuff\GitLab\school-work\Workspace\2026\challenge_creation_greyctf_finals\greymechaarmy_autorun_harness\harness\tools\badge_harness.py
```

Create CircuitPython test directories:

```text
hardware/greymecha_tests/
  fpga_ready/run.py
  peripheral_selftest/run.py
  starter_upload/run.py
```

Each `run.py` should reset or prepare the FPGA path, talk to the challenge UART path, and print one final result line:

```text
RESULT PASS starter_upload
```

or:

```text
RESULT FAIL starter_upload <reason>
```

The firmware is hardware-ready when the automated harness can run boot, self-test, bad-upload, and starter-upload tests repeatedly without manual power cycling.
