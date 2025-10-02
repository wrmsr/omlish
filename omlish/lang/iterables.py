import collections
import functools
import itertools
import typing as ta


T = ta.TypeVar('T')
R = ta.TypeVar('R')


##


def ilen(it: ta.Iterable) -> int:
    c = 0
    for _ in it:
        c += 1
    return c


def take(n: int, it: ta.Iterable[T]) -> list[T]:
    return list(itertools.islice(it, n))


def consume(it: ta.Iterable[ta.Any]) -> None:
    collections.deque(it, maxlen=0)


def peek(vs: ta.Iterable[T]) -> tuple[T, ta.Iterator[T]]:
    it = iter(vs)
    v = next(it)
    return v, itertools.chain(iter((v,)), it)


def chunk(n: int, iterable: ta.Iterable[T], strict: bool = False) -> ta.Iterator[list[T]]:
    # TODO: replace with itertools.batched in 3.13 - 3.12 doesn't support strict
    iterator = iter(functools.partial(take, n, iter(iterable)), [])
    if strict:
        def ret():
            for c in iterator:
                if len(c) != n:
                    raise ValueError('iterable is not divisible by n.')
                yield c
        return iter(ret())
    else:
        return iterator


def interleave(vs: ta.Iterable[T], d: T) -> ta.Iterator[T]:
    for i, v in enumerate(vs):
        if i:
            yield d
        yield v


def renumerate(it: ta.Iterable[T]) -> ta.Iterator[tuple[T, int]]:
    return ((e, i) for i, e in enumerate(it))


def common_prefix_len(*its: ta.Iterable) -> int:
    return ilen(itertools.takewhile(lambda t: all(e == t[0] for e in t[1:]), zip(*its)))


##


@ta.overload
def readiter(f: ta.TextIO, sz: int) -> ta.Iterator[str]:
    ...


@ta.overload
def readiter(f: ta.BinaryIO, sz: int) -> ta.Iterator[bytes]:
    ...


@ta.overload
def readiter(f: ta.IO, sz: int) -> ta.Iterator[ta.AnyStr]:
    ...


def readiter(f, sz):
    return iter(functools.partial(f.read, sz), None)


##


@ta.final
class IterGen(ta.Generic[T]):
    def __init__(self, fn: ta.Callable[[], ta.Iterable[T]]) -> None:
        self.fn = fn

    def __iter__(self):
        return iter(self.fn())


itergen = IterGen


##


flatten = itertools.chain.from_iterable


def flatmap(fn: ta.Callable[[T], ta.Iterable[R]], it: ta.Iterable[T]) -> ta.Iterable[R]:
    return flatten(map(fn, it))


##


Rangeable: ta.TypeAlias = ta.Union[  # noqa
    int,
    tuple[int],
    tuple[int, int],
    tuple[int, int, int],
    ta.Iterable[int],
]


def asrange(i: Rangeable) -> ta.Iterable[int]:
    if isinstance(i, int):
        return range(i)
    elif isinstance(i, tuple):
        return range(*i)
    elif isinstance(i, ta.Iterable):
        return i
    else:
        raise TypeError(i)


def prodrange(*dims: Rangeable) -> ta.Iterable[ta.Sequence[int]]:
    if not dims:
        return []
    return itertools.product(*map(asrange, dims))


##


class IteratorWithReturn(ta.Generic[T, R]):
    """Overlap with stuff in generators.py, but intentionally restricted to iteration (no send/throw)."""

    def __init__(self, it: ta.Iterator[T]) -> None:
        super().__init__()

        self._it = it
        self._has_value = False

    _value: R

    @property
    def has_value(self) -> bool:
        return self._has_value

    @property
    def value(self) -> R:
        return self._value

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return next(self._it)
        except StopIteration as e:
            self._has_value = True
            self._value = e.value
            raise
