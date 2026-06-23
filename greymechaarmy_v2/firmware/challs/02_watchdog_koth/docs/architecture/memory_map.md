# Watchdog KOTH Memory Map

This document mirrors `rtl/core/memory_map.vh`.

```text
0x0000_0000 - 0x0000_7fff  boot firmware ROM/RAM
0x0000_8000 - 0x0000_bfff  payload code/data RAM
0x0000_c000 - 0x0000_cfff  payload stack RAM
0x1000_0000 - 0x1000_00ff  UART MMIO
0x1000_0100 - 0x1000_01ff  LED/status MMIO
0x1000_0200 - 0x1000_02ff  watchdog MMIO
0x1000_0300 - 0x1000_03ff  reset/status/cycle MMIO
0x1000_1000 - 0x1000_1fff  GC9A01/display bridge MMIO
0x2000_0000 - 0x2000_00ff  flag ROM/peripheral
```

Unmapped reads return `0xbad0add5` and assert the bus `fault` signal. This keeps unmapped behavior deterministic for simulation and firmware self-tests.

## Flag Peripheral

The flag peripheral is a read-only 256-byte window at `0x2000_0000`. Writes are
ignored.

```text
0x2000_0000  flag word 0  "grey"
0x2000_0004  flag word 1  "{mmi"
0x2000_0008  flag word 2  "o_fu"
0x2000_000c  flag word 3  "zzz}"
0x2000_0010  zero / outside current flag data
0x2000_00f0  flag length in bytes, currently 16
0x2000_00f4  status, bit 0 = flag present
0x2000_00f8  profile id, 0 = public flag
```

The 32-bit word constants are little-endian as observed by RISC-V loads, so the
first word reads as `0x79657267`.

## Reset/Status/Cycle Peripheral

```text
0x1000_0300  reset reason
0x1000_0304  cycle counter low 32 bits
0x1000_0308  cycle counter high 32 bits
```

## Watchdog Peripheral

The watchdog is controlled by CPU MMIO and intentionally supports a software
disable path.

```text
0x1000_0200  CTRL     bit 0 enable, bit 1 arm, bit 2 clear counter on write
0x1000_0204  LIMIT    FPGA-cycle timeout threshold
0x1000_0208  COUNTER  current counter, writable for tests/payloads
0x1000_020c  STATUS   bit 0 enabled, bit 1 armed, bit 2 timeout
0x1000_0210  BASE     payload base address for watchdog-active fetches
0x1000_0214  END      payload end address for watchdog-active fetches
```

The current implementation starts counting on the first accepted instruction fetch
inside the configured watchdog region, then increments once per FPGA clock cycle
while armed, enabled, and payload-active. A timeout performs a soft CPU reset,
records `WATCHDOG_RESET`, and lets boot firmware restart and report the reason.
Writing `CTRL=0` from payload code disables watchdog enforcement while leaving the
MMIO register file readable and writable. With `CTRL.enable=0`, the watchdog no
longer increments, times out, or raises region resets.

Payload-region enforcement is part of watchdog enforcement. While the watchdog is
enabled and armed, after the first accepted instruction fetch inside the configured
region, later instruction fetches outside `BASE..END` request a soft CPU reset and
record `REGION_RESET`. The bootloader currently programs `BASE=0x00000000` and
`END=0xffffffff`, so region reset is not expected in the normal bootloader flow.

## Reset Reasons

```text
0x0000_0000  CLEAN_BOOT
0x0000_0001  WATCHDOG_RESET
0x0000_0002  REGION_RESET
0x0000_0003  PAYLOAD_FAULT
0x0000_0004  NO_SUCCESS
0x0000_0005  SUCCESS
```
