import typing as ta

from omlish import dataclasses as dc
from omlish import dispatch
from omlish import lang


Row: ta.TypeAlias = ta.Mapping[str, ta.Any]


##


class Node(dc.Frozen, lang.Abstract):
    pass


class Filter(Node, lang.Final):
    src: Node
    fn: ta.Callable[[Row], bool]


class Scan(Node, lang.Final):
    table: str
    columns: ta.Sequence[str] | None = None


##


class Driver:
    def __init__(
            self,
            *,
            tables: ta.Mapping[str, ta.Sequence[Row]] | None = None,
    ) -> None:
        super().__init__()

        self._tables = tables

    @dispatch.method
    def drive(self, n: Node) -> ta.Iterable[Row]:
        raise TypeError(n)

    @drive.register
    def drive_filter(self, n: Filter) -> ta.Iterable[Row]:
        src = self.drive(n.src)
        for r in src:
            if n.fn(r):
                yield r

    @drive.register
    def drive_scan(self, n: Scan) -> ta.Iterable[Row]:
        if not (tbls := self._tables):
            raise KeyError(n.table)
        tbl = tbls[n.table]

        if n.columns is not None:
            ks: set[str] | None = set(n.columns)
        else:
            ks = None

        for r in tbl:
            if ks is not None:
                r = {k: v for k, v in r.items() if k in ks}
            yield r


##


def _main() -> None:
    foo_rows = [
        {'x': 0, 'y': 1},
        {'x': 2, 'y': 3},
        {'x': 4, 'y': 5},
    ]
    x: Node = Scan('foo', ['y'])
    x = Filter(x, lambda r: r['y'] != 3)
    d = Driver(tables={'foo': foo_rows})
    o = list(d.drive(x))
    print(o)


if __name__ == '__main__':
    _main()
