import gc
import time

import adafruit_pioasm
import board
import digitalio
import hardware
import hardware.default_overlay
import hardware.fpga
import rp2pio


MODE_SECURE_MEMORY = (0, 1, 0)
PMOD_PINS = [board.GP27, None, board.GP23, board.GP25, board.GP26, board.GP22, board.GP28, board.GP24]


def get_overlay():
    if hasattr(hardware, "hw_state") and "fpga_overlay" in hardware.hw_state:
        return hardware.hw_state["fpga_overlay"]
    overlay = hardware.default_overlay.Overlay()
    hardware.hw_state = {"fpga_overlay": overlay}
    return overlay


def setup_fpga():
    overlay = get_overlay()
    try:
        overlay.deinit_mode_buttons()
    except Exception:
        pass
    try:
        overlay.deinit_mode_uart()
    except Exception:
        pass
    print("UPLOAD")
    rst = hardware.fpga.upload_bitstream("/hardware/bitstreams/main.bit")
    try:
        rst.deinit()
    except Exception:
        pass
    overlay.set_mode(MODE_SECURE_MEMORY)
    return overlay


def pmod_inputs():
    pins = []
    for pin in PMOD_PINS:
        if pin is None:
            pins.append(None)
        else:
            dio = digitalio.DigitalInOut(pin)
            dio.direction = digitalio.Direction.INPUT
            pins.append(dio)
    return pins


def read_pmod(pins):
    value = 0
    for bit, pin in enumerate(pins):
        if pin is not None and pin.value:
            value |= 1 << bit
    return value


def byte_pair(value):
    known = value & ~0x02
    return known, known | 0x02


def fmt(value):
    return chr(value) if 32 <= value <= 126 else "\\x%02x" % value


def make_addr_sm(addr):
    program = adafruit_pioasm.assemble(
        """
.program hold_addr
set pins %d
set x 0
mov isr, x
push block
loop:
jmp loop
"""
        % (addr & 31)
    )
    return rp2pio.StateMachine(
        program,
        frequency=10000,
        init=adafruit_pioasm.assemble("set pindirs 31"),
        first_set_pin=board.GP8,
        set_pin_count=5,
        initial_set_pin_state=31,
        initial_set_pin_direction=31,
    )


def main():
    gc.collect()
    setup_fpga()
    pins = pmod_inputs()
    try:
        for addr in [31, 0, 1, 2, 3, 4, 5, 8, 14]:
            sm = make_addr_sm(addr)
            try:
                sm.restart()
                dummy = bytearray(4)
                sm.readinto(dummy)
                time.sleep(0.25)
                value = read_pmod(pins)
            finally:
                sm.deinit()
            c0, c1 = byte_pair(value)
            print("addr", addr, "value", value, fmt(c0) + "/" + fmt(c1))
    finally:
        for pin in pins:
            if pin is not None:
                pin.deinit()
    print("PIO_ADDR_DIGITALIO_DONE")


main()
