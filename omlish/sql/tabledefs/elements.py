import typing as ta

from ... import check
from ... import collections as col
from ... import dataclasses as dc
from ... import lang
from .dtypes import Dtype


##


class Element(lang.Abstract, lang.Sealed):
    pass


##


@dc.dataclass(frozen=True)
class Column(Element, lang.Final):
    name: str
    type: Dtype
    nullable: bool = dc.field(default=False, kw_only=True)
    default: lang.Maybe[ta.Any] = dc.field(default=lang.empty(), kw_only=True)


@dc.dataclass(frozen=True)
class PrimaryKey(Element, lang.Final):
    columns: ta.Sequence[str]


@dc.dataclass(frozen=True)
class Index(Element, lang.Final):
    columns: ta.Sequence[str] = dc.xfield(coerce=col.seq)
    name: str | None = None


##


@dc.dataclass(frozen=True)
class IdIntegerPrimaryKey(Element, lang.Final):
    pass


#


@dc.dataclass(frozen=True)
class CreatedAt(Element, lang.Final):
    pass


@dc.dataclass(frozen=True)
class UpdatedAt(Element, lang.Final):
    pass


@dc.dataclass(frozen=True)
class UpdatedAtTrigger(Element, lang.Final):
    column: str


@dc.dataclass(frozen=True)
class CreatedAtUpdatedAt(Element, lang.Final):
    pass


##


@dc.dataclass(frozen=True)
class Elements(ta.Sequence[Element], lang.Final):
    lst: ta.Sequence[Element] = dc.xfield(coerce=col.seq_of(check.of_isinstance(Element)))

    def __iter__(self) -> ta.Iterator[Element]:
        return iter(self.lst)

    def __getitem__(self, index: ta.Any) -> Element:  # type: ignore[override]
        return self.lst[index]

    def __len__(self) -> int:
        return len(self.lst)

    @lang.cached_property
    def by_type(self) -> col.DynamicTypeMap[Element]:
        return col.DynamicTypeMap(self.lst)
