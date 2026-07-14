"""
A deliberately tiny predicate IR for DDL (partial-index WHERE, future check constraints). It is *not* the queries DML
expression system - DDL and DML diverge, and tabledefs must not import queries. The shared low-level bits (the
comparison-op vocabulary) come from sql.syntax, which knows nothing of this IR.

Predicate is an *open* family: a backend may define its own predicate node (mixing a backend marker), and its renderer
overrides render_predicate to handle it, deferring to super() for the common nodes.
"""
import typing as ta

from ... import dataclasses as dc
from ... import lang
from ..syntax import CompareOp


SimplePredicateValue: ta.TypeAlias = bool | int | float | str | None


##


class Predicate(lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class RawPredicate(Predicate, lang.Final):
    s: str


@dc.dataclass(frozen=True)
class Compare(Predicate, lang.Final):
    column: str
    op: CompareOp
    value: SimplePredicateValue


@dc.dataclass(frozen=True)
class IsNull(Predicate, lang.Final):
    column: str

    _: dc.KW_ONLY

    negated: bool = False


@dc.dataclass(frozen=True)
class Not(Predicate, lang.Final):
    predicate: Predicate


@dc.dataclass(frozen=True)
class And(Predicate, lang.Final):
    predicates: ta.Sequence[Predicate] = dc.xfield(coerce=tuple)


@dc.dataclass(frozen=True)
class Or(Predicate, lang.Final):
    predicates: ta.Sequence[Predicate] = dc.xfield(coerce=tuple)


##


CanPredicate: ta.TypeAlias = Predicate | str


def as_predicate(p: CanPredicate) -> Predicate:
    if isinstance(p, Predicate):
        return p
    elif isinstance(p, str):
        return RawPredicate(p)
    else:
        raise TypeError(p)


def as_opt_predicate(p: CanPredicate | None) -> Predicate | None:
    return None if p is None else as_predicate(p)
