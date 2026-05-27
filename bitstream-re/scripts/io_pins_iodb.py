#!/usr/bin/env python3
"""Map PIOT tiles to CABGA256 package sites using prjtrellis iodb.json."""

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "main.config"
ANALYSIS = ROOT / "analysis"
IODB = Path("/usr/share/trellis/database/ECP5/LFE5U-25F/iodb.json")
PACKAGE = "CABGA256"


def load_site_lookup():
    data = json.loads(IODB.read_text())
    pkgs = data["packages"][PACKAGE]
    # (row, col, pio) -> package ball
    lookup = {}
    for site, info in pkgs.items():
        key = (info["row"], info["col"], info["pio"])
        lookup[key] = site
    return lookup


IO_TILE_TYPES = {"PIOT0", "PIOT1", "PICT0", "PICT1"}


def parse_io_tiles(path: Path):
    tiles = {}
    current_name = None
    current_type = None
    lines = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^\.tile ([^:]+):(\S+)$", raw)
        if m:
            if current_name and current_type in IO_TILE_TYPES:
                tiles[current_name] = {"type": current_type, "lines": lines}
            current_name, current_type = m.group(1), m.group(2)
            lines = []
            continue
        if current_name:
            lines.append(raw)
    if current_name and current_type in IO_TILE_TYPES:
        tiles[current_name] = {"type": current_type, "lines": lines}
    return tiles


def parse_enum(lines):
    info = {"direction": "unknown", "io_type": "unknown", "clamp": "", "extras": []}
    for line in lines:
        if not line.startswith("enum:"):
            continue
        body = line.split(":", 1)[1].strip()
        parts = body.split()
        if len(parts) < 2:
            continue
        key = parts[0].split(".", 1)[-1]
        val = " ".join(parts[1:])
        if key == "BASE_TYPE":
            if val.startswith("INPUT"):
                info["direction"] = "input"
            elif val.startswith("OUTPUT"):
                info["direction"] = "output"
            elif val.startswith("BIDIR"):
                info["direction"] = "inout"
            info["io_type"] = val.split("_", 1)[-1] if "_" in val else val
        elif key == "CLAMP":
            info["clamp"] = val
        else:
            info["extras"].append(f"{key}={val}")
    return info


def main():
    lookup = load_site_lookup()
    piot = parse_io_tiles(CONFIG)
    rows = []

    for tile_name, data in sorted(piot.items()):
        m = re.match(r"MIB_R(\d+)C(\d+)", tile_name)
        if not m:
            continue
        row, col = int(m.group(1)), int(m.group(2))
        pio = "A" if data["type"] in ("PIOT0", "PICT0") else "B"
        info = parse_enum(data["lines"])
        package_site = lookup.get((row, col, pio), "")

        rows.append(
            {
                "tile": tile_name,
                "row": row,
                "col": col,
                "pio": f"PIO{pio}",
                "package_site": package_site,
                "direction": info["direction"],
                "io_type": info["io_type"],
                "clamp": info["clamp"],
                "extras": ";".join(info["extras"]),
            }
        )

    ANALYSIS.mkdir(parents=True, exist_ok=True)
    out = ANALYSIS / "io_pins.csv"
    fields = [
        "package_site",
        "direction",
        "io_type",
        "tile",
        "row",
        "col",
        "pio",
        "clamp",
        "extras",
    ]
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in sorted(rows, key=lambda r: (r["package_site"], r["tile"])):
            w.writerow(row)

    programmed = [
        r
        for r in rows
        if r["direction"] != "unknown"
        or r["clamp"]
        or r["extras"]
    ]
    summary = {
        "package": PACKAGE,
        "total_piot_tiles": len(rows),
        "programmed_io_buffers": len(programmed),
        "inputs": sum(1 for r in rows if r["direction"] == "input"),
        "outputs": sum(1 for r in rows if r["direction"] == "output"),
        "inouts": sum(1 for r in rows if r["direction"] == "inout"),
        "mapped_package_sites": sorted(
            {r["package_site"] for r in programmed if r["package_site"]}
        ),
    }
    with (ANALYSIS / "io_summary.json").open("w") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
