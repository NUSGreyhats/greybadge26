#!/bin/bash
#
# Burn CTF flag into BLOCK_USR_DATA (BLK3) eFuse on ESP32-C6.
# Flag value: C0FFEE414141676767DEAD (11 bytes, stored as raw hex).
# Participants are told to wrap it as grey{0x<value>}.
#
# Usage: ./burn_ctf.sh [port] [bit_offset]
#   port        Serial port (default: /dev/ttyACM0)
#   bit_offset  Bit offset within BLK3 where flag starts (default: 0)
#
# WARNING: eFuse burns are PERMANENT.

set -e

PORT=${1:-/dev/ttyACM0}
OFFSET_BITS=${2:-0}

# 11-byte flag: C0 FF EE 41 41 41 67 67 67 DE AD
FLAG_HEX="C0FFEE414141676767DEAD"
FLAG_LEN=11

echo "════════════════════════════════════════"
echo "  CTF EFUSE BURNER — ESP32-C6"
echo "════════════════════════════════════════"
echo "  Port       : $PORT"
echo "  Block      : BLOCK_USR_DATA (BLK3)"
echo "  Bit offset : $OFFSET_BITS"
echo "  Value      : 0x${FLAG_HEX}  (${FLAG_LEN} bytes)"
echo "════════════════════════════════════════"
echo ""
echo "⚠️  Efuses are PERMANENT (bits only go 0→1). Burning now..."
echo ""

python3 - "$OFFSET_BITS" "$FLAG_HEX" > /tmp/ctf_payload.bin <<'PYEOF'
import sys
offset_bits = int(sys.argv[1])
flag_hex    = sys.argv[2]

if offset_bits % 8 != 0:
    print("ERROR: offset must be byte-aligned", file=sys.stderr)
    sys.exit(1)

byte_offset = offset_bits // 8
flag_bytes  = bytes.fromhex(flag_hex)

if byte_offset + len(flag_bytes) > 32:
    print(f"ERROR: flag overflows BLK3 (32 B)", file=sys.stderr)
    sys.exit(1)

payload = bytearray(32)
payload[byte_offset : byte_offset + len(flag_bytes)] = flag_bytes
sys.stdout.buffer.write(payload)
PYEOF

espefuse --chip esp32c6 --port "$PORT" --do-not-confirm \
    burn-block-data BLOCK_USR_DATA /tmp/ctf_payload.bin

rm /tmp/ctf_payload.bin
echo ""
echo "✅ Burned 0x${FLAG_HEX} into BLOCK_USR_DATA"
echo ""
echo "Verify with:"
echo "  espefuse --chip esp32c6 --port $PORT summary | grep -A2 BLOCK_USR_DATA"
echo ""
echo "Expected participant flag:  grey{0x${FLAG_HEX}}"
