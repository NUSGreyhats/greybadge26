#!/bin/bash
#
# Burn 0xC0FFEE into USER_DATA efuse on ESP32-C6
# Offset is configurable so each board can have a different "address"

set -e

PORT=${1:-/dev/ttyACM0}
OFFSET_BITS=${2:-64}    # bit offset within BLK3 (default: 64 bits in)
VALUE="0x00C0FFEE"      # 24-bit value, padded to 32 bits

echo "════════════════════════════════════════"
echo "  CTF EFUSE BURNER — ESP32-C6"
echo "════════════════════════════════════════"
echo "  Port    : $PORT"
echo "  Block   : BLOCK_USR_DATA (BLK3)"
echo "  Offset  : $OFFSET_BITS bits"
echo "  Value   : $VALUE"
echo "════════════════════════════════════════"
echo ""
echo "⚠️  WARNING: Efuses are PERMANENT. Bits can only go 0→1."
echo "⚠️  This chip will be marked forever after burning."
echo ""
read -p "Type BURN to proceed: " confirm
if [ "$confirm" != "BURN" ]; then
    echo "Aborted."
    exit 1
fi

# Build a 32-byte (256-bit) value with 0xC0FFEE at the chosen offset
python3 - "$OFFSET_BITS" > /tmp/ctf_payload.bin <<'PYEOF'
import sys, struct
offset_bits = int(sys.argv[1])
payload = bytearray(32)  # 256 bits = 32 bytes
value = 0x00C0FFEE
byte_offset = offset_bits // 8
payload[byte_offset    ] = (value >>  0) & 0xFF
payload[byte_offset + 1] = (value >>  8) & 0xFF
payload[byte_offset + 2] = (value >> 16) & 0xFF
payload[byte_offset + 3] = (value >> 24) & 0xFF
sys.stdout.buffer.write(payload)
PYEOF

# Burn into BLOCK_USR_DATA
espefuse.py --chip esp32c6 --port "$PORT" \
    burn_block_data BLOCK_USR_DATA /tmp/ctf_payload.bin

rm /tmp/ctf_payload.bin
echo ""
echo "✅ Burned 0xC0FFEE into BLOCK_USR_DATA at bit offset $OFFSET_BITS"
echo ""
echo "Verify with:"
echo "  espefuse.py --chip esp32c6 --port $PORT summary | grep USR_DATA"
