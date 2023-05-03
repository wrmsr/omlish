import abc
import typing as ta


T = ta.TypeVar('T')


##


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


##


class _Just(Maybe[T]):

    def __init__(self, v: T) -> None:
        super().__init__()
        self._v = v

    @property
    def present(self) -> bool:
        return True

    def must(self) -> T:
        return self._v

    def __iter__(self) -> ta.Iterator[T]:
        yield self._v


just = _Just


##


class ValueNotPresentException(BaseException):
    pass


class _Empty(Maybe[T]):
    @property
    def present(self) -> bool:
        return False

    def must(self) -> T:
        raise ValueNotPresentException

    def __iter__(self) -> ta.Iterator[T]:
        return
        yield  # noqa


_empty = _Empty[ta.Any]()


def empty() -> Maybe[T]:
    return _empty  # type: ignore
