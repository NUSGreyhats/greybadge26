# PCB ↔ Bitstream Functionality Map

Cross-referencing the bitstream-only RE in [`BEHAVIOR.md`](BEHAVIOR.md) with the
KiCad schematic and PCB at `greymechaarmy_v2/hardware/greybadge_pcb/`. Source PCB
file: `greybadge_pcb.kicad_pcb`. The FPGA is reference designator **U8**
(`ECP5U_25_CABGA256` on a `BGA-256_14.0x14.0mm_Layout16x16_P0.8mm` footprint, placed
on the bottom side: `(layer "B.Cu")`).

Generated data: [`analysis/fpga_pinmap.csv`](analysis/fpga_pinmap.csv),
[`analysis/net_endpoints.csv`](analysis/net_endpoints.csv).

## 1. What the Bitstream Actually Wires Up

All 28 unique CABGA256 balls programmed by `main.bit`, paired with their PCB net
and the *other side* of that net:

| Ball | PCB net | Bitstream dir | Other endpoint | What it does on the board |
|------|---------|---------------|----------------|----------------------------|
| **A7** | `clk`  | input | **X1 SiT2001B pin 5** | **MEMS oscillator output → bitstream's `G_HPBX0300`** |
| A5  | `A5`   | input | SW1 pad 2, R1 10 kΩ pull-up | User push button SW1 |
| A3  | `A3`   | (input¹) | J1 pin 11 | Expansion-header pin |
| A9  | `A9`   | (input¹) | J1 pin 7  | Expansion-header pin |
| A11 | `A11`  | (output²) | J2 pin 11 | Expansion-header pin |
| A13 | `A13`  | (input/output) | J2 pin 7  | Expansion-header pin |
| B9  | `B9`   | input | J1 pin 8  | Expansion-header pin |
| B10 | `B10`  | input | J1 pin 6  | Expansion-header pin |
| B11 | `B11`  | input | J2 pin 12 | Expansion-header pin |
| B12 | `B12`  | input | J2 pin 10 | Expansion-header pin |
| B13 | `B13`  | input | J2 pin 8  | Expansion-header pin |
| B14 | `B14`  | input | J2 pin 6  | Expansion-header pin |
| **C4** | `C4`  | output | **LED D5 anode** | User LED |
| **C5** | `C5`  | output | **LED D2 anode** | User LED |
| **C6** | `C6`  | output | **LED D6 anode** | User LED |
| C7  | `clkt0_1` | (config) | (only on U8) | Dedicated FPGA clock-input ball, *not wired to anything else on PCB* |
| C8  | `CLKT1_0` | (config) | (only on U8) | Dedicated clock-input ball, not externally wired |
| D9  | `unconnected-…PadD9`  | (output) | — | FPGA fitter picked a free ball; nothing on PCB |
| D10 | `unconnected-…PadD10` | (output) | — | Same — orphan output |
| D11 | `D11`  | (config) | — | Net labelled but no other endpoint |
| D12 | `D12`  | (config) | SW2 + R3 10 kΩ + RP2350 pin 10 | Button SW2 shared with MCU (not actively driven by bitstream) |
| D13 | `D13`  | (config) | GC9A01 display pin 11 + RP2350 pin 9 | LCD signal shared with MCU |
| E4  | `unconnected-…PadE4` | (output) | — | Orphan |
| E5  | `unconnected-…PadE5` | (output) | — | Orphan |
| E6  | `unconnected-…PadE6` | (output) | — | Orphan |
| E7  | `clk0_1`   | (config) | — | Dedicated clock-input ball, unwired |
| E8  | `CLKT1_1`  | (config) | — | Dedicated clock-input ball, unwired |
| A2  | `A2`       | (config) | — | Net labelled but unrouted to other parts |

¹ direction listed by `io_pins.csv` is `input` because the IOLOGIC-side direction is what the bitstream encodes; the per-pad cone analysis shows some are LVCMOS25 outputs driven by the same fabric — see §3.

² A11's data path is constant `1'b1` ([`verilog/pads/pad_A11_PADDOB_PIO.v`](verilog/pads/pad_A11_PADDOB_PIO.v)) — i.e. the pin is held high.

## 2. The Three Functional Groups

### 2.1 Clock — A7 = SiT2001B

`A7` connects to pin 5 of **X1**, a Silicon Labs **SiT2001B** MEMS oscillator
(typical for badges: 16 / 25 / 33 MHz, factory-programmed). Pin 5 is the
oscillator's output. This single net is the **primary clock** that becomes
`G_HPBX0300` inside the bitstream and drives 986 of the 1015 sequential FFs.
*The exact frequency is in the oscillator's order code, which is not present in
the bitstream or schematic value field — both list only "SiT2001B" generically.*

### 2.2 User-facing IO — 3 LEDs + button + headers

Active outputs:

- **D2 / D5 / D6 LEDs** → C5 / C4 / C6. The bitstream drives each as a
  registered LVCMOS25 output. Each LED is wired anode-to-FPGA, cathode-to-GND
  through a 470 Ω resistor.
- **J1 / J2 (2×6 pin sockets, 2.54 mm, horizontal)** → 10 FPGA balls
  (A3, A9, B9, B10 on J1; A11, A13, B11, B12, B13, B14 on J2). Pins 1, 2 are
  +3V3, pins 3, 4 are GND. The remaining 8 IO pins per connector are FPGA-driven
  expansion / debug pins. These are the same pins as the bitstream's shift-chain
  cones.

Active input:

- **SW1** → A5 via 10 kΩ pull-up. Bitstream reads it but, per cone analysis, no
  user output pad's logic ever uses A5 — the input is read into FFs that don't
  reach the LVCMOS25 outputs. Likely scanned for SR/clear or just sampled into a
  dead path by the fitter.

### 2.3 Right-edge IOLOGIC chain — drives the SPI flash MSPI interface

The 948 right-edge FFs (the bulk of the design) that the bitstream-only
analysis flagged as "DDR/SSTL-style IOLOGIC" actually correspond to the
**MSPI/MASTER-SPI configuration interface to the on-board SPI flash**, not
SDRAM. The PCB shows:

| FPGA right-edge ball | PCB net | Other endpoint |
|---------------------|---------|----------------|
| **N8** | `sd_cs`   | W25Q128JVSIM pin 1 (CS#) + R45 10 kΩ pull-up |
| **N9** | `sd_clk`  | W25Q128JVSIM pin 6 (CLK) + R40 10 kΩ |
| **M7** | `sd_io2`  | W25Q128JVSIM pin 3 (~WP / IO2) + R44 10 kΩ |
| **N7** | `sd_io3`  | W25Q128JVSIM pin 7 (~HOLD / IO3) + R42 10 kΩ |
| (sdi / sdo / sd_clk to other balls) | `sdi`, `sdo` | W25Q128JVSIM pins 2, 5 |

**U9 is a Winbond W25Q128JVSIM, 128-Mbit SPI flash** — the standard "bitstream-
storage" flash for an ECP5. On power-up the FPGA's MSPI master reads
configuration from this flash; the bitstream we just RE'd is the *result* of
that load. The negedge-clocked 24-FF chain in §BEHAVIOR.md ("input on
`MIB_R2C72_PICR0_JDIA`") is the **SPI MISO sampling shift register**, and the
~950 IOLOGIC FFs on the right edge are the SPI command/address/data SDR/QSPI
DDR pipelines.

The SSTL18 IO standard the bitstream programs into these tiles isn't being
electrically used as SSTL18 (the W25Q128 is a 3.3 V SPI part) — the fitter just
chose those standards because the right edge of the ECP5 also supports MIPI/DDR.
At runtime the pins are 3.3 V CMOS.

## 3. PCB Resources the Bitstream Does *Not* Use

The board exposes a lot more to the FPGA than the bitstream touches. From the
KiCad netlist, here is what is wired to U8 but unused by `main.bit`:

| Group | FPGA balls | Other endpoints |
|-------|-----------|-----------------|
| 4 more buttons | B4 (SW4), B5 (SW5), B6 (SW3), A6 (SW7) | SW3-7 + 10 kΩ pull-ups |
| 6 more LEDs | C3 (D1), D3 (D3), D4 (D8), D5 (D4), D6 (D7) | LED anodes |
| Buzzer | F16 | BZ1 piezo + RP2350 pin 33 |
| Round LCD | C13, C14, D13, D14, E14 | **GC9A01 IPS display** pins shared with RP2350 |
| RP2350 GPIO | A15 (pin 12), B15 (13), B16 (14), C12 (3), C13 (5), C14 (4), C15 (15), C16 (16), D12 (10), D13 (9), D14 (8), D16 (17), E14 (7), E15 (18), E16 (19) | MCU GPIO direct connections |
| PMOD-style ports | B1/B2 (`PMOD1±`), C1/C2 (`PMOD2±`) → J6 | Differential / single-ended PMOD on J6 |
| Third 2×6 header J6 | B1, B2, C1, C2, D1, E1, E2, F2 | J6 pins 5-12 |
| More header pins | A4 (J1.12), A8 (J1.9), A10 (J1.5), A12 (J2.9), A14 (J2.5) | More J1/J2 pins |
| JTAG | **M10** = `fpga_tdo` (+ JP1), **R11** = `fpga_tdi` (+ JP3), (TCK/TMS via separate balls + JP2/JP4) | RP2350-driven JTAG for bitstream upload |
| Config | **N10** = `cfg_0`, **P10** = `cfg_1`, **R10** = `cfg_2` (each + 10 kΩ to +3V3) | FPGA configuration-mode strap pins |
| Reset / Done | **R9** = `creset` (+ R46 + JP5), **P9** = `cdone` (+ Q2 NMOS gate) | RP2350 reset of FPGA + FPGA-done signaling |
| `gp6`, `R12-R16`, `T2-T4`, `T13-T15`, etc. | banks 6/7/8 right-side balls | Various named nets going to RP2350 / test points |

This bitstream therefore exercises **a small subset** of the badge hardware:
just the LED triplet C4-C6, the J1/J2 expansion headers, the SiT2001B clock,
SW1, and the SPI-flash MSPI interface. The LCD, buzzer, PMODs, RP2350-shared
GPIO, and the other buttons/LEDs are all idle.

## 4. Bitstream-Behavior → Hardware Behavior Translation

Combining §1 of `BEHAVIOR.md` with the PCB:

1. **On power-up**, the ECP5 reads `main.bit` (this file) from W25Q128 flash
   over its right-edge MSPI interface (the 948-FF IOLOGIC pipeline). The chip
   pulls `cdone` (P9) high through Q2 once configured.
2. The MEMS oscillator X1 starts the moment +3V3 is present, providing the
   `clk` net continuously on ball A7.
3. After configuration, the bitstream's main logic runs on `G_HPBX0300`
   (A7 / X1 buffered onto the global clock spine). The 67-FF user shift chain
   walks state through PLC2 fabric cells on the top edge of the die, driven by
   a clock-enable derived from a LUT cone on `R10C10`.
4. The chain's terminal taps drive:
   - LVCMOS25 outputs on balls **C4 → D5 LED**, **C5 → D2 LED**, **C6 → D6 LED**.
     So three LEDs blink/scan as the shift chain advances.
   - Balls A3, A9, B9, B10, A11, A13, B11-B14 driving **J1 / J2 expansion
     headers**. These are externally probable signals (the same kind of layout
     used by `tinyfpga_bx`-style probe bitstreams).
5. The pad-tristate enables on most of these outputs are constant `1`, so they
   are always driving (not bidirectional).
6. SW1 (A5) is sampled but its data only feeds into FFs that don't reach the
   user-visible LEDs/headers — so visually the button has no effect on the
   exposed outputs in this configuration.

In short, `main.bit` is best described as a **post-config probe / scan-chain
demo** that:
- comes up from MSPI flash,
- runs on the on-board 25-MHz-class MEMS oscillator (frequency from the SiT2001B
  order code, not in the bitstream),
- drives a periodic / pseudo-random pattern out to three onboard LEDs and the
  two 2×5 expansion headers,
- ignores the rest of the badge peripherals (LCD, buzzer, RP2350 GPIO, PMODs,
  buttons SW2-SW7, the other LEDs).
