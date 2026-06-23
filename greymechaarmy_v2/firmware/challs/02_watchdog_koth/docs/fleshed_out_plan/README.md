# Watchdog KOTH Detailed Plan

This directory expands `docs/fleshed_out_plan.md` into numbered section folders. Each section explains what must be built, how to achieve it, how to simulate it, and how to validate it on the GreyMecha/Army board family.

`docs/plan.md` is intentionally left unchanged.

## Sections

Alternative organization: [Plan Sectioned](plan_sectioned/README.md)

1. [Overview](01_overview/README.md)
2. [Challenge Design](02_challenge_design/README.md)
3. [Implementation Roadmap](03_implementation_roadmap/README.md)
4. [Acceptance Criteria](04_acceptance_criteria/README.md)
5. [Test Plan](05_test_plan/README.md)
6. [GreyMecha/Army Board Reference](06_greymecha_army_board_reference/README.md)
7. [Risks and Open Questions](07_risks_and_open_questions/README.md)
8. [Original Rough Notes](08_original_rough_notes/README.md)
9. [Project Structure](09_project_structure/README.md)

## Recommended Build Order

1. Bring up the existing PicoRV32 project and confirm the baseline peripherals still work.
2. Define the challenge memory map and payload ABI.
3. Implement the UART loader with a minimal payload execution test.
4. Add watchdog cycle and region enforcement in simulation first.
5. Add the flag access path and success/failure reporting.
6. Build reference C and assembly solutions.
7. Tune the watchdog threshold using simulation, then validate on hardware.
8. Package public player artifacts and run a clean solve rehearsal.
9. Keep source, simulation, payload, hardware-test, and documentation artifacts in the project structure described in section 09.

## Referenced Board Artifacts

Use these local projects as board references:

- Greybadge25 KiCad project: `C:\Users\zunmun\Documents\Stuff\Github\WORK\GreyHats\greybadge25\hardware\greybadge_pcb\greybadge_pcb.kicad_pro`
- Greybadge25 ECP5 flow: `C:\Users\zunmun\Documents\Stuff\Github\WORK\GreyHats\greybadge25\firmware\ecp5`
- Greybadge26 KiCad project: `C:\Users\zunmun\Documents\Stuff\Github\WORK\GreyHats\greybadge26\greymechaarmy_v2\hardware\greybadge_pcb\greybadge_pcb.kicad_pro`
- Greybadge26 hardware schematics: `ecp5_25_fpga.kicad_sch`, `greybadge_pcb.kicad_sch`, `rp2350.kicad_sch`, and `greybadge_pcb.kicad_pcb`

The Greybadge25 ECP5 tests include existing Makefile-based flows for UART, OLED, and FPGA tests. The scanned Makefiles use `yosys`, `nextpnr-ecp5 --25k --package CABGA256 --lpf pinout.lpf`, and `ecppack`. Use those flows as the first hardware bring-up reference, then validate the final pinout against the Greybadge26 schematic if the challenge targets the newer board.

## Working Assumptions

- The first implementation should prefer raw binary payload upload over ELF parsing.
- The watchdog should be configurable during development and fixed for the released challenge.
- Simulation is the primary source of timing truth until hardware measurements prove otherwise.
- The public challenge should expose enough timing and memory information for a skilled player to solve without guessing.
