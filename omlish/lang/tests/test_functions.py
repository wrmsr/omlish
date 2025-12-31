import pytest

from ..functions import coalesce
from ..functions import finally_
from ..functions import opt_coalesce
from ..functions import strict_eq
from ..functions import try_


class FooError(Exception):
    pass


def test_try():
    def foo():
        raise FooError

    assert try_(foo, FooError, 5)() == 5


def test_try_with_multiple_exceptions():
    """Regression test: try_ should work with multiple exception types."""

    class BarError(Exception):
        pass

    def raise_foo():
        raise FooError('foo')

    def raise_bar():
        raise BarError('bar')

    def raise_value():
        raise ValueError('value')

    # Test with iterable of exception types
    wrapped_foo = try_(raise_foo, [FooError, BarError], default='caught')
    assert wrapped_foo() == 'caught'

    wrapped_bar = try_(raise_bar, [FooError, BarError], default='caught')
    assert wrapped_bar() == 'caught'

    wrapped_value = try_(raise_value, [FooError, BarError], default='caught')
    with pytest.raises(ValueError):
        wrapped_value()


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
