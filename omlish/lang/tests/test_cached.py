import functools
import pickle
import time

from ... import testing as tu
from ..cached import cached_function
from ..cached import cached_property
from ..contextmanagers import context_wrapped


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


def test_property():
    n = 0

    class C:
        @cached_property
        def x(self) -> int:
            nonlocal n
            n += 1
            return n

    c = C()
    assert c.x == 1
    assert c.x == 1
    assert C().x == 2
    assert C().x == 3


def test_collections_cache():
    from ...collections import cache

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


class _PickleTestClass:
    _c = 0

    @classmethod
    def c(cls) -> int:
        c = cls._c
        cls._c += 1
        return c

    @cached_function()
    def d_func(self) -> int:
        return self.c()

    @cached_function(transient=True)
    def t_func(self) -> int:
        return self.c()

    @cached_property()
    def d_prop(self) -> int:
        return self.c()

    @cached_property(transient=True)
    def t_prop(self) -> int:
        return self.c()


def test_pickling():
    c = _PickleTestClass()
    for _ in range(2):
        assert c.d_func() == 0
        assert c.t_func() == 1
        assert c.d_prop == 2
        assert c.t_prop == 3

    c2 = pickle.loads(pickle.dumps(c))  # noqa
    for _ in range(2):
        assert c2.d_func() == 0
        assert c2.t_func() == 4
        assert c2.d_prop == 2
        assert c2.t_prop == 5
