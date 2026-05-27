#!/usr/bin/env python3
"""Strip Yosys `initial begin ... end` blocks that confuse proc."""
import re
from pathlib import Path

SRC = Path("/mnt/c/Users/zunmun/Documents/Stuff/Github/WORK/GreyHats/greybadge26/bitstream-re/verilog/main_behavior.v")
DST = SRC.with_name("main_behavior_noinit.v")

text = SRC.read_text()
pattern = re.compile(r"  initial begin\n(?:    [^\n]*\n)+  end\n")
cleaned, n = pattern.subn("", text)
DST.write_text(cleaned)
print(f"removed {n} initial blocks, wrote {DST} ({len(cleaned)} bytes)")
