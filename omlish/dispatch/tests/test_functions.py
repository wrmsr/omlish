import typing as ta

from ..functions import function


def test_function():
    @function
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
    def f_a_or_b(x: ta.Union[A, B]):  # noqa
        return 'a_or_b'

    assert f(A()) == 'a_or_b'
    assert f(B()) == 'a_or_b'

    class C:
        pass

    class D:
        pass

    @f.register
    def f_c_or_d(x: C | D):
        return 'c_or_d'

    assert f(C()) == 'c_or_d'
    assert f(D()) == 'c_or_d'
