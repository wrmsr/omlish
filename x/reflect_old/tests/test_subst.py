import pprint
import typing as ta

from ... import reflect as rfl


T = ta.TypeVar('T')
U = ta.TypeVar('U')


def test_generic_mro():
    class A(ta.Generic[T]):
        a: T

    class B(ta.Generic[T]):
        b: T

    class C(A[U]):
        pass

    class D(C[str], B[int]):
        pass

    class E(A[int]):
        pass

    class F(A):
        pass

    class G(ta.Generic[T, U]):
        a: T
        b: U

    print()

    for ty in [
        A,
        A[str],
        B,
        B[int],
        C,
        C[str],
        D,
        E,
        F,
        G,
        G[int, str],
        C[B[int]],
        C[C[int]],
    ]:
        print(ty)
        pprint.pprint(rfl.generic_mro(ty))
        print()
