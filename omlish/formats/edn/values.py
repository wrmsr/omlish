import dataclasses as dc
import typing as ta

from ... import check
from ... import lang
from ...lite.dataclasses import dataclass_cache_hash


##


_DEBUG = __debug__
# _DEBUG = True


@dc.dataclass(frozen=True)
class Value(lang.Abstract, lang.Sealed):
    meta: ta.Any | None = dc.field(default=None, kw_only=True)


#


@dc.dataclass(frozen=True)
class Scalar(Value, lang.Abstract):
    pass


@dataclass_cache_hash()
@dc.dataclass(frozen=True)
class Keyword(Scalar, lang.Final):
    s: str

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.s!r})'

    if _DEBUG:
        def __post_init__(self) -> None:
            check.isinstance(self.s, str)


@dataclass_cache_hash()
@dc.dataclass(frozen=True)
class Char(Scalar, lang.Final):
    c: str

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.c!r})'

    if _DEBUG:
        def __post_init__(self) -> None:
            check.isinstance(self.c, str)
            check.equal(len(self.c), 1)


@dataclass_cache_hash()
@dc.dataclass(frozen=True)
class Symbol(Scalar, lang.Final):
    n: str

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.n!r})'

    if _DEBUG:
        def __post_init__(self) -> None:
            check.non_empty_str(self.n)


#


@dc.dataclass(frozen=True)
class Collection(Value, lang.Abstract):
    pass


@dataclass_cache_hash()
@dc.dataclass(frozen=True)
class List(Collection, lang.Final):
    items: ta.Sequence[ta.Any]

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.items!r})'

    if _DEBUG:
        def __post_init__(self) -> None:
            check.isinstance(self.items, tuple)

    @classmethod
    def new(cls, items: ta.Iterable[ta.Any], *, meta: ta.Any | None = None) -> 'List':
        return cls(tuple(items), meta=meta)


@dataclass_cache_hash()
@dc.dataclass(frozen=True)
class Vector(Collection, lang.Final):
    items: ta.Sequence[ta.Any]

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.items!r})'

    if _DEBUG:
        def __post_init__(self) -> None:
            check.isinstance(self.items, tuple)

    @classmethod
    def new(cls, items: ta.Iterable[ta.Any], *, meta: ta.Any | None = None) -> 'Vector':
        return cls(tuple(items), meta=meta)


@dataclass_cache_hash()
@dc.dataclass(frozen=True)
class Set(Collection, lang.Final):
    items: ta.Sequence[ta.Any]

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.items!r})'

    if _DEBUG:
        def __post_init__(self) -> None:
            check.isinstance(self.items, tuple)

    @classmethod
    def new(cls, items: ta.Iterable[ta.Any], *, meta: ta.Any | None = None) -> 'Set':
        return cls(tuple(items), meta=meta)


@dataclass_cache_hash()
@dc.dataclass(frozen=True)
class Map(Collection, lang.Final):
    items: ta.Sequence[tuple[ta.Any, ta.Any]]

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.items!r})'

    if _DEBUG:
        def __post_init__(self) -> None:
            check.isinstance(self.items, tuple)
            for t in self.items:
                check.isinstance(t, tuple)
                check.equal(len(t), 2)

    @classmethod
    def new(cls, items: ta.Iterable[ta.Iterable[ta.Any]], *, meta: ta.Any | None = None) -> 'Map':
        return cls(tuple((k, v) for k, v in items), meta=meta)


#


@dataclass_cache_hash()
@dc.dataclass(frozen=True)
class Tagged(Value, lang.Final):
    t: str
    v: ta.Any

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.t!r}, {self.v!r})'

    if _DEBUG:
        def __post_init__(self) -> None:
            check.non_empty_str(self.t)
