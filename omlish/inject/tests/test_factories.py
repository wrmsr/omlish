"""
Backported from lite injector.
"""
import dataclasses as dc
import functools
import typing as ta

from ... import inject as inj
from ... import lang


T = ta.TypeVar('T')
U = ta.TypeVar('U')


def make_factory(
        fn: ta.Callable[..., T],
        cls: U,
        ann: ta.Any = None,
) -> ta.Callable[..., U]:
    if ann is None:
        ann = cls

    def outer(injector: inj.Injector) -> ann:
        def inner(*args, **kwargs):
            return injector.inject(functools.partial(fn, *args, **kwargs))
        return cls(inner)  # type: ignore

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
            inj.bind(make_factory(self.Bar, lang.AnyFunc, self.BarFactory)),
            inj.bind(foo),
        )

        assert injector[self.Foo] is foo

        bar_factory = injector[self.BarFactory]

        for i in range(2):
            bar: TestFactories.Bar = bar_factory.fn(i)
            assert isinstance(bar, self.Bar)
            assert bar.y == i
            assert bar.foo is foo
