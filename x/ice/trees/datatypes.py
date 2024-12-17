import typing as ta

from omnibus import check
from omnibus import dispatch

from . import nodes as no
from . import origins as oris
from .. import metadata as md
from ..utils import memoized_unary
from .analysis import basic


class TypeAnalysis:

    def __init__(self, dts_by_node: ta.Mapping[no.Node, md.Datatype]) -> None:
        super().__init__()

        self._dts_by_node = dts_by_node

    @property
    def dts_by_node(self) -> ta.Mapping[no.Node, md.Datatype]:
        return self._dts_by_node


class _Analyzer(dispatch.Class):

    def __init__(self, root: no.Node, ori_ana: oris.OriginAnalysis, catalog: md.Catalog) -> None:
        super().__init__()

        self._root = check.isinstance(root, no.Node)
        self._ori_ana = check.isinstance(ori_ana, oris.OriginAnalysis)
        self._catalog = check.isinstance(catalog, md.Catalog)

        self._basic = basic(root)

    _process = dispatch.property()

    __call__ = memoized_unary(_process, identity=True, max_recursion=100)

    @property
    def dts_by_node(self) -> ta.Mapping[no.Node, md.Datatype]:
        return self.__call__.dct

    def _process(self, ori: oris.Origin) -> md.Datatype:  # noqa
        raise TypeError(ori)

    def _process(self, node: no.Node) -> md.Datatype:  # noqa
        raise TypeError(node)

    def _process(self, ori: oris.Constant) -> md.Datatype:  # noqa
        return self(ori.node)

    def _process(self, ori: oris.Derived) -> md.Datatype:  # noqa
        return self(ori.node)

    def _process(self, ori: oris.Direct) -> md.Datatype:  # noqa
        return self(ori.src)

    def _process(self, ori: oris.Export) -> md.Datatype:  # noqa
        return self(ori.src)

    def _process(self, ori: oris.Import) -> md.Datatype:  # noqa
        return self(ori.src)

    def _process(self, ori: oris.Scan) -> md.Datatype:  # noqa
        tbl = self._catalog.tables_by_name[check.isinstance(ori.node, no.Table).name.name]
        col = tbl.columns_by_name[ori.sym.name]
        return col.type

    def _process(self, node: no.BinaryExpr) -> md.Datatype:  # noqa
        left = self(node.left)
        right = self(node.right)
        check.state(left == right)
        return left

    def _process(self, node: no.EFalse) -> md.Datatype:  # noqa
        return md.BOOLEAN

    def _process(self, node: no.ETrue) -> md.Datatype:  # noqa
        return md.BOOLEAN

    def _process(self, node: no.Integer) -> md.Datatype:  # noqa
        return md.INTEGER

    def _process(self, node: no.QualifiedNameNode) -> md.Datatype:  # noqa
        return self(check.single(self._ori_ana.ori_sets_by_node[node]))

    def _process(self, node: no.Select) -> md.Datatype:  # noqa
        cols = [(k, self(v)) for k, v in self._ori_ana.exports_by_node_by_name.get(node, {}).items()]
        return md.TableType(cols)

    def _process(self, node: no.String) -> md.Datatype:  # noqa
        return md.STRING


def analyze(root: no.Node, ori_ana: oris.OriginAnalysis, catalog: md.Catalog) -> TypeAnalysis:
    ana = _Analyzer(root, ori_ana, catalog)
    ana(root)
    return TypeAnalysis(check.not_empty(ana.dts_by_node))
