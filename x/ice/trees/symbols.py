import collections
import typing as ta

from omnibus import check
from omnibus import collections as ocol
from omnibus import dataclasses as dc
from omnibus import dispatch
from omnibus import properties

from . import nodes as no
from .. import metadata as md
from ..types import QualifiedName
from ..utils import build_dc_repr


class Symbol(dc.Pure, eq=False):
    name: ta.Optional[str]
    node: no.Node
    scope: 'SymbolScope'

    def __post_init__(self) -> None:
        self.scope._add_sym(self)

    __repr__ = build_dc_repr


class SymbolRef(dc.Pure, eq=False):
    name: QualifiedName
    node: no.Node
    scope: 'SymbolScope'

    def __post_init__(self) -> None:
        self.scope._add_ref(self)

    __repr__ = build_dc_repr


class SymbolScope(dc.Data, eq=False, final=True):
    node: no.Node
    parent: ta.Optional['SymbolScope'] = None
    name: ta.Optional[str] = dc.field(default=None, kwonly=True)

    __repr__ = build_dc_repr

    def __post_init__(self) -> None:
        self._enclosed_nodes: ta.MutableSet[no.Node] = ocol.IdentitySet()
        self._children: ta.MutableSet['SymbolScope'] = set()
        self._syms: ta.MutableSet[Symbol] = set()
        self._refs: ta.MutableSet[SymbolRef] = set()
        self._sealed = False

        if self.parent is not None:
            self.parent._children.add(self)
        self._enclosed_nodes.add(self.node)

    def _add_sym(self, sym: Symbol) -> None:
        check.state(not self._sealed)
        self._syms.add(sym)

    def _add_ref(self, ref: SymbolRef) -> None:
        check.state(not self._sealed)
        self._refs.add(ref)

    def _seal(self) -> None:
        self._sealed = True

    @property
    def enclosed_nodes(self) -> ta.AbstractSet[no.Node]:
        return self._enclosed_nodes

    @property
    def children(self) -> ta.AbstractSet['SymbolScope']:
        return self._children

    @property
    def syms(self) -> ta.AbstractSet[Symbol]:
        return self._syms

    @property
    def refs(self) -> ta.AbstractSet[SymbolRef]:
        return self._refs


class SymbolResolutions(dc.Pure, eq=False):
    syms: ta.Mapping[SymbolRef, Symbol]
    refs: ta.Mapping[Symbol, ta.AbstractSet[SymbolRef]]


class SymbolAnalysis:

    def __init__(self, root: SymbolScope) -> None:
        super().__init__()

        self._root = check.isinstance(root, SymbolScope)

        self._scopes: ta.MutableSet[SymbolScope] = set()
        self._scopes_by_node: ta.MutableMapping[no.Node, SymbolScope] = ocol.IdentityKeyDict()
        self._sym_sets_by_node: ta.MutableMapping[no.Node, ta.MutableSet[Symbol]] = ocol.IdentityKeyDict()
        self._refs_by_node: ta.MutableMapping[no.Node, SymbolRef] = ocol.IdentityKeyDict()

        seen: ta.MutableSet[SymbolScope] = set()
        queue: ta.Deque[SymbolScope] = collections.deque()
        queue.append(root)
        seen.add(root)

        while queue:
            cur = queue.pop()
            check.not_in(cur, self._scopes)
            cur._seal()
            self._scopes.add(cur)
            for n in cur.enclosed_nodes:
                check.not_in(n, self._scopes_by_node)
                self._scopes_by_node[n] = cur
            for s in cur.syms:
                self._sym_sets_by_node.setdefault(s.node, set()).add(s)
            for r in cur.refs:
                check.not_in(r.node, self._refs_by_node)
                self._refs_by_node[r.node] = r
            for c in cur.children:
                check.not_in(c, seen)
                queue.append(c)
                seen.add(c)

    @property
    def root(self) -> SymbolScope:
        return self._root

    @property
    def scopes(self) -> ta.AbstractSet[SymbolScope]:
        return self._scopes

    @property
    def scopes_by_node(self) -> ta.Mapping[no.Node, SymbolScope]:
        return self._scopes_by_node

    @property
    def sym_sets_by_node(self) -> ta.Mapping[no.Node, ta.AbstractSet[Symbol]]:
        return self._sym_sets_by_node

    @property
    def refs_by_node(self) -> ta.Mapping[no.Node, SymbolRef]:
        return self._refs_by_node

    @staticmethod
    def get_scope_matches(ref: SymbolRef) -> ta.List[Symbol]:
        return [
            s
            for sc in ref.scope.children
            for s in sc.syms
            if s.name == ref.name[0]
        ]

    @staticmethod
    def get_sym_matches(ref: SymbolRef) -> ta.List[Symbol]:
        check.arg(len(ref.name) > 1)
        return [
            s
            for sc in ref.scope.children
            if sc.name == ref.name[0]
            for s in sc.syms
            if s.name == ref.name[1]
        ]

    @properties.cached
    @property
    def resolutions(self) -> SymbolResolutions:
        syms: ta.Dict[SymbolRef, Symbol] = {}
        refs: ta.Dict[Symbol, ta.Set[SymbolRef]] = {}

        for cur in self.scopes:
            for sr in cur.refs:
                if len(sr.name) > 1:
                    hits = self.get_sym_matches(sr)
                    if len(hits) == 1:
                        s = check.single(hits)
                        check.not_in(sr, syms)
                        syms[sr] = s
                        refs.setdefault(s, set()).add(sr)

        return SymbolResolutions(syms, refs)


class _Analyzer(dispatch.Class):

    def __init__(self, catalog: md.Catalog) -> None:
        super().__init__()

        self._catalog = check.isinstance(catalog, md.Catalog)

    def visit_children(
            self,
            node: no.Node,
            scope: ta.Optional[SymbolScope],
            *,
            exclude: ta.Iterable[no.Node] = (),
    ) -> None:
        for child in node.children:
            for exc in exclude:
                if child is exc:
                    break
            else:
                self(child, scope)

    def add_to(self, node: no.Node, scope: ta.Optional[SymbolScope]) -> None:
        if scope is not None:
            scope._enclosed_nodes.add(node)
        self.visit_children(node, scope)

    __call__ = dispatch.property()

    def __call__(self, node: no.Node, scope: ta.Optional[SymbolScope]) -> ta.Optional[SymbolScope]:  # noqa
        self.add_to(node, scope)
        return None

    def __call__(self, node: no.AliasedRelation, scope: ta.Optional[SymbolScope]) -> ta.Optional[SymbolScope]:  # noqa
        scope = SymbolScope(node, scope, name=node.alias.name)

        self.visit_children(node, scope)
        return scope

    def __call__(self, node: no.AllSelectItem, scope: ta.Optional[SymbolScope]) -> ta.Optional[SymbolScope]:  # noqa
        raise TypeError(node)

    def __call__(self, node: no.ExprSelectItem, scope: ta.Optional[SymbolScope]) -> ta.Optional[SymbolScope]:  # noqa
        if node.label is not None:
            name = node.label.name
        elif isinstance(node.value, no.QualifiedNameNode):
            name = node.value.parts[-1]
        else:
            name = None
        Symbol(name, node, scope)

        self.add_to(node, scope)
        return None

    def __call__(self, node: no.QualifiedNameNode, scope: ta.Optional[SymbolScope]) -> ta.Optional[SymbolScope]:  # noqa
        SymbolRef(node.name, node, scope)

        self.add_to(node, scope)
        return None

    def __call__(self, node: no.Select, scope: ta.Optional[SymbolScope]) -> ta.Optional[SymbolScope]:  # noqa
        scope = SymbolScope(node, scope)

        self.visit_children(node, scope)
        return scope

    def __call__(self, node: no.Table, scope: ta.Optional[SymbolScope]) -> ta.Optional[SymbolScope]:  # noqa
        tbl = self._catalog.tables_by_name[node.name.name]
        for col in tbl.columns:
            Symbol(col.name, node, scope)

        self.add_to(node, scope)
        return None


def analyze(root: no.Node, catalog: md.Catalog) -> SymbolAnalysis:
    scope = _Analyzer(catalog)(root, None)
    return SymbolAnalysis(scope)
