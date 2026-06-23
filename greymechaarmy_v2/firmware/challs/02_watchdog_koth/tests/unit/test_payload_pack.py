import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "payload"))

from pack_wdog import pack_payload


def test_pack_payload_header_and_length():
    packed = pack_payload(b"\x13\x00\x00\x00")
    assert packed[:4] == b"WDOG"
    assert packed[4:8] == (4).to_bytes(4, "little")
    assert packed[8:] == b"\x13\x00\x00\x00"


def test_pack_payload_rejects_empty_payload():
    try:
        pack_payload(b"")
    except ValueError as exc:
        assert "must not be empty" in str(exc)
    else:
        raise AssertionError("empty payload should be rejected")


def test_pack_payload_rejects_oversized_payload():
    try:
        pack_payload(b"A" * (0x4000 + 1))
    except ValueError as exc:
        assert "exceeds" in str(exc)
    else:
        raise AssertionError("oversized payload should be rejected")
