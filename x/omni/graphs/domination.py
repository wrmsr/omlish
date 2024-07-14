import abc
import typing as ta

from .. import check
from .. import lang
from .. import properties


lang.warn_unstable()


V = ta.TypeVar('V')
E = ta.TypeVar('E')
MK = ta.TypeVar('MK')
MV = ta.TypeVar('MV')
SetMap = ta.Mapping[MK, ta.AbstractSet[MV]]


class DirectedGraph(ta.Generic[V, E], lang.Abstract):

    @abc.abstractmethod
    def get_successors(self, vertex: V) -> ta.Collection[V]:
        raise NotImplementedError

    @abc.abstractmethod
    def yield_depth_first(self, root: V) -> ta.Iterator[V]:
        raise NotImplementedError


class ListDictDirectedGraph(DirectedGraph[V, E]):

    def __init__(self, items: ta.Iterable[ta.Tuple[V, ta.Iterable[V]]]) -> None:
        super().__init__()

        lst_dct: ta.Dict[V, ta.List[V]] = {}
        all_children = set()
        for parent, children in items:
            check.not_in(parent, lst_dct)
            lst = []
            seen = set()
            for child in children:
                if child not in seen:
                    seen.add(child)
                    lst.append(child)
                    all_children.add(child)
            lst_dct[parent] = lst
        check.empty(all_children - set(lst_dct))
        self._lst_dct = lst_dct

    def get_successors(self, vertex: V) -> ta.Collection[V]:
        return self._lst_dct[vertex]

    def yield_depth_first(self, root: V) -> ta.Iterator[V]:
        stack: ta.List[V] = [root]
        seen: ta.Set[V] = set()
        while stack:
            cur = stack.pop()
            yield cur
            for child in self._lst_dct[cur]:
                if child not in seen:
                    seen.add(child)
                    stack.append(child)


class DominatorTree(ta.Generic[V, E]):

    def __init__(self, graph: DirectedGraph[V, E], root: V) -> None:
        super().__init__()

        self._graph = check.not_none(graph)
        self._root = check.not_none(root)
        check.not_none(self._graph.get_successors(root))
        self._dfs = _Dfs(graph, root)

    @properties.cached
    def immediate_dominators(self) -> ta.Mapping[V, V]:
        return _ImmediateDominanceComputer(self._dfs).immediate_dominators

    @properties.cached
    def dominator_tree(self) -> SetMap[V, V]:
        tree: ta.Dict[V, ta.Set[V]] = {}
        for node, dom in self.immediate_dominators.items():
            tree.setdefault(dom, set()).add(node)
        return tree

    @properties.cached
    def deep_dominated(self) -> SetMap[V, V]:
        seen: ta.Set[V] = set()
        ret: ta.Dict[V, ta.Set[V]] = {}

        def rec(node: V) -> ta.Collection[V]:
            check.not_in(node, seen)
            seen.add(node)
            # FIXME: pyrsistent
            st = set()
            for child in self.dominator_tree.get(node, []):
                st.add(child)
                st.update(rec(child))
            if st:
                ret[node] = st
            return st

        rec(self._root)
        return ret

    @properties.cached
    def dominance_frontiers(self) -> SetMap[V, V]:
        dominance_frontiers: ta.Dict[V, ta.Set[V]] = {}

        for x in self.reverse_topological_traversal:
            dfx = dominance_frontiers.setdefault(x, set())

            for y in self._graph.get_successors(x):
                if self.immediate_dominators[y] != x:
                    dfx.add(y)

            for z in self.dominator_tree.get(x, []):
                for y in dominance_frontiers.get(z, []):
                    if self.immediate_dominators[y] != x:
                        dfx.add(y)

        return {k: v for k, v in dominance_frontiers.items() if v}

    @properties.cached
    def topological_traversal(self) -> ta.List[V]:
        # FIXME: LinkedList
        lst: ta.List[V] = []

        for node in self._dfs.vertex:
            try:
                idx = lst.index(self.immediate_dominators[node])
            except (KeyError, ValueError):
                lst.append(node)
            else:
                lst.insert(idx + 1, node)

        return lst

    @properties.cached
    def reverse_topological_traversal(self) -> ta.List[V]:
        return list(reversed(self.topological_traversal))


class _Dfs(ta.Generic[V, E]):

    def __init__(self, graph: DirectedGraph[V, E], root: V) -> None:
        super().__init__()

        semi: ta.Dict[V, int] = {}
        vertex: ta.List[V] = []
        parent: ta.Dict[V, V] = {}
        pred: ta.Dict[V, ta.Set[V]] = {}
        label: ta.Dict[V, V] = {}

        for node in graph.yield_depth_first(root):
            if node not in semi:
                vertex.append(node)

                check.not_in(node, semi)
                semi[node] = len(semi)
                check.not_in(node, label)
                label[node] = node

                for child in graph.get_successors(node):
                    pred.setdefault(child, set()).add(node)
                    if child not in semi:
                        check.not_in(child, parent)
                        parent[child] = node

        self._semi = semi
        self._vertex = vertex
        self._parent = parent
        self._pred = pred
        self._label = label

    @property
    def semi(self) -> ta.Dict[V, int]:
        return self._semi

    @property
    def vertex(self) -> ta.List[V]:
        return self._vertex

    @property
    def parent(self) -> ta.Dict[V, V]:
        return self._parent

    @property
    def pred(self) -> ta.Dict[V, ta.Set[V]]:
        return self._pred

    @property
    def label(self) -> ta.Dict[V, V]:
        return self._label


class _ImmediateDominanceComputer(ta.Generic[V, E]):

    def __init__(self, dfs: _Dfs[V, E]) -> None:
        super().__init__()

        self._dfs = check.isinstance(dfs, _Dfs)

        self._ancestor: ta.Dict[V, V] = {}
        self._semi = dict(self._dfs.semi)
        self._label = dict(self._dfs.label)

    @properties.cached
    def immediate_dominators(self) -> ta.Mapping[V, V]:
        idom: ta.Dict[V, V] = {}
        bucket: ta.Dict[V, ta.Set[V]] = {}

        last_semi_number = len(self._semi) - 1

        for i in range(last_semi_number, 0, -1):
            w = self._dfs.vertex[i]
            p = self._dfs.parent[w]

            semidominator = self._semi[w]
            for v in self._dfs.pred.get(w, []):
                semidominator = min(semidominator, self._semi[self._eval(v)])

            self._semi[w] = semidominator
            bucket.setdefault(self._dfs.vertex[semidominator], set()).add(w)

            self._ancestor[w] = p

            for v in bucket.get(p, []):
                u = self._eval(v)

                if self._semi[u] < self._semi[v]:
                    idom[v] = u
                else:
                    idom[v] = p

            try:
                del bucket[p]
            except KeyError:
                pass

        for i in range(1, last_semi_number + 1):
            w = self._dfs.vertex[i]

            if idom[w] != self._dfs.vertex[self._semi[w]]:
                idom[w] = idom[idom[w]]

        return idom

    def _eval(self, v: V) -> V:
        self._compress(v)
        return self._label[v]

    def _compress(self, v: V) -> None:
        worklist: ta.List[V] = [v]

        a = self._ancestor.get(v)

        while a in self._ancestor:
            worklist.append(a)
            a = self._ancestor[a]

        ancestor = worklist.pop()
        least_semi = self._semi[self._label[ancestor]]

        while worklist:
            descendent = worklist.pop()
            current_semi = self._semi[self._label[descendent]]

            if current_semi > least_semi:
                self._label[descendent] = self._label[ancestor]
            else:
                least_semi = current_semi

            ancestor = descendent
