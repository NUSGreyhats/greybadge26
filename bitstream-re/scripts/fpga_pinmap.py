#!/usr/bin/env python3
"""
Extract the ECP5 FPGA (U8) ball-to-net map from the KiCad PCB file, then
join it with the bitstream-derived per-pad IO direction and behavior tables.

Inputs:
  - greybadge_pcb/greybadge_pcb.kicad_pcb (PCB netlist source of truth)
  - bitstream-re/analysis/io_pins.csv     (bitstream IO direction/standard)
  - bitstream-re/analysis/port_map.csv    (decompiler port -> ball)
  - bitstream-re/verilog/pads/INDEX.csv   (per-pad cone size/FFs/clocks)

Outputs:
  - bitstream-re/analysis/fpga_pinmap.csv (ball, net, bitstream_dir, std,
        outputs, cone_units, ff_count, clocks)
  - bitstream-re/analysis/fpga_pinmap.json
"""

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PCB = ROOT.parent / "greymechaarmy_v2" / "hardware" / "greybadge_pcb" / "greybadge_pcb.kicad_pcb"
IO = ROOT / "analysis" / "io_pins.csv"
PORTMAP = ROOT / "analysis" / "port_map.csv"
PADIDX = ROOT / "verilog" / "pads" / "INDEX.csv"
OUT_CSV = ROOT / "analysis" / "fpga_pinmap.csv"
OUT_JSON = ROOT / "analysis" / "fpga_pinmap.json"


def find_u8_footprint(text):
    """Return the substring containing the U8 footprint body."""
    # Locate the BGA-256 footprint declared at "ECP5U_25_CABGA256" / Ref U8.
    # The footprint block is delimited by parentheses; find the matching close.
    fp_re = re.compile(
        r"\(footprint \"Package_BGA:BGA-256[^\"]*\"", re.S
    )
    starts = [m.start() for m in fp_re.finditer(text)]
    for start in starts:
        # Find matching closing paren.
        depth = 0
        i = start
        while i < len(text):
            ch = text[i]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    block = text[start : i + 1]
                    if '"Reference" "U8"' in block:
                        return block
                    break
            i += 1
    raise RuntimeError("U8 footprint not found in PCB")


def parse_pads(block):
    """Yield (pad_number, net_name) pairs for surface pads."""
    pad_re = re.compile(
        r"\(pad \"([A-R]\d+)\" (smd|thru_hole)[^()]*\(at[^)]*\)\s*"
        r".*?\(net\s+\d+\s+\"([^\"]+)\"\)",
        re.S,
    )
    # Simpler: scan for `(pad "X" ...` then find its `(net N "name")` before
    # the next `(pad ` or closing of footprint.
    pad_starts = [
        (m.start(), m.group(1))
        for m in re.finditer(r"\(pad \"([A-R]\d+)\"", block)
    ]
    pad_starts.append((len(block), None))
    pads = []
    for i in range(len(pad_starts) - 1):
        start, ball = pad_starts[i]
        end, _ = pad_starts[i + 1]
        segment = block[start:end]
        m = re.search(r"\(net\s+\d+\s+\"([^\"]+)\"\)", segment)
        net = m.group(1) if m else ""
        pads.append((ball, net))
    return pads


def load_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def main():
    text = PCB.read_text(encoding="utf-8", errors="replace")
    block = find_u8_footprint(text)
    pads = parse_pads(block)
    print(f"Found {len(pads)} pads in U8 (ECP5).")

    io_rows = load_csv(IO)
    portmap_rows = load_csv(PORTMAP)
    pad_idx_rows = load_csv(PADIDX) if PADIDX.exists() else []

    io_by_ball = {r["package_site"]: r for r in io_rows if r.get("package_site")}
    portmap_by_ball = defaultdict(list)
    for r in portmap_rows:
        if r.get("package_site"):
            portmap_by_ball[r["package_site"]].append(r)
    pads_by_ball = defaultdict(list)
    for r in pad_idx_rows:
        pads_by_ball[r["pad"]].append(r)

    rows = []
    for ball, net in pads:
        io = io_by_ball.get(ball, {})
        ports = portmap_by_ball.get(ball, [])
        cones = pads_by_ball.get(ball, [])
        max_units = max((int(c["units"]) for c in cones), default=0)
        total_ffs = sum(int(c["ffs"]) for c in cones)
        clocks = sorted(
            {c["clocks"] for c in cones if c["clocks"]}
        )
        rows.append(
            {
                "ball": ball,
                "pcb_net": net,
                "bs_direction": io.get("direction", ""),
                "bs_io_type": io.get("io_type", ""),
                "bs_extras": io.get("extras", ""),
                "bs_tile": io.get("tile", ""),
                "bs_ports": ";".join(p["decomp_port"] for p in ports),
                "cone_units": max_units,
                "ff_count": total_ffs,
                "clocks": ";".join(clocks),
            }
        )

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "ball",
                "pcb_net",
                "bs_direction",
                "bs_io_type",
                "bs_extras",
                "bs_tile",
                "bs_ports",
                "cone_units",
                "ff_count",
                "clocks",
            ],
        )
        w.writeheader()
        for r in rows:
            w.writerow(r)
    OUT_JSON.write_text(json.dumps(rows, indent=2))

    # Print a quick summary of "active" balls (programmed in bitstream).
    print()
    print("Active (programmed in bitstream) FPGA balls with PCB nets:")
    print(f"{'BALL':5} {'DIR':<7} {'STD':<10} {'NET':<55} {'FFs':>4}")
    for r in rows:
        if r["bs_direction"]:
            print(
                f"{r['ball']:5} {r['bs_direction']:<7} {r['bs_io_type']:<10} "
                f"{r['pcb_net']:<55} {r['ff_count']:>4}"
            )


if __name__ == "__main__":
    main()
