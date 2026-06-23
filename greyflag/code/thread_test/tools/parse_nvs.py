#!/usr/bin/env python3
"""
parse_nvs.py — extract Thread Network Key from ESP32 flash dump

Usage:
    esptool.py --port /dev/ttyACM0 read_flash 0 0x400000 flash_dump.bin
    python3 parse_nvs.py flash_dump.bin

Optional: specify NVS partition offset if non-default
    python3 parse_nvs.py flash_dump.bin 0x9000
"""

import sys
import struct

NVS_DEFAULT_OFFSET = 0x9000
NVS_DEFAULT_SIZE   = 0x6000   # 24 KB, typical NVS partition

# Thread Operational Dataset TLV types
TLV_NETWORK_KEY = 0x05        # type byte for Network Key
TLV_KEY_LENGTH  = 0x10        # 16 bytes


def search_for_key_tlv(nvs_bytes):
    """
    Scan the NVS region for the byte pattern: 05 10 <16 bytes>
    This is the Thread Network Key TLV.  Filters out all-zero and all-FF runs.
    """
    results = []
    for i in range(len(nvs_bytes) - 18):
        if nvs_bytes[i] == TLV_NETWORK_KEY and nvs_bytes[i + 1] == TLV_KEY_LENGTH:
            candidate = nvs_bytes[i + 2: i + 18]
            if candidate == bytes(16) or candidate == bytes([0xFF] * 16):
                continue    # skip erased flash
            results.append((i, candidate))
    return results


def search_around_dataset_key(nvs_bytes):
    """
    Locate the NVS key string 'active_dataset', then scan the surrounding
    512 bytes for a Network Key TLV.  Narrows down false positives.
    """
    marker = b'active_dataset\x00'
    pos = nvs_bytes.find(marker)
    if pos == -1:
        return None

    print(f"  [*] found 'active_dataset' at NVS offset +0x{pos:04x}")

    window_start = max(0, pos - 32)
    window_end   = min(len(nvs_bytes), pos + 512)
    window       = nvs_bytes[window_start:window_end]

    hits = search_for_key_tlv(window)
    if hits:
        offset_in_window, key = hits[0]
        return key
    return None


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    nvs_offset = NVS_DEFAULT_OFFSET
    if len(sys.argv) >= 3:
        nvs_offset = int(sys.argv[2], 16)

    with open(sys.argv[1], 'rb') as f:
        flash = f.read()

    print(f"[*] flash size : {len(flash)} bytes")
    print(f"[*] NVS offset : 0x{nvs_offset:04x}")

    nvs = flash[nvs_offset: nvs_offset + NVS_DEFAULT_SIZE]
    if len(nvs) < NVS_DEFAULT_SIZE:
        print("[-] flash dump too small for NVS region — check offset")
        sys.exit(1)

    # strategy 1: anchor to 'active_dataset' key, then scan nearby
    print("\n[1] searching near 'active_dataset' entry...")
    key = search_around_dataset_key(nvs)
    if key:
        _print_key(key)
        return

    # strategy 2: broad TLV pattern scan across the full NVS region
    print("[2] broad TLV scan across NVS region...")
    hits = search_for_key_tlv(nvs)
    if hits:
        print(f"  [*] found {len(hits)} candidate(s):")
        for offset, candidate in hits:
            print(f"      NVS+0x{offset:04x}: {candidate.hex()}")
        key = hits[0][1]
        _print_key(key)
        return

    print("[-] Network Key not found.")
    print("    hints:")
    print("    • confirm NVS offset with: esptool.py read_flash 0x8000 0x1000 ptable.bin")
    print("      then: python3 -m esptool gen_esp32part ptable.bin")
    print("    • badge must have joined the network at least once before dumping")


def _print_key(key):
    print(f"\n{'='*50}")
    print(f"  Network Key (hex): {key.hex()}")
    print(f"  Network Key (fmt): {':'.join(f'{b:02x}' for b in key)}")
    print(f"{'='*50}")
    print(f"\n  pass to decrypt_flag.py as the second argument")


if __name__ == "__main__":
    main()
