#!/usr/bin/env python3
"""Dump the full port/parameter list of one or more PLC2 tiles."""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC  = ROOT / "verilog" / "main_decomp.v"

WANT = {"R2C11", "R2C9", "R2C8", "R9C10", "R3C12", "R10C9"}

init_pat = re.compile(r"\.SLICE([ABCD])_LUT([01])_INITVAL\(16'b([01]+)\)")
mode_pat = re.compile(r"\.SLICE([ABCD])_MODE\(\"([^\"]+)\"\)")
inst_nm  = re.compile(r"\)\s+(R\d+C\d+)_PLC2_inst\s*\(")
port_pat = re.compile(r"\.([A-Z][A-Z0-9_]*)\s*\(\s*([^)\s]+)\s*\)")

with SRC.open() as f:
    for line in f:
        if not line.startswith("tile_PLC2"):
            continue
        mi = inst_nm.search(line)
        if not mi or mi.group(1) not in WANT:
            continue
        key = mi.group(1)
        inits = {(s,k): v for s,k,v in init_pat.findall(line)}
        modes = dict(mode_pat.findall(line))
        body = line[line.index(f"{key}_PLC2_inst"):]
        ports = dict(port_pat.findall(body))

        print(f"\n=== {key} ===")
        for sl in "ABCD":
            md = modes.get(sl,"")
            for li in (0,1):
                init = inits.get((sl,str(li)),"")
                if init or md:
                    print(f"  slice{sl}.LUT{li}  mode={md}  INIT={init}")
        print("  --- selected ports ---")
        for pname in sorted(ports):
            if any(x in pname for x in
                   ("A0","B0","C0","D0","A1","B1","C1","D1",
                    "A2","B2","C2","D2","A3","B3","C3","D3",
                    "A4","B4","C4","D4","A5","B5","C5","D5",
                    "A6","B6","C6","D6","A7","B7","C7","D7",
                    "M0","M1","M2","M3","M4","M5","M6","M7",
                    "CLK","CE0","DI","LSR")):
                print(f"    .{pname}({ports[pname]})")
