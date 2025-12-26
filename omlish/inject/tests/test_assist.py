import dataclasses as dc
import functools
import typing as ta

from ... import inject as inj


##


def bind_assist(
        key: ta.Any,
        fn: ta.Callable,
        **kwargs: ta.Any,
) -> inj.Elements:
    async def outer(i):
        return functools.partial(fn, **{k: await i[v] for k, v in kwargs.items()})

    return inj.as_elements(
        inj.bind(key, to_async_fn=inj.target(i=inj.AsyncInjector)(outer)),
    )


##


class Foo:
    @dc.dataclass(frozen=True)
    class Config:
        i: int

    def __init__(
            self,
            config: Config,
            *,
            bar: 'Bar',
    ) -> None:
        super().__init__()

        self._config = config
        self._bar = bar

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}{id(self):x}(config={self._config!r})'


class Bar:
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}()'


class FooFactory(ta.Protocol):
    def __call__(self, config: Foo.Config) -> Foo: ...


def test_assist():
    i = inj.create_injector(
        inj.bind(Bar, singleton=True),
        bind_assist(FooFactory, Foo, bar=Bar),
    )
    for n in range(2):
        print(i[FooFactory](Foo.Config(i=n)))
