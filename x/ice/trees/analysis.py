"""
TODO:
 - dom's
 - 'tracebacks'
 - jinja usage
 - types
  - including inferred jinja
 - * min/max/expected rowcounts *
  - if using insert into pagerduty/jira/slack/email/etc enforce bounds
 - cache/memo wrap ana dispatch.prop?

lint:
 - div0
 - bad auto-str conversion / missing try_parse
"""
import typing as ta

from omnibus import check
from omnibus import collections as ocol
from omnibus import dispatch
from omnibus import lang
from omnibus import properties

from . import nodes as no
from ..utils import memoized_unary


T = ta.TypeVar('T')
NodeGen = ta.Generator[no.Node, None, None]


class BasicAnalysis:

    def __init__(self, root: no.Node) -> None:
        super().__init__()

        self._root = root

        def walk(cur: no.Node) -> None:
            if cur in node_set:
                raise Exception(f'Duplicate node: {cur}', cur)
            nodes.append(cur)
            node_set.add(cur)
            for child in cur.children:
                walk(child)

        self._nodes = nodes = []
        self._node_set = node_set = ocol.IdentitySet()
        walk(root)

        self._node_sets_by_type: ta.Dict[type, ta.AbstractSet[no.Node]] = {}

    @property
    def root(self) -> no.Node:
        return self._root

    @property
    def nodes(self) -> ta.Sequence[no.Node]:
        return self._nodes

    @property
    def node_set(self) -> ta.AbstractSet[no.Node]:
        return self._node_set

    def get_node_type_set(self, ty: ta.Type[T]) -> ta.AbstractSet[T]:
        try:
            return self._node_sets_by_type[ty]
        except KeyError:
            ret = self._node_sets_by_type[ty] = ocol.IdentitySet(n for n in self.nodes if isinstance(n, ty))
            return ret

    @properties.cached
    def parents_by_node(self) -> ta.Mapping[no.Node, no.Node]:
        def walk(cur: no.Node) -> None:
            for child in cur.children:
                dct[child] = cur
                walk(child)
        dct = ocol.IdentityKeyDict()
        walk(self._root)
        return dct

    def yield_ancestors(self, node: no.Node) -> NodeGen:
        cur = node
        while True:
            cur = self.parents_by_node.get(cur)
            if cur is None:
                break
            yield cur

    def get_first_parent_of_type(self, node: no.Node, ty: ta.Type[T]) -> ta.Optional[no.Node]:
        for cur in self.yield_ancestors(node):
            if isinstance(cur, ty):
                return cur
        return None

    @properties.cached
    def child_sets_by_node(self) -> ta.Mapping[no.Node, ta.AbstractSet[no.Node]]:
        def walk(cur: no.Node) -> None:
            dct[cur] = ocol.IdentitySet(cur.children)
            for child in cur.children:
                walk(child)
        dct = ocol.IdentityKeyDict()
        walk(self._root)
        return dct


basic = BasicAnalysis


class Analyzer(dispatch.Class, lang.Abstract, ta.Generic[T]):
    _process = dispatch.property()

    __call__ = memoized_unary(_process, identity=True, max_recursion=100)

    def _process(self, node: no.Node) -> T:  # noqa
        raise TypeError(node)


class PreferredNameAnalyzer(Analyzer[ta.Optional[str]]):

    def _traverse(self, nodes: ta.Iterable) -> None:
        for node in nodes:
            self(node)

    def _from_children(self, node: no.Node) -> ta.Optional[str]:
        children = {self(c) for c in node.children}
        if len(children) == 1:
            return check.single(children)
        else:
            return None

    def _process(self, node: no.AliasedRelation) -> ta.Optional[str]:  # noqa
        return node.alias.name

    def _process(self, node: no.AllSelectItem) -> ta.Optional[str]:  # noqa
        return None

    def _process(self, node: no.Expr) -> ta.Optional[str]:  # noqa
        return self._from_children(node)

    def _process(self, node: no.ExprSelectItem) -> ta.Optional[str]:  # noqa
        if node.label is not None:
            return node.label.name
        else:
            return self(node.value)

    def _process(self, node: no.QualifiedNameNode) -> ta.Optional[str]:  # noqa
        return node.name[-1]

    def _process(self, node: no.Relation) -> ta.Optional[str]:  # noqa
        return self._from_children(node)

    def _process(self, node: no.Select) -> ta.Optional[str]:  # noqa
        self._traverse(node.items)
        self._traverse(node.relations)
        return None

    def _process(self, node: no.Table) -> ta.Optional[str]:  # noqa
        return node.name.name[-1]
