import sys
import time

import hardware.default_overlay
import hardware.fpga

try:
    import supervisor
except ImportError:
    supervisor = None


BITSTREAM = "/hackin7/watchdog_koth_board_test/watchdog_koth_smoke.bit"
PAYLOAD = "/hackin7/watchdog_koth_board_test/upload_payload.wdog"

PAYLOAD_BYTE_DELAY = 0.003
BOOT_READ_SECONDS = 2.0
UPLOAD_READ_SECONDS = 10.0
CONSOLE_SECONDS = 60.0


def print_bytes(prefix, data):
    if not data:
        return
    try:
        text = data.decode("utf-8")
    except UnicodeError:
        print("%s%r" % (prefix, data))
        return

    for line in text.splitlines(True):
        if line.endswith("\n"):
            print(prefix + line[:-1])
        else:
            print(prefix + line)


def read_for(uart, seconds, echo_prefix="[RISCV]: "):
    deadline = time.monotonic() + seconds
    data = bytearray()
    while time.monotonic() < deadline:
        chunk = uart.read(64)
        if chunk:
            data.extend(chunk)
            print_bytes(echo_prefix, chunk)
        time.sleep(0.01)
    return bytes(data)


def read_until(uart, needle, seconds, echo_prefix="[RISCV]: "):
    deadline = time.monotonic() + seconds
    data = bytearray()
    while time.monotonic() < deadline:
        chunk = uart.read(64)
        if chunk:
            data.extend(chunk)
            print_bytes(echo_prefix, chunk)
            if needle in data:
                return bytes(data)
        time.sleep(0.01)
    return bytes(data)


def usb_serial_available():
    return supervisor is not None and supervisor.runtime.serial_bytes_available


def read_usb_byte():
    value = sys.stdin.read(1)
    if value == "":
        return None
    return ord(value)


def console_loop(uart, seconds):
    print("[HOST]: console open for %d seconds" % seconds)
    print("[HOST]: bytes from FPGA UART are printed as [RISCV]")
    print("[HOST]: typed USB-serial characters are forwarded to FPGA UART")

    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        chunk = uart.read(64)
        if chunk:
            print_bytes("[RISCV]: ", chunk)

        while usb_serial_available():
            value = read_usb_byte()
            if value is None:
                break
            uart.write(bytes((value,)))

        time.sleep(0.005)


def send_payload(uart, path):
    with open(path, "rb") as payload_file:
        payload = payload_file.read()

    print("[HOST]: sending payload: %s (%d bytes)" % (path, len(payload)))
    for byte_value in payload:
        uart.write(bytes((byte_value,)))
        time.sleep(PAYLOAD_BYTE_DELAY)


def main():
    print("[HOST]: uploading bitstream: %s" % BITSTREAM)
    hardware.fpga.upload_bitstream(BITSTREAM)

    overlay = hardware.default_overlay.Overlay()
    uart = overlay.set_mode_uart()
    try:
        print("[HOST]: reading boot UART")
        read_for(uart, BOOT_READ_SECONDS)

        send_payload(uart, PAYLOAD)

        print("[HOST]: waiting for payload handoff")
        upload_log = read_until(uart, b"RUNNING\n", UPLOAD_READ_SECONDS)
        if b"LOADED\n" not in upload_log or b"RUNNING\n" not in upload_log:
            print("[HOST]: warning: did not see LOADED/RUNNING before console loop")

        console_loop(uart, CONSOLE_SECONDS)
        print("[HOST]: console closed")
    finally:
        uart.deinit()
        overlay.deinit()


main()
