from ..bits import Int64
from ..bits import get_bit
from ..bits import get_bits
from ..bits import set_bit
from ..bits import set_bits


def test_bits():
    assert get_bit(3, 0b0100) == 0
    assert get_bit(2, 0b0100) == 1
    assert get_bits(1, 2, 0b0100) == 0b10
    assert get_bits(1, 3, 0b0100) == 0b10
    assert get_bits(0, 3, 0b0100) == 0b100
    assert get_bits(1, 1, 0b0100) == 0
    assert set_bit(2, 1, 0b01010) == 0b01110
    assert set_bit(3, 0, 0b01010) == 0b00010
    assert set_bits(1, 2, 0b11, 0b01010) == 0b01110
    assert set_bits(1, 2, 0b10, 0b01010) == 0b01100


def test_int64():
    i = Int64

    assert i(5) == 5
    assert i(5) * i(2) == 10
    assert i(5) * 2 == 10
    assert i(50) % 8 == 2
    assert -i(5) == -5
    assert +(i(-5)) == -5
    assert ~i(5) == -6
    assert i(6) & 2 == 2
    assert i(4) | 2 == 6
    assert i(6) ^ 2 == 4
    assert i(2) << 2 == 8
    assert i(8) >> 2 == 2
    assert i(9223372036854775808) == -9223372036854775808
    assert i(-9223372036854775809) == 9223372036854775807
    assert i(18446744073709551615) == -1

    assert divmod(i(5), 3) == (1, 2)
    assert isinstance(divmod(i(5), 3)[0], i)
