import abc
import typing as ta


T = ta.TypeVar('T')


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
    def __iter__(self) -> ta.Iterator[T]:
        raise NotImplementedError


class _Maybe(Maybe[T], tuple):

    @property
    def present(self) -> bool:
        return bool(self)

    def must(self) -> T:
        if not self:
            raise ValueNotPresentException
        return self[0]

    def __iter__(self):
        raise TypeError

    locals()['__iter__'] = tuple.__iter__


def just(v: T) -> Maybe[T]:
    return tuple.__new__(_Maybe, (v,))


_empty = tuple.__new__(_Maybe, ())


def empty() -> Maybe[T]:
    return _empty  # type: ignore


def maybe(o: ta.Optional[T]) -> Maybe[T]:
    if o is None:
        return _empty
    return tuple.__new__(_Maybe, (o,))
