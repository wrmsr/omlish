from ... import dataclasses as dc
from ... import lang
from ..dtypes import Datetime
from ..dtypes import Integer
from ..dtypes import String
from .elements import Column
from .elements import Index
from .elements import PrimaryKey
from .elements import index_name
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
class AlterColumn(MigrationOp, lang.Final):
    table: str
    column: Column  # the desired end state; the backend renders the alter to reach it (type and/or nullability)


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


# The dtypes every backend reflects faithfully and unambiguously, so a change between two of them is a real, confident
# change worth acting on. Lossier types (Uuid/Boolean/Float/Bytes, which some backends' reflection collapses to
# String/Integer) are deliberately not compared, to avoid spurious churn.
_DIFFABLE_DTYPES = (Integer, String, Datetime)


def diff_table(current: TableDef, existing: TableDef) -> list[MigrationOp]:
    """
    Produce the migration ops that bring `existing` (e.g. a table reflected from a live db) up to `current` (the
    in-code definition): column add/drop/alter and named-index add/drop. A column's nullability change, or a type
    change among the faithfully-reflected dtypes (Integer/String/Datetime), becomes an in-place `AlterColumn`; lossier
    type differences are left untouched (reflection can't tell them apart). Primary-key changes are refused outright
    (`UnsupportedDiffError`); triggers and options are left untouched. Whether an `AlterColumn` can actually be applied
    is the backend's call - sqlite, lacking ALTER COLUMN, refuses it at render time. Operates on the order-normal-form,
    so element order is insignificant.
    """

    if current.name != existing.name:
        raise UnsupportedDiffError(f'table name differs: {current.name!r} != {existing.name!r}')

    current = normalize_table(current)
    existing = normalize_table(existing)

    cur_pk = current.elements.get(PrimaryKey)
    ex_pk = existing.elements.get(PrimaryKey)
    if frozenset(cur_pk.columns if cur_pk is not None else ()) != frozenset(ex_pk.columns if ex_pk is not None else ()):
        raise UnsupportedDiffError(f'primary-key change is not supported: {ex_pk!r} -> {cur_pk!r}')

    cur_pk_cols = frozenset(cur_pk.columns if cur_pk is not None else ())

    ops: list[MigrationOp] = []

    cur_cols = {c.name: c for c in current.elements.get(Column, ())}
    ex_cols = {c.name: c for c in existing.elements.get(Column, ())}

    for name, c in cur_cols.items():
        ex_col = ex_cols.get(name)
        if ex_col is None:
            ops.append(AddColumn(current.name, c))
            continue

        # A column on both sides: emit an in-place AlterColumn for the changes we can see faithfully - a nullability
        # change (reflected accurately everywhere except on pk columns, which are implicitly not-null however declared)
        # or a type change among the dtypes every backend reflects unambiguously. Lossier type differences are left
        # alone, since reflection can't tell them apart.
        nullability_changed = name not in cur_pk_cols and c.nullable != ex_col.nullable
        type_changed = (
            isinstance(c.type, _DIFFABLE_DTYPES) and
            isinstance(ex_col.type, _DIFFABLE_DTYPES) and
            type(c.type) is not type(ex_col.type)
        )
        if nullability_changed or type_changed:
            ops.append(AlterColumn(current.name, c))

    for name in ex_cols:
        if name not in cur_cols:
            ops.append(DropColumn(current.name, name))

    cur_idx = {index_name(current.name, i): i for i in current.elements.get(Index, ())}
    ex_idx = {index_name(existing.name, i): i for i in existing.elements.get(Index, ())}

    for nm, i in cur_idx.items():
        ex = ex_idx.get(nm)
        if ex is None:
            ops.append(AddIndex(current.name, i))
        elif (list(i.columns), i.unique) != (list(ex.columns), ex.unique):
            # Same name, changed definition - drop and recreate. The where-clause is intentionally not compared:
            # partial-index reflection is lossy, so doing so would diff forever.
            ops.append(DropIndex(current.name, nm))
            ops.append(AddIndex(current.name, i))
    for nm in ex_idx:
        if nm not in cur_idx:
            ops.append(DropIndex(current.name, nm))

    return ops
