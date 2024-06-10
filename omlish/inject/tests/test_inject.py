import abc
import typing as ta  # noqa

import pytest

from ... import dataclasses as dc
from ... import inject as inj
from ... import lang


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

    bs = inj.bind(
        # _as_binding(420),
        ifn,
        inj.singleton(sfn),
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
    i = inj.create_injector(inj.bind(420))
    assert i.provide(int) == 420


def test_dataclasses():
    @dc.dataclass(frozen=True)
    class Foo:
        i: int
        s: str

    foo = inj.create_injector(inj.bind(420, inj.fn(lambda: 'howdy', str), Foo)).provide(Foo)
    print(foo)


def test_override():
    b0 = inj.bind(420, 'abc')
    i0 = inj.create_injector(b0)
    assert i0.provide(int) == 420
    assert i0.provide(str) == 'abc'
    b1 = inj.override(b0, 421)
    i1 = inj.create_injector(b1)
    assert i1.provide(int) == 421
    assert i1.provide(str) == 'abc'


def test_multis():
    bs = inj.bind(
        inj.as_(inj.multi(int), [420]),
        inj.as_(inj.multi(int), [421]),
    )
    i = inj.create_injector(bs)
    p = i.provide(inj.multi(int))
    print(p)


def test_newtypes():
    Username = ta.NewType('Username', str)
    Password = ta.NewType('Password', str)
    i = inj.create_injector(inj.bind(
        inj.as_(Username, 'public'),
        inj.as_(Password, 'secret'),
    ))
    assert i[Username] == 'public'
    assert i[Password] == 'secret'


def test_cycles():
    i = inj.create_injector(inj.bind(
        lang.typed_lambda(float, x=int)(lambda x: float(x)),
        lang.typed_lambda(int, x=float)(lambda x: int(x)),
    ))
    with pytest.raises(inj.CyclicDependencyException):
        i[int]  # noqa
