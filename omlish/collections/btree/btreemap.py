"""Persistent counted B+-ish search tree with dense leaves and opportunistic compaction."""
import abc
import typing as ta

from ... import dataclasses as dc
from ... import lang
from ..intersections import PersistentSortedMapping
from ..mappings import IterItemsViewMapping
from ..mappings import IterValuesViewMapping
from ..mappings import iteritems_itervalues
from ..mappings import map_contains


K = ta.TypeVar('K')
V = ta.TypeVar('V')

Comparator: ta.TypeAlias = ta.Callable[[K, K], int]
Node: ta.TypeAlias = ta.Union['_Leaf', '_Branch']


##


_MAX_LEAF_LEN = 32
_MAX_BRANCH_LEN = 32


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
        keys = l.keys
        values = (*l.values[:idx], v, *l.values[idx + 1:])
    else:
        keys = (*l.keys[:idx], k, *l.keys[idx:])
        values = (*l.values[:idx], v, *l.values[idx:])

    if len(keys) <= _MAX_LEAF_LEN:
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

    if len(children) > _MAX_BRANCH_LEN:
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
        return len(a.keys) + len(b.keys) <= _MAX_LEAF_LEN

    if isinstance(a, _Branch) and isinstance(b, _Branch):
        return len(a.children) + len(b.children) <= _MAX_BRANCH_LEN

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
            return _EMPTY

    else:
        children = (*b.children[:idx], ta.cast(Node, res), *b.children[idx + 1:])

    compacted = _compact_children(children)

    if len(compacted) != len(children):
        return _make_branch(compacted)

    if len(children) == 1:
        return children[0]

    if res is _EMPTY:
        keys = (*b.keys[:idx], *b.keys[idx + 1:])

    else:
        nr = ta.cast(Node, res)
        nm = _node_max(nr)
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


@ta.final
class BtreeMap(
    IterValuesViewMapping[K, V],
    IterItemsViewMapping[K, V],
    PersistentSortedMapping[K, V],
    ta.Mapping[K, V],
    ta.Generic[K, V],
):
    __slots__ = ('_root', '_cmp')

    def __init__(
            self,
            *,
            _root: Node | None,
            _cmp: Comparator[K],
    ) -> None:
        super().__init__()

        self._root = _root
        self._cmp = _cmp

    @property
    def debug(self) -> ta.Mapping[K, V]:
        return dict(self)

    def __len__(self) -> int:
        return self._root.count if self._root is not None else 0

    def __getitem__(self, item: K) -> V:
        v = _find(self._root, item, self._cmp)

        if v is _EMPTY:
            raise KeyError(item)

        return v  # type: ignore[return-value]

    def __iter__(self) -> ta.Iterator[K]:
        i = self.iteritems()

        while i.has_next():
            yield i.next()[0]

    __contains__ = map_contains

    itervalues = iteritems_itervalues

    def iteritems(self) -> BtreeMapIterator[K, V]:
        return BtreeMapIterator.first(self._root)

    def items_desc(self) -> BtreeMapReverseIterator[K, V]:
        return BtreeMapReverseIterator.last(self._root)

    def items_from(self, k: K) -> BtreeMapIterator[K, V]:
        return BtreeMapIterator.from_key(self._root, k, self._cmp)

    def items_from_desc(self, k: K) -> BtreeMapReverseIterator[K, V]:
        return BtreeMapReverseIterator.from_key(self._root, k, self._cmp)

    def with_(self, k: K, v: V) -> BtreeMap[K, V]:
        if self._root is None:
            return BtreeMap(
                _root=_make_leaf((k,), (v,)),
                _cmp=self._cmp,
            )

        res = _insert(self._root, k, v, self._cmp)

        if isinstance(res, _Split):
            root = _make_branch((res.left, res.right))
        else:
            root = res

        return BtreeMap(
            _root=root,
            _cmp=self._cmp,
        )

    def without(self, k: K) -> BtreeMap[K, V]:
        if self._root is None:
            return self

        res = _delete(self._root, k, self._cmp)

        if res is self._root:
            return self

        return BtreeMap(
            _root=None if res is _EMPTY else ta.cast(Node, res),
            _cmp=self._cmp,
        )

    def default(self, k: K, v: V) -> BtreeMap[K, V]:
        try:
            self[k]  # noqa
        except KeyError:
            return self.with_(k, v)
        else:
            return self


def new_btree_map(
        items: ta.Iterable[tuple[K, V]] | None = None,
        *,
        cmp: ta.Callable[[K, K], int] | None = None,
) -> BtreeMap[K, V]:
    m: BtreeMap[K, V] = BtreeMap(
        _root=None,
        _cmp=cmp if cmp is not None else _default_cmp,
    )

    if items is not None:
        for k, v in items:
            m = m.with_(k, v)

    return m


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
