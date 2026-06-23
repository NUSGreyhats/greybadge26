# Script Reorganization

## Goal

Provide a small, stable command surface for building the bitstream, compiling payloads, and uploading to the GreyMecha hardware while preserving compatibility with useful existing entry points.

## Current State

Scripts are spread across simulation, payload, hardware, tool, and board-test contexts. Some scripts overlap in behavior or encode workflow-specific assumptions. Existing paths may already be referenced by local notes, automation, or operator muscle memory, so removing them outright would create unnecessary friction.

## Required Implementation Changes

Create three canonical scripts under the top-level `scripts/` directory:

```text
scripts/build_bitstream.sh
scripts/compile_payload.sh <payload>
scripts/upload_greymecha.ps1 -Payload <name> [-Drive D:\] [-Port COM17] [-BuildBitstream]
```

Define the old script archive structure as:

```text
old/sim_scripts/
old/payload_scripts/
old/hardware_scripts/
old/tools/
old/board_tests/
```

Move older scripts into the appropriate `old/` subfolder when they are no longer canonical. Keep old paths as compatibility wrappers where compatibility is useful. Wrappers should delegate to the canonical scripts and preserve expected arguments where practical.

The canonical scripts should be documented as the supported operator workflow:

- `scripts/build_bitstream.sh` builds the FPGA bitstream.
- `scripts/compile_payload.sh <payload>` compiles a named payload.
- `scripts/upload_greymecha.ps1` handles upload to the board, with optional bitstream build, drive selection, and serial port selection.

## Acceptance Criteria

- The three canonical scripts exist under top-level `scripts/`.
- Archived scripts are grouped under the specified `old/` subfolders.
- Useful legacy entry points still run as wrappers and clearly delegate to the new scripts.
- Documentation and examples point users at the canonical scripts.
- Script behavior remains equivalent unless a change is explicitly called out by the implementation task.

## Test Plan

- Run each canonical script with its expected nominal arguments.
- Run representative compatibility wrappers and confirm they invoke the matching canonical command.
- Verify missing or invalid arguments produce actionable errors.
- Confirm upload flow supports `-Payload <name>`, optional `-Drive`, optional `-Port`, and optional `-BuildBitstream`.
- Check that no unrelated generated or implementation files changed during the reorganization.

## Notes/Assumptions

- Compatibility wrappers should be kept only where they reduce breakage for known or likely users.
- The reorganization should not change payload formats, firmware behavior, RTL behavior, or board protocol behavior.
- Shell scripts should remain usable from the existing development environment.

