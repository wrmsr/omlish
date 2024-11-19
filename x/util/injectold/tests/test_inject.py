import abc
import dataclasses as dc
import typing as ta  # noqa

from ... import injectold as inj


def test_inject():
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
    assert i.provide(int) == 1
    assert i.provide(int) == 2
    assert i.provide(str) == '1'
    assert i.provide(str) == '1'

    def barf(x: int) -> int:
        return x + 1

    assert i.inject(barf) == 4
    assert i.inject(barf) == 5


class Barf(abc.ABC):
    @abc.abstractmethod
    def barf(self) -> str:
        raise NotImplementedError


class BarfA(Barf):
    def barf(self) -> str:
        return 'a'


class BarfB(Barf):
    def barf(self) -> str:
        return 'b'


def test_inject2():
    i = inj.create_injector(inj.as_bindings(inj.bind(420)))
    assert i.provide(int) == 420


def test_dataclasses():
    @dc.dataclass(frozen=True)
    class Foo:
        i: int
        s: str

    foo = inj.create_injector(inj.as_bindings(
        inj.bind(420),
        inj.bind(inj.fn(lambda: 'howdy', str)),
        inj.bind(Foo),
    )).provide(Foo)
    print(foo)


def test_override():
    b0 = inj.as_bindings(inj.bind(420), inj.bind('abc'))
    i0 = inj.create_injector(b0)
    assert i0.provide(int) == 420
    assert i0.provide(str) == 'abc'
    b1 = inj.override(b0, inj.bind(421))
    i1 = inj.create_injector(b1)
    assert i1.provide(int) == 421
    assert i1.provide(str) == 'abc'


def test_arrays():
    bs = inj.as_bindings(
        inj.as_(inj.array(int), 420),
        inj.as_(inj.array(int), 421),
    )
    i = inj.create_injector(bs)
    p = i.provide(inj.array(int))
    print(p)
