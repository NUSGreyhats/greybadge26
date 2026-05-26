# CircuitPython test harness for the FPGA upload path.
# Run on the badge REPL: from hardware.fpga.test_upload import run_all; run_all()

import time
import board, digitalio
from hardware.fpga import jtag


MAIN_BIT = "/hardware/bitstreams/main.bit"
PROBE_BIT = "/hardware/fpga/test_bitstreams/probe.bit"
EXPECTED_IDCODE = 0x41111043  # ECP5 LFE5U-25F (actual badge device; plan said 45F but device reports 25F).


def test_idcode():
    code = jtag.idcode()
    assert code == EXPECTED_IDCODE, "idcode mismatch: got 0x%08X, expected 0x%08X" % (code, EXPECTED_IDCODE)
    print("T1 idcode: 0x%08X OK" % code)


def _read_interconnect():
    pins = [digitalio.DigitalInOut(p) for p in (
        board.GP8, board.GP9, board.GP10, board.GP11,
        board.GP12, board.GP13, board.GP14, board.GP15)]
    try:
        for p in pins:
            p.switch_to_input(pull=None)
        # Settle a moment for input synchroniser
        time.sleep(0.001)
        v = 0
        for i, p in enumerate(pins):
            if p.value:
                v |= (1 << i)
        return v
    finally:
        for p in pins:
            p.deinit()


def test_status_via_main_bit():
    from hardware import fpga
    fpga.upload_bitstream(MAIN_BIT)
    print("T2 status via main.bit: prog_close returned (status check inside)")


def test_timing(path=MAIN_BIT, iterations=3):
    from hardware import fpga
    times_ms = []
    for i in range(iterations):
        t0 = time.monotonic_ns()
        fpga.upload_bitstream(path)
        elapsed = (time.monotonic_ns() - t0) // 1_000_000
        times_ms.append(elapsed)
        print("T4 iter %d: %d ms" % (i, elapsed))
        time.sleep(1)
    times_ms.sort()
    median = times_ms[len(times_ms) // 2]
    print("T4 min/median/max: %d / %d / %d ms" % (times_ms[0], median, times_ms[-1]))
    return times_ms


def test_probe_loopback():
    from hardware import fpga
    fpga.upload_bitstream(PROBE_BIT)
    time.sleep(0.05)
    sample_a = _read_interconnect()
    time.sleep(0.6)
    sample_b = _read_interconnect()
    # Upper 7 bits = 0xA4 (toggle on bit 0, static on bits 1..7).
    assert (sample_a & 0xFE) == 0xA4, "T3' static bits wrong: 0x%02X" % sample_a
    assert (sample_b & 0xFE) == 0xA4, "T3' static bits wrong: 0x%02X" % sample_b
    assert (sample_a & 0x01) != (sample_b & 0x01), \
        "T3' toggle bit did not change: a=0x%02X b=0x%02X" % (sample_a, sample_b)
    print("T3' probe loopback: a=0x%02X b=0x%02X OK" % (sample_a, sample_b))


def test_reupload():
    from hardware import fpga
    fpga.upload_bitstream(MAIN_BIT)
    fpga.upload_bitstream(MAIN_BIT)
    print("T5 re-upload: two consecutive uploads OK")


def test_exception_cleanup():
    from hardware import fpga
    try:
        fpga.upload_bitstream("/nonexistent.bit")
    except Exception as e:
        print("T6 expected exception: %r" % e)
    # idcode() must work after the failed upload
    code = jtag.idcode()
    assert code == EXPECTED_IDCODE, "T6 idcode after failed upload mismatch: 0x%08X" % code
    print("T6 exception cleanup: idcode still 0x%08X OK" % code)


def run_baseline():
    """Tests runnable before probe.bit exists."""
    test_idcode()
    test_status_via_main_bit()
    test_timing()


def run_all():
    test_idcode()
    test_status_via_main_bit()
    test_probe_loopback()
    test_timing()
    test_reupload()
    test_exception_cleanup()
    print("ALL TESTS PASSED")
