#!/usr/bin/env python3
"""Read R2C64 sliceA tile parameters directly from main_decomp.v."""
import re
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "verilog" / "main_decomp.v"
ASSIGNS = {}

print("Parsing assigns ...")
with SRC.open() as f:
    pat = re.compile(r"^assign\s+([^=\s]+)\s*=\s*([^;]+);")
    for line in f:
        m = pat.match(line)
        if m:
            ASSIGNS[m.group(1).strip()] = m.group(2).strip()

SINGLE_TOKEN = re.compile(r"^[\\A-Za-z0-9_.]+$")

def follow(sig, max_steps=256):
    seen = {sig}
    cur = sig
    for _ in range(max_steps):
        rhs = ASSIGNS.get(cur)
        if rhs is None:
            return cur
        if SINGLE_TOKEN.match(rhs):
            if rhs in seen:
                return rhs
            seen.add(rhs)
            cur = rhs
        else:
            return rhs
    return cur

print("Looking for R2C64 tile ...")
with SRC.open() as f:
    for line in f:
        if not line.startswith("tile_PLC2"):
            continue
        if "R2C64_PLC2_inst" not in line:
            continue
        print("Found R2C64 tile!")
        # Extract sliceA params
        for param in re.finditer(r"\.SLICEA_([A-Z0-9_]+)\(([^)]+)\)", line):
            print(f"  .SLICEA_{param.group(1)}({param.group(2)})")
        
        # Now resolve sliceA port connections
        port_pat = re.compile(r"\.([A-Z][A-Z0-9_]*)\s*\(\s*([^)\s]+)\s*\)")
        ports = dict(port_pat.findall(line[line.index("R2C64_PLC2_inst"):]))
        
        for pname in ["A0","B0","C0","D0","A1","B1","C1","D1","M0","M1",
                      "F5A","Q0","Q1"]:
            wire = ports.get(f"{pname}_SLICE")
            if wire:
                resolved = follow(wire)
                print(f"  .{pname}_SLICE({wire})  -> {resolved}")
        break
