import typing as ta

from ... import dataclasses as dc
from ... import lang
from .base import Builder
from .selects import Select
from .stmts import Stmt


##


class Union(Stmt, lang.Final):
    selects: ta.Sequence[Select] = dc.xfield(coerce=tuple)

    _: dc.KW_ONLY

    all: bool = False


class UnionBuilder(Builder):
    def union(self, *selects: Select, all: bool = False) -> Union:  # noqa
        return Union(selects, all=all)
