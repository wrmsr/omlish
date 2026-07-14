import typing as ta

import pytest

from ..comparison import cmp
from ..comparison import key_cmp


@pytest.mark.parametrize(
    ('l', 'r', 'expected'),
    [
        (1, 1, 0),
        (1, 2, -1),
        (2, 1, 1),
        (-5, -5, 0),
        (-5, 3, -1),
        (3, -5, 1),
        ('a', 'a', 0),
        ('a', 'b', -1),
        ('b', 'a', 1),
    ],
)
def test_cmp_basic(l, r, expected) -> None:
    assert cmp(l, r) == expected


def test_cmp_matches_python_ordering_sign() -> None:
    values = [3, 1, 2, 2, -1, 10]

    for l in values:
        for r in values:
            got = cmp(l, r)
            assert got in (-1, 0, 1)
            assert got == (0 if l == r else (1 if l > r else -1))


def test_cmp_custom_objects_with_rich_comparison() -> None:
    class Box:
        def __init__(self, value: int) -> None:
            self.value = value

        def __lt__(self, other: Box) -> bool:
            return self.value < other.value

        def __gt__(self, other: Box) -> bool:
            return self.value > other.value

    assert cmp(Box(1), Box(1)) == 0
    assert cmp(Box(1), Box(2)) == -1
    assert cmp(Box(2), Box(1)) == 1


def test_key_cmp_default_uses_first_tuple_item_only() -> None:
    kc: ta.Any = key_cmp()

    assert kc((1, 'x'), (1, 'y')) == 0
    assert kc((1, 'x'), (2, 'y')) == -1
    assert kc((2, 'x'), (1, 'y')) == 1


def test_key_cmp_ignores_second_tuple_item_entirely() -> None:
    kc: ta.Any = key_cmp()

    left = (10, object())
    right = (10, object())

    assert kc(left, right) == 0


def test_key_cmp_uses_custom_key_comparator() -> None:
    calls: list[tuple[str, str]] = []

    def reverse_cmp(l: str, r: str) -> int:
        calls.append((l, r))
        return cmp(r, l)

    kc = key_cmp(reverse_cmp)

    assert kc(('a', 1), ('b', 2)) == 1
    assert kc(('b', 1), ('a', 2)) == -1
    assert kc(('x', 1), ('x', 2)) == 0

    assert calls == [('a', 'b'), ('b', 'a'), ('x', 'x')]


def test_key_cmp_can_be_used_with_sorted_via_cmp_to_key() -> None:
    import functools

    items = [(3, 'c'), (1, 'z'), (2, 'x'), (1, 'a')]

    got = sorted(items, key=functools.cmp_to_key(key_cmp()))
    assert got == [(1, 'z'), (1, 'a'), (2, 'x'), (3, 'c')]


def test_key_cmp_can_sort_with_custom_reverse_key_order() -> None:
    import functools

    items = [(3, 'c'), (1, 'z'), (2, 'x')]

    def reverse_cmp(l: int, r: int) -> int:
        return cmp(r, l)

    got = sorted(items, key=functools.cmp_to_key(key_cmp(reverse_cmp)))
    assert got == [(3, 'c'), (2, 'x'), (1, 'z')]
