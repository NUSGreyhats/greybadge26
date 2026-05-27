#!/usr/bin/env python3
"""
Remove duplicate `wire X;` declarations whose name is already a top-level
port of the decompiled module. Icarus rejects the redeclaration.

Read in main_decomp.v, find the port list (between `module top (` and `);`),
then strip standalone `wire NAME;` lines whose NAME is in that set.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "sim" / "main_decomp.v"
DST = ROOT / "sim" / "main_decomp_patched.v"


def main():
    text = SRC.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"module\s+top\s*\(([^)]*)\)\s*;", text, re.DOTALL)
    if not m:
        sys.exit("port list not found")
    port_text = m.group(1)
    ports = set()
    for line in port_text.splitlines():
        line = line.strip().rstrip(",")
        # strip direction keyword
        tokens = line.split()
        if not tokens:
            continue
        if tokens[0] in ("input", "output", "inout"):
            tokens = tokens[1:]
        if tokens:
            ports.add(tokens[-1])
    print(f"found {len(ports)} ports")

    out_lines = []
    pat = re.compile(r"^\s*wire\s+([A-Za-z_][A-Za-z0-9_]*)\s*;\s*$")
    removed = 0
    for line in text.splitlines():
        m = pat.match(line)
        if m and m.group(1) in ports:
            removed += 1
            continue
        out_lines.append(line)
    print(f"removed {removed} duplicate wire decls")
    DST.write_text("\n".join(out_lines) + "\n")
    print(f"wrote {DST} ({DST.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
