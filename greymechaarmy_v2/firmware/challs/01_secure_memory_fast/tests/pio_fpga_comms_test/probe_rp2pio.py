import rp2pio

print("StateMachine attrs")
print([name for name in dir(rp2pio.StateMachine) if "read" in name.lower() or "waiting" in name.lower() or "count" in name.lower()])
print("RP2PIO_PROBE_DONE")
