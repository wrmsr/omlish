from ... import dataclasses as dc
from ... import lang
from ... import typedvalues as tv
from ..dtypes import Datetime
from ..dtypes import Integer
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
from .options import BackendOption
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

    return dc.replace(td, elements=Elements(*out))


##


def select_backend_options(td: TableDef, keep: type[BackendOption]) -> TableDef:
    """
    Strip every BackendOption that is not an instance of `keep` from the table and its columns/indexes - leaving the
    common (non-backend) options and the target backend's options. This is the fail-closed prep pass: the backend
    processor can then confidently raise on any option it still does not recognize.
    """

    def filt(opts: tv.TypedValues) -> tv.TypedValues:
        kept = [o for o in opts if not isinstance(o, BackendOption) or isinstance(o, keep)]
        if len(kept) == len(opts):
            return opts
        return tv.TypedValues(*kept)

    new_elements: list[Element] = []
    for e in td.elements:
        if isinstance(e, Column):
            new_elements.append(dc.replace(e, options=filt(e.options)))
        elif isinstance(e, Index):
            new_elements.append(dc.replace(e, options=filt(e.options)))
        else:
            new_elements.append(e)

    return dc.replace(
        td,
        elements=Elements(*new_elements),
        options=filt(td.options),
    )
