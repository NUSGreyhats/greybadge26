import time

import hardware.default_overlay
import hardware.fpga


BITSTREAM = "/hackin7/watchdog_koth_board_test/greymecha_uart_echo.bit"


def read_exact(uart, length, timeout):
    deadline = time.monotonic() + timeout
    data = bytearray()
    while time.monotonic() < deadline and len(data) < length:
        chunk = uart.read(length - len(data))
        if chunk:
            data.extend(chunk)
        time.sleep(0.01)
    return bytes(data)


def main():
    print("UART_ECHO: uploading", BITSTREAM)
    hardware.fpga.upload_bitstream(BITSTREAM)
    overlay = hardware.default_overlay.Overlay()
    uart = overlay.set_mode_uart()
    try:
        payload = b"WDOG"
        print("UART_ECHO: sending=%r" % payload)
        for byte_value in payload:
            uart.write(bytes((byte_value,)))
            time.sleep(0.02)
        echo = read_exact(uart, len(payload), 3.0)
        print("UART_ECHO: echo=%r" % echo)
        if echo != payload:
            raise AssertionError("UART echo mismatch")
        print("UART_ECHO: OK")
    finally:
        uart.deinit()
        overlay.deinit()


main()
