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


##


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


##


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
class StrOrStrsKeyword(Keyword, lang.Abstract):
    ss: str | ta.Sequence[str]


@dc.dataclass(frozen=True)
class KeywordsKeyword(Keyword, lang.Abstract):
    kw: Keywords


@dc.dataclass(frozen=True)
class StrToKeywordsKeyword(Keyword, lang.Abstract):
    m: ta.Mapping[str, Keywords]


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


class Type(StrOrStrsKeyword, lang.Final, tag='type'):
    pass


class Items(KeywordsKeyword, lang.Final, tag='items'):
    pass


##


class Required(StrOrStrsKeyword, lang.Final, tag='required'):
    pass


class Properties(StrToKeywordsKeyword, lang.Final, tag='properties'):
    pass


##


class MaxItems(NumberKeyword, lang.Final, tag='maxItems'):
    pass


class MinItems(NumberKeyword, lang.Final, tag='minItems'):
    pass


class UniqueItems(BooleanKeyword, lang.Final, tag='uniqueItems'):
    pass


#


class Maximum(NumberKeyword, lang.Final, tag='maximum'):
    pass


class ExclusiveMaximum(NumberKeyword, lang.Final, tag='exclusiveMaximum'):
    pass


class Minimum(NumberKeyword, lang.Final, tag='minimum'):
    pass


class ExclusiveMinimum(NumberKeyword, lang.Final, tag='exclusiveMinimum'):
    pass


##


KEYWORD_TYPES_BY_TAG: ta.Mapping[str, type[Keyword]] = col.unique_map_by(  # type: ignore
    operator.attrgetter('tag'),
    (cls for cls in lang.deep_subclasses(Keyword) if not lang.is_abstract_class(cls)),
    strict=True,
)
