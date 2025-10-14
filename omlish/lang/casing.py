import abc
import re
import typing as ta

from ..lite.abstract import Abstract


##


class StringCasingError(Exception):
    pass


class ImproperStringCasingError(StringCasingError):
    pass


class UnknownStringCasingError(StringCasingError):
    pass


class AmbiguousStringCasingError(StringCasingError):
    pass


def _check_all_lowercase(*ps: str) -> None:
    for p in ps:
        if p.lower() != p:
            raise ImproperStringCasingError(p)


##


class StringCasing(Abstract):
    @abc.abstractmethod
    def match(self, s: str) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def split(self, s: str) -> list[str]:
        """Returns lowercase."""

        raise NotImplementedError

    @abc.abstractmethod
    def join(self, *parts: str) -> str:
        """Expects lowercase."""

        raise NotImplementedError

    #

    def to(self, other: 'StringCasing') -> ta.Callable[[str], str]:
        def inner(s: str) -> str:
            return other.join(*self.split(s))
        return inner


#


class CamelCase(StringCasing):
    """FooBarBaz"""

    _PAT: ta.ClassVar[re.Pattern] = re.compile(r'[A-Z][a-z0-9]*(?:[A-Z][a-z0-9]*)*')
    _SPLIT_PAT: ta.ClassVar[re.Pattern] = re.compile(r'[A-Z][a-z0-9]*')

    def match(self, s: str) -> bool:
        return bool(self._PAT.fullmatch(s))

    def split(self, s: str) -> list[str]:
        if not self.match(s):
            raise ImproperStringCasingError(f'Not valid CamelCase: {s!r}')
        return [m.group(0).lower() for m in self._SPLIT_PAT.finditer(s)]

    def join(self, *parts: str) -> str:
        _check_all_lowercase(*parts)
        return ''.join(p.capitalize() for p in parts)


#


class LowCamelCase(StringCasing):
    """fooBarBaz"""

    _MATCH_PAT: ta.ClassVar[re.Pattern] = re.compile(r'[a-z][a-z0-9]*(?:[A-Z][a-z0-9]*)*')
    _FIRST_PAT: ta.ClassVar[re.Pattern] = re.compile(r'^[a-z0-9]+')
    _UPPER_PAT: ta.ClassVar[re.Pattern] = re.compile(r'[A-Z][a-z0-9]*')

    def match(self, s: str) -> bool:
        return bool(self._MATCH_PAT.fullmatch(s))

    def split(self, s: str) -> list[str]:
        if not self.match(s):
            raise ImproperStringCasingError(f'Not valid lowCamelCase: {s!r}')
        parts: list[str] = []
        m0 = self._FIRST_PAT.match(s)
        if m0:
            parts.append(m0.group(0))
            start = m0.end()
        else:
            start = 0
        for m in self._UPPER_PAT.finditer(s, pos=start):
            parts.append(m.group(0))
        return [p.lower() for p in parts]

    def join(self, *parts: str) -> str:
        _check_all_lowercase(*parts)
        if not parts:
            return ''
        first, *rest = parts
        return first.lower() + ''.join(p.capitalize() for p in rest)


#


class SnakeCase(StringCasing):
    """foo_bar_baz"""

    _PAT: ta.ClassVar[re.Pattern] = re.compile(r'[a-z0-9]+(?:_[a-z0-9]+)*')

    def match(self, s: str) -> bool:
        return bool(self._PAT.fullmatch(s))

    def split(self, s: str) -> list[str]:
        if not self.match(s):
            raise ImproperStringCasingError(f'Not valid snake_case: {s!r}')
        return s.split('_')

    def join(self, *parts: str) -> str:
        _check_all_lowercase(*parts)
        return '_'.join(p.lower() for p in parts)


#


class UpSnakeCase(StringCasing):
    """FOO_BAR_BAZ"""

    _PAT: ta.ClassVar[re.Pattern] = re.compile(r'[A-Z0-9]+(?:_[A-Z0-9]+)*')

    def match(self, s: str) -> bool:
        return bool(self._PAT.fullmatch(s))

    def split(self, s: str) -> list[str]:
        if not self.match(s):
            raise ImproperStringCasingError(f'Not valid UPPER_SNAKE_CASE: {s!r}')
        return [part.lower() for part in s.split('_')]

    def join(self, *parts: str) -> str:
        _check_all_lowercase(*parts)
        return '_'.join(p.upper() for p in parts)


##


STRING_CASINGS = [
    (CAMEL_CASE := CamelCase()),
    (LOW_CAMEL_CASE := LowCamelCase()),
    (SNAKE_CASE := SnakeCase()),
    (UP_SNAKE_CASE := UpSnakeCase()),
]


camel_case = CAMEL_CASE.join
low_camel_case = LOW_CAMEL_CASE.join
snake_case = SNAKE_CASE.join
up_snake_case = UP_SNAKE_CASE.join


camel_to_snake = CAMEL_CASE.to(SNAKE_CASE)
snake_to_camel = SNAKE_CASE.to(CAMEL_CASE)


##


def get_string_casing(s: str, casings: ta.Iterable[StringCasing] | None = None) -> StringCasing:
    if casings is None:
        casings = STRING_CASINGS
    cs = [c for c in casings if c.match(s)]
    if not cs:
        raise UnknownStringCasingError
    if len(cs) != 1:
        raise AmbiguousStringCasingError
    [c] = cs
    return c


def split_string_casing(s: str, casings: ta.Iterable[StringCasing] | None = None) -> list[str]:
    if casings is None:
        casings = STRING_CASINGS
    ts = {tuple(c.split(s)) for c in casings if c.match(s)}
    if not ts:
        raise UnknownStringCasingError
    if len(ts) != 1:
        raise AmbiguousStringCasingError
    [t] = ts
    return list(t)
