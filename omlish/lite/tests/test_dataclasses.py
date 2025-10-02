# ruff: noqa: PT009 PT027
import dataclasses as dc
import unittest
import typing as ta

from ..dataclasses import dataclass_cache_hash
from ..dataclasses import dataclass_descriptor_method
from ..dataclasses import dataclass_kw_only_init
from ..dataclasses import dataclass_maybe_post_init
from ..dataclasses import is_immediate_dataclass


##


class TestIsImmediate(unittest.TestCase):
    class A:
        pass

    @dc.dataclass()
    class B:
        pass

    class C(B):
        pass

    @dc.dataclass()
    class D(B):
        pass

    def test_is_immediate(self):
        self.assertFalse(is_immediate_dataclass(self.A))
        self.assertTrue(is_immediate_dataclass(self.B))
        self.assertFalse(is_immediate_dataclass(self.C))
        self.assertTrue(is_immediate_dataclass(self.D))


##


@dc.dataclass()
class CountingHashThing:
    hash: int = 0
    num_times_hashed: int = 0

    def __hash__(self):
        self.num_times_hashed += 1
        return self.hash


class TestCacheHash(unittest.TestCase):
    def test_cache_hash(self):
        @dc.dataclass(frozen=True)
        class Foo:
            thing: CountingHashThing = dc.field(default_factory=CountingHashThing)

        f = Foo()
        h1 = hash(f)
        self.assertEqual(f.thing.num_times_hashed, 1)
        h2 = hash(f)
        self.assertEqual(f.thing.num_times_hashed, 2)
        self.assertEqual(h1, h2)

        dataclass_cache_hash()(Foo)

        f = Foo()
        h1 = hash(f)
        self.assertEqual(f.thing.num_times_hashed, 1)
        h2 = hash(f)
        self.assertEqual(f.thing.num_times_hashed, 1)
        self.assertEqual(h1, h2)


##


class TestMaybePostInit(unittest.TestCase):
    def test_maybe_post_init(self):
        @dc.dataclass
        class A:
            l: list = dc.field(default_factory=list)

        @dc.dataclass
        class B(A):
            def __post_init__(self):
                dataclass_maybe_post_init(super())
                self.l.append('B')

        self.assertEqual(B().l, ['B'])

        @dc.dataclass
        class C(B):
            def __post_init__(self):
                dataclass_maybe_post_init(super())
                self.l.append('C')

        self.assertEqual(C().l, ['B', 'C'])

        @dc.dataclass
        class D(B):
            def __post_init__(self):
                dataclass_maybe_post_init(super())
                self.l.append('D')

        @dc.dataclass
        class E(D, C):
            def __post_init__(self):
                dataclass_maybe_post_init(super())
                self.l.append('E')

        self.assertEqual(E().l, ['B', 'C', 'D', 'E'])

    def test_maybe_post_init_bad(self):
        @dc.dataclass
        class Bad:
            def __post_init__(self):
                dataclass_maybe_post_init(self)

        with self.assertRaises(TypeError):
            Bad()


##


class TestKwOnlyInit(unittest.TestCase):
    def test_kw_only_init(self):
        @dataclass_kw_only_init()
        @dc.dataclass()
        class Foo:
            i: int
            s: str = 'barf'

        f = Foo(i=1, s='2')
        self.assertEqual(f.i, 1)
        self.assertEqual(f.s, '2')

        f = Foo(i=2)
        self.assertEqual(f.i, 2)
        self.assertEqual(f.s, 'barf')

        with self.assertRaises(TypeError):
            Foo(1, '2')


##


def test_dc_desc():
    @dc.dataclass()
    class Foo:
        __get__ = dataclass_descriptor_method('fn')

        i: int
        fn: ta.Callable[[int], int]

        def __call__(self, i: int) -> int:
            return self.fn(i + self.i)

    assert Foo(1, lambda i: i + 1)(1) == 3

    class Bar:
        def _fn(self, i: int) -> int:
            return i + 1

        fn = Foo(1, _fn)

    assert Bar().fn(1) == 3
