import datetime
import re
import typing as ta


##


def _is_exact_int(x: object) -> bool:
    return type(x) is int


def _is_exact_float(x: object) -> bool:
    return type(x) is float


def _is_exact_int_or_float(x: object) -> bool:
    return type(x) in (int, float)


##


@ta.final
class Bytes:
    """
    - +, - with exact int or Bytes -> Bytes
    - * with exact int -> Bytes
    - / and // with exact int -> Bytes (only if divisible exactly)
    - disallows Bytes*Bytes, Bytes/Bytes, etc.
    """

    def __new__(cls, v: ta.Union[int, 'Bytes']) -> 'Bytes':
        if isinstance(v, cls):
            return v
        else:
            return super().__new__(cls)

    def __init__(self, v: ta.Union['Bytes', int]) -> None:
        if isinstance(v, Bytes):
            if v is not self:
                raise TypeError(v)
        else:
            self._v = int(v)

    def __int__(self) -> int:
        return self._v

    # formatting / parsing

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._v!r})'

    _DEC_UNITS: ta.ClassVar[tuple[tuple[str, int], ...]] = (
        ('B', 1),
        ('KB', 1000),
        ('MB', 1000**2),
        ('GB', 1000**3),
        ('TB', 1000**4),
        ('PB', 1000**5),
        ('EB', 1000**6),
    )

    _BIN_UNITS: ta.ClassVar[tuple[tuple[str, int], ...]] = (
        ('B', 1),
        ('KiB', 1024),
        ('MiB', 1024**2),
        ('GiB', 1024**3),
        ('TiB', 1024**4),
        ('PiB', 1024**5),
        ('EiB', 1024**6),
    )

    _UNIT_MAP: ta.ClassVar[ta.Mapping[str,int]] = dict(_DEC_UNITS + _BIN_UNITS)

    def __str__(self) -> str:
        n = self._v
        sign = '-' if n < 0 else ''
        v = abs(n)
        if not v:
            return '0 B'

        # choose binary for nice powers-of-two, else decimal.
        # heuristic: prefer binary if divisible by 1024 and >= 1024.
        units = self._BIN_UNITS if (v >= 1024 and v % 1024 == 0) else self._DEC_UNITS

        # pick the largest unit that divides evenly; otherwise fall back to B.
        chosen_name, chosen_scale = 'B', 1
        for name, scale in units:
            if scale == 1:
                continue
            if v % scale == 0:
                chosen_name, chosen_scale = name, scale

        if chosen_scale == 1:
            return f'{sign}{v} B'
        return f'{sign}{v // chosen_scale} {chosen_name}'

    _PARSE_RE: ta.ClassVar[re.Pattern[str]] = re.compile(
        r'^\s*([+-]?\d+)\s*([A-Za-z]+)\s*$',
    )

    @classmethod
    def parse(cls, s: str) -> 'Bytes':
        m = cls._PARSE_RE.match(s)
        if not m:
            raise ValueError(f'Invalid Bytes string: {s!r}')
        num_s, unit = m.group(1), m.group(2)

        num = int(num_s)

        try:
            scale = cls._UNIT_MAP[unit]
        except KeyError:
            raise ValueError(f'Unknown byte unit {unit!r}') from None

        return cls(num * scale)

    # operators

    def __hash__(self) -> int:
        return hash(self._v)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Bytes):
            return NotImplemented
        return self._v == other._v

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Bytes):
            return NotImplemented
        return self._v != other._v

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Bytes):
            return NotImplemented
        return self._v < other._v

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Bytes):
            return NotImplemented
        return self._v <= other._v

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Bytes):
            return NotImplemented
        return self._v > other._v

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Bytes):
            return NotImplemented
        return self._v >= other._v

    def _coerce_other(self, other: object) -> int:
        if isinstance(other, Bytes):
            return other._v  # Noqa
        elif _is_exact_int(other):
            return other  # type: ignore[return-value]
        else:
            raise TypeError(f'Bytes can only add/sub Bytes or exact int, got {type(other).__name__}')

    def __add__(self, other: object) -> 'Bytes':
        return Bytes(self._v + self._coerce_other(other))

    def __radd__(self, other: object) -> 'Bytes':
        return self.__add__(other)

    def __sub__(self, other: object) -> 'Bytes':
        return Bytes(self._v - self._coerce_other(other))

    def __rsub__(self, other: object) -> 'Bytes':
        if isinstance(other, Bytes):
            return Bytes(other._v - self._v)
        if _is_exact_int(other):
            return Bytes(other - self._v)  # type: ignore[operator]
        return NotImplemented  # will raise TypeError

    def __mul__(self, other: object) -> 'Bytes':
        if _is_exact_int(other):
            return Bytes(self._v * other)  # type: ignore[operator]
        raise TypeError(f'Bytes can only be multiplied by exact int, got {type(other).__name__}')

    def __rmul__(self, other: object) -> 'Bytes':
        return self.__mul__(other)

    def _div_exact(self, other: object) -> 'Bytes':
        if not _is_exact_int(other):
            raise TypeError(f'Bytes can only be divided by exact int, got {type(other).__name__}')
        if other == 0:
            raise ZeroDivisionError
        n = self._v
        q, r = divmod(n, other)  # type: ignore[operator]
        if r != 0:
            raise ValueError(f'Non-exact byte division: {n} / {other} has remainder {r}')
        return Bytes(q)

    def __truediv__(self, other: object) -> 'Bytes':
        return self._div_exact(other)

    def __floordiv__(self, other: object) -> 'Bytes':
        return self._div_exact(other)


B: ta.Final[Bytes] = Bytes(1)

KB: ta.Final[Bytes] = 1000 * B
MB: ta.Final[Bytes] = 1000 * KB
GB: ta.Final[Bytes] = 1000 * MB
TB: ta.Final[Bytes] = 1000 * GB

KiB: ta.Final[Bytes] = 1024 * B
MiB: ta.Final[Bytes] = 1024 * KiB
GiB: ta.Final[Bytes] = 1024 * MiB
TiB: ta.Final[Bytes] = 1024 * GiB


##


@ta.final
class Seconds:
    """
    - +, - with exact int/float or Seconds -> Seconds
    - * and / with exact int/float -> Seconds
    - disallows Seconds*Seconds, Seconds/Seconds, etc.
    - timedelta interop via to_timedelta / from_timedelta
    """

    def __new__(cls, v: ta.Union[float, 'Seconds']) -> 'Seconds':
        if isinstance(v, cls):
            return v
        else:
            return super().__new__(cls)

    def __init__(self, v: ta.Union['Seconds', float]) -> None:
        if isinstance(v, Seconds):
            if v is not self:
                raise TypeError(v)
        else:
            self._v = float(v)

    def __float__(self) -> float:
        return self._v

    # formatting / parsing

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._v!r})'

    _UNITS: ta.ClassVar[tuple[tuple[str, float], ...]] = (
        ('ns', 1e-9),
        ('us', 1e-6),
        ('ms', 1e-3),
        ('s', 1.0),
        ('m', 60.0),
        ('h', 3600.0),
        ('d', 86400.0),
    )

    _UNITS_MAP: ta.ClassVar[ta.Mapping[str, float]] = dict(_UNITS)

    def __str__(self) -> str:
        x = self._v
        if not x:
            return '0 s'

        sign = '-' if x < 0 else ''
        v = abs(x)

        # choose a "nice" unit:
        # - if >= 60, prefer d/h/m where the scaled value is >= 1
        # - if < 1, prefer ms/us/ns where the scaled value is >= 1
        # For sub-second, pick the *largest* sub-second unit that yields >= 1.
        unit_name, unit_scale = 's', 1.0

        if v >= 60.0:
            for name, scale in reversed(self._UNITS):
                if scale >= 1.0 and (v / scale) >= 1.0:
                    unit_name, unit_scale = name, scale
                    break
        elif v < 1.0:
            for name, scale in reversed(self._UNITS):
                if scale < 1.0 and (v / scale) >= 1.0:
                    unit_name, unit_scale = name, scale
                    break

        scaled = v / unit_scale
        # Use a stable, parseable representation (roundtrip-ish for float).
        num_s = format(scaled, '.15g')
        return f'{sign}{num_s} {unit_name}'

    _PARSE_RE: ta.ClassVar[re.Pattern[str]] = re.compile(
        r'^\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*([A-Za-z]+)\s*$',
    )

    @classmethod
    def parse(cls, s: str) -> 'Seconds':
        m = cls._PARSE_RE.match(s)
        if not m:
            raise ValueError(f'Invalid Seconds string: {s!r}')
        num_s, unit = m.group(1), m.group(2)

        num = float(num_s)
        try:
            scale = cls._UNITS_MAP[unit]
        except KeyError:
            raise ValueError(f'Unknown time unit {unit!r}') from None

        return cls(num * scale)

    # operators

    def __hash__(self) -> int:
        return hash(self._v)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Seconds):
            return NotImplemented
        return self._v == other._v

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Seconds):
            return NotImplemented
        return self._v != other._v

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Seconds):
            return NotImplemented
        return self._v < other._v

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Seconds):
            return NotImplemented
        return self._v <= other._v

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Seconds):
            return NotImplemented
        return self._v > other._v

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Seconds):
            return NotImplemented
        return self._v >= other._v

    def _coerce_other(self, other: object) -> float:
        if isinstance(other, Seconds):
            return other._v  # Noqa
        elif _is_exact_int_or_float(other):
            return float(other)  # type: ignore[arg-type]
        else:
            raise TypeError(f'Seconds can only add/sub Seconds or exact int/float, got {type(other).__name__}')

    def __add__(self, other: object) -> 'Seconds':
        return Seconds(self._v + self._coerce_other(other))

    def __radd__(self, other: object) -> 'Seconds':
        return self.__add__(other)

    def __sub__(self, other: object) -> 'Seconds':
        return Seconds(self._v - self._coerce_other(other))

    def __rsub__(self, other: object) -> 'Seconds':
        if isinstance(other, Seconds):
            return Seconds(other._v - self._v)
        if _is_exact_int_or_float(other):
            return Seconds(float(other) - self._v)  # type: ignore[arg-type]
        return NotImplemented

    def __mul__(self, other: object) -> 'Seconds':
        if _is_exact_int_or_float(other):
            return Seconds(self._v * float(other))  # type: ignore[arg-type]
        raise TypeError(f'Seconds can only be multiplied by exact int/float, got {type(other).__name__}')

    def __rmul__(self, other: object) -> 'Seconds':
        return self.__mul__(other)

    def __truediv__(self, other: object) -> 'Seconds':
        if _is_exact_int_or_float(other):
            other_f = float(other)  # type: ignore[arg-type]
            if other_f == 0.0:
                raise ZeroDivisionError
            return Seconds(self._v / other_f)
        raise TypeError(f'Seconds can only be divided by exact int/float, got {type(other).__name__}')

    def __pow__(self, other: object, modulo: object = None) -> 'Seconds':
        raise TypeError('Seconds exponentiation is nonsensical for this unit type')

    # timedelta interop

    def to_timedelta(self) -> datetime.timedelta:
        return datetime.timedelta(seconds=self._v)

    @classmethod
    def from_timedelta(cls, td: datetime.timedelta) -> 'Seconds':
        return cls(td.total_seconds())


S: ta.Final[Seconds] = Seconds(1.0)
MS: ta.Final[Seconds] = Seconds(1e-3)
US: ta.Final[Seconds] = Seconds(1e-6)
NS: ta.Final[Seconds] = Seconds(1e-9)

M: ta.Final[Seconds] = 60 * S
H: ta.Final[Seconds] = 60 * M
D: ta.Final[Seconds] = 24 * H
