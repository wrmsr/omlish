import typing as ta

from ... import inject as inj


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
