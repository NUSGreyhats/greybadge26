#!/usr/bin/env python3
"""Trace LED-driving signals through the decompiled netlist's assign chain.

For each LED pad, follow the `assign X = Y;` chain until we hit either an
expression (LUT/FF/CCU2 output) or an unbound source.
"""
import re
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "verilog" / "main_decomp.v"

print("Loading assigns…")
assigns = {}
pat = re.compile(r"^assign\s+([^=\s]+)\s*=\s*([^;]+);")
with SRC.open() as f:
    for line in f:
        m = pat.match(line)
        if m:
            assigns[m.group(1).strip()] = m.group(2).strip()
print(f"Got {len(assigns)} assigns")

SINGLE_TOKEN = re.compile(r"^[\\A-Za-z0-9_.]+$")


def chase(name, max_depth=200):
    chain = [name]
    seen = {name}
    cur = name
    while True:
        rhs = assigns.get(cur)
        if rhs is None:
            return chain, "root"
        if SINGLE_TOKEN.match(rhs):
            if rhs in seen:
                chain.append(rhs)
                return chain, "cycle"
            seen.add(rhs)
            chain.append(rhs)
            cur = rhs
            if len(chain) > max_depth:
                return chain, "depth"
        else:
            chain.append(rhs)
            return chain, "expr"


targets = [
    "MIB_R0C11_PIOT0_JTXDATA0A_SIOLOGIC",   # C4 -> D5 LED
    "MIB_R0C15_PIOT0_PADDOA_PIO",            # C5 -> D2 LED
    "MIB_R0C22_PIOT0_JTXDATA0A_SIOLOGIC",   # C6 -> D6 LED
    "MIB_R0C13_PIOT0_PADDOB_PIO",            # D5 -> D4 LED
    "MIB_R0C20_PIOT0_JTXDATA0B_SIOLOGIC",   # D6 -> D7 LED
    "MIB_R0C9_PIOT0_JTXDATA0B_SIOLOGIC",    # D4 -> D8 LED
    "MIB_R2C0_PICL0_JTXDATA0C_IOLOGIC",     # C3 -> D1 LED
    "MIB_R2C0_PICL0_JTXDATA4C_IOLOGIC",     # C3 -> D1 LED (gearbox ch2)
]

for t in targets:
    chain, why = chase(t)
    print(f"\n{t}  ({why}, depth={len(chain)})")
    for i, c in enumerate(chain):
        print(f"  {i:3d}: {c}")
