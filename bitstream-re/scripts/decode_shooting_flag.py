#!/usr/bin/env python3
"""Simulate the shooting_flags challenge in software to recover the flag.

The bitstream's `shooting_flags` module displays
    LED[7:0] = rotl(flag[counter_display], counter_display % 8)
once per clk_wayang tick (~2 Hz) while got_commanding_officer = 1.

We extracted the 25-byte `flag[]` array from
greymechaarmy_v2/firmware/challs/secure_memory_fast/bitstream/generate_shooting_flag.py
and replay it here to show:
  1) the raw byte sequence the FPGA emits to the 8 LEDs
  2) the recovered ASCII flag after de-rotating
"""

FLAG = bytes(
    [
        103, 114, 101, 121, 123,
        101, 104, 95, 100, 111,
        110, 116, 95, 111, 110,
        108, 121, 95, 119, 97,
        121, 97, 110, 103, 125,
    ]
)

def rotl8(x: int, n: int) -> int:
    n %= 8
    return ((x << n) | (x >> (8 - n))) & 0xFF if n else x & 0xFF

displayed = []
for i, b in enumerate(FLAG):
    displayed.append(rotl8(b, i % 8))

print("Frame  ASCII  flag[i]  shift  LEDs(D8..D1)  hex")
print("-" * 60)
for i, (orig, leds) in enumerate(zip(FLAG, displayed)):
    bits = format(leds, "08b")
    print(f"  {i:3d}    '{chr(orig)}'    {orig:3d}     {i%8}     {bits}      0x{leds:02X}")

print()
print("Reconstructed flag:")
print("  " + "".join(chr(b) for b in FLAG))
