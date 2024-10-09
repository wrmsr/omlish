import inspect
import sys

from .. import objs as objs_


def test_recode_func():
    def g():
        frame = sys._getframe(1)
        func = objs_.get_code_function(frame.f_code)
        code = func.__code__
        newcodeargs = [getattr(code, f'co_{a}') for a in objs_.CODE_ARGS]
        newcodeargs[objs_.CODE_ARGS.index('consts')] = (None, 2)
        newcode = type(code)(*newcodeargs)
        func.__code__ = newcode

    class C:
        def f(self):
            g()
            return 1

    assert C().f() == 1
    assert C().f() == 2


def test_get_code_function():
    def f():
        return objs_.get_code_function(sys._getframe(1).f_code)

    def g():
        return f()

    v = g()
    assert v is g


def test_create_detour():
    def f(x):
        return x + 1

    def g(x):
        return x + 2

    assert f(3) == 4
    co = objs_.create_detour(inspect.getfullargspec(f), g)
    f.__code__ = co
    assert f(3) == 5
