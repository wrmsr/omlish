import enum
import functools
import re
import typing as ta

from . import check
from . import defs
from . import lang


lang.warn_unstable()


class Bound(enum.Enum):
    """
    These integer values are significant and used for ordering:

        (5, BELOW) < (5, EXACTLY) < (5, ABOVE)
        <-- 4            5              6 --->
    """

    BELOW = 1
    EXACTLY = 2
    ABOVE = 3


T = ta.TypeVar('T')
U = ta.TypeVar('U')


@functools.total_ordering
class Marker(ta.Generic[T]):
    """
    {ABOVE | EXACTLY} -> {EXACTLY | BELOW}
    """
    __slots__ = (
        '_value',
        '_bound',
    )

    UNBOUNDED_BELOW: 'Marker' = None
    EMPTY: 'Marker' = None
    UNBOUNDED_ABOVE: 'Marker' = None

    def __init__(self, value: ta.Optional[T], bound: Bound) -> None:
        super().__init__()

        self._value = value
        self._bound = check.isinstance(bound, Bound)

    @classmethod
    def of(cls, value, bound) -> 'Marker':
        return cls(value, lang.parse_enum(bound, Bound))

    @property
    def value(self) -> ta.Optional[T]:
        return self._value

    @property
    def bound(self) -> Bound:
        return self._bound

    defs.repr('value', 'bound')
    defs.hash_eq('value', 'bound')

    def __lt__(self, other: 'Marker[T]') -> bool:
        if type(self) is not type(other):
            return NotImplemented
        else:
            return \
                self.value < other.value and \
                self.bound.value < other.bound.value

    def __str__(self) -> str:
        prefix = '<' if self.bonud == Bound.BELOW else '>' if self.bound == Bound.ABOVE else ''
        value = '...' if self.value is None else str(self.value)
        return prefix + value

    @property
    def is_empty(self) -> bool:
        return self.value is None and self.bound == Bound.EXACTLY

    @property
    def is_unbounded(self) -> bool:
        return self.value is None and self.bound != Bound.EXACTLY

    def to_dict(self):
        return {
            'value': self.value,
            'bound': self.bound.name,
        }

    @classmethod
    def from_dict(cls, dct):
        check.arg(set(dct.keys()) == {'value', 'bound'})
        return cls(dct['value'], lang.parse_enum(dct['bound'], Bound))

    to_json = _to_json = to_dict
    from_json = _from_json = from_dict


Marker.UNBOUNDED_BELOW = Marker(None, Bound.BELOW)
Marker.EMPTY = Marker(None, Bound.EXACTLY)
Marker.UNBOUNDED_ABOVE = Marker(None, Bound.ABOVE)


class Span(ta.Generic[T]):
    """
    ~com.facebook.presto.spi.predicate.Range
    """
    __slots__ = (
        '_lower',
        '_upper',
    )

    UNBOUNDED: 'Span' = None
    EMPTY: 'Span' = None

    def __init__(self, lower: Marker[T], upper: Marker[T]) -> None:
        super().__init__()

        self._lower = check.isinstance(lower, Marker)
        self._upper = check.isinstance(upper, Marker)

        if lower.is_empty or upper.is_empty:
            if not (lower.is_empty and upper.is_empty):
                raise ValueError(f'Lower {lower!r} and upper {upper!r} must both be empty')
        if lower.bound == Bound.BELOW:
            raise ValueError(f'Present lower {lower!r} should never be BELOW')
        if upper.bound == Bound.ABOVE:
            raise ValueError(f'Present upper {upper!r} should never be ABOVE')
        if lower.value is not None and upper.value is not None and lower.value > upper.value:
            raise ValueError(f'Lower {lower!r} > upper {upper!r}')

    @classmethod
    def of(cls, lower_value, lower_bound, upper_value, upper_bound) -> 'Span':
        return Span(Marker.of(lower_value, lower_bound), Marker.of(upper_value, upper_bound))

    @property
    def lower(self) -> Marker[T]:
        return self._lower

    @property
    def upper(self) -> Marker[T]:
        return self._upper

    defs.repr('lower', 'upper')
    defs.hash_eq('lower', 'upper')

    def __contains__(self, item: Marker[T]) -> bool:
        """Only supported for bounded spans."""

        if type(self) is not Marker:
            return NotImplemented
        else:
            return not (self.upper < item) and not (item < self.lower)

    def __str__(self) -> str:
        if self.is_empty:
            return '()'
        lblock = '[' if self.lower.bound == Bound.EXACTLY else '('
        rblock = ']' if self.upper.bound == Bound.EXACTLY else ')'
        lvalue = '...' if self.lower.value is None else str(self.lower.value)
        rvalue = '...' if self.upper.value is None else str(self.upper.value)
        return lblock + lvalue + ',' + rvalue + rblock

    PARSE_PATTERN = re.compile(r'([\(\[])([^,]+),([^\]\)]+)([\)\]])')

    @classmethod
    def parse(cls, s: str, *, coerce: ta.Callable[[str], T] = str) -> 'Span[T]':
        match = cls.PARSE_PATTERN.match(s)
        if not match:
            raise ValueError(s)
        lb, lv, uv, ub = match.groups()
        lv = coerce(lv) if lv != '...' else None
        uv = coerce(uv) if uv != '...' else None
        return cls(
            Marker.UNBOUNDED_ABOVE if lv is None else Marker(lv, Bound.ABOVE if lb == '(' else Bound.EXACTLY),
            Marker.UNBOUNDED_BELOW if uv is None else Marker(uv, Bound.BELOW if ub == ')' else Bound.EXACTLY),
        )

    @property
    def is_empty(self) -> bool:
        if self.lower.is_empty:
            return True
        elif self.lower.bound == Bound.EXACTLY and self.upper.bound == Bound.EXACTLY:
            return False
        elif self.lower.is_unbounded or self.upper.is_unbounded:
            return False
        else:
            return not self.lower.value < self.upper.value

    @property
    def is_unbounded(self) -> bool:
        return self.lower.is_unbounded and self.upper.is_unbounded

    def to_dict(self) -> dict:
        return {
            'lower': self.lower.to_dict(),
            'upper': self.upper.to_dict(),
        }

    @classmethod
    def from_dict(cls, dct):
        check.arg(set(dct.keys()) == {'lower', 'upper'})
        return cls(Marker.from_dict(dct['lower']), Marker.from_dict(dct['upper']))

    to_json = _to_json = to_dict
    from_json = _from_json = from_dict


Span.UNBOUNDED = Span(Marker.UNBOUNDED_ABOVE, Marker.UNBOUNDED_BELOW)
Span.EMPTY = Span(Marker.EMPTY, Marker.EMPTY)


def _mod_align_up(value: T, alignment: U) -> T:
    modulo = value % alignment
    if modulo:
        return value + (alignment - modulo)
    else:
        return value


def _equiv(l: T, r: T) -> bool:
    return not (l < r or r < l)


def aligned_range(
        span: Span[T],
        alignment: U,
        align_up: ta.Callable[[T, U], T] = _mod_align_up
) -> ta.Iterator[Span[T]]:
    check.not_none(span.lower.value)
    check.not_none(span.upper.value)

    def yield_inclusive_aligned_values() -> ta.Iterator[T]:
        cur = align_up(span.lower.value, alignment)
        while cur < span.upper.value:
            yield cur
            cur += alignment

        # If equiv and span.upper is BELOW do not yield redundant marker.
        if _equiv(cur, span.upper.value) and span.upper.bound != Bound.BELOW:
            yield cur

    def yield_inclusive_aligned_lower_markers() -> ta.Iterator[Marker[T]]:
        yield span.lower

        it = yield_inclusive_aligned_values()
        try:
            value = next(it)
        except StopIteration:
            pass
        else:
            # If equiv and span.lower is ABOVE do not yield unordered EXACTLY.
            # If equiv and span.lower is EXACTLY do not yield redundant marker.
            if not _equiv(value, span.lower.value):
                yield Marker(value, Bound.EXACTLY)

        for value in it:
            yield Marker(value, Bound.EXACTLY)

    def yield_spans() -> ta.Iterator[Span[T]]:
        it = yield_inclusive_aligned_lower_markers()
        lower = next(it)

        for next_lower in it:
            yield Span(lower, Marker(next_lower.value, Bound.BELOW))
            lower = next_lower

        yield Span(lower, span.upper)

    return yield_spans()
