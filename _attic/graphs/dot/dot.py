"""
TODO:
 - import colorsys

https://github.com/chadbrewbaker/ReverseSnowflakeJoins/blob/master/dir.g lolwut
 - https://github.com/chadbrewbaker/ReverseSnowflakeJoins/blob/5a1186843b47db0c94d976ca115efa6012b572ba/gui.py#L37
 - * https://linux.die.net/man/1/gvpr *
 - https://github.com/rodw/gvpr-lib
"""
import html
import io
import subprocess
import typing as ta

from ... import check
from ... import collections as col
from ... import dataclasses as dc
from ... import dispatch as disp
from ... import os as oos


def escape(s: str) -> str:
    return html.escape(s).replace('@', '&#64;')


class Color(ta.NamedTuple):
    r: int
    g: int
    b: int


def gen_rainbow(steps: int) -> ta.List[Color]:
    colors = []
    for r in range(steps):
        colors.append(Color(r * 255 // steps, 255, 0))
    for g in range(steps, 0, -1):
        colors.append(Color(255, g * 255 // steps, 0))
    for b in range(steps):
        colors.append(Color(255, 0, b * 255 // steps))
    for r in range(steps, 0, -1):
        colors.append(Color(r * 255 // steps, 0, 255))
    for g in range(steps):
        colors.append(Color(0, g * 255 // steps, 255))
    for b in range(steps, 0, -1):
        colors.append(Color(0, 255, b * 255 // steps))
    colors.append(Color(0, 255, 0))
    return colors


class Item(dc.Enum, sealed=True):
    pass


class Value(Item, abstract=True):

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
    cells: ta.Sequence[Cell] = dc.field(coerce=col.seq)

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
    rows: ta.Sequence[Row] = dc.field(coerce=col.seq)

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
            (check.not_empty(check.isinstance(k, str)), Value.of(v))
            for k, v in check.isinstance(o, ta.Mapping).items()
        )
    )

    @classmethod
    def of(cls, obj: ta.Union['Attrs', ta.Mapping[str, ta.Any]]) -> 'Attrs':
        if isinstance(obj, Attrs):
            return obj
        elif isinstance(obj, ta.Mapping):
            return Attrs(obj)
        else:
            raise TypeError(obj)


class Stmt(Item, abstract=True):
    pass


class RawStmt(Stmt):
    raw: str

    @classmethod
    def of(cls, obj: ta.Union['RawStmt', str]) -> 'RawStmt':  # type: ignore
        if isinstance(obj, RawStmt):
            return obj
        elif isinstance(obj, str):
            return RawStmt(obj)
        else:
            raise TypeError(obj)


class Edge(Stmt):
    left: Id = dc.field(coerce=Id.of)
    right: Id = dc.field(coerce=Id.of)
    attrs: Attrs = dc.field(Attrs({}), coerce=Attrs.of)


class Node(Stmt):
    id: Id = dc.field(coerce=Id.of)
    attrs: Attrs = dc.field(Attrs({}), coerce=Attrs.of)


class Graph(Item):
    stmts: ta.Sequence[Stmt] = dc.field(coerce=col.seq)

    id: Id = dc.field(Id('G'), kwonly=True)


class Renderer(disp.Class):

    def __init__(self, out: ta.TextIO) -> None:
        super().__init__()

        self._out = out

    __call__ = disp.property()

    def __call__(self, item: Item) -> None:  # noqa
        raise TypeError(item)

    def __call__(self, item: Raw) -> None:   # noqa
        self._out.write(item.raw)

    def __call__(self, item: Text) -> None:  # noqa
        self._out.write(html.escape(item.text))

    def __call__(self, item: Cell) -> None:  # noqa
        self._out.write('<td>')
        self(item.value)
        self._out.write('</td>')

    def __call__(self, item: Row) -> None:  # noqa
        self._out.write('<tr>')
        for cell in item.cells:
            self(cell)
        self._out.write('</tr>')

    def __call__(self, item: Table) -> None:  # noqa
        self._out.write('<table>')
        for row in item.rows:
            self(row)
        self._out.write('</table>')

    def __call__(self, item: Id) -> None:  # noqa
        self._out.write(f'"{item.id}"')

    def __call__(self, item: Attrs) -> None:  # noqa
        if item.attrs:
            self._out.write('[')
            for i, (k, v) in enumerate(item.attrs.items()):
                if i:
                    self._out.write(', ')
                self._out.write(k)
                self._out.write('=<')
                self(v)
                self._out.write('>')
            self._out.write(']')

    def __call__(self, item: RawStmt) -> None:  # noqa
        self._out.write(item.raw)
        self._out.write('\n')

    def __call__(self, item: Edge) -> None:  # noqa
        self(item.left)
        self._out.write(' -> ')
        self(item.right)
        if item.attrs.attrs:
            self._out.write(' ')
            self(item.attrs)
        self._out.write(';\n')

    def __call__(self, item: Node) -> None:  # noqa
        self(item.id)
        if item.attrs.attrs:
            self._out.write(' ')
            self(item.attrs)
        self._out.write(';\n')

    def __call__(self, item: Graph) -> None:  # noqa
        self._out.write('digraph ')
        self(item.id)
        self._out.write(' {\n')
        for stmt in item.stmts:
            self(stmt)
        self._out.write('}\n')


def render(item: Item) -> str:
    out = io.StringIO()
    Renderer(out)(item)
    return out.getvalue()


def open_dot(gv: str, *, timeout: float = 1.) -> None:
    stdout, _ = subprocess.Popen(
        ['dot', '-Tpdf'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    ).communicate(
        input=gv.encode('utf-8'),
        timeout=timeout,
    )

    with oos.tmp_file() as pdf:
        pdf.file.write(stdout)
        pdf.file.flush()

        _, _ = subprocess.Popen(
            ['open', pdf.name],
        ).communicate(
            timeout=timeout,
        )
