import abc
import dataclasses as dc
import itertools
import typing as ta

from .. import lang


T = ta.TypeVar('T')
U = ta.TypeVar('U')

Transform: ta.TypeAlias = ta.Callable[[ta.Iterable[T]], ta.Iterable[U]]

X0 = ta.TypeVar('X0')
X1 = ta.TypeVar('X1')
X2 = ta.TypeVar('X2')
X3 = ta.TypeVar('X3')
X4 = ta.TypeVar('X4')
X5 = ta.TypeVar('X5')


##


_filter = filter
_map = map
_zip = zip


##


class Transform_(lang.Abstract, ta.Generic[T, U]):  # noqa
    @abc.abstractmethod
    def __call__(self, it: ta.Iterable[T]) -> ta.Iterable[U]:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class Filter(Transform_[T, T]):
    fn: ta.Callable[[T], bool] | None

    def __call__(self, it: ta.Iterable[T]) -> ta.Iterable[T]:
        return _filter(self.fn, it)


filter = Filter  # noqa


##


@dc.dataclass(frozen=True)
class Map(Transform_[T, U]):
    fn: ta.Callable[[T], U]

    def __call__(self, it: ta.Iterable[T]) -> ta.Iterable[U]:
        return _map(self.fn, it)


map = Map  # noqa


##


@dc.dataclass(frozen=True)
class Apply(Transform_[T, T]):
    fn: ta.Callable[[T], ta.Any]

    def __call__(self, it: ta.Iterable[T]) -> ta.Iterable[T]:
        return _map(lambda e: (self.fn(e), e)[1], it)


apply = Apply


##


@dc.dataclass(frozen=True)
class Flatten(Transform_[ta.Iterable[T], T]):
    def __call__(self, it: ta.Iterable[ta.Iterable[T]]) -> ta.Iterable[T]:
        return itertools.chain.from_iterable(it)


flatten = Flatten


##


@dc.dataclass(frozen=True)
class FlatMap(Transform_[T, U]):
    fn: ta.Callable[[T], ta.Iterable[U]]

    def __call__(self, it: ta.Iterable[T]) -> ta.Iterable[U]:
        return itertools.chain.from_iterable(_map(self.fn, it))


flat_map = FlatMap

# Alternatively:
# def flat_map(fn: ta.Callable[[T], ta.Iterable[U]]) -> Transform[T, U]:
#     return compose(map(fn), flatten())


##


@dc.dataclass(frozen=True)
class Compose(Transform_[T, U]):
    tfs: ta.Sequence[Transform]

    def __call__(self, it: ta.Iterable[T]) -> ta.Iterable[U]:
        for tf in self.tfs:
            it = tf(it)
        return it  # type: ignore[return-value]


@ta.overload
def compose(
        tf0: Transform[T, U],
) -> Transform[T, U]:
    ...


@ta.overload
def compose(
        tf0: Transform[T, X0],
        tf1: Transform[X0, U],
) -> Transform[T, U]:
    ...


@ta.overload
def compose(
        tf0: Transform[T, X0],
        tf1: Transform[X0, X1],
        tf2: Transform[X1, U],
) -> Transform[T, U]:
    ...


@ta.overload
def compose(
        tf0: Transform[T, X0],
        tf1: Transform[X0, X1],
        tf2: Transform[X1, X2],
        tf3: Transform[X2, U],
) -> Transform[T, U]:
    ...


@ta.overload
def compose(
        tf0: Transform[T, X0],
        tf1: Transform[X0, X1],
        tf2: Transform[X1, X2],
        tf3: Transform[X2, X3],
        tf4: Transform[X3, U],
) -> Transform[T, U]:
    ...


@ta.overload
def compose(
        tf0: Transform[T, X0],
        tf1: Transform[X0, X1],
        tf2: Transform[X1, X2],
        tf3: Transform[X2, X3],
        tf4: Transform[X3, X4],
        tf5: Transform[X4, U],
) -> Transform[T, U]:
    ...


@ta.overload
def compose(
        tf0: Transform[T, X0],
        tf1: Transform[X0, X1],
        tf2: Transform[X1, X2],
        tf3: Transform[X2, X3],
        tf4: Transform[X3, X4],
        tf5: Transform[X4, X5],
        tf6: Transform[X5, U],
) -> Transform[T, U]:
    ...


@ta.overload
def compose(
        *tf: Transform,
) -> Transform:
    ...


def compose(tf0, *tfn):
    if not tfn:
        return tf0
    return Compose([tf0, *tfn])
