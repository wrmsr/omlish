from ... import dataclasses as dc
from ... import lang
from .elements import Element
from .elements import Elements


##


@dc.dataclass(frozen=True)
class TableDef(lang.Final):
    name: str
    elements: Elements


def table_def(
        name: str,
        *elements: Element,
) -> TableDef:
    return TableDef(
        name,
        Elements(elements),
    )
