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


##


def _sort_options(opts: tv.TypedValues) -> tv.TypedValues:
    if len(opts) <= 1:
        return opts
    return tv.TypedValues(*sorted(opts, key=lambda o: type(o).__qualname__))


def _element_sort_key(e: Element) -> tuple[int, str]:
    if isinstance(e, PrimaryKey):
        return (0, '')
    elif isinstance(e, Index):
        return (1, e.name or '__'.join(e.columns))
    elif isinstance(e, UpdatedAtTrigger):
        return (2, e.column)
    else:
        return (3, type(e).__qualname__)


def normalize_table(td: TableDef) -> TableDef:
    """
    Canonicalize element and option order: columns keep their declared order (which is significant), while everything
    else - constraints, indexes, triggers, options - is order-insensitive and sorted deterministically. Two tabledefs
    that differ only in the order of non-column elements normalize to equal values; this is the basis for
    order-insensitive ddl diffing.
    """

    cols = [e for e in td.elements if isinstance(e, Column)]
    rest = sorted((e for e in td.elements if not isinstance(e, Column)), key=_element_sort_key)

    out: list[Element] = []
    for c in cols:
        out.append(dc.replace(c, options=_sort_options(c.options)))
    for e in rest:
        if isinstance(e, Index):
            out.append(dc.replace(e, options=_sort_options(e.options)))
        else:
            out.append(e)

    return dc.replace(
        td,
        elements=Elements(*out),
        options=_sort_options(td.options),
    )
