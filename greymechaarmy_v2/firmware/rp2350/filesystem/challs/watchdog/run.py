import time

import hardware.default_overlay
import hardware.fpga


BITSTREAM = "/challs/watchdog/watchdog_koth_smoke.bit"
PAYLOAD = "/challs/watchdog/payload.wdog" # Change to your own payload 


def print_uart(data):
    if not data:
        return
    try:
        text = data.decode("utf-8")
    except UnicodeError:
        print("[UART]: %r" % data)
        return

    for line in text.splitlines(True):
        if line.endswith("\n"):
            print("[UART]: " + line[:-1])
        else:
            print("[UART]: " + line)


def read_until(uart, needle, timeout):
    deadline = time.monotonic() + timeout
    window = bytearray()
    while time.monotonic() < deadline:
        chunk = uart.read(64)
        if chunk:
            window.extend(chunk)
            print_uart(chunk)
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
            print_uart(chunk)
        time.sleep(0.01)
    return bytes(data)


def print_forever(uart):
    print("WDOG_UPLOAD: UART_PRINT_FOREVER")
    while True:
        chunk = uart.read(64)
        if chunk:
            print_uart(chunk)
        time.sleep(0.01)


def main():
    print("WDOG_UPLOAD: uploading", BITSTREAM)
    hardware.fpga.upload_bitstream(BITSTREAM)
    overlay = hardware.default_overlay.Overlay()
    uart = overlay.set_mode_uart()
    try:
        boot_log = read_for(uart, 2.0)
        print("WDOG_UPLOAD: boot_log=%r" % boot_log)

        with open(PAYLOAD, "rb") as payload_file:
            payload = payload_file.read()
        print("WDOG_UPLOAD: sending_payload=%d bytes" % len(payload))
        for byte_value in payload:
            uart.write(bytes((byte_value,)))
            time.sleep(0.003)

        upload_log = read_until(uart, b"RUNNING\n", 10.0)
        print("WDOG_UPLOAD: upload_log=%r" % upload_log)
        if b"LOADED\n" not in upload_log or b"RUNNING\n" not in upload_log:
            raise AssertionError("payload upload did not reach LOADED/RUNNING")

        print("WDOG_UPLOAD: UART_UPLOAD_OK")
        print_forever(uart)
    finally:
        uart.deinit()
        overlay.deinit()


main()
