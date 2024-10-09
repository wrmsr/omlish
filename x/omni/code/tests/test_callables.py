import inspect
import pickle

from .. import callables as cs


class SomeType:
    pass


def test_get_arg_names():
    def f(x, y, z):
        pass
    assert ('x', 'y', 'z') == cs.get_arg_names(inspect.getfullargspec(f))

    def f(x, y, *args, **kwargs):
        pass
    assert ('x', 'y', 'args', 'kwargs') == \
        cs.get_arg_names(inspect.getfullargspec(f))


def test_build_arg_dict():
    def f(x, y, z):
        pass
    assert {'x': 1, 'y': 2, 'z': 3} == \
        cs.build_arg_dict(inspect.getfullargspec(f), (1, 2, 3), {})

    def f(x, y, z, *args, **kwargs):
        pass
    assert {'x': 1, 'y': 2, 'z': 3, 'args': (4, 5), 'kwargs': {'a': 8, 'b': 9}} == \
        cs.build_arg_dict(inspect.getfullargspec(f), (1, 2, 3, 4, 5), {'a': 8, 'b': 9})


def test_alias():
    @cs.alias()
    def f(x):
        return x + 1
    assert 'f' == repr(f)
    assert 2 == f(1)
    assert False == isinstance(f, SomeType)

    @cs.alias(SomeType)
    def f(x):
        return x + 1
    assert 'f' == repr(f)
    assert 2 == f(1)
    assert isinstance(f, SomeType)


def test_constructor():
    @cs.constructor()
    def f(x):
        def g(y):
            return x + y
        return g
    f_ = f(10)
    assert 'f(x=10)' == repr(f_)
    assert 12 == f_(2)
    assert False == isinstance(f_, SomeType)

    @cs.constructor(SomeType)
    def f(x):
        def g(y):
            return x + y
        return g
    f_ = f(10)
    assert 'f(x=10)' == repr(f_)
    assert 12 == f_(2)
    assert isinstance(f_, SomeType)


def test_const():
    c = cs.const(8)
    assert repr(c) == 'const(value=8)'
    assert 8 == c(1, 2, x=3)


def test_arg():
    @cs.constructor()
    def f(x, y, z=10):
        def g(n):
            return x + y + z + n
        return g
    assert f(1, 2).arg.x == 1
    assert f(1, 2).arg.y == 2
    assert f(1, 2).arg.z == 10

    @cs.constructor()
    def f(x, z=10, *ys, **kws):
        return lambda: 420

    g = f(1, 2, 3, 4).arg
    assert g.x == 1
    assert g.z == 2
    assert g.ys == (3, 4)
    assert g.kws == {}


@cs.constructor()
def adder(n: int):
    def inner(v):
        return n + v
    return inner


def test_picklable():
    expr = cs.Expr('lambda: 420')
    assert pickle.loads(pickle.dumps(expr))() == 420

    lmbda = cs.Lambda('x', 'x + 2')
    assert pickle.loads(pickle.dumps(lmbda))(420) == 422

    fn = cs.Function('x', 'return x + 3')
    assert pickle.loads(pickle.dumps(fn))(420) == 423

    assert pickle.loads(pickle.dumps(adder(4)))(3) == 7


def test_method():
    assert cs.method('__len__')([1, 2]) == 2
