def get_bit(bit: int, value: int) -> int:
    return (value >> bit) & 1


def get_bits(bits_from: int, num_bits: int, value: int) -> int:
    return (value & ((1 << (bits_from + num_bits)) - 1)) >> bits_from


def set_bit(bit: int, bit_value: int, value: int) -> int:
    if bit_value:
        return value | (1 << bit)
    else:
        return value & ~(1 << bit)


def set_bits(bits_from: int, num_bits: int, bits_value: int, value: int) -> int:
    return value & ~(((1 << num_bits) - 1) << bits_from) | (bits_value << bits_from)
