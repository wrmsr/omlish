from ... import dataclasses as dc
from ... import lang
from .dtypes import Datetime
from .dtypes import Integer
from .elements import Column
from .elements import CreatedAt
from .elements import CreatedAtUpdatedAt
from .elements import Element
from .elements import Elements
from .elements import IdIntegerPrimaryKey
from .elements import Index
from .elements import PrimaryKey
from .elements import UpdatedAt
from .elements import UpdatedAtTrigger
from .tabledefs import TableDef
from .values import Now


##


def lower_table_elements(td: TableDef) -> TableDef:
    out: list[Element] = []

    todo: list[Element] = list(td.elements)[::-1]

    def add_todo(*elements: Element) -> None:
        todo.extend(reversed(elements))

    while todo:
        match (e := todo.pop()):
            case Column() | PrimaryKey() | Index():
                out.append(e)

            case IdIntegerPrimaryKey():
                out.extend([
                    Column('id', Integer()),
                    PrimaryKey(['id']),
                ])

            case CreatedAt():
                out.append(Column('created_at', Datetime(), default=lang.just(Now())))

            case UpdatedAt():
                out.extend([
                    Column('updated_at', Datetime(), default=lang.just(Now())),
                    UpdatedAtTrigger('updated_at'),
                ])

            case CreatedAtUpdatedAt():
                add_todo(
                    CreatedAt(),
                    UpdatedAt(),
                )

            case _:
                raise TypeError(e)

    return dc.replace(td, elements=Elements(out))
