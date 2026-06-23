# Fast Secure Memory Payload

This payload attacks the registered-memory/live-address gate in `fast_secure_memory`.

`GP16` is currently not connected, so PMOD bit 1 cannot be sampled directly. The script prints byte candidates as `bit1=0/bit1=1` pairs and chooses printable flag-looking bytes for the `BEST` line.

Run it through the harness:

```powershell
python harness\tools\badge_harness.py --src harness\payloads\fast_secure_memory --drive D:\ --port COM17 --timeout 30 --settle 3
```

If `main.bit` is copied into this directory before upload, the payload programs it from `/tmp/main.bit`. Otherwise it uses the FPGA bitstream already loaded on the badge.
