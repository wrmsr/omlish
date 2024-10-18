import dataclasses as dc
import itertools
import typing as ta


T = ta.TypeVar('T')
S = ta.TypeVar('S')
R = ta.TypeVar('R')


BUILTIN_SCALAR_ITERABLE_TYPES: tuple[type, ...] = (
    bytearray,
    bytes,
    str,
)


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


@dc.dataclass(frozen=True)
class itergen(ta.Generic[T]):  # noqa
    fn: ta.Callable[[], ta.Iterable[T]]

    def __iter__(self):
        return iter(self.fn())


def renumerate(it: ta.Iterable[T]) -> ta.Iterable[tuple[T, int]]:
    return ((e, i) for i, e in enumerate(it))


flatten = itertools.chain.from_iterable


def flatmap(fn: ta.Callable[[T], ta.Iterable[R]], it: ta.Iterable[T]) -> ta.Iterable[R]:
    return flatten(map(fn, it))


class Generator(ta.Generator[T, S, R]):
    def __init__(self, gen: ta.Generator[T, S, R]) -> None:
        super().__init__()
        self.gen = gen

    value: R

    def __iter__(self):
        return self

    def __next__(self):
        return self.send(None)

    def send(self, v):
        try:
            return self.gen.send(v)
        except StopIteration as e:
            self.value = e.value
            raise

    def throw(self, *args):
        try:
            return self.gen.throw(*args)
        except StopIteration as e:
            self.value = e.value
            raise

    def close(self):
        self.gen.close()
