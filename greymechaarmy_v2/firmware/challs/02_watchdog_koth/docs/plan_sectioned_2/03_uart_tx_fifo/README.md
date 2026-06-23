# UART TX FIFO

## Goal

Add a 32-byte transmit FIFO to `uart_mmio` so firmware and payloads can enqueue multiple outgoing bytes without stalling on each individual serial transfer.

## Current State

The UART MMIO transmit path currently behaves as a narrow ready/write interface. RX FIFO behavior and the serial bridge interface already exist and should remain compatible with current users.

## Required Implementation Changes

Implement a 32-byte TX FIFO inside `uart_mmio`.

Define `UART_STATUS.TX_READY` to mean that at least one byte of TX FIFO space is available. A write to the TX data register should enqueue one byte when space exists. The FIFO must transmit bytes to the existing serial bridge in first-in, first-out order.

Preserve the RX FIFO interface and serial bridge interface. Do not require downstream serial bridge protocol changes for this feature.

The implementation must handle:

- Empty FIFO.
- Partially full FIFO.
- Full FIFO.
- Drain while additional writes arrive.
- Reset state.

## Acceptance Criteria

- TX FIFO depth is exactly 32 bytes.
- `UART_STATUS.TX_READY` is asserted when FIFO space is available.
- `UART_STATUS.TX_READY` is deasserted when the FIFO is full.
- Bytes drain in the same order they were written.
- FIFO full handling does not corrupt queued data.
- RX FIFO behavior remains unchanged.
- Existing serial bridge interface remains unchanged.

## Test Plan

- Add or update simulation tests for FIFO ordering across more than one byte.
- Fill the FIFO to 32 bytes and verify `TX_READY` deasserts.
- Drain one byte and verify `TX_READY` reasserts.
- Attempt writes around the full boundary and verify no data corruption.
- Verify reset clears the TX FIFO and returns status to the expected idle state.
- Run existing UART RX tests to confirm no regression.

## Notes/Assumptions

- The FIFO stores bytes, not words.
- Software should poll `UART_STATUS.TX_READY` before writing.
- If existing software writes without polling, implementation behavior at full should be deterministic and covered by tests.

