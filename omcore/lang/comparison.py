import typing as ta


_comparison: ta.Any
try:
    from . import _comparison  # type: ignore
except ImportError:
    _comparison = None


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


def cmp(l: ta.Any, r: ta.Any) -> int:
    return (l > r) - (l < r)


def hash_eq_id_cmp(l: ta.Any, r: ta.Any) -> int:
    if l is r or l == r:
        return 0

    hl = hash(l)
    hr = hash(r)
    if hl < hr:
        return -1
    elif hl > hr:
        return 1

    il = id(l)
    ir = id(r)

    return (il > ir) - (il < ir)


def key_cmp(fn: ta.Callable[[K, K], int] | None = None) -> ta.Callable[[tuple[K, V], tuple[K, V]], int]:
    if fn is None:
        fn = cmp
    return lambda t0, t1: fn(t0[0], t1[0])


if _comparison is not None:
    globals().update({a: getattr(_comparison, a) for a in [
        'cmp',
        'hash_eq_id_cmp',
        'key_cmp',
    ]})


##


class InfinityType:
    def __repr__(self) -> str:
        return 'Infinity'

    def __hash__(self) -> int:
        return hash(repr(self))

    def __lt__(self, other: ta.Any) -> bool:
        return False

    def __le__(self, other: ta.Any) -> bool:
        return False

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__)

    def __gt__(self, other: ta.Any) -> bool:
        return True

    def __ge__(self, other: ta.Any) -> bool:
        return True

    def __neg__(self: ta.Any) -> NegativeInfinityType:
        return NegativeInfinity


Infinity = InfinityType()


class NegativeInfinityType:
    def __repr__(self) -> str:
        return '-Infinity'

    def __hash__(self) -> int:
        return hash(repr(self))

    def __lt__(self, other: ta.Any) -> bool:
        return True

    def __le__(self, other: ta.Any) -> bool:
        return True

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__)

    def __gt__(self, other: ta.Any) -> bool:
        return False

    def __ge__(self, other: ta.Any) -> bool:
        return False

    def __neg__(self: ta.Any) -> InfinityType:
        return Infinity


NegativeInfinity = NegativeInfinityType()
