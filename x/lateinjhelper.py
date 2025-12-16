import abc
import typing as ta

from omlish import lang
from omlish import inject as inj


T = ta.TypeVar('T')


##


class Late(lang.Abstract, ta.Generic[T]):
    @abc.abstractmethod
    def __call__(self) -> T:
        raise NotImplementedError


class AsyncLate(lang.Abstract, ta.Generic[T]):
    @abc.abstractmethod
    def __call__(self) -> ta.Awaitable[T]:
        raise NotImplementedError


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
    def __init__(self, a: Late[ServiceA]) -> None:
        self.a = a


def test_late_inj_helper():
    injector = inj.create_injector(
        inj.bind(ServiceA, singleton=True),
        inj.bind(ServiceB, singleton=True),
        inj.bind(ServiceC, singleton=True),

        inj.bind(Late[ServiceA], to_fn=inj.KwargsTarget.of(
            lambda i: lambda: i[ServiceA],
            i=inj.Injector,
        )),
    )

    a = injector[ServiceA]
    print(a.foo())
