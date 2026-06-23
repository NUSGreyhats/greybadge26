import gc
import os
import time

import adafruit_pioasm
import board
import digitalio
import hardware.fpga
import rp2pio


OUT_PINS = [board.GP8, board.GP9]
IN_PINS = [board.GP10, board.GP11, board.GP12]
SETTLE = 0.20
PIO_READ_TIMEOUT = 1.0


def path_exists(path):
    try:
        directory, filename = path.rsplit("/", 1)
        return filename in os.listdir(directory)
    except Exception:
        return False


def setup_fpga():
    candidates = ("/tmp/pio_fpga_comms.bit", "/hardware/bitstreams/pio_fpga_comms.bit")
    for bitstream in candidates:
        if path_exists(bitstream):
            print("upload", bitstream)
            rst = hardware.fpga.upload_bitstream(bitstream)
            time.sleep(0.25)
            return bitstream, rst

    raise RuntimeError("missing pio_fpga_comms.bit in /tmp or /hardware/bitstreams")


def open_output(pin, value):
    dio = digitalio.DigitalInOut(pin)
    dio.direction = digitalio.Direction.OUTPUT
    dio.value = value
    return dio


def open_input(pin):
    dio = digitalio.DigitalInOut(pin)
    dio.direction = digitalio.Direction.INPUT
    return dio


def deinit_all(items):
    for item in items:
        if item is not None:
            try:
                item.deinit()
            except Exception:
                pass


def expected_loopback(out_value):
    # IN bit0 is a constant-high FPGA marker on GP10.
    # IN bit1 mirrors GP8, and IN bit2 mirrors GP9.
    return 0x1 | ((out_value & 0x1) << 1) | ((out_value & 0x2) << 1)


def read_digital_inputs(inputs):
    value = 0
    for bit, pin in enumerate(inputs):
        if pin.value:
            value |= 1 << bit
    return value


def print_result(label, expected, observed):
    ok = expected == observed
    if observed is None:
        observed_text = "timeout"
    else:
        observed_text = "0b%03d" % int(bin(observed)[2:])
    print(label, "expected=0b%03d" % int(bin(expected)[2:]), "observed=%s" % observed_text, "ok=%s" % ok)
    return ok


def run_digitalio_baseline():
    print("DIGITALIO_INTERCONNECT_BASELINE_START")
    outputs = []
    inputs = []
    try:
        for pin in OUT_PINS:
            outputs.append(open_output(pin, False))
        for pin in IN_PINS:
            inputs.append(open_input(pin))

        all_ok = True
        for pattern in (0, 1, 2, 3, 0):
            for bit, dio in enumerate(outputs):
                dio.value = bool(pattern & (1 << bit))
            time.sleep(SETTLE)
            observed = read_digital_inputs(inputs)
            all_ok = print_result("digitalio out=0b%02d" % int(bin(pattern)[2:]), expected_loopback(pattern), observed) and all_ok

        print("DIGITALIO_INTERCONNECT_BASELINE_OK", all_ok)
        return all_ok
    finally:
        deinit_all(inputs)
        deinit_all(outputs)


def make_pio_out_one_pin(pin, value):
    program = adafruit_pioasm.assemble(
        """
.program one_pin_hold
set pins %d
loop:
    jmp loop
"""
        % (1 if value else 0)
    )
    return rp2pio.StateMachine(
        program,
        frequency=10000,
        init=adafruit_pioasm.assemble("set pindirs 1"),
        first_set_pin=pin,
        set_pin_count=1,
        initial_set_pin_state=0,
        initial_set_pin_direction=1,
    )


def run_pio_out_digitalio_in():
    print("PIO_OUT_DIGITALIO_IN_START")
    inputs = []
    held_low = []
    try:
        for pin in IN_PINS:
            inputs.append(open_input(pin))
        all_ok = True

        for out_index, out_pin in enumerate(OUT_PINS):
            for other_index, other_pin in enumerate(OUT_PINS):
                if other_index != out_index:
                    held_low.append(open_output(other_pin, False))

            for value in (0, 1, 0):
                sm = make_pio_out_one_pin(out_pin, value)
                try:
                    time.sleep(SETTLE)
                    out_value = value << out_index
                    observed = read_digital_inputs(inputs)
                    all_ok = print_result("pio-out GP%d=%d digital-in" % (8 + out_index, value), expected_loopback(out_value), observed) and all_ok
                finally:
                    sm.deinit()

            deinit_all(held_low)
            held_low = []

        print("PIO_OUT_DIGITALIO_IN_OK", all_ok)
        return all_ok
    finally:
        deinit_all(held_low)
        deinit_all(inputs)


def make_pio_in_one_pin_sm(pin):
    program = adafruit_pioasm.assemble(
        """
.program in_one_pin
nop [31]
nop [31]
in pins, 1
push block
loop:
    jmp loop
"""
    )
    return rp2pio.StateMachine(
        program,
        frequency=10000,
        first_in_pin=pin,
        in_pin_count=1,
        in_shift_right=True,
        auto_push=False,
    )


def pio_read_one_pin(pin):
    sm = make_pio_in_one_pin_sm(pin)
    try:
        sm.restart()
        raw = read_pio_value(sm)
        if raw is None:
            return None
        return 1 if (raw & 0x80) else 0
    finally:
        sm.deinit()


def read_pio_value(sm):
    deadline = time.monotonic() + PIO_READ_TIMEOUT
    while time.monotonic() < deadline:
        try:
            waiting = sm.in_waiting
        except Exception:
            waiting = 0
        if waiting:
            rx = bytearray(waiting)
            sm.readinto(rx)
            value = 0
            for offset, byte in enumerate(rx):
                value |= byte << (8 * offset)
            print("pio raw waiting=%d value=0x%x" % (waiting, value))
            return value
        time.sleep(0.01)
    return None


def make_pio_out_in_one_pin_sm(out_pin, in_pin, value):
    program = adafruit_pioasm.assemble(
        """
.program out_in_one_pin
set pins %d
nop [31]
nop [31]
in pins, 1
push block
loop:
    jmp loop
"""
        % (1 if value else 0)
    )
    return rp2pio.StateMachine(
        program,
        frequency=10000,
        init=adafruit_pioasm.assemble("set pindirs 1"),
        first_set_pin=out_pin,
        set_pin_count=1,
        first_in_pin=in_pin,
        in_pin_count=1,
        in_shift_right=True,
        auto_push=False,
        initial_set_pin_state=0,
        initial_set_pin_direction=1,
    )


def pio_out_read_one_pin(out_pin, in_pin, value):
    sm = make_pio_out_in_one_pin_sm(out_pin, in_pin, value)
    try:
        sm.restart()
        raw = read_pio_value(sm)
        if raw is None:
            return None
        return 1 if (raw & 0x80) else 0
    finally:
        sm.deinit()


def run_pio_out_pio_in():
    print("PIO_OUT_PIO_IN_ONE_PIN_START")
    all_ok = True

    marker = pio_read_one_pin(board.GP10)
    all_ok = print_result("pio-in marker GP10", 1, marker) and all_ok

    pairs = ((board.GP8, board.GP11, "GP8_to_GP11"), (board.GP9, board.GP12, "GP9_to_GP12"))
    for out_pin, in_pin, name in pairs:
        for value in (0, 1, 0):
            observed = pio_out_read_one_pin(out_pin, in_pin, value)
            all_ok = print_result("pio-out-pio-in %s=%d" % (name, value), value, observed) and all_ok

    print("PIO_OUT_PIO_IN_ONE_PIN_OK", all_ok)
    return all_ok


def main():
    print("PIO_FPGA_INTERCONNECT_LOOPBACK_START")
    gc.collect()
    bitstream, fpga_rst = setup_fpga()
    print("bitstream uploaded", bitstream)

    try:
        digital_ok = run_digitalio_baseline()
        pio_digital_ok = run_pio_out_digitalio_in()
        pio_loop_ok = run_pio_out_pio_in()
        print("SUMMARY digitalio=%s pio_out_digitalio_in=%s pio_out_pio_in=%s" % (digital_ok, pio_digital_ok, pio_loop_ok))
    finally:
        deinit_all([fpga_rst])

    print("PIO_FPGA_COMMS_TEST_DONE")


main()
