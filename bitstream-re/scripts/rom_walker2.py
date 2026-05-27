#!/usr/bin/env python3
"""Continue from `rom_walker.py`: from each `mem_value[i]` FF, follow the
M-input (the FF data) back through the netlist to the LUTs that
implement the ROM read.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "verilog" / "main_decomp.v"
OUT_DIR = ROOT / "analysis"

# (bit, tile holding the mem_value FF, Qn we observed)
# Bit 7 is constant zero so we skip it.
FFS = [
    (0, "R2C64", 1),
    (1, "R2C57", 5),
    (2, "R2C55", 4),
    (3, "R2C53", 3),
    (4, "R2C65", 2),
    (5, "R2C60", 3),
    (6, "R2C54", 0),
]

# Q index -> (slice, reg) mapping used by the decompiler.
Q_TO_REG = {
    0: ("A", 0),
    1: ("A", 1),
    2: ("B", 0),
    3: ("B", 1),
    4: ("C", 0),
    5: ("C", 1),
    6: ("D", 0),
    7: ("D", 1),
}
M_PORTS = {0: "M0", 1: "M1", 2: "M2", 3: "M3", 4: "M4", 5: "M5", 6: "M6", 7: "M7"}
SLICE_LUT_INPUTS = {
    "A": {0: ("A0", "B0", "C0", "D0"), 1: ("A1", "B1", "C1", "D1")},
    "B": {0: ("A2", "B2", "C2", "D2"), 1: ("A3", "B3", "C3", "D3")},
    "C": {0: ("A4", "B4", "C4", "D4"), 1: ("A5", "B5", "C5", "D5")},
    "D": {0: ("A6", "B6", "C6", "D6"), 1: ("A7", "B7", "C7", "D7")},
}
SLICE_LUT_F_PORT = {  # which slice F port comes from sliceX.LUTn
    "A": {0: "F0", 1: "F1"},
    "B": {0: "F2", 1: "F3"},
    "C": {0: "F4", 1: "F5"},
    "D": {0: "F6", 1: "F7"},
}


def parse_tiles(path: Path) -> dict:
    tiles = {}
    init_pat = re.compile(r"\.SLICE([ABCD])_LUT([01])_INITVAL\(16'b([01]+)\)")
    mode_pat = re.compile(r"\.SLICE([ABCD])_MODE\(\"([^\"]+)\"\)")
    sd_pat   = re.compile(r"\.SLICE([ABCD])_REG([01])_SD\(\"([^\"]+)\"\)")
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
            sd = {(s, k): v for (s, k, v) in sd_pat.findall(line)}
            paren_idx = line.index(f"{key}_PLC2_inst")
            body = line[paren_idx:]
            ports = dict(port_pat.findall(body))
            tiles[key] = {
                "inits": inits,
                "modes": modes,
                "sd": sd,
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


def resolve(assigns: dict, name: str, max_steps: int = 512):
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


SLICE_F_OUT_RE = re.compile(r"^(R(\d+)C(\d+))_PLC2_F(\d+)_SLICE$")
SLICE_FX_OUT_RE = re.compile(r"^(R(\d+)C(\d+))_PLC2_F5([ABCD])_SLICE$")
SLICE_Q_OUT_RE = re.compile(r"^(R(\d+)C(\d+))_PLC2_Q(\d+)_SLICE$")


def analyse_lut(td, slice_letter, lut_idx, assigns):
    """Resolve the 4 inputs of a LUT4 in this tile/slice and return
    structured info."""
    inputs = []
    for inp in SLICE_LUT_INPUTS[slice_letter][lut_idx]:
        wire = td["ports"].get(f"{inp}_SLICE")
        if wire is None:
            inputs.append({"port": inp, "wire": None, "resolved": None})
            continue
        resolved = resolve(assigns, wire)
        inputs.append({"port": inp, "wire": wire, "resolved": resolved})
    return {
        "slice": slice_letter,
        "lut": lut_idx,
        "init": td["inits"].get((slice_letter, str(lut_idx)), "0000000000000000"),
        "mode": td["modes"].get(slice_letter, "LOGIC"),
        "inputs": inputs,
    }


def main():
    print("Parsing tiles ...")
    tiles = parse_tiles(SRC)
    print(f"  got {len(tiles)} tiles")
    print("Parsing assigns ...")
    assigns = parse_assigns(SRC)
    print(f"  got {len(assigns)} assigns")

    bit_to_lut_chain = {}
    address_input_candidates = set()

    for bit_idx, tile, qn in FFS:
        td = tiles[tile]
        slice_l, reg_i = Q_TO_REG[qn]
        m_port = M_PORTS[qn]
        sd = td["sd"].get((slice_l, str(reg_i)), "0")
        print(f"\n=== mem_value[{bit_idx}]  FF = {tile}.Q{qn} (slice{slice_l} reg{reg_i})  SD={sd} ===")
        wire = td["ports"].get(f"{m_port}_SLICE")
        if wire is None:
            print(f"  !! cannot find {m_port}_SLICE port")
            continue
        resolved = resolve(assigns, wire)
        print(f"  M{qn} wire={wire}  -> resolved={resolved}")

        # Resolved should be a slice F-output (LUT4) or F5*-output (OFX0
        # = PFUMX between two LUT4s, i.e. a 5-input LUT).
        m_f = SLICE_F_OUT_RE.match(resolved)
        m_fx = SLICE_FX_OUT_RE.match(resolved)
        if m_fx:
            src_tile = m_fx.group(1)
            src_sl = m_fx.group(4)
            # OFX0 = PFUMX(LUT1, LUT0, M0).  Both LUTs in the same slice.
            both = []
            for lut_idx in (0, 1):
                info = analyse_lut(tiles[src_tile], src_sl, lut_idx, assigns)
                info["tile"] = src_tile
                info["bit_idx"] = bit_idx
                both.append(info)
                for inp in info["inputs"]:
                    address_input_candidates.add(inp["resolved"])
            # plus M0 select wire
            m_sel_wire = tiles[src_tile]["ports"].get(f"M{ {'A':0,'B':2,'C':4,'D':6}[src_sl] }_SLICE")
            m_sel = resolve(assigns, m_sel_wire) if m_sel_wire else None
            address_input_candidates.add(m_sel)
            entry = {
                "kind": "OFX0 (PFUMX)",
                "tile": src_tile,
                "slice": src_sl,
                "luts": both,
                "m_sel_wire": m_sel_wire,
                "m_sel_resolved": m_sel,
            }
            bit_to_lut_chain[bit_idx] = entry
            print(f"  ROM = {src_tile}.slice{src_sl} OFX0 (PFUMX)")
            for li in both:
                print(f"    LUT{li['lut']} INIT = {li['init']}")
                for inp in li["inputs"]:
                    print(f"      {inp['port']:3s} : -> {inp['resolved']}")
            print(f"    PFUMX select M = {m_sel_wire} -> {m_sel}")
            continue
        if m_f:
            src_tile = m_f.group(1)
            f_idx = int(m_f.group(4))
            f_to_slice = {0:("A",0),1:("A",1),2:("B",0),3:("B",1),
                          4:("C",0),5:("C",1),6:("D",0),7:("D",1)}
            src_sl, src_lut = f_to_slice[f_idx]
            info = analyse_lut(tiles[src_tile], src_sl, src_lut, assigns)
            info["tile"] = src_tile
            info["bit_idx"] = bit_idx
            info["kind"] = "F (direct LUT4)"
            bit_to_lut_chain[bit_idx] = info
            print(f"  ROM LUT (4-input only) = {src_tile}.slice{src_sl}.LUT{src_lut}  INIT={info['init']}")
            for inp in info["inputs"]:
                print(f"    {inp['port']:3s} : -> {inp['resolved']}")
                address_input_candidates.add(inp["resolved"])
            continue
        print(f"  !! resolved {resolved} is neither F nor F5*; dumping nearby")
        bit_to_lut_chain[bit_idx] = {"resolved": resolved}

    print("\n=== Address candidates (union of all ROM-LUT inputs) ===")
    for c in sorted(address_input_candidates):
        print(f"  {c}")

    (OUT_DIR / "rom_walk2.json").write_text(json.dumps({
        str(k): v for k, v in bit_to_lut_chain.items()
    }, indent=2))


if __name__ == "__main__":
    main()
