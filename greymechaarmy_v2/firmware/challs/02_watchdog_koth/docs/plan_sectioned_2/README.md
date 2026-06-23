# Plan Sectioned 2

This folder captures the current implementation plan as sectioned documentation for a later implementation pass. It is decision-complete documentation only: saving this plan must not change RTL, firmware, scripts, payloads, tests, or generated artifacts.

## Sections

- [01 Script Reorganization](01_script_reorganization/README.md)
- [02 Flag Update](02_flag_update/README.md)
- [03 UART TX FIFO](03_uart_tx_fifo/README.md)
- [04 Bootloader Cycle Reporting](04_bootloader_cycle_reporting/README.md)
- [05 Test And Acceptance](05_test_and_acceptance/README.md)

## Decisions Preserved

- The top-level `scripts/` directory will contain three canonical scripts:
  - `scripts/build_bitstream.sh`
  - `scripts/compile_payload.sh <payload>`
  - `scripts/upload_greymecha.ps1 -Payload <name> [-Drive D:\] [-Port COM17] [-BuildBitstream]`
- Old scripts remain available as compatibility wrappers where useful and are archived under `old/`.
- The flag value becomes:

```text
grey{mmio_fuzzz}
```

- `uart_mmio` gains a 32-byte UART TX FIFO.
- Bootloader cycle reporting prints cycle start, end, and delta values, then returns to `READY` after a returning payload.
- Cycle values are printed as 64-bit hexadecimal values.

## Non-Goals

- Do not modify existing `docs/plan_sectioned/` content while saving this plan.
- Do not alter implementation behavior as part of this documentation task.
- Do not update generated distribution artifacts during this documentation-only pass.

