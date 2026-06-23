import time

import adafruit_pioasm
import board
import digitalio
import hardware.fpga
import rp2pio

print("DIRECT_FPGA_UPLOAD_GP8_PIO_ONLY_START")

jtag_rst = None
mode_pins = []
fixed = []
pmod = []
sm = None


def open_output(pin, value):
    d = digitalio.DigitalInOut(pin)
    d.direction = digitalio.Direction.OUTPUT
    d.value = value
    return d


def read_pmod():
    value = 0
    for i, d in enumerate(pmod):
        if d is not None and d.value:
            value |= 1 << i
    return value


def fmt(value):
    known = value & ~2
    a = chr(known) if 32 <= known <= 126 else "\\x%02x" % known
    b = chr(known | 2) if 32 <= (known | 2) <= 126 else "\\x%02x" % (known | 2)
    return a + "/" + b


try:
    print("upload main.bit")
    jtag_rst = hardware.fpga.upload_bitstream("/hardware/bitstreams/main.bit")
    print("upload done")
    time.sleep(0.2)

    mode_pins.append(open_output(board.GP13, False))
    mode_pins.append(open_output(board.GP14, True))
    mode_pins.append(open_output(board.GP15, False))
    print("mode set 010")
    time.sleep(0.2)

    for pin in [board.GP9, board.GP10, board.GP11, board.GP12]:
        fixed.append(open_output(pin, True))

    for pin in [board.GP27, None, board.GP23, board.GP25, board.GP26, board.GP22, board.GP28, board.GP24]:
        if pin is None:
            pmod.append(None)
        else:
            d = digitalio.DigitalInOut(pin)
            d.direction = digitalio.Direction.INPUT
            pmod.append(d)

    program = adafruit_pioasm.assemble(
        """
.program gp8pioonly
    set pindirs, 1
loop:
    pull
    mov x, osr
    jmp !x low
high:
    set pins, 1
    jmp loop
low:
    set pins, 0
    jmp loop
"""
    )

    sm = rp2pio.StateMachine(
        program,
        frequency=4000,
        first_set_pin=board.GP8,
        initial_set_pin_state=0,
        initial_set_pin_direction=1,
    )

    for bit in [0, 1, 0, 1, 0]:
        sm.write(bytes((bit,)))
        time.sleep(0.35)
        value = read_pmod()
        print("pio-only gp8", bit, "addr", 30 | bit, "value", value, fmt(value))
finally:
    if sm:
        sm.deinit()
    for d in pmod:
        if d is not None:
            d.deinit()
    for d in fixed:
        d.deinit()
    for d in mode_pins:
        d.deinit()
    if jtag_rst:
        jtag_rst.deinit()

print("DIRECT_FPGA_UPLOAD_GP8_PIO_ONLY_DONE")
