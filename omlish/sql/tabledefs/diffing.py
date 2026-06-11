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
# change worth refusing. Lossier types (Uuid/Boolean/Float/Bytes, which some backends' reflection collapses to
# String/Integer) are deliberately not compared, to avoid spurious churn.
_DIFFABLE_DTYPES = (Integer, String, Datetime)


def diff_table(current: TableDef, existing: TableDef) -> list[MigrationOp]:
    """
    Produce the migration ops that bring `existing` (e.g. a table reflected from a live db) up to `current` (the
    in-code definition). Limited to forward-only column and named-index add/drop. Changes it cannot safely apply -
    primary-key changes, column nullability changes, and column type changes among the faithfully-reflected dtypes -
    are refused with `UnsupportedDiffError` rather than silently ignored or mis-migrated; triggers, options, and
    lossier type changes are still left untouched. Operates on the order-normal-form, so element order is insignificant.
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

        # A column on both sides: detect the changes we can see faithfully and refuse them, rather than silently
        # leaving a schema/code mismatch. Nullability reflects accurately everywhere except on pk columns (implicitly
        # not-null however they were declared). Type changes are judged only among the dtypes every backend reflects
        # unambiguously; anything lossier is left alone.
        if name not in cur_pk_cols and c.nullable != ex_col.nullable:
            raise UnsupportedDiffError(
                f'column {name!r} nullability change is not supported: {ex_col.nullable} -> {c.nullable}',
            )
        if (
                isinstance(c.type, _DIFFABLE_DTYPES) and
                isinstance(ex_col.type, _DIFFABLE_DTYPES) and
                type(c.type) is not type(ex_col.type)
        ):
            raise UnsupportedDiffError(
                f'column {name!r} type change is not supported: {ex_col.type!r} -> {c.type!r}',
            )

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
