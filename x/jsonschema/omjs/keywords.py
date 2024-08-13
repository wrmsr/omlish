import operator
import typing as ta

from omlish import cached
from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang


KeywordT = ta.TypeVar('KeywordT', bound='Keyword')


class Keyword(lang.Abstract, lang.PackageSealed):
    tag: ta.ClassVar[str]

    def __init_subclass__(cls, *, tag: str | None = None, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)
        check.not_in('tag', dir(cls))
        if not lang.is_abstract_class(cls):
            check.issubclass(cls, lang.Final)
            cls.tag = check.non_empty_str(tag)
        else:
            check.none(tag)


@dc.dataclass(frozen=True)
class Keywords(lang.Final):
    lst: ta.Sequence[Keyword]

    @cached.property
    @dc.init
    def by_type(self) -> ta.Mapping[type[Keyword], Keyword]:
        return col.unique_map_by(type, self.lst, strict=True)  # type: ignore

    @cached.property
    @dc.init
    def by_tag(self) -> ta.Mapping[str, Keyword]:
        return col.unique_map_by(operator.attrgetter('tag'), self.lst, strict=True)  # type: ignore

    def __getitem__(self, item: type[KeywordT] | str) -> KeywordT:
        if isinstance(item, type):
            return self.by_type[item]  # type: ignore
        elif isinstance(item, str):
            return self.by_tag[item]
        else:
            raise TypeError(item)


@dc.dataclass(frozen=True)
class StrKeyword(Keyword, lang.Abstract):
    s: str


@dc.dataclass(frozen=True)
class StrOrStrsKeyword(Keyword, lang.Abstract):
    ss: str | ta.Sequence[str]


##


class Id(StrKeyword, lang.Final, tag='$id'):
    pass


class SchemaKeyword(StrKeyword, lang.Final, tag='$schema'):
    pass


class Ref(StrKeyword, lang.Final, tag='$ref'):
    pass


##


class Title(StrKeyword, lang.Final, tag='title'):
    pass


class Description(StrKeyword, lang.Final, tag='description'):
    pass


@dc.dataclass(frozen=True)
class Type(StrOrStrsKeyword, lang.Final, tag='type'):
    pass


##


@dc.dataclass(frozen=True)
class Required(StrOrStrsKeyword, lang.Final, tag='required'):
    pass


@dc.dataclass(frozen=True)
class Properties(Keyword, lang.Final, tag='properties'):
    dct: ta.Mapping[str, Keywords]


##


KEYWORD_TYPES_BY_TAG: ta.Mapping[str, type[Keyword]] = col.unique_map_by(  # type: ignore
    operator.attrgetter('tag'),
    (cls for cls in lang.deep_subclasses(Keyword) if not lang.is_abstract_class(cls)),
    strict=True,
)
