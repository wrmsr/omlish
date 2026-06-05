import abc
import typing as ta

from ... import dataclasses as dc
from ... import lang


K = ta.TypeVar('K')
V = ta.TypeVar('V')

Comparator: ta.TypeAlias = ta.Callable[[K, K], int]
Node: ta.TypeAlias = ta.Union['_Leaf', '_Branch']


##


MAX_LEAF_LEN = 32
MAX_BRANCH_LEN = 32


class _EMPTY(lang.Marker):  # noqa
    pass


def _default_cmp(a: K, b: K) -> int:
    return (a > b) - (a < b)  # type: ignore[operator]


@dc.dataclass(frozen=True, slots=True)
class _Leaf(ta.Generic[K, V]):
    keys: tuple[K, ...]
    values: tuple[V, ...]
    count: int


@dc.dataclass(frozen=True, slots=True)
class _Branch(ta.Generic[K, V]):
    # Invariants, relied on non-locally:
    #
    #  - len(children) >= 2. Unary branches are always collapsed into their child - by _make_branch, and reimplemented
    #    by the fast path in _branch_delete, which bypasses it. Collapse is also the sole source of mixed-height
    #    siblings (below), and is what keeps height <= log2(n) even in degenerate shapes.
    #
    #  - keys[i] is _node_max(children[i]) - the same *object*, not merely cmp-equal. Every construction path threads
    #    key objects by identity: tuple slices and concats preserve element identity, _leaf_insert reuses l.keys on
    #    value replacement, and _make_branch reads the live objects. This makes the 'is'-based "subtree max unchanged"
    #    checks in _replace_child / _branch_delete exact: same object trivially means same max, and a
    #    stale-but-cmp-equal new max would require two cmp-equal key objects coexisting, which insert-replace semantics
    #    forbid. (A miss would merely fall through to a splice anyway.)
    #
    #  - count == sum(c.count for c in children), exact - safe to drive rank/select.
    #
    #  - children may be of mixed kind and mixed height: deletes' unary collapse can hoist a leaf beside branches. All
    #    consumers must stay isinstance- and cmp-driven; nothing may assume uniform leaf depth or do height arithmetic.
    keys: tuple[K, ...]
    children: tuple[Node, ...]
    count: int


@dc.dataclass(frozen=True, slots=True)
class _Split(ta.Generic[K, V]):
    left: Node
    right: Node


def _node_max(n: Node) -> ta.Any:
    return n.keys[-1]


def _make_leaf(
        keys: tuple[K, ...],
        values: tuple[V, ...],
) -> _Leaf[K, V]:
    return _Leaf(
        keys=keys,
        values=values,
        count=len(keys),
    )


def _make_branch(children: tuple[Node, ...]) -> Node:
    # Unary collapse: maintains the >= 2-children invariant. Anything constructing _Branch directly (the _branch_delete
    # fast path) must reimplement this.
    if len(children) == 1:
        return children[0]

    return _Branch(
        keys=tuple(_node_max(c) for c in children),
        children=children,
        count=sum(c.count for c in children),
    )


def _key_index(
        keys: tuple[K, ...],
        k: K,
        cmp: Comparator[K],
) -> tuple[int, bool]:
    lo = 0
    hi = len(keys)

    while lo < hi:
        mid = (lo + hi) // 2
        c = cmp(keys[mid], k)
        if c < 0:
            lo = mid + 1
        else:
            hi = mid

    return lo, lo < len(keys) and cmp(keys[lo], k) == 0


def _child_index(
        keys: tuple[K, ...],
        k: K,
        cmp: Comparator[K],
) -> int:
    lo = 0
    hi = len(keys)

    while lo < hi:
        mid = (lo + hi) // 2
        if cmp(keys[mid], k) < 0:
            lo = mid + 1
        else:
            hi = mid

    if lo == len(keys):
        return len(keys) - 1

    return lo


def _leaf_insert(
        l: _Leaf[K, V],
        k: K,
        v: V,
        cmp: Comparator[K],
) -> Node | _Split[K, V]:
    idx, found = _key_index(l.keys, k, cmp)

    if found:
        # Value replacement keeps the *old* key object (dict semantics) and reuses l.keys outright. Identity is
        # load-bearing here: unchanged leaf keys means every ancestor's 'is' check sees "max unchanged" and reuses its
        # own keys tuple too, so the whole keys spine is shared across versions.
        keys = l.keys
        values = (*l.values[:idx], v, *l.values[idx + 1:])
    else:
        keys = (*l.keys[:idx], k, *l.keys[idx:])
        values = (*l.values[:idx], v, *l.values[idx:])

    if len(keys) <= MAX_LEAF_LEN:
        return _make_leaf(keys, values)

    mid = len(keys) // 2

    return _Split(
        left=_make_leaf(keys[:mid], values[:mid]),
        right=_make_leaf(keys[mid:], values[mid:]),
    )


def _replace_child(
        b: _Branch[K, V],
        idx: int,
        new: Node,
) -> _Branch[K, V]:
    old = b.children[idx]
    nm = _node_max(new)

    # 'is' is exact, not heuristic - see the key-identity invariant on _Branch. Same object <=> subtree max unchanged
    # <=> b.keys is still correct and can be shared wholesale with the new version.
    return _Branch(
        keys=b.keys if b.keys[idx] is nm else (*b.keys[:idx], nm, *b.keys[idx + 1:]),
        children=(*b.children[:idx], new, *b.children[idx + 1:]),
        count=b.count - old.count + new.count,
    )


def _branch_insert(
        b: _Branch[K, V],
        k: K,
        v: V,
        cmp: Comparator[K],
) -> Node | _Split[K, V]:
    idx = _child_index(b.keys, k, cmp)
    old = b.children[idx]

    res = _insert(old, k, v, cmp)

    if not isinstance(res, _Split):
        return _replace_child(b, idx, res)

    children = (*b.children[:idx], res.left, res.right, *b.children[idx + 1:])

    if len(children) > MAX_BRANCH_LEN:
        mid = len(children) // 2

        return _Split(
            left=_make_branch(children[:mid]),
            right=_make_branch(children[mid:]),
        )

    return _Branch(
        keys=(*b.keys[:idx], _node_max(res.left), _node_max(res.right), *b.keys[idx + 1:]),
        children=children,
        count=b.count - old.count + res.left.count + res.right.count,
    )


def _insert(
        n: Node,
        k: K,
        v: V,
        cmp: Comparator[K],
) -> Node | _Split[K, V]:
    if isinstance(n, _Leaf):
        return _leaf_insert(n, k, v, cmp)

    return _branch_insert(n, k, v, cmp)


def _can_merge(a: Node, b: Node) -> bool:
    if isinstance(a, _Leaf) and isinstance(b, _Leaf):
        return len(a.keys) + len(b.keys) <= MAX_LEAF_LEN

    if isinstance(a, _Branch) and isinstance(b, _Branch):
        return len(a.children) + len(b.children) <= MAX_BRANCH_LEN

    # Mixed leaf/branch siblings exist (see _Branch) and are deliberately unmergeable - consequence: a hoisted leaf has
    # no legal merge partner and may sit at 1 key indefinitely. Adjacent-occupancy arguments hold per-kind only.
    return False


def _merge(a: Node, b: Node) -> Node:
    if isinstance(a, _Leaf) and isinstance(b, _Leaf):
        return _make_leaf(
            a.keys + b.keys,
            a.values + b.values,
        )

    if isinstance(a, _Branch) and isinstance(b, _Branch):
        return _make_branch(a.children + b.children)

    raise TypeError((a, b))


def _compact_children(children: tuple[Node, ...]) -> tuple[Node, ...]:
    # Output length <= input length, with equality iff no merge happened - in which case the output is element-wise
    # identical to the input. _branch_delete's fast-path gate depends on exactly this.
    out: list[Node] = []

    for child in children:
        if out and _can_merge(out[-1], child):
            out[-1] = _merge(out[-1], child)
        else:
            out.append(child)

    return tuple(out)


def _leaf_delete(
        l: _Leaf[K, V],
        k: K,
        cmp: Comparator[K],
) -> Node | type[_EMPTY]:
    idx, found = _key_index(l.keys, k, cmp)

    if not found:
        # No-op by identity. Every level above short-circuits on 'res is old', so by induction 'res is not old' means
        # exactly one key was removed - which is what licenses count=b.count - 1 in _branch_delete (and the 'res is
        # self._root' no-op check in BtreeMap.without).
        return l

    keys = l.keys[:idx] + l.keys[idx + 1:]

    if not keys:
        return _EMPTY

    return _make_leaf(
        keys,
        l.values[:idx] + l.values[idx + 1:],
    )


def _branch_delete(
        b: _Branch[K, V],
        k: K,
        cmp: Comparator[K],
) -> Node | type[_EMPTY]:
    idx = _child_index(b.keys, k, cmp)
    old = b.children[idx]

    res = _delete(old, k, cmp)

    if res is old:
        return b

    if res is _EMPTY:
        children = (*b.children[:idx], *b.children[idx + 1:])

        if not children:
            # Unreachable while the >= 2-children invariant holds (a sibling always survives). Kept as defense against
            # hand-built trees.
            return _EMPTY

    else:
        children = (*b.children[:idx], ta.cast(Node, res), *b.children[idx + 1:])

    compacted = _compact_children(children)

    if len(compacted) != len(children):
        # Compaction only shrinks, so unequal length <=> at least one merge happened; equal length <=> 'compacted' is
        # element-wise identical, which is why the fast path below may keep using 'children'. The sweep is deliberately
        # over *all* children, not just pairs adjacent to idx: inserts never compact and splits leave half-full
        # siblings, so distant mergeable pairs accumulate and this is the only place they're caught.
        return _make_branch(compacted)

    if len(children) == 1:
        # Reimplements _make_branch's unary collapse - mandatory, since the fast path below constructs _Branch directly
        # and would otherwise mint unary branches, breaking the >= 2-children invariant (and with it the height bound).
        return children[0]

    if res is _EMPTY:
        keys = (*b.keys[:idx], *b.keys[idx + 1:])

    else:
        nr = ta.cast(Node, res)
        nm = _node_max(nr)
        # 'res is not old' guarantees exactly one key was removed (the identity chain rooted in _leaf_delete). Holds for
        # the _EMPTY arm too: only a 1-key leaf yields _EMPTY in practice (a branch only via the unreachable path
        # above), so dropping it is also net -1.
        keys = b.keys if b.keys[idx] is nm else (*b.keys[:idx], nm, *b.keys[idx + 1:])

    return _Branch(
        keys=keys,
        children=children,
        count=b.count - 1,
    )


def _delete(
        n: Node,
        k: K,
        cmp: Comparator[K],
) -> Node | type[_EMPTY]:
    if isinstance(n, _Leaf):
        return _leaf_delete(n, k, cmp)

    return _branch_delete(n, k, cmp)


def _find(
        n: Node | None,
        k: K,
        cmp: Comparator[K],
) -> V | type[_EMPTY]:
    while n is not None:
        if isinstance(n, _Leaf):
            idx, found = _key_index(n.keys, k, cmp)
            if found:
                return n.values[idx]
            return _EMPTY

        n = n.children[_child_index(n.keys, k, cmp)]

    return _EMPTY


##


class BaseBtreeMapIterator(lang.Abstract, ta.Iterator[tuple[K, V]], ta.Generic[K, V]):
    __slots__ = ('_st', '_leaf', '_idx')

    def __init__(
            self,
            *,
            _st: list[tuple[_Branch[K, V], int]],
            _leaf: _Leaf[K, V] | None,
            _idx: int,
    ) -> None:
        super().__init__()

        self._st = _st
        self._leaf = _leaf
        self._idx = _idx

    def __iter__(self) -> ta.Self:
        return self

    def __next__(self) -> tuple[K, V]:
        return self.next()

    def has_next(self) -> bool:
        return self._leaf is not None

    @abc.abstractmethod
    def next(self) -> tuple[K, V]:
        raise NotImplementedError


@ta.final
class BtreeMapIterator(BaseBtreeMapIterator[K, V]):
    __slots__ = ()

    @classmethod
    def first(cls, root: Node | None) -> ta.Self:
        st: list[tuple[_Branch[K, V], int]] = []
        n = root

        if n is None:
            return cls(_st=st, _leaf=None, _idx=0)

        while isinstance(n, _Branch):
            st.append((n, 0))
            n = n.children[0]

        return cls(
            _st=st,
            _leaf=n,
            _idx=0,
        )

    @classmethod
    def from_key(
            cls,
            root: Node | None,
            k: K,
            cmp: Comparator[K],
    ) -> ta.Self:
        st: list[tuple[_Branch[K, V], int]] = []
        n = root

        if n is None or cmp(k, _node_max(n)) > 0:
            # The k > tree-max early-out is load-bearing: it establishes the descent invariant k <= subtree max (so
            # _child_index's end-clamp never engages), which is what guarantees _key_index below yields idx <
            # len(leaf.keys).
            return cls(_st=st, _leaf=None, _idx=0)

        while isinstance(n, _Branch):
            idx = _child_index(n.keys, k, cmp)
            st.append((n, idx))
            n = n.children[idx]

        leaf = n
        idx, _ = _key_index(leaf.keys, k, cmp)

        return cls(
            _st=st,
            _leaf=leaf,
            _idx=idx,
        )

    def _advance_leaf(self) -> None:
        while self._st:
            b, idx = self._st.pop()
            idx += 1

            if idx < len(b.children):
                n = b.children[idx]
                self._st.append((b, idx))

                while isinstance(n, _Branch):
                    self._st.append((n, 0))
                    n = n.children[0]

                self._leaf = n
                self._idx = 0
                return

        self._leaf = None
        self._idx = 0

    def next(self) -> tuple[K, V]:
        leaf = self._leaf

        if leaf is None:
            raise StopIteration

        ret = (leaf.keys[self._idx], leaf.values[self._idx])

        self._idx += 1

        if self._idx >= len(leaf.keys):
            self._advance_leaf()

        return ret


@ta.final
class BtreeMapReverseIterator(BaseBtreeMapIterator[K, V]):
    __slots__ = ()

    @classmethod
    def last(cls, root: Node | None) -> ta.Self:
        st: list[tuple[_Branch[K, V], int]] = []
        n = root

        if n is None:
            return cls(_st=st, _leaf=None, _idx=-1)

        while isinstance(n, _Branch):
            idx = len(n.children) - 1
            st.append((n, idx))
            n = n.children[idx]

        leaf = n

        return cls(
            _st=st,
            _leaf=leaf,
            _idx=len(leaf.keys) - 1,
        )

    @classmethod
    def from_key(
            cls,
            root: Node | None,
            k: K,
            cmp: Comparator[K],
    ) -> ta.Self:
        st: list[tuple[_Branch[K, V], int]] = []
        n = root

        if n is None:
            return cls(_st=st, _leaf=None, _idx=-1)

        while isinstance(n, _Branch):
            idx = _child_index(n.keys, k, cmp)
            st.append((n, idx))
            n = n.children[idx]

        leaf = n
        idx, found = _key_index(leaf.keys, k, cmp)

        if not found:
            # Greatest key < k within this leaf. k > tree max needs no special case: _child_index clamps onto the
            # rightmost spine and this lands on the global max. idx may reach -1 when k precedes the whole leaf (k falls
            # between leaves, or k < tree min) - the predecessor then lives in the previous leaf, found by _retreat_leaf
            # below (or exhausted to empty).
            idx -= 1

        ret = cls(
            _st=st,
            _leaf=leaf,
            _idx=idx,
        )

        if idx < 0:
            ret._retreat_leaf()  # noqa

        return ret

    def _retreat_leaf(self) -> None:
        while self._st:
            b, idx = self._st.pop()
            idx -= 1

            if idx >= 0:
                n = b.children[idx]
                self._st.append((b, idx))

                while isinstance(n, _Branch):
                    ci = len(n.children) - 1
                    self._st.append((n, ci))
                    n = n.children[ci]

                self._leaf = ta.cast('_Leaf[K, V]', n)
                self._idx = len(self._leaf.keys) - 1
                return

        self._leaf = None
        self._idx = -1

    def next(self) -> tuple[K, V]:
        leaf = self._leaf

        if leaf is None:
            raise StopIteration

        ret = (leaf.keys[self._idx], leaf.values[self._idx])

        self._idx -= 1

        if self._idx < 0:
            self._retreat_leaf()

        return ret


##


def new(k: K, v: V) -> Node:
    return _make_leaf((k,), (v,))


def find(
        root: Node | None,
        k: K,
        cmp: Comparator[K] | None,
) -> V:
    v = _find(root, k, cmp if cmp is not None else _default_cmp)

    if v is _EMPTY:
        raise KeyError(k)

    return ta.cast(V, v)


def insert(
        root: Node | None,
        k: K,
        v: V,
        cmp: Comparator[K] | None,
) -> Node:
    cmp = cmp if cmp is not None else _default_cmp

    if root is None:
        return _make_leaf((k,), (v,))

    res = _insert(root, k, v, cmp)

    if isinstance(res, _Split):
        return _make_branch((res.left, res.right))

    return res


def delete(
        root: Node | None,
        k: K,
        cmp: Comparator[K] | None,
) -> Node | None:
    cmp = cmp if cmp is not None else _default_cmp

    if root is None:
        return None

    res = _delete(root, k, cmp)

    if res is root:
        return root

    if res is _EMPTY:
        return None

    return ta.cast(Node, res)


def len_(root: Node | None) -> int:  # noqa
    return root.count if root is not None else 0


def iter(root: Node | None) -> BtreeMapIterator[K, V]:  # noqa
    return BtreeMapIterator.first(root)


def riter(root: Node | None) -> BtreeMapReverseIterator[K, V]:
    return BtreeMapReverseIterator.last(root)


def iter_from(
        root: Node | None,
        k: K,
        cmp: Comparator[K] | None,
) -> BtreeMapIterator[K, V]:
    return BtreeMapIterator.from_key(root, k, cmp if cmp is not None else _default_cmp)


def riter_from(
        root: Node | None,
        k: K,
        cmp: Comparator[K] | None,
) -> BtreeMapReverseIterator[K, V]:
    return BtreeMapReverseIterator.from_key(root, k, cmp if cmp is not None else _default_cmp)
