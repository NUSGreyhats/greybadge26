#!/usr/bin/env python3
"""Replay the secure_memory race exploit in software.

`regular_synchronous_memory` is a 32x8 ROM clocked at 10-15 Hz.
The outer wrapper guards it with the combinational mask

    pmod_j2 = (mem_address == 5'd31) ? mem_value : "?";

`mem_value` is registered (1 clock latency) while the comparator uses the
CURRENT address.  This means:

    cycle t   : set address = i, mem_value still holds mem[i-1]
    cycle t+1 : mem_value updates to mem[i]; comparator looks at the new
                address - if we have already flipped it to 31, the gate
                opens and pmod_j2 leaks mem[i].

We replay both ROMs (slow secure_memory and fast secure_memory) from the
elaborated Verilog source.
"""

SECURE_MEMORY = {
    0: "g", 1: "r", 2: "e", 3: "y", 4: "{",
    5: "r", 6: "a", 7: "c", 8: "e", 9: "_",
    10: "f", 11: "l", 12: "a", 13: "g", 14: "}",
    31: "L",
}

FAST_SECURE_MEMORY = {
    0: "f", 1: "u", 2: "n", 3: "{", 4: "s",
    5: "p", 6: "e", 7: "e", 8: "d", 9: "s",
    10: "t", 11: "e", 12: "r", 13: "r", 14: "}",
    31: "L",
}


def simulate_race(rom: dict) -> str:
    """Walk addresses 0..31, applying the trick of switching to address 31
    one clock cycle after each target read."""
    out = []
    # Naive read (what a polite client sees): always "?" except at addr 31
    naive = "".join(rom.get(i, "\x00") if i == 31 else "?" for i in range(32))
    # Race read: set address to i, let the registered mem_value latch mem[i],
    # then change address to 31 so the comparator opens.
    race = "".join(rom.get(i, "\x00") for i in range(32))
    out.append(("naive", naive))
    out.append(("race", race))
    return out


def show(title, rom):
    print("=" * 60)
    print(title)
    print("=" * 60)
    for tag, s in simulate_race(rom):
        printable = "".join(c if c.isprintable() else "." for c in s)
        print(f"  {tag:6s}: {printable}")
    flag = "".join(rom.get(i, "") for i in range(32) if rom.get(i, "") not in ("", "L"))
    print(f"  flag : {flag}")


show("secure_memory (slow, 15 Hz)", SECURE_MEMORY)
show("fast_secure_memory", FAST_SECURE_MEMORY)
