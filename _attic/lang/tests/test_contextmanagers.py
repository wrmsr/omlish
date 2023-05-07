import collections.abc
import contextlib

from .. import contextmanagers as cms_


def test_manage_maybe_iterator():
    i = 0

    @contextlib.contextmanager
    def manager():
        nonlocal i
        i += 1
        yield

    assert cms_.manage_maybe_iterator(manager, lambda: None) is None
    assert i == 1

    assert cms_.manage_maybe_iterator(manager, lambda: []) == []
    assert i == 2

    it = cms_.manage_maybe_iterator(manager, lambda: iter([]))
    assert isinstance(it, collections.abc.Iterator)
    assert i == 3
    assert list(it) == []
    assert i == 4

    it = cms_.manage_maybe_iterator(manager, lambda: iter(range(3)))
    assert isinstance(it, collections.abc.Iterator)
    assert i == 5
    assert list(it) == [0, 1, 2]
    assert i == 6


def test_exit_stacked():
    class A(cms_.ExitStacked):
        pass

    with A() as a:
        assert isinstance(a, A)
        assert isinstance(a._exit_stack, contextlib.ExitStack)

    class B(cms_.ExitStacked):

        def __enter__(self):
            return 'hi'

    with B() as b:
        assert b == 'hi'


def test_context_wrapped():
    class CM:
        count = 0

        def __enter__(self):
            self.count += 1

        def __exit__(self, et, e, tb):
            pass

    cm = CM()

    @cms_.context_wrapped(cm)
    def f(x):
        return x + 1

    assert f(4) == 5
    assert cm.count == 1
    assert f(5) == 6
    assert cm.count == 2

    class C:
        def __init__(self):
            self.cm = CM()

        @cms_.context_wrapped('cm')
        def f(self, x):
            return x + 2

    for _ in range(2):
        c = C()
        assert c.f(6) == 8
        assert c.cm.count == 1

    gcm = CM()

    @cms_.context_wrapped(lambda x: gcm)
    def g(x):
        return x + 3

    assert g(10) == 13
    assert gcm.count == 1

    class D:
        @cms_.context_wrapped(lambda self, x: gcm)
        def g(self, x):
            return x + 3

    d = D()
    assert d.g(10) == 13
    assert gcm.count == 2
