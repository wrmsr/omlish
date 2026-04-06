import typing as ta

from ... import collections as col
from ... import dataclasses as dc
from ... import lang
from ... import typedvalues as tv
from .dtypes import Dtype
from .values import SimpleValue


##


class Element(tv.TypedValue, lang.Abstract, lang.Sealed):
    pass


##


@dc.dataclass(frozen=True)
class Column(Element, lang.Final):
    name: str
    type: Dtype
    nullable: bool = dc.field(default=False, kw_only=True)
    default: lang.Maybe[SimpleValue] = dc.field(default=lang.empty(), kw_only=True)


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


Elements: ta.TypeAlias = tv.TypedValues[Element]
