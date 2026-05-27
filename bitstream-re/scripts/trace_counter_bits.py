#!/usr/bin/env python3
"""
Trace the intermediate signals feeding the LED ROM LUTs back to raw
flip-flop outputs (Q-slices) — those are the counter bits.

Interesting intermediate signals found in the LED trace:
  R2C11_PLC2_F0_SLICE  (used by all 8 LED LUTs)
  R2C9_PLC2_F6_SLICE   (used by 5)
  R9C10_PLC2_Q0_SLICE  (FF — already a counter bit)
  R3C12_PLC2_Q1_SLICE  (FF)
  R2C8_PLC2_Q7_SLICE   (FF)
  R2C10_PLC2_Q1_SLICE  (FF)
  MIB_R5C72_PICR0_JDIA etc  (external pad = input from RP2350)

Strategy: recursively expand any F-slice output until we reach only
Q-slices (FFs) or external pads.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "verilog" / "main_decomp.v"

print("Parsing assigns …")
assigns = {}
pat = re.compile(r"^assign\s+([^=\s]+)\s*=\s*([^;]+);")
with SRC.open() as f:
    for line in f:
        m = pat.match(line)
        if m:
            assigns[m.group(1).strip()] = m.group(2).strip()
print(f"  {len(assigns)} assigns")

print("Parsing tiles …")
tiles = {}
init_pat    = re.compile(r"\.SLICE([ABCD])_LUT([01])_INITVAL\(16'b([01]+)\)")
mode_pat    = re.compile(r"\.SLICE([ABCD])_MODE\(\"([^\"]+)\"\)")
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
        body = line[line.index(f"{key}_PLC2_inst"):]
        ports = dict(port_pat.findall(body))
        tiles[key] = {"inits": inits, "modes": modes, "ports": ports}
print(f"  {len(tiles)} tiles")

SINGLE_TOKEN = re.compile(r"^[\\A-Za-z0-9_.]+$")

def resolve_chain(name, max_steps=512):
    seen = {name}
    cur = name
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

F_IDX_TO_SLICE = {0:("A",0),1:("A",1),2:("B",0),3:("B",1),
                   4:("C",0),5:("C",1),6:("D",0),7:("D",1)}
SLICE_INPUTS = {
    "A": {0: ("A0","B0","C0","D0"), 1: ("A1","B1","C1","D1")},
    "B": {0: ("A2","B2","C2","D2"), 1: ("A3","B3","C3","D3")},
    "C": {0: ("A4","B4","C4","D4"), 1: ("A5","B5","C5","D5")},
    "D": {0: ("A6","B6","C6","D6"), 1: ("A7","B7","C7","D7")},
}
SLICE_FX_RE  = re.compile(r"^(R\d+C\d+)_PLC2_F5([ABCD])_SLICE$")
SLICE_F_RE   = re.compile(r"^(R\d+C\d+)_PLC2_F(\d)_SLICE$")
SLICE_Q_RE   = re.compile(r"^(R\d+C\d+)_PLC2_Q(\d)_SLICE$")
SLICE_FXY_RE = re.compile(r"^(R\d+C\d+)_PLC2_FX([ABCD])_SLICE$")
EXTERNAL_RE  = re.compile(r"^(MIB_|CIB_)")


def leaf_type(name):
    if SLICE_Q_RE.match(name):
        return "FF"
    if EXTERNAL_RE.match(name):
        return "PAD"
    return None


def get_lut_inputs(tile_key, sl, lut_idx):
    td = tiles[tile_key]
    result = []
    for port in SLICE_INPUTS[sl][lut_idx]:
        wire = td["ports"].get(f"{port}_SLICE")
        if wire is None:
            result.append(None)
        else:
            result.append(resolve_chain(wire))
    return result


def expand_to_leaves(sig, depth=0, visited=None):
    """Return a set of (leaf_signal, depth) pairs reachable from sig
    by following F-slice outputs through LUT inputs."""
    if visited is None:
        visited = set()
    if sig in visited:
        return set()
    visited.add(sig)
    lt = leaf_type(sig)
    if lt:
        return {(sig, lt)}
    # Check if it's an F-slice output
    m = SLICE_F_RE.match(sig)
    if m:
        tk = m.group(1)
        sl, li = F_IDX_TO_SLICE[int(m.group(2))]
        leaves = set()
        for inp in get_lut_inputs(tk, sl, li):
            if inp is not None:
                leaves |= expand_to_leaves(inp, depth+1, visited)
        return leaves
    m = SLICE_FX_RE.match(sig)
    if m:
        tk, sl = m.group(1), m.group(2)
        leaves = set()
        for li in (0, 1):
            for inp in get_lut_inputs(tk, sl, li):
                if inp is not None:
                    leaves |= expand_to_leaves(inp, depth+1, visited)
        # also expand M-select
        sl_to_base = {"A":0,"B":2,"C":4,"D":6}
        m_wire = tiles[tk]["ports"].get(f"M{sl_to_base[sl]}_SLICE")
        if m_wire:
            m_res = resolve_chain(m_wire)
            leaves |= expand_to_leaves(m_res, depth+1, visited)
        return leaves
    # Unknown – treat as leaf
    return {(sig, "UNKNOWN")}


# Expand the two main intermediate signals
print("\n=== Expanding R2C11_PLC2_F0_SLICE to leaves ===")
leaves_f0 = expand_to_leaves("R2C11_PLC2_F0_SLICE")
for sig, t in sorted(leaves_f0):
    print(f"  [{t}] {sig}")

print("\n=== Expanding R2C9_PLC2_F6_SLICE to leaves ===")
leaves_f6 = expand_to_leaves("R2C9_PLC2_F6_SLICE")
for sig, t in sorted(leaves_f6):
    print(f"  [{t}] {sig}")

print("\n=== Expanding R2C8_PLC2_F5A_SLICE (PFUMX sel for D1) to leaves ===")
leaves_pfumx_sel = expand_to_leaves("R2C8_PLC2_F5A_SLICE")
for sig, t in sorted(leaves_pfumx_sel):
    print(f"  [{t}] {sig}")

# Expand other non-FF LED inputs that weren't clearly counter bits
for sig in ["R3C11_PLC2_F4_SLICE", "R3C11_PLC2_F7_SLICE", "R3C11_PLC2_F2_SLICE",
            "R3C8_PLC2_F6_SLICE", "R2C10_PLC2_F3_SLICE", "R2C8_PLC2_F3_SLICE"]:
    print(f"\n=== Expanding {sig} to leaves ===")
    leaves = expand_to_leaves(sig)
    for s, t in sorted(leaves):
        print(f"  [{t}] {s}")

# Collect all unique FF leaves
all_ff = set()
for sig in [
    "R2C11_PLC2_F0_SLICE",
    "R2C9_PLC2_F6_SLICE",
    "R2C8_PLC2_F5A_SLICE",
    "R3C11_PLC2_F4_SLICE", "R3C11_PLC2_F7_SLICE", "R3C11_PLC2_F2_SLICE",
    "R3C8_PLC2_F6_SLICE", "R2C10_PLC2_F3_SLICE", "R2C8_PLC2_F3_SLICE",
]:
    for s, t in expand_to_leaves(sig):
        if t == "FF":
            all_ff.add(s)

print("\n=== All unique FF leaves (= counter bits?) ===")
for ff in sorted(all_ff):
    print(f"  {ff}")
print(f"\nTotal: {len(all_ff)}")
