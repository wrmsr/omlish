import struct


def will_overflow():
    """
    Construct an array/string/bytes length which would cause a memory error on decode. This should be less than
    sys.maxsize (the max integer index)
    """

    bit_size = struct.calcsize('P') * 8
    huge_length = 1 << (bit_size - 8)
    return struct.pack('Q', huge_length)
