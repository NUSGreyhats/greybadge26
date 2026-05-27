#!/usr/bin/env python3
"""Reverse-engineer the secure_memory ROM straight out of the bitstream.

Strategy (no Verilog source allowed):

1. The 8 pmod_j2 output balls A14, A13, A12, A11, B14, B13, B12, B11 map
   to specific PIO sites in the decompiled netlist (computed below from
   prjtrellis's iodb).  Their `PADDOA/PADDOB` and `JTXDATA*` wires are the
   top-level outputs we need to chase backwards.

2. Walk the `assign` chain (one-token-per-line "wire" assigns produced by
   the decompiler) back from each pmod_j2 ball until we hit a SLICE port
   (`R<row>C<col>_PLC2_<port>_SLICE` etc.).  That terminal node is either:
       a) an OFX0 (PFUMX between two LUT4s) ‒ the typical pattern for a
          5-input LUT (the address is 5 bits wide).
       b) a Q port of a flip-flop holding the registered `mem_value` bit.
       c) a deeper combinational LUT ‒ in which case we keep climbing.

3. Once we land on the registered `mem_value[i]` FF, the LUTs feeding its
   D input are the ROM.  Together these LUTs implement
       mem[address] = ROM
   where the address bits are the 5 routed `interconnect[4:0]` signals.

4. Evaluate each LUT pair across all 32 possible address values to
   recover the 8-bit ROM word at each address.

This script focuses on producing a structural report we can hand-read; the
LUT evaluation step is in `extract_rom_eval.py`.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "verilog" / "main_decomp.v"

PMOD_BALLS = ["A14", "A13", "A12", "A11", "B14", "B13", "B12", "B11"]


def load_ball_to_site():
    iodb = json.loads(
        Path("/usr/share/trellis/database/ECP5/LFE5U-25F/iodb.json").read_text()
    )
    return iodb["packages"]["CABGA256"]


def main():
    pk = load_ball_to_site()
    for ball in PMOD_BALLS:
        info = pk[ball]
        # PIO A/B occupy MIB_R{row}C{col}_PIOT0 (A) or PIOT1 (B). For row 0
        # those are the top edge tiles. For other rows on the left/right
        # edge they are PICL0/1 or PICR0/1.
        row, col, pio = info["row"], info["col"], info["pio"]
        if row == 0:
            tile_a = f"MIB_R0C{col}_PIOT0"
            tile_b = f"MIB_R0C{col}_PIOT1"
        else:
            tile_a = f"MIB_R{row}C{col}_PICL0" if col == 0 else f"MIB_R{row}C{col}_PICR0"
            tile_b = f"MIB_R{row}C{col}_PICL1" if col == 0 else f"MIB_R{row}C{col}_PICR1"
        print(f"{ball:4s}  row={row:3d} col={col:3d} pio={pio}  -> tile A:{tile_a}  B:{tile_b}")


if __name__ == "__main__":
    main()
