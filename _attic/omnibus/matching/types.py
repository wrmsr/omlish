import abc
import typing as ta

from .. import check
from .. import defs
from .. import lang


F = ta.TypeVar('F')
T = ta.TypeVar('T')
U = ta.TypeVar('U')
R = ta.TypeVar('R')
C = ta.TypeVar('C')


patterns = lang.lazy_import('.patterns', __package__)


# region Captures


class Capture(ta.Generic[T]):
    pass


class Captures:

    _NIL: 'Captures'

    def __init__(self, capture: Capture, value: ta.Any, next: 'Captures') -> None:
        super().__init__()

        self._capture = capture
        self._value = value
        self._next = next

    defs.repr('capture', 'value')

    @property
    def capture(self) -> Capture:
        return self._capture

    @property
    def value(self) -> ta.Any:
        return self._value

    @staticmethod
    def of_optional(capture: 'Capture[T]', value: ta.Optional[T]) -> 'Captures':
        return Captures(capture, value, Captures._NIL) if value is not None else Captures._NIL

    def add_all(self, other: 'Captures') -> 'Captures':
        if self is Captures._NIL:
            return other
        else:
            return Captures(self._capture, self._value, self._next.add_all(other))

    def get(self, capture: 'Capture[T]') -> T:
        if self is Captures._NIL:
            raise TypeError
        elif self._capture is capture:
            return self._value
        else:
            return self._next.get(capture)

    @staticmethod
    def empty() -> 'Captures':
        return Captures._NIL


Captures._NIL = Captures(None, None, None)


# endregion


# region Matches


class Match(lang.Sealed, lang.Abstract, ta.Generic[T]):

    @abc.abstractproperty
    def is_present(self) -> bool:
        raise NotImplementedError

    @abc.abstractproperty
    def value(self) -> T:
        raise NotImplementedError

    @abc.abstractproperty
    def captures(self) -> 'Captures':
        raise NotImplementedError

    @abc.abstractmethod
    def filter(self, predicate: ta.Callable[[T], bool]) -> 'Match[T]':
        raise NotImplementedError

    @abc.abstractmethod
    def map(self, mapper: ta.Callable[[T], U]) -> 'Match[T]':
        raise NotImplementedError

    @abc.abstractmethod
    def flat_map(self, mapper: ta.Callable[[T], 'Match[U]']) -> 'Match[T]':
        raise NotImplementedError

    @classmethod
    def of(cls, value: T, captures: 'Captures') -> 'Match[T]':
        return PresentMatch(value, captures)

    @classmethod
    def empty(cls) -> 'Match[T]':
        return EmptyMatch()


class PresentMatch(Match[T]):

    def __init__(self, value: T, captures: 'Captures') -> None:
        super().__init__()

        self._value = value
        self._captures = captures

    @property
    def value(self) -> T:
        return self._value

    @property
    def captures(self) -> 'Captures':
        return self._captures

    @property
    def is_present(self) -> bool:
        return True

    def filter(self, predicate: ta.Callable[[T], bool]) -> 'Match[T]':
        return self if predicate(self._value) else Match.empty()

    def map(self, mapper: ta.Callable[[T], U]) -> 'Match[T]':
        return Match.of(mapper(self._value), self._captures)

    def flat_map(self, mapper: ta.Callable[[T], 'Match[U]']) -> 'Match[T]':
        return mapper(self._value)


class EmptyMatch(Match[T]):

    @property
    def is_present(self) -> bool:
        return False

    @property
    def value(self) -> bool:
        raise TypeError

    @property
    def captures(self) -> 'Captures':
        raise TypeError

    def filter(self, predicate: ta.Callable[[T], bool]) -> 'Match[T]':
        return self

    def map(self, mapper: ta.Callable[[T], U]) -> 'Match[T]':
        return self

    def flat_map(self, mapper: ta.Callable[[T], 'Match[U]']) -> 'Match[T]':
        return self


# endregion


# region Properties


class Property(lang.Final, ta.Generic[F, T]):

    def __init__(self, function: ta.Callable[[F], lang.Maybe[T]]) -> None:
        super().__init__()

        self._function = check.callable(function)

    @property
    def function(self) -> ta.Callable[[F], lang.Maybe[T]]:
        return self._function

    @classmethod
    def of(cls, function: ta.Callable[[F], T]) -> 'Property[F, T]':
        return cls(lambda v: lang.Maybe(function(v)))

    def matching(self, pattern: 'Pattern[R]') -> 'PropertyPatternPair[F, R]':
        return PropertyPatternPair(self, pattern)

    def capturing(self, capture: Capture[T]) -> 'PropertyPatternPair[F, T]':
        return self.matching(Pattern.any().captured(capture))

    def equaling(self, value: T) -> 'PropertyPatternPair[F, T]':
        return self.matching(patterns().EqualsPattern(value, None))

    def filtering(self, predicate: ta.Callable[[T], bool]) -> 'PropertyPatternPair[F, T]':
        return self.matching(patterns().FilterPattern(predicate, None))


class PropertyPatternPair(ta.Generic[F, R]):

    def __init__(self, property: Property[F, ta.Any], pattern: 'Pattern[R]') -> None:
        super().__init__()

        self._property = check.isinstance(property, Property)
        self._pattern = check.isinstance(pattern, Pattern)

    @property
    def pattern(self) -> 'Pattern[R]':
        return self._pattern

    @property
    def property(self) -> 'Property[F, ta.Any]':
        return self._property


# endregion


# region Patterns


class Pattern(lang.Abstract, ta.Generic[T]):

    @abc.abstractproperty
    def next(self) -> ta.Optional['Pattern']:
        raise NotImplementedError

    @abc.abstractmethod
    def accept(self, visitor: 'Visitor[R, C]', context: C) -> R:
        raise NotImplementedError

    @abc.abstractmethod
    def accept_matcher(self, matcher: 'Matcher[T]', value: ta.Any, captures: Captures) -> Match[T]:
        raise NotImplementedError

    @classmethod
    def any(cls) -> 'Pattern[ta.Any]':
        return cls.typed(object)

    @classmethod
    def typed(cls, cls_: ta.Type[T]) -> 'Pattern[T]':
        return patterns().TypePattern(cls_)

    @abc.abstractmethod
    def captured(self, capture: Capture[T]) -> 'Pattern[T]':
        raise NotImplementedError

    @abc.abstractmethod
    def filtered(self, predicate: ta.Callable[[T], bool]) -> 'Pattern[T]':
        raise NotImplementedError

    @abc.abstractmethod
    def with_(self, property_pattern_pair: PropertyPatternPair[T, ta.Any]) -> 'Pattern[T]':
        raise NotImplementedError


# endregion
