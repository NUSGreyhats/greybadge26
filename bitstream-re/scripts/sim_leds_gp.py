#!/usr/bin/env python3
"""
Simulate the LED outputs as a combinational function of the 8 RP2350
GP pins (GP8..GP15) by evaluating the full LUT tree.

RP2350 GP pin → FPGA ball → pad wire:
  GP8  → A15  → MIB_R0C67_PIOT0_JPADDIB_PIO
  GP9  → B15  → MIB_R2C72_PICR0_JDIB
  GP10 → B16  → MIB_R2C72_PICR0_JDIA
  GP11 → C15  → MIB_R5C72_PICR0_JDIB
  GP12 → C16  → MIB_R5C72_PICR0_JDIA
  GP13 → D16  → MIB_R8C72_PICR0_DQS2_JDIA
  GP14 → E15  → MIB_R8C72_PICR0_DQS2_JDIB
  GP15 → E16  → MIB_R11C72_PICR0_JPADDID_PIO

SW1 button (active-low) → A5 → MIB_R0C18_PIOT0_JPADDIA_PIO
  (idle = 1, pressed = 0)

All other external inputs are treated as 0 (off / idle).

We enumerate all 256 GP8..GP15 combinations (with SW1 forced =1 idle,
then =0 pressed) and look for output bytes that are printable ASCII.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC  = ROOT / "verilog" / "main_decomp.v"

# ---------------------------------------------------------------------------
# External signal → GP bit index
# ---------------------------------------------------------------------------
GP_MAP = {
    "MIB_R0C67_PIOT0_JPADDIB_PIO":         0,  # GP8
    "MIB_R2C72_PICR0_JDIB":                 1,  # GP9
    "MIB_R2C72_PICR0_JDIA":                 2,  # GP10
    "MIB_R5C72_PICR0_JDIB":                 3,  # GP11
    "MIB_R5C72_PICR0_JDIA":                 4,  # GP12
    "MIB_R8C72_PICR0_DQS2_JDIA":            5,  # GP13
    "MIB_R8C72_PICR0_DQS2_JDIB":            6,  # GP14
    "MIB_R11C72_PICR0_JPADDID_PIO":         7,  # GP15
}
SW1_PAD = "MIB_R0C18_PIOT0_JPADDIA_PIO"
# J1 connector PMOD that also appeared in a few expansions; treat as 0
OTHER_PADS = {
    "MIB_R0C6_PIOT0_JPADDIA_PIO",
    "MIB_R0C42_PIOT0_JPADDIA_PIO",
    "MIB_R0C42_PIOT0_JPADDIB_PIO",
    "MIB_R0C67_PIOT0_JPADDIB_PIO",   # already in GP_MAP but list here too
}

# ---------------------------------------------------------------------------
# Parse assigns + tiles
# ---------------------------------------------------------------------------
print("Parsing assigns …")
assigns = {}
with SRC.open() as f:
    pat = re.compile(r"^assign\s+([^=\s]+)\s*=\s*([^;]+);")
    for line in f:
        m = pat.match(line)
        if m:
            assigns[m.group(1).strip()] = m.group(2).strip()
print(f"  {len(assigns)} assigns")

print("Parsing tiles …")
tiles = {}
init_pat    = re.compile(r"\.SLICE([ABCD])_LUT([01])_INITVAL\(16'b([01]+)\)")
inst_nm_pat = re.compile(r"\)\s+(R\d+C\d+)_PLC2_inst\s*\(")
port_pat    = re.compile(r"\.([A-Z][A-Z0-9_]*)\s*\(\s*([^)\s]+)\s*\)")
with SRC.open() as f:
    for line in f:
        if not line.startswith("tile_PLC2"):
            continue
        mi = inst_nm_pat.search(line)
        if not mi:
            continue
        key = mi.group(1)
        inits = {(s,k): v for s,k,v in init_pat.findall(line)}
        body  = line[line.index(f"{key}_PLC2_inst"):]
        ports = dict(port_pat.findall(body))
        tiles[key] = {"inits": inits, "ports": ports}
print(f"  {len(tiles)} tiles")

SINGLE_TOKEN = re.compile(r"^[\\A-Za-z0-9_.]+$")
SLICE_INPUTS = {
    "A": {0: ("A0","B0","C0","D0"), 1: ("A1","B1","C1","D1")},
    "B": {0: ("A2","B2","C2","D2"), 1: ("A3","B3","C3","D3")},
    "C": {0: ("A4","B4","C4","D4"), 1: ("A5","B5","C5","D5")},
    "D": {0: ("A6","B6","C6","D6"), 1: ("A7","B7","C7","D7")},
}
F_IDX_TO_SLICE = {0:("A",0),1:("A",1),2:("B",0),3:("B",1),
                   4:("C",0),5:("C",1),6:("D",0),7:("D",1)}
SLICE_FX_RE  = re.compile(r"^(R\d+C\d+)_PLC2_F5([ABCD])_SLICE$")
SLICE_F_RE   = re.compile(r"^(R\d+C\d+)_PLC2_F(\d)_SLICE$")
SLICE_Q_RE   = re.compile(r"^(R\d+C\d+)_PLC2_Q(\d)_SLICE$")
SLICE_FXY_RE = re.compile(r"^(R\d+C\d+)_PLC2_FX([ABCD])_SLICE$")


def lut4(init_str: str, a: int, b: int, c: int, d: int) -> int:
    idx = a | (b << 1) | (c << 2) | (d << 3)
    return int(init_str[15 - idx])


def eval_sig(sig: str, gp: int, sw1: int, ff_state: dict, cache: dict,
             depth: int = 0) -> int:
    """Evaluate a signal given the GP input vector (8-bit int) and sw1."""
    if sig in cache:
        return cache[sig]
    if depth > 80:
        cache[sig] = 0
        return 0

    # External pad inputs
    if sig in GP_MAP:
        v = (gp >> GP_MAP[sig]) & 1
        cache[sig] = v
        return v
    if sig == SW1_PAD:
        cache[sig] = sw1
        return sw1
    if sig in OTHER_PADS or sig.startswith("MIB_") or sig.startswith("CIB_"):
        cache[sig] = 0
        return 0

    # FF outputs: use ff_state (default 0 if not set)
    mq = SLICE_Q_RE.match(sig)
    if mq:
        v = ff_state.get(sig, 0)
        cache[sig] = v
        return v

    # Follow assign chain
    rhs = assigns.get(sig)
    if rhs is None:
        # Local undriven tile wire → check if it's a constant-tied port
        # In ECP5 decompiler, unconnected tile ports become local wires = 0
        cache[sig] = 0
        return 0
    if SINGLE_TOKEN.match(rhs):
        v = eval_sig(rhs, gp, sw1, ff_state, cache, depth + 1)
        cache[sig] = v
        return v
    # It's an expression – shouldn't happen for single-output assigns,
    # but fall through to 0
    cache[sig] = 0
    return 0


def eval_f_slice(sig: str, gp: int, sw1: int, ff_state: dict, cache: dict,
                 depth: int = 0) -> int:
    """Evaluate a PLC2 F-output or F5 (PFUMX) output."""
    if sig in cache:
        return cache[sig]
    if depth > 60:
        cache[sig] = 0
        return 0

    m = SLICE_FX_RE.match(sig)
    if m:
        tk, sl = m.group(1), m.group(2)
        sl_to_base = {"A":0,"B":2,"C":4,"D":6}
        base = sl_to_base[sl]
        # Evaluate both LUT4s
        inits0 = tiles[tk]["inits"].get((sl,"0"), "0"*16)
        inits1 = tiles[tk]["inits"].get((sl,"1"), "0"*16)
        # LUT0 inputs: A{base}, B{base}, C{base}, D{base}
        a0 = eval_input(tk, f"A{base}", gp, sw1, ff_state, cache, depth+1)
        b0 = eval_input(tk, f"B{base}", gp, sw1, ff_state, cache, depth+1)
        c0 = eval_input(tk, f"C{base}", gp, sw1, ff_state, cache, depth+1)
        d0 = eval_input(tk, f"D{base}", gp, sw1, ff_state, cache, depth+1)
        # LUT1 inputs: A{base+1}, B{base+1}, ...
        a1 = eval_input(tk, f"A{base+1}", gp, sw1, ff_state, cache, depth+1)
        b1 = eval_input(tk, f"B{base+1}", gp, sw1, ff_state, cache, depth+1)
        c1 = eval_input(tk, f"C{base+1}", gp, sw1, ff_state, cache, depth+1)
        d1 = eval_input(tk, f"D{base+1}", gp, sw1, ff_state, cache, depth+1)
        r0 = lut4(inits0, a0, b0, c0, d0)
        r1 = lut4(inits1, a1, b1, c1, d1)
        # PFUMX select: M{base}
        m_wire = tiles[tk]["ports"].get(f"M{base}_SLICE")
        if m_wire:
            sel_sig = assign_chase(m_wire)
            sel = eval_any(sel_sig, gp, sw1, ff_state, cache, depth+1)
        else:
            sel = 0
        v = r1 if sel else r0
        cache[sig] = v
        return v

    m = SLICE_F_RE.match(sig)
    if m:
        tk = m.group(1)
        sl, li = F_IDX_TO_SLICE[int(m.group(2))]
        sl_to_base = {"A":0,"B":2,"C":4,"D":6}
        base = sl_to_base[sl]
        inp_idx = base + li
        init_str = tiles[tk]["inits"].get((sl, str(li)), "0"*16)
        a = eval_input(tk, f"A{inp_idx}", gp, sw1, ff_state, cache, depth+1)
        b = eval_input(tk, f"B{inp_idx}", gp, sw1, ff_state, cache, depth+1)
        c = eval_input(tk, f"C{inp_idx}", gp, sw1, ff_state, cache, depth+1)
        d = eval_input(tk, f"D{inp_idx}", gp, sw1, ff_state, cache, depth+1)
        v = lut4(init_str, a, b, c, d)
        cache[sig] = v
        return v

    # FXA etc – second mux level (OFX1)
    m = SLICE_FXY_RE.match(sig)
    if m:
        cache[sig] = 0
        return 0

    # Q output
    mq = SLICE_Q_RE.match(sig)
    if mq:
        v = ff_state.get(sig, 0)
        cache[sig] = v
        return v

    # External pad
    if sig in GP_MAP:
        v = (gp >> GP_MAP[sig]) & 1
        cache[sig] = v
        return v
    if sig == SW1_PAD:
        cache[sig] = sw1
        return sw1
    if sig.startswith("MIB_") or sig.startswith("CIB_"):
        cache[sig] = 0
        return 0

    # Local wire → chase assign
    rhs = assigns.get(sig)
    if rhs is None:
        cache[sig] = 0
        return 0
    if SINGLE_TOKEN.match(rhs):
        v = eval_any(rhs, gp, sw1, ff_state, cache, depth+1)
        cache[sig] = v
        return v
    cache[sig] = 0
    return 0


def assign_chase(wire: str, max_steps: int = 256) -> str:
    seen = {wire}
    cur = wire
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


def eval_input(tile_key: str, port_base: str, gp: int, sw1: int,
               ff_state: dict, cache: dict, depth: int) -> int:
    """Evaluate a tile input port (A0..D7)."""
    wire_name = tiles[tile_key]["ports"].get(f"{port_base}_SLICE")
    if wire_name is None:
        return 0
    resolved = assign_chase(wire_name)
    return eval_any(resolved, gp, sw1, ff_state, cache, depth)


def eval_any(sig: str, gp: int, sw1: int, ff_state: dict, cache: dict,
             depth: int = 0) -> int:
    if sig in cache:
        return cache[sig]
    # Dispatch
    if SLICE_F_RE.match(sig) or SLICE_FX_RE.match(sig) or SLICE_FXY_RE.match(sig):
        return eval_f_slice(sig, gp, sw1, ff_state, cache, depth)
    return eval_sig(sig, gp, sw1, ff_state, cache, depth)


# ---------------------------------------------------------------------------
# LED pad wires (from earlier trace)
# ---------------------------------------------------------------------------
LED_TERMINALS = {
    "D1": "R2C7_PLC2_F5A_SLICE",
    "D2": "R2C11_PLC2_F5_SLICE",   # F5 = sliceC LUT1
    "D3": "R2C10_PLC2_F6_SLICE",
    "D4": "R2C11_PLC2_F1_SLICE",   # F1 = sliceA LUT1
    "D5": "R2C9_PLC2_FXA_SLICE",   # OFX1 of sliceA = second PFUMX
    "D6": "R2C11_PLC2_F3_SLICE",
    "D7": "R2C11_PLC2_F6_SLICE",
    "D8": "R2C7_PLC2_F5_SLICE",    # F5 = sliceC LUT1
}

# ---------------------------------------------------------------------------
# First: try all GP combinations with SW1=1 (idle, not pressed) and no FF state
# ---------------------------------------------------------------------------
print("\nScanning GP8..GP15 (0..255) with SW1=1, all FFs=0 …")
printable = []
for gp in range(256):
    cache = {}
    ff_state = {}
    byte_val = 0
    for bit_idx, led in enumerate(["D1","D2","D3","D4","D5","D6","D7","D8"]):
        term = LED_TERMINALS[led]
        v = eval_any(term, gp, 1, ff_state, cache)
        byte_val |= (v << bit_idx)
    ch = chr(byte_val) if 32 <= byte_val <= 126 else "."
    if ch != ".":
        printable.append((gp, byte_val, ch))
        if len(printable) <= 60:
            gp_str = format(gp, "08b")
            print(f"  GP={gp_str} ({gp:3d})  byte=0x{byte_val:02X}  '{ch}'")

print(f"\nTotal printable outputs (SW1=1): {len(printable)}")

# Look for flag-like sequences
chars = {}
for gp, bval, ch in printable:
    chars[gp] = ch

# Check consecutive GP values for flag pattern
flag_chars = set("abcdefghijklmnopqrstuvwxyz_{}0123456789")
for start in range(256 - 6):
    run = ""
    for i in range(min(40, 256 - start)):
        c = chars.get(start + i, "")
        if c in flag_chars:
            run += c
        else:
            break
    if len(run) >= 5 and ("grey" in run or "{" in run):
        print(f"\n  POSSIBLE FLAG at GP={start}: {run!r}")

# Now try SW1=0 (button pressed)
print("\nScanning GP8..GP15 (0..255) with SW1=0, all FFs=0 …")
printable2 = []
for gp in range(256):
    cache = {}
    ff_state = {}
    byte_val = 0
    for bit_idx, led in enumerate(["D1","D2","D3","D4","D5","D6","D7","D8"]):
        term = LED_TERMINALS[led]
        v = eval_any(term, gp, 0, ff_state, cache)
        byte_val |= (v << bit_idx)
    ch = chr(byte_val) if 32 <= byte_val <= 126 else "."
    if ch != ".":
        printable2.append((gp, byte_val, ch))

print(f"Total printable outputs (SW1=0): {len(printable2)}")

# Check for consecutive flag-like characters
chars2 = {gp: ch for gp, _, ch in printable2}
for start in range(256 - 6):
    run = ""
    for i in range(min(40, 256 - start)):
        c = chars2.get(start + i, "")
        if c in flag_chars:
            run += c
        else:
            break
    if len(run) >= 5 and ("grey" in run or "{" in run):
        print(f"\n  POSSIBLE FLAG at GP={start}: {run!r}")

# Dump all non-trivial bytes for both modes
print("\n--- All non-zero bytes (SW1=1) ---")
for gp, bv, ch in printable:
    print(f"  0x{gp:02X} = GP[{gp:08b}]  0x{bv:02X} '{ch}'")
