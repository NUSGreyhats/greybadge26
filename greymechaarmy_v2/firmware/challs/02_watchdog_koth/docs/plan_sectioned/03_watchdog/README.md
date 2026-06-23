# 03 - Watchdog

## Concept

The watchdog is the core challenge mechanic, but it should also be an intentional target for the solve. It limits how many cycles a player payload can use and resets execution when the payload exceeds the budget. It should also cooperate with region enforcement so payloads cannot escape the intended code or memory ranges.

Unlike the stricter earlier design, the watchdog is allowed to be enabled or disabled by CPU writes to its MMIO control register. This creates two intended solve families:

1. Beat the watchdog by writing a fast enough payload.
2. Discover the watchdog control register and disable the watchdog before doing a slower flag extraction.

This means the watchdog is not a pure security boundary. The real challenge boundary becomes understanding the SoC memory map and control registers well enough to either optimize around the watchdog or intentionally turn it off.

## Implementation Details

Watchdog state:

- `armed`
- `enabled`
- `counter`
- `limit`
- `payload_active`
- `payload_base`
- `payload_limit`
- `reset_reason`

Recommended MMIO registers:

```text
WATCHDOG_CTRL       0x00
WATCHDOG_LIMIT      0x04
WATCHDOG_COUNTER    0x08
WATCHDOG_STATUS     0x0c
WATCHDOG_BASE       0x10
WATCHDOG_END        0x14
```

Recommended `WATCHDOG_CTRL` bits:

```text
bit 0  ENABLE       1 = counter can reset payload, 0 = timeout disabled
bit 1  ARM          1 = watchdog is armed for payload execution
bit 2  CLEAR        write 1 to clear counter
bit 3  LOCK         optional, 1 = ignore payload writes to control registers
```

For the intended disable-watchdog solve, leave `LOCK` unset in the released challenge or make it possible for player code to clear/avoid it. If `LOCK` is enabled permanently before payload execution, the disable-watchdog solve is removed.

Observed signals:

- firmware-to-payload handoff
- instruction address or PC
- memory valid
- memory address
- memory write enable
- success signal
- core reset
- trap/illegal instruction if exposed

Reset reasons:

```text
CLEAN_BOOT
WATCHDOG_RESET
REGION_RESET
PAYLOAD_FAULT
NO_SUCCESS
SUCCESS
```

Behavior:

1. Firmware configures payload base, payload limit, and cycle limit.
2. Firmware sets `ENABLE=1`, clears the counter, and arms watchdog during handoff.
3. Watchdog starts counting on the first payload cycle when `ENABLE=1` and `ARM=1`.
4. Counter increments while payload is active and watchdog is enabled.
5. Payload code may write `ENABLE=0` to disable timeout resets.
6. When `ENABLE=0`, timeout resets are suppressed and the counter may either stop or continue as diagnostic state.
7. Success stops the watchdog.
8. Timeout resets the core and records `WATCHDOG_RESET` only if `ENABLE=1`.
9. Illegal PC or memory access resets the core and records `REGION_RESET`.

Region enforcement should remain active even when the watchdog counter is disabled. Disabling the watchdog should remove only the cycle-budget pressure, not permit arbitrary code execution outside the allowed payload region.

## Acceptance Criteria

- CPU can enable and disable the watchdog through the documented MMIO control register.
- Firmware enables and arms the watchdog before normal payload execution.
- Player payloads can intentionally disable the watchdog if they discover and write the correct control register.
- Disabling the watchdog suppresses timeout resets.
- Disabling the watchdog does not disable region enforcement.
- Counter starts at a deterministic cycle.
- Timeout always records `WATCHDOG_RESET`.
- Illegal instruction fetch outside payload region records `REGION_RESET`.
- Illegal data access records `REGION_RESET` if data enforcement is implemented.
- Success stops the watchdog before reset.
- Reset reason persists long enough for boot firmware to report it.
- Threshold is configurable during development and fixed for release.
- The challenge has at least one passing disable-watchdog reference payload and one passing optimized-cycle reference payload.

## Test Plan

### Simulation

Unit tests:

- Counter reset value is zero.
- Writing `limit` changes threshold.
- Writing `WATCHDOG_CTRL.ENABLE=1` enables timeout reset behavior.
- Writing `WATCHDOG_CTRL.ENABLE=0` disables timeout reset behavior.
- Arming starts count only when payload is active.
- Deasserting reset clears active state but preserves or transfers reset reason as designed.
- Timeout fires at the expected cycle.
- Timeout does not fire when `ENABLE=0`.
- Region reset still fires when `ENABLE=0`.

SoC tests:

- Infinite loop payload triggers `WATCHDOG_RESET`.
- Payload that disables watchdog then loops does not trigger `WATCHDOG_RESET` within the normal timeout window.
- Payload with `limit - margin` loop succeeds.
- Payload with `limit + 1` loop resets.
- Jump below payload base triggers `REGION_RESET`.
- Jump above payload limit triggers `REGION_RESET`.
- Payload disables watchdog and then jumps outside the region; expected result is still `REGION_RESET`.
- Illegal data access triggers `REGION_RESET` if enabled.
- Successful optimized payload stops watchdog.
- Disable-watchdog reference payload succeeds even when the naive C flag-copy routine would otherwise exceed the cycle budget.

Cycle-tuning tests:

- `naive_c_flag_copy` fails by timeout.
- `optimized_asm_flag_copy` succeeds.
- `disable_watchdog_flag_copy` succeeds by disabling timeout enforcement before copying the flag.
- Microbenchmarks record branch, memory, and flag-read timing.

### Hardware

Hardware tests should initially use development thresholds:

1. Very high limit proves normal payload execution.
2. Very low limit proves timeout reset.
3. Swept limits find the hardware pass/fail boundary.
4. Final limit is tested repeatedly.
5. Disable-watchdog payload proves CPU control register writes work on hardware.
6. Disable-watchdog plus bad-region payload proves region enforcement remains active.

## Final Hardware Implementation

Add automated harness tests:

```text
hardware/greymecha_tests/
  watchdog_timeout/run.py
  watchdog_disable/run.py
  watchdog_disable_region_reset/run.py
  region_reset/run.py
  naive_c_fails/run.py
  optimized_succeeds/run.py
```

Each test should:

1. Prepare the FPGA/challenge interface.
2. Upload the target payload.
3. Read UART status.
4. Confirm the reset reason or success status.
5. Print `RESULT PASS <test_name>` or `RESULT FAIL <test_name> <reason>`.

For final event readiness, run at least 20 attempts each for timeout, watchdog disable, disable-plus-region-reset, region reset, naive failure, optimized success, and disable-watchdog success.

The final challenge should intentionally support both:

- Optimized timing solve: payload stays within the watchdog budget.
- Watchdog-control solve: payload writes `WATCHDOG_CTRL.ENABLE=0`, then performs the slower flag extraction.
