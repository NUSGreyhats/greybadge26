# 03 - Implementation Roadmap

This roadmap is ordered to reduce bring-up risk:

1. Update the softcore and memory-mapped peripherals first.
2. Prove those peripherals in simulation.
3. Add firmware, payload execution, and UART upload on the simulated softcore.
4. Tune challenge payloads in simulation.
5. Move to GreyMecha/Army board testing only after the simulated system is stable.
6. Automate board runs with the GreyMecha Army autorun harness.

The key rule is: do not debug payload upload or challenge code on hardware until the softcore peripheral contract is already proven in simulation.

## Phase 1: Softcore Peripheral Contract

Define the SoC shape before writing the challenge loader. The PicoRV32 integration should expose all challenge-relevant devices through a documented memory map.

Required softcore-visible devices:

- Boot firmware ROM/RAM.
- Payload RAM.
- Payload stack RAM.
- UART RX/TX.
- LED/status register.
- GC9A01/OLED display path or display SPI bridge.
- Watchdog control/status registers.
- Flag ROM or flag peripheral.
- Reset-reason register.

Recommended draft memory map:

```text
0x0000_0000 - 0x0000_7fff  boot firmware
0x0000_8000 - 0x0000_bfff  payload code/data
0x0000_c000 - 0x0000_cfff  payload stack
0x1000_0000 - 0x1000_00ff  UART
0x1000_0100 - 0x1000_01ff  LEDs/status
0x1000_0200 - 0x1000_02ff  watchdog registers
0x1000_0300 - 0x1000_03ff  reset/status registers
0x1000_1000 - 0x1000_1fff  GC9A01/display bridge
0x2000_0000 - 0x2000_00ff  flag ROM/peripheral
```

How to achieve it:

1. Add or update the softcore bus decoder.
2. Give each peripheral a small, explicit register interface.
3. Add a reset-reason path that firmware can read after watchdog or region reset.
4. Keep device timing deterministic, especially flag and memory accesses.
5. Make unmapped reads/writes return a defined error or trigger a region fault.
6. Document register offsets as soon as they are implemented.

## Phase 2: Peripheral Simulation Before Firmware

Before running C firmware, build RTL tests that prove each peripheral behaves correctly in isolation and through the SoC bus.

What to simulate:

- UART TX register accepts bytes and exposes busy/ready state.
- UART RX model delivers bytes to the softcore-visible RX register.
- LED register latches writes and resets to a known value.
- Display bridge accepts command/data writes without stalling unpredictably.
- Watchdog registers can be configured, armed, cleared, and read back.
- Watchdog counter expires at the expected cycle.
- Reset-reason register reports timeout, region reset, trap, or clean boot.
- Flag region returns deterministic dummy flag bytes.
- Unmapped or illegal accesses produce the chosen fault behavior.

How to simulate:

1. Use a bus-level testbench that can issue reads/writes without booting firmware.
2. Test every register reset value.
3. Test every writable register write/readback path.
4. Test each fault path with assertions.
5. Add waveform dumps for first bring-up, then keep self-checking tests for regression.

Exit criteria:

- Every memory-mapped peripheral has passing bus tests.
- Watchdog timeout is cycle-accurate in isolation.
- Region/fault behavior is deterministic.
- The dummy flag path has fixed latency.

## Phase 3: Softcore Firmware Bring-Up In Simulation

Only after peripheral tests pass, add boot firmware that runs on PicoRV32.

Firmware responsibilities:

- Print `READY` over UART.
- Initialize LEDs and optional display status.
- Read reset reason and report the previous failure state.
- Exercise each peripheral once in a power-on self-test mode.
- Stay in an upload loop until a payload arrives.

Simulation tests:

- Boot reaches `READY`.
- Firmware writes expected LED state.
- Firmware emits display initialization transactions or skips display cleanly in headless simulation.
- Firmware reads reset reason after a forced watchdog reset.
- Firmware reports a peripheral self-test failure if a simulated device is intentionally broken.

How to simulate:

1. Load firmware into boot memory.
2. Reset the SoC.
3. Capture UART output until `READY`.
4. Observe LED/display bus transactions.
5. Force reset reasons and confirm firmware reports them.

Exit criteria:

- Firmware can prove the SoC peripheral map from inside PicoRV32.
- UART logs are machine-readable enough for later automated tests.

## Phase 4: Payload ABI And Loader In Simulation

After firmware bring-up, implement the player payload interface.

Payload ABI:

- Entrypoint is the payload base address.
- Firmware sets `sp` to the top of payload stack.
- Payload runs with watchdog armed.
- Payload can use payload RAM and stack RAM.
- Payload succeeds only through the documented success path.

Recommended upload format:

```text
magic:   4 bytes, "WDOG"
length:  4 bytes, little endian
payload: length bytes
crc:     optional 4 bytes, add after basic upload is stable
```

Simulation tests:

- Valid minimal payload uploads and executes.
- Bad magic returns `UPLOAD_ERROR`.
- Oversized payload returns `UPLOAD_ERROR`.
- Partial payload times out and returns to `READY`.
- Payload memory is cleared before each upload.
- First payload instruction fetch equals payload base.
- Initial stack pointer equals documented stack top.

How to simulate:

1. Drive UART RX with the exact byte stream the host uploader will send.
2. Capture UART TX transcript.
3. Assert loader state transitions: `READY`, `LOADED`, `RUNNING`, terminal status.
4. Assert no payload code runs before `RUNNING`.

Exit criteria:

- Upload behavior is stable in simulation.
- Bad uploads do not corrupt later attempts.
- Minimal payload execution is repeatable.

## Phase 5: Watchdog, Region Enforcement, And Flag Path In Simulation

Now connect the challenge rules to payload execution.

Watchdog behavior:

- Counter starts on the firmware-to-payload handoff.
- Counter stops only on success or reset.
- Timeout resets the softcore and records `WATCHDOG_RESET`.

Region behavior:

- Instruction fetch must remain inside payload code range unless a specific trampoline is documented.
- Stack accesses must remain inside stack range if data enforcement is implemented.
- Flag reads must be allowed only through the intended flag path.
- Illegal peripheral access should fault or reset consistently.

Simulation tests:

- Infinite loop payload triggers `WATCHDOG_RESET`.
- Payload jumping below payload base triggers `REGION_RESET`.
- Payload jumping above payload limit triggers `REGION_RESET`.
- Bad stack access triggers `REGION_RESET` if data checks exist.
- Dummy flag can be read by a correct payload.
- Failure payloads never leak dummy flag bytes over UART.

Exit criteria:

- Watchdog and region failures are distinguishable.
- Reset returns firmware to `READY`.
- The flag path is reachable only through intended payload behavior.

## Phase 6: Reference Payloads And Cycle Tuning In Simulation

Create payloads only after upload, watchdog, and region rules are stable.

Payload set:

- `starter_ok`: public, proves upload and execution.
- `naive_c_flag_copy`: private, correct but too slow.
- `optimized_asm_flag_copy`: private, fast enough.
- `branch_microbench`: profiles branch timing.
- `mem_microbench`: profiles load/store and flag path timing.
- `uart_microbench`: confirms UART is not accidentally used in the hot path.

How to simulate:

1. Compile payloads with the same linker script and binary conversion flow players will use.
2. Upload each payload through UART simulation.
3. Record terminal status and cycle count.
4. Export disassembly for C and assembly reference payloads.
5. Set watchdog threshold between naive and optimized cycle counts.

Exit criteria:

- Naive C fails by timeout, not ABI or upload error.
- Optimized assembly succeeds with measured margin.
- Watchdog limit is justified by a cycle-count table.

## Phase 7: GreyMecha/Army Hardware Bring-Up

Move to hardware only after the simulation phases pass.

Board references:

- Greybadge25 KiCad project: `C:\Users\zunmun\Documents\Stuff\Github\WORK\GreyHats\greybadge25\hardware\greybadge_pcb\greybadge_pcb.kicad_pro`
- Greybadge25 ECP5 flow: `C:\Users\zunmun\Documents\Stuff\Github\WORK\GreyHats\greybadge25\firmware\ecp5`
- Greybadge26/GreyMechaArmy v2 KiCad project: `C:\Users\zunmun\Documents\Stuff\Github\WORK\GreyHats\greybadge26\greymechaarmy_v2\hardware\greybadge_pcb\greybadge_pcb.kicad_pro`

The discovered Greybadge25 Makefiles use:

```text
yosys -p "synth_ecp5 -top top -json test.json" tmp.v
nextpnr-ecp5 --json test.json --textcfg test_out.config --25k --package CABGA256 --lpf pinout.lpf
ecppack --svf test.svf test_out.config test.bit
```

Use that as the first ECP5 build reference, then verify final pin constraints against the target Greybadge26/GreyMechaArmy schematic if using the newer board.

Manual board smoke order:

1. LED blink.
2. UART TX boot banner.
3. UART RX echo.
4. Firmware peripheral self-test.
5. Loader receives `starter_ok`.
6. Watchdog timeout payload resets.
7. Region-reset payload resets.

Do not run reference flag payloads on the board until these smoke tests pass.

## Phase 8: Automated GreyMecha/Army Board Testing With Autorun Harness

Use the autorun harness to automate board-side tests that run on the badge CircuitPython environment.

Harness path:

```text
C:\Users\zunmun\Documents\Stuff\GitLab\school-work\Workspace\2026\challenge_creation_greyctf_finals\greymechaarmy_autorun_harness
```

Discovered harness behavior:

- Tool entrypoint: `harness\tools\badge_harness.py`.
- Uploads a file or directory to the mounted badge drive under `/tmp`.
- A single file is copied as `/tmp/run.py`.
- A directory upload must contain `run.py`.
- Runs `/tmp/run.py` through the CircuitPython serial REPL.
- Auto-detects a mounted drive named `CIRCUITPY` if `--drive` is omitted.
- Auto-detects a likely CircuitPython serial port if `--port` is omitted.
- Supports `--no-run`, `--timeout`, and `--settle`.
- Serial execution requires `pyserial`.

Example commands from the harness README:

```powershell
python tools\badge_harness.py --src .\run.py --drive E:\ --port COM7
python tools\badge_harness.py --src .\payload --drive E:\ --port COM7
python tools\badge_harness.py --src .\run.py --drive E:\ --no-run
```

How to use it for this challenge:

1. Create small CircuitPython `run.py` test drivers that control the badge-side path used to program, reset, or communicate with the FPGA.
2. For each challenge payload test, have `run.py` perform the board-specific setup, send the payload or command sequence, read UART/status output, and print a machine-readable result.
3. Run those scripts with `badge_harness.py` so every board test has the same upload/run mechanism.
4. Capture harness stdout as the official hardware test log.
5. Treat any Python traceback as a harness failure, since the tool exits nonzero when it sees a traceback.

Automated board test cases:

- `fpga_ready`: badge script confirms the FPGA challenge firmware reaches `READY`.
- `peripheral_selftest`: runs firmware self-test and expects `SELFTEST_OK`.
- `starter_upload`: uploads `starter_ok` payload and expects `OK`.
- `watchdog_timeout`: uploads timeout payload and expects `WATCHDOG_RESET`.
- `region_reset`: uploads bad-jump payload and expects `REGION_RESET`.
- `naive_c_fails`: uploads naive reference and expects `WATCHDOG_RESET`.
- `optimized_succeeds`: uploads optimized reference and expects `SUCCESS`.
- `repeatability`: runs the above sequence repeatedly without power cycling.

Recommended automation layout:

```text
hardware_tests/
  fpga_ready/run.py
  peripheral_selftest/run.py
  starter_upload/run.py
  watchdog_timeout/run.py
  region_reset/run.py
  naive_c_fails/run.py
  optimized_succeeds/run.py
  repeatability/run.py
```

Each `run.py` should print one final line:

```text
RESULT PASS <test_name>
```

or:

```text
RESULT FAIL <test_name> <reason>
```

Exit criteria:

- Harness can run tests with explicit `--drive` and `--port`.
- Harness can also run with auto-detection on the intended event laptop.
- Hardware logs show deterministic pass/fail strings.
- Repeatability test runs at least 20 attempts without power cycling.

## Phase 9: Final Challenge Validation

Final validation combines simulation and automated board data.

Required evidence:

- Peripheral simulation results.
- Firmware boot and self-test simulation logs.
- UART upload simulation logs.
- Watchdog and region reset simulation logs.
- Reference payload cycle-count table.
- GreyMecha/Army harness logs for every board test.
- Final board revision and constraint file used.
- Final watchdog threshold and measured optimized margin.

Release rule:

- If a test fails in simulation, do not debug it first on hardware.
- If a test passes in simulation but fails on hardware, add a board-specific diagnosis test through the autorun harness and record the discrepancy.
