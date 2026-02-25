# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import functools
import typing as ta


##


class UnknownHttpVersionError(Exception):
    pass


@ta.final
@functools.total_ordering
class HttpVersion:
    def __init__(self, major: int, minor: int) -> None:
        self._major = major
        self._minor = minor

        self._parts = parts = (major, minor)

        self._hash = hash(parts)

        self._str = f'HTTP/{major}.{minor}'
        self._short_str = f'{major}.{minor}'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.major}, {self.minor})'

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: object) -> ta.Any:
        if not isinstance(other, HttpVersion):
            return NotImplemented
        return self._parts == other._parts

    def __lt__(self, other: object) -> ta.Any:
        if not isinstance(other, HttpVersion):
            return NotImplemented
        return self._parts < other._parts

    @property
    def major(self) -> int:
        return self._major

    @property
    def minor(self) -> int:
        return self._minor

    def __str__(self) -> str:
        return self._str

    @property
    def short_str(self) -> str:
        return self._short_str

    def __iter__(self) -> ta.Iterator[int]:
        return iter(self._parts)


@ta.final
class HttpVersions:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    HTTP_0_9 = HttpVersion(0, 9)
    HTTP_1_0 = HttpVersion(1, 0)
    HTTP_1_1 = HttpVersion(1, 1)
    HTTP_2_0 = HttpVersion(2, 0)

    _FROM_STR: ta.ClassVar[ta.Mapping[str, HttpVersion]] = {
        str(v): v for v in [
            HTTP_0_9,
            HTTP_1_0,
            HTTP_1_1,
            HTTP_2_0,
        ]
    }

    @classmethod
    def from_str(cls, s: str) -> HttpVersion:
        try:
            return cls._FROM_STR[s]
        except KeyError:
            raise UnknownHttpVersionError(s) from None

    @classmethod
    def of(cls, o: ta.Union[HttpVersion, str]) -> HttpVersion:
        if isinstance(o, HttpVersion):
            return o
        elif isinstance(o, str):
            return cls.from_str(o)
        else:
            raise TypeError(o)
