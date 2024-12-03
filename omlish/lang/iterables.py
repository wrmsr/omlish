import dataclasses as dc
import itertools
import typing as ta

from .maybes import Maybe


T = ta.TypeVar('T')
I = ta.TypeVar('I')
O = ta.TypeVar('O')
R = ta.TypeVar('R')


BUILTIN_SCALAR_ITERABLE_TYPES: tuple[type, ...] = (
    bytearray,
    bytes,
    str,
)


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


##


class Generator(ta.Generator[O, I, R]):
    def __init__(self, g: ta.Generator[O, I, R]) -> None:
        super().__init__()
        self._g = g

    @property
    def g(self) -> ta.Generator[O, I, R]:
        return self._g

    value: R

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return next(self._g)
        except StopIteration as e:
            self.value = e.value
            raise

    def send(self, v):
        try:
            return self._g.send(v)
        except StopIteration as e:
            self.value = e.value
            raise

    def throw(self, *args):
        try:
            return self._g.throw(*args)
        except StopIteration as e:
            self.value = e.value
            raise

    def close(self):
        self._g.close()


##


class CoroutineGenerator(ta.Generic[O, I, R]):
    def __init__(self, g: ta.Generator[O, I, R]) -> None:
        super().__init__()
        self._g = g

    @property
    def g(self) -> ta.Generator[O, I, R]:
        return self._g

    #

    def close(self) -> None:
        self._g.close()

    def __enter__(self) -> ta.Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._g.close()

    #

    class Output(ta.NamedTuple, ta.Generic[T]):
        v: T

        @property
        def is_return(self) -> bool:
            raise NotImplementedError

    class Yield(Output[T]):
        @property
        def is_return(self) -> bool:
            return False

    class Return(Output[T]):
        @property
        def is_return(self) -> bool:
            return True

    class Nothing:
        def __new__(cls):
            raise TypeError

    #

    def send(self, /, v: I | type[Nothing] = Nothing) -> Yield[O] | Return[R]:
        try:
            if v is self.Nothing:
                o = next(self._g)
            else:
                o = self._g.send(v)  # type: ignore[arg-type]
        except StopIteration as e:
            return self.Return(e.value)
        else:
            return self.Yield(o)

    def send_opt(self, v: I | None) -> Yield[O] | Return[R]:
        return self.send(v if v is not None else self.Nothing)

    def send_maybe(self, v: Maybe[I]) -> Yield[O] | Return[R]:
        return self.send(v.or_else(self.Nothing))

    def throw(self, v: BaseException) -> Yield[O] | Return[R]:
        try:
            o = self._g.throw(v)
        except StopIteration as e:
            return self.Return(e.value)
        else:
            return self.Yield(o)


corogen = CoroutineGenerator
