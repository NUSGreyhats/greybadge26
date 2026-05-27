#!/usr/bin/env python3
"""
Per-pad backward cone extractor for main_behavior_noinit.v.

Builds a driver graph treating each `always` block as one unit and each
`assign` as one unit. For each used output package pad, recursively gathers
the units that drive it and emits a self-contained Verilog cone snippet.
"""

import csv
import re
from collections import defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "verilog" / "main_behavior_noinit.v"
PORT_MAP = ROOT / "analysis" / "port_map.csv"
OUT_DIR = ROOT / "verilog" / "pads"

# A backslash-escaped identifier runs until the next whitespace.
IDENT_RE = re.compile(r"\\\S+|\b[A-Za-z_][A-Za-z0-9_]*\b")
KEYWORDS = {
    "always", "begin", "end", "if", "else", "case", "endcase", "default",
    "posedge", "negedge", "wire", "reg", "input", "output", "module",
    "endmodule", "assign", "or", "and", "not", "xor",
}


def idents_in(text: str):
    for m in IDENT_RE.finditer(text):
        tok = m.group(0)
        if tok.startswith("\\"):
            yield tok
        elif tok in KEYWORDS:
            continue
        elif tok.isdigit():
            continue
        elif re.fullmatch(r"\d+'[bBhHdD][0-9a-fA-FxXzZ_]+", tok):
            continue
        else:
            yield tok


def parse(path: Path):
    """Return (units, port_in, port_out) where units is list of dicts.

    Each unit: {
        'kind': 'assign' | 'always',
        'sens': sensitivity string (or '' for assigns / '*' for combinational),
        'writes': set(LHS names),
        'reads': set(RHS names),
        'text': source text (Verilog body),
    }
    Also returns net_to_unit: name -> unit index that writes it.
    """
    units = []
    net_to_unit = {}
    ports_in, ports_out = [], []

    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.split("\n")

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if line.startswith("  output "):
            name = line.strip().split()[1].rstrip(";")
            ports_out.append(name)
            i += 1
            continue
        if line.startswith("  input "):
            name = line.strip().split()[1].rstrip(";")
            ports_in.append(name)
            i += 1
            continue
        # assign
        m = re.match(r"^\s*assign\s+(\\?\S+(?:\s+\\\S+)?)\s*=\s*(.+?);\s*$", line)
        if m:
            lhs = m.group(1).strip()
            rhs = m.group(2).strip()
            reads = set(t for t in idents_in(rhs) if t != lhs)
            idx = len(units)
            units.append(
                {
                    "kind": "assign",
                    "sens": "",
                    "writes": {lhs},
                    "reads": reads,
                    "text": f"  assign {lhs} = {rhs};",
                }
            )
            net_to_unit[lhs] = idx
            i += 1
            continue
        # always @(...) begin ... end
        m = re.match(r"^\s*always\s+@(\([^)]+\)|\*)\s*begin\s*$", line)
        if m:
            sens = m.group(1).strip("()") if m.group(1) != "*" else "*"
            body_lines = [line]
            depth = 1  # opening `begin` already consumed
            i += 1
            kw_re = re.compile(r"\b(begin|end|endcase)\b")
            while i < n and depth > 0:
                bl = lines[i]
                body_lines.append(bl)
                for km in kw_re.finditer(bl):
                    kw = km.group(1)
                    if kw == "begin":
                        depth += 1
                    else:
                        depth -= 1
                i += 1
            body = "\n".join(body_lines)
            writes = set()
            reads = set()
            # writes: LHS of `=` and `<=`
            for am in re.finditer(
                r"(\\?\S+?)\s*(<?=)\s*([^;]+);", body
            ):
                lhs = am.group(1).strip()
                op = am.group(2)
                rhs = am.group(3).strip()
                writes.add(lhs)
                for tok in idents_in(rhs):
                    reads.add(tok)
            # also read tokens from if/case conditions
            for cm in re.finditer(r"if\s*\(([^)]+)\)", body):
                for tok in idents_in(cm.group(1)):
                    reads.add(tok)
            idx = len(units)
            units.append(
                {
                    "kind": "always",
                    "sens": sens,
                    "writes": writes,
                    "reads": reads - writes,
                    "text": body,
                }
            )
            for w in writes:
                net_to_unit.setdefault(w, idx)
            continue
        i += 1

    return units, net_to_unit, ports_in, ports_out


def extract_cone(target, units, net_to_unit, ports_in_set):
    visited_units = set()
    visited_nets = set()
    used_inputs = set()
    queue = deque([target])
    while queue:
        net = queue.popleft()
        if net in visited_nets:
            continue
        visited_nets.add(net)
        if net in ports_in_set:
            used_inputs.add(net)
            continue
        ui = net_to_unit.get(net)
        if ui is None:
            continue
        if ui in visited_units:
            continue
        visited_units.add(ui)
        for r in units[ui]["reads"]:
            if r not in visited_nets:
                queue.append(r)
    return sorted(visited_units), visited_nets, used_inputs


def emit_cone(target, unit_ids, nets, used_inputs, units):
    lines = [f"// Backward logic cone for output: {target}", "module cone("]
    port_decls = [f"  output {target}"]
    for p in sorted(used_inputs):
        port_decls.append(f"  input  {p}")
    lines.append(",\n".join(port_decls))
    lines.append(");")

    declared = {target} | used_inputs
    regs = set()
    seq_clocks = set()
    for uid in unit_ids:
        u = units[uid]
        if u["kind"] == "always" and u["sens"] != "*":
            seq_clocks.add(u["sens"])
            for w in u["writes"]:
                regs.add(w)

    other_nets = nets - declared
    for n in sorted(other_nets):
        if n in regs:
            lines.append(f"  reg {n};")
        else:
            lines.append(f"  wire {n};")
    lines.append("")

    for uid in unit_ids:
        u = units[uid]
        lines.append(u["text"])
        lines.append("")

    lines.append("endmodule")
    return "\n".join(lines) + "\n", len(unit_ids), len(regs), len(used_inputs), seq_clocks


def main():
    print(f"Parsing {SRC} ...", flush=True)
    units, net_to_unit, ports_in, ports_out = parse(SRC)
    ports_in_set = set(ports_in)
    print(
        f"  units={len(units)}  net_to_unit={len(net_to_unit)}  "
        f"inputs={len(ports_in)}  outputs={len(ports_out)}",
        flush=True,
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(PORT_MAP.open(newline="")))
    pad_targets = []
    for r in rows:
        if r["direction"] == "output" and r["package_site"]:
            pad_targets.append(r)

    index = []
    for r in pad_targets:
        decomp_port = r["decomp_port"]
        annotated = r["annotated_name"]
        pad = r["package_site"]
        unit_ids, nets, used_inputs = extract_cone(
            decomp_port, units, net_to_unit, ports_in_set
        )
        text, n_units, n_regs, n_in, clks = emit_cone(
            decomp_port, unit_ids, nets, used_inputs, units
        )
        suffix = annotated.split("_", 2)[-1] if "_" in annotated else annotated
        fname = f"pad_{pad}_{suffix}.v"
        (OUT_DIR / fname).write_text(text)
        index.append(
            {
                "pad": pad,
                "port": decomp_port,
                "annotated": annotated,
                "file": str((OUT_DIR / fname).relative_to(ROOT)),
                "units": n_units,
                "ffs": n_regs,
                "inputs": n_in,
                "clocks": ";".join(sorted(clks)),
            }
        )

    with (OUT_DIR / "INDEX.csv").open("w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "pad",
                "port",
                "annotated",
                "file",
                "units",
                "ffs",
                "inputs",
                "clocks",
            ],
        )
        w.writeheader()
        for row in index:
            w.writerow(row)

    print(f"Wrote {len(index)} per-pad cones into {OUT_DIR}/")
    total_units = sum(r["units"] for r in index)
    print(f"Total cone units: {total_units}")

    # Build consolidated RTL: union of all pad-driving units
    print("Building consolidated RTL ...", flush=True)
    all_unit_ids = set()
    all_nets = set()
    all_inputs = set()
    pad_outputs = []
    for r in pad_targets:
        unit_ids, nets, used_inputs = extract_cone(
            r["decomp_port"], units, net_to_unit, ports_in_set
        )
        all_unit_ids.update(unit_ids)
        all_nets.update(nets)
        all_inputs.update(used_inputs)
        pad_outputs.append(r["decomp_port"])

    sorted_uids = sorted(all_unit_ids)
    declared = set(pad_outputs) | all_inputs
    regs = set()
    seq_clocks = set()
    for uid in sorted_uids:
        u = units[uid]
        if u["kind"] == "always" and u["sens"] != "*":
            seq_clocks.add(u["sens"])
            for w_ in u["writes"]:
                regs.add(w_)

    out_lines = [
        "// Consolidated RTL: union of backward cones of all used output pads.",
        "// Recovered from bitstream main.bit (LFE5U-25F-6CABGA256) by ecpunpack +",
        "// VoidMercy ECP5 decompiler + Yosys synth, condensed and re-parsed.",
        "module pad_behavior(",
    ]
    port_decls = []
    for p in sorted(pad_outputs):
        port_decls.append(f"  output {p}")
    for p in sorted(all_inputs):
        port_decls.append(f"  input  {p}")
    out_lines.append(",\n".join(port_decls))
    out_lines.append(");")

    other_nets = all_nets - declared
    for n in sorted(other_nets):
        if n in regs:
            out_lines.append(f"  reg {n};")
        else:
            out_lines.append(f"  wire {n};")
    out_lines.append("")
    for uid in sorted_uids:
        out_lines.append(units[uid]["text"])
        out_lines.append("")
    out_lines.append("endmodule")

    consolidated = ROOT / "verilog" / "main_pad_behavior.v"
    consolidated.write_text("\n".join(out_lines) + "\n")
    print(
        f"Consolidated: {len(sorted_uids)} units, {len(regs)} regs, "
        f"{len(all_inputs)} inputs, {len(pad_outputs)} outputs -> {consolidated}"
    )


if __name__ == "__main__":
    main()
