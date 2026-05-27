#!/usr/bin/env python3
"""Dump LUT INITVAL parameters for selected PLC2 tiles."""
import re
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "verilog" / "main_decomp.v"

WANTED = {
    "R2C7", "R2C8", "R2C9", "R2C10", "R2C11", "R2C12", "R2C14",
    "R3C1", "R3C13", "R4C1",
}

inst_pat = re.compile(r"^tile_PLC2\b.*?\)\s+(R(\d+)C(\d+))_PLC2_inst\s*\(", re.DOTALL)
init_pat = re.compile(r"\.SLICE([ABCD])_LUT([01])_INITVAL\(16'b([01]+)\)")
mode_pat = re.compile(r"\.SLICE([ABCD])_MODE\(\"([^\"]+)\"\)")

with SRC.open() as f:
    for line in f:
        if not line.startswith("tile_PLC2"):
            continue
        m = inst_pat.match(line)
        if not m:
            continue
        key = m.group(1)
        if key not in WANTED:
            continue
        # find all INITVAL and MODE entries
        inits = {(s[0], s[1]): s[2] for s in init_pat.findall(line)}
        modes = dict(mode_pat.findall(line))
        print(f"\n{key}:")
        for slice_id in ("A", "B", "C", "D"):
            mode = modes.get(slice_id, "")
            if mode:
                print(f"  SLICE{slice_id} MODE={mode}")
            for k in ("0", "1"):
                key2 = (slice_id, k)
                if key2 in inits:
                    init = inits[key2]
                    lsb = init[-1]
                    print(f"    SLICE{slice_id}.LUT{k}.INIT = {init}  (LSB={lsb})")
