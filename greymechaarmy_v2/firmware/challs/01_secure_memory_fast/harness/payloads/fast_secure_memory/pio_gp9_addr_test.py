import time

import adafruit_pioasm
import board
import digitalio
import hardware
import hardware.default_overlay
import rp2pio

print("PIO_GP9_ADDR_TEST_START")

try:
    overlay = hardware.hw_state["fpga_overlay"]
except Exception:
    try:
        overlay = hardware.default_overlay.Overlay()
        hardware.hw_state = {"fpga_overlay": overlay}
    except Exception:
        overlay = None

if overlay:
    try:
        overlay.deinit_mode_buttons()
    except Exception:
        pass
    try:
        overlay.deinit_mode_uart()
    except Exception:
        pass
    overlay.set_mode((0, 1, 0))

fixed = []
for pin in [board.GP8, board.GP10, board.GP11, board.GP12]:
    d = digitalio.DigitalInOut(pin)
    d.direction = digitalio.Direction.OUTPUT
    d.value = True
    fixed.append(d)

pmod = []
for pin in [board.GP27, None, board.GP23, board.GP25, board.GP26, board.GP22, board.GP28, board.GP24]:
    if pin is None:
        pmod.append(None)
    else:
        d = digitalio.DigitalInOut(pin)
        d.direction = digitalio.Direction.INPUT
        pmod.append(d)


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


program = adafruit_pioasm.assemble(
    """
.program gp9
loop:
    pull
    out pins, 1
    jmp loop
"""
)

sm = rp2pio.StateMachine(
    program,
    frequency=4000,
    first_out_pin=board.GP9,
    initial_out_pin_state=0,
    initial_out_pin_direction=1,
)

try:
    for bit in [0, 1, 0, 1, 0]:
        sm.write(bytes((bit,)))
        time.sleep(0.35)
        value = read_pmod()
        print("gp9", bit, "addr", 29 if bit == 0 else 31, "value", value, fmt(value))
finally:
    sm.deinit()
    for d in pmod:
        if d is not None:
            d.deinit()
    for d in fixed:
        d.deinit()

print("PIO_GP9_ADDR_TEST_DONE")
