from ... import dataclasses as dc
from .dtypes import Datetime
from .dtypes import Integer
from .elements import Column
from .elements import CreatedAt
from .elements import CreatedAtUpdatedAt
from .elements import Element
from .elements import Elements
from .elements import IdIntegerPrimaryKey
from .elements import PrimaryKey
from .elements import UpdatedAt
from .elements import UpdatedAtTrigger
from .tabledefs import TableDef


def lower_table_elements(td: TableDef) -> TableDef:
    todo: list[Element] = list(td.elements)[::-1]
    out: list[Element] = []

    while todo:
        match (e := todo.pop()):
            case Column() | PrimaryKey():
                out.append(e)

            case IdIntegerPrimaryKey():
                out.extend([
                    Column('id', Integer()),
                    PrimaryKey(['id']),
                ])

            case CreatedAt():
                out.append(Column('created_at', Datetime()))

            case UpdatedAt():
                out.extend([
                    Column('updated_at', Datetime()),
                    UpdatedAtTrigger('updated_at'),
                ])

            case CreatedAtUpdatedAt():
                todo.extend([
                    CreatedAt(),
                    UpdatedAt(),
                ][::-1])

            case _:
                raise TypeError(e)

    return dc.replace(td, elements=Elements(out))
