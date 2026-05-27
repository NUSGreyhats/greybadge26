# LFE5U-25F Bitstream Reverse Engineering — main.bit

Static reverse engineering of `main.bit` using Project Trellis and the VoidMercy ECP5 decompiler. No firmware, schematics, or other repo context was used.

## Input

| Property | Value |
|----------|-------|
| File | `main.bit` |
| Size | 582,369 bytes |
| SHA-256 | `9c2a2bb38f98ac247bdef84a44d666320d6065db019b80f114855ebfb3a5374b` |
| Part (header) | `LFE5U-25F-6CABGA256` |
| IDCODE | `0x41111043` |
| Config frames | 7562 |
| USERCODE | `0x00000000` |

## Toolchain

| Tool | Version |
|------|---------|
| ecpunpack / ecppack | Project Trellis 1.4-2+b4 |
| yosys | 0.52 |
| Decompiler | [VoidMercy/Lattice-ECP5-Bitstream-Decompiler](https://github.com/VoidMercy/Lattice-ECP5-Bitstream-Decompiler) |
| Device DB | `/usr/share/trellis/database/ECP5/LFE5U-25F/` |

## Commands Run

```bash
ecpunpack main.bit main.config
ecppack --idcode 0x41111043 main.config main_roundtrip.bit
python3 scripts/io_pins_iodb.py
python3 scripts/analyze_config.py
python3 scripts/decompile.py
yosys -p 'read_verilog -I.../cells main_decomp.v; synth; flatten; opt; clean; opt_clean; write_verilog main_synth.v'
python3 scripts/annotate_ports.py
```

## Round-Trip Validation

`main_roundtrip.bit` is **byte-identical** to `main.bit` (same SHA-256). Unpack → repack is lossless for this bitstream.

## Structural Findings

### Fabric Utilization

| Resource | Count in config |
|----------|-----------------|
| PLC2 (logic) tiles | 482 (100% programmed) |
| PIOT0 / PIOT1 (IO, top row) | 28 + 28 |
| PICT0 / PICT1 (IO, row 1) | 13 + 10 |
| CIB_PLL3 | 2 |
| CIB_EBR routing | 2 |
| ECLK_L / ECLK_R | 1 + 1 |
| TAP_DRIVE (clock spine) | 34 |

### External IO (CABGA256)

79 IO buffer tiles programmed; **28 package balls** used as functional IO:

**23 inputs** (LVCMOS25, hysteresis on most):

`A2, A3, A5, A7, A9, A11, A13, B9, B10, B11, B12, B13, B14, C4, C5, C6, C7, C8, D9, D10, D11, D12, D13`

**23 outputs** (SSTL18_II — likely paired with on-chip DDR/other IO logic):

Same package sites as inputs (top/bottom IO pairs on shared columns).

Full mapping: [`analysis/io_pins.csv`](analysis/io_pins.csv)

### Block RAM Init

1688 `word: ... INIT ...` entries extracted to [`analysis/ebr_init.hex`](analysis/ebr_init.hex). These are EBR initialization bit patterns embedded in the fabric config.

### Clock / Reset (inferred from netlist)

Decompiled top module exposes global clock inputs:

- `G_HPBX0000`, `G_HPBX0100` — primary global clock network entries
- Multiple `PLC2_CLK*` / `MUXCLK*` chains in PLC2 tiles (R8C5, R8C6 region)

Exact frequency is **not** recoverable from the bitstream alone.

## RTL Recovery

| Artifact | Size | Description |
|----------|------|-------------|
| [`verilog/main_decomp.v`](verilog/main_decomp.v) | 51 MB, 1.15M lines | Gate-level Verilog (TRELLIS_SLICE, PDPW16KD, IO cells) |
| [`verilog/main_synth.v`](verilog/main_synth.v) | 194 MB, 3.66M lines | Yosys synth/flatten/opt lift |
| [`verilog/main_behavior.v`](verilog/main_behavior.v) | 60 MB, 1.34M lines | Yosys condensed top module (139 primitive cells + 2030 processes) |
| [`verilog/main_behavior_noinit.v`](verilog/main_behavior_noinit.v) | 60 MB | Same, with broken `initial` blocks stripped |
| **[`verilog/main_pad_behavior.v`](verilog/main_pad_behavior.v)** | **45 KB, 1366 lines** | **Consolidated RTL: only logic that drives used package balls (start here)** |
| [`verilog/pads/pad_<BALL>_*.v`](verilog/pads/) | 34 files | Per-output-pad backward logic cones |
| [`verilog/main_top_annotated.v`](verilog/main_top_annotated.v) | small | Package-site port naming wrapper |
| [`analysis/port_map.csv`](analysis/port_map.csv) | — | Decompiler port ↔ CABGA256 ball map |
| [`verilog/pads/INDEX.csv`](verilog/pads/INDEX.csv) | — | Per-pad cone size, FF count, clocks |

A behavioral write-up of what the bitstream does is in [`BEHAVIOR.md`](BEHAVIOR.md).
A cross-reference to the actual board nets (KiCad PCB) is in [`PCB_MAPPING.md`](PCB_MAPPING.md).

Decompilation completed with warnings (expected):

- 7 unknown config opcodes (`F2B0`, `F3B0`, …) — likely PLL/DSP-adjacent
- Multiple-driver warnings on IOLOGIC sink nets (decompiler limitation on IO tiles)

## Limitations

| Recoverable | Not recoverable |
|-------------|-----------------|
| Package pin directions and IO standards | Original module/signal names |
| LUT/FF/BRAM configuration | Source comments and parameters |
| EBR init bit patterns | Clock frequency |
| Flat gate-level behavior | Designer intent / software API |
| ~28 used IO balls | PLL config (partially undocumented) |

## Directory Layout

```
bitstream-re/
  main.bit
  main.config              # ecpunpack output (558 KB)
  main_roundtrip.bit       # verified identical to main.bit
  analysis/
    io_pins.csv
    io_summary.json
    tile_summary.json
    ebr_init.hex
    port_map.csv
    port_map.json
  verilog/
    main_decomp.v
    main_synth.v
    main_top_annotated.v
  scripts/
    analyze_config.py
    io_pins_iodb.py
    decompile.py
    annotate_ports.py
```

## Reproduce

From WSL with `trellis` and `yosys` packages installed:

```bash
cd bitstream-re
ecpunpack main.bit main.config
python3 scripts/io_pins_iodb.py
python3 scripts/analyze_config.py
python3 scripts/decompile.py
# yosys step takes ~25 min and ~3.5 GB RAM on this design
python3 scripts/annotate_ports.py
```

Decompiler requires `~/Lattice-ECP5-Bitstream-Decompiler` with `prjtrellis-db` symlinked to `/usr/share/trellis/database`.
