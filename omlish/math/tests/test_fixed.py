import pytest

from ..fixed import CheckedInt64
from ..fixed import CheckedUint64
from ..fixed import ClampedInt64
from ..fixed import ClampedUint64
from ..fixed import OverflowFixedWidthIntError
from ..fixed import UnderflowFixedWidthIntError
from ..fixed import WrappedInt64
from ..fixed import WrappedUint64


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


def test_clamped_uint64():
    i = ClampedUint64

    assert i(5) == 5
    assert i(5) * i(2) == 10
    assert i(5) * 2 == 10
    assert i(50) % 8 == 2
    assert -i(5) == 0
    assert +(i(-5)) == 0
    assert ~i(5) == 18446744073709551610
    assert i(6) & 2 == 2
    assert i(4) | 2 == 6
    assert i(6) ^ 2 == 4
    assert i(2) << 2 == 8
    assert i(8) >> 2 == 2
    assert i(9223372036854775808) == 9223372036854775808
    assert i(-9223372036854775809) == 0
    assert i(18446744073709551615) == 18446744073709551615
    assert i(18446744073709551616) == 18446744073709551615

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


def test_checked_uint64():
    i = CheckedUint64

    assert i(5) == 5
    assert i(5) * i(2) == 10
    assert i(5) * 2 == 10
    assert i(50) % 8 == 2
    with pytest.raises(UnderflowFixedWidthIntError):
        -i(5)  # noqa
    with pytest.raises(UnderflowFixedWidthIntError):
        assert +(i(-5))
    assert ~i(5) == 18446744073709551610
    assert i(6) & 2 == 2
    assert i(4) | 2 == 6
    assert i(6) ^ 2 == 4
    assert i(2) << 2 == 8
    assert i(8) >> 2 == 2
    assert i(18446744073709551615) == 18446744073709551615
    with pytest.raises(OverflowFixedWidthIntError):
        i(18446744073709551616)

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


def test_wrapped_uint64():
    i = WrappedUint64

    assert i(5) == 5
    assert i(5) * i(2) == 10
    assert i(5) * 2 == 10
    assert i(50) % 8 == 2
    assert -i(5) == 18446744073709551611
    assert +(i(-5)) == 18446744073709551611
    assert ~i(5) == 18446744073709551610
    assert i(6) & 2 == 2
    assert i(4) | 2 == 6
    assert i(6) ^ 2 == 4
    assert i(2) << 2 == 8
    assert i(8) >> 2 == 2
    assert i(9223372036854775808) == 9223372036854775808
    assert i(-9223372036854775809) == 9223372036854775807
    assert i(18446744073709551615) == 18446744073709551615
    assert i(18446744073709551616) == 0

    assert divmod(i(5), 3) == (1, 2)
    assert isinstance(divmod(i(5), 3)[0], i)
