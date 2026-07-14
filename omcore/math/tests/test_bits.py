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
