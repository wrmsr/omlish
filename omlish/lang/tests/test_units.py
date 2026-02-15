import datetime as dt

import pytest

from ..units import GB  # noqa: F401
from ..units import KB  # noqa: F401
from ..units import MB  # noqa: F401
from ..units import MS  # noqa: F401
from ..units import NS  # noqa: F401
from ..units import TB  # noqa: F401
from ..units import US  # noqa: F401
from ..units import B  # noqa: F401
from ..units import Bytes  # noqa: F401
from ..units import D  # noqa: F401
from ..units import GiB  # noqa: F401
from ..units import H  # noqa: F401
from ..units import KiB  # noqa: F401
from ..units import M  # noqa: F401
from ..units import MiB  # noqa: F401
from ..units import S  # noqa: F401
from ..units import Seconds  # noqa: F401
from ..units import TiB  # noqa: F401


# Bytes tests


def test_bytes_constants() -> None:
    assert int(B) == 1
    assert int(KB) == 1000
    assert int(MB) == 1000_000
    assert int(GB) == 1000_000_000
    assert int(TB) == 1000_000_000_000

    assert int(KiB) == 1024
    assert int(MiB) == 1024**2
    assert int(GiB) == 1024**3
    assert int(TiB) == 1024**4


@pytest.mark.parametrize(
    ('val', 'expected'),
    [
        (Bytes(0), '0 B'),
        (Bytes(1), '1 B'),
        (Bytes(999), '999 B'),
        (Bytes(1000), '1 KB'),
        (Bytes(1000 * 1000), '1 MB'),
        (Bytes(1024), '1 KiB'),
        (Bytes(16 * 1024), '16 KiB'),
        (Bytes(-16 * 1024), '-16 KiB'),
        (Bytes(2 * 1024**3), '2 GiB'),
        (Bytes(3 * 1000**3), '3 GB'),
    ],
)
def test_bytes_str_pretty(val: Bytes, expected: str) -> None:
    assert str(val) == expected


@pytest.mark.parametrize(
    ('s', 'expected'),
    [
        ('0 B', 0),
        ('1 B', 1),
        ('16 KiB', 16 * 1024),
        ('16KiB', 16 * 1024),
        ('2 MiB', 2 * 1024**2),
        ('3 GB', 3 * 1000**3),
        ('-7 KB', -7 * 1000),
        ('  12   B  ', 12),
    ],
)
def test_bytes_parse_basic(s: str, expected: int) -> None:
    b = Bytes.parse(s)
    assert isinstance(b, Bytes)
    assert int(b) == expected


@pytest.mark.parametrize(
    'bad',
    [
        '',
        ' ',
        'KiB',
        '1',
        '1  ',
        '1 XB',
        '1 kib',   # case-sensitive by design
        '1.0 B',   # integer only
        'True B',
        '1.0KiB',
    ],
)
def test_bytes_parse_rejects_invalid(bad: str) -> None:
    with pytest.raises(ValueError):  # noqa
        Bytes.parse(bad)


@pytest.mark.parametrize(
    'n',
    [
        0,
        1,
        7,
        16,
        999,
        1000,
        1024,
        4096,
        10**6,
        2 * 1024**3,
        -17 * 1024,
    ],
)
def test_bytes_str_parse_roundtrip(n: int) -> None:
    b = Bytes(n)
    assert Bytes.parse(str(b)) == b


def test_bytes_add_sub_with_bytes_and_exact_int() -> None:
    assert isinstance(1 * KiB + 2 * KiB, Bytes)
    assert 1 * KiB + 2 * KiB == 3 * KiB

    assert 1 * KiB + 5 == Bytes(1024 + 5)
    assert 5 + 1 * KiB == Bytes(5 + 1024)

    assert 1 * KiB - 24 == Bytes(1024 - 24)
    assert 24 - 1 * KiB == Bytes(24 - 1024)

    assert (2 * KiB - 1 * KiB) == 1 * KiB
    assert isinstance(2 * KiB - 1 * KiB, Bytes)


@pytest.mark.parametrize('rhs', [True, False, 1.0, 1.5, object()])
def test_bytes_add_rejects_non_exact_int_and_non_bytes(rhs: object) -> None:
    with pytest.raises(TypeError):
        _ = Bytes(1) + rhs
    with pytest.raises(TypeError):
        _ = rhs + Bytes(1)


def test_bytes_mul_exact_int_only() -> None:
    assert 3 * KiB == Bytes(3 * 1024)
    assert KiB * 3 == Bytes(3 * 1024)
    assert isinstance(3 * KiB, Bytes)

    with pytest.raises(TypeError):
        _ = KiB * 1.0
    with pytest.raises(TypeError):
        _ = 1.0 * KiB
    with pytest.raises(TypeError):
        _ = KiB * True
    with pytest.raises(TypeError):
        _ = KiB * Bytes(2)


def test_bytes_div_exact_int_only_and_exactness() -> None:
    assert (16 * KiB) / 2 == 8 * KiB
    assert (16 * KiB) // 2 == 8 * KiB
    assert isinstance((16 * KiB) / 2, Bytes)

    with pytest.raises(ZeroDivisionError):
        _ = KiB / 0

    # non-exact division rejected
    with pytest.raises(ValueError):  # noqa
        _ = Bytes(10) / 3

    # wrong rhs types rejected
    with pytest.raises(TypeError):
        _ = KiB / 2.0
    with pytest.raises(TypeError):
        _ = KiB / True
    with pytest.raises(TypeError):
        _ = KiB / Bytes(2)


def test_bytes_pow_rejected() -> None:
    with pytest.raises(TypeError):
        _ = KiB ** 2  # type: ignore[operator]


# Seconds tests


def test_seconds_constants() -> None:
    assert float(S) == 1.0
    assert float(M) == 60.0
    assert float(H) == 3600.0
    assert float(D) == 86400.0
    assert float(MS) == 1e-3
    assert float(US) == 1e-6
    assert float(NS) == 1e-9


@pytest.mark.parametrize(
    ('val', 'expected'),
    [
        (Seconds(0.0), '0 s'),
        (Seconds(1.0), '1 s'),
        (Seconds(1.25), '1.25 s'),
        (Seconds(0.001), '1 ms'),
        (Seconds(0.000_001), '1 us'),
        (Seconds(0.000_000_001), '1 ns'),
        (Seconds(60.0), '1 m'),
        (Seconds(120.0), '2 m'),
        (Seconds(3600.0), '1 h'),
        (Seconds(-3600.0), '-1 h'),
        (Seconds(86400.0), '1 d'),
        (Seconds(90.0), '1.5 m'),
    ],
)
def test_seconds_str_pretty(val: Seconds, expected: str) -> None:
    assert str(val) == expected


@pytest.mark.parametrize(
    ('s', 'expected'),
    [
        ('0 s', 0.0),
        ('1 s', 1.0),
        ('1.25 s', 1.25),
        ('1 ms', 1e-3),
        ('1 us', 1e-6),
        ('1 ns', 1e-9),
        ('1 m', 60.0),
        ('1.5 m', 90.0),
        ('2 h', 7200.0),
        ('-2 h', -7200.0),
        ('  2.5   s ', 2.5),
        ('1e3 s', 1000.0),
        ('-1e-3 s', -1e-3),
    ],
)
def test_seconds_parse_basic(s: str, expected: float) -> None:
    t = Seconds.parse(s)
    assert isinstance(t, Seconds)
    assert float(t) == pytest.approx(expected)


@pytest.mark.parametrize(
    'bad',
    [
        '',
        ' ',
        's',
        '1',
        '1  ',
        '1 xs',
        '1 sec',
        '1S',     # requires space + exact unit token
        '1.2.3 s',
        'nan s',
        'inf s',
        '1  msms',
    ],
)
def test_seconds_parse_rejects_invalid(bad: str) -> None:
    with pytest.raises(ValueError):  # noqa
        Seconds.parse(bad)


@pytest.mark.parametrize(
    'x',
    [
        0.0,
        1.0,
        1.25,
        0.001,
        0.000001,
        0.000000001,
        60.0,
        90.0,
        3600.0,
        -2.5,
        12345.6789,
    ],
)
def test_seconds_str_parse_roundtrip_reasonable(x: float) -> None:
    t = Seconds(x)
    # We compare approximately because float formatting/parse may not be
    # bit-for-bit for arbitrary values, but should be stable for "normal" ones.
    assert float(Seconds.parse(str(t))) == pytest.approx(float(t), rel=0, abs=1e-11)


def test_seconds_add_sub_with_seconds_and_exact_number() -> None:
    assert isinstance(1.5 * M + 30 * S, Seconds)
    assert 1.5 * M + 30 * S == Seconds(120.0)

    assert 5 * S + 2 == Seconds(7.0)
    assert 2 + 5 * S == Seconds(7.0)

    assert 5 * S + 2.5 == Seconds(7.5)
    assert 2.5 + 5 * S == Seconds(7.5)

    assert 10 * S - 2 == Seconds(8.0)
    assert 2 - 10 * S == Seconds(-8.0)


@pytest.mark.parametrize('rhs', [True, False, object(), Bytes(1), '1'])
def test_seconds_add_rejects_non_exact_number_and_non_seconds(rhs: object) -> None:
    with pytest.raises(TypeError):
        _ = S + rhs
    with pytest.raises(TypeError):
        _ = rhs + S


def test_seconds_mul_div_exact_number_only() -> None:
    assert 2 * M == Seconds(120.0)
    assert M * 2 == Seconds(120.0)
    assert M * 2.5 == Seconds(150.0)
    assert 2.5 * M == Seconds(150.0)
    assert isinstance(2.5 * M, Seconds)

    assert (2 * M) / 2 == M
    assert (2 * M) / 2.0 == M

    with pytest.raises(ZeroDivisionError):
        _ = M / 0
    with pytest.raises(ZeroDivisionError):
        _ = M / 0.0

    # disallow Seconds * Seconds and Seconds / Seconds
    with pytest.raises(TypeError):
        _ = M * S
    with pytest.raises(TypeError):
        _ = M / S


def test_seconds_pow_rejected() -> None:
    with pytest.raises(TypeError):
        _ = S ** 2


def test_seconds_timedelta_roundtrip() -> None:
    t = 90 * S
    td = t.to_timedelta()
    assert isinstance(td, dt.timedelta)
    assert td == dt.timedelta(seconds=90)

    t2 = Seconds.from_timedelta(td)
    assert isinstance(t2, Seconds)
    assert t2 == 90 * S


def test_seconds_timedelta_fractional() -> None:
    t = 1.2345 * S
    td = t.to_timedelta()
    assert td == dt.timedelta(seconds=1.2345)

    # timedelta stores microsecond resolution; total_seconds reflects that.
    t2 = Seconds.from_timedelta(td)
    assert float(t2) == pytest.approx(1.2345, rel=0, abs=1e-6)


# Cross-type interaction sanity


def test_bytes_and_seconds_do_not_mix() -> None:
    with pytest.raises(TypeError):
        _ = KiB + S
    with pytest.raises(TypeError):
        _ = S + KiB
    with pytest.raises(TypeError):
        _ = KiB * S
    with pytest.raises(TypeError):
        _ = S * KiB
