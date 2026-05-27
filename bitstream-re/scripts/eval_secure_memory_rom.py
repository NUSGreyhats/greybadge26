#!/usr/bin/env python3
"""
Evaluate the secure_memory ROM directly from bitstream LUT INIT values.

From rom_walker2.py, each mem_value[i] FF's ROM is an OFX0 PFUMX:
  PFUMX select (M) = GP8  (MIB_R0C67_PIOT0_JPADDIB_PIO)
  LUT0/LUT1 inputs  A = GP12 (MIB_R5C72_PICR0_JDIA)
                    B = GP9  (MIB_R2C72_PICR0_JDIB) or GP10
                    C = GP11 (MIB_R5C72_PICR0_JDIB)
                    D = GP10 (MIB_R2C72_PICR0_JDIA) or local wire

The 5-bit ROM address is formed as:
  ROM_addr = GP12 | (GP9<<1) | (GP11<<2) | (GP10<<3) | (GP8<<4)

(This may have a different bit ordering per ROM bit — we collect all
combinations and look for flag patterns.)
"""
from pathlib import Path

# ROM LUT INIT values from rom_walker2.py output
# bit_idx, lut0_init, lut1_init, inputs_lut0, inputs_lut1, m_sel
ROM_BITS = {
    0: {
        "lut0": "0101010100010100",
        "lut1": "0001010000010100",
        "in0": ["GP12","GP9","GP11","GP10"],
        "in1": ["GP12","GP9","GP11","LOCAL0"],  # D1 local wire
        "sel": "GP8",
    },
    1: {
        "lut0": "0000010000000010",
        "lut1": "0000001100001010",
        "in0": ["GP10","GP9","GP12","GP11"],
        "in1": ["GP10","GP9","GP12","GP11"],
        "sel": "GP8",
    },
    2: {
        "lut0": "0010001100000010",
        "lut1": "1000000001001100",
        "in0": ["GP9","GP12","GP10","GP11"],
        "in1": ["GP9","GP11","GP10","GP12"],
        "sel": "GP8",
    },
    3: {
        "lut0": "0100000100000000",
        "lut1": "1000000001010100",
        "in0": ["GP12","GP11","GP9","GP10"],
        "in1": ["GP12","GP11","GP9","GP10"],
        "sel": "GP8",
    },
    4: {
        "lut0": "0100000000000100",
        "lut1": "0000000100010011",
        "in0": ["GP12","GP10","GP9","GP11"],
        "in1": ["GP10","GP12","GP9","GP11"],
        "sel": "GP8",
    },
    5: {
        "lut0": "0100010001000000",
        "lut1": "0001001000000000",
        "in0": ["GP12","GP11","GP9","GP10"],
        "in1": ["GP10","GP12","GP9","GP11"],
        "sel": "GP8",
    },
    # bit 6: R2C54_PLC2_M0 was unresolved (not F5A), skip for now
    # bit 7: constant 0
}


def lut4(init_str: str, a: int, b: int, c: int, d: int) -> int:
    idx = a | (b << 1) | (c << 2) | (d << 3)
    return int(init_str[15 - idx])


def eval_bit(bit_info: dict, addr5: int) -> int:
    """Evaluate one ROM bit given a 5-bit ROM address.
    We need to decide how to map addr5 to GP8..GP12.
    We try all possible mappings and look for flag patterns.
    """
    # GP values from the address
    gp_vals = {
        f"GP{8+i}": (addr5 >> i) & 1
        for i in range(5)
    }
    gp_vals["LOCAL0"] = 0

    sel = gp_vals[bit_info["sel"]]
    if sel == 0:
        init = bit_info["lut0"]
        ins  = bit_info["in0"]
    else:
        init = bit_info["lut1"]
        ins  = bit_info["in1"]
    a = gp_vals.get(ins[0], 0)
    b = gp_vals.get(ins[1], 0)
    c = gp_vals.get(ins[2], 0)
    d = gp_vals.get(ins[3], 0)
    return lut4(init, a, b, c, d)


def permute_addr(addr5: int, perm: list) -> int:
    """Permute 5 bits of addr5 according to perm mapping.
    perm[i] = which bit of original addr5 becomes bit i.
    """
    result = 0
    for i, src in enumerate(perm):
        result |= ((addr5 >> src) & 1) << i
    return result


print("=== Secure Memory ROM evaluation ===")
print()

# Try the straightforward mapping: addr[i] -> GP8+i
print("Direct mapping: addr[0]=GP8, addr[1]=GP9, addr[2]=GP10, addr[3]=GP11, addr[4]=GP12")
for addr in range(32):
    byte_val = 0
    for b in range(6):
        if b not in ROM_BITS:
            continue
        v = eval_bit(ROM_BITS[b], addr)
        byte_val |= v << b
    # bit 6 unknown, bit 7 = 0
    ch = chr(byte_val) if 32 <= byte_val <= 126 else "."
    print(f"  addr {addr:2d}: 0x{byte_val:02X}  '{ch}'")

print()
print("=== Trying bit-reversed address ===")
for addr in range(32):
    # Reverse bit order of 5 bits
    rev_addr = sum(((addr >> i) & 1) << (4 - i) for i in range(5))
    byte_val = 0
    for b in range(6):
        if b not in ROM_BITS:
            continue
        v = eval_bit(ROM_BITS[b], rev_addr)
        byte_val |= v << b
    ch = chr(byte_val) if 32 <= byte_val <= 126 else "."
    print(f"  addr {addr:2d} -> rev_addr {rev_addr:2d}: 0x{byte_val:02X}  '{ch}'")

# The ROM input bit ordering might be:
# addr[4] = GP8 (PFUMX sel), addr[0..3] = LUT inputs in order A,B,C,D
# But A,B,C,D correspond to GP12,GP9,GP11,GP10 (for bit 0)
# So addr = GP12|(GP9<<1)|(GP11<<2)|(GP10<<3)|(GP8<<4)
# which means: GP8=addr[4], GP9=addr[1], GP10=addr[3], GP11=addr[2], GP12=addr[0]
print()
print("=== LUT-natural mapping for bit0 (GP8=addr[4],GP9=addr[1],GP10=addr[3],GP11=addr[2],GP12=addr[0]) ===")
for addr in range(32):
    gp8  = (addr >> 4) & 1  # PFUMX sel
    gp9  = (addr >> 1) & 1
    gp10 = (addr >> 3) & 1
    gp11 = (addr >> 2) & 1
    gp12 = (addr >> 0) & 1

    gp_natural = {
        "GP8": gp8,
        "GP9": gp9,
        "GP10": gp10,
        "GP11": gp11,
        "GP12": gp12,
        "LOCAL0": 0,
    }
    byte_val = 0
    for b in range(6):
        if b not in ROM_BITS:
            continue
        bi = ROM_BITS[b]
        sel = gp_natural[bi["sel"]]
        if sel == 0:
            init = bi["lut0"]; ins = bi["in0"]
        else:
            init = bi["lut1"]; ins = bi["in1"]
        a = gp_natural.get(ins[0], 0)
        b_ = gp_natural.get(ins[1], 0)
        c = gp_natural.get(ins[2], 0)
        d = gp_natural.get(ins[3], 0)
        v = lut4(init, a, b_, c, d)
        byte_val |= v << b
    ch = chr(byte_val) if 32 <= byte_val <= 126 else "."
    print(f"  addr {addr:2d}: 0x{byte_val:02X}  '{ch}'")
