from omlish import lang

from ..funcs import create_detour


def test_recode_func():
    class C:
        def f(self):
            return '$REPLACEME$'

    assert C().f() == '$REPLACEME$'

    def patch_f(v):
        func = C.f
        code = func.__code__
        consts = code.co_consts
        [i] = [i for i, v in enumerate(consts) if v == '$REPLACEME$']
        newcode = code.replace(co_consts=(*consts[:i], v, *consts[i + 1:]))
        func.__code__ = newcode

    patch_f('efgh')

    print(C().f())
    assert C().f() == 'efgh'


def test_create_detour():
    def f(x):
        return x + 1

    def g(x):
        return x + 2

    assert f(3) == 4
    co = create_detour(lang.ParamSpec.inspect(f), g)
    f.__code__ = co
    assert f(3) == 5
