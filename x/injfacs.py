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
    def make_bar_factory(injector: Injector) -> BarFactory:
        def inner(y: int) -> Bar:
            return injector.inject(functools.partial(Bar, y))
        return BarFactory(Factory(inner))

    foo = Foo(420)

    injector = inj.create_injector(
        inj.bind(make_bar_factory),
        inj.bind(foo),
    )

    assert injector[Foo] is foo

    bar_factory = injector[BarFactory]

    for i in range(2):
        bar = bar_factory(i)
        assert isinstance(bar, Bar)
        assert bar.y == i
        assert bar.foo is foo


if __name__ == '__main__':
    _main()
