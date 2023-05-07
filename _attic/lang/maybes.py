import functools
import typing as ta

from .classes import Final


T = ta.TypeVar('T')
U = ta.TypeVar('U')


class MaybeNotPresentException(ValueError):
    pass


@functools.total_ordering
class Maybe(Final, ta.Generic[T], tuple):
    """~java.util.Optional"""

    EMPTY: 'Maybe'

    def __new__(cls, arg: T) -> 'Maybe[T]':
        return tuple.__new__(cls, (arg,))

    @classmethod
    def of_optional(cls, value: ta.Optional[T]) -> 'Maybe[T]':
        return cls(value) if value is not None else Maybe.EMPTY

    def __iter__(self) -> ta.Iterator[T]:
        raise TypeError

    locals()['__iter__'] = tuple.__iter__

    def __eq__(self, other):
        if type(other) is not Maybe:
            return False
        return tuple.__eq__(self, other)

    def __ne__(self, other):
        if type(other) is not Maybe:
            return True
        return tuple.__ne__(self, other)

    def __lt__(self, other):
        if type(other) is not Maybe:
            raise TypeError(other)
        return tuple.__lt__(self, other)

    @property
    def value(self) -> T:
        try:
            return self[0]
        except IndexError:
            raise MaybeNotPresentException

    @classmethod
    def _empty(cls):
        return tuple.__new__(cls, ())

    @staticmethod
    def empty() -> 'Maybe[T]':
        return Maybe.EMPTY

    def if_present(self, consumer: ta.Callable[[T], None]) -> None:
        if self:
            consumer(self[0])

    def filter(self, predicate: ta.Callable[[T], bool]) -> 'Maybe[T]':
        return self if self and predicate(self[0]) else Maybe.EMPTY

    def map(self, mapper: ta.Callable[[T], U]) -> 'Maybe[U]':
        if self:
            value = mapper(self[0])
            if value is not None:
                return Maybe(value)
        return Maybe.EMPTY

    def flat_map(self, mapper: ta.Callable[[T], 'Maybe[U]']) -> 'Maybe[U]':
        if self:
            value = mapper(self[0])
            if not isinstance(value, Maybe):
                raise TypeError(value)
            return value
        return Maybe.EMPTY

    def or_else(self, other: T) -> 'Maybe[T]':
        return self if self else Maybe(other)

    def or_else_get(self, supplier: ta.Callable[[], T]) -> 'Maybe[T]':
        return self if self else Maybe(supplier())

    def or_else_raise(self, exception_supplier: ta.Callable[[], Exception]) -> 'Maybe[T]':
        if self:
            return self
        raise exception_supplier()


Maybe.EMPTY = Maybe._empty()


def maybe(*args: T) -> Maybe[T]:
    if args:
        [value] = args
        return Maybe(value)
    else:
        return Maybe.EMPTY
