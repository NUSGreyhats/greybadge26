# Flag Update

## Goal

Update the challenge flag everywhere to the new canonical value and ensure tests, examples, documentation, and distribution payloads all agree.

## Current State

Existing tests, examples, documentation, payloads, and distribution artifacts may still reference the previous flag value. The implementation pass must treat any old value as stale.

## Required Implementation Changes

Use this flag as the sole canonical value:

```text
grey{mmio_fuzzz}
```

Represent the flag in little-endian 32-bit words as:

```text
0x79657267
0x696d6d7b
0x75665f6f
0x7d7a7a7a
```

Update all tests, docs, examples, firmware references, RTL memories, helper scripts, payload source, and generated distribution payloads that encode or assert the flag value.

## Acceptance Criteria

- Searching the repository shows no remaining intended references to the previous flag value.
- All expected flag reads reconstruct exactly `grey{mmio_fuzzz}`.
- Tests assert the new little-endian words.
- Distributed payloads and examples demonstrate the new flag.
- Documentation names the new flag value consistently.

## Test Plan

- Run repository-wide searches for old and new flag strings.
- Run flag memory/peripheral tests.
- Run payload tests that read or print the flag.
- Rebuild any distribution payloads that embed the flag and verify their output.
- Confirm little-endian word ordering in tests and implementation.

## Notes/Assumptions

- The new flag is 16 bytes and maps cleanly to four 32-bit little-endian words.
- All user-facing challenge material should use the exact spelling `grey{mmio_fuzzz}`.
- Any stale generated artifact should be regenerated rather than hand-edited when possible.

