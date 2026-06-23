#!/usr/bin/env python3
"""Upload files to CircuitPython and run /tmp/run.py with REPL prompt sync."""

import argparse
import ctypes
import os
import shutil
import sys
import time
from pathlib import Path


RUN_COMMAND = 'exec(open("/tmp/run.py").read(), {"__name__": "__main__"})'


class HarnessError(RuntimeError):
    pass


def windows_volume_label(root):
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


def find_circuitpy_drive():
    candidates = []
    if os.name == "nt":
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            root = f"{letter}:\\"
            if os.path.isdir(root) and windows_volume_label(root) == "CIRCUITPY":
                candidates.append(Path(root))
    else:
        for root in (Path("/Volumes"), Path("/media"), Path("/run/media"), Path("/mnt")):
            if root.exists():
                candidates.extend(p for p in root.rglob("CIRCUITPY") if p.is_dir())

    if not candidates:
        raise HarnessError("Could not find a mounted CIRCUITPY drive. Pass --drive explicitly.")
    if len(candidates) > 1:
        raise HarnessError("Found multiple CIRCUITPY drives. Pass --drive explicitly.")
    return candidates[0]


def copy_to_tmp(src, drive):
    src = src.resolve()
    drive = drive.resolve()
    tmp = drive / "tmp"
    if not src.exists():
        raise HarnessError(f"Source path does not exist: {src}")
    if not drive.exists():
        raise HarnessError(f"Badge drive does not exist: {drive}")

    tmp.mkdir(exist_ok=True)
    uploaded = []
    if src.is_file():
        dest = tmp / "run.py"
        shutil.copy2(src, dest)
        uploaded.append(dest)
    elif src.is_dir():
        if not (src / "run.py").is_file():
            raise HarnessError(f"Directory upload requires run.py: {src / 'run.py'}")
        for file_path in src.rglob("*"):
            if file_path.is_file():
                dest = tmp / file_path.relative_to(src)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dest)
                uploaded.append(dest)
    else:
        raise HarnessError(f"Source path is not a file or directory: {src}")

    if hasattr(os, "sync"):
        os.sync()
    return uploaded


def drain(ser, duration=0.25):
    end = time.monotonic() + duration
    data = bytearray()
    while time.monotonic() < end:
        waiting = ser.in_waiting
        if waiting:
            data.extend(ser.read(waiting))
            end = time.monotonic() + duration
        else:
            time.sleep(0.02)
    return bytes(data)


def wait_for_prompt(ser, timeout=5.0):
    end = time.monotonic() + timeout
    data = bytearray()
    while time.monotonic() < end:
        waiting = ser.in_waiting
        chunk = ser.read(waiting or 1)
        if chunk:
            data.extend(chunk)
            sys.stdout.buffer.write(chunk)
            sys.stdout.buffer.flush()
            if b">>>" in data[-128:]:
                return True
        else:
            time.sleep(0.02)
    return False


def stream(ser, timeout):
    end = time.monotonic() + timeout
    saw_traceback = False
    while time.monotonic() < end:
        chunk = ser.read(ser.in_waiting or 1)
        if chunk:
            text = chunk.decode("utf-8", errors="replace")
            if "Traceback (most recent call last):" in text:
                saw_traceback = True
            sys.stdout.buffer.write(chunk)
            sys.stdout.buffer.flush()
            end = time.monotonic() + timeout
        else:
            time.sleep(0.02)
    return 1 if saw_traceback else 0


def run_on_badge(port, timeout, settle):
    try:
        import serial
    except ImportError as exc:
        raise HarnessError("pyserial is required") from exc

    with serial.Serial(port, baudrate=115200, timeout=0.1, write_timeout=2) as ser:
        time.sleep(settle)
        drain(ser, 0.5)
        ser.write(b"\x03\x03\r\n")
        ser.flush()
        if not wait_for_prompt(ser, 5.0):
            drain(ser, 0.5)
            ser.write(b"\r\n")
            ser.flush()
            if not wait_for_prompt(ser, 2.0):
                raise HarnessError("CircuitPython REPL prompt did not appear")

        ser.write(("\r\n" + RUN_COMMAND + "\r\n").encode("utf-8"))
        ser.flush()
        return stream(ser, timeout)


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--src", required=True, type=Path)
    parser.add_argument("--drive", type=Path)
    parser.add_argument("--port", required=True)
    parser.add_argument("--no-run", action="store_true")
    parser.add_argument("--timeout", type=float, default=2.0)
    parser.add_argument("--settle", type=float, default=3.0)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    try:
        drive = args.drive.resolve() if args.drive else find_circuitpy_drive()
        uploaded = copy_to_tmp(args.src, drive)
        print(f"Uploaded {len(uploaded)} file(s) to {drive / 'tmp'}", flush=True)
        if args.no_run:
            return 0
        print(f"Running /tmp/run.py on {args.port}", flush=True)
        return run_on_badge(args.port, args.timeout, args.settle)
    except HarnessError as exc:
        print(f"error: {exc}", file=sys.stderr)
        print(f"manual REPL command: {RUN_COMMAND}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
