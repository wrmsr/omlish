# ruff: noqa: PT009 PT027
import dataclasses as dc
import unittest

from ..dataclasses import dataclass_cache_hash
from ..dataclasses import dataclass_maybe_post_init


@dc.dataclass()
class CountingHashThing:
    hash: int = 0
    num_times_hashed: int = 0

    def __hash__(self):
        self.num_times_hashed += 1
        return self.hash


class TestDataclasses(unittest.TestCase):
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
