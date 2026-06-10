import typing as ta

from ... import dataclasses as dc
from ... import lang
from ... import marshal as msh
from ... import typedvalues as tv
from .elements import Element
from .elements import Elements
from .options import TableOption
from .options import TableOptions


##


@dc.dataclass(frozen=True)
class TableDef(lang.Final):
    name: str
    elements: Elements

    _: dc.KW_ONLY

    options: TableOptions = (
        dc.xfield(default_factory=tv.TypedValues, coerce=tv.as_collection) |
        msh.dc_field_options(no_marshal=True, no_unmarshal=True)
    )


def table_def(
        name: str,
        *elements: Element,
        options: ta.Sequence[TableOption] = (),
) -> TableDef:
    return TableDef(
        name,
        Elements(*elements),
        options=tv.TypedValues(*options),
    )
