import dataclasses as dc
import functools
import typing as ta

from omlish.lite.inject import inj
from omlish.lite.inject import Injector


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True)
class Factory(ta.Generic[T]):
    fn: ta.Callable[..., T]

    def __call__(self, *args: ta.Any, **kwargs: ta.Any) -> T:
        return self.fn(*args, **kwargs)


def make_injector_factory(
        factory_cls: ta.Any,
        factory_fn: ta.Callable[..., T],
) -> ta.Callable[..., Factory[T]]:
    def outer(injector: Injector) -> factory_cls:
        def inner(*args, **kwargs):
            return injector.inject(functools.partial(factory_fn, *args, **kwargs))
        return Factory(inner)
    return outer


##


@dc.dataclass(frozen=True)
class Foo:
    x: int


@dc.dataclass(frozen=True)
class Bar:
    y: int
    foo: Foo


BarFactory = ta.NewType('BarFactory', Factory[Bar])


def _main() -> None:
    foo = Foo(420)

    injector = inj.create_injector(
        inj.bind(make_injector_factory(BarFactory, Bar)),
        inj.bind(foo),
    )

    assert injector[Foo] is foo

    bar_factory = injector[BarFactory]

    for i in range(2):
        bar: Bar = bar_factory.fn(i)
        assert isinstance(bar, Bar)
        assert bar.y == i
        assert bar.foo is foo


if __name__ == '__main__':
    _main()
