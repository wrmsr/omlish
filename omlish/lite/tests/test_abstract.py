# ruff: noqa: PT027
import abc
import unittest

from ..abstract import Abstract


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
