#!/usr/bin/env python3
"""Upload files to a CircuitPython GreyMecha Army badge and run /tmp/run.py."""

import argparse
import ctypes
import os
import shutil
import sys
import time
from pathlib import Path
from typing import List, Optional


RUN_COMMAND = 'exec(open("/tmp/run.py").read(), {"__name__": "__main__"})'


class HarnessError(RuntimeError):
    pass


def find_circuitpy_drive() -> Path:
    candidates = []  # type: List[Path]

    if os.name == "nt":
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            root = f"{letter}:\\"
            if os.path.isdir(root) and _windows_volume_label(root) == "CIRCUITPY":
                candidates.append(Path(root))
    else:
        roots = [Path("/Volumes"), Path("/media"), Path("/run/media"), Path("/mnt")]
        for root in roots:
            if root.exists():
                candidates.extend(p for p in root.rglob("CIRCUITPY") if p.is_dir())

    if not candidates:
        raise HarnessError("Could not find a mounted CIRCUITPY drive. Pass --drive explicitly.")
    if len(candidates) > 1:
        found = ", ".join(str(p) for p in candidates)
        raise HarnessError(f"Found multiple CIRCUITPY drives ({found}). Pass --drive explicitly.")
    return candidates[0]


def _windows_volume_label(root: str) -> Optional[str]:
    label = ctypes.create_unicode_buffer(261)
    fs_name = ctypes.create_unicode_buffer(261)
    serial = ctypes.c_uint32()
    max_component = ctypes.c_uint32()
    flags = ctypes.c_uint32()
    ok = ctypes.windll.kernel32.GetVolumeInformationW(
        ctypes.c_wchar_p(root),
        label,
        len(label),
        ctypes.byref(serial),
        ctypes.byref(max_component),
        ctypes.byref(flags),
        fs_name,
        len(fs_name),
    )
    return label.value if ok else None


def upload_to_tmp(src: Path, drive: Path) -> List[Path]:
    src = src.resolve()
    drive = drive.resolve()
    tmp = drive / "tmp"

    if not src.exists():
        raise HarnessError(f"Source path does not exist: {src}")
    if not drive.exists():
        raise HarnessError(f"Badge drive does not exist: {drive}")

    tmp.mkdir(exist_ok=True)
    uploaded = []  # type: List[Path]

    if src.is_file():
        dest = tmp / "run.py"
        _copy_file(src, dest)
        uploaded.append(dest)
    elif src.is_dir():
        run_py = src / "run.py"
        if not run_py.is_file():
            raise HarnessError(f"Directory upload requires a run.py entrypoint: {run_py}")
        for file_path in src.rglob("*"):
            if file_path.is_file():
                rel = file_path.relative_to(src)
                dest = tmp / rel
                _copy_file(file_path, dest)
                uploaded.append(dest)
    else:
        raise HarnessError(f"Source path is not a file or directory: {src}")

    _sync_best_effort()
    return uploaded


def _copy_file(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def _sync_best_effort() -> None:
    if hasattr(os, "sync"):
        os.sync()


def find_circuitpython_port() -> str:
    try:
        from serial.tools import list_ports
    except ImportError as exc:
        raise HarnessError("pyserial is required to auto-detect or use --port. Install it with: python -m pip install pyserial") from exc

    ports = list(list_ports.comports())
    preferred_terms = ("circuitpython", "rp2350", "raspberry pi pico", "usb serial device", "cdc")
    matches = [
        p.device
        for p in ports
        if any(term in " ".join(str(v).lower() for v in (p.description, p.manufacturer, p.product, p.hwid)) for term in preferred_terms)
    ]

    if len(matches) == 1:
        return matches[0]
    if not matches and len(ports) == 1:
        return ports[0].device
    if not matches:
        raise HarnessError("Could not find a CircuitPython serial port. Pass --port explicitly.")

    found = ", ".join(matches)
    raise HarnessError(f"Found multiple possible serial ports ({found}). Pass --port explicitly.")


def run_on_badge(port: str, timeout: float, settle: float, done_marker: Optional[str]) -> int:
    try:
        import serial
    except ImportError as exc:
        raise HarnessError("pyserial is required to run code over serial. Install it with: python -m pip install pyserial") from exc

    try:
        with serial.Serial(port, baudrate=115200, timeout=0.1, write_timeout=10) as ser:
            time.sleep(settle)
            _drain_serial(ser)
            ser.write(b"\x03\x03")
            ser.flush()
            time.sleep(0.5)
            _drain_serial(ser)

            ser.write(("\r\n" + RUN_COMMAND + "\r\n").encode("utf-8"))
            ser.flush()
            return _stream_serial(ser, timeout, done_marker)
    except serial.SerialException as exc:
        raise HarnessError(f"Serial communication failed on {port}: {exc}") from exc


def run_text_on_badge(port: str, timeout: float, settle: float, source: str, done_marker: Optional[str]) -> int:
    try:
        import serial
    except ImportError as exc:
        raise HarnessError("pyserial is required to run code over serial. Install it with: python -m pip install pyserial") from exc

    source = source.replace("\r\n", "\n").replace("\r", "\n")
    if not source.endswith("\n"):
        source += "\n"
    try:
        with serial.Serial(port, baudrate=115200, timeout=0.1, write_timeout=10) as ser:
            time.sleep(settle)
            _drain_serial(ser)
            ser.write(b"\x02")
            ser.flush()
            time.sleep(0.2)
            _drain_serial(ser)
            ser.write(b"\x03\x03")
            ser.flush()
            time.sleep(0.5)
            _drain_serial(ser)
            ser.write(b"\x01")
            ser.flush()
            time.sleep(0.2)
            _drain_serial(ser)
            _write_serial_chunks(ser, source.encode("utf-8"))
            time.sleep(0.3)
            ser.write(b"\x04")
            ser.flush()
            status = _stream_serial(ser, timeout, done_marker)
            try:
                ser.write(b"\x02")
                ser.flush()
            except Exception:
                pass
            return status
    except serial.SerialException as exc:
        raise HarnessError(f"Serial communication failed on {port}: {exc}") from exc


def _write_serial_chunks(ser, data: bytes, chunk_size: int = 64) -> None:
    for offset in range(0, len(data), chunk_size):
        ser.write(data[offset : offset + chunk_size])
        ser.flush()
        time.sleep(0.02)


def _drain_serial(ser) -> None:
    deadline = time.monotonic() + 0.5
    while time.monotonic() < deadline:
        if ser.in_waiting:
            ser.read(ser.in_waiting)
        else:
            time.sleep(0.05)


def _stream_serial(ser, timeout: float, done_marker: Optional[str]) -> int:
    deadline = time.monotonic() + timeout
    saw_traceback = False
    seen = ""

    while time.monotonic() < deadline:
        try:
            chunk = ser.read(ser.in_waiting or 1)
        except Exception as exc:
            raise HarnessError(f"Serial read failed while waiting for badge output: {exc}") from exc
        if chunk:
            text = chunk.decode("utf-8", errors="replace")
            if "Traceback (most recent call last):" in text:
                saw_traceback = True
            seen = (seen + text)[-512:]
            sys.stdout.buffer.write(chunk)
            sys.stdout.buffer.flush()
            if done_marker and done_marker in seen:
                return 1 if saw_traceback else 0
            deadline = time.monotonic() + timeout
        else:
            time.sleep(0.02)

    return 1 if saw_traceback else 0


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--src", required=True, type=Path, help="File or directory to upload. A single file is copied as /tmp/run.py.")
    parser.add_argument("--drive", type=Path, help="Mounted CIRCUITPY drive path, for example E:\\.")
    parser.add_argument("--port", help="CircuitPython USB serial port, for example COM7.")
    parser.add_argument("--no-run", action="store_true", help="Upload files but do not run /tmp/run.py.")
    parser.add_argument("--serial-only", action="store_true", help="Run a single source file through serial without writing to CIRCUITPY.")
    parser.add_argument("--timeout", type=float, default=2.0, help="Seconds to wait for additional serial output before exiting.")
    parser.add_argument("--settle", type=float, default=3.0, help="Seconds to wait after opening serial before interrupting the badge.")
    parser.add_argument("--done-marker", help="Stop reading serial output as soon as this marker appears.")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    try:
        if args.serial_only:
            if args.src.is_dir():
                raise HarnessError("--serial-only requires --src to be a single Python file.")
            port = args.port or find_circuitpython_port()
            source = args.src.read_text(encoding="utf-8")
            print(f"Running {args.src} on {port} without filesystem upload", flush=True)
            return run_text_on_badge(port, args.timeout, args.settle, source, args.done_marker)

        drive = args.drive.resolve() if args.drive else find_circuitpy_drive()
        uploaded = upload_to_tmp(args.src, drive)
        print(f"Uploaded {len(uploaded)} file(s) to {drive / 'tmp'}", flush=True)

        if args.no_run:
            return 0

        port = args.port or find_circuitpython_port()
        print(f"Running /tmp/run.py on {port}", flush=True)
        return run_on_badge(port, args.timeout, args.settle, args.done_marker)
    except HarnessError as exc:
        print(f"error: {exc}", file=sys.stderr)
        if "drive" in locals():
            print(f"badge drive: {drive}", file=sys.stderr)
        if "port" in locals():
            print(f"serial port: {port}", file=sys.stderr)
        print(f"manual REPL command: {RUN_COMMAND}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
