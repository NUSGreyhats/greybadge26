#!/usr/bin/env python3
import re
from pathlib import Path

CONFIG = Path(__file__).resolve().parent.parent / "main.config"
current = None
for line in CONFIG.read_text().splitlines():
    if line.startswith(".tile "):
        current = line
    if "OUTPUT" in line and current:
        print(current)
        print(line)
