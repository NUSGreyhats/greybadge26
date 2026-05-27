#!/usr/bin/env python3
"""Walk the decompiled netlist back from each pmod_j2 output far enough to
recover the 32-byte ROM behind `secure_memory`.

For every PLC2 tile we collect:
  * the LUT0/LUT1 INIT values for each slice
  * the per-slice MODE
  * the wire connected to every input (A0..A7, B0..B7, C0..C7, D0..D7,
    plus M0..M7, CE/CLK/LSR, FXAA..FXBD)
  * which net is wired to F*/Q*/OFX*.

Then starting at the 8 pmod LUTs we descend through the tile's LUT inputs
and tile-output assigns until we hit either:
  * a Q port (latched FF: we save the FF data input M_b and continue
    descending through M into a different LUT), or
  * an external input (top-level port - that is an address bit from the
    interconnect bus).

The script writes its findings to analysis/rom_walk.json.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "verilog" / "main_decomp.v"
OUT_DIR = ROOT / "analysis"
OUT_DIR.mkdir(exist_ok=True)
OUT = OUT_DIR / "rom_walk.json"


SLICE_LUTS = {
    # F_index : (slice_letter, lut_index, input_bus_id)
    0: ("A", 0, 0),
    1: ("A", 1, 1),
    2: ("B", 0, 2),
    3: ("B", 1, 3),
    4: ("C", 0, 4),
    5: ("C", 1, 5),
    6: ("D", 0, 6),
    7: ("D", 1, 7),
}


def parse_tiles(path: Path) -> dict:
    """Return {tile_key: { 'inits': {(slice,lut): bitstring}, 'modes': {slice: str},
        'ports': {port_name: wire_name} } }"""
    tiles = {}
    inst_pat = re.compile(r"^tile_PLC2\b")
    init_pat = re.compile(r"\.SLICE([ABCD])_LUT([01])_INITVAL\(16'b([01]+)\)")
    mode_pat = re.compile(r"\.SLICE([ABCD])_MODE\(\"([^\"]+)\"\)")
    inj_pat  = re.compile(r"\.SLICE([ABCD])_CCU2_INJECT1_([01])\(\"([^\"]+)\"\)")
    inst_name_pat = re.compile(r"\)\s+(R\d+C\d+)_PLC2_inst\s*\(")
    port_pat = re.compile(r"\.([A-Z][A-Z0-9_]*)\s*\(\s*([^)\s]+)\s*\)")

    with path.open() as f:
        for line in f:
            if not line.startswith("tile_PLC2"):
                continue
            mi = inst_name_pat.search(line)
            if not mi:
                continue
            key = mi.group(1)
            inits = {(s, k): v for (s, k, v) in init_pat.findall(line)}
            modes = dict(mode_pat.findall(line))
            inj   = {(s, k): v for (s, k, v) in inj_pat.findall(line)}
            # Collect port -> wire map.  We only need it for instance
            # connections, so start scanning after the inst name.
            paren_idx = line.index(f"{key}_PLC2_inst")
            body = line[paren_idx:]
            ports = dict(port_pat.findall(body))
            tiles[key] = {
                "inits": inits,
                "modes": modes,
                "inj": inj,
                "ports": ports,
            }
    return tiles


def parse_assigns(path: Path) -> dict:
    assigns = {}
    pat = re.compile(r"^assign\s+([^=\s]+)\s*=\s*([^;]+);")
    with path.open() as f:
        for line in f:
            m = pat.match(line)
            if m:
                assigns[m.group(1).strip()] = m.group(2).strip()
    return assigns


SINGLE_TOKEN = re.compile(r"^[\\A-Za-z0-9_.]+$")


def resolve(assigns: dict, name: str, max_steps: int = 256):
    """Follow assign chain until we hit something that is not another
    single-token alias.  Return the final name."""
    seen = {name}
    cur = name
    for _ in range(max_steps):
        rhs = assigns.get(cur)
        if rhs is None:
            return cur
        if SINGLE_TOKEN.match(rhs):
            if rhs in seen:
                return rhs
            seen.add(rhs)
            cur = rhs
        else:
            return cur
    return cur


SLICE_PORT_RE = re.compile(r"^(R(\d+)C(\d+))_PLC2_([A-Z][A-Z0-9_]*)_SLICE$")


def parse_slice_port(name: str):
    m = SLICE_PORT_RE.match(name)
    if not m:
        return None
    return {
        "tile": m.group(1),
        "row": int(m.group(2)),
        "col": int(m.group(3)),
        "port": m.group(4),
    }


def lut_inputs_for(slice_letter: str, lut_idx: int):
    """Return the 4 input port names that connect to a LUT4."""
    # Per cells_sim.v / tile.v:
    #   sliceA LUT0: A0,B0,C0,D0       sliceA LUT1: A1,B1,C1,D1
    #   sliceB LUT0: A2,B2,C2,D2       sliceB LUT1: A3,B3,C3,D3
    #   sliceC LUT0: A4,B4,C4,D4       sliceC LUT1: A5,B5,C5,D5
    #   sliceD LUT0: A6,B6,C6,D6       sliceD LUT1: A7,B7,C7,D7
    slice_to_base = {"A": 0, "B": 2, "C": 4, "D": 6}
    idx = slice_to_base[slice_letter] + lut_idx
    return [f"A{idx}", f"B{idx}", f"C{idx}", f"D{idx}"]


def m_port(slice_letter: str, reg_idx: int):
    """The M-input that feeds the FF when SD='0' (the default).  M0 is the
    sliceA reg0 input.  Each slice has M for both regs (we follow the
    register-set parameter naming)."""
    slice_to_base = {"A": 0, "B": 2, "C": 4, "D": 6}
    return f"M{slice_to_base[slice_letter] + reg_idx}"


def q_port(slice_letter: str, reg_idx: int):
    slice_to_base = {"A": 0, "B": 2, "C": 4, "D": 6}
    return f"Q{slice_to_base[slice_letter] + reg_idx}"


def main():
    print("Parsing tiles ...")
    tiles = parse_tiles(SRC)
    print(f"  got {len(tiles)} tiles")
    print("Parsing assigns ...")
    assigns = parse_assigns(SRC)
    print(f"  got {len(assigns)} assigns")

    # 8 pmod outputs - (label, terminal F port found earlier)
    pmod_targets = [
        ("pmod_j2[0]", "A14", "R2C64", "C", 1),  # sliceC LUT1 -> F5
        ("pmod_j2[1]", "A13", "R2C60", "B", 0),  # sliceB LUT0 -> F2
        ("pmod_j2[2]", "A12", "R2C53", "B", 1),  # sliceB LUT1 -> F3
        ("pmod_j2[3]", "A11", "R2C53", "C", 0),  # sliceC LUT0 -> F4
        ("pmod_j2[4]", "B14", "R2C65", "B", 1),  # sliceB LUT1 -> F3
        ("pmod_j2[5]", "B13", "R2C60", "D", 0),  # sliceD LUT0 -> F6
        ("pmod_j2[6]", "B12", "R2C55", "B", 1),  # sliceB LUT1 -> F3
        ("pmod_j2[7]", "B11", "R11C10","C", 0),  # sliceC LUT0 -> F4
    ]

    report = []
    for label, ball, tile, sl, lut in pmod_targets:
        if tile not in tiles:
            print(f"  !! tile {tile} not in netlist")
            continue
        td = tiles[tile]
        init = td["inits"].get((sl, str(lut)), "0000000000000000")
        mode = td["modes"].get(sl, "LOGIC")
        inputs = []
        for inp_port in lut_inputs_for(sl, lut):
            wire = td["ports"].get(f"{inp_port}_SLICE")
            if wire is None:
                inputs.append((inp_port, None, None))
                continue
            resolved = resolve(assigns, wire)
            inputs.append((inp_port, wire, resolved))
        report.append({
            "pmod": label,
            "ball": ball,
            "tile": tile,
            "slice": sl,
            "lut": lut,
            "init": init,
            "mode": mode,
            "inputs": inputs,
        })

    OUT.write_text(json.dumps(report, indent=2))
    print(f"\nWrote {OUT}\n")

    for r in report:
        print(f"--- {r['pmod']} ({r['ball']}) -> {r['tile']} slice{r['slice']} LUT{r['lut']} ---")
        print(f"  mode={r['mode']}  INIT={r['init']}")
        for port, wire, resolved in r["inputs"]:
            print(f"    {port:3s}: wire={wire}")
            print(f"         -> {resolved}")


if __name__ == "__main__":
    main()
