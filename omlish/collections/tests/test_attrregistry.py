import typing as ta

from ..attrregistry import AttrRegistry
from ..attrregistry import AttrRegistryCache


def test_attr_registry():
    class A:
        foo = AttrRegistry[ta.Callable, None]()

        def foo_a(self) -> None:
            pass
        foo.register(foo_a, None)

    class B(A):
        def foo_b(self) -> None:
            pass
        A.foo.register(foo_b, None)

    class C(A):
        def foo_c(self) -> None:
            pass
        A.foo.register(foo_c, None)

    class BC(B, C):
        def foo_bc(self) -> None:
            pass
        A.foo.register(foo_bc, None)

    class CB(C, B):
        def foo_cb(self) -> None:
            pass
        A.foo.register(foo_cb, None)

    class B2(A):
        def foo_b(self) -> None:
            pass
        A.foo.register(foo_b, None)

    class BC2(B2, BC):
        pass

    foo_cache = AttrRegistryCache[ta.Callable, None, ta.Any](A.foo, lambda c: c)

    for cls in [B, C, BC, CB, B2, BC2]:
        for _ in range(2):
            print(foo_cache.get(cls))
