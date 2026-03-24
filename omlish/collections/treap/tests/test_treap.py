import random
import typing as ta

import pytest

from .. import treap


def int_cmp(a: int, b: int) -> int:
    return (a > b) - (a < b)


def pair_key_cmp(a: tuple[int, str | None], b: tuple[int, str | None]) -> int:
    return (a[0] > b[0]) - (a[0] < b[0])


def make_node(v: int, *, rng: random.Random) -> treap.TreapNode[int]:
    return treap.new(
        v,
        priority=rng.getrandbits(32),
    )


def make_pair_node(
        k: int,
        v: str | None,
        *,
        rng: random.Random,
) -> treap.TreapNode[tuple[int, str | None]]:
    return treap.new(
        (k, v),
        priority=rng.getrandbits(32),
    )


def build_tree(values: ta.Iterable[int], *, seed: int = 0) -> treap.TreapNode[int] | None:
    rng = random.Random(seed)
    n: treap.TreapNode[int] | None = None
    for v in values:
        n = treap.union(n, make_node(v, rng=rng), int_cmp, True)
    return n


def build_pair_tree(
        items: ta.Iterable[tuple[int, str | None]],
        *,
        seed: int = 0,
) -> treap.TreapNode[tuple[int, str | None]] | None:
    rng = random.Random(seed)
    n: treap.TreapNode[tuple[int, str | None]] | None = None
    for k, v in items:
        n = treap.union(n, make_pair_node(k, v, rng=rng), pair_key_cmp, True)
    return n


def inorder(n: treap.TreapNode[int] | None) -> list[int]:
    return list(n) if n is not None else []


def inorder_pairs(
        n: treap.TreapNode[tuple[int, str | None]] | None,
) -> list[tuple[int, str | None]]:
    return list(n) if n is not None else []


def validate_treap(
        n: treap.TreapNode[int] | None,
        *,
        lo: int | None = None,
        hi: int | None = None,
) -> int:
    """
    Public-surface invariant check using only public properties:
      - BST invariant
      - heap invariant
      - count invariant
    Returns subtree size.
    """
    if n is None:
        return 0

    if lo is not None:
        assert lo < n.value
    if hi is not None:
        assert n.value < hi

    if n.left is not None:
        assert n.left.value < n.value
        assert n.priority >= n.left.priority
    if n.right is not None:
        assert n.value < n.right.value
        assert n.priority >= n.right.priority

    lc = validate_treap(n.left, lo=lo, hi=n.value)
    rc = validate_treap(n.right, lo=n.value, hi=hi)

    expected = 1 + lc + rc
    assert n.count == expected
    return expected


def validate_pair_treap(
        n: treap.TreapNode[tuple[int, str | None]] | None,
        *,
        lo: int | None = None,
        hi: int | None = None,
) -> int:
    if n is None:
        return 0

    k = n.value[0]

    if lo is not None:
        assert lo < k
    if hi is not None:
        assert k < hi

    if n.left is not None:
        assert n.left.value[0] < k
        assert n.priority >= n.left.priority
    if n.right is not None:
        assert k < n.right.value[0]
        assert n.priority >= n.right.priority

    lc = validate_pair_treap(n.left, lo=lo, hi=k)
    rc = validate_pair_treap(n.right, lo=k, hi=hi)

    expected = 1 + lc + rc
    assert n.count == expected
    return expected


def test_find_present_and_missing():
    n = build_tree([5, 2, 8, 1, 3], seed=1)

    found = treap.find(n, 3, int_cmp)
    assert found is not None
    assert found.value == 3

    missing = treap.find(n, 999, int_cmp)
    assert missing is None

    validate_treap(n)


def test_inorder_is_sorted_and_count_matches():
    vals = [5, 2, 8, 1, 3, 7, 9]
    n = build_tree(vals, seed=2)

    assert inorder(n) == sorted(vals)
    assert n is not None
    assert n.count == len(vals)
    validate_treap(n)


@pytest.mark.parametrize(
    ('values', 'pivot'),
    [
        ([5, 2, 8, 1, 3, 7, 9], 5),
        ([5, 2, 8, 1, 3, 7, 9], 4),
        ([5, 2, 8, 1, 3, 7, 9], 0),
        ([5, 2, 8, 1, 3, 7, 9], 10),
        ([], 5),
    ],
)
def test_split_partitions_correctly(values: list[int], pivot: int):
    n = build_tree(values, seed=3)

    left, dupe, right = treap.split(n, pivot, int_cmp)

    left_vals = inorder(left)
    right_vals = inorder(right)

    assert all(v < pivot for v in left_vals)
    assert all(v > pivot for v in right_vals)

    if pivot in values:
        assert dupe is not None
        assert dupe.value == pivot
    else:
        assert dupe is None

    got = left_vals + ([dupe.value] if dupe is not None else []) + right_vals
    assert got == sorted(values)

    validate_treap(left)
    validate_treap(dupe)
    validate_treap(right)


def test_delete_present_removes_key():
    vals = [5, 2, 8, 1, 3, 7, 9]
    n = build_tree(vals, seed=4)

    n2 = treap.delete(n, 5, int_cmp)

    assert inorder(n2) == [1, 2, 3, 7, 8, 9]
    validate_treap(n2)
    assert inorder(n) == sorted(vals)
    validate_treap(n)


def test_delete_missing_is_content_noop():
    vals = [5, 2, 8, 1, 3, 7, 9]
    n = build_tree(vals, seed=5)
    n2 = treap.delete(n, 12345, int_cmp)

    assert inorder(n2) == sorted(vals)
    validate_treap(n2)


def test_place_ascending_behavior():
    n = build_tree([10, 20, 30, 40, 50], seed=6)

    lst = treap.place(n, 25, int_cmp)
    assert lst
    assert lst[-1].value == 30

    lst2 = treap.place(n, 30, int_cmp)
    assert lst2
    assert lst2[-1].value == 30

    lst3 = treap.place(n, 99, int_cmp)
    assert lst3 == []


def test_place_descending_behavior():
    n = build_tree([10, 20, 30, 40, 50], seed=7)

    lst = treap.place(n, 25, int_cmp, desc=True)
    assert lst
    assert lst[-1].value == 20

    lst2 = treap.place(n, 30, int_cmp, desc=True)
    assert lst2
    assert lst2[-1].value == 30

    lst3 = treap.place(n, -1, int_cmp, desc=True)
    assert lst3 == []


def test_union_overwrite_true_prefers_other_for_duplicate_key():
    rng = random.Random(8)

    left = make_pair_node(1, 'left', rng=rng)
    right = make_pair_node(1, 'right', rng=rng)

    out = treap.union(left, right, pair_key_cmp, True)

    assert out is not None
    assert out.value == (1, 'right')
    assert out.count == 1
    validate_pair_treap(out)


def test_union_overwrite_false_prefers_original_for_duplicate_key():
    rng = random.Random(9)

    left = make_pair_node(1, 'left', rng=rng)
    right = make_pair_node(1, 'right', rng=rng)

    out = treap.union(left, right, pair_key_cmp, False)

    assert out is not None
    assert out.value == (1, 'left')
    assert out.count == 1
    validate_pair_treap(out)


def test_intersect():
    a = build_tree([1, 2, 3, 4, 5], seed=10)
    b = build_tree([4, 5, 6, 7], seed=11)

    out = treap.intersect(a, b, int_cmp)

    assert inorder(out) == [4, 5]
    validate_treap(out)


def test_diff():
    a = build_tree([1, 2, 3, 4, 5], seed=12)
    b = build_tree([2, 4, 6], seed=13)

    out = treap.diff(a, b, int_cmp)

    assert inorder(out) == [1, 3, 5]
    validate_treap(out)


def test_persistence_original_unchanged_after_delete():
    n = build_tree([1, 2, 3, 4, 5], seed=14)
    before = inorder(n)

    n2 = treap.delete(n, 3, int_cmp)

    assert inorder(n) == before
    assert inorder(n2) == [1, 2, 4, 5]
    validate_treap(n)
    validate_treap(n2)


def test_randomized_insert_delete_find_against_set():
    rng = random.Random(0xC0FFEE)

    root: treap.TreapNode[int] | None = None
    expected: set[int] = set()

    for _ in range(300):
        op = rng.choice(['insert', 'delete', 'find'])
        v = rng.randrange(50)

        if op == 'insert':
            root = treap.union(root, make_node(v, rng=rng), int_cmp, True)
            expected.add(v)

        elif op == 'delete':
            root = treap.delete(root, v, int_cmp)
            expected.discard(v)

        else:
            found = treap.find(root, v, int_cmp)
            assert (found is not None) == (v in expected)

        assert inorder(root) == sorted(expected)
        if root is not None:
            assert root.count == len(expected)
        validate_treap(root)


def test_randomized_union_intersect_diff_against_sets():
    rng = random.Random(0xABC123)

    for _ in range(50):
        a_vals = {rng.randrange(40) for _ in range(20)}
        b_vals = {rng.randrange(40) for _ in range(20)}

        a = build_tree(sorted(a_vals), seed=rng.getrandbits(32))
        b = build_tree(sorted(b_vals), seed=rng.getrandbits(32))

        u = treap.union(a, b, int_cmp, True)
        i = treap.intersect(a, b, int_cmp)
        d = treap.diff(a, b, int_cmp)

        assert inorder(u) == sorted(a_vals | b_vals)
        assert inorder(i) == sorted(a_vals & b_vals)
        assert inorder(d) == sorted(a_vals - b_vals)

        validate_treap(u)
        validate_treap(i)
        validate_treap(d)
