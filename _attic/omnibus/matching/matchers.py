import typing as ta

from .patterns import CapturePattern
from .patterns import EqualsPattern
from .patterns import FilterPattern
from .patterns import TypePattern
from .patterns import WithPattern
from .types import Captures
from .types import Match
from .types import Pattern


T = ta.TypeVar('T')


class Matcher(ta.Generic[T]):

    def match(self, pattern: Pattern[T], value: ta.Any, captures: Captures = Captures.empty()) -> Match[T]:
        raise TypeError(pattern)

    def match_capture(self, pattern: CapturePattern[T], value: ta.Any, captures: Captures) -> Match[T]:
        return self.match(pattern, value, captures)

    def match_equals(self, pattern: EqualsPattern[T], value: ta.Any, captures: Captures) -> Match[T]:
        return self.match(pattern, value, captures)

    def match_filter(self, pattern: FilterPattern[T], value: ta.Any, captures: Captures) -> Match[T]:
        return self.match(pattern, value, captures)

    def match_type(self, pattern: TypePattern[T], value: ta.Any, captures: Captures) -> Match[T]:
        return self.match(pattern, value, captures)

    def match_with(self, pattern: WithPattern[T], value: ta.Any, captures: Captures) -> Match[T]:
        return self.match(pattern, value, captures)


class DefaultMatcher(Matcher[T]):

    def match(self, pattern: Pattern[T], value: ta.Any, captures: Captures = Captures.empty()) -> Match[T]:
        if pattern.next is not None:
            match = self.match(pattern.next, value, captures)
            return match.flat_map(lambda v: pattern.accept_matcher(self, v, match.captures))
        else:
            return pattern.accept_matcher(self, value, captures)

    def match_capture(self, pattern: CapturePattern[T], value: ta.Any, captures: Captures) -> Match[T]:
        return Match.of(value, captures.add_all(Captures.of_optional(pattern.capture, value)))

    def match_equals(self, pattern: EqualsPattern[T], value: ta.Any, captures: Captures) -> Match[T]:
        return Match.of(value, captures).filter(lambda v: pattern.value == v)

    def match_filter(self, pattern: FilterPattern[T], value: ta.Any, captures: Captures) -> Match[T]:
        return Match.of(value, captures).filter(pattern.predicate)

    def match_type(self, pattern: TypePattern[T], value: ta.Any, captures: Captures) -> Match[T]:
        if isinstance(value, pattern.cls):
            return Match.of(value, captures)
        else:
            return Match.empty()

    def match_with(self, pattern: WithPattern[T], value: ta.Any, captures: Captures) -> Match[T]:
        property_value = pattern.property.function(value)
        property_match = property_value \
            .map(lambda v: self.match(pattern.pattern, value, captures)) \
            .or_else(Match.empty())
        return property_match.map(lambda _: value)
