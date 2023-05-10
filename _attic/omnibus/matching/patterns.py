import abc
import typing as ta

from .. import check
from .. import lang
from .types import Capture
from .types import Captures
from .types import Match
from .types import Pattern
from .types import Property
from .types import PropertyPatternPair


T = ta.TypeVar('T')
R = ta.TypeVar('R')
C = ta.TypeVar('C')


class AbstractPattern(Pattern[T], lang.Abstract):

    def __init__(self, next: ta.Optional['Pattern']) -> None:
        super().__init__()

        self._next = next

    @property
    def next(self) -> ta.Optional['Pattern']:
        return self._next

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
        return TypePattern(cls_)

    def captured(self, capture: Capture[T]) -> 'Pattern[T]':
        return CapturePattern(capture, self)

    def filtered(self, predicate: ta.Callable[[T], bool]) -> 'Pattern[T]':
        return FilterPattern(predicate, self)

    def with_(self, property_pattern_pair: PropertyPatternPair[T, ta.Any]) -> 'Pattern[T]':
        return WithPattern(property_pattern_pair, self)


class CapturePattern(AbstractPattern[T]):

    def __init__(self, capture: Capture[T], next: Pattern) -> None:
        super().__init__(check.not_none(next))

        self._capture = check.isinstance(capture, Capture)

    @property
    def capture(self) -> Capture[T]:
        return self._capture

    def accept(self, visitor: 'Visitor[R, C]', context: C) -> R:
        return visitor.visit_capture(self, context)

    def accept_matcher(self, matcher: 'Matcher[T]', value: ta.Any, captures: Captures) -> Match[T]:
        return matcher.match_capture(self, value, captures)


class EqualsPattern(AbstractPattern[T]):

    def __init__(self, value: T, next: ta.Optional[Pattern]) -> None:
        super().__init__(next)

        self._value = value

    @property
    def value(self) -> T:
        return self._value

    def accept(self, visitor: 'Visitor[R, C]', context: C) -> R:
        return visitor.visit_equals(self, context)

    def accept_matcher(self, matcher: 'Matcher[T]', value: ta.Any, captures: Captures) -> Match[T]:
        return matcher.match_equals(self, value, captures)


class FilterPattern(AbstractPattern[T]):

    def __init__(self, predicate: ta.Callable[[T], bool], next: ta.Optional[Pattern]) -> None:
        super().__init__(next)

        self._predicate = predicate

    @property
    def predicate(self) -> ta.Callable[[T], bool]:
        return self._predicate

    def accept(self, visitor: 'Visitor[R, C]', context: C) -> R:
        return visitor.visit_filter(self, context)

    def accept_matcher(self, matcher: 'Matcher[T]', value: ta.Any, captures: Captures) -> Match[T]:
        return matcher.match_filter(self, value, captures)


class TypePattern(AbstractPattern[T]):

    def __init__(self, cls: ta.Type[T]) -> None:
        super().__init__(None)

        self._cls = cls

    @property
    def cls(self) -> ta.Type[T]:
        return self._cls

    def accept(self, visitor: 'Visitor[R, C]', context: C) -> R:
        return visitor.visit_type(self, context)

    def accept_matcher(self, matcher: 'Matcher[T]', value: ta.Any, captures: Captures) -> Match[T]:
        return matcher.match_type(self, value, captures)


class WithPattern(AbstractPattern[T]):

    def __init__(self, property_pattern_pair: PropertyPatternPair[T, ta.Any], next: ta.Optional[Pattern]) -> None:
        super().__init__(next)

        self._property_pattern_pair = property_pattern_pair

    @property
    def property_pattern_pair(self) -> PropertyPatternPair[T, ta.Any]:
        return self._property_pattern_pair

    @property
    def pattern(self) -> 'Pattern[ta.Any]':
        return self._property_pattern_pair.pattern

    @property
    def property(self) -> 'Property[T, ta.Any]':
        return self._property_pattern_pair.property

    def accept(self, visitor: 'Visitor[R, C]', context: C) -> R:
        return visitor.visit_with(self, context)

    def accept_matcher(self, matcher: 'Matcher[T]', value: ta.Any, captures: Captures) -> Match[T]:
        return matcher.match_with(self, value, captures)


class Visitor(ta.Generic[R, C]):

    def process(self, pattern: Pattern, context: C) -> R:
        return pattern.accept(self, context)

    def visit(self, pattern: Pattern, context: C) -> R:
        raise TypeError(pattern)

    def visit_capture(self, pattern: CapturePattern, context: C) -> R:
        return self.visit(pattern, context)

    def visit_equals(self, pattern: EqualsPattern, context: C) -> R:
        return self.visit(pattern, context)

    def visit_filter(self, pattern: FilterPattern, context: C) -> R:
        return self.visit(pattern, context)

    def visit_type(self, pattern: TypePattern, context: C) -> R:
        return self.visit(pattern, context)

    def visit_with(self, pattern: WithPattern, context: C) -> R:
        return self.visit(pattern, context)
