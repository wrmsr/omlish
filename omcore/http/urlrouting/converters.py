# ruff: noqa: UP006 UP007 UP045
# @om-lite
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
    def __init__(
            self,
            min: int = 1,  # noqa
            max: ta.Optional[int] = None,  # noqa
            length: ta.Optional[int] = None,
    ) -> None:
        super().__init__()

        if length is not None:
            self.regex = r'[^/]{' + str(int(length)) + '}'
        elif max is not None:
            self.regex = r'[^/]{' + str(int(min)) + ',' + str(int(max)) + '}'
        elif min != 1:
            self.regex = r'[^/]{' + str(int(min)) + ',}'

    def to_url(self, v: ta.Any) -> str:
        return urllib.parse.quote(str(v), safe="!$&'()*+,:;=@")


class UrlRoutePathConverter(UrlRouteConverter):
    regex = r'.+'
    weight = 200
    is_greedy = True


class UrlRouteIntegerConverter(UrlRouteConverter):
    regex = r'\d+'
    weight = 50

    def __init__(
            self,
            min: ta.Optional[int] = None,  # noqa
            max: ta.Optional[int] = None,  # noqa
            signed: bool = False,
    ) -> None:
        super().__init__()

        if signed:
            self.regex = r'-?' + self.regex
        self._min = min
        self._max = max
        self._signed = signed

    def to_python(self, s: str) -> int:
        v = int(s)
        if self._min is not None and v < self._min:
            raise ValueError(s)
        if self._max is not None and v > self._max:
            raise ValueError(s)
        return v

    def to_url(self, v: ta.Any) -> str:
        i = int(v)
        if not self._signed and i < 0:
            raise ValueError(v)
        if self._min is not None and i < self._min:
            raise ValueError(v)
        if self._max is not None and i > self._max:
            raise ValueError(v)
        return str(i)


class UrlRouteFloatConverter(UrlRouteConverter):
    regex = r'\d+(?:\.\d+)?'
    weight = 60

    def __init__(
            self,
            min: ta.Optional[float] = None,  # noqa
            max: ta.Optional[float] = None,  # noqa
            signed: bool = False,
    ) -> None:
        super().__init__()

        if signed:
            self.regex = r'-?' + self.regex
        self._min = min
        self._max = max
        self._signed = signed

    def to_python(self, s: str) -> float:
        v = float(s)
        if self._min is not None and v < self._min:
            raise ValueError(s)
        if self._max is not None and v > self._max:
            raise ValueError(s)
        return v

    def to_url(self, v: ta.Any) -> str:
        f = float(v)
        if not self._signed and f < 0:
            raise ValueError(v)
        if self._min is not None and f < self._min:
            raise ValueError(v)
        if self._max is not None and f > self._max:
            raise ValueError(v)
        return str(f)


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

    def __init__(self, *items: str) -> None:
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
