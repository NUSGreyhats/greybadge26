# 05 - Hardware Tooling

## Concept

Hardware tooling connects the simulated challenge to the physical GreyMecha/Army board. It includes synthesis, constraints, bitstream generation, programming, serial upload tools, payload packing, and automated board tests.

The tooling should make hardware validation repeatable. Manual serial sessions are useful during bring-up, but final validation should run through scripts.

## Implementation Details

Tooling components:

- Top-level `Makefile`.
- ECP5 synthesis/place/route/pack flow.
- Board constraint files.
- Payload build and packing tools.
- Host serial upload tool.
- GreyMecha/Army autorun harness wrapper.
- Hardware test `run.py` directories.

Known Greybadge25 build pattern:

```text
yosys -p "synth_ecp5 -top top -json test.json" tmp.v
nextpnr-ecp5 --json test.json --textcfg test_out.config --25k --package CABGA256 --lpf pinout.lpf
ecppack --svf test.svf test_out.config test.bit
```

Referenced hardware projects:

```text
C:\Users\zunmun\Documents\Stuff\Github\WORK\GreyHats\greybadge25\hardware\greybadge_pcb\greybadge_pcb.kicad_pro
C:\Users\zunmun\Documents\Stuff\Github\WORK\GreyHats\greybadge26\greymechaarmy_v2\hardware\greybadge_pcb\greybadge_pcb.kicad_pro
```

Referenced autorun harness:

```text
C:\Users\zunmun\Documents\Stuff\GitLab\school-work\Workspace\2026\challenge_creation_greyctf_finals\greymechaarmy_autorun_harness\harness\tools\badge_harness.py
```

Harness behavior:

- Uploads a single file as `/tmp/run.py`, or a directory containing `run.py`.
- Uses the mounted `CIRCUITPY` drive unless `--drive` is specified.
- Uses a likely CircuitPython serial port unless `--port` is specified.
- Runs `/tmp/run.py` through the serial REPL.
- Returns failure if a Python traceback is seen.

## Acceptance Criteria

- One command builds simulation payloads.
- One command runs simulation tests.
- One command builds the ECP5 bitstream for the selected board.
- One command runs a named GreyMecha/Army hardware test.
- One command runs all board tests.
- Board tests produce machine-readable `RESULT PASS` or `RESULT FAIL` lines.
- Hardware logs include board revision, bitstream name, UART port, and test name.
- Final constraints are verified against the target board schematic.

## Test Plan

### Simulation Tool Tests

Run:

- Payload packer test: verifies `WDOG` magic, length, and payload bytes.
- Disassembly tool test: confirms generated payload has expected entrypoint.
- Serial transcript parser test: recognizes `READY`, `SUCCESS`, and reset reasons.
- Cycle summary parser test: extracts watchdog cycle counts.

Suggested tests:

```text
tests/unit/test_payload_pack.py
tests/unit/test_serial_expect.py
tests/integration/test_sim_statuses.py
tests/integration/test_cycle_budget.py
```

### Hardware Tool Tests

Run:

- Harness layout test: every `hardware/greymecha_tests/*/run.py` exists.
- Dry upload test with `--no-run` for a harmless script.
- `fpga_ready` test with explicit `--drive` and `--port`.
- `fpga_ready` test with auto-detected drive and port on the intended event laptop.
- Full repeatability test.

Suggested command shape:

```powershell
python C:\Users\zunmun\Documents\Stuff\GitLab\school-work\Workspace\2026\challenge_creation_greyctf_finals\greymechaarmy_autorun_harness\harness\tools\badge_harness.py --src .\hardware\greymecha_tests\fpga_ready --drive E:\ --port COM7
```

## Final Hardware Implementation

Final hardware tooling should expose these top-level targets:

```text
make sim-peripherals
make sim-boot
make sim-upload
make sim-watchdog
make sim-payloads
make payloads
make bitstream BOARD=greybadge25
make bitstream BOARD=greybadge26
make board-test TEST=fpga_ready DRIVE=E:\ PORT=COM7
make board-test-all DRIVE=E:\ PORT=COM7
```

The hardware tooling is accepted when a clean checkout can:

1. Build payloads.
2. Run simulation tests.
3. Build a board bitstream.
4. Program or prepare the board through the documented board flow.
5. Run all GreyMecha/Army hardware tests through the autorun harness.
6. Produce logs proving the optimized payload succeeds and naive payload fails.
