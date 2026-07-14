import typing as ta

import pytest

from ..attrregistry import AttrRegistry
from ..attrregistry import StrongAttrRegistryCache
from ..attrregistry import WeakAttrRegistryCache


@pytest.mark.parametrize('cache_cls', [
    StrongAttrRegistryCache,
    WeakAttrRegistryCache,
])
def test_attr_registry(cache_cls):
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
        @A.foo.register(None)
        def foo_c(self) -> None:
            pass

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

    foo_cache = cache_cls(A.foo, lambda _, c: c)

    expected = {
        B: {'foo_a': (A.foo_a, None), 'foo_b': (B.foo_b, None)},
        C: {'foo_a': (A.foo_a, None), 'foo_c': (C.foo_c, None)},
        BC: {'foo_a': (A.foo_a, None), 'foo_c': (C.foo_c, None), 'foo_b': (B.foo_b, None), 'foo_bc': (BC.foo_bc, None)},
        CB: {'foo_a': (A.foo_a, None), 'foo_b': (B.foo_b, None), 'foo_c': (C.foo_c, None), 'foo_cb': (CB.foo_cb, None)},
        B2: {'foo_a': (A.foo_a, None), 'foo_b': (B2.foo_b, None)},
        BC2: {'foo_a': (A.foo_a, None), 'foo_c': (C.foo_c, None), 'foo_b': (B2.foo_b, None), 'foo_bc': (BC.foo_bc, None)},  # noqa
    }

    for cls in [
        B,
        C,
        BC,
        CB,
        B2,
        BC2,
    ]:
        for _ in range(2):
            print(got := foo_cache.get(cls))
            assert list(got.items()) == list(expected[cls].items())  # type: ignore[attr-defined]
