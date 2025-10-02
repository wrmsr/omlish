# ruff: noqa: UP007 UP045
import abc
import functools
import operator
import typing as ta

from .abstract import Abstract


T = ta.TypeVar('T')
U = ta.TypeVar('U')


##


@functools.total_ordering
class Maybe(ta.Generic[T]):
    class ValueNotPresentError(BaseException):
        pass

    #

    @property
    @abc.abstractmethod
    def present(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def must(self) -> T:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def __hash__(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def __eq__(self, other) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def __lt__(self, other) -> bool:
        raise NotImplementedError

    #

    @ta.final
    def __ne__(self, other):
        return not (self == other)

    @ta.final
    def __iter__(self) -> ta.Iterator[T]:
        if self.present:
            yield self.must()

    @ta.final
    def __bool__(self) -> ta.NoReturn:
        raise TypeError

    #

    @ta.final
    def if_present(self, consumer: ta.Callable[[T], None]) -> None:
        if self.present:
            consumer(self.must())

    @ta.final
    def filter(self, predicate: ta.Callable[[T], bool]) -> 'Maybe[T]':
        if self.present and predicate(self.must()):
            return self
        else:
            return Maybe.empty()

    @ta.final
    def map(self, mapper: ta.Callable[[T], U]) -> 'Maybe[U]':
        if self.present:
            return Maybe.just(mapper(self.must()))
        else:
            return Maybe.empty()

    @ta.final
    def flat_map(self, mapper: ta.Callable[[T], 'Maybe[U]']) -> 'Maybe[U]':
        if self.present:
            if not isinstance(v := mapper(self.must()), Maybe):
                raise TypeError(v)
            return v
        else:
            return Maybe.empty()

    @ta.final
    def or_else(self, other: ta.Union[T, U]) -> ta.Union[T, U]:
        if self.present:
            return self.must()
        else:
            return other

    @ta.final
    def or_else_get(self, supplier: ta.Callable[[], ta.Union[T, U]]) -> ta.Union[T, U]:
        if self.present:
            return self.must()
        else:
            return supplier()

    @ta.final
    def or_else_raise(self, exception_supplier: ta.Callable[[], Exception]) -> T:
        if self.present:
            return self.must()
        else:
            raise exception_supplier()

    #

    @classmethod
    def of_optional(cls, v: ta.Optional[T]) -> 'Maybe[T]':
        if v is not None:
            return cls.just(v)
        else:
            return cls.empty()

    @classmethod
    def just(cls, v: T) -> 'Maybe[T]':
        return _JustMaybe(v)

    _empty: ta.ClassVar['Maybe']

    @classmethod
    def empty(cls) -> 'Maybe[T]':
        return Maybe._empty


##


class _Maybe(Maybe[T], Abstract):
    def __lt__(self, other):
        if not isinstance(other, _Maybe):
            return NotImplemented
        sp = self.present
        op = other.present
        if self.present and other.present:
            return self.must() < other.must()
        else:
            return op and not sp


@ta.final
class _JustMaybe(_Maybe[T]):
    __slots__ = ('_v', '_hash')

    def __init__(self, v: T) -> None:
        self._v = v

    @property
    def present(self) -> bool:
        return True

    def must(self) -> T:
        return self._v

    #

    def __repr__(self) -> str:
        return f'just({self._v!r})'

    _hash: int

    def __hash__(self) -> int:
        try:
            return self._hash
        except AttributeError:
            pass
        h = self._hash = hash((_JustMaybe, self._v))
        return h

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__ and
            self._v == other._v  # noqa
        )


@ta.final
class _EmptyMaybe(_Maybe[T]):
    __slots__ = ()

    @property
    def present(self) -> bool:
        return False

    def must(self) -> T:
        raise Maybe.ValueNotPresentError

    #

    def __repr__(self) -> str:
        return 'empty()'

    def __hash__(self) -> int:
        return hash(_EmptyMaybe)

    def __eq__(self, other):
        return self.__class__ is other.__class__


Maybe._empty = _EmptyMaybe()  # noqa


##


setattr(Maybe, 'just', _JustMaybe)  # noqa
setattr(Maybe, 'empty', functools.partial(operator.attrgetter('_empty'), Maybe))
