# Badge Harness

Upload a local script or script directory to a connected GreyMecha Army badge and run it as `/tmp/run.py` on the badge's CircuitPython interpreter.

Upload and run a single file:

```powershell
python tools\badge_harness.py --src .\run.py --drive E:\ --port COM7
```

Upload a directory that contains `run.py` and helper modules:

```powershell
python tools\badge_harness.py --src .\payload --drive E:\ --port COM7
```

Upload without running:

```powershell
python tools\badge_harness.py --src .\run.py --drive E:\ --no-run
```

Run a single Python file over serial without writing to `CIRCUITPY`, useful when the badge mass-storage volume is write-protected:

```powershell
python tools\badge_harness.py --src .\run.py --port COM7 --serial-only
```

If the badge is still rebooting after a file copy, the harness waits briefly before interrupting the serial REPL. Adjust that delay with `--settle`.

If `--drive` is omitted, the harness tries to find a mounted drive named `CIRCUITPY`. If `--port` is omitted, it tries to find a likely CircuitPython USB serial port. Serial execution requires `pyserial`:

```powershell
python -m pip install pyserial
```
