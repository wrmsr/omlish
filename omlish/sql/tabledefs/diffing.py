from ... import dataclasses as dc
from ... import lang
from .elements import Column
from .elements import Index
from .elements import PrimaryKey
from .lower import normalize_table
from .tabledefs import TableDef


##


class MigrationOp(lang.Abstract, lang.Sealed):
    pass


@dc.dataclass(frozen=True)
class AddColumn(MigrationOp, lang.Final):
    table: str
    column: Column


@dc.dataclass(frozen=True)
class DropColumn(MigrationOp, lang.Final):
    table: str
    name: str


@dc.dataclass(frozen=True)
class AddIndex(MigrationOp, lang.Final):
    table: str
    index: Index


@dc.dataclass(frozen=True)
class DropIndex(MigrationOp, lang.Final):
    table: str
    name: str


##


class UnsupportedDiffError(Exception):
    pass


def diff_table(current: TableDef, existing: TableDef) -> list[MigrationOp]:
    """
    Produce the migration ops that bring `existing` (e.g. a table reflected from a live db) up to `current` (the
    in-code definition). Deliberately limited: added/dropped columns and added/dropped *named* indexes - the common
    forward-only evolution. Column type/nullability changes, primary-key changes, triggers, and options are outside the
    supported subset and are left untouched for now (a richer differ, with a confident "I don't understand this"
    report, is future work). Operates on the order-normal-form, so element order is insignificant.
    """

    if current.name != existing.name:
        raise UnsupportedDiffError(f'table name differs: {current.name!r} != {existing.name!r}')

    current = normalize_table(current)
    existing = normalize_table(existing)

    cur_pk = current.elements.get(PrimaryKey)
    ex_pk = existing.elements.get(PrimaryKey)
    if frozenset(cur_pk.columns if cur_pk is not None else ()) != frozenset(ex_pk.columns if ex_pk is not None else ()):
        raise UnsupportedDiffError(f'primary-key change is not supported: {ex_pk!r} -> {cur_pk!r}')

    ops: list[MigrationOp] = []

    cur_cols = {c.name: c for c in current.elements.get(Column, ())}
    ex_cols = {c.name: c for c in existing.elements.get(Column, ())}

    for name, c in cur_cols.items():
        if name not in ex_cols:
            ops.append(AddColumn(current.name, c))
    for name in ex_cols:
        if name not in cur_cols:
            ops.append(DropColumn(current.name, name))

    cur_idx = {i.name: i for i in current.elements.get(Index, ()) if i.name is not None}
    ex_idx = {i.name: i for i in existing.elements.get(Index, ()) if i.name is not None}

    for name, i in cur_idx.items():
        if name not in ex_idx:
            ops.append(AddIndex(current.name, i))
    for name in ex_idx:
        if name not in cur_idx:
            ops.append(DropIndex(current.name, name))

    return ops
