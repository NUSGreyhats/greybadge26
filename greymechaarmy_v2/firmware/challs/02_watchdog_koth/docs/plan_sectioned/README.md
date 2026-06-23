# Plan Sectioned

This plan reorganizes the Watchdog KOTH challenge around the five cooperating parts of the system:

1. [Softcore](01_softcore/README.md)
2. [Boot Firmware Over UART](02_boot_firmware_over_uart/README.md)
3. [Watchdog](03_watchdog/README.md)
4. [Flag Memory Peripheral](04_flag_memory_peripheral/README.md)
5. [Hardware Tooling](05_hardware_tooling/README.md)

Each section follows the same structure:

- Concept.
- Implementation details.
- Acceptance criteria.
- Test plan.
- Final hardware implementation.

## System Flow

The challenge should be developed in this order:

1. Build the softcore integration and memory-mapped peripherals.
2. Prove the softcore peripherals in simulation without firmware.
3. Add boot firmware and UART upload behavior.
4. Add watchdog enforcement around payload execution.
5. Add the flag memory peripheral.
6. Tune the reference payloads in simulation.
7. Build the GreyMecha/Army bitstream.
8. Run automated hardware tests through the GreyMecha Army autorun harness.

This order keeps hardware debugging late. If a behavior cannot pass in simulation, it should not be debugged first on the physical board.

## Shared Interfaces

All five parts must agree on these contracts:

- Memory map.
- MMIO register offsets.
- Reset reason codes.
- UART upload protocol.
- Payload ABI.
- Watchdog state machine.
- Flag access timing.
- Board status strings.

These contracts should eventually live in `docs/architecture/` and be mirrored into RTL headers, firmware headers, payload linker scripts, and test scripts.

## Default Memory Map

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

The exact addresses can change to match the existing PicoRV32 project, but every section should use one final map.
