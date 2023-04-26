from .. import defs


def test_delegate_method():
    class C:
        def __init__(self, lst):
            self.lst = lst
        defs.delegate_method('__len__', to='lst')

    assert len(C([1, 2, 3])) == 3


def test_repr():
    class A:
        defs.repr('a', 'b', mro=True)
        a = 0
        b = 1

    assert repr(A()).endswith('(a=0, b=1)')


def test_repr_mro():
    class A:
        defs.repr('a', mro=True)
        a = 0

    class B(A):
        __repr_attrs__ = ['b']
        b = 1

    assert repr(A()).endswith('(a=0)')
    assert repr(B()).endswith('(a=0, b=1)')


def test_repr_recursion():
    class A:
        defs.repr('o')
        o = None

    a = A()
    assert 'self' not in repr(a)
    a.o = a
    assert repr(a).endswith('(o=<self>)')

    b = A()
    a.o, b.o = b, a
    assert '(o=<seen@' in repr(a)
    assert '(o=<seen@' in repr(b)
