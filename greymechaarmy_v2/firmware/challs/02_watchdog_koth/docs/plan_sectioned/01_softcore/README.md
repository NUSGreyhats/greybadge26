# 01 - Softcore

## Concept

The softcore is the trusted execution platform for the challenge. It combines PicoRV32, memory, MMIO peripherals, address decoding, and board-facing top-level wiring. Player payloads run inside this environment, but they should not control the enforcement logic.

The softcore must be boring, deterministic, and measurable. The challenge depends on cycle counting, so the memory map, peripheral latency, reset behavior, and bus faults must be stable in simulation and on hardware.

## Implementation Details

Implement the softcore as a small SoC around PicoRV32:

- `rtl/core/picorv32.v`: vendored or referenced PicoRV32 core.
- `rtl/core/soc_bus.v`: central bus decoder.
- `rtl/core/memory_map.vh`: address constants shared by RTL modules.
- `rtl/top/sim_top.v`: simulation top-level.
- `rtl/top/board_greymecha_top.v`: GreyMecha/Army board top-level.
- `rtl/top/watchdog_koth_top.v`: challenge SoC top-level independent of board pins.
- `rtl/peripherals/uart_mmio.v`: UART register bridge.
- `rtl/peripherals/led_mmio.v`: LED/status register.
- `rtl/peripherals/display_mmio.v`: GC9A01/OLED command/data bridge.
- `rtl/peripherals/reset_reason.v`: reset reason storage.

The bus decoder should define behavior for every access class:

- Boot firmware reads.
- Payload RAM reads/writes.
- Stack RAM reads/writes.
- Valid peripheral MMIO reads/writes.
- Flag peripheral reads.
- Unmapped reads/writes.

Unmapped access should not silently return random data. Pick one behavior and make it testable: return a fixed error value, trigger a bus fault, or trigger region reset.

Keep the top-level split clean:

- `watchdog_koth_top.v` should know about PicoRV32, RAM, peripherals, watchdog, and flag path.
- `sim_top.v` should wrap that SoC with simulation UART/display/flag models.
- `board_greymecha_top.v` should wrap the same SoC with GreyMecha/Army clock, reset, UART, LED, display, and interconnect pins.

## Acceptance Criteria

- PicoRV32 resets and fetches from the boot firmware base.
- Every memory range in the final memory map decodes to exactly one device.
- Every MMIO peripheral has defined reset values.
- UART, LEDs, display bridge, reset reason, watchdog registers, and flag path are reachable over the bus.
- Unmapped access behavior is deterministic.
- Simulation top-level and board top-level instantiate the same challenge SoC.
- Board-specific pin names and constraints are isolated from challenge logic.

## Test Plan

### Simulation

Run peripheral and bus tests before running firmware.

Simulate:

- Reset vector fetch from boot memory.
- Read/write to payload RAM.
- Read/write to stack RAM.
- Read/write to UART registers.
- Read/write to LED/status register.
- Write-only or command/data behavior for display bridge.
- Read/write behavior for watchdog registers.
- Read behavior for reset reason.
- Read behavior for dummy flag peripheral.
- Unmapped read/write behavior.

Use a bus-level testbench that can issue transactions directly. This avoids needing firmware just to prove the hardware map.

Expected testbench files:

- `sim/tb/tb_peripherals.v`
- `sim/tb/tb_soc_bus.v`
- `sim/models/uart_model.v`
- `sim/models/display_sink.v`
- `sim/models/flag_model.v`

Required checks:

- Assert every peripheral reset value.
- Assert write/readback where supported.
- Assert illegal access behavior.
- Assert no two devices respond to the same address.

### Hardware

Do not start with the full challenge. Use minimal board smoke builds:

1. LED blink from board clock.
2. UART TX boot banner.
3. UART RX echo.
4. MMIO self-test firmware printing `SELFTEST_OK`.
5. Display bridge smoke test if display is in scope for v1.

## Final Hardware Implementation

Use the Greybadge25 ECP5 flow as the known-good build reference:

```text
yosys -p "synth_ecp5 -top top -json test.json" tmp.v
nextpnr-ecp5 --json test.json --textcfg test_out.config --25k --package CABGA256 --lpf pinout.lpf
ecppack --svf test.svf test_out.config test.bit
```

Verify final pins against the target board schematic:

- Greybadge25: `C:\Users\zunmun\Documents\Stuff\Github\WORK\GreyHats\greybadge25\hardware\greybadge_pcb\greybadge_pcb.kicad_pro`
- Greybadge26/GreyMechaArmy v2: `C:\Users\zunmun\Documents\Stuff\Github\WORK\GreyHats\greybadge26\greymechaarmy_v2\hardware\greybadge_pcb\greybadge_pcb.kicad_pro`

The final hardware softcore is accepted when the board can boot, run the firmware self-test, and return to a known `READY` state repeatedly.
