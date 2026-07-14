import operator
import typing as ta

from .... import cached
from .... import check
from .... import collections as col
from .... import dataclasses as dc
from .... import lang


with lang.auto_proxy_import(globals()):
    from . import rendering as _rendering


T = ta.TypeVar('T')

KeywordT = ta.TypeVar('KeywordT', bound='Keyword')


##


class _Renderable:
    _rendered: ta.ClassVar[ta.Any]

    @ta.final
    def render(self) -> ta.Any:
        try:
            return self._rendered
        except AttributeError:
            pass
        ret = _rendering.render(self)  # type: ignore[arg-type]
        object.__setattr__(self, '_rendered', ret)
        return ret


##


class Keyword(_Renderable, lang.Abstract):
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


@ta.final
class KeywordsByTypeMapping(col.ProxyMapping[type[Keyword], Keyword]):
    def __getitem__(self, key: type[KeywordT], /) -> KeywordT:
        return self._target[key]  # type: ignore[return-value]

    @ta.overload
    def get(self, key: type[KeywordT], /) -> KeywordT | None: ...  # noqa

    @ta.overload
    def get(self, key: type[KeywordT], default: KeywordT, /) -> KeywordT: ...  # noqa

    @ta.overload
    def get(self, key: type[KeywordT], default: T, /) -> KeywordT | T: ...  # noqa

    def get(self, key, default=None):
        return self._target.get(key, default)


@dc.dataclass(frozen=True)
class Keywords(_Renderable, lang.Final):
    lst: ta.Sequence[Keyword]

    #

    @cached.property
    @dc.init
    def by_type(self) -> KeywordsByTypeMapping:
        return KeywordsByTypeMapping(col.make_map_by(  # noqa
            type,
            (k for k in self.lst if not isinstance(k, UnknownKeyword)),
            strict=True,
        ))

    @cached.property
    @dc.init
    def by_tag(self) -> ta.Mapping[str, Keyword]:
        return col.make_map_by(operator.attrgetter('tag'), self.lst, strict=True)  # noqa

    #

    def __getitem__(self, item: type[KeywordT] | str) -> KeywordT:
        if isinstance(item, type):
            return self.by_type[item]  # noqa
        elif isinstance(item, str):
            return self.by_tag[item]
        else:
            raise TypeError(item)

    def __contains__(self, item: type[Keyword] | str | Keyword) -> bool:
        if isinstance(item, Keyword):
            return item in self.lst
        else:
            try:
                self[item]  # noqa
            except KeyError:
                return False
            else:
                return True

    def __len__(self) -> int:
        return len(self.lst)

    def __iter__(self) -> ta.Iterator[Keyword]:
        return iter(self.lst)


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
