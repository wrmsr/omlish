import contextlib

from .. import dynamic as dyn
from ..dev.pytest import skip_if_cant_import


def test_dyn():
    with dyn.dyn(x=5):
        assert dyn.dyn.x == 5
        with dyn.dyn(y=10):
            assert dyn.dyn.x == 5 and dyn.dyn.y == 10
            with dyn.dyn(x=6):
                assert dyn.dyn.x == 6 and dyn.dyn.y == 10
                with dyn.dyn(y=11):
                    assert dyn.dyn.x == 6 and dyn.dyn.y == 11
                assert dyn.dyn.x == 6 and dyn.dyn.y == 10
            assert dyn.dyn.x == 5 and dyn.dyn.y == 10
        assert dyn.dyn.x == 5

    try:
        dyn.dyn.x
    except AttributeError:
        pass
    else:
        assert False

    def _g1():
        while True:
            yield dyn.dyn.x
    g1 = _g1()

    with dyn.dyn(x=99):
        assert next(g1) == 99

    def _g2(x):
        while True:
            with dyn.dyn(x=x):
                yield next(g1)

    # g2a = _g2('a')
    # g2b = _g2('b')

    # FIXME
    # assert next(g2a) == 'a'
    # assert next(g2b) == 'b'
    # with dyn.dyn(x=100):
    #     assert next(g1) == 100
    #     assert next(g2a) == 'a'
    #     assert next(g2b) == 'b'

    try:
        next(g1)
    except AttributeError:
        pass
    else:
        assert False


def test_var():
    v = dyn.Var()
    with v(4):
        assert v() == 4


def test_cm():
    v = dyn.Var(420)

    @dyn.contextmanager
    def cm():
        with v(421):
            yield

    assert v() == 420
    with cm():
        assert v() == 421
    assert v() == 420

    @dyn.contextmanager
    def cm2():
        with cm():
            yield

    assert v() == 420
    with cm2():
        assert v() == 421
    assert v() == 420

    with contextlib.ExitStack() as es:
        assert v() == 420
        es.enter_context(cm2())
        assert v() == 421
    assert v() == 420


@skip_if_cant_import('greenlet')
def test_greenlet():
    import greenlet

    def test1():
        assert list(v.values) == [0]
        with v(2):
            assert list(v.values) == [2, 0]
            gr2.switch()
            with v(3):
                assert list(v.values) == [3, 2, 0]
                gr2.switch()
                assert list(v.values) == [3, 2, 0]
            assert list(v.values) == [2, 0]
        assert list(v.values) == [0]
        nonlocal done
        done += 1

    def test2():
        def f():
            assert list(v.values) == [4, 0]
            with v(5):
                assert list(v.values) == [5, 4, 0]
                gr1.switch()
                assert list(v.values) == [5, 4, 0]
            assert list(v.values) == [4, 0]

        assert list(v.values) == [0]
        with v(4):
            assert list(v.values) == [4, 0]
            f()
            assert list(v.values) == [4, 0]
        assert list(v.values) == [0]
        nonlocal done
        done += 1
        gr1.switch()

    done = 0
    v = dyn.Var(0)
    assert list(v.values) == [0]
    with v(1):
        assert list(v.values) == [1, 0]

    gr1 = greenlet.greenlet(test1)
    gr2 = greenlet.greenlet(test2)
    gr1.switch()
    assert done == 2

    assert list(v.values) == [0]
