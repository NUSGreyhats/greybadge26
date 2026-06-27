from pathlib import Path
import importlib.util
import unittest


ROOT = Path(__file__).resolve().parents[4]
AUTORUN_PATH = (
    ROOT
    / "rp2350"
    / "filesystem"
    / "challs"
    / "watchdog_oled"
    / "autorun.py"
)


def load_autorun():
    spec = importlib.util.spec_from_file_location("watchdog_oled_autorun", AUTORUN_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WatchdogOledAutorunTests(unittest.TestCase):
    def test_pack_autorun_marker_round_trips_paths(self):
        autorun = load_autorun()
        bitstream = "/challs/watchdog_oled/watchdog_koth_oled.bit"
        payload = "/challs/watchdog_oled/payload.wdog"

        packet = autorun.pack_autorun_marker(bitstream, payload)

        self.assertEqual(packet[0], autorun.NVM_MAGIC)
        self.assertEqual(autorun.unpack_autorun_marker(packet), (bitstream, payload))

    def test_pack_autorun_marker_rejects_oversized_paths(self):
        autorun = load_autorun()
        long_path = "/" + ("x" * 260)

        with self.assertRaisesRegex(ValueError, "too long"):
            autorun.pack_autorun_marker(
                long_path,
                "/challs/watchdog_oled/payload.wdog",
            )


if __name__ == "__main__":
    unittest.main()
