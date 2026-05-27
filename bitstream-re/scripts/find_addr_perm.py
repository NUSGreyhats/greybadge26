#!/usr/bin/env python3
"""
Find the correct GP8..GP12 → address bit permutation by brute force.

We know secure_memory stores ['g','r','e','y','{','r','a','c','e','_','f','l','a','g','}']
at consecutive ROM addresses, and bit 7 of each byte is always 0.

For each of the 5! = 120 address-bit permutations, evaluate the 6-bit ROM
output (bits 0..5) for addresses 0..31 and check if the result matches
the expected flag bytes (ignoring bit 6 and bit 7, both TBD).
"""
from itertools import permutations
from pathlib import Path

# Secure memory ROM from rom_walker2.py
# Each entry: (lut0_init, lut1_init, [A0,B0,C0,D0 as GP indices], [A1,B1,C1,D1 as GP indices])
# GP indices: 0=GP8, 1=GP9, 2=GP10, 3=GP11, 4=GP12
# PFUMX select = GP8 (index 0) for all bits

SEC_MEM_ROM = {
    0: {
        "lut0": "0101010100010100",
        "lut1": "0001010000010100",
        "in0": [4, 1, 3, 2],   # GP12, GP9, GP11, GP10
        "in1": [4, 1, 3, -1],  # GP12, GP9, GP11, LOCAL0(=0)
        "sel": 0,              # GP8
    },
    1: {
        "lut0": "0000010000000010",
        "lut1": "0000001100001010",
        "in0": [2, 1, 4, 3],   # GP10, GP9, GP12, GP11
        "in1": [2, 1, 4, 3],
        "sel": 0,
    },
    2: {
        "lut0": "0010001100000010",
        "lut1": "1000000001001100",
        "in0": [1, 4, 2, 3],   # GP9, GP12, GP10, GP11
        "in1": [1, 3, 2, 4],   # GP9, GP11, GP10, GP12
        "sel": 0,
    },
    3: {
        "lut0": "0100000100000000",
        "lut1": "1000000001010100",
        "in0": [4, 3, 1, 2],   # GP12, GP11, GP9, GP10
        "in1": [4, 3, 1, 2],
        "sel": 0,
    },
    4: {
        "lut0": "0100000000000100",
        "lut1": "0000000100010011",
        "in0": [4, 2, 1, 3],   # GP12, GP10, GP9, GP11
        "in1": [2, 4, 1, 3],   # GP10, GP12, GP9, GP11
        "sel": 0,
    },
    5: {
        "lut0": "0100010001000000",
        "lut1": "0001001000000000",
        "in0": [4, 3, 1, 2],   # GP12, GP11, GP9, GP10
        "in1": [2, 4, 1, 3],   # GP10, GP12, GP9, GP11
        "sel": 0,
    },
}

# Expected 6-bit values at addresses 0..14 (bits 0..5 only)
EXPECTED_CHARS = list("grey{race_flag}")
print(f"Expected flag: {''.join(EXPECTED_CHARS)!r}  ({len(EXPECTED_CHARS)} chars)")


def lut4(init_str: str, a: int, b: int, c: int, d: int) -> int:
    idx = a | (b << 1) | (c << 2) | (d << 3)
    return int(init_str[15 - idx])


def eval_rom_bit(bit_info: dict, gp_vals: list) -> int:
    """gp_vals[i] is the value of GP(8+i) for i in 0..4."""
    sel = gp_vals[bit_info["sel"]]
    if sel == 0:
        init = bit_info["lut0"]
        ins  = bit_info["in0"]
    else:
        init = bit_info["lut1"]
        ins  = bit_info["in1"]
    def gv(idx):
        return gp_vals[idx] if idx >= 0 else 0
    a = gv(ins[0]); b = gv(ins[1]); c = gv(ins[2]); d = gv(ins[3])
    return lut4(init, a, b, c, d)


def eval_byte(gp_vals: list) -> int:
    byte_val = 0
    for b in range(6):
        v = eval_rom_bit(SEC_MEM_ROM[b], gp_vals)
        byte_val |= v << b
    return byte_val


# The addr→GP mapping: for ROM address n, what GP values do we set?
# gp_vals[i] = (n >> perm[i]) & 1   where perm[i] maps addr bit positions to GP indices

def addr_to_gp(addr: int, perm: tuple) -> list:
    """perm[i] = which addr bit drives GP8+i.
    So gp_vals[i] = (addr >> perm[i]) & 1."""
    return [(addr >> perm[i]) & 1 for i in range(5)]


print("\nSearching all 5! permutations …")
best = []
for perm in permutations(range(5)):
    # perm[i] = which ROM address bit is gated by GP8+i
    # evaluate first 15 addresses
    matches = 0
    for rom_addr, expected_ch in enumerate(EXPECTED_CHARS):
        gp_vals = addr_to_gp(rom_addr, perm)
        byte_val = eval_byte(gp_vals)
        # mask to 6 bits and compare with expected (also masked)
        expected_6bit = ord(expected_ch) & 0x3F
        if byte_val == expected_6bit:
            matches += 1
    if matches >= 12:
        best.append((matches, perm))

best.sort(reverse=True)
print(f"Top permutations (≥12 matches):")
for matches, perm in best[:10]:
    print(f"  matches={matches}/15  perm={perm}  "
          f"(GP8→addr[{perm[0]}], GP9→addr[{perm[1]}], GP10→addr[{perm[2]}], "
          f"GP11→addr[{perm[3]}], GP12→addr[{perm[4]}])")

if not best:
    print("  None found with ≥12 matches. Trying ≥8 …")
    for perm in permutations(range(5)):
        matches = 0
        for rom_addr, expected_ch in enumerate(EXPECTED_CHARS):
            gp_vals = addr_to_gp(rom_addr, perm)
            byte_val = eval_byte(gp_vals)
            expected_6bit = ord(expected_ch) & 0x3F
            if byte_val == expected_6bit:
                matches += 1
        if matches >= 8:
            best.append((matches, perm))
    best.sort(reverse=True)
    for matches, perm in best[:10]:
        print(f"  matches={matches}/15  perm={perm}")

# If the best permutation found, print the full ROM
if best:
    best_perm = best[0][1]
    print(f"\nBest permutation: {best_perm}")
    print("Full ROM (all 32 addresses):")
    for rom_addr in range(32):
        gp_vals = addr_to_gp(rom_addr, best_perm)
        byte6 = eval_byte(gp_vals)
        ch = chr(byte6) if 32 <= byte6 <= 126 else f"[{byte6}]"
        print(f"  addr {rom_addr:2d}  GPs={gp_vals}  6-bit=0x{byte6:02X}  '{ch}'")
