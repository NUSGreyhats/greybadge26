# 06 - GreyMecha/Army Board Reference

## Discovered Local References

Greybadge25:

```text
C:\Users\zunmun\Documents\Stuff\Github\WORK\GreyHats\greybadge25\hardware\greybadge_pcb\greybadge_pcb.kicad_pro
C:\Users\zunmun\Documents\Stuff\Github\WORK\GreyHats\greybadge25\hardware\greybadge_pcb\ecp5_25_fpga.kicad_sch
C:\Users\zunmun\Documents\Stuff\Github\WORK\GreyHats\greybadge25\hardware\greybadge_pcb\greybadge_pcb.kicad_sch
C:\Users\zunmun\Documents\Stuff\Github\WORK\GreyHats\greybadge25\hardware\greybadge_pcb\rp2350.kicad_sch
C:\Users\zunmun\Documents\Stuff\Github\WORK\GreyHats\greybadge25\firmware\ecp5
```

Greybadge26/GreyMechaArmy v2:

```text
C:\Users\zunmun\Documents\Stuff\Github\WORK\GreyHats\greybadge26\greymechaarmy_v2\hardware\greybadge_pcb\greybadge_pcb.kicad_pro
C:\Users\zunmun\Documents\Stuff\Github\WORK\GreyHats\greybadge26\greymechaarmy_v2\hardware\greybadge_pcb\ecp5_25_fpga.kicad_sch
C:\Users\zunmun\Documents\Stuff\Github\WORK\GreyHats\greybadge26\greymechaarmy_v2\hardware\greybadge_pcb\greybadge_pcb.kicad_sch
C:\Users\zunmun\Documents\Stuff\Github\WORK\GreyHats\greybadge26\greymechaarmy_v2\hardware\greybadge_pcb\rp2350.kicad_sch
C:\Users\zunmun\Documents\Stuff\Github\WORK\GreyHats\greybadge26\greymechaarmy_v2\hardware\greybadge_pcb\greybadge_pcb.kicad_pcb
```

## What To Extract From The Schematics

Before final hardware work, extract and record:

- ECP5 exact part/package.
- Clock source and frequency.
- FPGA reset source.
- UART path: direct USB-UART, RP2350 bridge, or board interconnect.
- LED pins and voltage bank.
- Display interface pins and voltage bank.
- Any interconnect pins between RP2350 and FPGA.
- Programming interface and boot mode.
- Power rails used by FPGA IO banks.

Do not assume Greybadge25 and Greybadge26 pinouts match. Use Greybadge25 tests as known examples, but verify final constraints against the target board schematic.

## Known Greybadge25 ECP5 Flow

The discovered Greybadge25 test Makefiles build by concatenating Verilog under `src`, synthesizing with Yosys, placing/routing with nextpnr-ecp5, and packing with ecppack.

The observed nextpnr target is:

```text
nextpnr-ecp5 --25k --package CABGA256 --lpf pinout.lpf
```

The observed `uart_flag/pinout.lpf` includes constraints for:

- `clk` at site `A7` as `LVCMOS33`
- `led[0]` through `led[7]` as `LVCMOS25`
- `btn[0]` through `btn[4]` as `LVCMOS25`
- `interconnect[0]` through `interconnect[7]` as `LVCMOS25`

Treat these as evidence for Greybadge25 test designs, not automatic final challenge constraints.

## Simulation Plan For Board Integration

Create a board wrapper simulation around the challenge SoC:

- Instantiate the same top-level ports used by the ECP5 bitstream.
- Tie unused buttons/interconnects to stable values.
- Drive clock/reset according to the board wrapper.
- Model UART at the chosen baud rate.
- Optionally model display SPI as a passive sink that records transactions.
- Assert LED state changes for idle, running, reset, and success.

This catches top-level wiring mistakes before programming the board.

## GreyMecha/Army Board Run Plan

Hardware bring-up should be incremental:

1. Build and program LED blink.
2. Build and program UART TX banner.
3. Build and program UART RX echo.
4. Build and program loader-only challenge shell.
5. Upload `starter_ok`.
6. Upload timeout payload.
7. Upload bad-jump payload.
8. Upload naive C reference.
9. Upload optimized assembly reference.

For every step, capture:

- bitstream name and git revision if available
- target board revision
- LPF/constraint file
- UART port and baud
- UART transcript
- observed LED/OLED state
- pass/fail result

If the RP2350 is part of the UART or programming path, document whether it is running stock badge firmware, a bridge firmware, or a custom test firmware.
