#!/usr/bin/env python3
"""
Evaluate the secure_memory ROM with correct D1MUX handling.

For every ROM bit FF, we need to:
1. Read the tile parameters including D0MUX / D1MUX to know if D0 or D1
   are hard-wired to VCC (logic 1).
2. Read the actual input connections from the tile port list.
3. Evaluate LUT0 and LUT1 with the correct D values.

RP2350 sends address n on GP8-GP12 as:
  GP8 = n[0] (LSB sent on first pin in DATA_PINS array)
  GP9 = n[1]
  GP10 = n[2]
  GP11 = n[3]
  GP12 = n[4] (MSB)

FPGA ROM LUT sees:
  PFUMX select M = GP8 = n[0]  → when n[0]=0: LUT0; when n[0]=1: LUT1
  LUT A = GP12 = n[4]
  LUT B = GP9  = n[1]
  LUT C = GP11 = n[3]
  LUT D = GP10 = n[2]   (if DNMUX="0")
       OR = 1           (if DNMUX="1")
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC  = ROOT / "verilog" / "main_decomp.v"

GP_PADS = {
    "MIB_R0C67_PIOT0_JPADDIB_PIO":   0,  # GP8  = n[0]
    "MIB_R2C72_PICR0_JDIB":           1,  # GP9  = n[1]
    "MIB_R2C72_PICR0_JDIA":           2,  # GP10 = n[2]
    "MIB_R5C72_PICR0_JDIB":           3,  # GP11 = n[3]
    "MIB_R5C72_PICR0_JDIA":           4,  # GP12 = n[4]
}

print("Parsing assigns …")
assigns = {}
with SRC.open() as f:
    pat = re.compile(r"^assign\s+([^=\s]+)\s*=\s*([^;]+);")
    for line in f:
        m = pat.match(line)
        if m:
            assigns[m.group(1).strip()] = m.group(2).strip()

SINGLE_TOKEN = re.compile(r"^[\\A-Za-z0-9_.]+$")

def follow(sig, max_steps=256):
    seen = {sig}
    cur = sig
    for _ in range(max_steps):
        rhs = assigns.get(cur)
        if rhs is None:
            return cur
        if SINGLE_TOKEN.match(rhs):
            if rhs in seen:
                return rhs
            seen.add(rhs)
            cur = rhs
        else:
            return cur
    return cur

def gp_index(resolved_sig):
    """Return GP bit index (0-4) if this signal is a GP pad, else None."""
    return GP_PADS.get(resolved_sig)

def is_const_1(resolved_sig):
    """Return True if the signal is an unresolved local wire.
    We've confirmed that unresolved local wires in ROM LUTs are VCC-tied
    via the D1MUX parameter.  We detect them as wires not in assigns and
    not pad names.
    """
    if resolved_sig in GP_PADS:
        return False
    if resolved_sig.startswith("MIB_") or resolved_sig.startswith("CIB_"):
        return False
    # If not in assigns, it's a local constant (VCC or GND)
    # The D1MUX="1" tells us these particular wires are VCC
    return True


print("Parsing tiles …")
TILES_OF_INTEREST = {"R2C53", "R2C55", "R2C57", "R2C60", "R2C64", "R2C65"}
tile_data = {}

init_pat  = re.compile(r"\.SLICEA_LUT([01])_INITVAL\(16'b([01]+)\)")
mux_pat   = re.compile(r"\.SLICEA_D([01])MUX\(\"([01])\"\)")
inst_pat  = re.compile(r"\)\s+(R\d+C\d+)_PLC2_inst\s*\(")
port_pat  = re.compile(r"\.([A-Z][A-Z0-9_]*)\s*\(\s*([^)\s]+)\s*\)")

with SRC.open() as f:
    for line in f:
        if not line.startswith("tile_PLC2"):
            continue
        mi = inst_pat.search(line)
        if not mi or mi.group(1) not in TILES_OF_INTEREST:
            continue
        key = mi.group(1)
        inits = {int(k): v for k, v in init_pat.findall(line)}
        muxs  = {int(k): int(v) for k, v in mux_pat.findall(line)}
        body  = line[line.index(f"{key}_PLC2_inst"):]
        ports = dict(port_pat.findall(body))
        tile_data[key] = {"inits": inits, "muxs": muxs, "ports": ports}

print(f"  {len(tile_data)} tiles loaded")

def get_lut_input(tile_key, port_name):
    wire = tile_data[tile_key]["ports"].get(f"{port_name}_SLICE")
    if wire is None:
        return ("const", 0)
    resolved = follow(wire)
    gp_i = gp_index(resolved)
    if gp_i is not None:
        return ("gp", gp_i)
    return ("const", 0)  # unresolved local wire = constant 0 by default

def eval_lut(tile_key, lut_idx, n):
    """Evaluate one LUT for the given 5-bit RP2350 address n.
    n[0]=GP8, n[1]=GP9, n[2]=GP10, n[3]=GP11, n[4]=GP12.
    """
    td = tile_data[tile_key]
    muxs = td["muxs"]
    inits = td["inits"]
    # sliceA: LUT0 uses inputs A0,B0,C0,D0; LUT1 uses A1,B1,C1,D1
    port_names = {0: ("A0","B0","C0","D0"), 1: ("A1","B1","C1","D1")}[lut_idx]
    dm = muxs.get(lut_idx, 0)  # D{lut_idx}MUX: 0=external, 1=VCC

    init_str = inits.get(lut_idx, "0"*16)
    vals = []
    for i, pn in enumerate(port_names):
        if i == 3 and dm == 1:
            # D input hardwired to 1
            vals.append(1)
        else:
            kind, v = get_lut_input(tile_key, pn)
            if kind == "gp":
                vals.append((n >> v) & 1)
            else:
                vals.append(0)
    a, b, c, d = vals
    idx = a | (b << 1) | (c << 2) | (d << 3)
    return int(init_str[15 - idx])

def pfumx_sel(tile_key, n):
    """Return PFUMX select value = M0 = GP8 = n[0]."""
    wire = tile_data[tile_key]["ports"].get("M0_SLICE")
    if wire is None:
        return 0
    resolved = follow(wire)
    gp_i = gp_index(resolved)
    if gp_i is not None:
        return (n >> gp_i) & 1
    return 0

def eval_ofx0(tile_key, n):
    """Evaluate the OFX0 (PFUMX) for sliceA of the given tile."""
    sel = pfumx_sel(tile_key, n)
    lut_idx = 1 if sel else 0
    return eval_lut(tile_key, lut_idx, n)


# The mem_value[i] → tile mapping (from rom_walker2):
MEM_VALUE_TILES = {
    0: "R2C64",
    1: "R2C57",
    2: "R2C55",
    3: "R2C53",
    4: "R2C65",
    5: "R2C60",
    # bits 6, 7 need separate handling
}

print("\n=== Secure Memory ROM (6-bit output, addresses 0-31) ===")
print(f"{'addr':>5}  {'bin':>5}  {'6-bit':>6}  char")
for addr in range(32):
    byte_val = 0
    for bit_idx, tile in MEM_VALUE_TILES.items():
        if tile not in tile_data:
            continue
        v = eval_ofx0(tile, addr)
        byte_val |= v << bit_idx
    ch = chr(byte_val) if 32 <= byte_val <= 126 else "."
    flagch = "grey{race_flag}"[addr] if addr < 15 else " "
    match = "✓" if addr < 15 and ch == flagch else " "
    print(f"  {addr:3d}  {addr:05b}  0x{byte_val:02X}   '{ch}'  {match} (expected: '{flagch}')")

# Also try with D1MUX forced to 1 for all tiles (already done above via muxs dict)
print()
print("=== Checking if bit6 matters: printing 7-bit values ===")
# For bit 6, try to find it from the R2C54 tile
R2C54_DATA = None
r2c54_pat = re.compile(r"\.SLICEA_LUT([01])_INITVAL\(16'b([01]+)\)")
r2c54_dm  = re.compile(r"\.SLICEA_D([01])MUX\(\"([01])\"\)")
r2c54_m   = re.compile(r"\.M0_SLICE\(([^)]+)\)")
with SRC.open() as f:
    for line in f:
        if not line.startswith("tile_PLC2"):
            continue
        mi = inst_pat.search(line)
        if not mi or mi.group(1) != "R2C54":
            continue
        body = line[line.index("R2C54_PLC2_inst"):]
        ports = dict(port_pat.findall(body))
        inits2 = {int(k): v for k, v in r2c54_pat.findall(line)}
        muxs2  = {int(k): int(v) for k, v in r2c54_dm.findall(line)}
        R2C54_DATA = {"inits": inits2, "muxs": muxs2, "ports": ports}
        print(f"\nR2C54 sliceA:")
        for k in ["A0","B0","C0","D0","A1","B1","C1","D1","M0"]:
            w = ports.get(f"{k}_SLICE")
            if w:
                print(f"  {k} -> {follow(w)}")
        for k, v in inits2.items():
            print(f"  LUT{k} INIT = {v}")
        for k, v in muxs2.items():
            print(f"  D{k}MUX = {v}")
        break
