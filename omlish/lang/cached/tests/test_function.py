import dataclasses as dc
import functools
import time
import typing as ta

import pytest

from .... import testing as tu
from ...contextmanagers import context_wrapped
from ..function import cached_function


def test_cached_function_nullary():
    c = 0

    @cached_function
    def f():
        nonlocal c
        c += 1
        return 'f'

    assert f() == 'f'
    assert c == 1
    assert f() == 'f'
    assert c == 1
    f.reset()
    assert f() == 'f'
    assert c == 2
    assert f() == 'f'
    assert c == 2

    class C:
        cv = 'C'

        def __init__(self, iv):
            super().__init__()
            self.iv = iv

        @cached_function
        @staticmethod
        def s() -> str:
            nonlocal c
            c += 1
            return 'C.s'

        @cached_function
        @classmethod
        def c(cls) -> str:
            nonlocal c
            c += 1
            return f'C.c({cls.cv})'

        @cached_function
        def i(self) -> str:
            nonlocal c
            c += 1
            return f'C.i({self.iv})'

    class D(C):
        cv = 'D'

    c = 0
    ci = C('c')
    di = D('d')

    assert C.s() == 'C.s'
    assert c == 1
    assert C.s() == 'C.s'
    assert c == 1
    assert D.s() == 'C.s'
    assert c == 1
    assert ci.s() == 'C.s'
    assert c == 1
    assert di.s() == 'C.s'
    assert c == 1

    c = 0

    assert C.c() == 'C.c(C)'
    assert c == 1
    assert C.c() == 'C.c(C)'
    assert c == 1
    assert ci.c() == 'C.c(C)'
    assert c == 1
    assert D.c() == 'C.c(D)'
    assert c == 2
    assert di.c() == 'C.c(D)'
    assert c == 2

    c = 0
    ci2 = C('c2')

    assert ci.i() == 'C.i(c)'
    assert c == 1
    assert ci.i() == 'C.i(c)'
    assert c == 1
    assert di.i() == 'C.i(d)'
    assert c == 2
    assert ci2.i() == 'C.i(c2)'
    assert c == 3
    assert ci2.i() == 'C.i(c2)'
    assert c == 3


def test_cached_function():
    c = 0

    @cached_function
    def f(x, y):
        nonlocal c
        c += 1
        return x + y

    for _ in range(2):
        assert f(1, 2) == 3
        assert c == 1


def test_cached_function_locked():
    c = 0
    e = 0

    @cached_function(lock=True)
    def f(x, y):
        nonlocal c, e
        c += 1
        e += 1
        # FIXME: lol
        for _ in range(2):
            time.sleep(.1)
            assert e == 1
        e -= 1
        time.sleep(.1)
        assert e == 0
        return x + y

    def do():
        assert f(1, 2) == 3

    tu.call_many_with_timeout([do for _ in range(2)])
    assert c == 1


def test_collections_cache():
    from ....collections import cache

    xys = []

    @cached_function(map_maker=functools.partial(cache.new_cache, max_size=3))
    def f(x, y):
        xys.append((x, y))
        return x + y

    assert f(1, 2) == 3
    assert xys == [(1, 2)]
    assert f(1, 2) == 3
    assert xys == [(1, 2)]
    assert f(1, 3) == 4
    assert xys == [(1, 2), (1, 3)]
    assert f(1, 2) == 3
    assert f(1, 3) == 4
    assert xys == [(1, 2), (1, 3)]
    assert f(2, 3) == 5
    assert xys == [(1, 2), (1, 3), (2, 3)]
    assert f(2, 3) == 5
    assert f(1, 3) == 4
    assert f(1, 2) == 3
    assert xys == [(1, 2), (1, 3), (2, 3)]
    assert f(2, 1) == 3
    assert xys == [(1, 2), (1, 3), (2, 3), (2, 1)]
    assert f(1, 2) == 3
    assert xys == [(1, 2), (1, 3), (2, 3), (2, 1)]
    assert f(2, 3) == 5
    assert xys == [(1, 2), (1, 3), (2, 3), (2, 1), (2, 3)]


def test_context_wrapped():
    class ContextCounter:
        enter_count = 0
        exit_count = 0

        def __enter__(self):
            self.enter_count += 1

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.exit_count += 1

    class C:
        def __init__(self) -> None:
            super().__init__()
            self._lock = ContextCounter()

        @cached_function
        @context_wrapped('_lock')
        def a(self):
            return 'a'

        @cached_function
        @context_wrapped('_lock')
        def b(self):
            return f'b{self.a()}'

        @cached_function
        @context_wrapped('_lock')
        def c(self):
            return f'c{self.a()}'

        @cached_function
        @context_wrapped('_lock')
        def d(self):
            return f'd{self.c()}{self.b()}'

    c = C()
    assert c.d() == 'dcaba'
    assert c._lock.enter_count == 4  # noqa
    assert c._lock.exit_count == 4  # noqa


def test_func_only_kws():
    c = 0

    @cached_function
    def foo(**kw):
        nonlocal c
        c += 1
        return kw

    assert c == 0

    for _ in range(2):
        assert foo() == {}
        assert c == 1

    for _ in range(2):
        assert foo(x=1) == {'x': 1}
        assert c == 2

    for _ in range(2):
        assert foo(x=1, y=2) == {'x': 1, 'y': 2}
        assert c == 3
        assert foo(y=2, x=1) == {'x': 1, 'y': 2}
        assert c == 3


def test_partials():
    c = 0

    @cached_function
    def f(x):
        nonlocal c
        c += 1
        return x + 1

    pf = functools.partial(f, 1)
    assert c == 0
    for _ in range(2):
        assert pf() == 2
        assert f(1) == 2
        assert c == 1


class Thingy(ta.NamedTuple):
    v: ta.Any


class _TypeEq:
    def __eq__(self, other):
        return type(other) is type(self)

    def __ne__(self, other):
        return not (self == other)


@dc.dataclass()
class Ex1(Exception):  # noqa
    pass


@dc.dataclass()
class Ex2(Ex1):  # noqa
    pass


@dc.dataclass()
class Ex3(Exception):  # noqa
    pass


def test_no_cache_exceptions():
    c = 0

    @cached_function
    def fn(v):
        nonlocal c
        c += 1
        if isinstance(v, type) and issubclass(v, Exception):
            raise v
        return v

    assert c == 0
    assert fn(5) == 5
    assert c == 1

    for i in range(2):
        with pytest.raises(Ex1):
            fn(Ex1)
        assert c == 2 + i


def test_cache_exceptions():
    c = 0

    @cached_function(cache_exceptions=(Ex1,))
    def fn(v):
        nonlocal c
        c += 1
        if isinstance(v, type) and issubclass(v, Exception):
            raise v
        return v

    assert c == 0
    assert fn(5) == 5
    assert c == 1

    for _ in range(2):
        with pytest.raises(Ex1):
            fn(Ex1)
        assert c == 2

    for _ in range(2):
        with pytest.raises(Ex2):
            fn(Ex2)
        assert c == 3

    for i in range(2):
        with pytest.raises(Ex3):
            fn(Ex3)
        assert c == 4 + i


def test_bound_method():
    class Foo:
        c = 0

        def f(self, x):
            self.c += 1
            return x + 1

    foo = Foo()
    f = cached_function(foo.f)
    assert foo.c == 0
    for _ in range(2):
        assert f(5) == 6
        assert foo.c == 1
    assert f(6) == 7
    assert foo.c == 2
