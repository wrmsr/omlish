import typing as ta

from ... import inject as inj
from ... import lang


##


class ServiceA:
    def __init__(self, b: 'ServiceB') -> None:
        self.b = b

    def foo(self) -> ta.Any:
        return {
            'a': self,
            'b': self.b,
            'b.c': self.b.c,
            'b.c.a': self.b.c.a,
            'b.c.a()': self.b.c.a(),
        }


class ServiceB:
    def __init__(self, c: 'ServiceC') -> None:
        self.c = c


class ServiceC:
    def __init__(self, a: inj.Late[ServiceA]) -> None:
        self.a = a


def test_late_inj_helper():
    injector = inj.create_injector(
        inj.bind(ServiceA, singleton=True),
        inj.bind(ServiceB, singleton=True),
        inj.bind(ServiceC, singleton=True),

        inj.bind_late(ServiceA),
    )

    a = injector[ServiceA]
    assert a.foo()['b.c.a()'] is a


class Thingy:
    def __init__(self, i: int) -> None:
        self.i = i


class ThingyGetter(lang.CachedFunc0[Thingy]):
    pass


def test_late_inj_helper_explicit():
    injector = inj.create_injector(
        inj.bind(42),
        inj.bind(Thingy, singleton=True),

        inj.bind_late(Thingy, ThingyGetter),
    )

    tg = injector[ThingyGetter]
    assert isinstance(tg, ThingyGetter)
    assert isinstance(t := tg(), Thingy)
    assert t.i == 42


##


class AsyncServiceA:
    def __init__(self, b: 'AsyncServiceB') -> None:
        self.b = b

    async def foo(self) -> ta.Any:
        return {
            'a': self,
            'b': self.b,
            'b.c': self.b.c,
            'b.c.a': self.b.c.a,
            'b.c.a()': await self.b.c.a(),
        }


class AsyncServiceB:
    def __init__(self, c: 'AsyncServiceC') -> None:
        self.c = c


class AsyncServiceC:
    def __init__(self, a: inj.AsyncLate[AsyncServiceA]) -> None:
        self.a = a


def test_async_late_inj_helper():
    injector = lang.sync_await(inj.create_async_injector(
        inj.bind(AsyncServiceA, singleton=True),
        inj.bind(AsyncServiceB, singleton=True),
        inj.bind(AsyncServiceC, singleton=True),

        inj.bind_async_late(AsyncServiceA),
    ))

    a = lang.sync_await(injector[AsyncServiceA])
    assert lang.sync_await(a.foo())['b.c.a()'] is a


class AsyncThingyGetter(lang.CachedFunc0[ta.Awaitable[Thingy]]):
    pass


def test_async_late_inj_helper_explicit():
    injector = lang.sync_await(inj.create_async_injector(
        inj.bind(42),
        inj.bind(Thingy, singleton=True),

        inj.bind_async_late(Thingy, AsyncThingyGetter),
    ))

    tg = lang.sync_await(injector[AsyncThingyGetter])
    assert isinstance(tg, AsyncThingyGetter)
    assert isinstance(t := lang.sync_await(tg()), Thingy)
    assert t.i == 42
