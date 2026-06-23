import time

import hardware.default_overlay
import hardware.fpga


BITSTREAM = "/hackin7/watchdog_koth_board_test/watchdog_koth_smoke.bit"
PAYLOAD = "/hackin7/watchdog_koth_board_test/led_counter.wdog"


def read_until(uart, needle, timeout):
    deadline = time.monotonic() + timeout
    window = bytearray()
    while time.monotonic() < deadline:
        chunk = uart.read(64)
        if chunk:
            window.extend(chunk)
            if needle in window:
                return bytes(window)
        time.sleep(0.01)
    return bytes(window)


def read_for(uart, timeout):
    deadline = time.monotonic() + timeout
    data = bytearray()
    while time.monotonic() < deadline:
        chunk = uart.read(64)
        if chunk:
            data.extend(chunk)
        time.sleep(0.01)
    return bytes(data)


def main():
    print("WDOG_LED_COUNTER: uploading", BITSTREAM)
    hardware.fpga.upload_bitstream(BITSTREAM)
    overlay = hardware.default_overlay.Overlay()
    uart = overlay.set_mode_uart()
    try:
        boot_log = read_for(uart, 2.0)
        print("WDOG_LED_COUNTER: boot_log=%r" % boot_log)

        with open(PAYLOAD, "rb") as payload_file:
            payload = payload_file.read()
        print("WDOG_LED_COUNTER: sending_payload=%d bytes" % len(payload))
        for byte_value in payload:
            uart.write(bytes((byte_value,)))
            time.sleep(0.003)

        upload_log = read_until(uart, b"RUNNING\n", 10.0)
        print("WDOG_LED_COUNTER: upload_log=%r" % upload_log)
        if b"LOADED\n" not in upload_log or b"RUNNING\n" not in upload_log:
            raise AssertionError("LED counter payload did not reach LOADED/RUNNING")

        print("WDOG_LED_COUNTER: UART_UPLOAD_OK")
    finally:
        uart.deinit()
        overlay.deinit()


main()
