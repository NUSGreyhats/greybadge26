# 04 - Flag Memory Peripheral

## Concept

The flag memory peripheral is the protected source of the flag. It gives payloads something to extract, but the watchdog makes extraction timing-sensitive.

The first version should keep the flag path simple and deterministic. The challenge should be hard because of cycle pressure, not because the flag peripheral has undocumented behavior.

## Implementation Details

Recommended v1 design:

- Memory-map the flag at a fixed address range.
- Use a dummy flag in public simulation.
- Use a test flag in private hardware development.
- Inject the real flag only in the final event build.
- Return one byte or word per read with deterministic latency.
- Optionally expose a `flag_len` register if the length should be discoverable.

Default address:

```text
0x2000_0000 - 0x2000_00ff  flag ROM/peripheral
```

Implementation files:

- `rtl/peripherals/flag_rom.v`
- `sim/models/flag_model.v`
- `firmware/include/memory_map.h`
- `docs/architecture/memory_map.md`

Do not print the flag from boot firmware. The flag should leave the board only through the payload success path.

## Acceptance Criteria

- Dummy flag is available in simulation.
- Test flag is available in hardware development builds.
- Real flag is absent from public docs, public simulation artifacts, and source intended for release.
- Flag reads have deterministic timing.
- Failure paths do not print partial flag bytes.
- Optimized payload can read and return the flag before watchdog expiry.
- Naive payload can read the flag in principle but fails due to cycle budget.

## Test Plan

### Simulation

Run:

- Direct flag peripheral read returns expected dummy bytes.
- Reads outside flag range trigger expected behavior.
- Flag read latency is fixed.
- Starter payload cannot accidentally print flag bytes.
- Naive C payload times out.
- Optimized assembly payload succeeds.
- Failure payload UART logs do not contain dummy flag bytes.

Also search generated public simulation artifacts for the real flag string before release. Public simulation should use a dummy flag value.

### Hardware

Run hardware with a test flag first:

1. Program test-flag bitstream.
2. Upload a known success payload.
3. Confirm test flag is returned.
4. Upload timeout and region-failure payloads.
5. Confirm no partial test flag appears.
6. Replace test flag with real event flag only for final private bitstream.

## Final Hardware Implementation

Keep three build profiles:

```text
FLAG_PROFILE=public_dummy
FLAG_PROFILE=private_test
FLAG_PROFILE=event_real
```

The final event build should be produced from the `event_real` profile, but public artifacts should use `public_dummy`.

Automated harness tests:

```text
hardware/greymecha_tests/
  optimized_succeeds/run.py
  naive_c_fails/run.py
  repeatability/run.py
```

The final flag peripheral is accepted when:

- Private optimized payload returns the flag repeatedly.
- Failure payloads never leak flag bytes.
- Public release artifacts contain no real flag.
