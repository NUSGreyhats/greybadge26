#!/usr/bin/env python3
"""
decrypt_flag.py — decrypt a raw 802.15.4 broadcaster frame

Requires: pip install pycryptodome

Usage:
    python3 decrypt_flag.py <frame_hex> <network_key_hex>

Where:
    frame_hex       — hex string from sniffer output (the part after "RX CH15 RSSI:... LEN:...: ")
                      e.g. "49d80337130xffff..."
    network_key_hex — 32-char hex string (16 bytes) from parse_nvs.py output

Example:
    python3 decrypt_flag.py 49d803371300ffff... deadbeefcafebabe0123456789abcdef

How to identify the broadcaster frame in sniffer output:
    Look for: bytes at position 3-4 (0-indexed from Frame Control) equal to "37 13"
    That is PAN ID 0x1337 in little-endian — the broadcaster's PAN.
    Thread frames use PAN ID 0x1234 (bytes "34 12").

Frame format built by organiser_broadcaster:
    [FC:2][Seq:1][DstPAN:2][DstAddr:2][SrcEUI64:8][SecCtrl:1][FrameCtr:4][Ciphertext:N][MIC:4]
    SecCtrl = 0x05  (Security Level 5 = ENC-MIC-32, Key ID Mode 0 = implicit)

Nonce construction (13 bytes):
    SrcEUI64(8B, as in frame) || FrameCtr(4B, little-endian) || SecLevel(1B = 0x05)

AAD (authenticated additional data):
    All bytes from Frame Control through end of Aux Security Header (20 bytes).
    Must be passed to cipher.update() BEFORE decrypt — affects MIC verification.
"""

import sys
import struct
from Crypto.Cipher import AES


def parse_frame(raw: bytes) -> dict:
    """Parse a raw 802.15.4 MAC frame (starting from Frame Control)."""
    off = 0

    # ── Frame Control ─────────────────────────────────────────────────────────
    fc_word        = struct.unpack_from('<H', raw, off)[0]; off += 2
    security_en    = (fc_word >> 3)  & 0x1
    pan_compress   = (fc_word >> 6)  & 0x1
    dst_addr_mode  = (fc_word >> 10) & 0x3
    src_addr_mode  = (fc_word >> 14) & 0x3

    seq = raw[off]; off += 1

    # ── Destination PAN ID (always present in our frame) ──────────────────────
    dst_pan = struct.unpack_from('<H', raw, off)[0]; off += 2

    # ── Destination address ───────────────────────────────────────────────────
    if   dst_addr_mode == 2: off += 2   # 16-bit short (e.g. 0xFFFF broadcast)
    elif dst_addr_mode == 3: off += 8   # 64-bit extended

    # ── Source PAN ID (omitted when PAN ID Compression bit is set) ───────────
    if not pan_compress and src_addr_mode != 0:
        off += 2

    # ── Source extended address (EUI-64) ──────────────────────────────────────
    if src_addr_mode != 3:
        raise ValueError(f"expected extended source address, got mode {src_addr_mode}")
    src_eui64 = raw[off: off + 8]; off += 8

    if not security_en:
        raise ValueError("Security Enabled bit is not set — frame is not encrypted")

    # ── Auxiliary Security Header ─────────────────────────────────────────────
    sec_ctrl      = raw[off]; off += 1
    sec_level     = sec_ctrl & 0x07         # bits[2:0]
    key_id_mode   = (sec_ctrl >> 3) & 0x03  # bits[4:3]

    frame_ctr_raw = raw[off: off + 4]; off += 4
    frame_ctr     = struct.unpack('<I', frame_ctr_raw)[0]

    if   key_id_mode == 1: off += 1    # 1-byte key index
    elif key_id_mode == 2: off += 5    # 4-byte key source + 1-byte key index
    # mode 0: no field

    # ── AAD = everything from FC to end of Aux Sec Header ────────────────────
    aad_end    = off
    aad        = raw[:aad_end]

    # ── Ciphertext and MIC ────────────────────────────────────────────────────
    ciphertext = raw[off:-4]
    mic        = raw[-4:]

    # ── Nonce (13 bytes) ──────────────────────────────────────────────────────
    # Bytes come directly from the frame in wire order (no swapping needed).
    nonce = bytes(src_eui64) + frame_ctr_raw + bytes([sec_level])

    return {
        'dst_pan':    dst_pan,
        'src_eui64':  src_eui64,
        'frame_ctr':  frame_ctr,
        'sec_level':  sec_level,
        'key_id_mode': key_id_mode,
        'nonce':      nonce,
        'aad':        aad,
        'ciphertext': ciphertext,
        'mic':        mic,
    }


def decrypt(frame_hex: str, key_hex: str):
    raw = bytes.fromhex(frame_hex.replace(' ', '').replace(':', ''))
    key = bytes.fromhex(key_hex.replace(' ', '').replace(':', ''))

    if len(key) != 16:
        print(f"[-] network key must be 16 bytes, got {len(key)}")
        sys.exit(1)

    try:
        info = parse_frame(raw)
    except (ValueError, struct.error) as e:
        print(f"[-] frame parse error: {e}")
        sys.exit(1)

    print(f"  dest PAN ID   : 0x{info['dst_pan']:04X}")
    print(f"  src EUI-64    : {info['src_eui64'].hex(' ')}")
    print(f"  frame counter : {info['frame_ctr']}")
    print(f"  sec level     : {info['sec_level']} (ENC-MIC-32)")
    print(f"  key ID mode   : {info['key_id_mode']} (0=implicit/raw key)")
    print(f"  nonce (13B)   : {info['nonce'].hex()}")
    print(f"  AAD  ({len(info['aad']):2d}B)   : {info['aad'].hex()}")
    print(f"  ciphertext    : {info['ciphertext'].hex()}")
    print(f"  MIC (4B)      : {info['mic'].hex()}")

    cipher = AES.new(key, AES.MODE_CCM, nonce=info['nonce'], mac_len=4)
    cipher.update(info['aad'])

    try:
        plaintext = cipher.decrypt_and_verify(info['ciphertext'], info['mic'])
    except ValueError:
        print("\n[-] MIC verification failed — check:")
        print("    1. network key is from THIS badge's NVS, after joining")
        print("    2. frame hex starts at Frame Control (skip the length byte)")
        print("    3. frame hex ends after MIC (no FCS — sniffer strips it)")
        print("    4. if you used Thread-derived MAC key: this is NOT a Thread frame")
        print("       the broadcaster uses the raw Network Key, not the derived MAC Key")
        sys.exit(1)

    print(f"\n{'='*50}")
    print(f"  {plaintext.decode('utf-8', errors='replace')}")
    print(f"{'='*50}\n")
    return plaintext


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    decrypt(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
