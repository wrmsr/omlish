import pytest  # noqa

from .. import methods


def test_method():
    class A:
        @methods.method
        def f(self, x: object):
            return 'A:object'

        @f.register
        def f_str(self, x: str):
            return 'A:str'

    assert A().f(object()) == 'A:object'
    assert A().f(None) == 'A:object'
    assert A().f(1) == 'A:object'
    assert A().f('') == 'A:str'


def test_method_mro():
    class A:
        @methods.method
        def f(self, x: object):
            return 'A:object'

        @f.register
        def f_str(self, x: str):
            return 'A:str'

    repr(A.f)  # noqa

    for _ in range(2):
        obj = A()
        assert obj.f(None) == 'A:object'
        assert obj.f(1) == 'A:object'
        assert obj.f('') == 'A:str'
        assert A.f(obj, None) == 'A:object'
        assert A.f(obj, 1) == 'A:object'
        assert A.f(obj, '') == 'A:str'

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
        assert A.f(obj, None) == 'A:object'
        assert A.f(obj, 1) == 'A:object'
        assert A.f(obj, '') == 'A:str'

        obj = B()
        assert obj.f(None) == 'A:object'
        assert obj.f(1) == 'B:int'
        assert obj.f('') == 'B:str'
        assert A.f(obj, None) == 'A:object'
        assert A.f(obj, 1) == 'B:int'
        assert A.f(obj, '') == 'B:str'

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

    # class E(B):
    #     @A.f.register
    #     def f_str(self, x: str):
    #         return 'E:' + super().f(x)
    #
    # for _ in range(2):
    #     obj = E()
    #     assert obj.f(None) == 'A:object'
    #     assert obj.f(1) == 'B:int'
    #     # assert obj.f('') == 'E:B:str'
    #     with pytest.raises(TypeError):
    #         obj.f('')


def test_method_no_set_name():
    class A:
        pass

    def f(self, x: object):
        return 'A:object'

    A.f = methods.method(f)  # type: ignore

    assert A().f(None) == 'A:object'  # type: ignore


def test_accessor_wrapper_atts():
    class A:
        @methods.method
        def f(self, x: object):
            """foo"""
            return 'A:object'

    class B(A):
        @A.f.register
        def f_str(self, x: str):
            return 'B:str'

    assert A().f('') == 'A:object'
    assert B().f('') == 'B:str'

    assert A.f.__doc__ == 'foo'
    assert B.f.__doc__ == 'foo'
