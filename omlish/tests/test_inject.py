import abc

from .. import inject as inj


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
