# Behavioral Analysis of main.bit

Source-of-truth artifacts produced from `main.bit` only (no firmware/schematic context).

## Recovered RTL Files

| File | Lines | Purpose |
|------|-------|---------|
| `verilog/main_decomp.v` | 1.15M | Gate-level (`TRELLIS_SLICE`, LUT4, PDPW16KD, IO) — raw decompiler output |
| `verilog/main_synth.v` | 3.66M | After Yosys `synth`+`flatten`+`opt` — primitive `$and/$or/$mux` with processes |
| `verilog/main_behavior.v` | 1.34M | Top module only, condensed after extra Yosys opt+flatten |
| `verilog/main_behavior_noinit.v` | 1.34M | Same with `initial` blocks stripped for downstream tool compatibility |
| **`verilog/main_pad_behavior.v`** | **1.37K** | **Consolidated RTL — only logic that drives used package balls** |
| `verilog/pads/pad_<BALL>_*.v` | varies | Per-output-pad backward cones (34 files) |

The smallest readable RTL is **`main_pad_behavior.v`** (1366 lines, 237 always/assign units, 67 FFs). Start there.

## Clock Domains

| Clock net | Posedge FFs (full design) | Posedge FFs (reaching pads) | Note |
|-----------|---------------------------|----------------------------|------|
| `G_HPBX0300` | 986 | 65 | Primary clock; nearly all logic |
| `G_HPBX0200` | 13 | 1 | Secondary |
| `G_HPBX0100` | 8 | 1 | Secondary |
| `G_HPBX0000` | 7 | 0 | Secondary (drives only DDR/IOLOGIC ports) |
| `MIB_R0C29_PIOT0_JPADDIA_PIO` | 1 | 0 | Input pad A7 used as clock |
| `MIB_R2C72_PICR0_JDIA` (negedge) | 24 | 0 | Input on right side used as negedge clock — likely the DDR strobe path |

The design is essentially **single-clock on `G_HPBX0300`** (a global clock buffer; its actual external source is one of the dedicated clock-input balls, which the bitstream alone does not tell us).

## Where the External IO Goes

After backward-cone reduction, only **5 input pads** actually drive logic that reaches the 34 used output port nets:

| Internal name | Position | Notes |
|---------------|----------|-------|
| `MIB_R0C67_PIOT0_JPADDIB_PIO` | top row, col 67 (ball B14) | Single LVCMOS25 input |
| `MIB_R11C72_PICR0_JPADDID_PIO` | right side row 11 | SSTL18 DDR-bank input |
| `MIB_R2C72_PICR0_JDIA` | right side row 2 | DDR data input |
| `MIB_R8C72_PICR0_DQS2_JDIA` | right side row 8 | DDR DQS2 strobe |
| `MIB_R8C72_PICR0_DQS2_JDIB` | right side row 8 | DQS2 strobe (complementary) |

The other 18 input balls are either pulled to constants or only feed dead logic — many drive enable signals into the DDR/IOLOGIC chain that doesn't propagate to user IO.

The bulk of FFs in the bitstream (~948 of 1015) drive **internal IOLOGIC/DDR ports** (`PICR0_JTXDATA*`, `PICL0_JTXDATA*`) on the right and left chip edges. These are SSTL18_II outputs typical of an **SDRAM/DDR memory controller** front-end. They are not externally observable on package balls in the same way as LVCMOS25 pads — they drive on-die IO logic.

## What the Pad-Driving Logic Looks Like

A representative cone for **ball A3 PADDOA_PIO** ([`verilog/pads/pad_A3_PADDOA_PIO.v`](verilog/pads/pad_A3_PADDOA_PIO.v)) shows a **shift register chain on `G_HPBX0300`**:

```verilog
// Synchronous FF with clock-enable, captured from neighbor cell.
always @* begin
  _2063_ = \R4C16_PLC2_inst.sliceD_inst.ff_1.Q ;       // default: hold
  if (\R10C10_PLC2_inst.sliceD_inst.ff_0.CE) begin
    _2063_ = \R4C11_PLC2_inst.sliceA_inst.ff_1.Q ;     // CE active: shift in
  end
end
always @(posedge G_HPBX0300) begin
  \R4C16_PLC2_inst.sliceD_inst.ff_1.Q <= _2063_;
end
```

The same `R10C10.ff_0.CE` and `R6C33.ff_0.CE` signals gate dozens of similar FFs — they're the global clock-enable signals for a sequencer that walks data through a chain.

Several FFs additionally have a synchronous-clear behavior:

```verilog
if (_5114_) begin _2308_ = 1'b0; end
else if (...CE) begin _2308_ = ...; end
```

`_5114_` aliases `_5085_` (one driver feeding many resets — a global reset/clear signal).

## Constant Outputs

A few output pads are **driven by constants**:

| Pad | Driver | Value |
|-----|--------|-------|
| A11 `PADDOB_PIO` | `R2C53.sliceB.lut4_1.Z` → `_6974_` | `1'b1` |
| (multiple `*_PADDT*` tristate-enables) | various LUTs evaluated to constants | mostly `1'b1` (output enabled) |

A pad whose tristate-enable is constant `1` is simply **always driving** (not tri-stated).

## Output Pad Categories

Across the 34 used output ports (covering 28 unique package balls):

- **`*_PADDOA_PIO` / `*_PADDOB_PIO`** — direct pad output value (LVCMOS25)
- **`*_PADDTA_PIO` / `*_PADDTB_PIO`** — pad tristate enable (typically constant)
- **`*_JTXDATA0A_SIOLOGIC` / `*_JTXDATA0B_SIOLOGIC`** — IOLOGIC TX data path (SDR mode)
- **`*_JTSDATA0A_SIOLOGIC` / `*_JTSDATA0B_SIOLOGIC`** — IOLOGIC TX-side tristate path

So each used ball has a value-out path and a tristate-out path; some balls drive through both the simple PADDO* and IOLOGIC chains in parallel (typical when DDR IO blocks are partially used).

## What This Bitstream Does (Best Inference From Bitstream Alone)

1. Runs a single primary clock domain on `G_HPBX0300`. We cannot recover its frequency.
2. Implements a sizeable **shift-register / sequencer** on the top row of the fabric (R2..R10) feeding LVCMOS25 outputs on the top edge balls.
3. The shift chain advances on a clock-enable signal `R10C10.D.ff_0.CE` and has synchronous clears triggered by a LUT output network rooted at `R10C10.D.ff_0.CE` / `_5085_`.
4. Reads from ball **B14** (top edge input) and from **right-edge DDR/SSTL pads** (DQS strobes and one DDR data input). The data eventually reaches the top-edge LVCMOS25 outputs.
5. Has a separate, larger pool of ~950 FFs feeding the right-edge SSTL18 IOLOGIC outputs — characteristic of an **on-die DDR memory controller** datapath. These FFs do not reach the LVCMOS25 user outputs.

No PLL configuration was extracted (PLL tile programming is partially documented in Project Trellis). No EBR data RAM is initialized (1688 EBR INIT bits were extracted but they appear in routing/CIB tiles and do not form a coherent RAM contents block in this design).

## How to Read the Recovered RTL

Signal names follow this pattern:

- `MIB_R<r>C<c>_PIOT0_*` / `MIB_R<r>C<c>_PIOT1_*` — pad cells on the top edge, column c
- `MIB_R<r>C<c>_PICL0_*` / `MIB_R<r>C<c>_PICR0_*` — pad cells on left/right edges, row r
- `\R<r>C<c>_PLC2_inst.slice<X>_inst.ff_<n>.Q` — FF n in slice X of PLC2 logic tile at row r, col c
- `\R<r>C<c>_PLC2_inst.slice<X>_inst.genblk9.lut4_<n>.Z` — LUT4 n output Z in the same slice
- `_NNNN_` — Yosys-introduced intermediate signal
- `G_HPBX<XXXX>` — global clock buffer output (XXXX is the clock spine index)

Each FF is encoded as a pair of always blocks:
1. `always @*` that computes the next-state expression into a `_NNNN_` reg
2. `always @(posedge clk)` that captures `_NNNN_` into the FF's `.Q`

This is faithful to the silicon — each Lattice slice FF has CE/SR/clock inputs and the next-state mux pattern recovered here matches the standard slice cell.
