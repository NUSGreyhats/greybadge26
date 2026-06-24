# Payload Compile Tools

This folder contains a minimal build flow for Watchdog KOTH payloads.

## Requirements

- `riscv64-unknown-elf-gcc`
- `riscv64-unknown-elf-objcopy`
- Python 3
- Optional: `riscv64-unknown-elf-objdump`

## Build

From this directory:

```sh
bash compile_payload.sh
```

Or build a different payload source directory:

```sh
bash compile_payload.sh payload
```

Output files are written to `build/`:

```text
build/payload.elf       linked RV32I ELF
build/payload.bin       raw payload bytes loaded at 0x00008000
build/payload.wdog      UART upload packet
build/payload.wdog.hex  one hex byte per line, useful for simulation
build/payload.dis       optional disassembly or diagnostic
```

The `.wdog` format is:

```text
0x00  4 bytes  ASCII "WDOG"
0x04  4 bytes  payload length, little-endian
0x08  N bytes  raw payload binary
```

## Payload Layout

The payload source directory must contain:

```text
startup.S
main.c
linker.ld
```

The linker places code at:

```text
0x00008000
```

and the payload must fit within 16 KiB.

## Useful MMIO Addresses

```c
#define UART_BASE      0x10000000u
#define LED_BASE       0x10000100u
#define FLAG_BASE      0x20000000u
```