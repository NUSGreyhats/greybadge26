import importlib.util
import unittest
from pathlib import Path


def load_payload_symbols():
    path = Path(__file__).resolve().parents[1] / "payloads" / "fast_secure_memory" / "run.py"
    source = path.read_text(encoding="utf-8")
    keep = []
    for line in source.splitlines():
        if line == "solve()":
            break
        if line.startswith("import ") or line.startswith("from "):
            continue
        keep.append(line)
    namespace = {}
    exec("\n".join(keep), namespace)
    return namespace


class FastSecureMemoryDecodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ns = load_payload_symbols()

    def test_raw_to_known_byte_mapping_without_gp16(self):
        raw_to_known_byte = self.ns["raw_to_known_byte"]

        # Character "f" is 0b0110_0110. With bit1 missing, the known bits
        # reconstruct as 0b0110_0100.
        raw = 0
        raw |= 0 << 5  # bit0 on GP27
        raw |= 1 << 1  # bit2 on GP23
        raw |= 0 << 3  # bit3 on GP25
        raw |= 0 << 4  # bit4 on GP26
        raw |= 1 << 6  # bit5 on GP28
        raw |= 1 << 0  # bit6 on GP22
        raw |= 0 << 2  # bit7 on GP24

        self.assertEqual(ord("f") & ~0x02, raw_to_known_byte(raw))

    def test_candidates_restore_missing_bit(self):
        candidates_for_known = self.ns["candidates_for_known"]

        self.assertEqual((ord("d"), ord("f")), candidates_for_known(ord("f") & ~0x02))


if __name__ == "__main__":
    unittest.main()
