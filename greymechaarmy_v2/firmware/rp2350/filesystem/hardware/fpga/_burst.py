# Selects the burst driver implementation. Phase B's native module (when
# present) is preferred; otherwise Phase A's pure-Python rp2pio driver is used.

try:
    import _burst_native            # provided by a custom CircuitPython UF2 (Phase B)
    BurstDriver = _burst_native.BurstDriverNative
    print("fpga: using native burst driver (Phase B)")
except ImportError:
    from .burst_pio import BurstDriverPIO as BurstDriver
    print("fpga: using rp2pio burst driver (Phase A)")
