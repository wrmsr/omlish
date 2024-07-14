"""
TODO:
 - @property dfs, bfs
"""
import functools
import typing as ta
import weakref

from .. import check
from .. import collections as col
from .. import lang
from .. import nodal
from .. import properties


T = ta.TypeVar('T')
NodeT = ta.TypeVar('NodeT')
NodeWalker = ta.Callable[[NodeT], ta.Iterable[NodeT]]
NodeGenerator = ta.Generator[NodeT, None, None]
NodalT = ta.TypeVar('NodalT', bound=nodal.Nodal)


class NodeException(ta.Generic[NodeT], Exception):
    def __init__(self, node: NodeT, msg: str, *args, **kwargs) -> None:
        super().__init__(msg, *args, **kwargs)  # noqa
        self._node = node

    @property
    def node(self) -> NodeT:
        return self._node


class DuplicateNodeException(NodeException[NodeT]):
    def __init__(self, node: NodeT, *args, **kwargs) -> None:
        super().__init__(node, f'Duplicate node: {node!r}', *args, **kwargs)


class UnknownNodeException(NodeException[NodeT]):
    def __init__(self, node: NodeT, *args, **kwargs) -> None:
        super().__init__(node, f'Unknown node: {node!r}', *args, **kwargs)


class BasicTreeAnalysis(ta.Generic[NodeT]):

    def __init__(
            self,
            root: NodeT,
            walker: NodeWalker[NodeT],
            *,
            identity: bool = False,
    ) -> None:
        super().__init__()

        self._root = root
        self._walker = walker
        self._identity = identity

        self._set_fac: ta.Callable[..., ta.MutableSet[NodeT]] = col.IdentitySet if identity else set
        self._dict_fac: ta.Callable[..., ta.MutableMapping[NodeT, ta.Any]] = col.IdentityKeyDict if identity else dict
        self._idx_seq_fac: ta.Callable[..., col.IndexedSeq[NodeT]] = functools.partial(col.IndexedSeq, identity=identity)  # noqa

        def walk(cur: NodeT, parent: ta.Optional[NodeT]) -> None:
            check.not_none(cur)
            if cur in node_set:
                raise DuplicateNodeException(cur)

            nodes.append(cur)
            node_set.add(cur)
            if parent is None:
                check.state(cur is root)
            elif parent not in node_set:
                raise UnknownNodeException(parent)

            parents_by_node[cur] = parent

            children_by_node[cur] = children = list(walker(cur))
            child_sets_by_node[cur] = self._set_fac(children)
            for child in children:
                walk(child, cur)

        nodes: ta.List[NodeT] = []
        node_set: ta.MutableSet[NodeT] = self._set_fac()
        children_by_node: ta.MutableMapping[ta.Optional[NodeT], ta.Sequence[NodeT]] = self._dict_fac()
        child_sets_by_node: ta.MutableMapping[ta.Optional[NodeT], ta.AbstractSet[NodeT]] = self._dict_fac()
        parents_by_node: ta.MutableMapping[NodeT, ta.Optional[NodeT]] = self._dict_fac()

        children_by_node[None] = [root]
        child_sets_by_node[None] = self._set_fac([root])

        walk(root, None)

        self._nodes = self._idx_seq_fac(nodes)
        self._node_set: ta.AbstractSet[NodeT] = node_set
        self._children_by_node: ta.Mapping[ta.Optional[NodeT], col.IndexedSeq[NodeT]] = self._dict_fac(
            [(n, self._idx_seq_fac(cs)) for n, cs in children_by_node.items()])
        self._child_sets_by_node: ta.Mapping[ta.Optional[NodeT], ta.AbstractSet[NodeT]] = child_sets_by_node
        self._parents_by_node: ta.Mapping[NodeT, ta.Optional[NodeT]] = parents_by_node

    @property
    def root(self) -> NodeT:
        return self._root

    @property
    def nodes(self) -> col.IndexedSeq[NodeT]:
        return self._nodes

    @property
    def walker(self) -> NodeWalker[NodeT]:
        return self._walker

    @property
    def identity(self) -> bool:
        return self._identity

    @property
    def node_set(self) -> ta.AbstractSet[NodeT]:
        return self._node_set

    @property
    def children_by_node(self) -> ta.Mapping[NodeT, col.IndexedSeq[NodeT]]:
        return self._children_by_node

    @property
    def child_sets_by_node(self) -> ta.Mapping[NodeT, ta.AbstractSet[NodeT]]:
        return self._child_sets_by_node

    @property
    def parents_by_node(self) -> ta.Mapping[NodeT, ta.Optional[NodeT]]:
        return self._parents_by_node

    @classmethod
    def from_parents(
            cls,
            src: ta.Union[
                ta.Mapping[NodeT, ta.Optional[NodeT]],
                ta.Iterable[ta.Tuple[NodeT, ta.Optional[NodeT]]],
            ],
            *,
            identity: bool = False,
            **kwargs
    ) -> 'BasicTreeAnalysis[NodeT]':
        if isinstance(src, ta.Mapping):
            pairs = list(src.items())
        elif isinstance(src, ta.Iterable):
            pairs = list(src)
        else:
            raise TypeError(src)

        pairs: ta.Sequence[ta.Tuple[NodeT, NodeT]]
        pairs = [(check.not_none(n), p) for n, p in pairs]

        root = check.single([n for n, p in pairs if p is None])  # noqa

        children_by_node: ta.MutableMapping[NodeT, ta.MutableSequence[NodeT]]
        children_by_node = col.IdentityKeyDict() if identity else {}
        for n, _ in pairs:
            children_by_node[n] = []
        for n, p in pairs:
            if p is not None:
                children_by_node[p].append(n)

        return cls(
            root,
            children_by_node.__getitem__,
            identity=identity,
            **kwargs,
        )

    @classmethod
    def from_children(
            cls,
            src: ta.Union[
                ta.Mapping[NodeT, ta.Iterable[NodeT]],
                ta.Iterable[ta.Tuple[NodeT, ta.Iterable[NodeT]]],
            ],
            *,
            identity: bool = False,
            **kwargs
    ) -> 'BasicTreeAnalysis[NodeT]':
        if isinstance(src, ta.Mapping):
            pairs = list(src.items())
        elif isinstance(src, ta.Iterable):
            pairs = list(src)
        else:
            raise TypeError(src)

        pairs: ta.Sequence[ta.Tuple[NodeT, ta.Sequence[NodeT]]]
        pairs = [(check.not_none(n), [check.not_none(c) for c in cs]) for n, cs in pairs]

        children_by_node = col.IdentityKeyDict() if identity else {}
        parents_by_node = col.IdentityKeyDict() if identity else {}
        for n, cs in pairs:
            check.not_in(n, children_by_node)
            children_by_node[n] = cs
            for c in cs:
                check.not_in(c, parents_by_node)
                parents_by_node[c] = n

        if identity:
            e, d = id, col.unique_dict((id(n), n) for n, _ in pairs)
        else:
            e, d = lang.identity, lang.identity
        tsd = {e(n): {e(p)} for n, p in parents_by_node.items()}
        ts = list(col.mut_toposort(tsd))
        root = d(check.single(ts[0]))

        return cls(
            root,
            children_by_node.__getitem__,
            identity=identity,
            **kwargs,
        )

    @classmethod
    def from_nodal(cls, root: NodalT, **kwargs) -> 'BasicTreeAnalysis[NodalT]':
        return cls(root, lambda n: n.children, **kwargs)

    @properties.cached  # noqa
    @property
    def _node_sets_by_type(self) -> ta.MutableMapping[type, ta.AbstractSet[NodeT]]:
        return weakref.WeakKeyDictionary()

    def get_node_type_set(self, ty: ta.Type[T]) -> ta.AbstractSet[T]:
        try:
            return self._node_sets_by_type[ty]
        except KeyError:
            ret = self._node_sets_by_type[ty] = self._set_fac(n for n in self.nodes if isinstance(n, ty))
            return ret

    def iter_ancestors(self, node: NodeT) -> NodeGenerator[NodeT]:
        cur = node
        while True:
            cur = self.parents_by_node.get(cur)
            if cur is None:
                break
            yield cur

    def get_lineage(self, node: NodeT) -> col.IndexedSeq[NodeT]:
        return self._idx_seq_fac(reversed([node, *self.iter_ancestors(node)]))

    def get_first_parent_of_type(self, node: NodeT, ty: ta.Type[T]) -> ta.Optional[NodeT]:
        for cur in self.iter_ancestors(node):
            if isinstance(cur, ty):
                return cur
        return None

    @properties.cached  # noqa
    @property
    def depths_by_node(self) -> ta.Mapping[NodeT, int]:
        def rec(n, d):
            dct[n] = d
            for c in self._children_by_node[n]:
                rec(c, d + 1)
        dct: ta.MutableMapping[NodeT, int] = self._dict_fac()
        rec(self._root, 0)
        return dct
