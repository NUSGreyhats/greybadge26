#!/usr/bin/env python3
"""Trace each pmod_j2 output back through the decomp netlist far enough to
reach the LUTs/FFs that produce it.  Print the structural chain so we can
identify the ROM.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "verilog" / "main_decomp.v"

# (ball, top-level signal candidate)
PMODS = [
    ("A14[pmod_j2_0]", "MIB_R0C65_PIOT0_JTXDATA0B_SIOLOGIC"),
    ("A13[pmod_j2_1]", "MIB_R0C65_PIOT0_JTXDATA0A_SIOLOGIC"),
    ("A12[pmod_j2_2]", "MIB_R0C53_PIOT0_PADDOB_PIO"),
    ("A11[pmod_j2_3]", "MIB_R0C53_PIOT0_JTXDATA0A_SIOLOGIC"),
    ("B14[pmod_j2_4]", "MIB_R0C67_PIOT0_JTXDATA0A_SIOLOGIC"),
    ("B13[pmod_j2_5]", "MIB_R0C60_PIOT0_PADDOA_PIO"),
    ("B12[pmod_j2_6]", "MIB_R0C56_PIOT0_PADDOA_PIO"),
    ("B11[pmod_j2_7]", "MIB_R0C49_PIOT0_PADDOA_PIO"),
]

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


def chase(name, max_depth=400):
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


for label, target in PMODS:
    if target not in assigns:
        print(f"\n{label}  *** {target} is not assigned (probably a top-level driver pad, see slice trace ***")
        continue
    chain, why = chase(target)
    print(f"\n{label}  {target}  ({why})")
    for c in chain[-12:]:
        print(f"    {c}")
