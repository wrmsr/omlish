import typing as ta

from ... import collections as col
from ... import dataclasses as dc
from ... import lang
from ... import marshal as msh
from ... import typedvalues as tv
from ..dtypes import Dtype
from .options import ColumnOptions
from .options import IndexOptions
from .predicates import Predicate
from .predicates import as_opt_predicate
from .values import SimpleValue


##


class Element(tv.TypedValue, lang.Abstract, lang.Sealed):
    pass


##


@dc.dataclass(frozen=True)
class Column(Element, lang.Final):
    name: str
    type: Dtype

    _: dc.KW_ONLY

    nullable: bool = False
    default: lang.Maybe[SimpleValue] = lang.empty()

    # TODO: marshal once concrete (backend) option types exist - open families have no poly impls yet.
    options: ColumnOptions = (
        dc.xfield(default_factory=tv.TypedValues, coerce=tv.as_collection) |
        msh.dc_field_options(no_marshal=True, no_unmarshal=True)
    )


@dc.dataclass(frozen=True)
class PrimaryKey(Element, tv.UniqueTypedValue, lang.Final):
    columns: ta.Sequence[str]


@dc.dataclass(frozen=True)
class Index(Element, lang.Final):
    columns: ta.Sequence[str] = dc.xfield(coerce=col.seq)  # noqa

    _: dc.KW_ONLY

    name: str | None = None

    unique: bool = False
    where: Predicate | None = (
        dc.xfield(None, coerce=as_opt_predicate) |
        msh.dc_field_options(no_marshal=True, no_unmarshal=True)
    )

    options: IndexOptions = (
        dc.xfield(default_factory=tv.TypedValues, coerce=tv.as_collection) |
        msh.dc_field_options(no_marshal=True, no_unmarshal=True)
    )


def index_name(table_name: str, e: Index) -> str:
    """
    The effective name an index is created under: its explicit `name`, or the deterministic auto-name derived from the
    table and columns. Shared by the DDL renderer and the differ so an unnamed in-code index matches its reflected,
    db-named counterpart (otherwise diffing would drop-and-recreate it on every run).
    """

    return e.name if e.name is not None else '__'.join([table_name, 'index', *e.columns])


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
