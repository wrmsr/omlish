# ruff: noqa: PT027
import abc
import typing as ta
import unittest

from ..abstract import Abstract


T = ta.TypeVar('T')


class TestAbstract(unittest.TestCase):
    def test_abstract(self):
        class C(Abstract):
            pass

        class D(C):
            pass

        class E(D, Abstract):
            pass

        class F(E):
            pass

        with self.assertRaises(TypeError):
            C()

        D()

        with self.assertRaises(TypeError):
            E()

        F()

    def test_abstract2(self):
        class O(Abstract):
            pass

        # assert is_abstract(O)

        with self.assertRaises(TypeError):
            O()

        class A(Abstract):
            @abc.abstractmethod
            def f(self):
                pass

        # assert is_abstract(A)

        with self.assertRaises(TypeError):
            A()  # type: ignore

        class B(A, Abstract):
            pass

        with self.assertRaises(TypeError):
            B()  # type: ignore

        class B2(A, abc.ABC):
            pass

        with self.assertRaises(TypeError):
            B2()  # type: ignore

        class C(B):
            f = 0  # type: ignore

        assert C()

        with self.assertRaises(TypeError):
            class D(A):
                pass

    def test_abstract_mro_check(self):
        class C1(Abstract, abc.ABC):
            pass

        # class C2(Abstract, ta.Generic[T]):
        #     pass

        # class C3(Abstract, abc.ABC, ta.Generic[T]):
        #     pass

        with self.assertRaises(TypeError) as te:
            class C4(abc.ABC, Abstract):
                pass
        assert str(te.exception).endswith('(ABC, Abstract)')

        # with self.assertRaises(TypeError) as te:
        #     class C5(ta.Generic[T], Abstract):
        #         pass
        # assert str(te.exception).endswith('(Generic, Abstract)')

        # with self.assertRaises(TypeError) as te:
        #     class C6(Abstract, ta.Generic[T], abc.ABC):
        #         pass
        # assert str(te.exception).endswith('(Abstract, Generic, ABC)')
