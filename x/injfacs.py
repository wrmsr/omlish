import dataclasses as dc
import functools
import typing as ta

from omlish.lite.inject import inj
from omlish.lite.inject import Injector
from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.typing import Func


T = ta.TypeVar('T')


##


def make_injector_factory(
        factory_cls: ta.Any,
        factory_fn: ta.Callable[..., T],
) -> ta.Callable[..., Func[T]]:
    def outer(injector: Injector) -> factory_cls:
        def inner(*args, **kwargs):
            return injector.inject(functools.partial(factory_fn, *args, **kwargs))
        return Func(inner)
    return outer


def bind_injector_factory(
        factory_cls: ta.Any,
        factory_fn: ta.Callable[..., T],
) -> InjectorBindingOrBindings:
    return inj.bind(make_injector_factory(factory_cls, factory_fn))


##


@dc.dataclass(frozen=True)
class Foo:
    x: int


@dc.dataclass(frozen=True)
class Bar:
    y: int
    foo: Foo


BarFactory = ta.NewType('BarFactory', Func[Bar])


def _main() -> None:
    foo = Foo(420)

    injector = inj.create_injector(
        bind_injector_factory(BarFactory, Bar),
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
