import time

import adafruit_pioasm
import board
import digitalio
import hardware.fpga
import rp2pio

print("DIRECT_FPGA_UPLOAD_GP8_PIO_SIDESET_START")

jtag_rst = None
mode_pins = []
fixed = []
pmod = []
gp8_dio = None
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

    gp8_dio = open_output(board.GP8, False)
    time.sleep(0.35)
    value = read_pmod()
    print("digitalio gp8 0 addr 30 value", value, fmt(value))

    gp8_dio.value = True
    time.sleep(0.35)
    value = read_pmod()
    print("digitalio gp8 1 addr 31 value", value, fmt(value))

    gp8_dio.value = False
    time.sleep(0.1)
    gp8_dio.deinit()
    gp8_dio = None

    program = adafruit_pioasm.assemble(
        """
.program gp8side
.side_set 1
loop:
    pull
    mov x, osr
    jmp !x low side 0
high:
    nop side 1
    jmp loop side 1
low:
    nop side 0
    jmp loop side 0
"""
    )

    sm = rp2pio.StateMachine(
        program,
        frequency=4000,
        first_sideset_pin=board.GP8,
        initial_sideset_pin_state=0,
        initial_sideset_pin_direction=1,
    )

    for bit in [0, 1, 0, 1, 0]:
        sm.write(bytes((bit,)))
        time.sleep(0.35)
        value = read_pmod()
        print("pio-side gp8", bit, "addr", 30 | bit, "value", value, fmt(value))
finally:
    if sm:
        sm.deinit()
    if gp8_dio:
        gp8_dio.deinit()
    for d in pmod:
        if d is not None:
            d.deinit()
    for d in fixed:
        d.deinit()
    for d in mode_pins:
        d.deinit()
    if jtag_rst:
        jtag_rst.deinit()

print("DIRECT_FPGA_UPLOAD_GP8_PIO_SIDESET_DONE")
