import pytest

from ..fixed import CheckedInt64
from ..fixed import ClampedInt64
from ..fixed import OverflowFixedWidthIntError
from ..fixed import UnderflowFixedWidthIntError
from ..fixed import WrappedInt64


def test_clamped_int64():
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
    assert i(9223372036854775808) == 9223372036854775807
    assert i(-9223372036854775809) == -9223372036854775808
    assert i(18446744073709551615) == 9223372036854775807

    assert divmod(i(5), 3) == (1, 2)
    assert isinstance(divmod(i(5), 3)[0], i)


def test_checked_int64():
    i = CheckedInt64

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
    with pytest.raises(OverflowFixedWidthIntError):
        i(9223372036854775808)
    with pytest.raises(UnderflowFixedWidthIntError):
        i(-9223372036854775809)

    assert divmod(i(5), 3) == (1, 2)
    assert isinstance(divmod(i(5), 3)[0], i)


def test_wrapped_int64():
    i = WrappedInt64

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
