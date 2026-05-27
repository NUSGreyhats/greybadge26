#!/usr/bin/env python3
"""Map programmed IO using pytrellis + system prjtrellis-db."""

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "main.config"
BIT = ROOT / "main.bit"
ANALYSIS = ROOT / "analysis"
DB = Path("/usr/share/trellis/database")


def parse_piot_tiles(path: Path):
    tiles = {}
    current_name = None
    current_type = None
    lines = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^\.tile ([^:]+):(\S+)$", raw)
        if m:
            if current_name and current_type in ("PIOT0", "PIOT1"):
                tiles[current_name] = {"type": current_type, "lines": lines}
            current_name, current_type = m.group(1), m.group(2)
            lines = []
            continue
        if current_name:
            lines.append(raw)
    if current_name and current_type in ("PIOT0", "PIOT1"):
        tiles[current_name] = {"type": current_type, "lines": lines}
    return tiles


def parse_enum(lines):
    info = {"pad": None, "direction": "unknown", "io_type": "unknown", "clamp": None}
    for line in lines:
        if not line.startswith("enum:"):
            continue
        body = line.split(":", 1)[1].strip()
        parts = body.split()
        if len(parts) < 2:
            continue
        pad = parts[0].split(".")[0]  # PIOA / PIOB
        key = parts[0].split(".", 1)[1] if "." in parts[0] else parts[0]
        val = " ".join(parts[1:])
        info["pad"] = pad
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
    return info


def main():
    try:
        import pytrellis
    except ImportError:
        print("pytrellis not available", file=sys.stderr)
        sys.exit(1)

    pytrellis.load_database(str(DB))
    chip = pytrellis.Chip("LFE5U-25F")
    chip.load_bitstream(str(BIT))

    piot = parse_piot_tiles(CONFIG)
    rows = []

    for tile_name, data in sorted(piot.items()):
        m = re.match(r"MIB_R(\d+)C(\d+)", tile_name)
        if not m:
            continue
        row, col = int(m.group(1)), int(m.group(2))
        pad_side = "A" if data["type"] == "PIOT0" else "B"
        info = parse_enum(data["lines"])

        package_site = ""
        pad_name = f"PIO{pad_side}"
        try:
            io_tile = chip.get_io_tile(row, col)
            site_idx = 0 if pad_side == "A" else 1
            site = io_tile.get_site(pad_name)
            package_site = site.name
            cfg = site.config
            if info["direction"] == "unknown" and cfg:
                for k, v in cfg.items():
                    if "BASE_TYPE" in k:
                        if "INPUT" in v:
                            info["direction"] = "input"
                        elif "OUTPUT" in v:
                            info["direction"] = "output"
                        elif "BIDIR" in v:
                            info["direction"] = "inout"
                        if "_" in v:
                            info["io_type"] = v.split("_", 1)[1]
        except Exception as e:
            package_site = f"ERR:{e}"

        rows.append(
            {
                "tile": tile_name,
                "pad": pad_name,
                "package_site": package_site,
                "direction": info["direction"],
                "io_type": info["io_type"],
                "clamp": info["clamp"] or "",
            }
        )

    ANALYSIS.mkdir(parents=True, exist_ok=True)
    out = ANALYSIS / "io_pins.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["tile", "pad", "package_site", "direction", "io_type", "clamp"],
        )
        w.writeheader()
        for row in rows:
            w.writerow(row)

    programmed = [r for r in rows if r["direction"] != "unknown" or r["io_type"] != "unknown"]
    summary = {
        "total_piot_tiles": len(rows),
        "programmed_io_buffers": len(programmed),
        "inputs": sum(1 for r in rows if r["direction"] == "input"),
        "outputs": sum(1 for r in rows if r["direction"] == "output"),
        "inouts": sum(1 for r in rows if r["direction"] == "inout"),
    }
    with (ANALYSIS / "io_summary.json").open("w") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
