cpdef long get_bit(int bit, long value):
    return (value >> bit) & 1


cpdef long get_bits(int bits_from, int num_bits, long value):
    return (value & ((1 << (bits_from + num_bits)) - 1)) >> bits_from


cpdef long set_bit(int bit, int bit_value, long value):
    if bit_value:
        return value | (1 << bit)
    else:
        return value & ~(1 << bit)


cpdef long set_bits(int bits_from, int num_bits, long bits_value, long value):
    return value & ~(((1 << num_bits) - 1) << bits_from) | (bits_value << bits_from)
