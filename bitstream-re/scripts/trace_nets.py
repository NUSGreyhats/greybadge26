#!/usr/bin/env python3
"""
Trace the FPGA-connected PCB nets back to all footprints/pads using them.

For each net that touches a U8 (ECP5) ball, list the *other* endpoints
(footprint ref, pad, footprint value).

Outputs: bitstream-re/analysis/net_endpoints.csv
"""

import csv
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PCB = ROOT.parent / "greymechaarmy_v2" / "hardware" / "greybadge_pcb" / "greybadge_pcb.kicad_pcb"
PINMAP = ROOT / "analysis" / "fpga_pinmap.csv"
OUT = ROOT / "analysis" / "net_endpoints.csv"


def split_footprints(text):
    """Yield (start, end) ranges for each top-level `(footprint ...)` block."""
    fp_re = re.compile(r"\n\t\(footprint ")
    starts = [m.start() + 1 for m in fp_re.finditer(text)]  # skip leading newline
    starts.append(len(text))
    blocks = []
    for i in range(len(starts) - 1):
        # Find matching paren close for this footprint
        start = starts[i]
        depth = 0
        j = start
        while j < starts[i + 1] + 50000:
            ch = text[j] if j < len(text) else ""
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    blocks.append((start, j + 1))
                    break
            j += 1
    return blocks


def parse_footprint(text, start, end):
    block = text[start:end]
    # Reference
    ref_m = re.search(r'\(property "Reference" "([^"]+)"', block)
    val_m = re.search(r'\(property "Value" "([^"]+)"', block)
    ref = ref_m.group(1) if ref_m else "?"
    value = val_m.group(1) if val_m else "?"
    # Pads with their nets
    pads = []
    pad_starts = [
        (m.start(), m.group(1))
        for m in re.finditer(r'\(pad "([^"]+)"', block)
    ]
    pad_starts.append((len(block), None))
    for i in range(len(pad_starts) - 1):
        ps, pad_num = pad_starts[i]
        pe, _ = pad_starts[i + 1]
        seg = block[ps:pe]
        nm = re.search(r'\(net\s+\d+\s+"([^"]+)"\)', seg)
        if nm:
            pads.append((pad_num, nm.group(1)))
    return ref, value, pads


def main():
    text = PCB.read_text(encoding="utf-8", errors="replace")
    blocks = split_footprints(text)
    print(f"Found {len(blocks)} footprints", flush=True)

    net_to_endpoints = defaultdict(list)  # net -> list of (ref, value, pad)
    for s, e in blocks:
        ref, value, pads = parse_footprint(text, s, e)
        for pad, net in pads:
            net_to_endpoints[net].append((ref, value, pad))

    # Read FPGA pinmap to know which nets to report.
    fpga_nets = []
    with PINMAP.open(newline="") as f:
        for r in csv.DictReader(f):
            fpga_nets.append((r["ball"], r["pcb_net"]))

    rows = []
    for ball, net in fpga_nets:
        endpoints = net_to_endpoints.get(net, [])
        # filter U8 itself
        others = [(r, v, p) for (r, v, p) in endpoints if r != "U8"]
        for r, v, p in others:
            rows.append(
                {
                    "fpga_ball": ball,
                    "net": net,
                    "other_ref": r,
                    "other_value": v,
                    "other_pad": p,
                }
            )
        if not others:
            rows.append(
                {
                    "fpga_ball": ball,
                    "net": net,
                    "other_ref": "",
                    "other_value": "",
                    "other_pad": "",
                }
            )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "fpga_ball",
                "net",
                "other_ref",
                "other_value",
                "other_pad",
            ],
        )
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"Wrote {OUT}")

    # Print balls from active set
    active = {
        "A2", "A3", "A5", "A7", "A9", "A11", "A13", "B9", "B10", "B11",
        "B12", "B13", "B14", "C4", "C5", "C6", "C7", "C8",
        "D9", "D10", "D11", "D12", "D13", "E4", "E5", "E6", "E7", "E8",
    }
    print()
    print(
        f"{'BALL':5} {'NET':<35} {'OTHER':<10} {'VAL':<35} {'PAD':<8}"
    )
    for r in rows:
        if r["fpga_ball"] in active:
            print(
                f"{r['fpga_ball']:5} {r['net'][:35]:<35} {r['other_ref'][:10]:<10} "
                f"{r['other_value'][:35]:<35} {r['other_pad']:<8}"
            )


if __name__ == "__main__":
    main()
