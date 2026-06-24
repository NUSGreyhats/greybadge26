#!/usr/bin/env python3
import argparse
from pathlib import Path

MAGIC = b"WDOG"
MAX_PAYLOAD_SIZE = 0x4000


def pack_payload(payload: bytes) -> bytes:
    if not payload:
        raise ValueError("payload must not be empty")
    if len(payload) > MAX_PAYLOAD_SIZE:
        raise ValueError("payload exceeds 16 KiB payload region")
    return MAGIC + len(payload).to_bytes(4, "little") + payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Pack a raw payload into the WDOG UART upload format.")
    parser.add_argument("input", type=Path, help="raw payload binary")
    parser.add_argument("output", type=Path, help="output .wdog file")
    args = parser.parse_args()

    args.output.write_bytes(pack_payload(args.input.read_bytes()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
