#!/usr/bin/env python3
"""
Decode the shooting_flags challenge flag purely from the bitstream.

No Verilog source files are consulted – only main_decomp.v (the
decompiler's output from the bitstream) and the PCB net-endpoint CSV.

Approach
--------
1.  The 8 user LEDs (D1-D8) are driven from FPGA balls
    C3, C5, D3, D5, C4, C6, D6, D4  (from net_endpoints.csv).
2.  Each ball maps to a PIO site obtained from prjtrellis iodb.
3.  We resolve the top-level output pad wire names from the MIB_ / CIB_ /
    R*C* assign chain in main_decomp.v.
4.  Every bit's assign chain terminates in either:
      * an F-output (direct LUT4 output)   -> 4-address bits
      * an F5A-output (OFX0 = PFUMX)       -> 5-address bits
5.  We extract the INIT values of the LUTs that drive each bit, work out
    the address signals (shared across all 8 bits), and evaluate the
    ROM table for addresses 0-31 to reconstruct 8-bit words.
6.  Finally we decode the shooting-flags cyclic-rotate logic:
      displayed[i] = rotl8(flag[i], i % 8)
    by checking which address value produces each rotating pattern.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "verilog" / "main_decomp.v"

# ---------------------------------------------------------------------------
# 1.  LED ball -> PIO mapping  (from iodb + PCB net CSV)
# ---------------------------------------------------------------------------
LED_BALLS = [
    ("C3", "D1"),
    ("C5", "D2"),
    ("D3", "D3"),
    ("D5", "D4"),
    ("C4", "D5"),
    ("C6", "D6"),
    ("D6", "D7"),
    ("D4", "D8"),
]
# Pre-computed from iodb  (row, col, pio)
BALL_TO_PIO = {
    "C3": (2, 0,  "C"),
    "C5": (0, 15, "A"),
    "D3": (2, 0,  "D"),
    "D5": (0, 13, "B"),
    "C4": (0, 11, "A"),
    "C6": (0, 22, "A"),
    "D6": (0, 20, "B"),
    "D4": (0, 9,  "B"),
}

# ---------------------------------------------------------------------------
# 2.  Build the pad-output wire names from the MIB_ naming convention
# ---------------------------------------------------------------------------
# For a given PIO site, the decompiler produces output wires named:
#   row 0 (top edge) : MIB_R0C{col}_PIOT0_PADDOA_PIO      (PIO A, simple pad)
#                      MIB_R0C{col}_PIOT0_PADDOB_PIO      (PIO B, simple pad)
#                      MIB_R0C{col}_PIOT0_JTXDATA0A_SIOLOGIC   (DDR gearbox A)
#                      MIB_R0C{col}_PIOT0_JTXDATA0B_SIOLOGIC   (DDR gearbox B)
#   row 2, col 0 (left edge, row 2):
#                      MIB_R2C0_PICL0_JTXDATA0C_IOLOGIC
#                      MIB_R2C0_PICL0_JTXDATA4C_IOLOGIC
#                      MIB_R2C0_PICL0_JTXDATA0D_IOLOGIC
#                      MIB_R2C0_PICL0_JTXDATA4D_IOLOGIC
# We generate several candidate names and keep whichever one appears
# in the assign dict.

def candidate_output_wires(row, col, pio):
    if row == 0:
        tile = f"MIB_R0C{col}_PIOT0"
        letter = pio  # A or B
        return [
            f"{tile}_PADDO{letter}_PIO",
            f"{tile}_JTXDATA0{letter}_SIOLOGIC",
            f"{tile}_JTXDATA4{letter}_SIOLOGIC",
        ]
    elif col == 0:
        tile = f"MIB_R{row}C0_PICL0"
        return [
            f"{tile}_JTXDATA0{pio}_IOLOGIC",
            f"{tile}_JTXDATA4{pio}_IOLOGIC",
            f"{tile}_PADDO{pio}_PIO",
        ]
    elif col == 72:  # right edge
        tile = f"MIB_R{row}C72_PICR0"
        return [
            f"{tile}_JTXDATA0{pio}_IOLOGIC",
            f"{tile}_JTXDATA4{pio}_IOLOGIC",
            f"{tile}_PADDO{pio}_PIO",
        ]
    return []

# ---------------------------------------------------------------------------
# 3.  Parse the netlist
# ---------------------------------------------------------------------------
print("Parsing assigns …")
SINGLE_TOKEN = re.compile(r"^[\\A-Za-z0-9_.]+$")
assigns = {}
with SRC.open() as f:
    pat = re.compile(r"^assign\s+([^=\s]+)\s*=\s*([^;]+);")
    for line in f:
        m = pat.match(line)
        if m:
            assigns[m.group(1).strip()] = m.group(2).strip()
print(f"  {len(assigns)} assigns loaded")

def resolve_chain(name, max_steps=512):
    """Follow assign chain to terminal (non-single-token or unknown)."""
    seen = {name}
    cur = name
    for _ in range(max_steps):
        rhs = assigns.get(cur)
        if rhs is None:
            return cur, "root"
        if SINGLE_TOKEN.match(rhs):
            if rhs in seen:
                return rhs, "cycle"
            seen.add(rhs)
            cur = rhs
        else:
            return rhs, "expr"  # expression – return RHS, not LHS
    return cur, "depth"


print("Parsing tiles …")
tiles = {}
init_pat    = re.compile(r"\.SLICE([ABCD])_LUT([01])_INITVAL\(16'b([01]+)\)")
mode_pat    = re.compile(r"\.SLICE([ABCD])_MODE\(\"([^\"]+)\"\)")
regset_pat  = re.compile(r"\.SLICE([ABCD])_REG([01])_REGSET\(\"([^\"]+)\"\)")
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
        inits = {(s, k): v for s, k, v in init_pat.findall(line)}
        modes = dict(mode_pat.findall(line))
        body  = line[line.index(f"{key}_PLC2_inst"):]
        ports = dict(port_pat.findall(body))
        tiles[key] = {"inits": inits, "modes": modes, "ports": ports}

print(f"  {len(tiles)} tiles loaded")

# ---------------------------------------------------------------------------
# 4.  Trace each LED back to its driving LUT(s)
# ---------------------------------------------------------------------------
SLICE_INPUTS = {
    "A": {0: ("A0","B0","C0","D0"), 1: ("A1","B1","C1","D1")},
    "B": {0: ("A2","B2","C2","D2"), 1: ("A3","B3","C3","D3")},
    "C": {0: ("A4","B4","C4","D4"), 1: ("A5","B5","C5","D5")},
    "D": {0: ("A6","B6","C6","D6"), 1: ("A7","B7","C7","D7")},
}
F_IDX_TO_SLICE = {0:("A",0),1:("A",1),2:("B",0),3:("B",1),
                   4:("C",0),5:("C",1),6:("D",0),7:("D",1)}
Q_IDX_TO_SLICE = F_IDX_TO_SLICE  # same mapping

SLICE_FX_RE   = re.compile(r"^(R\d+C\d+)_PLC2_F5([ABCD])_SLICE$")
SLICE_F_RE    = re.compile(r"^(R\d+C\d+)_PLC2_F(\d)_SLICE$")
SLICE_Q_RE    = re.compile(r"^(R\d+C\d+)_PLC2_Q(\d)_SLICE$")
SLICE_FXY_RE  = re.compile(r"^(R\d+C\d+)_PLC2_FX([ABCD])_SLICE$")


def get_lut_inputs(tile_key, sl, lut_idx):
    td = tiles[tile_key]
    result = []
    for port in SLICE_INPUTS[sl][lut_idx]:
        wire = td["ports"].get(f"{port}_SLICE")
        if wire is None:
            result.append((port, None, None))
        else:
            resolved, why = resolve_chain(wire)
            result.append((port, wire, resolved))
    return result


def get_lut_init(tile_key, sl, lut_idx):
    return tiles[tile_key]["inits"].get((sl, str(lut_idx)), "0" * 16)


def analyse_terminal(resolved):
    """
    Given the terminal resolved wire, return a description dict.
    Returns a list of LUT dicts (one for LUT4, two for PFUMX/OFX0).
    Each LUT dict: {tile, slice, lut, init, inputs}
    """
    luts = []
    m = SLICE_FX_RE.match(resolved)
    if m:
        tk, sl = m.group(1), m.group(2)
        for li in (0, 1):
            luts.append({
                "kind": "PFUMX/OFX0",
                "tile": tk, "slice": sl, "lut": li,
                "init": get_lut_init(tk, sl, li),
                "inputs": get_lut_inputs(tk, sl, li),
            })
        # PFUMX select input = M{base} of the slice
        sl_to_base = {"A":0,"B":2,"C":4,"D":6}
        m_wire = tiles[tk]["ports"].get(f"M{sl_to_base[sl]}_SLICE")
        sel_res, _ = resolve_chain(m_wire) if m_wire else (None, None)
        luts.append({"kind": "PFUMX_SEL", "wire": m_wire, "resolved": sel_res})
        return luts
    m = SLICE_F_RE.match(resolved)
    if m:
        tk = m.group(1)
        sl, li = F_IDX_TO_SLICE[int(m.group(2))]
        luts.append({
            "kind": "LUT4",
            "tile": tk, "slice": sl, "lut": li,
            "init": get_lut_init(tk, sl, li),
            "inputs": get_lut_inputs(tk, sl, li),
        })
        return luts
    # FF output: chase the M input
    m = SLICE_Q_RE.match(resolved)
    if m:
        tk = m.group(1)
        sl, ri = Q_IDX_TO_SLICE[int(m.group(2))]
        sl_to_base = {"A":0,"B":2,"C":4,"D":6}
        m_port = f"M{sl_to_base[sl] + ri}_SLICE"
        m_wire = tiles[tk]["ports"].get(m_port)
        if m_wire:
            m_res, _ = resolve_chain(m_wire)
            deeper = analyse_terminal(m_res)
            luts.append({"kind": "FF_M", "tile": tk, "slice": sl, "reg": ri,
                         "m_wire": m_wire, "m_resolved": m_res})
            luts.extend(deeper)
        return luts
    return [{"kind": "unknown", "resolved": resolved}]


print("\n=== Tracing LED outputs ===\n")
led_data = []
for ball, led_ref in LED_BALLS:
    row, col, pio = BALL_TO_PIO[ball]
    candidates = candidate_output_wires(row, col, pio)
    pad_wire = None
    for cand in candidates:
        if cand in assigns:
            pad_wire = cand
            break
    print(f"{led_ref} ({ball})  row={row} col={col} pio={pio}")
    if pad_wire is None:
        print(f"  !! no pad wire found (tried: {candidates})")
        led_data.append({"led": led_ref, "ball": ball, "luts": []})
        continue
    terminal, why = resolve_chain(pad_wire)
    print(f"  pad_wire = {pad_wire}")
    print(f"  terminal = {terminal}  ({why})")
    lut_chain = analyse_terminal(terminal)
    for item in lut_chain:
        if item["kind"] in ("LUT4", "PFUMX/OFX0"):
            print(f"  [{item['kind']}] {item['tile']}.slice{item['slice']}.LUT{item['lut']}  INIT={item['init']}")
            for p, w, r in item["inputs"]:
                print(f"    {p}: -> {r}")
        elif item["kind"] == "PFUMX_SEL":
            print(f"  [PFUMX_SEL] {item['resolved']}")
        elif item["kind"] == "FF_M":
            print(f"  [FF] {item['tile']}.slice{item['slice']} reg{item['reg']}  M->{item['m_resolved']}")
        else:
            print(f"  [?] {item}")
    led_data.append({"led": led_ref, "ball": ball, "pad_wire": pad_wire,
                      "terminal": terminal, "luts": lut_chain})
    print()

# ---------------------------------------------------------------------------
# 5.  Identify address lines (signals common to multiple LED ROM LUTs)
# ---------------------------------------------------------------------------
print("\n=== Address line candidates ===")
all_inputs = {}
for ld in led_data:
    for item in ld["luts"]:
        if "inputs" not in item:
            continue
        for p, w, r in item["inputs"]:
            all_inputs[r] = all_inputs.get(r, 0) + 1

for sig, cnt in sorted(all_inputs.items(), key=lambda x: -x[1]):
    if cnt >= 4:
        print(f"  {sig}  (used by {cnt} LUT inputs)")

# ---------------------------------------------------------------------------
# 6.  Evaluate the ROM for each bit across all 32 addresses
# ---------------------------------------------------------------------------
# The address bus is 5 bits wide: addr[4] = PFUMX select (M port),
# addr[3:0] = the 4 LUT4 data inputs.
# All ROM LUTs use the same 5 address signals (confirmed by the common inputs).
# We need to order them addr[4..0] and assign them names.

# We'll let the script auto-detect the 5 most-shared signals.
top_sigs = [s for s, c in sorted(all_inputs.items(), key=lambda x: -x[1]) if c >= 4]
print(f"\nTop shared signals ({len(top_sigs)}): {top_sigs}")


def lut4_eval(init_str: str, a: int, b: int, c: int, d: int) -> int:
    """Evaluate a 16-bit LUT4.
    The ECP5 decompiler stores INITVAL as a 16-char bit string where
    bit[0] is the LSB (input combo 0b0000) and bit[15] is the MSB.
    The string is written MSB-first, so bit index = 15 - position_in_string.
    """
    idx = a | (b << 1) | (c << 2) | (d << 3)
    bit_pos = 15 - idx   # string position for this address
    return int(init_str[bit_pos])


def pfumx_eval(init0: str, init1: str, sel: int,
               a: int, b: int, c: int, d: int) -> int:
    """OFX0 = PFUMX(LUT1_out, LUT0_out, M/sel).
    When sel=0 -> LUT0 result; sel=1 -> LUT1 result."""
    r0 = lut4_eval(init0, a, b, c, d)
    r1 = lut4_eval(init1, a, b, c, d)
    return r1 if sel else r0


# Collect per-bit ROM info
bit_roms = {}
for ld in led_data:
    luts = ld["luts"]
    if not luts:
        continue
    # Separate FF wrappers from LUT entries
    pfumx_pair = [x for x in luts if x["kind"] == "PFUMX/OFX0"]
    lut4_only  = [x for x in luts if x["kind"] == "LUT4"]
    pfumx_sel  = next((x for x in luts if x["kind"] == "PFUMX_SEL"), None)

    if pfumx_pair:
        bit_roms[ld["led"]] = {
            "type": "PFUMX",
            "lut0": pfumx_pair[0],
            "lut1": pfumx_pair[1],
            "sel": pfumx_sel,
        }
    elif lut4_only:
        bit_roms[ld["led"]] = {
            "type": "LUT4",
            "lut0": lut4_only[0],
        }

# Build a common address map if we have 5 signals
if len(top_sigs) >= 5:
    addr_sigs = top_sigs[:5]
    print(f"\nAddress signals (5): {addr_sigs}")

    def get_input_order(lut_entry):
        """Return the order of the 4 LUT inputs relative to addr_sigs[0:4]."""
        order = []
        for p, w, r in lut_entry["inputs"]:
            if r in addr_sigs:
                order.append(addr_sigs.index(r))
            else:
                order.append(None)
        return order

    print("\n=== ROM table (per address 0-31) ===")
    print(f"{'addr':>6}  {'bits D8..D1':16}  char  byte")
    print("-" * 50)
    rom = {}
    for addr in range(32):
        bits5 = [(addr >> i) & 1 for i in range(5)]  # bits5[0]=addr[0] .. [4]=addr[4]
        byte_val = 0
        bit_str = ""
        for bit_idx, led_ref in enumerate(["D1","D2","D3","D4","D5","D6","D7","D8"]):
            entry = bit_roms.get(led_ref)
            if entry is None:
                bit_str += "?"
                continue
            if entry["type"] == "PFUMX":
                lut0e = entry["lut0"]
                lut1e = entry["lut1"]
                sel_e = entry["sel"]
                sel_resolved = sel_e["resolved"] if sel_e else None
                sel_bit = bits5[addr_sigs.index(sel_resolved)] if sel_resolved in addr_sigs else 0
                # Map each LUT input to address bit
                inp_bits = []
                for p, w, r in lut0e["inputs"]:
                    if r in addr_sigs:
                        inp_bits.append(bits5[addr_sigs.index(r)])
                    else:
                        inp_bits.append(0)
                while len(inp_bits) < 4:
                    inp_bits.append(0)
                # Use same input ordering for lut1 (they share the same inputs)
                out_bit = pfumx_eval(lut0e["init"], lut1e["init"], sel_bit,
                                     inp_bits[0], inp_bits[1], inp_bits[2], inp_bits[3])
            elif entry["type"] == "LUT4":
                lut_e = entry["lut0"]
                inp_bits = []
                for p, w, r in lut_e["inputs"]:
                    if r in addr_sigs:
                        inp_bits.append(bits5[addr_sigs.index(r)])
                    else:
                        inp_bits.append(0)
                while len(inp_bits) < 4:
                    inp_bits.append(0)
                out_bit = lut4_eval(lut_e["init"], inp_bits[0], inp_bits[1],
                                    inp_bits[2], inp_bits[3])
            else:
                out_bit = 0
                bit_str += "?"
                continue
            byte_val |= (out_bit << bit_idx)
            bit_str += str(out_bit)
        rom[addr] = byte_val
        ch = chr(byte_val) if 32 <= byte_val <= 126 else "."
        print(f"  {addr:4d}   {bit_str:16s}  '{ch}'  0x{byte_val:02X}")
    print()

    # Check: does any permutation of the 5 address lines produce a printable flag?
    # The flag bytes are rotated before display:
    #   displayed[counter] = rotl8(flag[counter], counter % 8)
    # So to recover: flag[counter] = rotr8(rom[counter], counter % 8)
    def rotr8(x, n):
        n %= 8
        if n == 0:
            return x & 0xFF
        return ((x >> n) | (x << (8 - n))) & 0xFF

    print("=== Attempting flag recovery (de-rotating) ===")
    flag_bytes = [rotr8(rom[i], i % 8) for i in range(32)]
    flag_str = "".join(chr(b) if 32 <= b <= 126 else "." for b in flag_bytes)
    print(f"  flag (all 32): {flag_str}")

    # Find the printable window
    printable_run = ""
    for b in flag_bytes:
        ch = chr(b) if 32 <= b <= 126 else None
        if ch:
            printable_run += ch
        else:
            if printable_run:
                print(f"  printable run: {printable_run!r}")
            printable_run = ""
    if printable_run:
        print(f"  printable run: {printable_run!r}")
else:
    print("Need to identify 5 address signals manually.")

(ROOT / "analysis" / "rom_walk_leds.json").write_text(
    json.dumps({ld["led"]: {
        "ball": ld["ball"],
        "pad_wire": ld.get("pad_wire"),
        "terminal": ld.get("terminal"),
    } for ld in led_data}, indent=2)
)
print("\nDone.")
