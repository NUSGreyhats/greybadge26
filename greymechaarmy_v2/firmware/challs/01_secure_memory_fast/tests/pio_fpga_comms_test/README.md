# PIO to FPGA comms scratch test

This test builds a temporary FPGA bitstream that mirrors `interconnect[4:0]`
onto `pmod_j2[4:0]` and drives `pmod_j2[7:5]` to `3'b101`.

Build the bitstream from `tests/pio_fpga_comms_test/fpga`:

```sh
make
```

The build writes `fpga/pio_fpga_comms.bit` and also copies it to
`payloads/pio_fpga_comms.bit` so the harness can upload the payload directory
to `/tmp`.

Run on the badge with the payload directory so `/tmp/pio_fpga_comms.bit` is
available:

```sh
python harness\tools\badge_harness.py --src tests\pio_fpga_comms_test\payloads --port COM17 --timeout 90 --settle 2 --done-marker PIO_FPGA_COMMS_TEST_DONE
```

`--serial-only` can run only `run.py`; it will work only if
`pio_fpga_comms.bit` already exists on the badge in `/tmp` or
`/hardware/bitstreams`.
