import pickle

from .. import functions as fns


def test_cls_dct():
    class C:
        assert fns.is_possibly_cls_dct(locals())

    assert not fns.is_possibly_cls_dct(locals())


def test_const():
    c = fns.constant(4)
    assert c() == 4
    assert pickle.loads(pickle.dumps(c))() == 4


def test_cmp():
    assert fns.cmp('a', 'b') == -1
    assert fns.cmp('b', 'b') == 0
    assert fns.cmp('c', 'b') == 1


def test_recurse():
    assert fns.recurse(lambda rec, i: i + (rec(i - 1) if i else 0), 5) == 5 + 4 + 3 + 2 + 1


def test_cached_nullary():
    c = 0

    @fns.cached_nullary
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

        @fns.cached_nullary
        @staticmethod
        def s():
            nonlocal c
            c += 1
            return 'C.s'

        @fns.cached_nullary
        @classmethod
        def c(cls):
            nonlocal c
            c += 1
            return f'C.c({cls.cv})'

        @fns.cached_nullary
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


def test_try():
    assert fns.try_()(int)(5) == 5
    assert fns.try_()(int)('x') is None


def test_optional_of():
    f = fns.optional_of(lambda x: x + 1)
    assert f(1) == 2
    assert f(None) is None
