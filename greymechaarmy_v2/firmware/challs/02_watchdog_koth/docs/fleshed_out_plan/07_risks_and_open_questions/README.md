# 07 - Risks And Open Questions

## Risk: Timing Drift Between Simulation And Hardware

Impact:

- Players may build a payload that passes simulation but fails onsite.

Mitigation:

- Measure representative microbenchmarks on hardware.
- Tune watchdog with margin above the worst optimized hardware run.
- Avoid thresholds that require undocumented timing side effects.

Simulation test:

- Sweep branch-heavy, memory-heavy, and flag-copy payloads.

Board test:

- Sweep watchdog thresholds in development builds and compare pass/fail boundaries.

## Risk: Payload Format Complexity

Impact:

- ELF loading can consume time and introduce parser bugs.

Mitigation:

- Use raw binary plus a tiny `WDOG` header.
- Provide linker script and `objcopy` command.

Simulation test:

- Exercise malformed headers and oversized lengths.

Board test:

- Send corrupted serial streams and confirm recovery to `READY`.

## Risk: Incomplete Region Enforcement

Impact:

- Players may bypass the intended timing route.

Mitigation:

- Enforce PC range at minimum.
- Add load/store range checks where bus signals make it practical.
- Document exact enforcement semantics.

Simulation test:

- Bad PC and bad data access payloads.

Board test:

- Same payloads through UART with reset reason capture.

## Risk: Board Revision Mismatch

Impact:

- A bitstream validated on Greybadge25 may not match Greybadge26/GreyMechaArmy v2 pins or peripheral routing.

Mitigation:

- Verify final constraints against the target KiCad project.
- Keep board revision in every hardware log.
- Treat Greybadge25 flows as examples, not final truth.

Simulation test:

- Board wrapper simulation uses final top-level names and active polarities.

Board test:

- LED, UART, display, and reset smoke tests on the exact event board.

## Risk: Flag Leakage

Impact:

- Public artifacts may accidentally contain the real flag.

Mitigation:

- Use dummy flags in public simulation.
- Inject real flag only in private hardware/event builds.
- Search release artifacts before publishing.

Simulation test:

- Run failure payloads and inspect UART logs for dummy flag leakage.

Board test:

- Run failure payloads with a test flag build and verify no flag bytes leave the success path.

## Risk: Onsite Reliability

Impact:

- Serial transfer issues or stale reset state can make the challenge operationally fragile.

Mitigation:

- Make every attempt reset-clean and host-driven.
- Add upload timeouts.
- Log machine-readable statuses.

Simulation test:

- Back-to-back upload attempts with mixed success and failure.

Board test:

- At least 20 repeated attempts without power cycling.
