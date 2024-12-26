import dataclasses as dc
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


def exhaust(it: ta.Iterable[ta.Any]) -> None:
    for _ in it:
        pass


def peek(vs: ta.Iterable[T]) -> tuple[T, ta.Iterator[T]]:
    it = iter(vs)
    v = next(it)
    return v, itertools.chain(iter((v,)), it)


def interleave(vs: ta.Iterable[T], d: T) -> ta.Iterable[T]:
    for i, v in enumerate(vs):
        if i:
            yield d
        yield v


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


@dc.dataclass(frozen=True)
class IterGen(ta.Generic[T]):
    fn: ta.Callable[[], ta.Iterable[T]]

    def __iter__(self):
        return iter(self.fn())


itergen = IterGen


def renumerate(it: ta.Iterable[T]) -> ta.Iterable[tuple[T, int]]:
    return ((e, i) for i, e in enumerate(it))


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
