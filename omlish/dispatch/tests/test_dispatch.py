import typing as ta

from .. import dispatch


def test_dispatch():
    @dispatch.function
    def f(x: object):
        return 'object'

    @f.register
    def f_int(x: int):
        return 'int'

    @f.register
    def f_str(x: str):
        return 'str'

    assert f(1.) == 'object'
    assert f(1) == 'int'
    assert f('1') == 'str'

    class A:
        pass

    class B:
        pass

    @f.register
    def f_a_or_b(x: ta.Union[A, B]):
        return 'a_or_b'

    assert f(A()) == 'a_or_b'
    assert f(B()) == 'a_or_b'


def test_method():
    class A:
        @dispatch.method
        def f(self, x: object):
            return 'A:object'

        @f.register
        def f_str(self, x: str):
            return 'A:str'

    assert A().f(None) == 'A:object'
    assert A().f(1) == 'A:object'
    assert A().f('') == 'A:str'


def test_method_mro():
    class A:
        @dispatch.method
        def f(self, x: object):
            return 'A:object'

        @f.register
        def f_str(self, x: str):
            return 'A:str'

    assert A().f(None) == 'A:object'
    assert A().f(1) == 'A:object'
    assert A().f('') == 'A:str'

    class B(A):
        @A.f.register
        def f_int(self, x: int):
            return 'B:int'

        @A.f.register
        def f_str(self, x: str):
            return 'B:str'

    assert A().f(None) == 'A:object'
    assert A().f(1) == 'A:object'
    assert A().f('') == 'A:str'

    assert B().f(None) == 'A:object'
    assert B().f(1) == 'B:int'
    assert B().f('') == 'B:str'

    class C(B):
        pass

    assert C().f(None) == 'A:object'
    assert C().f(1) == 'B:int'
    assert C().f('') == 'B:str'
