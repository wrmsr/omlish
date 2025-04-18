import abc
import typing as ta

from ..lite.maybes import Maybe as _LiteMaybe
from ..lite.maybes import as_maybe as _as_lite_maybe


T = ta.TypeVar('T')
U = ta.TypeVar('U')


##


class ValueNotPresentException(BaseException):
    pass


class Maybe(abc.ABC, ta.Generic[T]):
    @property
    @abc.abstractmethod
    def present(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def must(self) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def __call__(self) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def __iter__(self) -> ta.Iterator[T]:
        raise NotImplementedError

    @abc.abstractmethod
    def __getitem__(self, item: int) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def if_present(self, consumer: ta.Callable[[T], None]) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def filter(self, predicate: ta.Callable[[T], bool]) -> 'Maybe[T]':
        raise NotImplementedError

    @abc.abstractmethod
    def map(self, mapper: ta.Callable[[T], U]) -> 'Maybe[U]':
        raise NotImplementedError

    @abc.abstractmethod
    def flat_map(self, mapper: ta.Callable[[T], 'Maybe[U]']) -> 'Maybe[U]':
        raise NotImplementedError

    @abc.abstractmethod
    def or_else(self, other: T | U) -> T | U:
        raise NotImplementedError

    @abc.abstractmethod
    def or_else_get(self, supplier: ta.Callable[[], U]) -> T | U:
        raise NotImplementedError

    @abc.abstractmethod
    def or_else_raise(self, exception_supplier: ta.Callable[[], Exception]) -> T:
        raise NotImplementedError


class _Maybe(Maybe[T], tuple):
    __slots__ = ()

    def __init_subclass__(cls, **kwargs):
        raise TypeError

    @property
    def present(self) -> bool:
        return bool(self)

    def must(self) -> T:
        if not self:
            raise ValueNotPresentException
        return self[0]

    __call__ = must

    def __iter__(self) -> ta.Iterator[T]:
        raise TypeError

    locals()['__iter__'] = tuple.__iter__

    def __getitem__(self, item: int) -> T:  # type: ignore
        raise TypeError

    locals()['__getitem__'] = tuple.__getitem__

    def if_present(self, consumer: ta.Callable[[T], None]) -> None:
        if self:
            consumer(self[0])

    def filter(self, predicate: ta.Callable[[T], bool]) -> Maybe[T]:
        return self if self and predicate(self[0]) else _empty

    def map(self, mapper: ta.Callable[[T], U]) -> Maybe[U]:
        if self:
            return just(mapper(self[0]))
        return _empty  # noqa

    def flat_map(self, mapper: ta.Callable[[T], Maybe[U]]) -> Maybe[U]:
        if self:
            value = mapper(self[0])
            if not isinstance(value, Maybe):
                raise TypeError(value)
            return value
        return _empty  # noqa

    def or_else(self, other: T | U) -> T | U:
        return self.must() if self else other

    def or_else_get(self, supplier: ta.Callable[[], T | U]) -> T | U:
        return self.must() if self else supplier()

    def or_else_raise(self, exception_supplier: ta.Callable[[], Exception]) -> T:
        if self:
            return self.must()
        raise exception_supplier()


#


def just(v: T) -> Maybe[T]:
    return tuple.__new__(_Maybe, (v,))  # noqa


_empty = tuple.__new__(_Maybe, ())


def empty() -> Maybe[T]:
    return _empty  # noqa


def maybe(o: T | None) -> Maybe[T]:
    if o is None:
        return _empty  # noqa
    return just(o)


##


@_as_lite_maybe.register
def _(obj: Maybe) -> _LiteMaybe:
    if obj.present:
        return _LiteMaybe.just(obj.must())
    else:
        return _LiteMaybe.empty()
