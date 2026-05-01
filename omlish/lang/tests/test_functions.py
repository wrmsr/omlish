import typing as ta

import pytest

from ..functions import coalesce
from ..functions import finally_
from ..functions import opt_coalesce
from ..functions import recurse
from ..functions import strict_eq
from ..functions import try_
from ..functions import unnest


class FooError(Exception):
    pass


def test_try():
    def foo():
        raise FooError

    assert try_(foo, FooError, 5)() == 5


def test_finally():
    c = 0

    def foo():
        raise FooError

    def fin():
        nonlocal c
        c += 1

    f = finally_(foo, fin)
    with pytest.raises(FooError):
        f()
    assert c == 1


def test_coalesce():
    oi0: int | None = None
    oi1: int | None = 1

    #

    assert coalesce(oi0, 2) == 2
    assert coalesce(oi1, 2) == 1
    assert coalesce(oi0, oi1, 2) == 1

    with pytest.raises(ValueError):  # noqa
        assert coalesce(oi0, None)

    #

    assert opt_coalesce(oi0, 2) == 2
    assert opt_coalesce(oi1, 2) == 1
    assert opt_coalesce(oi0, oi1, 2) == 1
    assert opt_coalesce(oi0, None) is None


def test_strict_eq():
    class MyStr(str):  # noqa
        pass

    assert 'foo' == MyStr('foo')  # noqa
    assert MyStr('foo') == 'foo'
    assert strict_eq(MyStr('foo'), MyStr('foo'))
    assert strict_eq('foo', 'foo')
    assert not strict_eq(MyStr('foo'), 'foo')
    assert not strict_eq('foo', MyStr('foo'))
    assert not strict_eq(MyStr('foo'), MyStr('bar'))

    class MyOtherStr(str):  # noqa
        def __eq__(self, other):
            return False

        def __ne__(self, other):
            return not self == other

    assert not strict_eq(MyStr('foo'), MyOtherStr('foo'))
    assert not strict_eq(MyOtherStr('foo'), MyOtherStr('foo'))


def test_recurse_factorial() -> None:
    def fact(rec: ta.Callable[[int], int], n: int) -> int:
        return 1 if n <= 1 else n * rec(n - 1)

    assert recurse(fact, 0) == 1
    assert recurse(fact, 1) == 1
    assert recurse(fact, 5) == 120


def test_recurse_multiple_args_and_kwargs() -> None:
    def walk(
        rec: ta.Callable[[int, int], int],
        n: int,
        acc: int = 0,
    ) -> int:
        return acc if n <= 0 else rec(n - 1, acc + n)

    assert recurse(walk, 5) == 15
    assert recurse(walk, 5, acc=10) == 25


def test_recurse_preserves_return_value() -> None:
    marker = object()

    def fn(rec: ta.Callable[[], object]) -> object:
        return marker

    assert recurse(fn) is marker


def test_unnest_leaf_returns_singleton_list() -> None:
    def children(x: int) -> list[int] | None:
        return None

    assert unnest(children, 42) == [42]


def test_unnest_nested_tree() -> None:
    tree: dict[str, list[str] | None] = {
        'root': ['a', 'b'],
        'a': ['c', 'd'],
        'b': None,
        'c': None,
        'd': ['e'],
        'e': None,
    }

    def children(x: str) -> ta.Sequence[str] | None:
        return tree[x]

    assert unnest(children, 'root') == ['c', 'e', 'b']


def test_unnest_empty_children_means_no_leaves() -> None:
    tree: dict[str, list[str] | None] = {
        'root': ['a', 'b', 'c'],
        'a': None,
        'b': [],
        'c': None,
    }

    def children(x: str) -> ta.Sequence[str] | None:
        return tree[x]

    assert unnest(children, 'root') == ['a', 'c']


def test_unnest_preserves_depth_first_left_to_right_order() -> None:
    def children(x: int) -> list[int] | None:
        return None if x <= 1 else [x - 1, x - 2]

    assert unnest(children, 4) == [1, 0, 1, 1, 0]


def test_unnest_propagates_exceptions() -> None:
    def children(x: int) -> list[int] | None:
        if x == 2:
            raise ValueError('boom')
        return None if x <= 1 else [x - 1]

    with pytest.raises(ValueError, match='boom'):
        unnest(children, 3)
