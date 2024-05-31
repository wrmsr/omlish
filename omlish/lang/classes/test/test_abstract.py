import abc

import pytest

from ..abstract import Abstract
from ..abstract import is_abstract


def test_abstract():
    class C(Abstract):
        pass

    class D(C):
        pass

    class E(D, Abstract):
        pass

    class F(E):
        pass

    with pytest.raises(TypeError):
        C()
    D()
    with pytest.raises(TypeError):
        E()
    F()


def test_abstract2():
    class O(Abstract):
        pass

    assert is_abstract(O)

    with pytest.raises(TypeError):
        O()

    class A(Abstract):
        @abc.abstractmethod
        def f(self):
            pass

    assert is_abstract(A)

    with pytest.raises(TypeError):
        A()  # type: ignore

    class B(A, Abstract):
        pass

    with pytest.raises(TypeError):
        B()  # type: ignore

    class C(B):
        f = 0

    assert C()

    with pytest.raises(TypeError):
        class D(A):
            pass


def test_is_abstract():
    class A(Abstract):
        pass

    assert is_abstract(A)

    class B(A):
        pass

    assert not is_abstract(B)

    class C(Abstract):

        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            if cls.__name__ == 'D':
                assert is_abstract(cls)
            else:
                assert not is_abstract(cls)

    class D(C, Abstract):
        pass

    class E(D):
        pass
