# Bootloader Cycle Reporting

## Goal

Expose cycle counter state through MMIO and have the bootloader report per-payload cycle start, end, and delta values before returning to `READY` for another payload when the payload returns.

## Current State

The bootloader can load and run payloads, but returning payload behavior and timing visibility need to be made explicit. The host/operator should be able to observe a complete run cycle and then upload another payload without reflashing or resetting when the payload returns normally.

## Required Implementation Changes

Expose reset reason and cycle counter values at these MMIO addresses:

```text
0x1000_0300 reset reason
0x1000_0304 cycle low
0x1000_0308 cycle high
```

Print the boot output sequence:

```text
BOOT: CYCLE_START <hex64>
BOOT: RUNNING
BOOT: CYCLE_END <hex64>
BOOT: CYCLE_DELTA <hex64>
BOOT: DONE
BOOT: READY
```

Cycle values must be printed as 64-bit hexadecimal values. `CYCLE_DELTA` must be computed from the end value minus the start value using the 64-bit counter value.

When a payload returns to the bootloader, the bootloader must complete the reporting sequence and re-enter the load loop. It should print `BOOT: READY` to signal that it is ready for another payload.

Payloads that do not return should continue running until interrupted by reset, watchdog, or other existing mechanisms.

## Acceptance Criteria

- MMIO reads expose reset reason, cycle low, and cycle high at the specified addresses.
- Bootloader prints `CYCLE_START` before transferring control to the payload.
- Bootloader prints `RUNNING` when the payload is launched.
- Bootloader prints `CYCLE_END`, `CYCLE_DELTA`, `DONE`, and `READY` after a returning payload.
- All cycle values are formatted as 64-bit hex.
- A second payload can be loaded after a returning payload without a board reset.
- Non-returning payload behavior is not broken.

## Test Plan

- Add or update firmware tests for formatting and output order.
- Add MMIO tests for cycle low/high address behavior.
- Run a returning payload and assert the full boot output sequence.
- Verify `CYCLE_DELTA` equals `CYCLE_END - CYCLE_START` for captured values.
- Upload a second returning payload after `BOOT: READY` and confirm the loop repeats.
- Run a non-returning payload smoke test to confirm existing behavior remains intact.

## Notes/Assumptions

- Hex formatting should be fixed-width enough to unambiguously represent a 64-bit value.
- Reset reason semantics should remain compatible with existing watchdog/reset behavior.
- Cycle counter reads should be coherent enough for the intended bootloader reporting path.

