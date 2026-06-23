# Test And Acceptance

## Goal

Define the combined regression and acceptance plan for the script reorganization, flag update, UART TX FIFO, bootloader cycle reporting, returning-payload behavior, and hardware upload flow.

## Current State

The planned implementation touches user workflows, visible challenge values, MMIO behavior, firmware output, and hardware-facing scripts. These changes need targeted tests plus an end-to-end acceptance pass to catch integration issues.

## Required Implementation Changes

Collect and maintain tests covering:

- Script wrapper compatibility.
- Canonical script behavior.
- Flag value and little-endian word layout.
- UART TX FIFO order, full, and drain behavior.
- Bootloader cycle reporting output.
- Returning-payload re-load loop.
- Hardware upload checks.

The final implementation pass should update automated tests where feasible and document any hardware-only manual checks.

## Acceptance Criteria

- Canonical scripts are the documented supported workflow.
- Useful old script paths still work as wrappers.
- The flag is consistently `grey{mmio_fuzzz}` across source, tests, docs, examples, and distribution payloads.
- UART TX FIFO depth is 32 bytes and status semantics match the plan.
- Bootloader emits cycle start, running, cycle end, cycle delta, done, and ready messages in order.
- Cycle values are printed as 64-bit hex.
- Returning payloads allow a subsequent payload load without reset.
- Hardware upload flow works with the canonical PowerShell script and optional parameters.
- No unrelated RTL, firmware, payload, or script behavior changes are introduced beyond the planned implementation.

## Test Plan

Run the relevant automated regression suite:

- Script tests for canonical entry points and compatibility wrappers.
- Flag tests for string value and little-endian words.
- UART MMIO simulation tests for TX FIFO order, full, drain, reset, and RX non-regression.
- Bootloader tests for output sequence and cycle delta arithmetic.
- Returning-payload tests for repeated load/run/ready cycles.

Run hardware checks where hardware is available:

- Build the bitstream with `scripts/build_bitstream.sh`.
- Compile a known returning payload with `scripts/compile_payload.sh <payload>`.
- Upload with `scripts/upload_greymecha.ps1 -Payload <name>`.
- Repeat upload using explicit `-Drive` and `-Port` values.
- Run upload with `-BuildBitstream` and confirm the combined flow works.
- Capture serial output and verify boot messages and flag behavior.

## Notes/Assumptions

- Hardware upload checks may remain manual if CI lacks board access.
- Generated distribution payloads should be rebuilt by normal build scripts.
- Existing `docs/plan_sectioned/` is historical context and should not be modified for this documentation-only task.
- This folder should remain implementation-oriented so a later pass can execute the work without rediscovering decisions.

