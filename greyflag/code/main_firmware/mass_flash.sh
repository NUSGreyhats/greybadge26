#!/bin/bash
#
# mass_flash.sh — Greyflag badge provisioning script
#
# For each board (one at a time):
#   1. Detects ESP32-C6 on /dev/ttyACM0
#   2. Flashes full firmware (bootloader + partitions + app + spiffs)
#   3. Burns CTF flag into BLOCK_USR_DATA eFuse (PERMANENT)
#
# Usage: ./mass_flash.sh
#   Optional env overrides:
#     PORT=/dev/ttyACM1 ./mass_flash.sh

set -e

PORT=${PORT:-/dev/ttyACM0}
ESPTOOL="$HOME/.espressif/tools/python/v6.0.1/venv/bin/esptool"
ESPEFUSE="$HOME/.espressif/tools/python/v6.0.1/venv/bin/espefuse"
BUILD="$(dirname "$0")/build"

FLAG_HEX="C0FFEE414141676767DEAD"
FLAG_LEN=11

# ── helpers ────────────────────────────────────────────────────────────────

wait_for_connect() {
    echo ""
    echo "════════════════════════════════════════"
    echo "  Waiting for board on $PORT ..."
    echo "  Plug in the next Greyflag badge."
    echo "════════════════════════════════════════"
    while [ ! -e "$PORT" ]; do sleep 0.5; done
    sleep 1   # let the USB stack settle
    echo "  Device detected."
}

wait_for_disconnect() {
    echo ""
    echo "  Unplug the board to continue to the next one."
    while [ -e "$PORT" ]; do sleep 0.5; done
    echo "  Board removed."
}

flash_firmware() {
    echo ""
    echo "  Flashing firmware..."
    "$ESPTOOL" --chip esp32c6 --port "$PORT" --baud 460800 \
        --before default-reset --after hard-reset \
        write_flash \
        --flash-mode dio --flash-size 4MB --flash-freq 80m \
        0x0      "$BUILD/bootloader/bootloader.bin" \
        0x8000   "$BUILD/partition_table/partition-table.bin" \
        0x10000  "$BUILD/greyflag_badge.bin" \
        0x210000 "$BUILD/storage.bin"
    echo "  Firmware flashed."
}

burn_efuse() {
    echo ""
    echo "  Burning eFuse (PERMANENT)..."

    python3 - "$FLAG_HEX" > /tmp/ctf_payload.bin <<'PYEOF'
import sys
flag_bytes = bytes.fromhex(sys.argv[1])
payload = bytearray(32)
payload[0:len(flag_bytes)] = flag_bytes
sys.stdout.buffer.write(payload)
PYEOF

    "$ESPEFUSE" --chip esp32c6 --port "$PORT" --do-not-confirm \
        burn-block-data BLOCK_USR_DATA /tmp/ctf_payload.bin

    rm /tmp/ctf_payload.bin
    echo "  eFuse burned: 0x${FLAG_HEX}"
}

# ── main loop ──────────────────────────────────────────────────────────────

BOARD=0

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   GREYFLAG MASS FLASH SCRIPT         ║"
echo "║   Ctrl+C to stop                     ║"
echo "╚══════════════════════════════════════╝"

while true; do
    BOARD=$((BOARD + 1))
    wait_for_connect

    echo ""
    echo "  ── Board #$BOARD ──"

    flash_firmware
    burn_efuse

    echo ""
    echo "  ✓ Board #$BOARD done — flag: grey{0x${FLAG_HEX}}"
    wait_for_disconnect
done
