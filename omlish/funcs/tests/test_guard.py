import typing as ta

import pytest

from ... import check
from .. import guard as gfs


def test_dumb():
    assert gfs.dumb(lambda x: x + 1)(1)() == 2


def test_multi():
    def inc_int(x: ta.Any) -> ta.Callable[[], ta.Any] | None:
        if isinstance(x, int):
            return lambda: x + 1
        else:
            return None

    def exclaim_str(s: ta.Any) -> ta.Callable[[], ta.Any] | None:
        if isinstance(s, str):
            return lambda: s + '!'
        else:
            return None

    mgf = gfs.multi(inc_int, exclaim_str)
    assert check.not_none(mgf(1))() == 2
    assert check.not_none(mgf('1'))() == '1!'
    assert mgf(1.0) is None


@pytest.mark.parametrize('instance_cache', [False, True])
def test_guard_method(instance_cache):
    class A:
        @gfs.method(strict=True, instance_cache=instance_cache)
        def foo(self, x: ta.Any) -> ta.Callable[[], str] | None:
            raise NotImplementedError

        @foo.register
        def foo_int(self, x: ta.Any) -> ta.Callable[[], str] | None:
            if not isinstance(x, int):
                return None
            return lambda: f'A.foo_int: {x}'

        @foo.register
        def foo_str(self, x: ta.Any) -> ta.Callable[[], str] | None:
            if not isinstance(x, str):
                return None
            return lambda: f'A.foo_str: {x}'

    for _ in range(2):
        a = A()

        assert a.foo(1)() == 'A.foo_int: 1'
        assert a.foo('x')() == 'A.foo_str: x'
        assert a.foo([]) is None

        assert A.foo(a, 1)() == 'A.foo_int: 1'
        assert A.foo(a, 'x')() == 'A.foo_str: x'
        assert A.foo(a, []) is None

    class B(A):
        @A.foo.register
        def foo_list(self, x: ta.Any) -> ta.Callable[[], str] | None:
            if not isinstance(x, list):
                return None
            return lambda: f'B.foo_list: {x}'

    for _ in range(2):
        b = B()

        assert b.foo(1)() == 'A.foo_int: 1'
        assert b.foo('x')() == 'A.foo_str: x'
        assert b.foo([])() == 'B.foo_list: []'

        assert B.foo(b, 1)() == 'A.foo_int: 1'
        assert B.foo(b, 'x')() == 'A.foo_str: x'
        assert B.foo(b, [])() == 'B.foo_list: []'


@pytest.mark.parametrize('instance_cache', [False, True])
def test_guard_method_with_default(instance_cache):
    class A:
        @gfs.method(strict=True, default=True, instance_cache=instance_cache)
        def foo(self, x: ta.Any) -> ta.Callable[[], str]:
            return lambda: f'A.foo: {x}'

        @foo.register
        def foo_int(self, x: ta.Any) -> ta.Callable[[], str] | None:
            if not isinstance(x, int):
                return None
            return lambda: f'A.foo_int: {x}'

        @foo.register
        def foo_str(self, x: ta.Any) -> ta.Callable[[], str] | None:
            if not isinstance(x, str):
                return None
            return lambda: f'A.foo_str: {x}'

    for _ in range(2):
        a = A()

        assert a.foo(1)() == 'A.foo_int: 1'
        assert a.foo('x')() == 'A.foo_str: x'
        assert a.foo([])() == 'A.foo: []'

        assert A.foo(a, 1)() == 'A.foo_int: 1'
        assert A.foo(a, 'x')() == 'A.foo_str: x'
        assert A.foo(a, [])() == 'A.foo: []'

    class B(A):
        @A.foo.register
        def foo_list(self, x: ta.Any) -> ta.Callable[[], str] | None:
            if not isinstance(x, list):
                return None
            return lambda: f'B.foo_list: {x}'

    for _ in range(2):
        b = B()

        assert b.foo(1)() == 'A.foo_int: 1'
        assert b.foo('x')() == 'A.foo_str: x'
        assert b.foo([])() == 'B.foo_list: []'

        assert B.foo(b, 1)() == 'A.foo_int: 1'
        assert B.foo(b, 'x')() == 'A.foo_str: x'
        assert B.foo(b, [])() == 'B.foo_list: []'


@pytest.mark.parametrize('instance_cache', [False, True])
def test_immediate_guard_method(instance_cache):
    class A:
        @gfs.immediate_method(strict=True, instance_cache=instance_cache)
        def foo(self, x: ta.Any) -> str:
            return f'A.foo: {x}'

        @foo.register
        def foo_int(self, x: ta.Any) -> ta.Callable[[], str] | None:
            if not isinstance(x, int):
                return None
            return lambda: f'A.foo_int: {x}'

        @foo.register
        def foo_str(self, x: ta.Any) -> ta.Callable[[], str] | None:
            if not isinstance(x, str):
                return None
            return lambda: f'A.foo_str: {x}'

    for _ in range(2):
        a = A()

        assert a.foo(1) == 'A.foo_int: 1'
        assert a.foo('x') == 'A.foo_str: x'
        assert a.foo([]) == 'A.foo: []'

        assert A.foo(a, 1) == 'A.foo_int: 1'
        assert A.foo(a, 'x') == 'A.foo_str: x'
        assert A.foo(a, []) == 'A.foo: []'

    class B(A):
        @A.foo.register
        def foo_list(self, x: ta.Any) -> ta.Callable[[], str] | None:
            if not isinstance(x, list):
                return None
            return lambda: f'B.foo_list: {x}'

    for _ in range(2):
        b = B()

        assert b.foo(1) == 'A.foo_int: 1'
        assert b.foo('x') == 'A.foo_str: x'
        assert b.foo([]) == 'B.foo_list: []'

        assert B.foo(b, 1) == 'A.foo_int: 1'
        assert B.foo(b, 'x') == 'A.foo_str: x'
        assert B.foo(b, []) == 'B.foo_list: []'
