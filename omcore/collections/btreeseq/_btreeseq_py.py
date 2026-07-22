import bisect
import itertools
import typing as ta

from ... import dataclasses as dc
from ... import lang


T = ta.TypeVar('T')

Node: ta.TypeAlias = ta.Union['_Leaf[T]', '_Branch[T]']


##


MAX_LEAF_LEN = 32
MAX_BRANCH_LEN = 32


class _MISSING(lang.Marker):  # noqa
    pass


@dc.dataclass(frozen=True, slots=True)
class _Leaf(ta.Generic[T]):
    items: tuple[T, ...]
    count: int
    height: int = 0


@dc.dataclass(frozen=True, slots=True)
class _Branch(ta.Generic[T]):
    children: tuple[Node[T], ...]
    # Cumulative child counts: offsets[i] is the total count of children[:i + 1], so offsets[-1] == count and child i
    # spans positions [offsets[i - 1], offsets[i]) with an implicit leading 0. Cumulative (rather than per-child) so
    # descents bisect instead of scanning.
    offsets: tuple[int, ...]
    count: int
    height: int


def _make_leaf(items: tuple[T, ...]) -> Node[T] | None:
    if not items:
        return None

    return _Leaf(
        items=items,
        count=len(items),
    )


def _make_branch_raw(children: tuple[Node[T], ...]) -> Node[T] | None:
    if not children:
        return None

    if len(children) == 1:
        return children[0]

    offsets = tuple(itertools.accumulate(c.count for c in children))

    return _Branch(
        children=children,
        offsets=offsets,
        count=offsets[-1],
        height=1 + max(c.height for c in children),
    )


def _can_merge(a: Node[T], b: Node[T]) -> bool:
    if isinstance(a, _Leaf) and isinstance(b, _Leaf):
        return len(a.items) + len(b.items) <= MAX_LEAF_LEN

    if isinstance(a, _Branch) and isinstance(b, _Branch):
        return len(a.children) + len(b.children) <= MAX_BRANCH_LEN

    return False


def _merge(a: Node[T], b: Node[T]) -> Node[T]:
    if isinstance(a, _Leaf) and isinstance(b, _Leaf):
        return ta.cast('Node[T]', _make_leaf(a.items + b.items))

    if isinstance(a, _Branch) and isinstance(b, _Branch):
        return ta.cast('Node[T]', _make_branch_raw(a.children + b.children))

    raise TypeError((a, b))


def _compact_children(children: tuple[Node[T], ...]) -> tuple[Node[T], ...]:
    out: list[Node[T]] = []

    for child in children:
        if out and _can_merge(out[-1], child):
            out[-1] = _merge(out[-1], child)
        else:
            out.append(child)

    return tuple(out)


def _pack_children(children: tuple[Node[T], ...]) -> Node[T] | None:
    children = _compact_children(tuple(c for c in children if c.count))

    if not children:
        return None

    if len(children) <= MAX_BRANCH_LEN:
        return _make_branch_raw(children)

    groups = tuple(
        ta.cast('Node[T]', _make_branch_raw(children[i:i + MAX_BRANCH_LEN]))
        for i in range(0, len(children), MAX_BRANCH_LEN)
    )

    return _pack_children(groups)


def _concat(a: Node[T] | None, b: Node[T] | None) -> Node[T] | None:
    # Height-guided, rope-style: descend the taller side's spine until heights match, merge there, and repack on the
    # way back up. Merging at matched height means leaves meet leaves and branches meet branches, so splice boundaries
    # stay mergeable -- the old single-level flatten could hoist a leaf among branch siblings, where same-type-only
    # _can_merge stranded it at minimal occupancy forever. Sibling heights may still differ (packing is relaxed, not
    # RRB-strict); everything downstream is count- and isinstance-driven, so that's fine. Relies on: height == 0 <=>
    # leaf, since unary collapse keeps every branch at height >= 1 with >= 2 children. This is also the lone consumer
    # of the stored height field.
    #
    # On the unequal-height paths, the recursive result is bounded by max(child height, other height) + 1 <= the
    # taller side's own height. When it *reaches* that bound (a merge one level down overflowed and packed into a
    # fresh parent), its children are spliced in as siblings -- b+tree split propagation. Keeping it as an opaque
    # child instead would nest one level per overflow, degenerating a spine of repeated appends into a linked list of
    # packed pairs.
    if a is None:
        return b

    if b is None:
        return a

    if a.height == b.height:
        if isinstance(a, _Leaf):
            bl = ta.cast('_Leaf[T]', b)

            if len(a.items) + len(bl.items) <= MAX_LEAF_LEN:
                return _make_leaf(a.items + bl.items)

            return _pack_children((a, bl))

        bb = ta.cast('_Branch[T]', b)

        return _pack_children(a.children + bb.children)

    if a.height > b.height:
        ab = ta.cast('_Branch[T]', a)

        sub = ta.cast('Node[T]', _concat(ab.children[-1], b))

        if sub.height == ab.height:
            return _pack_children((*ab.children[:-1], *ta.cast('_Branch[T]', sub).children))

        return _pack_children((*ab.children[:-1], sub))

    bb = ta.cast('_Branch[T]', b)

    sub = ta.cast('Node[T]', _concat(a, bb.children[0]))

    if sub.height == bb.height:
        return _pack_children((*ta.cast('_Branch[T]', sub).children, *bb.children[1:]))

    return _pack_children((sub, *bb.children[1:]))


def _find_child(n: _Branch[T], idx: int) -> tuple[int, int]:
    # First child whose end offset exceeds idx. An out-of-range idx lands on len(children) and the caller's child
    # access raises -- per the backend contract, the wrapper owns validation.
    i = bisect.bisect_right(n.offsets, idx)

    return i, idx - (n.offsets[i - 1] if i else 0)


def _get(n: Node[T], idx: int) -> T:
    while isinstance(n, _Branch):
        child_idx, idx = _find_child(n, idx)
        n = n.children[child_idx]

    return n.items[idx]


def _iter_items(n: Node[T] | None) -> ta.Iterator[T]:
    if n is None:
        return

    st: list[Node[T]] = [n]

    while st:
        m = st.pop()

        if isinstance(m, _Leaf):
            yield from m.items
        else:
            st.extend(reversed(m.children))


def _iter_items_desc(n: Node[T] | None) -> ta.Iterator[T]:
    if n is None:
        return

    st: list[Node[T]] = [n]

    while st:
        m = st.pop()

        if isinstance(m, _Leaf):
            yield from reversed(m.items)
        else:
            st.extend(m.children)


def _iter_items_from(n: Node[T] | None, idx: int) -> ta.Iterator[T]:
    if n is None or idx >= n.count:
        return

    if idx <= 0:
        yield from _iter_items(n)
        return

    # Descend to the leaf containing idx, stacking the right siblings passed at each level. Deeper siblings are pushed
    # later and so pop first, which is exactly sequence order.
    st: list[Node[T]] = []

    while isinstance(n, _Branch):
        ci, idx = _find_child(n, idx)

        if ci + 1 < len(n.children):
            st.extend(reversed(n.children[ci + 1:]))

        n = n.children[ci]

    yield from n.items[idx:]

    while st:
        m = st.pop()

        if isinstance(m, _Leaf):
            yield from m.items
        else:
            st.extend(reversed(m.children))


def _take(n: Node[T] | None, idx: int) -> Node[T] | None:
    # Prefix [:idx]. With _drop, replaces a two-sided split: only the kept side is ever constructed, so a splice needs
    # no intermediate 'rest' tree and never packs a discarded segment.
    if n is None or idx >= n.count:
        return n

    if idx <= 0:
        return None

    if isinstance(n, _Leaf):
        return _make_leaf(n.items[:idx])

    ci = bisect.bisect_left(n.offsets, idx)
    base = n.offsets[ci - 1] if ci else 0

    # 0 < idx - base <= children[ci].count here, so the recursion yields a node -- possibly children[ci] itself,
    # shared whole, when idx lands exactly on its end.
    sub = ta.cast('Node[T]', _take(n.children[ci], idx - base))

    return _pack_children((*n.children[:ci], sub))


def _drop(n: Node[T] | None, idx: int) -> Node[T] | None:
    # Suffix [idx:].
    if n is None or idx <= 0:
        return n

    if idx >= n.count:
        return None

    if isinstance(n, _Leaf):
        return _make_leaf(n.items[idx:])

    ci = bisect.bisect_right(n.offsets, idx)
    base = n.offsets[ci - 1] if ci else 0

    # 0 <= idx - base < children[ci].count here, so the recursion yields a node -- possibly children[ci] itself,
    # shared whole, when idx lands exactly on its start.
    sub = ta.cast('Node[T]', _drop(n.children[ci], idx - base))

    return _pack_children((sub, *n.children[ci + 1:]))


def _slice(n: Node[T] | None, start: int, stop: int) -> Node[T] | None:
    if n is None or start >= stop:
        return None

    return _take(_drop(n, start), stop - start)


def _replace_same(
        n: Node[T],
        start: int,
        items: tuple[T, ...],
        off: int = 0,
        lim: int | None = None,
) -> Node[T]:
    # Same-length replacement of positions [start, start + (lim - off)) with items[off:lim]. Threads (off, lim)
    # instead of slicing `items` per level -- the old form partitioned the full replacement at every depth, costing
    # O(k * log n) tuple copying; this is O(k + B * log n), with the only item copies at the leaves.
    if lim is None:
        lim = len(items)

    if off >= lim:
        return n

    if isinstance(n, _Leaf):
        stop = start + (lim - off)

        for i in range(off, lim):
            if n.items[start - off + i] is not items[i]:
                break
        else:
            # Identity no-op, mirroring btreemap's identical-value reinsert: the branch level below short-circuits on
            # 'sub is child', so replacing a run with the very same objects reuses the whole tree (and the wrapper's
            # 'root is self._root' check then returns self).
            return n

        return ta.cast('Node[T]', _make_leaf(n.items[:start] + items[off:lim] + n.items[stop:]))

    end = start + (lim - off)
    ci = bisect.bisect_right(n.offsets, start)
    children = list(n.children)
    base = n.offsets[ci - 1] if ci else 0
    item_off = off
    changed = False

    for i in range(ci, len(n.children)):
        if base >= end:
            break

        child = n.children[i]
        nxt = n.offsets[i]

        child_start = max(start, base) - base
        child_stop = min(end, nxt) - base
        item_lim = item_off + (child_stop - child_start)

        sub = _replace_same(child, child_start, items, item_off, item_lim)

        if sub is not child:
            children[i] = sub
            changed = True

        item_off = item_lim
        base = nxt

    if not changed:
        return n

    # Shape-preserving by induction (leaves replace equal-length runs, so every child's count is unchanged), which
    # makes offsets/count/height all reusable as-is -- sharing the offsets tuple across versions. len(children) ==
    # len(n.children) >= 2, so _make_branch_raw's unary collapse cannot apply and bypassing it is safe.
    return _Branch(
        children=tuple(children),
        offsets=n.offsets,
        count=n.count,
        height=n.height,
    )


def _append_small(n: Node[T], items: tuple[T, ...]) -> Node[T] | None:
    # Right-spine append fast path: when the run fits in the rightmost leaf, rebuild just the spine -- no
    # _pack_children sweeps, no recomputation beyond the final offset. Returns None when the run doesn't fit, leaving
    # the general splice path (whose _concat compacts and splits as needed) to handle it -- that happens at most once
    # per MAX_LEAF_LEN single-item appends, keeping the amortized cost low.
    if isinstance(n, _Leaf):
        if len(n.items) + len(items) > MAX_LEAF_LEN:
            return None

        return _make_leaf(n.items + items)

    res = _append_small(n.children[-1], items)

    if res is None:
        return None

    # res has the same height as the child it replaces (by induction: leaves stay leaves, branches reuse their
    # height), so height, sibling structure, and every non-final offset carry over unchanged.
    return _Branch(
        children=(*n.children[:-1], res),
        offsets=(*n.offsets[:-1], n.count + len(items)),
        count=n.count + len(items),
        height=n.height,
    )


def _splice(
        n: Node[T] | None,
        start: int,
        stop: int,
        items: tuple[T, ...],
) -> Node[T] | None:
    remove_len = stop - start

    if n is None:
        return from_iterable(items)

    if remove_len == len(items):
        if remove_len == 0:
            return n

        return _replace_same(n, start, items)

    if start == stop == n.count and (res := _append_small(n, items)) is not None:
        return res

    left = _take(n, start)
    right = _drop(n, stop)
    mid = from_iterable(items)

    return _concat(_concat(left, mid), right)


##


class BtreeSeqIterator(ta.Iterator[T], ta.Generic[T]):
    __slots__ = ('_it', '_next')

    def __init__(self, it: ta.Iterator[T]) -> None:
        super().__init__()

        self._it = it
        self._next: ta.Any = _MISSING

    def __iter__(self) -> ta.Self:
        return self

    def __next__(self) -> T:
        if (nxt := self._next) is not _MISSING:
            self._next = _MISSING
            return nxt

        return next(self._it)

    next = __next__

    def has_next(self) -> bool:
        if self._next is not _MISSING:
            return True

        try:
            self._next = next(self._it)
        except StopIteration:
            return False

        return True


##
#
# Public backend surface. Indices are assumed pre-normalized by the wrapper: 0 <= idx < count for get, and
# 0 <= start <= stop <= count for slice/splice/iter_from. Violations are not reliably detected here -- e.g. a negative
# get() on a leaf root wraps python-style, and on a deeper tree returns an unrelated element -- the wrapper owns
# validation, and the C++ backend mirrors this contract rather than adding checks.


def iter(root: Node[T] | None) -> BtreeSeqIterator[T]:  # noqa
    return BtreeSeqIterator(_iter_items(root))


def riter(root: Node[T] | None) -> BtreeSeqIterator[T]:
    return BtreeSeqIterator(_iter_items_desc(root))


def iter_from(root: Node[T] | None, idx: int) -> BtreeSeqIterator[T]:
    return BtreeSeqIterator(_iter_items_from(root, idx))


def from_iterable(items: ta.Iterable[T]) -> Node[T] | None:
    leaves: list[Node[T]] = []
    cur: list[T] = []

    for item in items:
        cur.append(item)

        if len(cur) >= MAX_LEAF_LEN:
            leaves.append(ta.cast('Node[T]', _make_leaf(tuple(cur))))
            cur.clear()

    if cur:
        leaves.append(ta.cast('Node[T]', _make_leaf(tuple(cur))))

    return _pack_children(tuple(leaves))


def len_(root: Node[T] | None) -> int:
    return root.count if root is not None else 0


def get(root: Node[T] | None, idx: int) -> T:
    if root is None:
        raise IndexError(idx)

    return _get(root, idx)


def slice(root: Node[T] | None, start: int, stop: int):  # noqa
    return _slice(root, start, stop)


def splice(
        root: Node[T] | None,
        start: int,
        stop: int,
        items: ta.Iterable[T],
):
    return _splice(root, start, stop, tuple(items))
