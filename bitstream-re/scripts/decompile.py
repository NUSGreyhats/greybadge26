#!/usr/bin/env python3
"""Decompile main.config to gate-level Verilog using VoidMercy ECP5 decompiler."""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECOMPILER = Path.home() / "Lattice-ECP5-Bitstream-Decompiler"
CONFIG = ROOT / "main.config"
OUT = ROOT / "verilog" / "main_decomp.v"


def load_ecp5_class():
    """Load ECP5 without executing Decompiler.py's example block at import time."""
    path = DECOMPILER / "Decompiler.py"
    source = path.read_text()
    # Strip the self-test that runs on import.
    marker = 'os.system("ecpunpack example/counter.bit'
    if marker in source:
        source = source[: source.index(marker)]
    spec = importlib.util.spec_from_loader("ecp5_decompiler", loader=None)
    module = importlib.util.module_from_spec(spec)
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module.ECP5


def main():
    import os

    os.chdir(DECOMPILER)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    ECP5 = load_ecp5_class()
    ecp5 = ECP5(str(CONFIG))
    ecp5.write_code(str(OUT))
    print(f"Decompiled -> {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
