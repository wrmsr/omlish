# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import re
import typing as ta
import urllib.parse
import uuid


##


class UrlRouteConverter:
    regex: str = r'[^/]+'
    weight: ta.ClassVar[int] = 100
    is_greedy: ta.ClassVar[bool] = False

    def to_python(self, s: str) -> ta.Any:
        return s

    def to_url(self, v: ta.Any) -> str:
        return urllib.parse.quote(str(v), safe="!$&'()*+,/:;=@")


class UrlRouteStringConverter(UrlRouteConverter):
    pass


class UrlRoutePathConverter(UrlRouteConverter):
    regex = r'.+'
    weight = 200
    is_greedy = True


class UrlRouteIntegerConverter(UrlRouteConverter):
    regex = r'\d+'
    weight = 50

    def to_python(self, s: str) -> int:
        return int(s)

    def to_url(self, v: ta.Any) -> str:
        return str(int(v))


class UrlRouteFloatConverter(UrlRouteConverter):
    regex = r'\d+(?:\.\d+)?'
    weight = 60

    def to_python(self, s: str) -> float:
        return float(s)

    def to_url(self, v: ta.Any) -> str:
        return str(float(v))


class UrlRouteUuidConverter(UrlRouteConverter):
    regex = (
        r'[A-Fa-f0-9]{8}-[A-Fa-f0-9]{4}-'
        r'[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{12}'
    )
    weight = 40

    def to_python(self, s: str) -> uuid.UUID:
        return uuid.UUID(s)

    def to_url(self, v: ta.Any) -> str:
        return str(uuid.UUID(str(v)))


class UrlRouteAnyConverter(UrlRouteConverter):
    weight = 30

    def __init__(self, items: ta.Iterable[str]) -> None:
        super().__init__()

        self._items = frozenset(items)
        self.regex = '(?:' + '|'.join(re.escape(i) for i in sorted(self._items)) + ')'

    def to_python(self, s: str) -> str:
        if s not in self._items:
            raise ValueError(s)
        return s

    def to_url(self, v: ta.Any) -> str:
        s = str(v)
        if s not in self._items:
            raise ValueError(s)
        return urllib.parse.quote(s, safe="!$&'()*+,/:;=@")


URL_ROUTE_DEFAULT_CONVERTERS: ta.Mapping[str, ta.Callable[..., UrlRouteConverter]] = {
    'str': UrlRouteStringConverter,
    'string': UrlRouteStringConverter,
    'path': UrlRoutePathConverter,
    'int': UrlRouteIntegerConverter,
    'float': UrlRouteFloatConverter,
    'uuid': UrlRouteUuidConverter,
    'any': UrlRouteAnyConverter,
}

