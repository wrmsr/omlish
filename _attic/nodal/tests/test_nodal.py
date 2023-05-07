import typing as ta

import pytest

from .. import annotations
from .. import nodal


class Annotation(annotations.Annotation):
    pass


class A(nodal.Nodal['A', Annotation]):
    pass


def test_nodal():
    class B(A):
        pass

    B()

    class C(A):
        al: ta.Sequence[A]

    C([])

    with pytest.raises(TypeError):
        class D(A):
            al: ta.AbstractSet[A]

        D(set())


# FIXME: lol
# @pytest.mark.xfail
# def test_fmap():
#     class Annotation(annotations.Annotation):
#         pass
#
#     class Node(nodal.Nodal['Node', Annotation]):
#         pass
#
#     class Foo(Node):
#         l: ta.Sequence[Node]
#
#     class Bar(Node):
#         s: str
#         l: ta.Sequence[Node]
#
#     n0 = Foo([
#         Foo([
#             Bar('a', []),
#             Foo([
#                 Bar('b', []),
#                 Bar('c', []),
#             ]),
#             Bar('d', []),
#             Foo([
#                 Bar('e', []),
#                 Foo([]),
#                 Foo([
#                     Bar('f', []),
#                 ]),
#             ]),
#         ]),
#     ])
#     print(n0)
#
#     n1 = n0.fmap(lambda n: {'s': n.s + '!'} if isinstance(n, Bar) else {})
#     print(n1)
