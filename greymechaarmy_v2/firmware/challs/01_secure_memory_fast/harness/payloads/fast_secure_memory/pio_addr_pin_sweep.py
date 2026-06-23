import time

import adafruit_pioasm
import board
import digitalio
import hardware
import hardware.default_overlay
import rp2pio

print("PIO_ADDR_PIN_SWEEP_START")

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
.program addrpin
loop:
    pull
    out pins, 1
    jmp loop
"""
)

addr_pins = [
    ("GP8", board.GP8, 1),
    ("GP9", board.GP9, 2),
    ("GP10", board.GP10, 4),
    ("GP11", board.GP11, 8),
    ("GP12", board.GP12, 16),
]

try:
    for name, pin, mask in addr_pins:
        fixed = []
        sm = None
        try:
            for fixed_name, fixed_pin, _ in addr_pins:
                if fixed_name == name:
                    continue
                d = digitalio.DigitalInOut(fixed_pin)
                d.direction = digitalio.Direction.OUTPUT
                d.value = True
                fixed.append(d)

            sm = rp2pio.StateMachine(
                program,
                frequency=4000,
                first_out_pin=pin,
                initial_out_pin_state=0,
                initial_out_pin_direction=1,
            )

            for bit in [0, 1, 0]:
                sm.write(bytes((bit,)))
                time.sleep(0.35)
                addr = (31 & ~mask) | (mask if bit else 0)
                value = read_pmod()
                print(name, bit, "addr", addr, "value", value, fmt(value))
        except Exception as exc:
            print(name, "ERROR", repr(exc))
        finally:
            if sm:
                sm.deinit()
            for d in fixed:
                d.deinit()
finally:
    for d in pmod:
        if d is not None:
            d.deinit()

print("PIO_ADDR_PIN_SWEEP_DONE")
