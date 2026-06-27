# Watchdog KOTH OLED Variant

This sibling variant keeps `../02_watchdog_koth` as the source of truth for the
PicoRV32 SoC, watchdog, bootloader, payload tooling, and payload examples. The
local RTL adds only the passive GC9A01 OLED execution heatmap and board wrapper.

The CPU-visible display MMIO range remains present through the reused `soc_bus`,
but the physical OLED pins are driven only by the local heatmap renderer.

## Build

From this directory:

```sh
bash scripts/build_bitstream.sh
```

The output bitstream is:

```text
build/greymecha_watchdog_oled/watchdog_koth_oled.bit
```

## Badge Files

Deploy the bitstream and a packed payload to:

```text
/challs/watchdog_oled/watchdog_koth_oled.bit
/challs/watchdog_oled/payload.wdog
```

Then run:

```py
import challs.watchdog_oled.run
```

The launcher releases the RP2350 display in-place, programs the OLED watchdog
bitstream, sends the payload over UART, and prints UART output.
