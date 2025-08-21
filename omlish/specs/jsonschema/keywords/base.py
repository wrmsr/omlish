import operator
import typing as ta

from .... import cached
from .... import check
from .... import collections as col
from .... import dataclasses as dc
from .... import lang


KeywordT = ta.TypeVar('KeywordT', bound='Keyword')


##


class Keyword(lang.Abstract):
    tag: ta.ClassVar[str]


##


class KnownKeyword(Keyword, lang.Abstract):
    aliases: ta.ClassVar[frozenset[str]]

    tag_and_aliases: ta.ClassVar[frozenset[str]]

    def __init_subclass__(
            cls,
            *,
            tag: str | None = None,
            aliases: ta.Iterable[str] | None = None,
            **kwargs: ta.Any,
    ) -> None:
        super().__init_subclass__(**kwargs)

        check.empty(set(dir(cls)) & {'tag', 'aliases', 'tag_and_aliases'})
        if not lang.is_abstract_class(cls):
            check.issubclass(cls, lang.Final)
            check.not_isinstance(aliases, str)
            cls.tag = check.non_empty_str(tag)
            cls.aliases = frozenset(aliases or ())
            cls.tag_and_aliases = frozenset([cls.tag, *cls.aliases])
        else:
            for a in (tag, aliases):
                check.none(a)


##


@dc.dataclass(frozen=True)
class UnknownKeyword(Keyword, lang.Final):
    tag: str  # type: ignore[misc]
    value: ta.Any


##


@dc.dataclass(frozen=True)
class Keywords(lang.Final):
    lst: ta.Sequence[Keyword]

    @cached.property
    @dc.init
    def by_type(self) -> ta.Mapping[type[Keyword], Keyword]:
        return col.make_map_by(type, (k for k in self.lst if not isinstance(k, UnknownKeyword)), strict=True)  # noqa

    @cached.property
    @dc.init
    def by_tag(self) -> ta.Mapping[str, Keyword]:
        return col.make_map_by(operator.attrgetter('tag'), self.lst, strict=True)  # noqa

    def __getitem__(self, item: type[KeywordT] | str) -> KeywordT:
        if isinstance(item, type):
            return self.by_type[item]  # noqa
        elif isinstance(item, str):
            return self.by_tag[item]
        else:
            raise TypeError(item)


##


@dc.dataclass(frozen=True)
class AnyKeyword(Keyword, lang.Abstract):
    v: ta.Any


@dc.dataclass(frozen=True)
class AnyArrayKeyword(Keyword, lang.Abstract):
    vs: ta.Sequence[ta.Any]


@dc.dataclass(frozen=True)
class BooleanKeyword(Keyword, lang.Abstract):
    b: bool


@dc.dataclass(frozen=True)
class NumberKeyword(Keyword, lang.Abstract):
    n: int | float


@dc.dataclass(frozen=True)
class StrKeyword(Keyword, lang.Abstract):
    s: str


@dc.dataclass(frozen=True)
class StrOrStrArrayKeyword(Keyword, lang.Abstract):
    ss: str | ta.Sequence[str]


@dc.dataclass(frozen=True)
class KeywordsKeyword(Keyword, lang.Abstract):
    kw: Keywords


@dc.dataclass(frozen=True)
class KeywordsArrayKeyword(Keyword, lang.Abstract):
    kws: ta.Sequence[Keywords]


@dc.dataclass(frozen=True)
class StrToKeywordsKeyword(Keyword, lang.Abstract):
    m: ta.Mapping[str, Keywords]


@dc.dataclass(frozen=True)
class BooleanOrKeywordsKeyword(Keyword, lang.Abstract):
    bk: bool | Keywords
