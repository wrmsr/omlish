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
    counts: tuple[int, ...]
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

    return _Branch(
        children=children,
        counts=tuple(c.count for c in children),
        count=sum(c.count for c in children),
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

        return _pack_children((*ab.children[:-1], ta.cast('Node[T]', _concat(ab.children[-1], b))))

    bb = ta.cast('_Branch[T]', b)

    return _pack_children((ta.cast('Node[T]', _concat(a, bb.children[0])), *bb.children[1:]))


def _find_child(n: _Branch[T], idx: int) -> tuple[int, int]:
    base = 0

    for i, count in enumerate(n.counts):
        nxt = base + count

        if idx < nxt:
            return i, idx - base

        base = nxt

    raise IndexError(idx)


def _get(n: Node[T], idx: int) -> T:
    while isinstance(n, _Branch):
        child_idx, idx = _find_child(n, idx)
        n = n.children[child_idx]

    return n.items[idx]


def _iter_items(n: Node[T] | None) -> ta.Iterator[T]:
    if n is None:
        return

    if isinstance(n, _Leaf):
        yield from n.items
        return

    for child in n.children:
        yield from _iter_items(child)


def _iter_items_desc(n: Node[T] | None) -> ta.Iterator[T]:
    if n is None:
        return

    if isinstance(n, _Leaf):
        yield from reversed(n.items)
        return

    for child in reversed(n.children):
        yield from _iter_items_desc(child)


def _iter_items_from(n: Node[T] | None, idx: int) -> ta.Iterator[T]:
    if n is None or idx >= n.count:
        return

    if idx <= 0:
        yield from _iter_items(n)
        return

    if isinstance(n, _Leaf):
        yield from n.items[idx:]
        return

    base = 0
    started = False

    for child in n.children:
        if started:
            yield from _iter_items(child)
        else:
            nxt = base + child.count

            if idx < nxt:
                yield from _iter_items_from(child, idx - base)
                started = True

            base = nxt


def _split(n: Node[T] | None, idx: int) -> tuple[Node[T] | None, Node[T] | None]:
    if n is None:
        return None, None

    if idx <= 0:
        return None, n

    if idx >= n.count:
        return n, None

    if isinstance(n, _Leaf):
        return (
            _make_leaf(n.items[:idx]),
            _make_leaf(n.items[idx:]),
        )

    left_children: list[Node[T]] = []
    right_children: list[Node[T]] = []

    base = 0
    done = False

    for child in n.children:
        nxt = base + child.count

        if done:
            right_children.append(child)

        elif idx <= base:
            right_children.append(child)

        elif idx >= nxt:
            left_children.append(child)

        else:
            left, right = _split(child, idx - base)

            if left is not None:
                left_children.append(left)

            if right is not None:
                right_children.append(right)

            done = True

        base = nxt

    return (
        _pack_children(tuple(left_children)),
        _pack_children(tuple(right_children)),
    )


def _slice(n: Node[T] | None, start: int, stop: int) -> Node[T] | None:
    if n is None or start == stop:
        return None

    _, rest = _split(n, start)
    mid, _ = _split(rest, stop - start)

    return mid


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

        return ta.cast('Node[T]', _make_leaf(n.items[:start] + items[off:lim] + n.items[stop:]))

    children = list(n.children)
    end = start + (lim - off)
    base = 0
    item_off = off

    for i, child in enumerate(n.children):
        nxt = base + child.count

        if nxt <= start:
            base = nxt
            continue

        if base >= end:
            break

        child_start = max(start, base) - base
        child_stop = min(end, nxt) - base
        item_lim = item_off + (child_stop - child_start)

        children[i] = _replace_same(child, child_start, items, item_off, item_lim)

        item_off = item_lim
        base = nxt

    # Shape-preserving by induction (leaves replace equal-length runs, so every child's count is unchanged), which
    # makes counts/count/height all reusable as-is -- sharing the counts tuple across versions. len(children) ==
    # len(n.children) >= 2, so _make_branch_raw's unary collapse cannot apply and bypassing it is safe.
    return _Branch(
        children=tuple(children),
        counts=n.counts,
        count=n.count,
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

    left, rest = _split(n, start)
    _, right = _split(rest, remove_len)
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
        return self.next()

    def has_next(self) -> bool:
        if self._next is not _MISSING:
            return True

        try:
            self._next = next(self._it)
        except StopIteration:
            return False

        return True

    def next(self) -> T:
        if self._next is not _MISSING:
            ret = self._next
            self._next = _MISSING
            return ret

        return next(self._it)


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
