# 04 - Acceptance Criteria

## 1. UART Upload Is Reliable

Requirement:

- A host can upload payloads repeatedly without reprogramming or power-cycling the board.

Simulation proof:

- Test 20 consecutive valid uploads.
- Test partial upload timeout.
- Test malformed header recovery.
- Verify the loader always returns to `READY`.

Board proof:

- Run the host upload script 20 times against the GreyMecha/Army board.
- Capture UART logs.
- Confirm no stale payload bytes affect later attempts.

## 2. Payload Executes From The Documented Region

Requirement:

- First instruction fetch occurs at the payload base and stack starts at the documented stack top.

Simulation proof:

- Assert the first payload PC equals payload base.
- Assert initial `sp` equals stack top.
- Run a payload that reports stack write/read success.

Board proof:

- Upload a payload that writes known LED patterns before and after stack use.
- Confirm UART prints `OK` and the pattern is visible.

## 3. Region Violations Reset

Requirement:

- Illegal PC or memory behavior does not continue execution.

Simulation proof:

- Payload jumps below payload base.
- Payload jumps past payload limit.
- Payload writes outside stack if data enforcement is enabled.
- Assert `reset_reason == REGION_RESET`.

Board proof:

- Upload the same bad-jump payloads.
- Confirm UART reports `REGION_RESET`.
- Confirm LEDs/OLED show the failure state.

## 4. Watchdog Timeout Resets

Requirement:

- Payloads exceeding the cycle budget reset deterministically.

Simulation proof:

- Infinite loop payload resets.
- Loop at `limit - margin` succeeds.
- Loop at `limit + 1` resets.
- Counter starts only after `RUNNING`.

Board proof:

- Run timeout payload 20 times.
- Confirm reset reason and return to `READY`.

## 5. Naive C Fails

Requirement:

- The readable reference C solution is correct in principle but too slow.

Simulation proof:

- Compile with documented unoptimized flags.
- Run and record cycle count.
- Confirm timeout, not upload or region failure.

Board proof:

- Upload the same binary.
- Confirm repeated `WATCHDOG_RESET`.

## 6. Optimized Reference Succeeds

Requirement:

- The optimized private reference payload recovers the flag reliably.

Simulation proof:

- Run 100 times if deterministic, or enough randomized reset-alignment cases if reset timing varies.
- Record worst observed cycle count.

Board proof:

- Run at least 20 attempts.
- Confirm every attempt prints the test flag in development mode.
- Confirm final private build prints the real flag only on success.

## 7. Simulation Is Trustworthy

Requirement:

- Players can rely on simulation to optimize.

Simulation proof:

- Compare cycle traces for branch, load/store, and flag-copy microbenchmarks.
- Export trace logs or summary CSVs.

Board proof:

- Run the same microbenchmarks and compare pass/fail boundaries.
- If exact cycle readback is unavailable on board, sweep watchdog thresholds in development builds and infer hardware boundaries.

## 8. Flag Does Not Leak

Requirement:

- The real flag appears only on the success path.

Simulation proof:

- Run all failure payloads with a dummy flag.
- Confirm no partial flag appears in UART logs, waveforms intended for release, or public ROMs.

Board proof:

- Run failure payloads against a test flag build.
- Confirm display, LEDs, and UART never print flag bytes on failure.
- Search final release artifacts for the real flag before publishing anything public.
