# ruff: noqa: PT009
import dataclasses as dc
import typing as ta  # noqa
import unittest

from ..inject import inj
from ..typing import AnyFunc


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


class TestInject2(unittest.TestCase):
    def test_inject2(self):
        i = inj.create_injector(inj.bind(420))
        self.assertEqual(i.provide(int), 420)


class TestDataclasses(unittest.TestCase):
    def test_dataclasses(self):
        @dc.dataclass(frozen=True)
        class Foo:
            i: int
            s: str

        foo = inj.create_injector(
            inj.bind(420),
            inj.bind(lambda: 'howdy', key=str),
            inj.bind(Foo),
        ).provide(Foo)
        print(foo)


class TestOverride(unittest.TestCase):
    def test_override(self):
        b0 = inj.as_bindings(inj.bind(420), inj.bind('abc'))
        i0 = inj.create_injector(b0)
        self.assertEqual(i0.provide(int), 420)
        self.assertEqual(i0.provide(str), 'abc')
        b1 = inj.override(b0, inj.bind(421))
        i1 = inj.create_injector(b1)
        self.assertEqual(i1.provide(int), 421)
        self.assertEqual(i1.provide(str), 'abc')


class TestArrays(unittest.TestCase):
    def test_arrays(self):
        bs = inj.as_bindings(
            inj.bind(420, array=True),
            inj.bind(421, array=True),
        )
        i = inj.create_injector(bs)
        p = i.provide(inj.array(int))
        print(p)


class TestFactories(unittest.TestCase):
    @dc.dataclass(frozen=True)
    class Foo:
        x: int

    @dc.dataclass(frozen=True)
    class Bar:
        y: int
        foo: 'TestFactories.Foo'

    def test_factories(self):
        # Note: in 3.8 NewType is a function not a type, so tacking it on TestFactories like the classes makes it a
        # bound method lol.
        BarFactory = ta.NewType('BarFactory', AnyFunc[TestFactories.Bar])  # noqa

        foo = self.Foo(420)

        injector = inj.create_injector(
            inj.bind_factory(self.Bar, AnyFunc, BarFactory),
            inj.bind(foo),
        )

        self.assertIs(injector[self.Foo], foo)

        bar_factory = injector[BarFactory]

        for i in range(2):
            bar: TestFactories.Bar = bar_factory.fn(i)
            self.assertIsInstance(bar, self.Bar)
            self.assertEqual(bar.y, i)
            self.assertIs(bar.foo, foo)
