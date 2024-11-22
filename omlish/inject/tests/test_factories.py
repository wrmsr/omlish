"""
Backported from lite injector.
"""
import dataclasses as dc
import functools
import typing as ta

from ... import inject as inj
from ... import lang


T = ta.TypeVar('T')


def make_factory(
        factory_cls: ta.Any,
        factory_fn: ta.Callable[..., T],
) -> ta.Callable[..., lang.AnyFunc[T]]:
    def outer(injector: inj.Injector) -> factory_cls:
        def inner(*args, **kwargs):
            return injector.inject(functools.partial(factory_fn, *args, **kwargs))
        return lang.AnyFunc(inner)
    return outer


class TestFactories:
    @dc.dataclass(frozen=True)
    class Foo:
        x: int

    @dc.dataclass(frozen=True)
    class Bar:
        y: int
        foo: 'TestFactories.Foo'

    BarFactory = ta.NewType('BarFactory', lang.AnyFunc[Bar])

    def test_factories(self):
        foo = self.Foo(420)

        injector = inj.create_injector(
            inj.bind(make_factory(self.BarFactory, self.Bar)),
            inj.bind(foo),
        )

        assert injector[self.Foo] is foo

        bar_factory = injector[self.BarFactory]

        for i in range(2):
            bar: TestFactories.Bar = bar_factory.fn(i)
            assert isinstance(bar, self.Bar)
            assert bar.y == i
            assert bar.foo is foo
