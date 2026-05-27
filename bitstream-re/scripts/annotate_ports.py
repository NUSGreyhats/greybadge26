#!/usr/bin/env python3
"""Map decompiler top-level ports to CABGA256 package ball names."""

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IO_CSV = ROOT / "analysis" / "io_pins.csv"
DECOMP = ROOT / "verilog" / "main_decomp.v"
OUT_MAP = ROOT / "analysis" / "port_map.csv"
OUT_JSON = ROOT / "analysis" / "port_map.json"
OUT_V = ROOT / "verilog" / "main_top_annotated.v"


def load_io_lookup():
    # tile + pio side -> package site
    by_tile = {}
    with IO_CSV.open(newline="") as f:
        for row in csv.DictReader(f):
            by_tile[(row["tile"], row["pio"])] = row
    return by_tile


def infer_tile_pio(port: str):
    m = re.match(r"(MIB_R\d+C\d+)_(PIOT[01]|PICT[01])_(.+)", port)
    if not m:
        return None, None, port
    tile, tt, rest = m.group(1), m.group(2), m.group(3)
    pio = "PIOA" if tt in ("PIOT0", "PICT0") else "PIOB"
    return tile, pio, rest


def parse_top_ports(path: Path):
    text = path.read_text(errors="replace")
    m = re.search(r"module top\s*\((.*?)\);", text, re.DOTALL)
    if not m:
        raise SystemExit("module top not found")
    ports = []
    for line in m.group(1).splitlines():
        line = line.strip().rstrip(",")
        if not line:
            continue
        pm = re.match(r"(input|output)\s+(\S+)", line)
        if pm:
            ports.append({"dir": pm.group(1), "name": pm.group(2)})
    return ports


def main():
    io = load_io_lookup()
    ports = parse_top_ports(DECOMP)
    mapped = []

    for p in ports:
        tile, pio, suffix = infer_tile_pio(p["name"])
        site = ""
        io_type = ""
        if tile and pio:
            row = io.get((tile, pio), {})
            site = row.get("package_site", "")
            io_type = row.get("io_type", "")
        annotated = f"pad_{site}_{suffix}" if site else p["name"]
        mapped.append(
            {
                "decomp_port": p["name"],
                "direction": p["dir"],
                "package_site": site,
                "io_type": io_type,
                "tile": tile or "",
                "pio": pio or "",
                "annotated_name": annotated,
            }
        )

    OUT_MAP.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "annotated_name",
        "direction",
        "package_site",
        "decomp_port",
        "io_type",
        "tile",
        "pio",
    ]
    with OUT_MAP.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in sorted(mapped, key=lambda r: (r["package_site"], r["decomp_port"])):
            w.writerow(row)

    summary = {
        "total_ports": len(mapped),
        "mapped_to_package_site": sum(1 for r in mapped if r["package_site"]),
        "inputs": sum(1 for r in mapped if r["direction"] == "input"),
        "outputs": sum(1 for r in mapped if r["direction"] == "output"),
    }
    OUT_JSON.write_text(json.dumps({"summary": summary, "ports": mapped}, indent=2))

    # Small wrapper documenting renamed IO (references full netlist separately)
    lines = [
        "// IO annotation wrapper for bitstream-only RE of main.bit",
        "// Full gate-level netlist: main_decomp.v (51 MB)",
        "// Yosys-lifted netlist: main_synth.v (194 MB)",
        f"// Mapped {summary['mapped_to_package_site']}/{summary['total_ports']} top ports to package sites",
        "module main_top_annotated(",
    ]
    port_lines = []
    for row in mapped:
        if row["package_site"]:
            port_lines.append(f"  {row['direction']} {row['annotated_name']}")
    lines.append(",\n".join(port_lines))
    lines.append(");")
    lines.append("  // See analysis/port_map.csv for decomp_port <-> pad_* mapping")
    lines.append("endmodule")
    OUT_V.write_text("\n".join(lines) + "\n")

    print(json.dumps(summary, indent=2))
    print(f"Wrote {OUT_MAP}, {OUT_JSON}, {OUT_V}")


if __name__ == "__main__":
    main()
