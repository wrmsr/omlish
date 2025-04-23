from ..fixed import ClampedInt64


def test_int64():
    i = ClampedInt64

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
