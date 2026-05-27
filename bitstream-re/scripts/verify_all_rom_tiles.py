#!/usr/bin/env python3
"""Read all 7 secure_memory ROM tiles directly and verify against expected flag."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC  = ROOT / "verilog" / "main_decomp.v"

GP_PADS = {
    "MIB_R0C67_PIOT0_JPADDIB_PIO":   0,  # GP8  = addr[0]
    "MIB_R2C72_PICR0_JDIB":           1,  # GP9  = addr[1]
    "MIB_R2C72_PICR0_JDIA":           2,  # GP10 = addr[2]
    "MIB_R5C72_PICR0_JDIB":           3,  # GP11 = addr[3]
    "MIB_R5C72_PICR0_JDIA":           4,  # GP12 = addr[4]
}

print("Parsing assigns …")
assigns = {}
with SRC.open() as f:
    pat = re.compile(r"^assign\s+([^=\s]+)\s*=\s*([^;]+);")
    for line in f:
        m = pat.match(line)
        if m:
            assigns[m.group(1).strip()] = m.group(2).strip()
print(f"  {len(assigns)} assigns")

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

print("Parsing tiles …")
TILES_WANT = {"R2C53","R2C54","R2C55","R2C57","R2C60","R2C64","R2C65"}

init_pat  = re.compile(r"\.SLICEA_LUT([01])_INITVAL\(16'b([01]+)\)")
dmux_pat  = re.compile(r"\.SLICEA_D([01])MUX\(\"([01])\"\)")
inst_pat  = re.compile(r"\)\s+(R\d+C\d+)_PLC2_inst\s*\(")
port_pat  = re.compile(r"\.([A-Z][A-Z0-9_]*)\s*\(\s*([^)\s]+)\s*\)")

tile_data = {}
with SRC.open() as f:
    for line in f:
        if not line.startswith("tile_PLC2"):
            continue
        mi = inst_pat.search(line)
        if not mi or mi.group(1) not in TILES_WANT:
            continue
        key = mi.group(1)
        inits = {int(k): v for k, v in init_pat.findall(line)}
        muxs  = {int(k): int(v) for k, v in dmux_pat.findall(line)}
        body  = line[line.index(f"{key}_PLC2_inst"):]
        ports = dict(port_pat.findall(body))
        # Resolve all sliceA inputs
        inputs = {}
        for pn in ["A0","B0","C0","D0","A1","B1","C1","D1","M0","M1"]:
            wire = ports.get(f"{pn}_SLICE")
            if wire:
                resolved = follow(wire)
                gp_i = GP_PADS.get(resolved)
                inputs[pn] = ("gp", gp_i) if gp_i is not None else ("other", resolved)
        tile_data[key] = {"inits": inits, "muxs": muxs, "inputs": inputs}
print(f"  {len(tile_data)} tiles")

def lut4(init_str, a, b, c, d):
    idx = a | (b << 1) | (c << 2) | (d << 3)
    return int(init_str[15 - idx])

def get_input_val(tile, pn, n):
    """Get value of input port pn for 5-bit RP2350 address n."""
    kind, val = tile["inputs"].get(pn, ("other","?"))
    if kind == "gp":
        return (n >> val) & 1
    # Check if D{i}MUX hardwires it
    # For D0: muxs.get(0), for D1: muxs.get(1)
    dm_key = 0 if pn[0] == "D" and pn[1] == "0" else (1 if pn[0] == "D" and pn[1] == "1" else None)
    if dm_key is not None and tile["muxs"].get(dm_key, 0) == 1:
        return 1
    return 0

def eval_ofx0(tile, n):
    """Evaluate PFUMX of sliceA: sel = M0, LUT0 or LUT1 based on sel."""
    sel_kind, sel_val = tile["inputs"].get("M0", ("other", "?"))
    if sel_kind == "gp":
        sel = (n >> sel_val) & 1
    else:
        sel = 0
    lut_idx = 1 if sel else 0
    init_str = tile["inits"].get(lut_idx, "0"*16)
    dm = tile["muxs"].get(lut_idx, 0)
    port_suffix = str(lut_idx)  # "0" or "1"
    # Inputs: A{lut_idx}, B{lut_idx}, C{lut_idx}, D{lut_idx}
    ports = [f"A{port_suffix}", f"B{port_suffix}", f"C{port_suffix}", f"D{port_suffix}"]
    vals = []
    for i, p in enumerate(ports):
        if i == 3 and dm == 1:
            vals.append(1)
        else:
            vals.append(get_input_val(tile, p, n))
    return lut4(init_str, *vals)

# Print per-tile input info for debugging
print("\n=== Tile input wiring (for sliceA) ===")
for tk, td in sorted(tile_data.items()):
    print(f"\n{tk}:")
    for pn in ["A0","B0","C0","D0","A1","B1","C1","D1","M0"]:
        k, v = td["inputs"].get(pn, ("?","?"))
        dmux = td["muxs"].get(int(pn[-1]) if pn[0]=="D" else -1, "?")
        print(f"  {pn}: {k}={v}  (D{pn[-1]}MUX={dmux})" if pn[0]=="D" else f"  {pn}: {k}={v}")
    for li, iv in sorted(td["inits"].items()):
        dm = td["muxs"].get(li,"?")
        print(f"  LUT{li} INIT={iv}  D{li}MUX={dm}")

# Bit→Tile mapping (pmod_j2[i] → mem_value[i] → FF in tile)
BIT_TILE = {0:"R2C64", 1:"R2C57", 2:"R2C55", 3:"R2C53", 4:"R2C65", 5:"R2C60"}

EXPECTED = list("grey{race_flag}")

print("\n=== ROM evaluation (6-bit) ===")
for addr in range(32):
    byte6 = 0
    for bit_i, tk in BIT_TILE.items():
        td = tile_data.get(tk)
        if td:
            v = eval_ofx0(td, addr)
            byte6 |= v << bit_i
    ex_ch = EXPECTED[addr] if addr < len(EXPECTED) else " "
    ex6 = ord(ex_ch) & 0x3F if addr < len(EXPECTED) else -1
    mark = "✓" if byte6 == ex6 else "✗"
    print(f"  addr {addr:2d}  6b=0x{byte6:02X}  ex6=0x{ex6:02X}  {mark}  '{chr(byte6+0x40)}'vs'{ex_ch}'")
