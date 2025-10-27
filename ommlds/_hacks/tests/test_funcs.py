from omlish import lang

from ..funcs import create_detour


def test_recode_func():
    class C:
        def f(self):
            return 1

    assert C().f() == 1

    def patch_f():
        func = C.f
        code = func.__code__
        newcode = code.replace(co_consts=(None, 2))
        func.__code__ = newcode

    patch_f()

    assert C().f() == 2


def test_create_detour():
    def f(x):
        return x + 1

    def g(x):
        return x + 2

    assert f(3) == 4
    co = create_detour(lang.ParamSpec.inspect(f), g)
    f.__code__ = co
    assert f(3) == 5
