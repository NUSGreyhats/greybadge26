#!/usr/bin/env python3
"""Parse ecpunpack main.config for IO pins, tile utilization, and EBR init."""

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "main.config"
ANALYSIS = ROOT / "analysis"


def parse_config(path: Path):
    tiles = []
    current = None
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith(".device"):
                device = line.split(maxsplit=1)[1]
                continue
            if line.startswith(".comment"):
                continue
            m = re.match(r"^\.tile ([^:]+):(\S+)$", line)
            if m:
                if current:
                    tiles.append(current)
                current = {
                    "name": m.group(1),
                    "type": m.group(2),
                    "lines": [],
                }
                continue
            if current is not None:
                current["lines"].append(line)
        if current:
            tiles.append(current)
    return device if "device" in dir() else "unknown", tiles


def tile_coords(name: str):
    m = re.match(r"([A-Z0-9_]+)_R(\d+)C(\d+)$", name)
    if not m:
        return None
    return int(m.group(2)), int(m.group(3)), m.group(1)


def parse_pio_tile(tile):
    """Extract IO site info from a PIO tile block."""
    site = None
    direction = None
    io_type = None
    comp = None
    nets = []
    for line in tile["lines"]:
        if line.startswith("comp "):
            comp = line.split(maxsplit=1)[1]
        elif line.startswith("site "):
            site = line.split(maxsplit=1)[1]
        elif line.startswith("enum "):
            parts = line.split()
            if len(parts) >= 3:
                key, val = parts[1], parts[2]
                if key == "PIO_DIRECTION":
                    direction = val
                elif key == "PIO_IO_TYPE":
                    io_type = val
        elif line.startswith("arc:"):
            nets.append(line.split(":", 1)[1].strip())
    return {
        "tile": tile["name"],
        "site": site or comp or tile["name"],
        "direction": direction or "unknown",
        "io_type": io_type or "unknown",
        "nets": ";".join(nets),
    }


def parse_ebr_tile(tile):
    """Extract EBR/DP16KD init data if present."""
    inits = []
    for line in tile["lines"]:
        if line.startswith("enum INIT"):
            parts = line.split()
            if len(parts) >= 3:
                inits.append(parts[2])
        elif line.startswith("enum ") and "INIT" in line:
            parts = line.split()
            if len(parts) >= 3:
                inits.append(f"{parts[1]}={parts[2]}")
    return inits


def is_programmed(tile):
    """Tile has non-routing-only config."""
    for line in tile["lines"]:
        if line.startswith(("enum ", "comp ", "site ", "param ")):
            return True
        if line.startswith("arc:"):
            # routing-only tiles still count as used if they have arcs
            pass
    return bool(tile["lines"])


def main():
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    device, tiles = parse_config(CONFIG)

    type_counts = Counter(t["type"] for t in tiles)
    programmed_by_type = Counter(
        t["type"] for t in tiles if is_programmed(t)
    )

    # IO pins
    io_pins = []
    for t in tiles:
        if t["type"] in ("PIO", "PIO3", "IOLOGIC"):
            io_pins.append(parse_pio_tile(t))
        elif "PIO" in t["type"]:
            io_pins.append(parse_pio_tile(t))

    # EBR init
    ebr_data = {}
    for t in tiles:
        if t["type"] in ("EBR", "DP16KD", "EBR_CORE"):
            inits = parse_ebr_tile(t)
            if inits:
                ebr_data[t["name"]] = inits

    # EBR init from word: entries (block RAM init bits in fabric tiles)
    ebr_words = []
    for t in tiles:
        for line in t["lines"]:
            if line.startswith("word:") and "INIT" in line:
                ebr_words.append(f"{t['name']}: {line}")

    summary = {
        "device": device,
        "total_tiles_in_config": len(tiles),
        "tile_types": dict(type_counts),
        "programmed_tile_types": dict(programmed_by_type),
        "io_pin_count": len(io_pins),
        "ebr_tiles_with_init": len(ebr_data),
        "ebr_init_word_count": len(ebr_words),
        "plc2_tile_count": type_counts.get("PLC2", 0),
        "logic_utilization_pct": round(
            100 * programmed_by_type.get("PLC2", 0) / max(type_counts.get("PLC2", 1), 1),
            1,
        ),
    }

    with (ANALYSIS / "tile_summary.json").open("w") as f:
        json.dump(summary, f, indent=2)

    if ebr_words:
        with (ANALYSIS / "ebr_init.hex").open("w") as f:
            for entry in ebr_words:
                f.write(entry + "\n")

    print(json.dumps(summary, indent=2))
    print(f"Wrote {ANALYSIS / 'tile_summary.json'}")
    if ebr_words:
        print(f"Wrote {ANALYSIS / 'ebr_init.hex'} ({len(ebr_words)} INIT words)")


if __name__ == "__main__":
    main()
