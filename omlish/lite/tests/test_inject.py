# ruff: noqa: PT009
import abc
import dataclasses as dc
import typing as ta  # noqa
import unittest

from ..inject import inj


class TestInject(unittest.TestCase):
    def test_inject(self):
        ifn_n = 0

        def ifn() -> int:
            nonlocal ifn_n
            ifn_n += 1
            return ifn_n

        sfn_n = 0

        def sfn() -> str:
            nonlocal sfn_n
            sfn_n += 1
            return str(sfn_n)

        bs = inj.as_bindings(
            # inj.bind(420),
            inj.bind(ifn),
            inj.bind(sfn, singleton=True),
        )

        i = inj.create_injector(bs)
        self.assertEqual(i.provide(int), 1)
        self.assertEqual(i.provide(int), 2)
        self.assertEqual(i.provide(str), '1')
        self.assertEqual(i.provide(str), '1')

        def barf(x: int) -> int:
            return x + 1

        self.assertEqual(i.inject(barf), 4)
        self.assertEqual(i.inject(barf), 5)

    class Barf(abc.ABC):
        @abc.abstractmethod
        def barf(self) -> str:
            raise NotImplementedError

    class BarfA(Barf):
        def barf(self) -> str:
            return 'a'

    class BarfB(Barf):
        def barf(self) -> str:
            return 'b'

    def test_inject2(self):
        i = inj.create_injector(inj.as_bindings(inj.bind(420)))
        self.assertEqual(i.provide(int), 420)

    def test_dataclasses(self):
        @dc.dataclass(frozen=True)
        class Foo:
            i: int
            s: str

        foo = inj.create_injector(inj.as_bindings(
            inj.bind(420),
            inj.bind(lambda: 'howdy', key=str),
            inj.bind(Foo),
        )).provide(Foo)
        print(foo)

    def test_override(self):
        b0 = inj.as_bindings(inj.bind(420), inj.bind('abc'))
        i0 = inj.create_injector(b0)
        self.assertEqual(i0.provide(int), 420)
        self.assertEqual(i0.provide(str), 'abc')
        b1 = inj.override(b0, inj.bind(421))
        i1 = inj.create_injector(b1)
        self.assertEqual(i1.provide(int), 421)
        self.assertEqual(i1.provide(str), 'abc')

    def test_arrays(self):
        bs = inj.as_bindings(
            inj.bind(420, array=True),
            inj.bind(421, array=True),
        )
        i = inj.create_injector(bs)
        p = i.provide(inj.array(int))
        print(p)
