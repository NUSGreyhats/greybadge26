import time

import board
import digitalio
import hardware.fpga


BITSTREAM = "/hackin7/watchdog_koth_board_test/watchdog_koth_smoke.bit"
INTERCONNECT_PINS = (
    board.GP8,
    board.GP9,
    board.GP10,
    board.GP11,
    board.GP12,
    board.GP13,
    board.GP14,
    board.GP15,
)


def read_interconnect():
    pins = [digitalio.DigitalInOut(pin) for pin in INTERCONNECT_PINS]
    try:
        for pin in pins:
            pin.switch_to_input(pull=None)
        time.sleep(0.05)

        value = 0
        for index, pin in enumerate(pins):
            if pin.value:
                value |= 1 << index
        return value
    finally:
        for pin in pins:
            pin.deinit()


def main():
    print("WDOG_SMOKE: uploading", BITSTREAM)
    hardware.fpga.upload_bitstream(BITSTREAM)

    last = 0
    for index in range(10):
        time.sleep(0.2)
        last = read_interconnect()
        print("WDOG_SMOKE: sample[%d]=0x%02X" % (index, last))

    print("WDOG_SMOKE: interconnect_value=0x%02X led_upper=0x%02X" % (last, last & 0xFC))

    if (last & 0xFC) != 0xA4:
        raise AssertionError("expected LED self-test upper bits 0xA4, got 0x%02X" % (last & 0xFC))
    print("WDOG_SMOKE: LED_SELFTEST_OK")


main()
