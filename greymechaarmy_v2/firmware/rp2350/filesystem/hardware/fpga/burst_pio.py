# Phase A burst driver: rp2pio.StateMachine + DMA-backed background_write.
#
# Public interface (matches BurstDriverNative in Phase B):
#     drv = BurstDriverPIO(pin_tck, pin_tdi, pin_tdo, freq_hz=6_000_000)
#     drv.open()
#     drv.write(buf)        # buf is bytes-like; clocks len(buf)*8 bits of TDI
#     drv.close()
#
# No header framing is needed: the PIO program clocks 8 bits per byte
# autopulled from the TX FIFO and runs as long as bytes keep arriving. The
# caller controls total bit count by controlling len(buf). After each
# background_write completes we drain the RX FIFO (TDO response is not
# meaningful during LSC_BITSTREAM_BURST).

import rp2pio

from . import jtag_burst_pio


class BurstDriverPIO:
    def __init__(self, pin_tck, pin_tdi, pin_tdo, freq_hz=6_000_000):
        self._pin_tck = pin_tck
        self._pin_tdi = pin_tdi
        self._pin_tdo = pin_tdo
        # SM clock = freq_hz * 4 nominally; the inner loop is 4 cycles/bit.
        # The extra `set x, 7` once per byte adds 1/8 of a cycle per bit on
        # average; we accept the slight TCK derate rather than scaling here.
        self._sm_freq = freq_hz * 4
        self._sm = None

    def open(self):
        if self._sm is not None:
            return
        self._sm = rp2pio.StateMachine(
            jtag_burst_pio.PROGRAM.assembled,
            frequency=self._sm_freq,
            first_out_pin=self._pin_tdi,
            out_pin_count=1,
            first_in_pin=self._pin_tdo,
            in_pin_count=1,
            first_sideset_pin=self._pin_tck,
            sideset_pin_count=1,
            sideset_enable=True,        # .side_set 1 opt
            auto_pull=True,
            pull_threshold=8,
            out_shift_right=False,      # MSB first within each byte (matches bitbangio.SPI default)
            auto_push=True,
            push_threshold=8,
            in_shift_right=True,
        )

    def write(self, buf):
        if self._sm is None:
            raise RuntimeError("BurstDriverPIO not open")
        if len(buf) == 0:
            return
        self._sm.background_write(buf)
        # Drain the RX FIFO continuously while DMA is running; without this,
        # auto_push fills the 4-entry RX FIFO after 4 bytes and the SM stalls
        # (blocking the DMA transfer from completing).
        while self._sm.writing:
            if self._sm.in_waiting:
                self._sm.clear_rxfifo()
        # Final drain for any bytes that arrived after the DMA completed.
        self._sm.clear_rxfifo()

    def close(self):
        if self._sm is None:
            return
        self._sm.deinit()
        self._sm = None
