# 02 - Challenge Design

## Player Objective

Players must write a payload that reads the flag and returns it through the approved success path before watchdog expiry. The challenge should be fair to solve from public artifacts: memory map, ABI, simulator, upload format, and enough timing information to reason about optimization.

## Rules And Constraints

The released challenge should define:

- Payload entrypoint.
- Payload maximum size.
- Payload stack range.
- Allowed instruction-fetch range.
- Allowed data ranges.
- Flag access mechanism.
- UART upload format.
- Status strings and reset reasons.
- Whether the exact watchdog threshold is public or inferred.

Keep the rules mechanical. Avoid prose-only behavior like "do not do weird things"; express constraints as ranges, registers, and status codes.

## Intended Solve Path

The expected solution should look like this:

1. Build and run a starter payload.
2. Write a simple C loop that reads/copies the flag.
3. Compile without optimization and observe watchdog failure.
4. Inspect the disassembly.
5. Remove unnecessary stack use, branches, repeated loads, and function calls.
6. Hand-write a tight assembly loop.
7. Confirm the optimized cycle count in simulation.
8. Submit to the board and receive the flag.

## Failure And Feedback Design

Use short status strings:

```text
READY
LOADED
RUNNING
UPLOAD_ERROR
REGION_RESET
WATCHDOG_RESET
PAYLOAD_FAULT
NO_SUCCESS
SUCCESS
```

The UART should be the authoritative status channel. LEDs and OLED are secondary feedback. For example, LEDs can encode the low bits of `reset_reason`, while the OLED shows `no flag for you` on non-successful completion.

## How To Achieve This Requirement

Build a private "challenge contract" file first. It should contain the memory map, ABI, status strings, and upload format. Then make firmware and RTL implement that contract exactly.

Recommended default:

- Raw binary payload upload.
- Header magic `WDOG`.
- Little-endian payload length.
- Optional checksum once basic upload works.
- Entrypoint equals payload base address.
- `sp` initialized to top of payload stack.
- Success requires writing the flag buffer to a designated success mailbox or UART success routine before timeout.

## Simulation Plan

Simulate the player experience, not only internal modules.

Test cases:

- Valid starter payload reaches `SUCCESS` or `OK`.
- Bad magic returns `UPLOAD_ERROR`.
- Oversized payload returns `UPLOAD_ERROR`.
- Payload that returns immediately without success returns `NO_SUCCESS`.
- Payload that jumps outside the payload region returns `REGION_RESET`.
- Payload that loops forever returns `WATCHDOG_RESET`.
- Naive C flag-copy payload times out.
- Optimized assembly flag-copy payload succeeds.

Use UART byte streams in the testbench. Do not preload payload memory for the main acceptance tests, because preloading skips the exact path players use.

Record for each run:

- payload name
- payload size
- reset reason
- cycle count from jump-to-payload to terminal status
- UART transcript

## GreyMecha/Army Board Run Plan

Run the same challenge-design cases on the board:

1. Program the FPGA with a diagnostic build.
2. Open the serial connection at the selected baud rate.
3. Confirm `READY`.
4. Send each payload through the host upload script.
5. Capture UART transcript to a log file.
6. Confirm LEDs/OLED match the UART status.
7. Power-cycle or soft-reset between failure classes while reset logic is still being debugged.
8. Once stable, run back-to-back attempts without power cycling.

Board-specific references:

- Use Greybadge25 `firmware/ecp5/tests/uart_flag` as the closest existing UART challenge-style test.
- Use Greybadge25 `firmware/ecp5/tests/uart_tx_test` for UART bring-up if RX is not yet stable.
- Use Greybadge25 `firmware/ecp5/tests/pmod_oled_test` as display bring-up reference.
- Verify final Greybadge26 pins against its `ecp5_25_fpga.kicad_sch` and `greybadge_pcb.kicad_pcb`.
