"""
https://github.com/chadbrewbaker/ReverseSnowflakeJoins/blob/master/dir.g lolwut
 - https://github.com/chadbrewbaker/ReverseSnowflakeJoins/blob/5a1186843b47db0c94d976ca115efa6012b572ba/gui.py#L37
 - * https://linux.die.net/man/1/gvpr *
 - https://github.com/rodw/gvpr-lib
"""
import typing as ta

from ... import check
from ... import collections as col
from ... import dataclasses as dc
from ... import lang


##


class Item(dc.Frozen, lang.Abstract, lang.Sealed):
    pass


class Value(Item, lang.Abstract):
    @classmethod
    def of(cls, obj: ta.Union['Value', str, ta.Sequence]) -> 'Value':
        if isinstance(obj, Value):
            return obj
        elif isinstance(obj, str):
            return Text(obj)
        elif isinstance(obj, ta.Sequence):
            return Table.of(obj)
        else:
            raise TypeError(obj)


class Raw(Value):
    raw: str

    @classmethod
    def of(cls, obj: ta.Union['Raw', str]) -> 'Raw':  # type: ignore
        if isinstance(obj, Raw):
            return obj
        elif isinstance(obj, str):
            return Raw(obj)
        else:
            raise TypeError(obj)


class Text(Value):
    text: str

    @classmethod
    def of(cls, obj: ta.Union['Text', str]) -> 'Text':  # type: ignore
        if isinstance(obj, Text):
            return obj
        elif isinstance(obj, str):
            return Text(obj)
        else:
            raise TypeError(obj)


class Cell(Item):
    value: Value

    @classmethod
    def of(cls, obj: ta.Union['Cell', ta.Any]) -> 'Cell':
        if isinstance(obj, Cell):
            return obj
        else:
            return Cell(Value.of(obj))


class Row(Item):
    cells: ta.Sequence[Cell] = dc.xfield(coerce=col.seq)

    @classmethod
    def of(cls, obj: ta.Union['Row', ta.Sequence[ta.Any]]) -> 'Row':
        if isinstance(obj, Row):
            return obj
        elif isinstance(obj, str):
            raise TypeError(obj)
        elif isinstance(obj, ta.Sequence):
            return Row([Cell.of(e) for e in obj])
        else:
            raise TypeError(obj)


class Table(Value):
    rows: ta.Sequence[Row] = dc.xfield(coerce=col.seq)

    @classmethod
    def of(cls, obj: ta.Union['Table', ta.Sequence[ta.Any]]) -> 'Table':  # type: ignore
        if isinstance(obj, Table):
            return obj
        elif isinstance(obj, str):
            raise TypeError(obj)
        elif isinstance(obj, ta.Sequence):
            return Table([Row.of(e) for e in obj])
        else:
            raise TypeError(obj)


class Id(Item):
    id: str

    @classmethod
    def of(cls, obj: ta.Union['Id', str]) -> 'Id':
        if isinstance(obj, Id):
            return obj
        elif isinstance(obj, str):
            return Id(obj)
        else:
            raise TypeError(obj)


class Attrs(Item):
    attrs: ta.Mapping[str, Value] = dc.field(
        coerce=lambda o: col.frozendict(
            (check.not_empty(check.isinstance(k, str)), Value.of(v))  # type: ignore
            for k, v in check.isinstance(o, ta.Mapping).items()
        ),
    )

    @classmethod
    def of(cls, obj: ta.Union['Attrs', ta.Mapping[str, ta.Any]]) -> 'Attrs':
        if isinstance(obj, Attrs):
            return obj
        elif isinstance(obj, ta.Mapping):
            return Attrs(obj)
        else:
            raise TypeError(obj)


class Stmt(Item, lang.Abstract):
    pass


class RawStmt(Stmt):
    raw: str

    @classmethod
    def of(cls, obj: ta.Union['RawStmt', str]) -> 'RawStmt':
        if isinstance(obj, RawStmt):
            return obj
        elif isinstance(obj, str):
            return RawStmt(obj)
        else:
            raise TypeError(obj)


class Edge(Stmt):
    left: Id = dc.xfield(coerce=Id.of)
    right: Id = dc.xfield(coerce=Id.of)
    attrs: Attrs = dc.xfield(default=Attrs({}), coerce=Attrs.of)


class Node(Stmt):
    id: Id = dc.xfield(coerce=Id.of)
    attrs: Attrs = dc.xfield(default=Attrs({}), coerce=Attrs.of)


class Graph(Item):
    stmts: ta.Sequence[Stmt] = dc.xfield(coerce=col.seq)

    id: Id = dc.xfield(default=Id('G'), kw_only=True)
