import abc
import typing as ta

from omnibus import check
from omnibus import collections as ocol
from omnibus import dataclasses as dc
from omnibus import dispatch

from . import nodes as no
from .symbols import Symbol
from .symbols import SymbolAnalysis
from .symbols import SymbolRef


class Origin(dc.Enum, eq=False):
    node: no.Node = dc.field(check=lambda o: isinstance(o, no.Node))

    @abc.abstractproperty
    def srcs(self) -> ta.Collection['Origin']:
        raise NotImplementedError


class Derived(Origin):
    srcs: ta.Sequence[Origin] = dc.field(coerce=ocol.seq, check=lambda l: all(isinstance(e, Origin) for e in l))


class Link(Origin, abstract=True):
    src: Origin = dc.field(check=lambda o: isinstance(o, Origin))

    @property
    def srcs(self) -> ta.Collection[Origin]:
        return [self.src]


class Leaf(Origin, abstract=True):

    @property
    def srcs(self) -> ta.Collection[Origin]:
        return []


class Direct(Link):
    pass


class Derive(Link):
    pass


class Export(Link):
    sym: Symbol = dc.field(check=lambda o: isinstance(o, Symbol))


class Import(Link):
    ref: SymbolRef = dc.field(check=lambda o: isinstance(o, SymbolRef))


class Constant(Leaf):
    pass


class Scan(Leaf):
    sym: Symbol = dc.field(check=lambda o: isinstance(o, Symbol))


class Context(dc.Enum, ta.Iterable[Origin]):
    node: no.Node = dc.field(check=lambda o: isinstance(o, no.Node))


class Value(Context):
    ori: Origin = dc.field(check=lambda o: isinstance(o, Origin))

    def __iter__(self) -> ta.Iterator[Origin]:
        yield self.ori


class Scope(Context):
    oris_by_sym: ta.Mapping[Symbol, Origin] = dc.field(
        coerce=ocol.map, check=lambda dct: all(isinstance(k, Symbol) and isinstance(v, Origin) for k, v in dct.items()))

    def __iter__(self) -> ta.Iterator[Origin]:
        yield from self.oris_by_sym.values()


class OriginAnalysis:

    def __init__(self, ctxs: ta.Iterable[Context]) -> None:
        super().__init__()

        self._ctxs = list(ctxs)

        self._ctxs_by_node: ta.MutableMapping[no.Node, Context] = ocol.IdentityKeyDict()
        self._ori_sets_by_node: ta.Mapping[no.Node, ta.AbstractSet[Origin]] = ocol.IdentityKeyDict()
        self._exports_by_sym: ta.MutableMapping[Symbol, Export] = {}
        self._exports_by_node_by_name: ta.MutableMapping[no.Node, ta.MutableMapping[str, Export]] = ocol.IdentityKeyDict()  # noqa

        for ctx in self._ctxs:
            check.isinstance(ctx, Context)
            check.not_in(ctx.node, self._ctxs_by_node)
            self._ctxs_by_node[ctx.node] = ctx

            for ori in ctx:
                self._ori_sets_by_node.setdefault(ori.node, set()).add(ori)

                if isinstance(ori, Export):
                    check.not_in(ori.sym, self._exports_by_sym)
                    self._exports_by_sym[ori.sym] = ori

                    if ori.sym.name is not None:
                        dct = self._exports_by_node_by_name.setdefault(ori.node, {})
                        check.not_in(ori.sym.name, dct)
                        dct[ori.sym.name] = ori

    @property
    def ctxs(self) -> ta.Sequence[Context]:
        return self._ctxs

    @property
    def ctxs_by_node(self) -> ta.Mapping[no.Node, Context]:
        return self._ctxs_by_node

    @property
    def ori_sets_by_node(self) -> ta.Mapping[no.Node, ta.AbstractSet[Origin]]:
        return self._ori_sets_by_node

    @property
    def exports_by_sym(self) -> ta.MutableMapping[Symbol, Export]:
        return self._exports_by_sym

    @property
    def exports_by_node_by_name(self) -> ta.MutableMapping[no.Node, ta.MutableMapping[str, Export]]:
        return self._exports_by_node_by_name


class _Analyzer(dispatch.Class):

    def __init__(self, sym_ana: SymbolAnalysis) -> None:
        super().__init__()

        self._sym_ana = check.isinstance(sym_ana, SymbolAnalysis)

        self._ctxs_by_node: ta.MutableMapping[no.Node, Context] = ocol.IdentityKeyDict()
        self._exports_by_sym: ta.MutableMapping[Symbol, Export] = {}

    def _add(self, ctx: Context) -> Context:
        check.isinstance(ctx, Context)
        check.not_in(ctx.node, self._ctxs_by_node)
        self._ctxs_by_node[ctx.node] = ctx

        for ori in ctx:
            check.isinstance(ori, Origin)

            if isinstance(ori, Export):
                check.not_in(ori.sym, self._exports_by_sym)
                self._exports_by_sym[ori.sym] = ori

        return ctx

    __call__ = dispatch.property()

    def __call__(self, node: no.Node) -> Context:  # noqa
        raise TypeError(node)

    def __call__(self, node: no.AliasedRelation) -> Context:  # noqa
        src_scope = check.isinstance(self(node.relation), Scope)
        scope = {}
        for sym, src in src_scope.oris_by_sym.items():
            scope[sym] = Export(node, src, sym)
        return self._add(Scope(node, scope))

    def __call__(self, node: no.AllSelectItem) -> Context:  # noqa
        raise TypeError(node)

    def __call__(self, node: no.Expr) -> Context:  # noqa
        check.not_empty(list(node.children))
        srcs = [check.isinstance(self(check.isinstance(n, no.Expr)), Value).ori for n in node.children]
        return self._add(Value(node, Derived(node, srcs)))

    def __call__(self, node: no.ExprSelectItem) -> Context:  # noqa
        src = check.isinstance(self(node.value), Value).ori
        return self._add(Value(node, Direct(node, src)))

    def __call__(self, node: no.FunctionCallExpr) -> Context:  # noqa
        srcs = [check.isinstance(self(n), Value).ori for n in node.call.args]
        return self._add(Value(node, Derived(node, srcs)))

    def __call__(self, node: no.Primitive) -> Context:  # noqa
        return self._add(Value(node, Constant(node)))

    def __call__(self, node: no.QualifiedNameNode) -> Context:  # noqa
        ref = self._sym_ana.refs_by_node[node]
        sym = self._sym_ana.resolutions.syms[ref]
        src = self._exports_by_sym[sym]
        return self._add(Value(node, Import(node, src, ref)))

    def __call__(self, node: no.Select) -> Context:  # noqa
        for rel in node.relations:
            self(rel)
        scope = {}
        for item in node.items:
            sym = check.single(self._sym_ana.sym_sets_by_node[item])
            src = check.isinstance(self(item), Value).ori
            scope[sym] = Export(node, src, sym)
        return self._add(Scope(node, scope))

    def __call__(self, node: no.Table) -> Context:  # noqa
        return self._add(Scope(node, {
            sym: Scan(node, sym)
            for sym in self._sym_ana.sym_sets_by_node.get(node, [])
            for _ in [check.state(sym.node is node)]
        }))


def analyze(root: no.Node, sym_ana: SymbolAnalysis) -> OriginAnalysis:
    ana = _Analyzer(sym_ana)
    ana(root)
    return OriginAnalysis(ana._ctxs_by_node.values())
