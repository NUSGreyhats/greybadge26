NVM_MAGIC = 0xA7
MAX_PATH_LEN = 255


def _check_path(name, value):
    if not value:
        raise ValueError("%s path is empty" % name)
    encoded = value.encode("utf-8")
    if len(encoded) > MAX_PATH_LEN:
        raise ValueError("%s path too long" % name)
    return encoded


def pack_autorun_marker(bitstream_path, payload_path):
    bitstream = _check_path("bitstream", bitstream_path)
    payload = _check_path("payload", payload_path)
    return bytes((NVM_MAGIC, len(bitstream), len(payload))) + bitstream + payload


def unpack_autorun_marker(data):
    if data[0] != NVM_MAGIC:
        raise ValueError("watchdog OLED autorun marker not present")
    bit_len = data[1]
    payload_len = data[2]
    bit_start = 3
    payload_start = bit_start + bit_len
    payload_end = payload_start + payload_len
    bitstream = bytes(data[bit_start:payload_start]).decode("utf-8")
    payload = bytes(data[payload_start:payload_end]).decode("utf-8")
    return bitstream, payload


def write_autorun_marker(nvm, bitstream_path, payload_path):
    packet = pack_autorun_marker(bitstream_path, payload_path)
    if len(packet) > len(nvm):
        raise ValueError("autorun marker too long for nvm")
    nvm[0:len(packet)] = packet


def read_autorun_marker(nvm):
    return unpack_autorun_marker(nvm)


def clear_autorun_marker(nvm):
    nvm[0:3] = b"\x00\x00\x00"
