import html
import io
import subprocess
import tempfile
import time
import typing as ta

from ... import dispatch
from .items import Attrs
from .items import Cell
from .items import Edge
from .items import Graph
from .items import Id
from .items import Item
from .items import Node
from .items import Raw
from .items import RawStmt
from .items import Row
from .items import Table
from .items import Text


class Renderer:

    def __init__(self, out: ta.TextIO) -> None:
        super().__init__()

        self._out = out

    @dispatch.method
    def render(self, item: Item) -> None:
        raise TypeError(item)

    @render.register
    def render_raw(self, item: Raw) -> None:
        self._out.write(item.raw)

    @render.register
    def render_text(self, item: Text) -> None:
        self._out.write(html.escape(item.text))

    @render.register
    def render_cell(self, item: Cell) -> None:
        self._out.write('<td>')
        self.render(item.value)
        self._out.write('</td>')

    @render.register
    def render_row(self, item: Row) -> None:
        self._out.write('<tr>')
        for cell in item.cells:
            self.render(cell)
        self._out.write('</tr>')

    @render.register
    def render_table(self, item: Table) -> None:
        self._out.write('<table>')
        for row in item.rows:
            self.render(row)
        self._out.write('</table>')

    @render.register
    def render_id(self, item: Id) -> None:
        self._out.write(f'"{item.id}"')

    @render.register
    def render_attrs(self, item: Attrs) -> None:
        if item.attrs:
            self._out.write('[')
            for i, (k, v) in enumerate(item.attrs.items()):
                if i:
                    self._out.write(', ')
                self._out.write(k)
                self._out.write('=<')
                self.render(v)
                self._out.write('>')
            self._out.write(']')

    @render.register
    def render_raw_stmt(self, item: RawStmt) -> None:
        self._out.write(item.raw)
        self._out.write('\n')

    @render.register
    def render_edge(self, item: Edge) -> None:
        self.render(item.left)
        self._out.write(' -> ')
        self.render(item.right)
        if item.attrs.attrs:
            self._out.write(' ')
            self.render(item.attrs)
        self._out.write(';\n')

    @render.register
    def render_node(self, item: Node) -> None:
        self.render(item.id)
        if item.attrs.attrs:
            self._out.write(' ')
            self.render(item.attrs)
        self._out.write(';\n')

    @render.register
    def render_graph(self, item: Graph) -> None:
        self._out.write('digraph ')
        self.render(item.id)
        self._out.write(' {\n')
        for stmt in item.stmts:
            self.render(stmt)
        self._out.write('}\n')


def render(item: Item) -> str:
    out = io.StringIO()
    Renderer(out).render(item)
    return out.getvalue()


def open_dot(
        gv: str,
        *,
        timeout_s: float = 1.,
        sleep_s: float = 0.,
        delete: bool = False,
) -> None:
    stdout, _ = subprocess.Popen(
        ['dot', '-Tpdf'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    ).communicate(
        input=gv.encode('utf-8'),
        timeout=timeout_s,
    )

    with tempfile.NamedTemporaryFile(
        suffix='.pdf',
        delete=delete,
    ) as pdf:
        pdf.file.write(stdout)
        pdf.file.flush()

    _, _ = subprocess.Popen(
        ['open', pdf.name],
    ).communicate(
        timeout=timeout_s,
    )

    if sleep_s > 0.:
        time.sleep(sleep_s)
