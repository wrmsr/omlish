import functools

from ..cached import cached_property
from ..cached import cached_function


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
        def s():
            nonlocal c
            c += 1
            return 'C.s'

        @cached_function
        @classmethod
        def c(cls):
            nonlocal c
            c += 1
            return f'C.c({cls.cv})'

        @cached_function
        def i(self):
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
