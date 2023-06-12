import typing as ta

import pytest

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

    for _ in range(2):
        obj = A()
        assert obj.f(None) == 'A:object'
        assert obj.f(1) == 'A:object'
        assert obj.f('') == 'A:str'

    class B(A):
        @A.f.register
        def f_int(self, x: int):
            return 'B:int'

        @A.f.register
        def f_str(self, x: str):
            return 'B:str'

    for _ in range(2):
        obj = A()
        assert obj.f(None) == 'A:object'
        assert obj.f(1) == 'A:object'
        assert obj.f('') == 'A:str'

        obj = B()
        assert obj.f(None) == 'A:object'
        assert obj.f(1) == 'B:int'
        assert obj.f('') == 'B:str'

    class C(B):
        pass

    for _ in range(2):
        obj = C()
        assert obj.f(None) == 'A:object'
        assert obj.f(1) == 'B:int'
        assert obj.f('') == 'B:str'

    class D(B):
        @A.f.register
        def f_str(self, x: str):
            return 'D:' + super().f_str(x)

    for _ in range(2):
        obj = D()
        assert obj.f(None) == 'A:object'
        assert obj.f(1) == 'B:int'
        assert obj.f('') == 'D:B:str'

    # TODO:
    class E(B):
        @A.f.register
        def f_str(self, x: str):
            return 'E:' + super().f(x)

    for _ in range(2):
        obj = E()
        assert obj.f(None) == 'A:object'
        assert obj.f(1) == 'B:int'
        # assert obj.f('') == 'E:B:str'
        with pytest.raises(TypeError):
            obj.f('')
